# Instructions

#### 1. Login to Their Telegram on Browser Using Thier Phone Number

#### 2. Create Telegram app and get info:

    1. Go to -> https://my.telegram.org/apps
    2. Get the api_id
    3. Get the api_hash
    4. App Title -> Chat to Trojan
    5. Stort -> Deez

#### 3. On Telegram Add @solana_trojanbot Bot

#### 4. Join the chanel (https://t.me/cryptoyeezuscalls)

#### 5. Deploy Test Container with their details
    
    1. send a test message
    2. send a test coin

#### 6. Deploy Production Container with Channel
```
https://t.me/cryptoyeezuscalls
```


# Docker Commands

#### See Active Containers
```
docker ps
```

#### See All Containers
```
docker ps -a 
```

#### Start Container
```
docker start -i <name>
```

#### Stop Container
Graceful Stop
```
docker stop <name>
```
Force Kill
```
docker kill <name>
```

#### Remove Container
```
docker rm NAME
```

#### Interact With Container
```
docker attach NAME
```

#### Copying addresses.txt to container
```
docker cp addresses.txt <name>:/app/addresses.txt
```

Exit Interact
```
Exit -> Ctrl + P -> Ctrl + Q
```
#### Create Container
```
docker run -it \
  --name <name> \
  -e API_ID="" \
  -e API_HASH="" \
  -e PHONE_NUMBER="" \
  -e TROJAN_BOT_CHAT_ID="@solana_trojanbot" \
  -e CHANNEL_INVITE_LINK='[""]' \
  --restart=no \
  --tty \
  --interactive \
  umarraj008/my-python-app
```
