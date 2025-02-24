from telethon import TelegramClient, events
from datetime import datetime
from tests import test_data
import asyncio
import re
import json
import sys
import argparse

# Get args
parser = argparse.ArgumentParser(description="Check for CLI arguments")
parser.add_argument('arg1', nargs='?', help="First argument")
args = parser.parse_args()

if args.arg1 == "test":
    test = True

# Load configuration from the config.json file
def load_config():
    configFile = "config.json"
    if test: configFile = "testConfig.json"

    with open(configFile, 'r') as f:
        return json.load(f)

# Load the configuration data
config = load_config()

# Your Telegram API details from the config file
api_id = config['api_id']
api_hash = config['api_hash']
phone_number = config['phone_number']

# Trojan bot's chat ID or username
TROJAN_BOT_CHAT_ID = config['trojan_bot_chat_id']

# List of private channel invite links
channel_invite_links = config['channel_invite_links']

# Set up the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Function to save address to a file
def save_address(address):
    with open('addresses.txt', 'a') as f:
        f.write(address + '\n')

# Function to check if the address already exists in the file
def address_exists(address):
    if test: return False
    try:
        with open('addresses.txt', 'r') as f:
            addresses = f.readlines()
        return any(line.strip() == address for line in addresses)
    except FileNotFoundError:
        return False

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
async def forward_message(message):
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
            # if not test:
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

                if not test:
                    await client.send_message(TROJAN_BOT_CHAT_ID, f"{cleaned_address}")
                    save_address(cleaned_address)
                return cleaned_address
            else:
                log(f"Address {cleaned_address} has already been forwarded or is invalid. Skipping.")

    return None  # If nothing was found

# Keep track of processed message IDs
processed_message_ids = set()
lastMessage = ""

# Set up event handler to listen for new messages from the channels
@client.on(events.NewMessage(chats=channel_invite_links))  # Listen for new messages from multiple channels
async def handler(event):
    global lastMessage  

    message = event.message
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Normalize message text (remove extra spaces, newlines, etc.)
    message_text = message.text.strip() if message.text else ""

    # Check if message ID or content has already been processed
    if message.id in processed_message_ids or lastMessage == message_text:
        print(f"[{current_time}] Message {message.id} already processed, skipping.")
        return  # Skip duplicate messages

    # Update last message content **before processing**
    lastMessage = message_text
    processed_message_ids.add(message.id)

    print(f"[{current_time}] Received Message: {message.id}")
    
    await forward_message(message)  # Forward the message immediately


# Start the client and handle the login process
async def main():
    await client.start(phone_number)  # Login using your phone number
    print("Client started, listening for messages...")
    await client.run_until_disconnected()  # Keep the client running

async def run_tests(test_data):
    print("---TEST MODE---")
    print("----------------------------------------------------------------------------------")


    # Define Message class
    class Message:
        def __init__(self, text):
            self.text = text

    passes = 0

    # Loop and do tests
    for test in test_data:
        message = Message(test[1])
        result = await forward_message(message)

        if (result == test[2]):
            print(f"\033[32mTest:     {test[0]} was successful\033[0m")
            print(f"\033[32mExpected: {test[2]}\033[0m")
            print(f"\033[32mReceived: {result}\033[0m")
            passes += 1
        else:
            print(f"\033[31mTest:     {test[0]} Failed\033[0m")
            print(f"\033[31mExpected: {test[2]}\033[0m")
            print(f"\033[31mReceived: {result}\033[0m")
               
        print("----------------------------------------------------------------------------------")

    print("")

    if passes == len(test_data):
        print(f"\033[32mAll Tests Passed!\033[0m")
        print(f"\033[32m{passes} / {len(test_data)} passed.\033[0m")
    else:
        print(f"\033[31mTests Failed!\033[0m")
        print(f"\033[31m{passes} / {len(test_data)} passed.\033[0m")

    print("")
    sys.exit("---END---")

if __name__ == '__main__':
    if test:
        asyncio.run(run_tests(test_data))
    else:
        test = False
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())