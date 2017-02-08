#include "header.h"
#include <ctime>

using namespace std;


int main(int argc, char* argv[]){
	if (argc == 2){// ./p 2
		Game game;

		game.play();
	}
	else if (argc == 3){// ./p 1 N
		Players clanA(atoi(argv[2]));

		clanA.readFile("ClanA.txt");

		cout << "Heap Sort..." << endl;
		clock_t elapsedTime = clock();
		clanA.heapSort();
		elapsedTime -= clock();
		cout << "Elapsed time: " << elapsedTime << " seconds" << endl;

		clanA.writeFile("A_sorted.txt");
	}
	else{
		cout << "Invalid number of inputs." << endl;

		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
