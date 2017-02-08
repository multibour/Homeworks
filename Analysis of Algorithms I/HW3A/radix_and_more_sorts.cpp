#include <cstdlib>
#include <ctime>
#include "sorts.h"

using namespace std;

int main(int argc, char* argv[]){
	if (argc != 2){
		cout << "Invalid number of inputs." << endl;
		return EXIT_FAILURE;
	}

	Sorting sorting(atoi(argv[1]));
	sorting.readFile("numbers_to_sort.txt");

	cout << "Sorting..." << endl;
	clock_t elapsedTime = clock();
	sorting.radixSort();
	elapsedTime -= clock();
	cout << "Elapsed time: " << elapsedTime << " seconds" << endl;

	sorting.writeFile("sorted_numbers.txt");

	/*{
		long long int* arr1 = sorting.getCopy();
		long long int* arr2 = sorting.getCopy();

		gnomeSort(arr1, sorting.getSize());
		freezingSort(arr2, sorting.getSize());
	
		delete[] arr1;
		delete[] arr2;
	}*/

	return EXIT_SUCCESS;
}
