// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "../../lib/forge-std/src/Script.sol";
import "../../lib/forge-std/src/console2.sol";
import "../../src/ThetaChain/SignedMinter.sol";
import "../../src/ThetaChain/Token.sol";

// forge script script/ThetaChain/deploySignedMinterAndToken.s.sol:DeployScript --rpc-url https://api.calibration.node.glif.io/rpc/v1 -vvvv --optimize --optimizer-runs 200 -g 100000
contract DeployScript is Script {
    function run() external {
        // deploy vision contract
        // update oracle contract whitelist so vision contract can call it

        // Get the privKey from the env var testnet values
        address deployer = vm.envAddress("PK1_ADDRESS");
        uint256 deployerPrivKey = vm.envUint("PK1");

        address payloadSigner = vm.envAddress("PAYLOAD_SIGNER_ADDRESS");

        // // Tell F to send txs to the BC
        vm.startBroadcast(deployerPrivKey);

        // Deploy the contract and set deployer token address temporarily
        SignedMinter signedMinter = new SignedMinter(deployer, payloadSigner);
        // Output the contract address for ease of access!
        console2.log("signedMinter contract address", address(signedMinter));

        // SignedMinter sM = SignedMinter(0xF00DF8031E2e20F5334A3a4A0FbAaD156B6E58c7);

        // // Deploy Token
        // Token token = new Token(address(sM));
        // // Output the contract address for ease of access!
        // console2.log("token contract address", address(token));

        // // Set the token address in the signedMinter contract
        // sM.setTokenAddress(address(token));
        // console2.log("deployerAddress", deployer);

        vm.stopBroadcast();
    }
}
