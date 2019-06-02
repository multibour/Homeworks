#include <iostream>
#include <map>
#include <tuple>
#include <string>
#include <functional>
#include <list>
#include <random>
#include <numeric>
#include <fstream>
#include <vector>

//-- type definitions

typedef std::function<void(unsigned int)> FunctionType;
typedef std::tuple<double, int, FunctionType&> FEL_Tuple;
typedef std::map<unsigned int, std::vector<unsigned int> > Statistics;

//-- initialise random device
std::mt19937 mt(std::random_device{}());

auto customerArrival = std::bind(std::uniform_real_distribution<>(0, 3), std::ref(mt));
auto cabbageDelivery = std::bind(std::uniform_real_distribution<>(1, 15), std::ref(mt));
auto cabbageRot = std::bind(std::uniform_real_distribution<>(7, 12), std::ref(mt));

//-- global variables and constants
double clock = 0;
unsigned int customerCount = 0;
unsigned int deniedCustomers = 0;
unsigned int rottenCabbages = 0;
const unsigned int CUSTOMER_LIMIT = 10000u;
const unsigned int TRIAL_COUNT = 1000u;
const std::string arrivedCustomers = "arrivedCustomers";
const std::string restockingCabbages = "restockingCabbages";
const std::string shelf = "onShelf";


//-- funstion declarations
void simulate(std::list<FEL_Tuple>&);
void writeToFile(std::string&&, const Statistics&, const Statistics&);


//-- main
int main() {
	std::list<FEL_Tuple> FEL; // future event list
	std::map<std::string, std::list<unsigned int>> states = {
		{arrivedCustomers, {}}, //initialise an empty list for every state
		{restockingCabbages, {}},
		{shelf, {}}
	};
	

	//-- Event Function Definitions --//

	FunctionType arrivalEvent, restockingEvent, buyingEvent, rottingEvent;

	arrivalEvent = [&](unsigned int customerId) {
		states.at(arrivedCustomers).push_back(customerId);
		FEL.push_back({ clock, customerId, buyingEvent });

		// new customer
		FEL.push_back({ clock + customerArrival(), customerId + 1, arrivalEvent });
	};

	restockingEvent = [&](unsigned int cabbageId) {
		states.at(restockingCabbages).remove(cabbageId);
		states.at(shelf).push_back(cabbageId);
		FEL.push_back({ clock + cabbageRot(), cabbageId, rottingEvent });
	};

	buyingEvent = [&](unsigned int customerId) {
		++customerCount;

		auto & onShelf = states.at(shelf);
		if (!onShelf.empty()) {
			unsigned int cabbageId = onShelf.front();
			onShelf.pop_front();

			// remove the rotting event of the corresponding cabbage id from FEL
			FEL.remove_if([cabbageId, &rottingEvent](FEL_Tuple & tuple) { 
				return (std::get<1>(tuple) == cabbageId) && (&std::get<2>(tuple) == &rottingEvent); //memory addresses of std::function objects do work. Why? look at line 15
			});

			states.at(restockingCabbages).push_back(cabbageId);
			FEL.push_back({ clock + cabbageDelivery(), cabbageId, restockingEvent });
		}
		else {
			//deny customer
			++deniedCustomers;
		}

		states.at(arrivedCustomers).remove(customerId);
	};

	rottingEvent = [&](unsigned int cabbageId) {
		states.at(shelf).remove(cabbageId);
		states.at(restockingCabbages).push_back(cabbageId);

		FEL.push_back({ clock + cabbageDelivery(), cabbageId, restockingEvent });
	};


	//-- Simulation Start --//
	Statistics shelfSize_to_refusedCustomers;
	Statistics shelfSize_to_rottenCabbages;

	for (unsigned int shelfSize = 1; shelfSize <= 50; ++shelfSize) { // for every shelf size until 50
		shelfSize_to_refusedCustomers[shelfSize]; //initialise std::vector
		shelfSize_to_rottenCabbages[shelfSize];

		for (unsigned int i = 0; i < TRIAL_COUNT; ++i) { //for each trial
			//-- initialisation
			deniedCustomers = 0;
			rottenCabbages = 0;
			clock = 0;
			customerCount = 0;

			for (auto & element : states) //clear states' lists
				element.second.clear();

			auto & onShelf = states.at(shelf);
			onShelf.resize(shelfSize); //resize shelf
			std::iota(onShelf.begin(), onShelf.end(), 1); //fill it with cabbages

			//-- add initial events
			FEL.clear();
			FEL.push_back({ clock + customerArrival(), 1, arrivalEvent }); // arrival of the first customer
			for (unsigned int i = 1; i <= shelfSize; ++i)
				FEL.push_back({ clock + cabbageRot(), i, rottingEvent }); // rotting event of each cabbage in shelf


			//-- simulate
			std::cout << "Simulating shelf size " << shelfSize << " & trial " << i << '\n';
			simulate(FEL);
			std::cout << "\tfinished at " << clock << '\n';

			shelfSize_to_refusedCustomers[shelfSize].push_back(deniedCustomers);
			shelfSize_to_rottenCabbages[shelfSize].push_back(rottenCabbages);
		}

		std::cout << shelfSize << " finished" << std::endl;
	}

	//-- Write Results to File --//
	writeToFile("results", shelfSize_to_refusedCustomers, shelfSize_to_rottenCabbages);
	std::cout << "Wrote results to file." << std::endl;

	return 0;
}


void simulate(std::list<FEL_Tuple> & futureEventList) {
	const unsigned int progress = CUSTOMER_LIMIT / 5u;
	while (customerCount < CUSTOMER_LIMIT) { //until 10000 customers have been reached
		futureEventList.sort([](const FEL_Tuple & left, const FEL_Tuple & right) { return std::get<0>(left) < std::get<0>(right); });

		clock = std::get<0>(futureEventList.front());
		unsigned int id = std::get<1>(futureEventList.front());
		auto & eventFunction = std::get<2>(futureEventList.front());
		futureEventList.pop_front();

		eventFunction(id);

		if (customerCount % progress == 0)
			std::cout << '.';
	}
}


void writeToFile(std::string && filename, const Statistics & deniedCustomersMap, const Statistics & rottenCabbagesMap) {
	std::ofstream outFile(filename + ".csv"), outFile2(filename + "_detailed.csv");
	const char delim = ',';

	for (int i = 0; i < 2; ++i) {

		for (const auto & vals : (i == 0 ? deniedCustomersMap : rottenCabbagesMap)) { //denied customers first, then rotten cabbages
			outFile2 << vals.first;
			for (auto & val : vals.second)
				outFile2 << delim << val;
			outFile2 << std::endl;

			outFile << vals.first << delim;
			outFile << std::accumulate(vals.second.begin(), vals.second.end(), 0.0) / double(vals.second.size()) << '\n';
		}

		if (i == 0) {
			outFile << "\nrotten cabbages\n\n";
			outFile2 << "\nrotten cabbages\n\n";
		}
	}

	outFile.close();
	outFile2.close();
}

