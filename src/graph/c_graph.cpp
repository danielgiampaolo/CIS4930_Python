#include <cstdio>
#include <cstring>

extern "C"
{
void update_fields(char **nodes, char ***edges, char *test);
bool add_node(const char **nodes, int node_num, const char *new_node);
int add_edge(char **nodes, char **edges, int num_nodes, int num_edges, char *new_from, char *new_to);
void del_node(char **nodes, char **edges, int num_nodes, int num_edges);
void del_edge(char ***edges, char ***new_edges);
}

void update_fields(char **nodes, char ***edges, char *test, char **new_nodes) {

}

bool add_node(const char **nodes, int node_num, const char *new_node) {
    printf("\ninside add_node\n");

    // doesnt happen I think
    if (new_node == nullptr) {
        return false;
    }

    for (int i = 0; i < node_num; i++) {

        if (strcmp(new_node, nodes[i]) == 0) {
            printf("found a match\n");
            return false;
        }
    }

    printf("\n found no matches \n\n");

    return true;
}

void del_node(char **nodes, char **edges, int num_nodes, int num_edges) {
    printf("\ninside del_node\n");

    // edges is a 1D array and every 2 elements are a pair of edges

    char *edge_from, *edge_to, *cur_node;
    bool delete_node;

    //printf("checking num edges: %d!!!\n", num_edges);

    // checking nodes still have connections
    for (int j = 0; j < num_nodes; ++j) {
        cur_node = nodes[j];

        delete_node = true;
        // going to increment this to traverse **edges
        int edge_index = 0;

        for (int i = 0; i < num_edges; ++i) {
            edge_from = edges[edge_index++];
            edge_to = edges[edge_index++];

            // find edges for the remaining nodes

            printf("checking %s and %s\n", edge_from, edge_to);

            if (strcmp(cur_node, edge_from) == 0) {
                delete_node = false;
                break;
            }

            if (strcmp(cur_node, edge_to) == 0) {
                delete_node = false;
                break;
            }
        }

        if (delete_node) {
            printf("marking node %s for deletion\n", cur_node);
            strncpy(cur_node, "\0", strlen(cur_node));
            // empty string is a mark for deletion
            // handled on python side
            // future versions of this code might allocate a new char **
            // in order to not have to filter it python side
        }

    }


    printf("\nafter del_node\n\n");
}

// add more fields as necessary
// or use struct

int add_edge(char **nodes, char **edges, int num_nodes, int num_edges, char *new_from, char *new_to) {

    int edge_index = 0;
    char *from_node = nullptr;
    char *to_node = nullptr;

    for (int i = 0; i < num_edges; ++i) {
        from_node = edges[edge_index++];
        to_node = edges[edge_index++];

        if (strcmp(from_node, new_from) == 0 && strcmp(to_node, new_to) == 0) {
            return 0;
        }
    }

    // To not allocate on C side, I will have multiple valid return values
    // 0 -> Do not add edge
    // 1 -> Add edge, no new nodes
    // 2 -> Add edge, add "new_from"
    // 3 -> Add edge, add "new_to"
    // 4 -> Add edge, add both nodes

    // duplicate edge was not found,
    // verify if there are new nodes

    // to tell when to go to 2/3/4
    bool matched_from = false;
    bool matched_to = false;
    char *cur_node = nullptr;

    for (int j = 0; j < num_nodes; ++j) {
        cur_node = nodes[j];

        if (strcmp(cur_node, new_from) == 0) {
            matched_from = true;
        }

        if (strcmp(cur_node, new_to) == 0) {
            matched_to = true;
        }
    }

    if (matched_from && matched_to) {
        // both nodes exist
        return 1;
    }
    else if (matched_from && !matched_to) {
        return 2;
    }
    else if (!matched_from && matched_to) {
        return 3;
    }
    else /*(!matched_from && !matched_to)*/ {
        // no matches (add both)
        return 4;
    }
}

void del_edge(char ***edges, char ***new_edges) {

}