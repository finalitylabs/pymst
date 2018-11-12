# pymst - Merkle-Sum-Tree in Python

## Usage:

Here is an example of creating a Merkle-Sum-Tree of size 2^64, getting the proof
for 3rd leaf and verifying it.

```py
from pymst import MerkleSumTree, Leaf

TREE_SIZE = 2 ** 64

leaves = [Leaf((0, 4), None), # None means the leaf is empty.
            Leaf((4, 10), b"tx1"),
            Leaf((10, 15), None),
            Leaf((15, 20), b"tx2"),
            Leaf((20, 90), b"tx4"),
            Leaf((90, TREE_SIZE), None)]

tree = MerkleSumTree(leaves)

root = tree.get_root()
proof = tree.get_proof(3)

if MerkleSumTree.verify_proof(root, tree.leaves[3], proof):
  print("Proof is valid!")
else:
  print("Proof is not valid!")
```
