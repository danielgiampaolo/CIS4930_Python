#include <cstdio>
#include <cstring>

extern "C"
{
    void update_fields(char **nodes, char ***edges, char* test);
    bool add_node(const char **nodes, int node_num, const char *new_node);
    void add_edge(char ***edges, char ***new_edges);
    void del_node(char **nodes, char ***edges, int num_nodes, int num_edges, const char *deleted);
    void del_edge(char ***edges, char ***new_edges);
}

void update_fields(char **nodes, char ***edges, char* test, char **new_nodes) {

}

bool add_node(const char **nodes, int node_num, const char *new_node){
    printf("\ninside add_node\n");

    if(new_node == nullptr){
        return false;
    }

    for(int i = 0; i < node_num; i++){

        if(strcmp(new_node, nodes[i]) == 0){
            printf("found a match\n");
            return false;
        }
    }

    printf("\n found no matches \n\n");

    return true;
}

void del_node(char **nodes, char ***edges, int num_nodes, int num_edges, const char *deleted){
    printf("\ninside del_node\n");

    //new_nodes[2][1] = nullptr;

    printf("test: %s\n", nodes[0]);

    int edge_param = 2;

    for (int i = 0; i < num_edges; ++i) {
        for (int j = 0; j < edge_param; ++j) {
            // 2 edges to check, change to 3 when checking for 3rd param, weight
            printf("bruh\n");
            printf("%s\n", edges[i][j]);
            if(strcmp(edges[i][j], deleted) == 0){
                printf("found a match\n");
                //edges[i][j] = nullptr;

                // am I leaking memory? Questions for later
            }
        }
    }


    printf("\nafter del_node\n\n");
}

// add more fields as necessary

void add_edge(char ***edges, char ***new_edges){

}

void del_edge(char ***edges, char ***new_edges){

}