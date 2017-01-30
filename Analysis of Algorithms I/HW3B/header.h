#ifndef _HEADER_P3_2_H
#define _HEADER_P3_2_H

#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <cmath>

using namespace std;

//-- Necessary Definitions --//

template<class T>
void exchange(T & a, T & b){
	T temp = a;
	a = b;
	b = temp;
}

struct Player{
	int id;
	long long int cp;
};


//-- Classes --//

class Players{
private:
	Player* playerArray;
	const int size;

private://private method(s)
	static void max_heapify(Player* arr, int index, const int heapSize){
		int left = 2 * index + 1,
			right = 2 * index + 2,
			max = index;

		if (left < heapSize && arr[left].cp > arr[max].cp)
			max = left;
		if (right < heapSize && arr[right].cp > arr[max].cp)
			max = right;

		if (max != index){
			exchange(arr[index], arr[max]);
			max_heapify(arr, max, heapSize);
		}
	}

public:
	Players(int N) : size(N){
		if (N < 0 || N > 1000000)
			playerArray = NULL;
		else
			playerArray = new Player[N];
	}
	~Players(){
		if (playerArray != NULL)
			delete[] playerArray;
	}


	bool readFile(const char * fileName){
		ifstream infile(fileName);
		if (!infile.is_open())
			return false;

		for (int iii = 0; iii < size; ++iii)
			infile >> playerArray[iii].id >> playerArray[iii].cp;

		infile.close();
		return true;
	}
	bool writeFile(const char * fileName){
		ofstream outfile(fileName);
		if (!outfile.is_open())
			return false;

		for (int iii = 0; iii < size; ++iii)
			outfile << playerArray[iii].id << '\t' << playerArray[iii].cp << endl;
		
		outfile.close();
		return true;
	}


	void heapSort(){
		for (int iii = size / 2 - 1; iii >= 0; --iii)
			max_heapify(playerArray, iii, size);

		
		for (int iii = size - 1; iii >= 0; --iii){
			exchange(playerArray[0], playerArray[iii]);
			max_heapify(playerArray, 0, iii);
		}
		
		//if (!ascending)
		//	reverse();
	}


	Player& operator[](unsigned int index){//reversed
		// //better to expect a segmentation error
		//if (index >= size)
		//	index %= size;
		
		//reversed, 0 -> size-1, size-1->0
		return playerArray[size - index - 1];
	}
	unsigned int getReversePosition(unsigned int index){
		return size - index - 1;
	}
	unsigned long long int getTotalCP(){
		unsigned long long int sum = 0;
		for (int iii = 0; iii < size; ++iii)
			sum += playerArray[iii].cp;

		return sum;
	}
	int getSize(){
		return size;
	}


	void reverse(){
		for (int iii = 0; iii < size / 2; ++iii)
			exchange(playerArray[iii], playerArray[size - iii - 1]);
	}
};


class Game{
	struct Log {
		unsigned int id;
		char attackerClan;
		unsigned int attacker;
		unsigned int attacked;
	};
	
private:
	Players clanA;
	Players clanB;

	Log* gameLogs;
	const int gameCount;

private: //Private Method(s)
	static void dealDamage(Player & attacker, unsigned int position1, Player & attacked, unsigned int position2){
		if (position1 == 0){ //leader
			attacker.cp += attacked.cp / 2;
			attacked.cp -= attacked.cp / 2;
		}
		else if (1 <= position1 && position1 <= 7){ //henchman
			attacker.cp += 500;
			attacked.cp -= 500;
		}
		else{ //soldier
			attacker.cp += 30 * (abs( int(log2(position1 + 1)) - int(log2(position2 + 1)) ) + 1);
			attacked.cp -= 120;
		}

		if (attacked.cp < 0)
			attacked.cp = 0;
		//if (attacker.cp < 0)
		//	attacker.cp = 0;
	}

public:
	Game() : clanA(10000), clanB(10000), gameCount(10000){
		clanA.readFile("ClanA.txt");
		clanB.readFile("ClanB.txt");

		cout << "Extracting game logs..." << endl;
		ifstream infile("gamelogs.txt");
		if (infile.is_open()){
			gameLogs = new Log[gameCount];

			for (int iii = 0; iii < gameCount; ++iii)
				infile >> gameLogs[iii].id
					   >> gameLogs[iii].attackerClan
					   >> gameLogs[iii].attacker
					   >> gameLogs[iii].attacked;

			infile.close();

			cout << "gamelogs.txt read." << endl;
		}
		else
			gameLogs = NULL;
	}
	~Game(){
		clanA.reverse();
		clanA.writeFile("A_results.txt");
	}

	void play(){
		cout << "Sorting clans..." << endl;
		clanA.heapSort();
		clanB.heapSort();
		
		cout << "Playing game... (may take a few minutes)" << endl;
		for (int iii = 0; iii < gameCount; ++iii){
			//cout << "\tRound: " << iii << endl;
			if (gameLogs[iii].attackerClan == 'A')
				dealDamage(clanA[ gameLogs[iii].attacker ],
						   clanA.getReversePosition(gameLogs[iii].attacker),
						   clanB[ gameLogs[iii].attacked ],
						   clanB.getReversePosition(gameLogs[iii].attacked));
			else//attackerClan == 'B'
				dealDamage(clanB[ gameLogs[iii].attacker ],
						   clanB.getReversePosition(gameLogs[iii].attacker),
						   clanA[ gameLogs[iii].attacked ],
						   clanA.getReversePosition(gameLogs[iii].attacked));

			clanA.heapSort();
			clanB.heapSort();
		}//end for

		cout << "Calculating total points..." << endl;
		unsigned long long int totalA = clanA.getTotalCP();
		unsigned long long int totalB = clanB.getTotalCP();

		cout << "ClanA: " << totalA << " CP" << endl;
		cout << "ClanB: " << totalB << " CP" << endl;

		cout << "The winner is "
			 << (totalA == totalB ? "noone. It is a tie." : (totalA > totalB ? "A." : "B."))
			 << endl;
	}
};


#endif
