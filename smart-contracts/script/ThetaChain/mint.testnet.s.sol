// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "../../lib/forge-std/src/Script.sol";
import "../../lib/forge-std/src/console2.sol";
import "../../src/ThetaChain/SignedMinter.sol";
import "../../src/ThetaChain/Token.sol";

// forge script script/ThetaChain/mint.testnet.s.sol:Mint --rpc-url https://api.calibration.node.glif.io/rpc/v1 -vvvv --optimize --optimizer-runs 200 --via-ir -g 100000
contract Mint is Script {
    function run() external {
        uint256 deployerPrivKey = vm.envUint("PK1");
        address signedMinter = vm.envAddress("SIGNEDMINTER_ADDRESS");
        address playbackToken = vm.envAddress("PLAYBACKTOKEN_ADDRESS");

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
            hex"54bd977e8b46f329a42d1dd8ca295e2fa3488c2cf4ee3fcbcf3babd16faaabc87730fe1a6bb4f73d865835ecd076bf20b04f96ca16bfd50e5f4d8235833ce3b21c";

        uint256 tokenAmount = 1000000000000000000;
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
