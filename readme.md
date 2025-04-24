## Python Telegram Crypto Bot

```
  ______     __                                ____        __ 
 /_  __/__  / /__  ____ __________ _____ ___  / __ )____  / /_
  / / / _ \/ / _ \/ __ `/ ___/ __ `/ __ `__ \/ __  / __ \/ __/
 / / /  __/ /  __/ /_/ / /  / /_/ / / / / / / /_/ / /_/ / /_  
/_/  \___/_/\___/\__, /_/   \__,_/_/ /_/ /_/_____/\____/\__/ 
                /____/   
```

| Version: v5  
| By Umar Rajput

---

## Overview

This bot monitors Telegram channels for Solana coin addresses, validates them, detects potential rug pulls, and forwards addresses to a user’s trading bot. It is containerized using Docker for easy deployment and isolation. The bot is capable of detecting and forwarding only new, unprocessed Solana addresses, with advanced features such as rug pull detection and more.

---

## Features

- **Solana Address Extraction**: Uses regex to identify Solana coin addresses.
- **Address Validation**: Validates Solana addresses using Base58 encoding and address length (43 or 44 characters).
- **Rug Pull Detection**: Identifies rug pull attempts using a list of negative keywords.
- **Message Processing**: Removes specific keywords (e.g., "KING") from messages.
- **Coin Address Handling**: Detects and combines split coin addresses into a full address.
- **Test Mode**: Use `-test` to run in test mode (requires `testConfig.json`).
- **Printer Mode**: Use `-printer` to forward monitored messages to a private channel with detailed metadata.
- **Communicator Integration**: Connects users to a private channel for text-based interactions with the bot.
- **Address Deduplication**: Only processes new addresses and avoids duplicates.
- **Address Storage**: Stores processed addresses in `addresses.txt` for later use.
- **Flexible Configuration**: Configure channels, groups, and allowed users via environment variables or `config.json`.

---

## Setup

### Prerequisites

- **Docker**: Make sure Docker is installed and running on your machine.
- **Python**: The bot relies on Python and several libraries (`Telethon`, etc.) that are pre-installed in the Docker container.

---

### Docker Setup

#### Important: Setting the Correct Environment Variables

When creating your Docker container **for the first time**, it is crucial to provide the correct environment variables, as they will be passed to the `config.json` file. These values are required for the bot to work correctly, as they configure the bot's behavior and connection to Telegram.

- If you're running the bot for the first time, **ensure you replace the placeholders** in the `docker run` commands with your actual information (e.g., `API_ID`, `API_HASH`, `PHONE_NUMBER`, etc.).
- These environment variables are passed directly into the `config.json` and will be used by the bot script to authenticate and interact with Telegram.

#### Getting Your Telegram API ID and API Hash

To obtain your **Telegram API ID** and **API hash**, you'll need to create a Telegram app:

1. Go to [https://my.telegram.org/apps](https://my.telegram.org/apps).
2. Log in with your Telegram account.
3. Click on "Create New Application".
4. Follow the instructions to create your app and obtain your **API ID** and **API hash**.

---

#### Channels and Groups Setup

When adding **channels** and **groups** to the bot's configuration, it's preferable to use the **public URL link** (e.g., `https://t.me/my_channel`). However, if you're using **private channels** or **private groups**, you will need to obtain the **channel/group ID**.

- The **channel ID** for private channels/groups looks something like `-100350535` (note the negative sign).
- You can find this ID by  using telethon to retrieve the ID from a username.

You can then use the **channel ID** instead of the public URL when setting up your environment variables.

---

#### Allowed Users Setup

For **allowed users**, you should provide either the **public username** (e.g., `@username`) or the **user ID** if the account is private.

- To obtain the **user ID**, you can use telethon to get the user's sender ID from their username.
- Add the **user ID** in the configuration if the user is private or not using a public username.

---

#### Create a New Container and Run (Printer Mode Disabled)

To create a new container and run the bot without the printer mode, use the following command. Make sure to replace the placeholder values with your actual configuration data.

```bash
docker run -it \
  --name <container_name> \
  -e NEW=true \
  -e NAME="<user_name>" \
  -e API_ID="<random_api_id>" \
  -e API_HASH="<random_api_hash>" \
  -e PHONE_NUMBER="<random_phone_number>" \
  -e TROJAN_BOT_CHAT_ID="<random_chat_id>" \
  -e CHANNEL_INVITE_LINK_1="<random_channel_1>" \
  -e CHANNEL_INVITE_LINK_2="<random_channel_2>" \
  -e ALLOWED_USER_1="<random_username>" \
  --restart=no \
  --tty \
  --interactive \
  <docker_image>
```

#### Create a New Container and Run (Printer Mode Enabled)

To enable the printer mode, use this command. This will forward monitored messages to a dedicated private channel.

```bash
docker run -it \
  --name <container_name> \
  -e NEW=true \
  -e NAME="<user_name>" \
  -e API_ID="<random_api_id>" \
  -e API_HASH="<random_api_hash>" \
  -e PHONE_NUMBER="<random_phone_number>" \
  -e TROJAN_BOT_CHAT_ID="<random_chat_id>" \
  -e CHANNEL_INVITE_LINK_1="<random_channel_1>" \
  -e CHANNEL_INVITE_LINK_2="<random_channel_2>" \
  -e ALLOWED_USER_1="<random_username>" \
  -e PRINTER=true \
  --restart=no \
  --tty \
  --interactive \
  <docker_image>
```

#### Create New Version Container for Updating

To create a new container for updating, use this command. This is mainly used for replacing old containers with newer versions.

```bash
docker create \
  --name <new_container_name> \
  --restart=no \
  --tty \
  --interactive \
  <docker_image>
```

---

### Transfer Data Between Containers

If you need to update your container without losing data (e.g., addresses, sessions, config), use the **transfer** script to copy files from an old container to the new one.

#### Transfer Script

1. After creating a new container, use the transfer script to move the configuration and session files from the old container to the new one:

```bash
# Use the transfer script (example)
transfer <old-container> <new-container>
```

2. Ensure that the `transfer.sh` script is available on your system by moving it to `/usr/local/bin` so it can be run globally:

```bash
# Move the script to /usr/local/bin for easy access
sudo mv transfer.sh /usr/local/bin/transfer
sudo chmod +x /usr/local/bin/transfer
```

Now you can execute the `transfer` command from anywhere on your system.

---

## Configuration

### Configuration File (`config.json`)

The bot configuration is stored in the `config.json` file. It includes settings like monitored channels, allowed users, and more. The configuration file can be updated directly or through environment variables passed to the Docker container.

### Environment Variables

The bot can be configured via environment variables when creating a Docker container:

- `NAME`: User's name.
- `API_ID` / `API_HASH`: Your Telegram API credentials.
- `PHONE_NUMBER`: Your phone number for authentication.
- `TROJAN_BOT_CHAT_ID`: The bot’s chat ID for interactions.
- `CHANNEL_INVITE_LINK_1` / `CHANNEL_INVITE_LINK_2`: Links to Telegram channels for monitoring.
- `ALLOWED_USER_1`: Telegram usernames allowed to forward messages from group chats.
- `PRINTER`: Set to `true` to enable printer mode for forwarding messages to a private channel.

---

## Running the Bot

To run the bot, simply start the container using the Docker commands above. The bot will begin listening for messages containing Solana addresses in the specified channels and groups.

---

## License

This project is licensed under the MIT License.

---

### Additional Considerations

- The **first-time setup** requires all the necessary environment variables (like your API credentials) to ensure that the bot functions properly.
- If you have existing data, use the **transfer script** to move important files between containers.

---

### Conclusion

With this setup, you’ll have a fully working Telegram bot for monitoring Solana addresses, detecting rug pulls, and interacting with Telegram channels. The modular nature of the bot allows for easy configuration and scalability, making it a great solution for crypto enthusiasts and developers alike.