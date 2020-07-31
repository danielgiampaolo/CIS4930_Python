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
  char**** edges;
} Ext_Struct;

Ext_Struct PerfRead;

void init(void)
{
    // testing
    PerfRead.nodes = ["t"];
    PerfRead.edges = [["5","6"]];
}

// nvm



extern Ext_Struct PerfRead;

extern void read(const char*);

void read(const char* data)
{

    std::string line;
    int line_count = 0;
    int element_count = 0;
    std::stringstream ss;


    std::istringstream test_stream(data);
    string node1;
    string node2;
    string weight;
    char ** row;


    /*strcpy brings a compiler error.
      Instead we have to use strcpy_s(char *restrict dest, rsize_t destsz, const char *restrict src);
    */
    /* Test cope with strcpy_s
    std::string str = "string";
    char *cstr = new char[str.length() + 1];
    strcpy_s(cstr,str.length(), str.c_str());
    // Nope doesnt work
    delete [] cstr;
    https://stackoverflow.com/questions/7352099/stdstring-to-char
    */
    while (std::getline(test_stream, node1, ',')){
      std::getline(test_stream, weight, ',');
      std::getline(test_stream, node2);


    }

    /*
      string idk = "asd";

    vector<char> test1(idk.begin(), idk.end());
    char* test2 = test1.data();

    vector<string> test3 = {"123", "1234"};
    const char** test4 = nullptr;

    for(int i = 0; i < test3.size(); i++){

      test4[i] = test3[i].data();

     }

    */


   /*
      Alternate idea, run a for loop for evey char in the 3 strings for char*.
      Then we appends those 3 strings to a char **(each column info).
      Then the char ** is appended to a char ***(row).
   */

}}