import argparse
import psycopg2
import redis
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient, events

def get_db_connection():
    """Connect to Postgres Database"""
    return psycopg2.connect(
        dbname="your_db_name",
        user="your_db_user",
        password="your_db_password",
        host="localhost",
        port="5432"
    )

def get_user_details(user_id):
    """ Fetch user details from the PostgreSQL database based on user_id """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT id, name, api_id, api_hash, phone_number, bot_chat, test_chat_link, created_at FROM users WHERE id = %s'
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_user_channels(user_id):
    """ Fetch user's channels from the PostgreSQL database based on user_id """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT c.id, c.name, c.link
        FROM user_channels uc
        JOIN channels c ON uc.channel_id = c.id
        WHERE uc.user_id = %s
    '''
    cursor.execute(query, (user_id,))
    channels = cursor.fetchall()
    cursor.close()
    conn.close()
    return channels

def is_message_processed(message_id):
    """ Check if message is already processed (in DB or Redis) """
    # Check in Redis Queue
    if redis_client.exists(f"message:{message_id}"):
        return True
    
    # Check in DB (if message_id exists)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT 1 FROM messages WHERE message_id = %s'
    cursor.execute(query, (message_id,))
    processed = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return processed

async def forward_message(address, from_channel, time_received):
    """Forward the received message to the bot's chat."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    message = f"""
    Sent: {time_received}
    Received: {current_time}

    {address}
    """
    await client.send_message(user["BOT_CHAT"], message)

async def handle_redis_notifications():
    """Listen for messages from the Redis queue and handle them accordingly"""
    pubsub = redis_client.pubsub()  # Create a pubsub object to subscribe to Redis channels
    pubsub.subscribe('messages_channel')  # Subscribe to the 'messages_channel' Redis channel

    print("Subscribed to 'messages_channel'... Waiting for notifications")

    # Listen for messages from Redis
    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                # Deserialize the message (which is a JSON string) back to a Python object
                message_data = json.loads(message['data'])
                
                # Extract the data from the message
                address = message_data.get("address", "")
                from_channel = message_data.get("from_channel", "")
                time_received = message_data.get("time_received", "")

                print(f"New Address Received From Channel {from_channel}: {address}")
                forward_message(address, from_channel, time_received)

            except json.JSONDecodeError as e:
                print(f"Error decoding message data: {e}")

@client.on(events.NewMessage(chats=[channel["LINK"] for channel in user["CHANNELS"]]))
async def handler(event):
    """Event handler to listen for new messages from the channels"""
    message = event.message
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Normalize message text (remove extra spaces, newlines, etc.)
    message_text = message.text.strip() if message.text else ""

    # Skip empty messages
    if not message_text:
        return

    # Check if the message has already been processed in the database
    if is_message_processed(message.id):
        return

   # Get the channel's username
    channel_username = event.chat.username if event.chat.username else None

    # If the channel doesn't have a username, skip processing this message
    if channel_username is None:
        print(f"Error: Could not find username for the message from channel {event.chat.id} "
            f"(Message ID: {message.id}, Sender ID: {message.sender_id}, Message Text: {message.text})")
        return

    # Prepare the data to send to Redis
    message_data = {
        "message_id": message.id,
        "text": message_text,
        "from_user": user["NAME"],
        "from_channel": channel_username,
        "time_received": current_time  # The time the message was received
    }

    # Serialize message data into JSON format
    message_json = json.dumps(message_data)

    # Add to Redis queue
    redis_client.rpush('messages_queue', message_json)

async def main():
    """Run Telegram Client Loop"""

    # Start Telegram
    print("Starting Telegram...")
    await client.start(user["PHONE_NUMBER"])  

    # Start Redis listener
    print("Listening For Redis Notifications...")
    asyncio.create_task(handle_redis_notifications())

    # Run the Telegram client event loop
    await client.run_until_disconnected()  # Keep running the client

def init():
    """Initialise Script And Fetch User Data From Database"""
    # Command-line argument parsing
    print("Starting script...")
    parser = argparse.ArgumentParser(description='Telegram bot client script.')
    parser.add_argument('--userid', required=True, help='User ID to fetch details for.')
    args = parser.parse_args()
    user_id = args.userid

    ######################
    ## NEED TO ADD DB VARS TO CLI

    # Defining User
    global user
    user = {
        "ID": "",
        "NAME": "",
        "API_ID": "",
        "API_HASH": "",
        "PHONE_NUMBER": "",
        "BOT_CHAT": "",
        "TEST_CHAT_LINK": "",
        "CREATED_AT": "",
        "CHANNELS": {
            "ID": "",
            "NAME": "",
            "LINK": "",
        }
    }

    # Connecting to Redis
    print("Connecting to Redis...")
    global redis_client
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Get user data
    print("Fetching User Data...")
    user_details = get_user_details(user_id)
    
    print("Fetching Channel Data...")
    user_channels = get_user_channels(user_id)

    # Check user and channel data exists
    if not user_details and not user_channels:
        print(f"User Not Found or User Has No Channels | UID: {user_id}")
        exit(1)

    # Extract user details into the global user dictionary
    user["ID"], user["NAME"], user["API_ID"], user["API_HASH"], user["PHONE_NUMBER"], user["BOT_CHAT"], user["TEST_CHAT_LINK"], user["CREATED_AT"] = user_details
    user["CHANNELS"] = [{"ID": channel[0], "NAME": channel[1], "LINK": channel[2]} for channel in user_channels]

    # Set up the Telegram client
    global client
    client = TelegramClient(user["NAME"], user["API_ID"], user["API_HASH"])
    print("Completed Init")

if __name__ == '__main__':
    init()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# Check for args

# if no arg for userid then exit

# if no DB connection then exit

# from DB get user details with arg id -> {}
# from DB get user channels -> []

# start telegram listening for messages in channels (list of invite links)

# telegram chanel listener -> recieve message
    # get time recieved
    # check DB if message ID exists [yes]-> return
    # check redis queue if message id is there [yes]-> return
    # send message to reddis queue
    # message {text: message.text, from_user: client_name, from_channel: channel_link, time_recieved: recieved}

# Listen for notifs from queues
    # message {ca: ADDRESS, "time_recieved: 00:00:00.000", time_processed: time.now(), from_channel: channel}
    # if subscibed to channel [yes] -> forward message