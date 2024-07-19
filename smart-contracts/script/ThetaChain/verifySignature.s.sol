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
            hex"98c1a1a70968c78ef1b4152f181c0b4bbdc889f4c0620dad5a2522d26b846c2b52f55ef66d4cb76966bf50b1e5461e0ba37c265f1c512bfdeda83d2505a3cc2c1b";

        uint256 tokenAmount = 58000000000000000000;
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
