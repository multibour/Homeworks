#include <iostream>
#include <fstream>
#include <ctime>
#include <cstdlib>
#include <cmath>
#include <cfloat>

using namespace std;

//-- Declarations --//

struct User_Input{
		unsigned int N;
		unsigned int K;

		string algorithmType;

		int x_axis;
		int y_axis;
};

struct Location {
	unsigned int id;

	int x;
	int y;

	double distance;
};


void insertionSort(Location*, unsigned int);
void mergeSort(Location*, unsigned int, unsigned int);
Location* linearSearchMethod(Location*,  unsigned int, unsigned int);


//-- MAIN --//

int main(int argc, char* argv[]){
	//-- Check initial condition --//
	
	if (argc != 6){
		cout << "Invalid number of inputs." << endl;
		return EXIT_FAILURE;//1
	}
	

	//-- Handle User Inputs --//

	cout << "Handling user inputs..." << endl;

	User_Input userInput;

	userInput.N = atoi(argv[argc-5]);
	userInput.K = atoi(argv[argc-4]);
	userInput.algorithmType = string(argv[argc-3]);
	userInput.x_axis = atoi(argv[argc-2]);//Assuming coordinates
	userInput.y_axis = atoi(argv[argc-1]);//are always integers


	//-- Check if user inputs are valid --//

	if (userInput.N > 1000000 || userInput.K > userInput.N){
		cout << "Invalid input(s)." << endl;
		return EXIT_FAILURE;//1
	}


	//-- Create Arrays --//

	Location* locationArray = new Location [userInput.N];
	Location* readyArray = NULL; //will be used if linear search method is used

	
	//-- Extract Data from File --//

	cout << "Extracting data from file..." << endl;

	ifstream infile("warehouselocations.txt");

	for (unsigned int index = 0; index < userInput.N; index++){
		Location temp;
		infile >> temp.id >> temp.x >> temp.y;

		//euclidean distance
		temp.distance = sqrt(pow(userInput.x_axis - temp.x, 2) +
							 pow(userInput.y_axis - temp.y, 2));
		
		locationArray[index] = temp;
	}

	infile.close();


	//-- Algorithms --//

	cout << "Applying algorithm..." << endl;

	clock_t time; //to calculate time

	if (userInput.algorithmType == "IS"){ //insertion sort
		time = clock();
		insertionSort(locationArray, userInput.N);
		time = clock() - time;
	}
	else if (userInput.algorithmType == "MS"){ //merge sort
		time = clock();
		mergeSort(locationArray, 0, userInput.N - 1);
		time = clock() - time;
	}
	else if (userInput.algorithmType == "LS"){ //linear search
		time = clock();
		readyArray = linearSearchMethod(locationArray, userInput.N, userInput.K);
		time = clock() - time;
	}
	else{
		cout << "Invalid algorithm." << endl;

		delete [] locationArray;
		return EXIT_FAILURE;//1
	}

	//Print past time
	cout << "-----" << endl;
	cout << "Elapsed time: " << double(time) / CLOCKS_PER_SEC << " seconds" << endl;
	cout << "~~~in clocks: " << time << " clocks" << endl;
	cout << "-----" << endl;


	//-- Print closest K locations to Output File --//

	cout << "Creating output file..." << endl;

	ofstream outfile("output.txt");

	Location* outArray = (readyArray == NULL) ? locationArray : readyArray;
	for(unsigned int index = 0; index < userInput.K; index++){
		outfile << outArray[index].id << '\t'
				<< outArray[index].x << '\t'
				<< outArray[index].y << '\t'
				<< outArray[index].distance << endl;
	}

	outfile.close();


	//-- Deallocate Array(s) --//

	if (readyArray != NULL)
		delete [] readyArray;
	delete [] locationArray;


	cout << "Complete!" << endl;

	return EXIT_SUCCESS;//0
}


//-- Function Definitions --//

void insertionSort(Location* toBeSorted, unsigned int size){
	for (unsigned int jjj = 1; jjj < size; jjj++){
		Location key = toBeSorted[jjj];

		int iii = jjj - 1;//iii can become -1

		while ((iii >= 0) && (toBeSorted[iii].distance > key.distance)){
			toBeSorted[iii + 1] = toBeSorted[iii];
			iii--;
		}

		toBeSorted[iii + 1] = key;
	}
}

void mergeSort(Location* toBeSorted, unsigned int lowIndex, unsigned int highIndex){
	if (lowIndex < highIndex){
		unsigned int midIndex = (lowIndex + highIndex) / 2; //middle index

		//Split to left and right
		mergeSort(toBeSorted, lowIndex, midIndex);
		mergeSort(toBeSorted, midIndex + 1, highIndex);

		
		//--//-- Merging Process --//--//

		//-- Set initial Values & Arrays --//
		
		unsigned int n_1 = midIndex - lowIndex + 1; //length of left array
		unsigned int n_2 = highIndex - midIndex; //length of right array

		Location* leftArray = new Location [n_1];
		Location* rightArray = new Location [n_2];

		for (unsigned int iii = 0; iii < n_1; iii++)
			leftArray[iii] = toBeSorted[lowIndex + iii];

		for (unsigned int jjj = 0; jjj < n_2; jjj++)
			rightArray[jjj] = toBeSorted[midIndex + jjj + 1];


		//-- Sorting Process --//

		unsigned int iii = 0,//indices
					 jjj = 0,
					 kkk = lowIndex; 

		while (iii < n_1 && jjj < n_2){
			if (leftArray[iii].distance <= rightArray[jjj].distance){
				toBeSorted[kkk] = leftArray[iii];
				iii++;
			}
			else{
				toBeSorted[kkk] = rightArray[jjj];
				jjj++;
			}
			kkk++;
		}

		//dump remaining of left, if any
		while (iii < n_1){
			toBeSorted[kkk] = leftArray[iii];
			iii++;
			kkk++;
		}

		//dump reamining of right, if any
		while (jjj < n_2){
			toBeSorted[kkk] = rightArray[jjj];
			jjj++;
			kkk++;
		}


		//-- Deallocate left & right Arrays --//

		delete [] leftArray;
		delete [] rightArray;
	}
}

Location* linearSearchMethod(Location* locationArray, unsigned int size, unsigned int searchCount){
	Location* resultArray = new Location [searchCount];
	unsigned int* index_array_of_pulled_elements = new unsigned int [searchCount];

	for (unsigned int iii = 0; iii < searchCount; iii++){ //search K times
		double minimum = DBL_MAX;//max double value

		for (unsigned int jjj = 0; jjj < size; jjj++){ //traverse array

			if (locationArray[jjj].distance <= minimum){

				//Check whether that element has been pulled before
				bool isPulledBefore = false;
				for (unsigned int kkk = 0; kkk < iii; kkk++){
					if (index_array_of_pulled_elements[kkk] == jjj){
						isPulledBefore = true;
						break;
					}
				}

				//If that element has not been pullled before
				if (!isPulledBefore){
					resultArray[iii] = locationArray[jjj];
					minimum = locationArray[jjj].distance;

					index_array_of_pulled_elements[iii] = jjj;
				}
			}
		}//end of jjj for
	}//end of iii for

	delete [] index_array_of_pulled_elements;
	return resultArray;
}
