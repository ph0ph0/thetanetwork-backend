// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.23;

import "forge-std/Test.sol";
import "forge-std/StdJson.sol";
import "../../lib/forge-std/src/console2.sol";
import "../../src/ThetaChain/SignedMinter.sol";
import "../../src/ThetaChain/Token.sol";

contract ThetaTest is Test {
    using stdJson for string;

    address public deployer;
    address public testUser;
    address public manager;
    address public payloadSigner;
    SignedMinter public signedMinter;
    Token public token;

    // Used to create addresses
    uint256 _addressSeed = 123456789;

    // Fork Identifiers
    uint256 public fork;

    function makeAddress(string memory label) public returns (address) {
        address addr = vm.addr(_addressSeed);
        vm.label(addr, label);
        _addressSeed++;
        return addr;
    }

    function setUp() public {

        testUser = makeAddress("TestUser");
        vm.deal(testUser, 1000 ether);

        deployer = makeAddress("Owner");
        vm.deal(deployer, 1000 ether);

        manager = makeAddress("Manager");
        vm.deal(manager, 1000 ether);

        payloadSigner = vm.envAddress("PAYLOAD_SIGNER_ADDRESS");

        vm.startPrank(deployer, deployer);

        // Deploy Token
        token = new Token(deployer);

        // Deploy SignedMinter
        signedMinter = new SignedMinter(address(token), payloadSigner);

        // Set signed minter on PBT
        token.setSignedMinter(address(signedMinter));
        vm.stopPrank();
    }

    function test_Verify() external {
        vm.startPrank(deployer);

        bytes memory rawSig =
            hex"9a32f7acce70206b433e7ef80fafbd60c5e3d67b7dc9175271342dc8de06834d5eac982d1b40754bd7b00fe157ad773d4b3de5618c708998a7b5497143d3d84a1b";

        uint256 tokenAmount = 100000;
        address recipient = 0x590A1ADd90cbC6a0B53346b2CF8a78ebdaC24f02;

        bytes32 message = keccak256(abi.encodePacked(tokenAmount, recipient));
        // address recoveredAddress = signedMinter.recoverSigner(message, rawSig);
        bool verified = signedMinter._verify(rawSig, tokenAmount, recipient);
        // console2.log("Recovered Address:", recoveredAddress);

        assertEq(verified, true);
        // assertEq(recoveredAddress, vm.envAddress("PAYLOAD_SIGNER_ADDRESS"));

        vm.stopPrank();
    }

    function test_Mint() external {
        vm.startPrank(deployer);

        bytes memory rawSig =
            hex"9a32f7acce70206b433e7ef80fafbd60c5e3d67b7dc9175271342dc8de06834d5eac982d1b40754bd7b00fe157ad773d4b3de5618c708998a7b5497143d3d84a1b";

        uint256 tokenAmount = 100000;
        address recipient = 0x590A1ADd90cbC6a0B53346b2CF8a78ebdaC24f02;

        uint256 balBefore = token.balanceOf(recipient);
        signedMinter.mint(rawSig, tokenAmount, recipient);
        uint256 balAfter = token.balanceOf(recipient);

        assertEq(balBefore + tokenAmount, balAfter);

        vm.stopPrank();
    }
}
