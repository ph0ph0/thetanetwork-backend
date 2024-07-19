// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "../../lib/forge-std/src/Script.sol";
import "../../lib/forge-std/src/console2.sol";
import "../../src/ThetaChain/SignedMinter.sol";

// forge script script/ThetaChain/verifySignature.s.sol:VerifySignature --rpc-url https://api.calibration.node.glif.io/rpc/v1 -vvvv --optimize --optimizer-runs 200  --via-ir -g 100000
contract VerifySignature is Script {
    function run() external {
        address deployer = vm.envAddress("PK1_ADDRESS");
        uint256 deployerPrivKey = vm.envUint("PK1");
        address payloadSigner = vm.envAddress("PAYLOAD_SIGNER_ADDRESS");

        vm.startBroadcast(deployerPrivKey);

        // NOTE: Deployer address is used here as otherwise we have to deploy a token contract (saves time)
        SignedMinter sM = new SignedMinter(deployer, payloadSigner);

        bytes memory rawSig =
            hex"9a32f7acce70206b433e7ef80fafbd60c5e3d67b7dc9175271342dc8de06834d5eac982d1b40754bd7b00fe157ad773d4b3de5618c708998a7b5497143d3d84a1b";

        uint256 tokenAmount = 100000;
        address recipient = 0x590A1ADd90cbC6a0B53346b2CF8a78ebdaC24f02;
        // 0x590A1ADd90cbC6a0B53346b2CF8a78ebdaC24f02

        // NOTE: Used to call `recoverStringFromRaw` directly
        // bytes32 message = keccak256(abi.encodePacked(tokenAmount, recipient));
        // address recoveredAddress = sM.recoverStringFromRaw(message, rawSig);
        // console2.log("Recovered Address:", recoveredAddress);

        bool recoveredAddress = sM._verify(rawSig, tokenAmount, recipient);
        console2.log(recoveredAddress);

        vm.stopBroadcast();
    }
}
