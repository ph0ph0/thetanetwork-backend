from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import json

PRIVATE_KEY = '0xcf038c8a292755cdd249ca744a1d8767339d91e271ad0cc78a3bc3b3b70d0f14'

def generate_signed_message(recipient: str, valuation: int) -> dict:
    if not Web3.is_address(recipient):
        raise ValueError("Invalid Ethereum address")

    if not isinstance(valuation, int) or valuation < 0:
        raise ValueError("Valuation must be a positive integer")

    # Create the message hash the same way as in Solidity
    message = Web3.solidity_keccak(['uint256', 'address'], [valuation, recipient])
    
    # Create an Account object from the private key
    account = Account.from_key(PRIVATE_KEY)
    
    # Sign the message
    signed_message = account.sign_message(encode_defunct(message))
    
    # Prepare the result
    result = {
        "message": {
            "recipient": recipient,
            "valuation": valuation
        },
        "signature": signed_message.signature.hex(),
        "signer": account.address
    }
    
    return result[signature]

if __name__ == "__main__":
    example_usage()

# Example usage
# if __name__ == "__main__":
    # recipient_address = "0x590A1ADd90cbC6a0B53346b2CF8a78ebdaC24f02"
    # valuation = 100000  # Example valuation (100,000)
    
    # try:
    #     signed_data = generate_signed_message(recipient_address, valuation)
    #     print("Signed Message:")
    #     print(json.dumps(signed_data, indent=2))
    # except ValueError as e:
    #     print(f"Error: {e}")