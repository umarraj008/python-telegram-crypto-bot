#!/bin/bash
SESSION_NAME=$1

docker run -d --name $SESSION_NAME \
  -e SESSION_NAME=$SESSION_NAME \
  -e DB_HOST=your_db_host \
  -e REDIS_HOST=your_redis_host \
  --restart unless-stopped \
  your-client-image