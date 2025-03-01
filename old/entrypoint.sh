#!/bin/bash

# Printing Ev Data
echo "+===========================================================+"
echo $HOSTNAME
echo "+===========================================================+"
echo "API_ID: $API_ID"
echo "API_HASH: $API_HASH"
echo "PHONE_NUMBER: $PHONE_NUMBER"
echo "TROJAN_BOT_CHAT_ID: $TROJAN_BOT_CHAT_ID"
echo "CHANNEL_INVITE_LINK: $CHANNEL_INVITE_LINK"
echo ""

# Replace placeholders in config.json with environment variables
echo "{\"api_id\": \"$API_ID\", \"api_hash\": \"$API_HASH\", \"phone_number\": \"$PHONE_NUMBER\", \"trojan_bot_chat_id\": \"$TROJAN_BOT_CHAT_ID\", \"channel_invite_links\": $CHANNEL_INVITE_LINK}" > /app/config.json

# Debugging: print the content of config.json
echo "+===========================================================+"
echo "Config.json:"
echo "+===========================================================+"
cat /app/config.json
echo ""

# Loop through environment variables ADDR_1, ADDR_2, ADDR_3, etc., and append them to addresses.txt
i=1
while [ ! -z "$(eval echo \${ADDR_$i})" ]; do
    echo "$(eval echo \${ADDR_$i})" >> /app/addresses.txt
    ((i++))
done

# Debugging: print the content of addresses.txt
echo "+===========================================================+"
echo "addresses.txt:"
echo "+===========================================================+"
cat /app/addresses.txt

# Run the Python application
exec python main.py
