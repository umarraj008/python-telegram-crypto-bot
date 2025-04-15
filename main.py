from telethon import TelegramClient, events
from datetime import datetime
import asyncio
import re
import json
import base58
# from Bot import BotCommunicator
from typing import List

# Load configuration from the config.json file
def load_config():
    configFile = "config.json"

    with open(configFile, 'r') as f:
        return json.load(f)

# Load the configuration data
config = load_config()

# Your Telegram API details from the config file
api_id = config['api_id']
api_hash = config['api_hash']
phone_number = config['phone_number']
allowed_users = config['allowed_users']

# Trojan bot's chat ID or username
TROJAN_BOT_CHAT_ID = config['trojan_bot_chat_id']

# List of private channel invite links
channel_invite_links = config['channel_invite_links']

# Keep track of processed message IDs
processed_message_ids = set()
lastMessage = ""

# Set up the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Function to save address to a file
def save_address(address):
    with open('addresses.txt', 'a') as f:
        f.write(address + '\n')

# Function to check if the address already exists in the file
def address_exists(address):
    try:
        with open('addresses.txt', 'r') as f:
            addresses = f.readlines()
        return any(line.strip() == address for line in addresses)
    except FileNotFoundError:
        return False

def log(msg):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] {msg}")

def extract_solana_address(text):
    """Extract Solana address from the text using regex"""
    solana_address_pattern = r"[1-9A-HJ-NP-Za-km-z]{32,44}"
    match = re.search(solana_address_pattern, text)
    return match.group(0) if match else None

def is_valid_solana_address(address):
    """Check if a Solana address is a valid base58-encoded 32-byte string"""
    if len(address) not in (43, 44):
        return False
    try:
        decoded_address = base58.b58decode(address)
    except ValueError:
        return False  # Base58 decoding failed
    return len(decoded_address) == 32

def combine_solana_address_parts(text):
    """Combine two Solana address parts found in the text"""
    parts = re.findall(r"[1-9A-HJ-NP-Za-km-z]{16,44}", text)

    if len(parts) == 2:
        return parts[0] + parts[1]
    return ""

def find_possible_split_parts(text: str) -> List[str]:
    """
    Looks for two consecutive base58 strings that together form a valid Solana address.
    Returns a list with two parts if a valid pair is found, else empty list.
    """
    BASE58_REGEX = r"[1-9A-HJ-NP-Za-km-z]+" 
    tokens = re.findall(BASE58_REGEX, text)
    for i in range(len(tokens) - 1):
        combined = tokens[i] + tokens[i + 1]
        if 32 <= len(combined) <= 44 and is_valid_solana_address(combined):
            return [tokens[i], tokens[i + 1]]
    return []

# Function to forward filtered messages
# VERSION 1 (NO REMOVE DETECTION)
async def forward_messageV1(message):
    # List of filter words (keywords to avoid in URLs, etc.)
    filter_words = ['http', 'https', 'dexscreener', '.com']
    
    # Regular expression to detect Solana addresses (44 alphanumeric characters)
    address_pattern = r'\b[A-Za-z0-9]{44}\b'  # Matches 44 alphanumeric characters (Solana address format)
    
    # Split the message text into lines
    lines = message.text.splitlines()

    # Process each line in the message
    for line in lines:
        # Check if the line contains any of the filter keywords
        if any(keyword in line.lower() for keyword in filter_words):
            # print(f"Filtered line (contains keyword): {line}")
            continue  # Skip this line if it contains unwanted keywords
        
        # Search for all 44-character addresses in the line
        addresses = re.findall(address_pattern, line)
        
        # Process each address found
        for address in addresses:
            # Get the current time in a readable format
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # Check if the address has already been forwarded
            if not address_exists(address):
                # If the address is valid and not already saved, forward it
                print(f"[{current_time}] Found and forwarding address: {address}")
                await client.send_message(TROJAN_BOT_CHAT_ID, f"{address}")
                save_address(address)  # Save the address after forwarding
                return
            else:
                print(f"[{current_time}] Address {address} has already been forwarded. Skipping.")

# Function to forward filtered messages
# VERSION 2 (REMOVE WORD DETECTION)
async def forward_messageV2(message):
    def log(msg):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] {msg}")

    filter_words = ['http', 'https', 'dexscreener', '.com']
    address_pattern = r'\b[A-Za-z0-9]{44,}\b'
    dex_url_pattern = r'https://dexscreener[A-Za-z0-9]*\.com/solana/([A-Za-z0-9]{44,})\b'

    # Stop processing if it's a known scam/rug pull
    if "do not buy" in message.text.lower() or "insta rug" in message.text.lower() or "DO NOT BUY THIS IM FISHING FOR A BOT FRONT RUNNING THE CALLS WILL INSTA RUG DO NOT BUY" in message.text.lower() or "FISHING" in message.text.lower():
        log("This coin is flagged as a rug pull. Stopping processing.")
        return "This coin is flagged as a rug pull. Stopping processing."

    # Check if the message contains a word inside quotes (assumed to be the removal keyword)
    word_to_remove = None
    match = re.search(r'["“”\']([A-Za-z0-9]+)["“”\']', message.text)
    if match:
        word_to_remove = match.group(1)
        log(f"Found instruction to remove word: {word_to_remove}")

    # # Check for a DexScreener URL
    # dex_match = re.search(dex_url_pattern, message.text)
    # if dex_match:
    #     dex_address = dex_match.group(1)
    #     log(f"Found DexScreener address: {dex_address}")

    #     if word_to_remove:
    #         dex_address = dex_address.replace(word_to_remove, "")
    #         log(f"Cleaned DexScreener address: {dex_address}")

    #     if len(dex_address) == 44:  # Ensure it's still valid after removal
    #         log(f"Sending DexScreener address to client: {dex_address}")
    #         await client.send_message(TROJAN_BOT_CHAT_ID, f"{dex_address}")
    #         save_address(dex_address)
    #         return dex_address
    #     else:
    #         log(f"Invalid DexScreener address after removal: {dex_address}")

    # Process each line in the message for a Solana address
    for line in message.text.splitlines():
        if any(keyword in line.lower() for keyword in filter_words):
            continue  # Skip lines containing unwanted keywords

        addresses = re.findall(address_pattern, line)
        for address in addresses:
            cleaned_address = address

            # Remove the keyword from the address if needed
            if word_to_remove:
                cleaned_address = cleaned_address.replace(word_to_remove, "")
                log(f"Cleaned Solana address: {cleaned_address}")

            if len(cleaned_address) == 44 and not address_exists(cleaned_address):
                log(f"Found and forwarding Solana address: {cleaned_address}")
                await client.send_message(TROJAN_BOT_CHAT_ID, f"{cleaned_address}")
                save_address(cleaned_address)
                return cleaned_address
            else:
                log(f"Address {cleaned_address} has already been forwarded or is invalid. Skipping.")
                return f"Address {cleaned_address} has already been forwarded or is invalid. Skipping."

    return None  # If nothing was found

# VERSION 3 
# RUG DETECTION
# SAVES RUGS
# REMOVES KING
# SPLIT DETECTION
# SOLANA VALIDATE
# TIME PRINTING
async def forward_messageV3(message):
    # Initialize values
    rug_pull = False
    address = ""
    message_text = message.text

    # Remove URLs
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', message_text)

    # Check for rug-related words in text
    if any(word in text.lower() for word in ["rug", "do not buy", "rug pull", "insta rug", "fishing"]):
        rug_pull = True
                        
    # Remove all occurrences of the word "KING" from the text
    kingless_text = re.sub(r'king', '', text, flags=re.IGNORECASE)

    # Try extracting the address
    address = extract_solana_address(kingless_text)

    if not address:
        parts = find_possible_split_parts(kingless_text)

        if parts:
            address = parts[0] + parts[1]
            log(f"Detected split address parts and combined: {address}")

    if not address:
        address = combine_solana_address_parts(kingless_text)

    # If no address is found
    if not address:
        log(f"No address found")
        return None
                    
    # Validate Solana address
    if not is_valid_solana_address(address):
        log(f"Address {address} has already been forwarded or is invalid. Skipping.")
        return f"Address {address} has already been forwarded or is invalid. Skipping."

    # Check if address exists in addresses.txt
    if address_exists(address):
        log(f"Address {address} has already been forwarded or is invalid. Skipping.")
        return f"Address {address} has already been forwarded or is invalid. Skipping."

    # Save address
    save_address(address)

    # If rug pull dont forward
    if rug_pull:
        log(f"This coin is flagged as a rug pull.")
        return "This coin is flagged as a rug pull. Stopping processing."

    log(f"Found and forwarding Solana address: {address}")
    await client.send_message(TROJAN_BOT_CHAT_ID, address)
    return address

#Set up event handler to listen for new messages from the channels
@client.on(events.NewMessage(chats=channel_invite_links))  # Listen for new messages from multiple channels
async def handler(event):
    global lastMessage  

    message = event.message
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Normalize message text (remove extra spaces, newlines, etc.)
    message_text = message.text.strip() if message.text else ""

    # Check if message ID or content has already been processed
    if message.id in processed_message_ids or lastMessage == message_text:
        #print(f"[{current_time}] Message {message.id} already processed, skipping.")
        return  # Skip duplicate messages

   # If from group, check if it's from the correct username
    if event.is_group or (event.is_channel and not event.chat.broadcast):  # i.e., it's a megagroup
        sender = await message.get_sender()

        if sender is None:
            #print(f"[{current_time}] Message {message.id} has no sender, skipping.")
            return

        sender_username = sender.username.lower() if sender.username else None
        
        #print(f"Sender Username: {sender_username}")
        #print(f"[{current_time}] Message {message.id} | {message.text}")

        if sender_username not in [username.lower() for username in allowed_users]:
            #print(f"[{current_time}] Message {message.id} not from target username, skipping.")
            return
        #print(f"[{current_time}] SPECIAL Message FROM ALLOWED USER {message.id} | {message.text}")

    # Update last message content **before processing**
    lastMessage = message_text
    processed_message_ids.add(message.id)

    # TODO add from channel/chat and username
    print(f"[{current_time}] Received Message: {message.id} | {sender_username}")
    
    await forward_messageV3(message)  # Forward the message immediately

async def find_group_chat_id():
    all_chats = await client.get_dialogs()
    for chat in all_chats:
        if chat.is_group:
            return f"Group Name: {chat.name} | Group ID: {chat.id}"

async def find_user_id(username=""):
    user = await client.get_entity(username)
    return user.id

async def find_channel():
    all_chats = await client.get_dialogs()
    for chat in all_chats:
        if chat.name == "Sniper King Bot":
            return chat.id
    print("Channel not found.")
    return None

# Start the client and handle the login process
async def main():
    await client.start(phone_number)  # Login using your phone number
    print("Client started, listening for messages...")

    # Find the channel ID
    # global bot_channel_id
    # bot_channel_id = await find_channel()
    
    # Create Bot
    # if bot_channel_id:
    #     global botCommunicator
    #     botCommunicator = BotCommunicator(client, bot_channel_id, "**🛠 Sniper King V2.2**")
    #     await botCommunicator.send_welcome_message()

    #     @client.on(events.NewMessage(chats=bot_channel_id))
    #     async def handler(event):
    #         message = event.message
    #         message_text = message.text.strip() if message.text else ""
    #         await botCommunicator.input(message_text)

    await client.run_until_disconnected()  # Keep the client running

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())