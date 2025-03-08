import os
import psycopg2
import redis
import json
import re
import asyncio
import base58
from datetime import datetime

# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "telegram_db")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

# PostgreSQL Database Connection
def get_db_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )

# Check for Redis and Postgres connection
def check_connections():
    """Check Redis and PostgreSQL connection"""
    try:
        # Test Redis connection
        redis_client.ping()
        print("Connected to Redis...")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        exit(1)

    try:
        # Test PostgreSQL connection
        conn = get_db_connection()
        conn.close()
        print("Connected to PostgreSQL...")
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        exit(1)

# Process next message from the queue
async def process_message():
    """Process the next message from the Redis queue"""
    while True:
        # Get the next message from Redis queue
        if message_data:
            try:
                print(f"Processing new message ID {message_id}.")

                # Deserialize message data (JSON)
                message_data = json.loads(message_data)

                # Extract message data
                message_id = message_data.get("message_id")
                text = message_data.get("text", "")
                from_user = message_data.get("from_user")
                from_channel = message_data.get("from_channel")
                time_received = message_data.get("time_received")

                # Check if message_id is already processed in coins table
                if is_message_in_db(message_id):
                    print(f"Message ID {message_id} already exists in the database.")
                    continue

                # Initialize values
                rug_pull = False
                address = ""

                # Processing based on from_channel
                if from_channel == "yeezus":
                    # Check for rug-related words in text
                    if any(word in text.lower() for word in ["rug", "do not buy", "rug pull", "insta rug", "fishing", "front running"]):
                        rug_pull = True
                    
                    # Remove all occurrences of the word "KING" from the text
                    text = text.replace("KING", "")

                    # Check if the text contains the word SPLIT and attempt to combine two parts
                    if "SPLIT" in text:
                        address = combine_solana_address_parts(text)
                    else:
                        # Regex to extract Solana address
                        address = extract_solana_address(text)

                elif from_channel == "apes":
                    # Extract Solana address using regex
                    address = extract_solana_address(text)

                # If no address is found
                if not address:
                    print(f"No address found: {message_id} from {from_channel}")
                    continue
                
                # Validate Solana address
                if not is_valid_solana_address(address):
                    print(f"Address not valid: {message_id} from {from_channel} | {address}")
                    continue

                # Check if address exists in coins table
                if is_address_in_db(address):
                    print(f"Address {address} already exists in the database.")
                    continue

                # If not a rug pull, publish to Redis
                if not rug_pull:
                    publish_to_redis(address, from_channel, time_received)

                # Add new coin record to PostgreSQL
                add_coin_to_db(address, rug_pull, from_channel, message_id)

                # Remove message from queue
                redis_client.lrem('messages_queue', 0, message_data)
                print(f"Processed and removed message ID {message_id} from queue.")

            except Exception as e:
                print(f"Error processing message: {e}")
        
        # Delay before checking for new messages
        await asyncio.sleep(1)

def is_message_in_db(message_id):
    """Check if message_id exists in the coins table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT 1 FROM coins WHERE message_id = %s'
    cursor.execute(query, (message_id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def is_address_in_db(address):
    """Check if address exists in the coins table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT 1 FROM coins WHERE address = %s'
    cursor.execute(query, (address,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def add_coin_to_db(address, rug_pull, from_channel, message_id):
    """Add a new coin record to the coins table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'INSERT INTO coins (address, rug_pull, channel_name, message_id) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (address, rug_pull, from_channel, message_id))
    conn.commit()
    cursor.close()
    conn.close()

def extract_solana_address(text):
    """Extract Solana address from the text using regex"""
    solana_address_pattern = r"[1-9A-HJ-NP-Za-km-z]{32,44}"
    match = re.search(solana_address_pattern, text)
    return match.group(0) if match else None

def is_valid_solana_address(address):
    """Check if a Solana address is valid"""
    if len(address) != 44:
        return False
    try:
        decoded_address = base58.b58decode(address)
    except ValueError:
        return False  # If the base58 decoding fails, the address is invalid
    return len(decoded_address) == 32

def combine_solana_address_parts(text):
    """Combine two Solana address parts found in the text"""
    parts = re.findall(r"[1-9A-HJ-NP-Za-km-z]{32,44}", text)
    if len(parts) == 2:
        return parts[0] + parts[1]
    return ""

def publish_to_redis(address, from_channel, time_received):
    """Publish message to Redis"""
    message = {
        "address": address,
        "from_channel": from_channel,
        "time_received": time_received
    }
    redis_client.publish('messages_channel', json.dumps(message))
    print(f"Published message for address {address} to Redis channel.")

async def main():
    """Main entry point for the script"""
    await process_message()  # Start processing messages

def init():
    # Redis Client Setup
    print("Connecting to Redis...")
    global redis_client
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

    # Check Redis and DB connections
    check_connections()

if __name__ == '__main__':
    init()
    asyncio.run(main())