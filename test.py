import psutil
import time
from telethon import TelegramClient, events
from datetime import datetime
import re
import json

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
async def forward_message(message):
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
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if the address has already been forwarded
            if not address_exists(address):
                # If the address is valid and not already saved, forward it
                print(f"[{current_time}] Found and forwarding address: {address}")
                await client.send_message(TROJAN_BOT_CHAT_ID, f"{address}")
                save_address(address)  # Save the address after forwarding
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
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if the message has already been processed (based on message ID)
    if message.id in processed_message_ids:
        print(f"[{current_time}] Message {message.id} already processed, skipping.")
        return  # Skip this message

    # Mark the message as processed
    processed_message_ids.add(message.id)

    print(f"[{current_time}] Received Message")
    await forward_message(message)

# Function to monitor CPU and memory usage
def monitor_system():
    while True:
        # Get the current process
        process = psutil.Process()
        
        # Get the current CPU and memory usage
        cpu_usage = process.cpu_percent(interval=1)  # CPU usage in percent
        memory_info = process.memory_info()
        memory_usage = memory_info.rss / (1024 * 1024)  # Memory usage in MB
        
        # Print or log the usage stats
        print(f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage:.2f} MB")
        
        # Log it to a file for future analysis
        with open("system_usage.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - CPU: {cpu_usage}% | Memory: {memory_usage:.2f} MB\n")
        
        time.sleep(5)  # Log stats every 5 seconds

# Start the system monitoring in a separate thread
import threading
monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
monitoring_thread.start()

# Your existing Telegram bot code...

# Start the client and handle the login process
async def main():
    await client.start(phone_number)  # Login using your phone number
    print("Client started, listening for messages...")
    await client.run_until_disconnected()  # Keep the client running

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())