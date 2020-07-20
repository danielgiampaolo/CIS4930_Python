#include <cstdint>
#include <cstring>
#include <stdio.h>
#include <string>

extern "C"
{
    void update_fields(char **nodes, char ***edges, char* test);
    void add_node(const char **nodes, char **new_nodes, char *new_node);
    void add_edge(char ***edges, char ***new_edges);
    void del_node(char **nodes, char **new_nodes);
    void del_edge(char ***edges, char ***new_edges);
}

void update_fields(char **nodes, char ***edges, char* test, char **new_nodes) {

}

void add_node(const char **nodes, char **new_nodes, char *new_node){
    printf("\ninside add_node\n");

    // printing doesnt really work while server is running

    *new_nodes = new_node;

    //printf("printing\n");
    //printf("%c\n", (new_nodes[0])[0]);

    printf("\noutside add_node\n\n");
}

void del_node(char **nodes, char **new_nodes){

}

// add more fields as necessary

void add_edge(char ***edges, char ***new_edges){

}

void del_edge(char ***edges, char ***new_edges){

}