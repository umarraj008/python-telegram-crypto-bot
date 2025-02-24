# Set Docker Hub username
$DOCKER_USER = "umarraj008"
$DOCKER_REPO = "python-telegram"

# List of services to build and push
$SERVICES = @("client", "controller", "web")

foreach ($SERVICE in $SERVICES) {
    Write-Host "Building $SERVICE..."
    docker build -t "$DOCKER_USER/$DOCKER_REPO/$SERVICE" "./$SERVICE"

    Write-Host "Pushing $SERVICE to Docker Hub..."
    docker push "$DOCKER_USER/$DOCKER_REPO/$SERVICE"
}

Write-Host "All images built and pushed successfully!"
