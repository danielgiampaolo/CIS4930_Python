#include <cstdio>
#include <cstring>

extern "C" {
    // use struct to shorten parameter passing next
    void update_fields(char **nodes, char ***edges, char *test, char **new_nodes);
    bool add_node(struct State *state, const char *new_node);
    int add_edge(struct State *state, char *new_from, char *new_to);
    void del_node(struct State *state);
    void del_edge(struct State *state, char *del_from, char *del_to);
}

struct Node {
    char *name;
    char **description;
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
    //printf("\ninside add_node\n");

    // doesnt happen I think
    if (new_node == nullptr) {
        return false;
    }

    //printf(" nodes: ...%d!\n\n", state->num_nodes);

    for (int i = 0; i < state->num_nodes; i++) {
        //printf(" bruhhhh\n");
        if (strcmp(new_node, state->nodes[i].name) == 0) {
            //printf("found a match\n");
            return false;
        }
    }

    //printf("\n found no matches \n\n");

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

            // update, nodes changed to "\0" seem to stay that way
            // when re-entered in python, causing bugs
        }

    }


    printf("\nafter del_node\n\n");
}

// add more fields as necessary
// or use struct

/**
 * @param state         Current internal state
 * @param new_from      Edge's begin node
 * @param new_to        Edge's end node
 * @return              `0` if Do not add edge.
 *                      `1` if Add edge, don't add nodes.
 *                      `2` if Add edge, add "from" node only.
 *                      `3` if Add edge, add "to" node only.
 *                      `4` if Add edge, add both nodes.
 */
int add_edge(struct State *state, char *new_from, char *new_to) {
    char **edges = state->edges;
    struct Node *nodes = state->nodes;
    unsigned int num_edges = state->num_edges;
    unsigned int num_nodes = state->num_nodes;

    char *from_node = nullptr;
    char *to_node = nullptr;

    for (int i = 0; i < num_edges * 3;) {
        from_node = edges[i++];
        to_node = edges[i++];
        i++; // weight, dont worry about it

        if (strcmp(from_node, new_from) == 0 && strcmp(to_node, new_to) == 0) {
            // Edge is already in list, do not add
            return 0;
        }
    }

    // duplicate edge was not found, verify if there are new nodes

    // to tell when to go to 2/3/4
    bool matched_from = false;
    bool matched_to = false;

    for (int j = 0; j < num_nodes; ++j) {
        struct Node cur_node = nodes[j];

        if (strcmp(cur_node.name, new_from) == 0) {
            matched_from = true;
        }

        if (strcmp(cur_node.name, new_to) == 0) {
            matched_to = true;
        }
    }

    if (matched_from && matched_to) {
        // both nodes exist
        return 1;
    } else if (!matched_from && matched_to) {
        return 2;
    } else if (matched_from && !matched_to) {
        return 3;
    } else {
        // no matches (add both)
        return 4;
    }
}

void del_edge(struct State *state, char *del_from, char *del_to) {

    char *edge_from, *edge_to, *weight;
    bool delete_from = true, delete_to = true;

    // checking nodes still have connections

    int edge_index = 0;

    for (int i = 0; i < state->num_edges; ++i) {
        edge_from = state->edges[edge_index++];
        edge_to = state->edges[edge_index++];
        weight = state->edges[edge_index++];
        // ^^ might comment out later for a nice performance boost /s

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

        for (int i = 0; i < state->num_nodes; ++i) {
            cur_node = state->nodes[i].name;

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