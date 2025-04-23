# log_channel.py

from telethon.errors import MessageIdInvalidError, FloodWaitError
from datetime import datetime

async def send_to_log_channel(client, event, username, version, log_channel):
    """
    Forwards a message to a log channel and sends detailed information about the message.

    Args:
        client (TelegramClient): The Telethon client instance to send messages.
        event (Event): The event object representing the new message event.
        username (str): The username of the sender who initiated the message.
        version (str): The version of the bot or script running.
        log_channel (str): The channel ID or username where the log will be sent.

    Returns:
        None
    """
    message = event.message
    current_time = datetime.now().strftime('%Y-%m-%d • %H:%M:%S')

    # Get message details with checks for missing attributes
    raw_chat_title = event.chat.title if event.chat and hasattr(event.chat, 'title') else 'Unknown'
    sender_id = event.sender_id if event.sender_id else 'Null'
    message_id = message.id if hasattr(message, 'id') else 'Null'
    chat_id = event.chat_id if event.chat_id else 'Null'
    is_group = 'G' if getattr(event, 'is_group', False) else 'C'
    has_media = 'Y' if event.media else 'N'

    chat_title_map = {
        "Yeezus Prophets Chat": "Yeezus Chat",
        "Yeezus’ Prophets": "Yeezus Channel"
    }

    chat_title = chat_title_map.get(raw_chat_title, raw_chat_title)

    # Prepare message details to print
    message_details = f"""
**🕒 {current_time}** | __{version}__
**💬 {chat_title}:** {username}
`{is_group}{has_media}{chat_id}.{message_id}.{sender_id}`
"""
    #VERSION:TYPE:MEDIA:CID:MID:SID
    # Forward message
    try:
        if message_id != 'Null':  # Check if message ID is valid
            await client.forward_messages(log_channel, message, background=True)
        else:
            print(f"Message ID {message_id} is invalid, cannot forward.")
            await client.send_message(log_channel, message.text or '[No text content]', background=True)
    except MessageIdInvalidError:
        print(f"Message ID {message_id} is invalid or deleted, sending text instead.")
        await client.send_message(log_channel, message.text or '[No text content]', background=True)
    except FloodWaitError as e:
        wait_time = e.seconds
        print(f"Message sent as text due to flood wait. Wait time: {wait_time} seconds.")
        await client.send_message(log_channel, message.text or '[No text content]', background=True)

    # Send details of that message
    await client.send_message(log_channel, message_details, background=True)