from telethon import TelegramClient, events
from datetime import datetime
import asyncio
import json

def load_config():
    configFile = "config.json"
    with open(configFile, 'r') as f:
        return json.load(f)

config = load_config()
api_id = config['api_id']
api_hash = config['api_hash']
phone_number = config['phone_number']
allowed_users = config['allowed_users']
TROJAN_BOT_CHAT_ID = config['trojan_bot_chat_id']
channel_invite_links = config['channel_invite_links']
processed_message_ids = set()
lastMessage = ""
client = TelegramClient('session_name', api_id, api_hash)

#Set up event handler to listen for new messages from the channels
@client.on(events.NewMessage(chats=channel_invite_links))  # Listen for new messages from multiple channels
async def handler(event):
    global lastMessage  
    message = event.message
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    message_text = message.text.strip() if message.text else ""
    if message.id in processed_message_ids or lastMessage == message_text:
        return
    
    sender_username = "Unknown"
    sender = await message.get_sender()

    if event.is_group or (event.is_channel and not event.chat.broadcast):  # i.e., it's a megagroup
        if sender is None:
            return

        sender_username = sender.username.lower() if sender.username else "Unknown"
        
        if sender_username not in [username.lower() for username in allowed_users]:
            return
    else:
        if sender is not None:
            sender_username = sender.username.lower() if sender.username else "Unknown"

    lastMessage = message_text
    processed_message_ids.add(message.id)
    print(f"[{current_time}] Received Message: {message.id} | {sender_username}")
    await print_and_save_message(event, sender_username)

# Function to print and save message details
async def print_and_save_message(event, username):
    message = event.message
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Prepare message details to print
    message_details = [
        f"[{current_time}]----------------------------------------------",
        "Message Text:",
        f"{message.text.strip()}\n",
        f"Received At: {current_time} | Message ID: {message.id} | Sender ID: {event.sender_id} | Sender Username: [{event.sender.username if event.sender else 'Unknown'} : {username}] | Chat Name: {event.chat.title if event.chat else 'N/A'} | Message Date: {message.date} | Is Group: {event.is_group} | Is Channel: {event.is_channel} | Has Media: {'Yes' if event.media else 'No'}",
        f"[----------------------------------------------------------------------\n"
    ]

    # Print the details to the console
    for line in message_details:
        print(line)

    # Save the message details to a file
    file_name = "addresses.txt"
    with open(file_name, "a", encoding="utf-8") as file:
        for line in message_details:
            file.write(line + "\n")

    print(f"Message details saved to {file_name}")

# Start the client and handle the login process
async def main():
    await client.start(phone_number)  # Login using your phone number
    print("Client started, listening for messages...")
    await client.run_until_disconnected()  # Keep the client running

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())