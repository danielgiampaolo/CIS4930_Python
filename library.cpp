#define PY_SSIZE_T_CLEAN
#include <stdio.h>

extern "C" void cipher(const char *msg, char *buffer, int msg_len)
{
  const char *hello = "hello";

  for (unsigned int i = 0; i < msg_len; i++) {
      buffer[i] = hello[i % 5];
  }
}

struct Node {
  char *Name;
  char **Description;
  unsigned int DescriptionLines;
};

extern "C" void rename_node(struct Node *nodes, int length) {
  for (size_t i = 0; i < length; i++) {
    printf("INDEX: %lu\n", i);
    printf("  - Name: %s\n", nodes[i].Name);
    printf("  - Description:\n");

    for (size_t j = 0; j < nodes[i].DescriptionLines; j++) {
      printf("    %lu)  \"%s\"\n", j + 1, nodes[i].Description[j]);
    }
  }
}
