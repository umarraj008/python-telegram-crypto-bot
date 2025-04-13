#!/bin/bash

set -e  # Exit immediately on error

# Check if at least two arguments are provided (source and destination container names)
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: transfer <from-container> <to-container>"
  exit 1
fi

FROM_CONTAINER="$1"
TO_CONTAINER="$2"
TEMP_DIR="./temp_transfer"  # Temporary directory to store files

echo "Starting transfer from container '$FROM_CONTAINER' to container '$TO_CONTAINER'..."

# Create a temporary directory to store the files
mkdir -p "$TEMP_DIR"

# 1. Copy addresses.txt and session_name.session from the source container to the temporary directory
echo "Copying addresses.txt from $FROM_CONTAINER to temporary directory..."
docker cp "$FROM_CONTAINER":/app/addresses.txt "$TEMP_DIR/addresses.txt" || echo "Warning: addresses.txt not found"

echo "Copying session_name.session from $FROM_CONTAINER to temporary directory..."
docker cp "$FROM_CONTAINER":/app/session_name.session "$TEMP_DIR/session_name.session" || echo "Warning: session_name.session not found"

# 2. Stop the source container
echo "Stopping source container '$FROM_CONTAINER'..."
docker stop "$FROM_CONTAINER"

# 3. Start the destination container
echo "Starting destination container '$TO_CONTAINER'..."
docker start "$TO_CONTAINER"

# 4. Copy the files into the new container
echo "Copying addresses.txt to $TO_CONTAINER..."
docker cp "$TEMP_DIR/addresses.txt" "$TO_CONTAINER":/app/addresses.txt || echo "Warning: addresses.txt not copied"

echo "Copying session_name.session to $TO_CONTAINER..."
docker cp "$TEMP_DIR/session_name.session" "$TO_CONTAINER":/app/session_name.session || echo "Warning: session_name.session not copied"

# 5. Clean up the temporary directory
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo "Transfer complete: $FROM_CONTAINER stopped, $TO_CONTAINER started and updated with new files."