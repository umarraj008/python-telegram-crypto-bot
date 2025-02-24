import asyncio
import os
import time
import psycopg2
import redis
from datetime import datetime
from telethon import TelegramClient, events
import json

# Connect to PostgreSQL and fetch user details
def get_user_details(session_name):
    conn = psycopg2.connect(
        dbname="telegram_db",
        user="your_user",
        password="your_password",
        host="your_db_host",
        port="5432"
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT telegram_api_id, telegram_api_hash, telegram_session, telegram_channel, bot_chat
        FROM users WHERE session_name = %s AND is_active = TRUE
    """, (session_name,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        return {
            "api_id": result[0],
            "api_hash": result[1],
            "session": result[2],
            "channel": result[3],
            "bot_chat": result[4]
        }
    else:
        print(f"[ERROR] No active session found for {session_name}")
        exit()

# Load user session details
session_name = os.getenv("TELEGRAM_SESSION", "default_session")
user_details = get_user_details(session_name)

# Setup Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
redis_subscriber = redis_client.pubsub()
redis_subscriber.subscribe("coin_addresses")  # Listen for extracted addresses

# Initialize Telegram Client
client = TelegramClient(user_details["session"], user_details["api_id"], user_details["api_hash"])

async def process_message(event):
    """Process incoming messages from the Telegram channel."""
    message_text = event.raw_text
    lines = message_text.strip().split("\n")

    if len(lines) > 3:  # Only process messages with more than 3 lines
        message_time = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{message_time}] Received message in channel, sending to controller...")

        # Check Redis if message is already being processed
        message_hash = hash(message_text)  # Simple deduplication check
        if redis_client.exists(f"processing:{message_hash}"):
            print(f"[{message_time}] Message already being processed. Skipping.")
            return

        redis_client.setex(f"processing:{message_hash}", 30, "processing")  # Mark as processing

        # Send message to controller via Redis queue
        redis_client.rpush("processing_queue", json.dumps({
            "session_name": session_name,
            "message_text": message_text,
            "received_at": message_time
        }))

        print(f"[{message_time}] Sent message to controller.")

async def listen_for_coin_addresses():
    """Listens for new coin addresses from Redis and forwards them to the bot chat."""
    print("[INFO] Listening for new coin addresses...")
    while True:
        message = redis_subscriber.get_message()
        if message and message["type"] == "message":
            data = json.loads(message["data"])
            coin_address = data.get("coin_address")
            received_at = data.get("received_at")
            processed_at = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]

            if coin_address:
                message_to_send = f"""
Received: {received_at}
Processed: {processed_at}
Forwarded: {datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]}

{coin_address}
                """.strip()

                # Send message to bot chat
                await client.send_message(user_details["bot_chat"], message_to_send)
                print(f"[{processed_at}] Forwarded coin address to bot chat.")

        await asyncio.sleep(0.1)  # Prevents busy-waiting

async def main():
    """Main function to start Telegram client and listen for messages."""
    print(f"[INFO] Client {session_name} started, listening for messages...")

    # Start Telegram message listener
    async with client:
        client.add_event_handler(process_message, events.NewMessage(chats=user_details["channel"]))
        await asyncio.gather(listen_for_coin_addresses())

# Run the client
asyncio.run(main())