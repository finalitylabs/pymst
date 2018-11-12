#!/usr/bin/python3

import hashlib
import struct

def H(data):
    """Hash function (Currently SHA256)"""
    return hashlib.sha256(data).digest()

def encode(num):
    """Encodes uint64 to bytes"""
    return struct.pack(">Q", num)

def decode(bts):
    """Decodes bytes to uint64"""
    return struct.unpack(">Q", bts)[0]

TREE_SIZE = 2 ** 64

class Bucket:
    def __init__(self, size, hashed):
        self.size = size
        self.hashed = hashed
        # Each node in the tree can have a parent, and a left or right neighbor.
        self.parent = None
        self.left = None
        self.right = None

class ProofStep:
    def __init__(self, bucket, right):
        self.bucket = bucket
        self.right = right# Whether the bucket hash should be appended on the right side in this step (Default is left)

class MerkleSumTree:

    def __init__(self, buckets):
        """Initializes the Merkle-Sum-Tree"""
        self.buckets = list(buckets)
        while len(buckets) != 1:
            new_buckets = []
            while buckets:
                if len(buckets) >= 2:
                    b1 = buckets.pop(0)
                    b2 = buckets.pop(0)
                    size = b1.size + b2.size
                    hashed = H(encode(b1.size) + b1.hashed) + H(encode(b2.size) + b2.hashed)
                    b = Bucket(size, hashed)
                    b1.parent = b2.parent = b
                    b1.right = b2
                    b2.left = b1
                    new_buckets.append(b)
                else:
                    new_buckets.append(buckets.pop(0))
            buckets = new_buckets
        self.root = buckets[0]

    def get_root(self):
        return self.root

    def get_proof(self, index):
        """Gets inclusion/exclusion proof of a bucket in the specified index"""
        curr = self.buckets[index]
        proof = []
        while curr.parent:
            right = True if curr.right else False
            bucket = curr.right if curr.right else curr.left
            curr = curr.parent
            proof.append(ProofStep(bucket, right))
        return proof

    def verify_proof(root, bucket, range, proof):
        """Validates the supplied `proof` for a specific `bucket` in a desired
        `range` by the `root` bucket of the Merkle-Sum-Tree."""
        rng = (sum([s.bucket.size for s in proof if not s.right]),
                root.size - sum([s.bucket.size for s in proof if s.right]))
        if rng != range:
            # Supplied steps are not routing us to the range specified.
            return False
        curr = bucket
        for step in proof:
            if step.right:
                hashed = H(encode(curr.size) + curr.hashed) + H(encode(step.bucket.size) + step.bucket.hashed)
            else:
                hashed = H(encode(step.bucket.size) + step.bucket.hashed) + H(encode(curr.size) + curr.hashed)
            curr = Bucket(curr.size + step.bucket.size, hashed)
        return curr.size == root.size and curr.hashed == root.hashed


if __name__ == '__main__':

    buckets = [Bucket(4, b""), # (0, 4)
                Bucket(6, b"tx1"), # (4, 10)
                Bucket(5, b""), # (10, 15)
                Bucket(5, b"tx2"), # (15, 20)
                Bucket(50, b"tx3"), # (20, 70)
                Bucket(20, b"tx4"), # (70, 90)
                Bucket(TREE_SIZE - 90, b"")] # (90, TREE_SIZE)

    tree = MerkleSumTree(buckets)

    root = tree.get_root()
    bucket = tree.buckets[3]
    rng = (15, 20) # Desired range for bucket 3
    proof = tree.get_proof(3)
    print(MerkleSumTree.verify_proof(root, bucket, rng, proof))
