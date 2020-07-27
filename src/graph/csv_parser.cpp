#include <stddef.h>
#include <cstdint>
#include <fstream>
#include <cstring>
#include <set>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
/*
while(std::getline(ss, token, ',')) {
    std::cout << token << '\n';
}
*/

typedef struct {
    char** nodes;
    char*** edges;
} Ext_Struct;


void init(Ext_Struct* PerfRead)
{
    // testing
    PerfRead->nodes = nullptr;
    PerfRead->edges = nullptr;
}


extern void read(const char* Ext_Struct);

void read(const char* data, Ext_Struct* PerfRead)
{
    cout << "Made it inside" << endl;
    init(PerfRead);
    vector<char*> words;
    vector<char**> rows;
    set<string> node_set;
    int letter_a_count = 0;
    int letter_b_count = 0;
    int letter_c_count = 0;
    int line_count = 0;
    int element_count = 0;
    std::stringstream ss;
    int index = 0;


    std::istringstream test_stream(data);
    string node1;
    string node2;
    string weight;


    std::getline(test_stream, node1, ',');
    std::getline(test_stream, weight, ',');
    std::getline(test_stream, node2, '\n'); //Clears the Node,Link,and Node header

    while (std::getline(test_stream, node1, ',')) {
        std::getline(test_stream, weight, ',');
        std::getline(test_stream, node2, '\n');

        while (node1.at(0) == ' ') // Erases any spaces that may exist
            node1.erase(0, 1);
        while (weight.at(0) == ' ')
            weight.erase(0, 1);
        while (node2.at(0) == ' ')
            node2.erase(0, 1);

        letter_a_count += node1.size(); // Idea was to allocate memory for bigger names but that may bee too difficult
        letter_b_count += weight.size();
        letter_c_count += node2.size();
        words.push_back((char*)malloc(25 * sizeof(char))); // As of right now it holds 24 chars plus the null operator
        words.push_back((char*)malloc(25 * sizeof(char)));
        words.push_back((char*)malloc(25 * sizeof(char)));

        char* letter_iter_a = words.at(index); //Points the pointers in the word vector to a random char*
        char* letter_iter_b = words.at(index + 1);
        char* letter_iter_c = words.at(index + 2);

        node_set.insert(node1); // Adds the node strings to the set
        node_set.insert(node2);

        for (int i = 0; i < node1.size(); i++) //Manually adds each character to their respective array
        {
               
            *letter_iter_a = node1.at(i);
             letter_iter_a++;
            
        }
        for (int i = 0; i < weight.size(); i++)
        {

            *letter_iter_b = weight.at(i);
            letter_iter_b++;
        }
        for (int i = 0; i < node2.size(); i++)
        {
                *letter_iter_c = node2.at(i);
                letter_iter_c++;
        }
        *letter_iter_a = '\0';
        *letter_iter_b = '\0';
        *letter_iter_c = '\0';

        rows.push_back((char**)malloc(3 * sizeof(char*))); // Allocate an index for 3 strings. Ech index represents a row
        char** row = rows.at(index / 3);
        *row = words.at(index); 
        row++;
        *row = words.at(index + 1);
        row++;
        *row = words.at(index + 2);
        row++;

        index = index + 3;
        line_count++;
    }
    
    //Inserts rows char** to structure char***
    PerfRead->edges = (char***)malloc(rows.size() * sizeof(char**));
    char*** edges_iter = PerfRead->edges;
    for (int i = 0; i < rows.size(); i++)
    {
        *edges_iter = rows.at(i);
        edges_iter++;
    }

    //Section to insert all nodes in the set to the nodes**
    PerfRead->nodes = (char**)malloc(node_set.size() * sizeof(char*));
    words.clear();
    char** nodes_iter = PerfRead->nodes;
    index = 0;
    for (auto it = node_set.begin(); it != node_set.end(); it++)
    {
        words.push_back((char*)malloc(25 * sizeof(char)));
        char* letter_iter_a = words.at(index);
        for (int i = 0; i < (*it).size(); i++)
        {
            *letter_iter_a = (*it).at(i);
            letter_iter_a++;
        }
        (*letter_iter_a) = '\0';
        *nodes_iter = words.at(index);
        nodes_iter++;
        index++;
    }

    //Commented code is to test if the edges*** correctly got all the strings. Worked with test data i used
    /*auto help = PerfRead.edges;
    int i = 0;
    int k = 0;
    while (i != line_count)
    {
        while (k != 3)
        {
            cout << **help << endl;
            (*help)++;
            k++;
        }
        k = 0;
        help++;
        i++;
    }*/
}

