#include <cstdio>
#include <cstring>

extern "C"
{
// use struct to shorten parameter passing next
void update_fields(char **nodes, char ***edges, char *test);
bool add_node(struct State *state, const char *new_node);
int add_edge(char **nodes, char **edges, int num_nodes, int num_edges, char *new_from, char *new_to);
void del_node(struct State *state);
void del_edge(char **nodes, char **edges, int num_nodes, int num_edges, char *del_from, char *del_to);
}

struct Node {
    char *name;
    char *description;
    unsigned int descriptionLines;
};

struct State {
    struct Node *nodes;    // see above
    char **edges;          // [edge1_from, edge1_to, edge1_weight, edge2...]
    unsigned int num_nodes;
    unsigned int num_edges;
};

void update_fields(char **nodes, char ***edges, char *test, char **new_nodes) {
    // unsure how to approach in a simple way, so left empty on purpose
}

bool add_node(struct State *state, const char *new_node) {
    printf("\ninside add_node\n");

    // doesnt happen I think
    if (new_node == nullptr) {
        return false;
    }

    printf(" nodes: ...%d!\n\n", state->num_nodes);

    for (int i = 0; i < state->num_nodes; i++) {
        printf(" bruhhhh\n");
        if (strcmp(new_node, state->nodes[i].name) == 0) {
            printf("found a match\n");
            return false;
        }
    }

    printf("\n found no matches \n\n");

    return true;
}

void del_node(struct State *state) {
    printf("\ninside del_node\n");

    // edges is a 1D array and every 3 elements represents an edge

    char *edge_from, *edge_to, *cur_node, *weight;
    bool delete_node;

    //printf("checking num edges: %d!!!\n", num_edges);

    // checking nodes still have connections
    for (int j = 0; j < state->num_nodes; ++j) {
        cur_node = state->nodes[j].name;

        delete_node = true;
        // going to increment this to traverse **edges
        int edge_index = 0;

        for (int i = 0; i < state->num_edges; ++i) {
            edge_from = state->edges[edge_index++];
            edge_to = state->edges[edge_index++];
            weight = state->edges[edge_index++];
            // might just to ignore weight?
            // look into if I need to do something with it
            // currently here because then putting weight into
            // new array after function is done could be more work

            // find edges for the remaining nodes

            //printf("checking %s and %s\n", edge_from, edge_to);

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
    } else if (matched_from && !matched_to) {
        return 2;
    } else if (!matched_from && matched_to) {
        return 3;
    } else /*(!matched_from && !matched_to)*/ {
        // no matches (add both)
        return 4;
    }
}

void del_edge(char **nodes, char **edges, int num_nodes, int num_edges, char *del_from, char *del_to) {

    char *edge_from, *edge_to;
    bool delete_from = true, delete_to = true;

    // checking nodes still have connections

    int edge_index = 0;

    for (int i = 0; i < num_edges; ++i) {
        edge_from = edges[edge_index++];
        edge_to = edges[edge_index++];

        // find edges that contain the nodes of the deleted edge

        //printf("checking %s and %s\n", edge_from, edge_to);

        if (strcmp(del_from, edge_from) == 0 || strcmp(del_from, edge_to) == 0) {
            delete_from = false;
        }

        if (strcmp(del_to, edge_from) == 0 || strcmp(del_to, edge_to) == 0) {
            delete_to = false;
        }

        if (!delete_from && !delete_to) break;
    }

    if (delete_from || delete_to) {
        //printf("marking node %s for deletion\n", cur_node);
        //strncpy(cur_node, "\0", strlen(cur_node));

        char *cur_node;

        for (int i = 0; i < num_nodes; ++i) {
            cur_node = nodes[i];

            // delete_x = true means that
            // an edge containing the node was not found
            // right here, we find said node and mark it

            if (delete_from && strcmp(cur_node, del_from) == 0) {
                printf("marking node %s for deletion\n", cur_node);
                strncpy(cur_node, "\0", strlen(cur_node));
            }

            if (delete_to && strcmp(cur_node, del_to) == 0) {
                printf("marking node %s for deletion\n", cur_node);
                strncpy(cur_node, "\0", strlen(cur_node));
            }
        }
    }


}