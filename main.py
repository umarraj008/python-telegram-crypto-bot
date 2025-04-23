# main.py

from bot import TelegramBot
from config_loader import parse_args, load_config
import asyncio

# ───────── Load Config (from config.json) ───────── #
args = parse_args()
config = load_config(args)

async def main():
    """
    Starts the Telegram client, logs in using the phone number, and listens for new messages.
    """

    bot = TelegramBot(config)
    await bot.run()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())