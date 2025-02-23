from telethon import TelegramClient, events
from datetime import datetime
import re
import json

tests = [
    (
        "Regular Post",
        """
        🚨PAID PROMO ACROSS ALL PLATFORMS🚨

        LOW CAP HIGH RISK HIGH REWARD MOONSHOT SHITTER GAMBLE AROUND 33K MC AREA. DYOR NFA. 

        GOOD BRANDING AND NARRATIVE IN CURRENT MARKET SENTIMENT WITH VIRAL POTENTIAL. TEAM SEEMS TO BE GRINDING HARD AS WELL.

        https://x.com/growaparonsol

        https://dexscreener.com/solana/Hwercue3DeYXUhbybMrUeX8KNMh42zZQdhbMNN3wMwyc

        https://t.me/GrowAPair100x

        7w1YgW5kkwBz43E32jWdnskK8wdvgvsSAoWZ7v9Nmoon
        """,
        "Hwercue3DeYXUhbybMrUeX8KNMh42zZQdhbMNN3wMwyc"
    ),
    (
        """
        🚨HIGH RISK HIGH REWARD GAMBLE PLAY🚨

        GOING OUT ACROSS ALL PLATFORMS

        GOOD NARRATIVE FART META. THE ONLY OTHER FART BOOK MY ADAM WALLACE LIKE THE FARTBOY COIN  THAT RAN OVER 200M THE REST ARE JUST DERIVATIVES EXCEPT THIS ONE SO I THINK ITS SUPER UNDERVALUED. 300K MC AREA DYOR NFA.

        https://dexscreenerDEEZ.com/solana/4iWpF4TMzHnDP7tjfYWqW8x1qWHb1AbqNhhJqVdTYxL4

        https://fartclubsol.com/

        https://x.com/fartclub_cto

        https://t.me/cto_fartclub

        6zkZPeSVSynKoNgPjb6DEEZyCfJ5BFFro4gcKXuMrPtvpump

        YOU HAVE TO REMOVE THE WORD “DEEZ” FROM THE CA AND DEX LINK SO BOTS GET SIDELINED
        """,
        "4iWpF4TMzHnDP7tjfYWqW8x1qWHb1AbqNhhJqVdTYxL4"
    ),
]

deezMessageWithBrokenURL= ()
kingMessage = ()
kingMessageWithBrokenURL= ()
rugPullMessage = ()
brokenURLmessage = ()
longRemoveWord = ()
removeSentance = ()
lowercaseRemoveWord = ()
randomCaseRemoveWord = ()
# Load configuration from the config.json file
def load_config():
    with open('config.json', 'r') as f:
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
    # List of filter words (keywords to avoid in URLs, etc.)
    filter_words = ['http', 'https', 'dexscreener', '.com']
    
    # Regular expression to detect Solana addresses (44 alphanumeric characters)
    address_pattern = r'\b[A-Za-z0-9]{44}\b'  # Matches exactly 44 alphanumeric characters
    
    # Split the message text into lines
    lines = message.text.splitlines()

    # First, check for "DO NOT BUY" or "INSTA RUG" phrases
    if "do not buy" in message.text.lower() or "insta rug" in message.text.lower():
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] This coin is flagged as a rug pull. Stopping processing.")
        return  # Stop processing if any of these phrases are found

    # Initialize the word to be removed as None
    word_to_remove = None

    # Look for the phrase "REMOVE THE WORD" and extract the word
    match = re.search(r'remove the word ["\']([A-Za-z0-9]+)["\']', message.text, re.IGNORECASE)
    if match:
        word_to_remove = match.group(1).lower()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] Found instruction to remove word: {word_to_remove}")

    # If a word to remove is found, clean the message by removing the word
    if word_to_remove:
        message.text = message.text.replace(word_to_remove, "")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] Removed all occurrences of the word '{word_to_remove}' from the message.")

    # Look for the Dexscreener URL and extract the address
    dex_url_pattern = r'https://dexscreener(?:[A-Za-z0-9]+)?\.com/solana/([A-Za-z0-9]+(?:[A-Za-z0-9]*))'
    dex_match = re.search(dex_url_pattern, message.text)

    if dex_match:
        dex_address = dex_match.group(1)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] Found Dexscreener address (before cleaning): {dex_address}")
        
        # If there's a word to remove, clean the address part of the URL
        if word_to_remove:
            dex_address = dex_address.replace(word_to_remove, "")
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{current_time}] Removed the word '{word_to_remove}' from the Dexscreener address: {dex_address}")
        
        # Validate the cleaned address length
        if len(dex_address) == 44:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{current_time}] Sending the cleaned Dexscreener address to client: {dex_address}")
            # await client.send_message(TROJAN_BOT_CHAT_ID, f"{dex_address}")  # Uncomment to send
            return
        else:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{current_time}] Cleaned address is invalid (not 44 characters): {dex_address}")
    
    # Process each line in the message for Solana coin address
    for line in lines:
        # Check if the line contains any of the filter keywords (URLs)
        if any(keyword in line.lower() for keyword in filter_words):
            continue  # Skip this line if it contains unwanted keywords
        
        # Search for all 44-character addresses in the line
        addresses = re.findall(address_pattern, line)
        
        # Process each address found
        for address in addresses:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # Check if the address has already been forwarded
            if not address_exists(address):
                # If the address is valid and not already saved, forward it
                print(f"[{current_time}] Found and forwarding address: {address}")
                # await client.send_message(TROJAN_BOT_CHAT_ID, f"{address}")  # Uncomment to actually send
                # save_address(address)  # Save the address after forwarding
                return
            else:
                print(f"[{current_time}] Address {address} has already been forwarded. Skipping.")


# Keep track of processed message IDs
processed_message_ids = set()

# Set up event handler to listen for new messages from the channels
@client.on(events.NewMessage(chats=channel_invite_links))  # Listen to messages from multiple channels
async def handler(event):
    message = event.message

    # Get the current time in a readable format
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Check if the message has already been processed (based on message ID)
    if message.id in processed_message_ids:
        print(f"[{current_time}] Message {message.id} already processed, skipping.")
        return  # Skip this message

    # Mark the message as processed
    processed_message_ids.add(message.id)

    print(f"[{current_time}] Received Message: {message.id}")
    await forward_message(message)

# Start the client and handle the login process
async def main():
    await client.start(phone_number)  # Login using your phone number
    print("Client started, listening for messages...")
    await client.run_until_disconnected()  # Keep the client running

    

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())