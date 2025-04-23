#!/bin/bash

# Print a section header with a border
print_section() {
  local title="$1"
  echo "+===========================================================+"
  echo "  $title"
  echo "+===========================================================+"
}

# Print the environment variables
print_section "Environment Variables"

echo "Hostname: $HOSTNAME"
echo "API ID: $API_ID"
echo "API HASH: $API_HASH"
echo "Phone Number: $PHONE_NUMBER"
echo "Trojan Bot Chat ID: $TROJAN_BOT_CHAT_ID"
echo "Printer Enabled: $PRINTER"
echo "Allowed Users: ${ALLOWED_USERS[*]}"
echo "Channel Invite Links: ${CHANNEL_INVITE_LINKS[*]}"

# Adding extra space for readability
echo ""

# Set PRINTER to false by default if not set
PRINTER=${PRINTER:-false}

# Check if NEW=true is set to decide if config.json should be updated
if [ "$NEW" == "true" ]; then
    echo "NEW environment variable detected. Updating config.json..."

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
    echo "{\"api_id\": \"$API_ID\", \"api_hash\": \"$API_HASH\", \"phone_number\": \"$PHONE_NUMBER\", \"trojan_bot_chat_id\": \"$TROJAN_BOT_CHAT_ID\", \"channel_invite_links\": $FINAL_CHANNEL_INVITE_LINKS, \"allowed_users\": $FINAL_ALLOWED_USERS}" > /app/config.json

    # Debugging: print the content of config.json
    echo "+===========================================================+"
    echo "Config.json:"
    echo "+===========================================================+"
    cat /app/config.json
    echo ""

else
    echo "Skipping config.json update. Proceeding directly to Python script..."
fi

# Check if printer is enabled
if [ "$PRINTER" == "true" ]; then
    echo "WARNING: This bot will print to log channel!"
    # Run the Python application in printing mode
    exec python main.py -printer

else
    # Run the Python application
    exec python main.py
fi