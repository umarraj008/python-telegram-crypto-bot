#!/bin/bash

# Replace placeholders in config.json with environment variables
echo "{\"api_id\": \"$API_ID\", \"api_hash\": \"$API_HASH\", \"phone_number\": \"$PHONE_NUMBER\", \"trojan_bot_chat_id\": \"$TROJAN_BOT_CHAT_ID\", \"channel_invite_links\": $CHANNEL_INVITE_LINK}" > /app/config.json

# Debugging: print the content of config.json
cat /app/config.json

# Run the Python application
exec python main.py
