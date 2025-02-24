import os
import json
import time
import redis
import psycopg2
import requests
from datetime import datetime

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "fake_key")
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "telegram_db")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

# Initialize Redis
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Connect to PostgreSQL database
def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port="5432")

# Process a message through OpenAI (or mock API)
def process_message_with_gpt(message_text):
    try:
        prompt = f"""
        Extract the Solana coin address (CA) from the following Telegram message.
        If the message contains a valid 44-character CA, return: "Buy,<CA>"
        If it suggests a scam/rug pull, return: "Rug Pull,<CA>"
        If there is no CA, return: "No CA"
        
        Message: {message_text}
        """

        # Prepare API request
        api_url = f"{OPENAI_API_BASE_URL}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": prompt}]
        }

        # Send request
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()

        # Extract GPT response
        if "choices" in response_data and len(response_data["choices"]) > 0:
            result = response_data["choices"][0]["message"]["content"].strip()
            return result  # Expected format: "Buy,<CA>" or "Rug Pull,<CA>" or "No CA"

    except Exception as e:
        print(f"[ERROR] OpenAI processing failed: {e}")
    
    return "No CA"

# Check if CA is already in the database
def is_ca_already_used(coin_address):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM coin_addresses WHERE ca = %s", (coin_address,))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result > 0  # True if CA exists, False if new

# Save new CA to the database
def save_coin_address(coin_address, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO coin_addresses (ca, status, created_at) VALUES (%s, %s, %s)",
        (coin_address, status, datetime.utcnow())
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"[INFO] Saved CA {coin_address} with status {status}")

# Listen for new messages in the Redis queue
def process_queue():
    print("[INFO] Controller started, listening for new messages...")

    while True:
        raw_message = redis_client.lpop("processing_queue")  # Get message from Redis queue
        if raw_message:
            data = json.loads(raw_message)
            message_text = data["message_text"]
            received_at = data["received_at"]

            print(f"[{received_at}] Processing new message...")

            # Send to GPT (or mock API)
            gpt_response = process_message_with_gpt(message_text)
            print(f"[INFO] GPT Response: {gpt_response}")

            # Parse GPT response
            parts = gpt_response.split(",")
            if len(parts) == 2:
                status, coin_address = parts[0], parts[1]
            else:
                status = gpt_response
                coin_address = None

            if status == "Buy" and coin_address:
                if not is_ca_already_used(coin_address):  # Check if already used
                    save_coin_address(coin_address, "Buy")
                    redis_client.publish("coin_addresses", json.dumps({"coin_address": coin_address, "received_at": received_at}))
                    print(f"[INFO] Published new CA: {coin_address}")
                else:
                    print(f"[INFO] Duplicate CA found, not publishing: {coin_address}")

            elif status == "Rug Pull" and coin_address:
                save_coin_address(coin_address, "Rug Pull")
                print(f"[INFO] Marked as Rug Pull: {coin_address}")

            else:
                print(f"[INFO] No valid CA found in message.")

        time.sleep(0.1)  # Small delay to prevent CPU overuse

# Run the controller
if __name__ == "__main__":
    process_queue()