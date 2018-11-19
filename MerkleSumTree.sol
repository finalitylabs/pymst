pragma solidity ^0.4.24;

contract MerkleSumTree {

  function readUint64(bytes data, uint256 offset) private pure returns (uint64) {
    offset += 32;
    uint64 result;
    assembly {result := div(mload(add(data, offset)), exp(256, 24))}
    return result;
  }

  function readUint8(bytes data, uint256 offset) private pure returns (uint8) {
    offset += 32;
    uint8 result;
    assembly {result := div(mload(add(data, offset)), exp(256, 31))}
    return result;
  }

  function readBytes32(bytes data, uint256 offset) private pure returns (bytes32) {
    offset += 32;
    bytes32 result;
    assembly {result := mload(add(data, offset))}
    return result;
  }

  function verify(
    bytes proof,
    bytes32 rootHash, uint64 rootSize,
    bytes32 leafHash, uint64 leafStart, uint64 leafEnd
  )
    public
    pure
    returns (bool)
  {
    require(proof.length % 41 == 0, "Invalid proof.");

    // Current bucket
    uint64 currSize = leafEnd - leafStart;
    bytes32 currHash = leafHash;
    uint64 currStart = 0;
    uint64 currEnd = rootSize;

    uint8 bucketLeftOrRight;
    uint64 bucketSize;
    bytes32 bucketHash;
    uint stepPos = 0;

    while(stepPos < proof.length) {

        bucketLeftOrRight = readUint8(proof, stepPos);
        bucketSize = readUint64(proof, stepPos + 1);
        bucketHash = readBytes32(proof, stepPos + 9);


        if(bucketLeftOrRight == 0) {
          currStart += bucketSize;
          currHash = keccak256(abi.encodePacked(bucketSize, bucketHash, currSize, currHash));
        }
        else {
          currEnd -= bucketSize;
          currHash = keccak256(abi.encodePacked(currSize, currHash, bucketSize, bucketHash));
        }
        currSize = currSize + bucketSize;

        stepPos += 41;
    }

    return currHash == rootHash && currSize == rootSize &&
            currStart == leafStart && currEnd == leafEnd;
  }

}
