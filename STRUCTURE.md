# Structure

## Internal State Management

### edges `Array`

```py
array_element = ["from", "to", "weight"]

example = [
  ["node 1", "node 2", 10],
  ["node 2", "node 3", 10]
]
```

### nodes `Array`

```py
array_element = [
  "internal_name",
  "Description, line 1",
  "Description, line 2",
  "..."
]

example = [
  [
    "node 1",
    "Router",
    "Room 2178"
  ]
]
```

### bold_edges `Array`

```py
array_element = ["from_node", "to_node"]

# To bolden the edge (node 1 -> node 2) and (node 2 -> node 3):
example = [
  ["node 1", "node 2"],
  ["node 2", "node 3"]
]
```
