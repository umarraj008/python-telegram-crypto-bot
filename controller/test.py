import base58

def is_valid_solana_address(address):
    """Check if a Solana address is valid"""
    if len(address) != 44:
        return False
    try:
        decoded_address = base58.b58decode(address)
    except ValueError:
        return False  # If the base58 decoding fails, the address is invalid
    return len(decoded_address) == 32

# Example invalid address (this is just a random string)
address = "DSXVmrBySfBcmdNDGQkk59hGwXhAKNjEwc4as8nfmysd"

print(is_valid_solana_address(address))