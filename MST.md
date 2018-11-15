# Plasma Cashflow: Merkle-Sum-Trees

There have been some confusions around Merkle-Sum-Trees proposed in Plasma Cashflow (see [Plasma Cashflow spec](https://hackmd.io/DgzmJIRjSzCYvl4lUjZXNQ?view#Constructing-a-transaction-tree))

In this post, a brief description of different Merkle-Trees will be presented, beside an explanation on what problem Merkle-Sum-Trees are trying to solve and how, based on our researches in FinalityLabs. You can find a working implementation of Merkle-Sum-Trees in Python and Solidity here: [https://github.com/finalitylabs/pymst](https://github.com/finalitylabs/pymst).

## Merkle-Tree

<img width="600px" src="https://upload.wikimedia.org/wikipedia/commons/9/95/Hash_Tree.svg"/>

In this case, having a proof of inclusion of a certain transaction doesn't mean that the same coin is not double spent elsewhere in the Merkle-Tree, so we have to download the entire tree of each block because the operator can cheat and put malicious transactions in the tree. (For example, the operator can put both transactions `Alice sent coin A to Bob` and `Alice sent coin A to Alice` in the tree and give Bob the inclusion proof of the first transaction without Bob being notified about the second transaction which is also included in the tree.)

Proof data of L3:
```
R Hash1-1
L Hash0
```

Verification:
```
currHash = Hash(L3) = Hash1-0
currHash = Hash(currHash + Hash1-1) # Appended to Right
currHash = Hash(Hash0 + currHash) # Appended to Left
return currHash == rootHash
```

## Sparse-Merkle-Tree

Plasma Cash proposed that we can force our transactions to be in fixed slots of the merkle-tree and therefore prevent the operator from putting malicious transactions in the tree (Because it is not possible to put two different transactions in the same slot  and all transactions that are in wrong slots would get invalidated by the Plasma contract). Therefore we do not need the Rs and Ls of regular merkle-tree proofs in Sparse-Merkle-Trees. Because we know where to go in the tree based on our coinId.

As an example, the operator can't inlcude both transactions  `Alice sent coin A to Bob` and `Alice sent coin A to Alice` in the tree because there is only one valid slot for coin A, and the operator can't put two transactions in the slot of coin A.

Example:

Proof data of L3:
```
Hash1-1
Hash0
```

Verification of L3:
```
coinId = 2 # L3
currHash = Hash(L3) = Hash1-0

index = coinId % 2 # => 0
coinId = coinId / 2
currHash = Hash(currHash + Hash1-1) # Appended to Right because index = 0

index = coinId % 2 # => 1
coinId = coinId / 2
currHash = Hash(Hash0 + currHash) # Appended to Left because index = 1

return currHash == RootHash
```

## Merkle-Sum-Tree

Because we are working with ranges of coins in Plasma Cashflow and not coin-ids, using a Sparse-Merkle-Tree is not feasible because we can't consider a specific slot for a transaction on a range of coins in a Sparse-Merkle-Tree. Therefore we are forced to use regular merkle-trees here, and the proofs should contain L & R directions in themselves.

The question is: How can we make sure that the operator is not cheating and is not double-spending your range of coins elsewhere in the tree?

The answer is Merkle-Sum-Tree. In Merkle-Sum-Trees we also add an extra number in each proof step which shows us how many coins were involved in corresponding hash.

Example:

Consider:
 - L1 with range 0 to 9: Alice sent coins **20 to 24** to Bob
 - L2 with range 10 to 14: Nothing happened with coins 10 to 14
 - L3 with range 15 to 29: Alice sent coins 15 to 29 to Alice
 - L4 with range 30 to 39: Nothing happened with coins 30 to 39

As you can see, leaf 0 contains an invalid transaction and it should be not possible for the operator to include both transactions in leaves 0 and 2 in the tree.

Proof data of L3:
```
R 10 Hash1-1
L 15 Hash0
```

Verification of L3:
```
currSize = L3.end - L3.start + 1 = 15
currHash = Hash(L3) = Hash1-0

currStart = 0
currEnd = 39

currHash = Hash(currHash + currSize + Hash1-1 + Hash1-1.size) # Appended to Right
currSize = currSize + Hash1-1.size
currEnd -= Hash1-1.size # Because by appending a bucket to the right side we are neglecting Hash1-1.size number of coins from the right side

currHash = Hash(Hash0 + Hash0.size + currHash + currSize) # Appended to Left
currSize = currSize + Hash0.size
currStart += Hash1-1.size # Because by appending a bucket to the left side we are neglecting Hash0.size number of coins from the left side

return currHash == rootHash && currSize == rootSize
	&& currStart == L3.start && currEnd == L3.end
```

Using this algorithm, the verification process of the invalid transaction in L0 fails as the state of the algorithm ends up with `currStart = 0` and `currEnd = 9` 
