#ifndef _SORTS_H
#define _SORTS_H

#include <iostream>
#include <fstream>
#include <string>
#include <cmath>

using namespace std;

template<class T>
void swapValues(T & a, T & b){
	T temp = a;
	a = b;
	b = temp;
}

const int number_of_digits = 10; //every number in the file has 10 digits max


//-- CLASS --//

class Sorting{
private:
	struct NumberArray{
		long long int id;
		long long int number;
	} * numberArray;
	int size;

public:
	static int getDigit(long long int number, int digit){
		while (digit != 1){
			number /= 10;
			--digit;
		}
		return number % 10;
	}

public:
	Sorting(int N){
		if (N <= 1000000 && N > 0){
			size = N;
			numberArray = new NumberArray[size];
		}
		else{
			size = 0;
			numberArray = NULL;
		}
	}
	~Sorting(){
		if (numberArray != NULL)
			delete[] numberArray;
	}


	void readFile(const char * fileName){
		ifstream infile;
		infile.open(fileName);
		
		//format: ID NUMBER\n
		for (int iii = 0; iii < size; ++iii){
			infile >> numberArray[iii].id >> numberArray[iii].number;
		}

		infile.close();
	}

	void writeFile(const char * fileName){
		ofstream outfile;
		outfile.open(fileName);

		cout << "Writing file" << endl;
		
		for (int iii = 0; iii < size; ++iii){
			outfile << numberArray[iii].id << '\t' << numberArray[iii].number << '\n';
		}

		outfile.close();

		cout << "Finished writing to file!" << endl;
	}


	void radixSort(){
		//radix sort
		for (int iii = 1; iii <= number_of_digits; ++iii){
			//counting sort
			int countArray[10] = { 0 };
			int positionArray[10] = { 0 };

			for (int jjj = 0; jjj < size; ++jjj)
				++countArray[ getDigit(numberArray[jjj].number, iii) ];
			for (int jjj = 1; jjj < 10; ++jjj)
				countArray[jjj] += countArray[jjj - 1];
			for (int jjj = 1; jjj < 10; ++jjj)
				positionArray[jjj] = countArray[jjj - 1];
				

			NumberArray* temp = new NumberArray[size];			

			for (int jjj = 0; jjj < size; ++jjj){
				temp[ positionArray[ getDigit(numberArray[jjj].number, iii) ]++ ] = numberArray[jjj];
				//++positionArray[getDigit(numberArray[jjj].number, iii)];

				//temp[countArray[ getDigit(numberArray[jjj].number, iii) ] - 1] = numberArray[jjj];
				//--countArray[ getDigit(numberArray[jjj].number, iii) ];
			}

			delete[] numberArray;
			numberArray = temp;
		}
	}


	long long int* getCopy(){
		long long int* copy = new long long int[size];
		for (int iii = 0; iii < size; ++iii){
			copy[iii] = numberArray[iii].number;
		}
		return copy;
	}

	int getSize(){
		return size;
	}
};


//-- Other Sort functions --//

void gnomeSort(long long int arr[], int size){
	cout << "Gnome Sort" << endl;
	int iii = 1,
		jjj = 2;

	while (iii < size){
		if (arr[iii - 1] <= arr[iii]){
			iii = jjj;
			++jjj;
		}
		else{
			swapValues(arr[iii - 1], arr[iii]);
			--iii;
			if (iii == 0){
				iii = jjj;
				++jjj;
			}
		}
	}
}

void freezingSort(long long int arr[], int size){
	cout << "Freezing Sort" << endl;
	for (int freeze_count = 0; freeze_count < size; ++freeze_count){
		//freeze from left
		for (int iii = freeze_count; iii < (size + freeze_count) / 2 + 1; ++iii){
			if (iii != size - iii + freeze_count && arr[iii] < arr[size - iii + freeze_count]){
				swapValues(arr[size - iii + freeze_count], arr[iii]);
			}
		}

		//freeze from right
		if (freeze_count != 0){
			for (int iii = size - freeze_count; iii > (size - freeze_count) / 2; --iii){
				if (iii != (size - iii - freeze_count)  &&  arr[size - iii - freeze_count] < arr[iii]){
					swapValues(arr[size - iii - freeze_count], arr[iii]);
				}
			}
		}
	}//end of outermost for
}


#endif
