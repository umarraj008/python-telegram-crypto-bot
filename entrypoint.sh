#!/bin/bash

# Printing Env Data
echo "+===========================================================+"
echo "Hostname: $HOSTNAME"
echo "+===========================================================+"
echo "API_ID: $API_ID"
echo "API_HASH: $API_HASH"
echo "PHONE_NUMBER: $PHONE_NUMBER"
echo "TROJAN_BOT_CHAT_ID: $TROJAN_BOT_CHAT_ID"
echo "CHANNEL_INVITE_LINK_1: $CHANNEL_INVITE_LINK_1"
echo "CHANNEL_INVITE_LINK_2: $CHANNEL_INVITE_LINK_2"
echo "CHANNEL_INVITE_LINK_3: $CHANNEL_INVITE_LINK_3"
echo "... (and more links if set)"
echo ""

# Initialize an empty array to store the invite links
CHANNEL_INVITE_LINKS=()

# Loop to dynamically add each environment variable
i=1
while true; do
    INVITE_VAR="CHANNEL_INVITE_LINK_$i"
    INVITE_URL="${!INVITE_VAR}"
    
    if [ -z "$INVITE_URL" ]; then
        break  # Stop if we find an empty or unset value
    fi
    
    # Add the URL to the array with quotes
    if [ ${#CHANNEL_INVITE_LINKS[@]} -gt 0 ]; then
        # Add a comma before adding the next item
        CHANNEL_INVITE_LINKS+=(", \"$INVITE_URL\"")
    else
        CHANNEL_INVITE_LINKS+=("\"$INVITE_URL\"")
    fi
    
    # Increment the counter for the next variable
    ((i++))
done

# Construct the final JSON array from the invite links
FINAL_CHANNEL_INVITE_LINKS="[${CHANNEL_INVITE_LINKS[@]}]"

# Debugging: show the final constructed array
echo "Final constructed CHANNEL_INVITE_LINKS: $FINAL_CHANNEL_INVITE_LINKS"

# Replace placeholders in config.json with environment variables
echo "{\"api_id\": \"$API_ID\", \"api_hash\": \"$API_HASH\", \"phone_number\": \"$PHONE_NUMBER\", \"trojan_bot_chat_id\": \"$TROJAN_BOT_CHAT_ID\", \"channel_invite_links\": $FINAL_CHANNEL_INVITE_LINKS}" > /app/config.json

# Debugging: print the content of config.json
echo "+===========================================================+"
echo "Config.json:"
echo "+===========================================================+"
cat /app/config.json
echo ""

# Check the value of the UPDATE variable
if [ "$UPDATE" == "true" ]; then
    echo "Update mode is enabled. Skipping Python script execution."
else
    # If UPDATE is not true (or is false), run the Python application
    echo "Running the Python application..."
    exec python main.py
fi