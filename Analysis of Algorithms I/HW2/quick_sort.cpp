#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <cstdlib>

using namespace std;


//-- Structs --//

struct Word{
	string word;
	int order;
};

struct Line{
	vector<Word> words;
	int lineID;
};


//-- Function Declarations --//

void quickSort(Line &, int, int); //sort words at a line
void quickSort(vector<Line> &, int, int); //sort lines
void quickSort(vector<int> &, int, int); //sort number array

template<class T>
void swapElements(T & a, T & b){
	T temp = a;
	a = b;
	b = temp;
}


//-- Global Variables --//

unsigned int quicksort_counter = 0;

struct UserInput{
	unsigned int mode;
	unsigned int M_or_K;
	unsigned int N;
} userInput;


//-- Main --//

int main(int argc, char* argv[]){
	srand(255);
	cout << "rand() check: " << rand() << endl;

	vector<Line> novel;
	vector<int> arr;

	//-- Handle User Input --//
	if (argc < 3 || 4 < argc){
		cout << "Invalid number of Inputs" << endl;
		return EXIT_FAILURE;//1
	}
	if (!(atoi(argv[1]) == 1 || atoi(argv[1]) == 2)){
		cout << "Wrong mode type." << endl;
		return EXIT_FAILURE;//1
	}
	

	userInput.mode = atoi(argv[1]);
	userInput.M_or_K = atoi(argv[2]);
	if (userInput.mode == 1)
		userInput.N = atoi(argv[3]);
	
	
	//For testing locally
	//argc = 3;		//2 - numbers | 3 - novel
	//userInput.M_or_K = 100;
	//userInput.N = 500;


	//-- Read File --//
	cout << "Reading file..." << endl;

	if(userInput.mode == 1){
		ifstream infile("mobydick.txt");

		Word singleWord;
		char dummy;
		string temp("");
		
		while (!infile.eof()){ //Format: lineID {word1_word2_..._wordn} {order1_order2_..._ordern}\n
			Line toAdd;

			infile >> toAdd.lineID >> dummy; // |lineID {|
			
			while (dummy != '}'){ // |word1_word2_..._wordn}|
				infile >> dummy;

				if (dummy != '_' && dummy != '}')
					temp += dummy;
				else{
					singleWord.word = temp;
					temp.clear();

					toAdd.words.push_back(singleWord);
				}
			}

			infile >> dummy; // | {|

			// |order1_order2_..._ordern}|
			for (int iii = 0; iii < toAdd.words.size(); ++iii)
				infile >> toAdd.words[iii].order >> dummy;

			novel.push_back(toAdd);
		}//end while
		
		//last element is put twice due to last line being empty in file
		novel.pop_back();//delete this line if last element is not added

		infile.close();
	}

	else{ //mode == 2
		ifstream infile("numbers_to_sort.txt");

		int temp;

		for (int iii = 0; iii < userInput.M_or_K; ++iii){
			infile >> temp;
			arr.push_back(temp);
		}

		infile.close();
	}

	cout << "Finished reading file." << endl;


	//-- Sort & Write to File --//

	cout << "Sorting..." << endl;

	if (userInput.mode == 2){//only K
		cout << "\tSorting numbers..." << endl;
		quickSort(arr, 0, arr.size() - 1);

		cout << "Writing to numbers.txt..." << endl;
		ofstream outfile("numbers.txt");
		for (int iii = 0; iii < arr.size(); ++iii)
			outfile << arr[iii] << '\n';
		outfile.close();
	}
	else{//mode == 1 //M and N
		cout << "\tSorting lines..." << endl;
		quicksort_counter = 0;
		quickSort(novel, 0, novel.size() - 1);

		cout << "\tSorting words at each line..." << endl;
		for (int iii = 0; iii < novel.size(); ++iii){
			quickSort(novel[iii], 0, novel[iii].words.size() - 1);
		}

		cout << "Writing to novel.txt..." << endl;
		ofstream outfile("novel.txt");
		for (int iii = 0; iii < novel.size(); ++iii){
			for (int jjj = 0; jjj < novel[iii].words.size(); ++jjj){
				outfile << novel[iii].words[jjj].word << ' ';
			}
			outfile << '\n';
		}
		outfile.close();
	}

	cout << "Finished writing to file." << endl;


	return EXIT_SUCCESS;//0
}


//-- Function Definitions --//

void quickSort(Line & line, int low, int high){//sort words
	if (low < high){
		//-- Partition --//
		swapElements(line.words[(rand() % (high - low + 1)) + low],
					 line.words[high]);//random pivoting

		int pivot = line.words[high].order,
			mid = low - 1;


		for (int jjj = low; jjj <= high - 1; ++jjj){
			if (line.words[jjj].order <= pivot){
				++mid;
				swapElements(line.words[mid], line.words[jjj]);
			}
		}

		++mid;

		swapElements(line.words[mid], line.words[high]);


		//-- Recursion --//
		quickSort(line, low, mid - 1);
		quickSort(line, mid + 1, high);
	}
}

void quickSort(vector<Line> & novel, int low, int high){//sorts lines
	if (++quicksort_counter == userInput.M_or_K){//counter == M
		cout << "Mth Quicksort - Line ID of Nth Element: " << novel[userInput.N].lineID << endl;
	}
	if (low < high){
		//-- Partition --//
		int pivot = novel[high].lineID,
			index = low - 1;

		for (int jjj = low; jjj <= high - 1; ++jjj){
			if (novel[jjj].lineID <= pivot){
				++index;
				swapElements(novel[index], novel[jjj]);
			}
		}

		++index;

		swapElements(novel[index], novel[high]);


		//-- Recursion --//
		quickSort(novel, low, index - 1);
		quickSort(novel, index + 1, high);
	}
}

void quickSort(vector<int> & arr, int low, int high){
	if (low < high){
		//-- Partition --//
		int pivot = arr[high],
			index = low - 1;

		for (int jjj = low; jjj <= high - 1; ++jjj){
			if (arr[jjj] <= pivot){
				++index;
				swapElements(arr[index], arr[jjj]);
			}
		}

		++index;

		swapElements(arr[index], arr[high]);


		//-- Recursion --//
		quickSort(arr, low, index - 1);
		quickSort(arr, index + 1, high);
	}
}
