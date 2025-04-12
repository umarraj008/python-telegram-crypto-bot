#!/bin/bash

set -e  # Exit immediately on error

if [ -z "$1" ]; then
  echo "Usage: update <container-name>"
  exit 1
fi

CONTAINER_NAME="$1"
TEMP_DIR="updater_temp"

echo "Updating container: $CONTAINER_NAME"
mkdir -p "$TEMP_DIR"

# 1. Copy essential files from the running container
echo "Copying essential files..."
docker cp "$CONTAINER_NAME":/app/addresses.txt "$TEMP_DIR/addresses.txt" || echo "Warning: addresses.txt not found"
docker cp "$CONTAINER_NAME":/app/session_name.session "$TEMP_DIR/session_name.session" || echo "Warning: session_name.session not found"

# Extract environment variables
echo "Extracting environment variables..."
docker inspect "$CONTAINER_NAME" | jq -r '.[0].Config.Env[]' > "$TEMP_DIR/env_vars.txt"

# Extract image name
IMAGE=$(docker inspect --format='{{.Config.Image}}' "$CONTAINER_NAME")

# 2. Stop and remove the old container
echo "Stopping and removing old container..."
docker stop "$CONTAINER_NAME"
docker rm "$CONTAINER_NAME"

# 3. Create new container (paused using sleep)
echo "Creating new container with preserved environment variables..."
ENV_FLAGS=$(cat "$TEMP_DIR/env_vars.txt" | sed 's/^/--env /' | xargs)
docker create --name "$CONTAINER_NAME" $ENV_FLAGS "$IMAGE" sleep infinity

# 4. Copy essential files into new container
echo "Copying files into new container..."
docker cp "$TEMP_DIR/addresses.txt" "$CONTAINER_NAME":/app/addresses.txt || echo "Warning: addresses.txt not copied"
docker cp "$TEMP_DIR/session_name.session" "$CONTAINER_NAME":/app/session_name.session || echo "Warning: session_name.session not copied"

# 5. Clean up temp files
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# 6. Start the new container and run the app
echo "Starting container and launching app..."
docker start "$CONTAINER_NAME"
docker exec -d "$CONTAINER_NAME" /app/entrypoint.sh

echo "Update complete: $CONTAINER_NAME is now running."