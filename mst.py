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

class Bucket:
    def __init__(self, size, hashed):
        self.size = size
        self.hashed = hashed
        # Each node in the tree can have a parent, and a left or right neighbor.
        self.parent = None
        self.left = None
        self.right = None

class Leaf:
    def __init__(self, rng, data):
        self.rng = rng
        self.data = data

    def get_bucket(self):
        hashed = H(self.data) if self.data else b'\x00' * 32
        return Bucket(self.rng[1] - self.rng[0], hashed)

class ProofStep:
    def __init__(self, bucket, right):
        self.bucket = bucket
        self.right = right# Whether the bucket hash should be appended on the right side in this step (Default is left)

class MerkleSumTree:

    def __init__(self, leaves):
        """Initializes the Merkle-Sum-Tree"""
        self.leaves = leaves
        self.buckets = [l.get_bucket() for l in leaves]
        buckets = list(self.buckets)
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

    def verify_proof(root, leaf, proof):
        """Validates the supplied `proof` for a specific `leaf` according to the
        `root` bucket of Merkle-Sum-Tree."""
        rng = (sum([s.bucket.size for s in proof if not s.right]),
                root.size - sum([s.bucket.size for s in proof if s.right]))
        if rng != leaf.rng:
            # Supplied steps are not routing us to the range specified.
            return False
        curr = leaf.get_bucket()
        for step in proof:
            if step.right:
                hashed = H(encode(curr.size) + curr.hashed) + H(encode(step.bucket.size) + step.bucket.hashed)
            else:
                hashed = H(encode(step.bucket.size) + step.bucket.hashed) + H(encode(curr.size) + curr.hashed)
            curr = Bucket(curr.size + step.bucket.size, hashed)
        return curr.size == root.size and curr.hashed == root.hashed
