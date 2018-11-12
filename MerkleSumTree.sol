pragma solidity ^0.4.24;

library MerkleSumTree {

  function verify(
    bytes proof,
    bytes32 rootHash, uint64 rootSize, // Root bucket
    bytes32 leafHash, uint64 leafStart, uint64 leafEnd // Leaf bucket
  )
    internal
    pure
    returns (bool)
  {
    // Each step is 41 bytes long. First 8 bytes represents number of steps.
    require((proof.length - 8) % 41 == 0, "Invalid proof.");

    // Current bucket
    uint64 currSize = leafEnd - leafStart;
    bytes32 currHash = leafHash;

    uint8 bucketLeftOrRight;
    uint64 bucketSize;
    bytes32 bucketHash;

    uint64 stepsCount = readUint64(proof, 0);
    uint16 stepPos = 8;

    for(uint i = 0; i < stepsCount; i++) {
        require(proof.length >= stepPos + 41, "Invalid proof.");

        bucketLeftOrRight = readUint8(proof, stepPos);
        bucketSize = readUint64(proof, stepPos + 1);
        bucketHash = readBytes32(proof, stepPos + 9);

        currSize = currSize + bucketSize;
        if(bucketLeftOrRight == 0)
          currHash = sha3(abi.encodePacked(bucketSize, bucketHash, currSize, currHash));
        else
          currHash = sha3(abi.encodePacked(currSize, currHash, bucketSize, bucketHash));

        stepPos += 41;
    }

    return currHash == rootHash && currSize == rootSize;
  }

}
