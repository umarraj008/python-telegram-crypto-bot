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

# Make PRINTER optional (default to false if not set)
PRINTER=${PRINTER:-false}

# Loop to dynamically add each environment variable
i=1
while true; do
    INVITE_VAR="CHANNEL_INVITE_LINK_$i"
    INVITE_URL="${!INVITE_VAR}"

    if [ -z "$INVITE_URL" ]; then
        break  # Stop if we find an empty or unset value
    fi

    # Check if the link is numeric (this is for numerical values like chat IDs)
    if [[ "$INVITE_URL" =~ ^-?[0-9]+$ ]]; then
        # If it's a number, don't add quotes around it
        if [ ${#CHANNEL_INVITE_LINKS[@]} -gt 0 ]; then
            CHANNEL_INVITE_LINKS+=(", $INVITE_URL")
        else
            CHANNEL_INVITE_LINKS+=("$INVITE_URL")
        fi
    else
        # If it's not a number, add quotes around the URL
        if [ ${#CHANNEL_INVITE_LINKS[@]} -gt 0 ]; then
            CHANNEL_INVITE_LINKS+=(", \"$INVITE_URL\"")
        else
            CHANNEL_INVITE_LINKS+=("\"$INVITE_URL\"")
        fi
    fi

    # Increment the counter for the next variable
    ((i++))
done

# Construct the final JSON array from the invite links
FINAL_CHANNEL_INVITE_LINKS="[${CHANNEL_INVITE_LINKS[@]}]"

# Construct the final JSON array from the invite links
FINAL_CHANNEL_INVITE_LINKS="[${CHANNEL_INVITE_LINKS[@]}]"

# Initialize an empty array to store allowed users
ALLOWED_USERS=()

# Loop to dynamically add each environment variable for allowed users
j=1
while true; do
    USER_VAR="ALLOWED_USER_$j"
    USERNAME="${!USER_VAR}"
    
    if [ -z "$USERNAME" ]; then
        break  # Stop if we find an empty or unset value
    fi
    
    # Add the username to the array with quotes
    if [ ${#ALLOWED_USERS[@]} -gt 0 ]; then
        # Add a comma before adding the next item
        ALLOWED_USERS+=(", \"$USERNAME\"")
    else
        ALLOWED_USERS+=("\"$USERNAME\"")
    fi
    
    # Increment the counter for the next variable
    ((j++))
done

# Construct the final JSON array from the allowed users
FINAL_ALLOWED_USERS="[${ALLOWED_USERS[@]}]"

# Debugging: show the final constructed array
echo "Final constructed CHANNEL_INVITE_LINKS: $FINAL_CHANNEL_INVITE_LINKS"

# Replace placeholders in config.json with environment variables
echo "{\"api_id\": \"$API_ID\", \"api_hash\": \"$API_HASH\", \"phone_number\": \"$PHONE_NUMBER\", \"trojan_bot_chat_id\": \"$TROJAN_BOT_CHAT_ID\", \"printer\": $PRINTER, \"channel_invite_links\": $FINAL_CHANNEL_INVITE_LINKS, \"allowed_users\": $FINAL_ALLOWED_USERS}" > /app/config.json

# Debugging: print the content of config.json
echo "+===========================================================+"
echo "Config.json:"
echo "+===========================================================+"
cat /app/config.json
echo ""

if [ "$PRINTER" = "true" ]; then
    echo "WARNING: This bot will print to log channel!"
fi

# Run the Python application
exec python main.py