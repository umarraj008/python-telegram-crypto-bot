import os
import redis
import psycopg2
import json
from redis.exceptions import ConnectionError

# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "telegram_db")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

# if no postgres DB connection then exit
# if no redis connection then exit

# start redis queue

# process next message from queue
    # Message Data Recieved as json:
        # message_id
        # text
        # from_user
        # from_channel
        # time_recieved

    # check postgres DB if coins table has message_id [yes]-> return
    
    # set error = False
    # set rugPull = False
    # set address = ""

    # if from_channel is "yeezus": 
        # if text contains [rug, do not buy, rug pull, insta rug, fishing, front running]
            # [yes]-> rugPull = True
        
        # remove all occurances of the word KING from text

        # use regex on text to extract solana coin address (44 character string)
        # useing solana library public key to check if address is valid 
            # [yes]-> address = extracted address
            # [no]-> see if text contains the word SPLIT
                # [yes]-> using regex find 2 solana coin address parts (2 strings)
                    # if found parts then join the strings to one -> address = combined string
                # [no] -> error = True

    # if from_channel is "apes"
        # use regex on text to extract solana coin address (44 character string)
        # useing solana library public key to check if address is valid 
            # [yes]-> address = extracted address
            # [no] -> error = True

    # if error [yes] -> return

    # check postgres DB if coins table has address [yes]-> return

    # if not rugPull 
        # [yes]-> publish to redis subs on messages_channel: message: {address: address, from_channel: from_channel, time_received: time_recieved}

    # add new coin record to postgres database
        # address
        # rug_pull
        # from_channel
        # message_id

    # remove message from queue