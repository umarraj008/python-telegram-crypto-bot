# bot.py

from telethon import TelegramClient, events
from log_channel import send_to_log_channel
from utils import *
from communicator import Communicator
import re

class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.client = TelegramClient('session_name', config['api_id'], config['api_hash'])
        self.allowed_users = config['allowed_users']
        self.trojan_bot_chat_id = config['trojan_bot_chat_id']
        self.version = "v5"
        self.negative_keywords = ["rug", "do not buy", "rug pull", "insta rug", "fishing", "bat call", "robot call", "sniper call", "scraper call", "bot call", "dont buy", "don't buy", "no buy", "scrapers", "for the boys", "for the community", "rug call", "instant rug", "dump"]
        self.processed_message_ids = set()
        self.lastMessage = ""
        self.channel_invite_links = config['channel_invite_links']
        self.printer = config['printer']
        self.test = config['test']
        self.phone_number = config['phone_number']
        self.log_channel = "https://t.me/+hcUaCptjn3RkZTU0"
        self.control_channel_name = f"Sniper King Controller#{self.config['name']}"
        self.communicator = None

    async def forward_message(self, message):
        """
        Processes a message to extract a Solana address and forward it to a designated chat.
        """
        # Initialize values
        rug_pull = False
        address = ""
        message_text = message.text

        # Remove URLs
        text = re.sub(r'http[s]?://\S+|www\.\S+', '', message_text)

        # Check for rug-related words in text
        if any(word in text.lower() for word in self.negative_keywords):
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
        await self.client.send_message(self.trojan_bot_chat_id, address)
        return address

    def get_config(self):
        return (
f"""```api_id: {self.config['api_id']}
api_hash: {self.config['api_hash']}
phone_number: {self.config['phone_number']}
trojan_bot_chat_id: {self.config['trojan_bot_chat_id']}
printer: {self.config['printer']}
channel_invite_links: {self.config['channel_invite_links']}
allowed_users: {self.config['allowed_users']}
```""")
    
    def get_channels(self):
        invite_links = self.config['channel_invite_links']
        formatted = "\n".join([f"{i+1}. {link}" for i, link in enumerate(invite_links)])
        return f"""
{formatted}
"""

    async def init_bot_communicator(self):
        """
        Initializes the text-interface Communicator.
        """
        try:
            # Check if the control channel exists
            control_channel_id = await find_channel_id(self.client, self.control_channel_name)

            if control_channel_id is None:
                # If the control channels ID is not found, stop the bot and notify
                print(f"WARN: Channel '{self.control_channel_name}' ID not found, stopping bot.")
                return
            
            # If channel ID is found, proceed with initializing the Communicator
            self.communicator = Communicator(self.client, 
                                             control_channel_id, 
                                             self.version, 
                                             self.get_config,
                                             self.get_channels)
            await self.communicator.send_welcome_message()
            print(f"Communicator initialized at '{self.control_channel_name}'")

        except Exception as e:
            print(f"WARN: Failed to initialize Communicator: {e}")

    async def handler(self, event):
        """
        Event handler that listens for new messages from specified channels and processes them.
        """
        message = event.message
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Normalize message text (remove extra spaces, newlines, etc.)
        message_text = message.text.strip() if message.text else ""

        # Check if message ID or content has already been processed
        if message.id in self.processed_message_ids or self.lastMessage == message_text:
            #print(f"[{current_time}] Message {message.id} already processed, skipping.")
            return

        # Get sender
        sender_username = "Unknown"
        sender = await message.get_sender()

        # If from group, check if it's from the correct username
        if event.is_group or (event.is_channel and not event.chat.broadcast):  # i.e., it's a megagroup
            if sender is None:
                #print(f"[{current_time}] Message {message.id} has no sender, skipping.")
                return

            sender_username = sender.username.lower() if sender.username else "Unknown"
            
            if sender_username not in [username.lower() for username in self.allowed_users]:
                #print(f"[{current_time}] Message {message.id} not from target username, skipping.")
                return
        else:
            if sender is not None:
                sender_username = sender.username.lower() if sender.username else "Unknown"

        # Update last message content **before processing**
        self.lastMessage = message_text
        self.processed_message_ids.add(message.id)

        print(f"[{current_time}] Received Message: {message.id} | {sender_username}")
        await self.forward_message(message)  # Forward the message immediately

        if self.printer:
            await send_to_log_channel(self.client, event, sender_username, self.version, self.log_channel)

    async def run(self):
        if self.test:
            print(f"WARN: Running in test mode")
        if self.printer:
            print(f"WARN: Running in printer mode")

        await self.client.start(self.phone_number)
        await self.init_bot_communicator()

        print(f"""
  ______     __                                ____        __ 
 /_  __/__  / /__  ____ __________ _____ ___  / __ )____  / /_
  / / / _ \/ / _ \/ __ `/ ___/ __ `/ __ `__ \/ __  / __ \/ __/
 / / /  __/ /  __/ /_/ / /  / /_/ / / / / / / /_/ / /_/ / /_  
/_/  \___/_/\___/\__, /_/   \__,_/_/ /_/ /_/_____/\____/\__/ 
                /____/

| Version: {self.version}
| By Umar Rajput""")
        print("")

        self.client.add_event_handler(self.handler, events.NewMessage(chats=self.channel_invite_links))
        print("TelegramBot has started...")

        if self.communicator is not None:
            self.client.add_event_handler(self.communicator.handler, events.NewMessage(chats=self.communicator.channel))
            print("TelegramBot Communicator has started...")
        
        await self.client.run_until_disconnected()