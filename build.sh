#!/bin/bash

# Set Docker Hub username
DOCKER_USER="umarraj008"
DOCKER_REPO="python-telegram"

# Services list
SERVICES=("client" "controller" "web")

# Loop through each service, build, and push
for SERVICE in "${SERVICES[@]}"; do
    echo "Building $SERVICE..."
    docker build -t $DOCKER_USER/$DOCKER_REPO/$SERVICE ./$SERVICE

    echo "Pushing $SERVICE to Docker Hub..."
    docker push $DOCKER_USER/$DOCKER_REPO/$SERVICE
done

echo "All images built and pushed successfully!"