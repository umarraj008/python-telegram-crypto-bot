#!/bin/bash

set -e  # Exit immediately on error

# Check if at least six arguments are provided (container name, new container name, image tag, phone number, and invite links)
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
  echo "Usage: updater <container-name> <new-container-name> <tag> <phone-number> <invite-link-1> <invite-link-2> <...>"
  exit 1
fi

CONTAINER_NAME="$1"
NEW_CONTAINER_NAME="$2"
TAG="$3"
PHONE_NUMBER="$4"  # Take phone number as argument
IMAGE="umarraj008/telegram-bot:$TAG"  # Use the image with the specified tag
TEMP_DIR="updater_temp"
INVITE_LINKS=("${@:5}")  # Collect all invite links from the arguments

echo "Updating container: $CONTAINER_NAME with image: $IMAGE"
mkdir -p "$TEMP_DIR"

# 1. Copy essential files from the running container (addresses.txt and session_name.session)
echo "Copying essential files..."
docker cp "$CONTAINER_NAME":/app/addresses.txt "$TEMP_DIR/addresses.txt" || echo "Warning: addresses.txt not found"
docker cp "$CONTAINER_NAME":/app/session_name.session "$TEMP_DIR/session_name.session" || echo "Warning: session_name.session not found"

# 2. Extract environment variables and filter relevant ones
echo "Extracting environment variables..."
docker inspect "$CONTAINER_NAME" | jq -r '.[0].Config.Env[]' | grep -E '^(API_ID|API_HASH|TROJAN_BOT_CHAT_ID)' > "$TEMP_DIR/env_vars.txt"

# 3. Pull the image to ensure it's up to date
echo "Pulling image: $IMAGE..."
docker pull "$IMAGE"

# 4. Create the new container with the updated image and environment variables (with UPDATE=true)
echo "Creating new container with image $IMAGE and preserved environment variables..."
# Wrap the environment variables in quotes to avoid issues with spaces
ENV_FLAGS=$(cat "$TEMP_DIR/env_vars.txt" | sed 's/^/--env /' | sed 's/\([^=]*=[^ ]*\)/"\1"/g' | xargs)
docker create --name "$NEW_CONTAINER_NAME" --env UPDATE=true $ENV_FLAGS "$IMAGE" sleep infinity

# 5. Copy essential files into the new container
echo "Copying files into new container..."
docker cp "$TEMP_DIR/addresses.txt" "$NEW_CONTAINER_NAME":/app/addresses.txt || echo "Warning: addresses.txt not copied"
docker cp "$TEMP_DIR/session_name.session" "$NEW_CONTAINER_NAME":/app/session_name.session || echo "Warning: session_name.session not copied"

# 6. Start the new container to run the entrypoint with UPDATE=true
echo "Starting new container to allow updates..."
docker start "$NEW_CONTAINER_NAME"

# 7. Set invite links and phone number in the new container's app/.env
echo "Setting invite links and phone number in the new container..."
i=1
for INVITE_LINK in "${INVITE_LINKS[@]}"; do
  docker exec "$NEW_CONTAINER_NAME" sh -c "echo \"CHANNEL_INVITE_LINK_${i}=${INVITE_LINK}\" >> /app/.env"
  ((i++))
done

# Add the phone number to app/.env
echo "Setting PHONE_NUMBER in the new container..."
docker exec "$NEW_CONTAINER_NAME" sh -c "echo \"PHONE_NUMBER=${PHONE_NUMBER}\" >> /app/.env"

# 8. Update the container's environment to set UPDATE=false
echo "Updating UPDATE flag to false in the new container..."
docker update --env UPDATE=false "$NEW_CONTAINER_NAME"

# 9. Restart the new container to run the normal Python script (now that UPDATE=false)
echo "Restarting the new container to run the Python script..."
docker restart "$NEW_CONTAINER_NAME"

# 10. Stop the old container after successful creation of the new one
echo "Stopping the old container..."
docker stop "$CONTAINER_NAME"

echo "Update complete: $CONTAINER_NAME has been replaced by $NEW_CONTAINER_NAME with image $IMAGE."