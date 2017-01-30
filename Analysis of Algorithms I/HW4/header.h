#include <iostream>
#include <fstream>
#include <string>

using namespace std;

//-- HASH --//

class Hash{
private: //-- private variables
	string* hashTable;
	unsigned int totalEntries;

public: //-- public variables
	int _tableSize;
	int collision;

private: //-- private methods
	int hashFunc(const string & str) const{
		unsigned long long int val = 1;

		for (int iii = 0; iii < _tableSize; ++iii){
			if (str[iii] == '\0') //IF at the end of string
				break;
			if (iii % 5 == 0) //(every 5 steps, take the modulus to avoid overflow)
				val %= _tableSize;

			val *= str[iii];
		}

		return val %= _tableSize;
	}

	static bool isEmpty(const string & str){
		return str == "*" || str == "";
	}

	
public: //-- public methods
	Hash(int tableSize){
		collision = 0;
		_tableSize = tableSize;
		totalEntries = 0;

		hashTable = new string[_tableSize];
	}
	~Hash(){
		delete[] hashTable;
	}


	//-- INSERT --//

	bool insert(const string & str){
		collision = 0;

		if (totalEntries == _tableSize){ //IF hash table is full
			cout << "WARNING: There is no empty space in the hash table for the word: " << str << endl;
			return false;
		}

		if (retrieve(str) != -1){ //IF the word exists
			cout << "WARNING: The word '" << str << "' is already in the dictionary." << endl;
			return false;
		}
		

		//
		//IF the word does not exist in the hash table

		collision = 0;

		int key = hashFunc(str);

		while (!isEmpty(hashTable[key])){ //WHILE the slot is NOT empty to corresponding key
			++collision;
			/*
			// UNNECESSARY since the existence is checked before

			if (hashTable[key] == str){ //IF the word in the slot is the given word
				cout << "WARNING: The word '" << str << "' is already in the dictionary." << endl;
				return false;
			}
			*/

			++key;
			if (key >= _tableSize) //IF the key is equal to or exceeds the table size
				key %= _tableSize;
		}

		cout << "INSERT: The word '" << str << "' is put in the cell number: " << key << endl;

		hashTable[key] = str;
		++totalEntries;

		return true;
	}


	//-- RETRIEVE --//

	int retrieve(const string & str){
		collision = 0;

		int key = hashFunc(str);

		const int initial = key;
		while (hashTable[key] != str){
			++collision;

			++key;
			if (key >= _tableSize)
				key %= _tableSize;
			
			if (hashTable[key] == "" || key == initial){//IF the slot is empty and not deleted before OR key has iterated the whole table
				collision = 0;
				return -1;
			}
		}

		return key;
	}


	//-- REMOVE --//

	bool remove(const string & str){
		collision = 0;

		int key = hashFunc(str);

		const int initial = key;
		while (hashTable[key] != str){
			++collision;

			++key;
			if (key >= _tableSize)
				key %= _tableSize;

			if (key == initial){
				collision = 0;
				cout << "WARNING: The word '" << str << "' couldn't be found in the dictionary" << endl;
				return false;
			}
		}


		hashTable[key] = "*";//lazy delete
		--totalEntries;

		cout << "REMOVE: The word '" << str << "' is removed from the dictionary" << endl;

		return true;
	}


	//-- Spell Check --//

	void spell_checker(string str){
		char original;
		int matchCount = 0;

		for (unsigned int iii = 0; iii < str.size(); ++iii){
			original = str[iii];

			for (char jjj = 'a'; jjj <= 'z'; ++jjj){
				if (jjj == original)
					continue;

				str[iii] = jjj;

				if (retrieve(str) != -1){
					++matchCount;
					cout << (matchCount == 1 ? "" : ", ") << str;
				}
			}
		}

		if (matchCount == 0)
			cout << "NONE FOUND";
	}


	//-- Get Table --//

	const string * getTable(){
		return hashTable;
	}
};


//-- DICTIONARY --//

class Dictionary{
	enum Operation{INSERT, RETRIEVE, REMOVE, UNDEFINED};

private: //-- private variables
	Hash hash;

private: //-- private methods
	static Operation parse(string & left, string & right, char delim){
		int delimPos = left.find(delim);
		if (delimPos == string::npos)
			return UNDEFINED;
		
		right = left.substr(delimPos + 1);
		left = left.substr(0, delimPos);

		if (left == "insert")
			return INSERT;
		else if (left == "retrieve")
			return RETRIEVE;
		else if (left == "delete")
			return REMOVE;
		else
			return UNDEFINED;
	}

public: //-- public methods
	Dictionary(int N) : hash(N){}
	~Dictionary(){}


	//-- READ FILE & INTERPRET

	void readFile(const char * fileName){
		ifstream infile(fileName);
		if (!infile.is_open()){
			cout << "ERROR: Could not open input file" << endl;
			return;
		}

		string line, word;
		int key;
		unsigned int totalCollisions = 0;

		while (infile >> line){
			switch (parse(line, word, ':')){
			case INSERT:
				hash.insert(word);
				break;
			case RETRIEVE:
				key = hash.retrieve(word);

				if (key == -1){
					cout << "WARNING: The word '" << word << "' couldn't be found in the dictionary" << endl;
					cout << "Looking for possible suggestions..." << endl;
					cout << "SUGGESTIONS for " << word << ": ";
					hash.spell_checker(word);
					cout << endl;
				}
				else{ //IF found
					cout << "RETRIEVE: The word '" << word << "' found in the dictionary with index: " << key << endl;
				}
				
				break;
			case REMOVE:
				hash.remove(word);
				break;
			default:
				cout << "ERROR: Invalid line input" << endl;
				break;
			}//end of switch

			totalCollisions += hash.collision;

			cout << "COLLISIONS: " << hash.collision << endl;
			cout << "--------------------------------------" << endl;
		}//end of while

		cout << "--------------------------------------" << endl;
		cout << "TOTAL COLLISIONS: " << totalCollisions << endl;

		infile.close();
	}


	//-- WRITE TO FILE

	void writeFile(const char * fileName){
		ofstream outfile(fileName);
		if (!outfile.is_open()){
			cout << "ERROR: Could not open output file" << endl;
			return;
		}

		const string * table = hash.getTable();

		for (int iii = 0; iii < hash._tableSize; ++iii)
			outfile << iii << ":\t" << (table[iii] == "*" ? "" : table[iii]) << endl;

		outfile.close();
	}
};
