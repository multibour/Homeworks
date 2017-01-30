#include <cstdlib>
#include "150140127.h"

using namespace std;

const char * outfileName = "150140127_output.txt";

int main(int argc, char* argv[]){
	/**/
	if (argc != 3){
		cout << "ERROR: Invalid number of inputs" << endl;
		return EXIT_FAILURE;
	}

	Dictionary dic(atoi(argv[2]));
	dic.readFile(argv[1]);
	dic.writeFile(outfileName);
	

	/*
	Dictionary dic(337);
	dic.readFile("words.txt");
	dic.writeFile(outfileName);

	int l;
	cin >> l;*/


	cout << "Final form of hash table is saved as " << outfileName << endl;

	return EXIT_SUCCESS;
}
