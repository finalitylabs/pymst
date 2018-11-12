#!/usr/bin/python3

from mst import MerkleSumTree, Leaf

if __name__ == '__main__':

    TREE_SIZE = 2 ** 64

    leaves = [Leaf((0, 4), None), # None means the leaf is empty.
                Leaf((4, 10), b"tx1"),
                Leaf((10, 15), None),
                Leaf((15, 20), b"tx2"),
                Leaf((20, 70), b"tx3"),
                Leaf((70, 90), b"tx4"),
                Leaf((90, TREE_SIZE), None)]

    tree = MerkleSumTree(leaves)

    root = tree.get_root()
    leaf = tree.leaves[3]
    proof = tree.get_proof(3)
    print(MerkleSumTree.verify_proof(root, leaf, proof))
