#!/bin/bash

set -e  # Exit immediately on error

# Check if at least three arguments are provided (container name, new container name, image tag)
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: updater <container-name> <new-container-name> <tag>"
  exit 1
fi

CONTAINER_NAME="$1"
NEW_CONTAINER_NAME="$2"
TAG="$3"
IMAGE="umarraj008/telegram-bot:$TAG"  # Use the image with the specified tag
TEMP_DIR="updater_temp"

echo "Updating container: $CONTAINER_NAME with image: $IMAGE"
mkdir -p "$TEMP_DIR"

# 1. Copy essential files from the running container
echo "Copying essential files..."
docker cp "$CONTAINER_NAME":/app/addresses.txt "$TEMP_DIR/addresses.txt" || echo "Warning: addresses.txt not found"
docker cp "$CONTAINER_NAME":/app/session_name.session "$TEMP_DIR/session_name.session" || echo "Warning: session_name.session not found"

# Extract environment variables
echo "Extracting environment variables..."
docker inspect "$CONTAINER_NAME" | jq -r '.[0].Config.Env[]' | grep -v '7399' > "$TEMP_DIR/env_vars.txt"  # Filter out any invalid environment vars

# 2. Pull the image to ensure it's up to date
echo "Pulling image: $IMAGE..."
docker pull "$IMAGE"

# 3. Create the new container (paused using sleep)
echo "Creating new container with image $IMAGE and preserved environment variables..."
ENV_FLAGS=$(cat "$TEMP_DIR/env_vars.txt" | sed 's/^/--env /' | xargs)
docker create --name "$NEW_CONTAINER_NAME" $ENV_FLAGS "$IMAGE" sleep infinity

# 4. Copy essential files into the new container
echo "Copying files into new container..."
docker cp "$TEMP_DIR/addresses.txt" "$NEW_CONTAINER_NAME":/app/addresses.txt || echo "Warning: addresses.txt not copied"
docker cp "$TEMP_DIR/session_name.session" "$NEW_CONTAINER_NAME":/app/session_name.session || echo "Warning: session_name.session not copied"

# 5. Clean up temp files
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# 6. Start the new container and run the app
echo "Starting new container and launching app..."
docker start "$NEW_CONTAINER_NAME"
docker exec -d "$NEW_CONTAINER_NAME" /app/entrypoint.sh

# 7. Stop and remove the old container after successful creation of the new one
echo "Stopping and removing the old container..."
docker stop "$CONTAINER_NAME"
docker rm "$CONTAINER_NAME"

echo "Update complete: $CONTAINER_NAME has been replaced by $NEW_CONTAINER_NAME with image $IMAGE."