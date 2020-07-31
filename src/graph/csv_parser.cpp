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


struct Ext_Struct {
    char** nodes;
    char*** edges;
    int node_size;
    int edge_size;
};

struct Desc_Struct {
    char*** descriptions;
    int nodes_read;
    int* desc_num;
};



extern Ext_Struct Read;

extern "C" void read(const char* data, struct Ext_Struct* Perf);
extern "C" void read_desc(const char* data, struct Desc_Struct* PerfRead);
extern "C" void dealloc_read(struct Ext_Struct* PerfRead);
extern "C" void dealloc_desc(struct Desc_Struct* PerfRead);

void read(const char* data, struct Ext_Struct* PerfRead)
{
    vector<char*> words;
    vector<char**> rows;
    set<string> node_set;
    int line_count = 0;
    int element_count = 0;
    std::stringstream ss;
    int index = 0;


    std::istringstream test_stream(data);
    string node1;
    string node2;
    string weight;
    string dummy;

    std::getline(test_stream, node1, ',');
    std::getline(test_stream, weight, ',');
    std::getline(test_stream, node2, '\n'); //Clears the Node,Link,and Node header

    while (std::getline(test_stream, node1, ',')) {
        std::getline(test_stream, weight, ',');
        std::getline(test_stream, node2, '\r'); 
        std::getline(test_stream, dummy, '\n'); 

        while (node1.at(0) == ' ') // Erases any spaces that may exist
            node1.erase(0, 1);
        while (weight.at(0) == ' ')
            weight.erase(0, 1);
        while (node2.at(0) == ' ')
            node2.erase(0, 1);

        words.push_back((char*)malloc(node1.size() + 1 * sizeof(char)));
        words.push_back((char*)malloc(weight.size() + 1 * sizeof(char)));
        words.push_back((char*)malloc(node2.size() + 1 * sizeof(char)));

        char* letter_iter_a = words.at(index); //Points the pointers in the word vector to a random char*
        char* letter_iter_b = words.at(index + 1);
        char* letter_iter_c = words.at(index + 2);

        node_set.insert(node1); // Adds the node strings to the set
        node_set.insert(node2);

        for (int i = 0; i < node1.size(); i++) //Manually adds each character to their respective array
        {
            if(node1.at(i) != '\r')
            {
                *letter_iter_a = node1.at(i);
                letter_iter_a++;
            }

        }
        for (int i = 0; i < weight.size(); i++)
        {
            if(weight.at(i) != '\r')
            {
                *letter_iter_b = weight.at(i);
                letter_iter_b++;
            }
        }
        for (int i = 0; i < node2.size(); i++)
        {
            if(node2.at(i) != '\r')
            {
            *letter_iter_c = node2.at(i);
            letter_iter_c++;
            }
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
        cout << *it << endl;
    }
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

    //Loads how many edges and nodes we have so python can easily iterate through them
    PerfRead->node_size = node_set.size();
    PerfRead->edge_size = line_count;
}

void read_desc(const char* data, struct Desc_Struct* PerfRead)
{
    cout << "I'm in description read" << endl;

    std::stringstream ss;
    int line_count = 0;
    int index = 0;
    int old_index = 0;


    std::istringstream test_stream(data);
    string line;
    string desc;
    string desc_old;

    vector<char*> words;
    vector<char**> rows;
    vector<int>num;

    while (getline(test_stream, line))
    {
        istringstream desc_stream(line);
        while (getline(desc_stream, desc, ','))
        {
            words.push_back((char*)malloc(desc.size() + 1 * sizeof(char)));
            char* letter_iter_a = words.at(index); //Points the pointers in the word vector to a random char*

            for (int i = 0; i < desc.size(); i++) //Manually adds each character to their respective array
            {
                if(desc.at(i) != '\r')
                {
                    *letter_iter_a = desc.at(i);
                    letter_iter_a++;
                }
            }
            *letter_iter_a = '\0';
            index++;
        }
        num.push_back(index-old_index);
        line_count++;
        rows.push_back((char**)malloc((index - old_index) * sizeof(char*))); // Allocate an index for 3 strings. Ech index represents a row
        char** row = rows.at(rows.size() - 1);
        for (old_index; old_index < index; old_index++)
        {
            *row = words.at(old_index);
            row++;
        }
        *row = nullptr;
        row = nullptr;

    }


    PerfRead->descriptions = (char***)malloc(rows.size() * sizeof(char**));
    char*** desc_iter = PerfRead->descriptions;
    for (int i = 0; i < rows.size(); i++)
    {
        *desc_iter = rows.at(i);
        desc_iter++;
    }

    PerfRead->desc_num = (int*)malloc(num.size()*sizeof(int));
    auto iter = PerfRead->desc_num;
    for(int i = 0; i < num.size(); i++)
    {
        *iter = num.at(i);
        iter++;
    }

    iter = nullptr;

    *desc_iter = nullptr;
    desc_iter = nullptr;

    PerfRead->nodes_read = line_count;
}

void dealloc_read(struct Ext_Struct* PerfRead)
{
    auto iter = PerfRead->edges;
    for (int i = 0; i < PerfRead->edge_size; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            free(iter[i][j]);
        }
        free(iter[i]);
    }
    free(iter);

    auto iter2 = PerfRead->nodes;
    for (int j = 0; j < PerfRead->node_size; j++)
    {
            free(iter2[j]);
    }
    free(iter2);

}

void dealloc_desc(struct Desc_Struct* PerfRead)
{
    auto iter = PerfRead->descriptions;
    for (int i = 0; i < PerfRead->nodes_read; i++)
    {
        for (int j = 0; j < PerfRead->desc_num[i]; j++)
        {
            free(iter[i][j]);
        }
        free(iter[i]);
    }
    free(iter);

    int* del = PerfRead->desc_num;
    free(del);

}