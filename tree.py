#!/usr/bin/python3

import hashlib
import struct

# Hash function (Currently SHA256)
def H(data):
    return hashlib.sha256(data).digest()

# Encode a uint64 to bytes
def encode(num):
    return struct.pack(">Q", num)

def decode(bts):
    return struct.unpack(">Q", bts)[0]

TREE_SIZE = 100 # 2 ** 128

class Bucket:
    def __init__(self, size, data):
        self.size = size
        self.data = data
        self.parent = None
        self.left = None
        self.right = None

class ProofStep:
    def __init__(self, bucket, right):
        self.bucket = bucket
        self.right = right

class MerkleSumTree:

    def __init__(self, buckets):
        self.buckets = list(buckets)
        while len(buckets) != 1:
            new_buckets = []
            while buckets:
                if len(buckets) >= 2:
                    b1 = buckets.pop(0)
                    b2 = buckets.pop(0)
                    size = b1.size + b2.size
                    data = H(encode(b1.size) + b1.data) + H(encode(b2.size) + b2.data)
                    b = Bucket(size, data)
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
        curr = self.buckets[index]
        proof = []
        while curr.parent:
            right = True if curr.right else False
            bucket = curr.right if curr.right else curr.left
            curr = curr.parent
            proof.append(ProofStep(bucket, right))
        return proof

    def verify_proof(root, bucket, proof):
        curr = bucket
        for step in proof:
            if step.right:
                data = H(encode(curr.size) + curr.data) + H(encode(step.bucket.size) + step.bucket.data)
            else:
                data = H(encode(step.bucket.size) + step.bucket.data) + H(encode(curr.size) + curr.data)
            curr = Bucket(curr.size + step.bucket.size, data)
        return curr.size == root.size and curr.data == root.data


if __name__ == '__main__':
    
    buckets = [Bucket(4, b""),
                Bucket(6, b"tx1"),
                Bucket(5, b""),
                Bucket(5, b"tx2"),
                Bucket(50, b"tx3"),
                Bucket(20, b""),
                Bucket(10, b"tx4")]

    tree = MerkleSumTree(buckets)

    root = tree.get_root()
    bucket = tree.buckets[3]
    proof = tree.get_proof(3)
    print(MerkleSumTree.verify_proof(root, bucket, proof))
