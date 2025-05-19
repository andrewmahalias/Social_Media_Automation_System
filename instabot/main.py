import logging
import time

from bot_instance import bot
from instabot.bot import MessageHandler
from instabot.state_manager import StateManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    msg_handler = MessageHandler(bot.cl)
    state_manager = StateManager()

    # todo: add general bot logic
    while True:
        try:


        except Exception as e:
            logging.error(f"Error occurred: {e}")
            logging.info("Restarting bot after 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()
