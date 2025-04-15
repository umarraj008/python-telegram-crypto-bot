import os

class Gap:
    def display(self):
        return "\n"

class Info:
    def __init__(self, text):
        self.text = text

    def display(self):
        return self.text

class Option:
    def __init__(self, text, action):
        self.text = text
        self.action = action
        self.number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    def display(self, index):
        return f"{self.number_emojis[index]} {self.text}"

    def execute(self):
        self.action()

class Page:
    def __init__(self, slash="", bot_name="Sniper King", title="", info="", options=[], expects_text=False):
        self.title = title
        self.info = info
        self.slash = slash
        self.bot_name = bot_name
        self.options = options
        self.expects_text = expects_text  # If True, this page expects text input (like channel name)
        self.pending_text_action = None  # Action to take when text is input (e.g., adding a channel)
        self.invalid_input = False
        self.visible_options = []

    def display(self):
        options = ""
        invalid = ""

        # Only display options, not gaps, for numeric input
        index = 1
        for option in self.options:
            if not isinstance(option, Option):
                options += option.display()
            else:
                self.visible_options.append(option)
                options += option.display(index) + "\n"  # Display the actual option
                index += 1

        if self.invalid_input:
            self.invalid_input = False
            invalid = "\n❌ **Invalid Input** ❌ Please enter a valid option."
        return (
f"""
{self.bot_name}

{self.title} /{self.slash} 

{self.info}
(Please type the number corresponding to your choice)

{options}{invalid}
""")

    def handle_input(self, user_input):
        if self.expects_text:
            # If the page expects text input, handle it (e.g., adding a channel)
            if self.pending_text_action:
                self.pending_text_action(user_input)
            self.expects_text = False  # Reset after handling the input
        else:
            try:
                # Handle numeric option input (map to visible options)
                choice = int(user_input)
                if 1 <= choice <= len(self.visible_options):
                    # Execute the selected option's action
                    self.visible_options[choice - 1].execute()
                else:
                    self.invalid_input = True
            except ValueError:
                self.invalid_input = True

class BotCommunicator:
    def __init__(self, client, channel, bot_name):
        self.client = client
        self.channel = channel
        self.current_page = "menu"
        self.invalid_input = False
        self.bot_name = bot_name
        self.changelog = (
"""**[v2.2]**
- Added support for **private groups** and **channels**
- Now using **dynamic list** to only allow messages from **select users**

**[v2.1]**
- Support for **Solana coin addresses (CA)** with **43-character length**
- Integrated group chat monitoring for **cryptoyeezus**

**[v2.0]**
- **Rug pull detection** improvements
- Detection of **SPLIT CA**
- Detection of the **KING** keyword
- **Solana coin validation** using **Base58 decoding**
- **Length validation** for **Solana addresses** (**44 characters**)
- **Debug output** with **timestamp printing**
- **Rug pull CA** are now saved properly

**[v1.2]**
- Initial **rug pull detection**
- **Word detection** and **removal functionality**

**[v1.0]**
- Monitoring of **Telegram channels**
- Detection of **coin addresses (CA)**
- Forwarding detected **CA** to **trojan bot**
""")
        self.pages = {
            "menu": Page(
                slash="menu", 
                bot_name=self.bot_name, 
                title="🏠 Menu 🏠",
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
                title="📡 **Manage Channels** 📡",
                info="Here you can manage the channels that are being monitored.",
                options=[
                    Option("Show Monitored Channels 📋", lambda: print("Displaying monitored channels...")),
                    Option("Add Channel ➕", lambda: self.prompt_for_channel_name()),
                    Option("Remove Channel ➖", lambda: print("Removing channel...")),
                    Option("Clear All Channels 🧹", lambda: print("Clearing channels...")),
                    Gap(),  # Just to leave a space
                    Option("Go Back 🔙", lambda: self.switch_page("menu")),
                ],
            ),
            "addresses": Page(
                slash="addresses",
                bot_name=self.bot_name,
                title="💰 **Manage Coin Addresses** 💰",
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
                title="⏸️ **Pause Bot** ⏸️",
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
                title="📂 **View Config** 📂",
                info="Here is the current configuration (config.json):",
                options=[
                    Info(
"""
```
{ "api_id": "20027855", "api_hash": "ab5081fcbdc01d94c1d182d7ac44a020", "phone_number": "+44 7399 276578", "trojan_bot_chat_id": "@solana_trojanbot", "channel_invite_links": [ "https://t.me/+J2FjYDsfcyU2NzZk", "https://t.me/+uefASAelAsc2MWVk", "https://t.me/cryptoyeezuschat", -1002560071675 ], "allowed_users": [ "CRYPTOYEEZUSSSS", "fiorenzonsol" ] }
```
"""),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
            "help": Page(
                slash="help", 
                bot_name=self.bot_name, 
                title="❓ **Help** ❓",
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
                title="📑 **View Patch Notes** 📑",
                info="Here are the latest updates to Sniper King Bot v2.1:",
                options=[
                    Info(self.changelog),
                    Gap(),
                    Option("Go Back 🔙",             lambda: self.switch_page("menu"))
                ],
            ),
        }

    def switch_page(self, to):
        self.current_page = to

    def prompt_for_channel_name(self):
        # When this is called, set `expects_text` to True to indicate the page now expects text input
        print("Please type the name of the new channel:")
        self.pages["channels"].expects_text = True  # Indicate that the page expects text input
        self.pages["channels"].pending_text_action = self.add_channel

    def add_channel(self, channel_name):
        # This is the action to take once the user inputs a channel name
        print(f"Channel '{channel_name}' has been added!")  # Replace with actual logic for adding a channel

    def display(self):
        invalid = ""
        if self.invalid_input:
            self.invalid_input = False
            invalid = "❌ **Invalid Input** ❌ Please use a valid page name." 
        return (
f"""
{self.pages[self.current_page].display()}{invalid}
""")

    async def input(self, text):
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
        await self.send_message(
f"""
{self.bot_name}

Hello 👋
Ready to help manage your bot! 🚀

Just type /menu to get going or /help if you need assistance! 😊
""")
    
    async def send_message(self, message):
        await self.client.send_message(self.channel, message)

def main():
    bot_communicator = BotCommunicator()

    while True:
        os.system("cls")  # Clear screen for each new loop
        bot_communicator.display()
        user_input = input().strip()  # Get user input
        bot_communicator.input(user_input)

if __name__ == "__main__":
    main()