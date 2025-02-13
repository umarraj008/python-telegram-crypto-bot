from telethon import TelegramClient, events
import re

# Your Telegram API details
api_id = ''       # Replace with your API ID from https://my.telegram.org
api_hash = ''   # Replace with your API hash from https://my.telegram.org
phone_number = ''  # Your phone number registered with Telegram

# Replace with your Trojan bot's chat ID or username
TROJAN_BOT_CHAT_ID = '@solana_trojanbot'  # This is the bot's username

# List of private channel invite links
channel_invite_links = [
    'https://t.me/cryptoyeezuscalls'
]

# Set up the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

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
            # If the address is valid and not part of a filtered URL, forward it
            print(f"Found and forwarding address: {address}")
            # Uncomment the next line to forward the address to the bot
            await client.send_message(TROJAN_BOT_CHAT_ID, f"{address}")


# Set up event handler to listen for new messages from the channels
@client.on(events.NewMessage(chats=channel_invite_links))  # Listen to messages from multiple channels
async def handler(event):
    message = event.message
    print(f"Received message: {message.text}")
    await forward_message(message)

# Start the client and handle the login process
async def main():
    await client.start(phone_number)  # Login using your phone number
    print("Client started, listening for messages...")
    await client.run_until_disconnected()  # Keep the client running

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

#ALREADY USED
#https://dexscreener.com/solana/gegkwsv48e3luplcpbvwnznbake4p8rgaaz6tjwhmoon