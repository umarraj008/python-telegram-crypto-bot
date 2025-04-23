# communicator.py
from telethon.tl.custom import Button
from telethon.errors import MessageIdInvalidError

from page import Page
from option import Option
from info import Info
from gap import Gap
from updates import updates, all_updates

class Communicator:
    def __init__(self, client, channel, version, get_config_function, get_channels_function):
        """
        Initializes the Communicator class.

        Args:
            client: The Telegram client instance used to send messages.
            channel: The channel where the bot will send messages.
            version: The version of the bot.
        """
        self.get_config_function = get_config_function
        self.get_channels_function = get_channels_function
        self.client = client
        self.channel = channel
        self.current_page = "menu"
        self.invalid_input = False
        self.last_sent_message_id = None
        self.bot_name = f"🤖 Sniper King Controller {version}".ljust(100)
        self.pages = {
            "menu": Page(
                slash="menu", 
                bot_name=self.bot_name, 
                title="🏠 Menu",
                info="Welcome to your bot's control panel.",
                options=[
                    Option("Manage Channels ➡️",       lambda: self.switch_page("channels")),
                    Option("Manage Coin Addresses ➡️", lambda: self.switch_page("addresses")),
                    Option("Pause Bot ⏸️",             lambda: self.switch_page("pause")),
                    Option("View Config 📂",           lambda: self.switch_page("config")),
                    Option("View Patch Notes 📑",      lambda: self.switch_page("patch")),
                    Option("Help ❓",                   lambda: self.switch_page("help")),
                ]
            ),
            "channels": Page(
                slash="channels",
                bot_name=self.bot_name,
                title="📡 Manage Channels",
                info="Here you can manage the channels that are being monitored.",
                options=[
                    Info("**Channels and Groups:**"),
                    Info(self.get_channels_function()),
                    Gap(),
                    Option("Add Channel ➕", lambda: self.prompt_for_channel_name()),
                    Option("Remove Channel ➖", lambda: print("Removing channel...")),
                    Option("Clear All Channels 🧹", lambda: print("Clearing channels...")),
                    Gap(),
                    Option("Go Back 🔙", lambda: self.switch_page("menu")),
                ],
            ),
            "addresses": Page(
                slash="addresses",
                bot_name=self.bot_name,
                title="💰 Manage Coin Addresses",
                info="Here you can manage the saved coin addresses.",
                options=[
                    Option("Show Addresses 📋",      lambda: print("")),
                    Option("Add Address ➕",         lambda: self.prompt_for_channel_name()),
                    Option("Remove Address ➖",      lambda: print("")),
                    Option("Clear All Addresses 🧹", lambda: print("")),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
            "pause": Page(
                slash="pause", 
                bot_name=self.bot_name,
                title="⏸️ Pause Bot",
                info="Would you like to pause the bot?",
                options=[
                    Option("🔴 **Pause Bot** (Stops forwarding addresses)",    lambda: print("Displaying monitored channels...")),
                    Option("🟢 **Resume Bot** (Resumes forwarding addresses)", lambda: self.prompt_for_channel_name()),
                    Gap(),
                    Info("Current Status: 🟢 Running"),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
            "config": Page(
                slash="config",
                bot_name=self.bot_name,
                title="📂 View Config",
                info="Here is the current configuration (config.json):",
                options=[
                    Info(self.get_config_function()),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
            "help": Page(
                slash="help", 
                bot_name=self.bot_name, 
                title="❓ Help",
                info="To interact with the bot's control panel, please follow these steps:",
                options=[
                    Info(
"""
1. Look at the menu and find the option you want to select.
2. Type the number corresponding to the option in the chat.
3. If you need to go back, select the "Go Back" option.

Here are some commands:
- **/menu**: 
- **/channels**: Manage channels and group chats
- **/addresses**: Manage coin addresses
- **/pause**: Pause/Unpause the bot
- **/config**: View your config
- **/patch**: View patch notes
- **/help**: View help information

If you type something random, the bot will guide you back to the main menu.
"""),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
            "patch": Page(
                slash="patch",
                bot_name=self.bot_name,
                title="📑 Patch Notes",
                info=f"Here are the latest updates to {self.bot_name}:",
                options=[
                    Info(all_updates()),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
        }

    async def handler(self, event):
        message = event.message
        message_text = message.text.strip() if message.text else ""

        # Check if the message contains the bot's identifier text (e.g., "🤖 Sniper King Controller")
        if "🤖 Sniper King Controller" in message_text:
            # Ignore the message if it contains the bot's identifier
            return

        await self.input(message_text)

        # Delete the user's input message after processing
        try:
            # Ensure the message exists before trying to delete
            await self.client.delete_messages(event.chat_id, message.id)
        except MessageIdInvalidError:
            pass

    def switch_page(self, to):
        """
        Switches the current page of the bot's UI.

        Args:
            to: The name of the page to switch to.
        """
        self.current_page = to

    def prompt_for_channel_name(self):
        """
        Prompts the user for a channel name and sets up the action to add the channel.

        This function is used when the bot expects the user to input a channel name.
        """
        # When this is called, set `expects_text` to True to indicate the page now expects text input
        print("Please type the name of the new channel:")
        self.pages["channels"].expects_text = True  # Indicate that the page expects text input
        self.pages["channels"].pending_text_action = self.add_channel

    def add_channel(self, channel_name):
        """
        Handles adding a new channel once the user provides a channel name.

        Args:
            channel_name: The name of the channel to be added.
        """
        # This is the action to take once the user inputs a channel name
        print(f"Channel '{channel_name}' has been added!")  # Replace with actual logic for adding a channel

    def display(self):
        """
        Returns the current page's display content.

        Returns:
            str: The formatted string representation of the current page.
        """
        invalid = ""
        if self.invalid_input:
            self.invalid_input = False
            invalid = "❌ **Invalid Input** __Please use a valid page name!__" 
        return (
f"""
{self.pages[self.current_page].display()}{invalid}
""")

    async def input(self, text):
        """
        Handles the user's input, either commands or selection choices.

        If the input is a command (starts with '/'), the corresponding page is displayed.
        If the input is a choice (numeric), the appropriate action is triggered.

        Args:
            text: The user's input text (either a command or a choice).
        """
        # Handle / commands: check if the text starts with / and match to a page's slash field
        if text.startswith("/"):

            # Home command
            if text == "/home": 
                self.switch_page("menu")
                await self.send_message(self.display())
                return
            
            # Extract the command after the slash (e.g., /channels -> "channels")
            page_name = text[1:]
            if page_name in self.pages:
                self.switch_page(page_name)
            else:
                self.invalid_input = True

            await self.send_message(self.display())

        else:        
            # Handle input for the current page (either option selection or text input)
            self.pages[self.current_page].handle_input(text)
            await self.send_message(self.display())

    async def send_welcome_message(self):
        """
        Sends a welcome message to the user when they start interacting with the bot.
        """

        button = Button.inline("Go to Menu", b"goto_menu")

        await self.send_message(
f"""
**{self.bot_name}**

Hello 👋
Ready to help manage your bot! 🚀

Just type **/menu** to get going or **/help** if you need assistance! 😊

**Latest Update:**
{updates[0]}

To view rest use **/patch**
""")
    
    async def send_message(self, message):
        """
        Sends a message to the specified channel.

        Args:
            message: The message to be sent to the channel.
        """
        if self.last_sent_message_id:
            try:
                # Edit the last message if it exists
                await self.client.edit_message(self.channel, self.last_sent_message_id, message, link_preview=False)
            except Exception as e:
                pass
        else:
            # Send a new message if there is no previous message to edit
            sent_message = await self.client.send_message(self.channel, message, background=False, link_preview=False)
            self.last_sent_message_id = sent_message.id  # Store the ID of the new sent message