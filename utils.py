# utils.py

import base58
import re
from datetime import datetime
from typing import List

def log(msg):
    """
    Logs a message to the console with a timestamp.

    The timestamp is formatted as 'YYYY-MM-DD HH:MM:SS.mmm' (to milliseconds)
    for easier tracking of events during runtime.

    Args:
        msg (str): The message to log.
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] {msg}")

def save_address(address):
    """
    Appends a given address to the 'addresses.txt' file.

    Each address is written on a new line. If the file does not exist,
    it will be created automatically.

    Args:
        address (str): The address to be saved.
    """
    with open('addresses.txt', 'a') as f:
        f.write(address + '\n')

def address_exists(address):
    """
    Checks whether a given address already exists in the 'addresses.txt' file.

    Each line in the file is treated as a separate address. If the file does not exist,
    the function assumes no addresses have been saved yet and returns False.

    Args:
        address (str): The address to check for existence.

    Returns:
        bool: True if the address is already in the file, False otherwise.
    """
    try:
        with open('addresses.txt', 'r') as f:
            addresses = f.readlines()
        return any(line.strip() == address for line in addresses)
    except FileNotFoundError:
        return False
    
def extract_solana_address(text):
    """
    Extracts a Solana address from a given text using a regular expression.

    Solana addresses are base58-encoded strings typically between 32 and 44 characters long,
    excluding 0, O, I, and l to avoid visual ambiguity.

    Args:
        text (str): The text to search for a Solana address.

    Returns:
        str or None: The matched Solana address if found, otherwise None.
    """
    solana_address_pattern = r"[1-9A-HJ-NP-Za-km-z]{32,44}"
    match = re.search(solana_address_pattern, text)
    return match.group(0) if match else None

def is_valid_solana_address(address):
    """
    Validates whether a given string is a properly formatted Solana address.

    A valid Solana address is a base58-encoded string that decodes to exactly 32 bytes.
    Typically, such addresses are 43 or 44 characters long.

    Args:
        address (str): The Solana address to validate.

    Returns:
        bool: True if the address is valid, False otherwise.
    """
    if len(address) not in (43, 44):
        return False
    try:
        decoded_address = base58.b58decode(address)
    except ValueError:
        return False  # Base58 decoding failed
    return len(decoded_address) == 32

def find_possible_split_parts(text: str) -> List[str]:
    """
    Searches for two consecutive base58 strings in the text that, when combined, form a valid Solana address.

    This function looks for base58-encoded tokens in the input text and attempts to find two consecutive tokens 
    that together create a valid Solana address (base58 string of length between 32 and 44 bytes). 
    It returns the two parts as a list if a valid pair is found, otherwise, it returns an empty list.

    Args:
        text (str): The text to search for consecutive base58 strings.

    Returns:
        List[str]: A list containing two strings (the address parts) if a valid Solana address is formed,
                   otherwise, an empty list.
    """
    BASE58_REGEX = r"[1-9A-HJ-NP-Za-km-z]+" 
    tokens = re.findall(BASE58_REGEX, text)
    for i in range(len(tokens) - 1):
        combined = tokens[i] + tokens[i + 1]
        if 32 <= len(combined) <= 44 and is_valid_solana_address(combined):
            return [tokens[i], tokens[i + 1]]
    return []

def combine_solana_address_parts(text):
    """
    Combines two Solana address parts found in the text into a single address.

    The function searches for two base58-encoded address parts in the given text. 
    If exactly two parts are found, they are concatenated to form a valid Solana address.
    If there are not exactly two parts, an empty string is returned.

    Args:
        text (str): The text containing potential Solana address parts.

    Returns:
        str: The combined Solana address if two valid address parts are found; 
             otherwise, an empty string.
    """
    parts = re.findall(r"[1-9A-HJ-NP-Za-km-z]{16,44}", text)

    if len(parts) == 2:
        return parts[0] + parts[1]
    return ""

async def find_group_chat_id(client):
    """
    Finds and returns the ID of the first group chat that the client is part of.
    """
    all_chats = await client.get_dialogs()
    for chat in all_chats:
        if chat.is_group:
            return f"Group Name: {chat.name} | Group ID: {chat.id}"

async def find_user_id(client, username=""):
    """
    Retrieves the user ID for a given username.
    """
    user = await client.get_entity(username)
    return user.id

async def find_channel_id(client, channel_name):
    """
    Retrieves the chat ID for a given channel name.
    """
    all_chats = await client.get_dialogs()
    for chat in all_chats:
        if chat.name == channel_name:
            return chat.id
    return None