// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "../../lib/forge-std/src/Script.sol";
import "../../lib/forge-std/src/console2.sol";
import "../../src/ThetaChain/SignedMinter.sol";
import "../../src/ThetaChain/Token.sol";

// forge script script/ThetaChain/mint.testnet.s.sol:Mint --rpc-url https://eth-sepolia.g.alchemy.com/v2/_yLxTeW4JJan3E71O5UcDqg6B4o-vlqO -vvvv --optimize --optimizer-runs 200 --via-ir --legacy
contract Mint is Script {
    function run() external {
        uint256 deployerPrivKey = vm.envUint("PK1");
        address signedMinter = vm.envAddress("SIGNEDMINTER_ADDRESS");
        address playbackToken = vm.envAddress("TOKEN_ADDRESS");

        vm.startBroadcast(deployerPrivKey);

        // NOTE: Deployer address is used here as otherwise we have to deploy a token contract (saves time)
        SignedMinter sM = SignedMinter(signedMinter);
        Token pT = Token(playbackToken);

        // bytes memory rawSig =
        //     hex"eb3d55a8155dc3beb09e8f70712a6f0d5ea81a8fdfca4191bf4c48c0b7a70433414e077e72e328e36a5e3bada66bc908c585f47f8703edd1c117c20b4f0710b61b";

        // uint256 tokenAmount = 100;
        // address recipient = 0x2dC8Bc53ECf1A59188e4c7fAB0c7bB57339F85e7;

        // Fabian's inputs
        bytes memory rawSig =
            hex"918be91e9592a2a6279dbb921ac315d60717fc6d0d5dccf1757cf1ee3703a2c56a1b849fc038350060d1c1f933e923ae4224f673803ac4a23419116f549d8ebf1c";

        uint256 tokenAmount = 90000000000000000000;
        address recipient = 0x590A1ADd90cbC6a0B53346b2CF8a78ebdaC24f02;

        // NOTE: Used to call `recoverStringFromRaw` directly
        // bytes32 message = keccak256(abi.encodePacked(tokenAmount, recipient));
        // address recoveredAddress = sM.recoverStringFromRaw(message, rawSig);
        // console2.log("Recovered Address:", recoveredAddress);

        // Recipient balance before
        uint256 balanceBefore = pT.balanceOf(recipient);
        // function mint(bytes memory signature, uint256 tokenAmount, address recipient) public
        sM.mint(rawSig, tokenAmount, recipient);
        // Recipient balance after
        uint256 balanceAfter = pT.balanceOf(recipient);

        console2.log("Recipient Balance Before:", balanceBefore);
        console2.log("Recipient Balance After:", balanceAfter);
        console2.log("Recipient Balance Difference:", balanceAfter - balanceBefore);

        vm.stopBroadcast();
    }
}
