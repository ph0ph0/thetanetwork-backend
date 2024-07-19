pragma solidity ^0.8.23;

import "../../lib/openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol";
import "./Token.sol";
import "../../lib/openzeppelin-contracts/contracts/access/Ownable.sol";
import "../../lib/openzeppelin-contracts/contracts/utils/cryptography/MessageHashUtils.sol";

contract SignedMinter is Ownable {
    event SignatureVerified(address indexed recipient, bytes signature, uint256 tokenAmount, address payloadSigner);

    Token token;
    address payloadSigner;
    // TODO: Nonces

    constructor(address _tokenAddress, address _payloadSigner) Ownable(msg.sender) {
        token = Token(_tokenAddress);
        payloadSigner = _payloadSigner;
    }

    function setTokenAddress(address addr) external onlyOwner {
        token = Token(addr);
    }

    function mint(bytes memory signature, uint256 tokenAmount, address recipient) public {
        // Ensure the signer is authorised
        require(_verify(signature, tokenAmount, recipient), "Invalid signature");

        emit SignatureVerified(recipient, signature, tokenAmount, payloadSigner);
        // Mint tokens
        token.mint(recipient, tokenAmount);
    }

    function _verify(bytes memory signature, uint256 tokenAmount, address recipient) public view returns (bool) {
    bytes32 message = keccak256(abi.encodePacked(tokenAmount, recipient));
    bytes32 ethSignedMessageHash = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", message));
    address recoveredAddress = recoverSigner(ethSignedMessageHash, signature);
    return recoveredAddress == payloadSigner;
}

function recoverSigner(bytes32 ethSignedMessageHash, bytes memory signature) public pure returns (address) {
    require(signature.length == 65, "Invalid signature length");
    bytes32 r;
    bytes32 s;
    uint8 v;
    assembly {
        r := mload(add(signature, 32))
        s := mload(add(signature, 64))
        v := byte(0, mload(add(signature, 96)))
    }
    if (v < 27) {
        v += 27;
    }
    return ecrecover(ethSignedMessageHash, v, r, s);
}
}
