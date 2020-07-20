#include <stddef.h>

#include <sstream>

/*
while(std::getline(ss, token, ',')) {
    std::cout << token << '\n';
}
*/

Ext_Struct PerfRead;

void init(void)
{
    // testing
    PerfRead.nodes = [[["t"]]];
    PerfRead.edges = [[[["5"]]]];
}

// nvm

typedef struct {
  char*** nodes;                         
  char**** edges;                          
} Ext_Struct;

extern Ext_Struct PerfRead;

extern void read(void);