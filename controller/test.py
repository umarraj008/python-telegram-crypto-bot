import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey


def is_valid_solana_address(address):
    """Check if a Solana address is valid (both format and existence)"""
    
    # Check length and format using base58
    if len(address) != 44:
        return False
    
    try:
        decoded_address = base58.b58decode(address)
    except ValueError:
        return False  # If base58 decoding fails, address is invalid
    
    # Ensure the decoded address is 32 bytes long (Solana address length)
    if len(decoded_address) != 32:
        return False
    
    # Check if the address is a real Solana address (active on the blockchain)
    solana_client = Client("https://api.mainnet-beta.solana.com")  # Mainnet Solana RPC endpoint
    
    # Convert address to a Pubkey object
    pubkey = Pubkey.from_string(address)
    
    # Query the account info using the Pubkey object
    response = solana_client.get_account_info(pubkey)

    if response.value is not None:
        return True  # Address exists on the Solana blockchain
    return False  # Address doesn't exist or is not active on the blockchain

# Example usage
validAddress = is_valid_solana_address("DSXVmrBySfBcmdNDGQkk59hGwXhAKNjEwc4as8nfmysd")
invalidAddress = is_valid_solana_address("DSXVmrBfSfBcmffffffa59hGwXhAKNjEwc4astnfmysd")

print(f"VALID: {validAddress}")   # Should be True if the address exists on the blockchain
print(f"WRONG: {invalidAddress}")  # Should be False since this is not a valid address




# import base58

# def is_valid_solana_address(address):
#     """Check if a Solana address is valid"""
#     if len(address) != 44:
#         return False
#     try:
#         decoded_address = base58.b58decode(address)
#     except ValueError:
#         return False  # If the base58 decoding fails, the address is invalid
#     return len(decoded_address) == 32

# # Example invalid address (this is just a random string)
# validAddress = is_valid_solana_address("DSXVmrBySfBcmdNDGQkk59hGwXhAKNjEwc4as8nfmysd")
# invalidAddress = is_valid_solana_address("DSXVmrBfSfBcmffffffa59hGwXhAKNjEwc4astnfmysd")

# print(f"VALID: {validAddress}")
# print(f"WRONG: {invalidAddress}")