#!/usr/bin/python3

from pymst import MerkleSumTree, Leaf

if __name__ == '__main__':

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
