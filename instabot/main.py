import json
import logging
import os
import time

import random

from instabot.bot import ChatBot, MessageHandler
from instabot.state_manager import StateManager, BotState

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    config = load_config("insta_config.json")
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")

    bot = ChatBot(username, password, config)
    bot.login()
    bot.cl.base_headers[  # Move the headers to the separate file
        "User-Agent"] = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36"
    bot.cl.base_headers["X-IG-App-ID"] = "567067343352427"
    bot.cl.base_headers["X-IG-Device-ID"] = "android-49904f1265b9805d"
    bot.cl.base_headers["X-IG-Android-ID"] = "android-49904f1265b9805d"
    bot.cl.base_headers["X-IG-Connection-Type"] = "WIFI"
    bot.cl.base_headers["X-IG-Capabilities"] = "3brTvw=="
    bot.cl.base_headers["Accept-Language"] = "en-US"

    bot.cl.api_version = "269.0.0.18.75"
    bot.cl.device_settings = {
        "manufacturer": "Xiaomi",
        "model": "M2101K6G",
        "android_version": 13,
        "android_release": "33",
    }
    msg_handler = MessageHandler(bot.cl)
    state_manager = StateManager()

    while True:
        try:
            media_id = bot.cl.media_pk_from_url(config['post_url'])
            target_username = bot.get_target_username(media_id)

            if not target_username:
                logging.info("No target user found based on the trigger keywords.")
                time.sleep(10)
                continue

            user_id = bot.cl.user_id_from_username(target_username)
            thread_id = msg_handler._get_user_thread_id(target_username)

            if not thread_id:
                logging.info(f"No thread found for user @{target_username}.")
                time.sleep(10)
                continue

            current_state = state_manager.get_state(user_id)

            # Send greeting message only once
            if current_state == BotState.IDLE:
                logging.info(f"Sending greeting message to @{target_username}")
                msg_handler.send_message_to_user(target_username, config["messages"]["greeting_message"])
                state_manager.set_state(user_id, BotState.WAITING_FOR_WANT)

            # Get the latest message (always check for new messages)
            last_message = msg_handler.search_next_message(thread_id, user_id)

            if last_message:
                last_message = last_message.lower()

                if "want" in last_message:
                    logging.info(f"User @{target_username} requested access.")
                    state_manager.set_state(user_id, BotState.CHECKING_SUBSCRIPTION)

                elif "watch" in last_message:
                    logging.info(f"User @{target_username} requested to watch.")
                    msg_handler.send_message_to_user(target_username, config["messages"]["content_getting"])
                    state_manager.set_state(user_id, BotState.COMPLETED)
                else:
                    continue

            # Check subscription only if the user is in CHECKING_SUBSCRIPTION state
            if current_state == BotState.CHECKING_SUBSCRIPTION:
                is_subscribed = bot.is_user_subscribed(target_username)
                if is_subscribed:
                    msg_handler.send_message_to_user(target_username, config["messages"]["subscribed_message"])
                else:
                    msg_handler.send_message_to_user(target_username, config["messages"]["non_subscribed_messages"])
                state_manager.set_state(user_id, BotState.CHECKING_SUBSCRIPTION)

            elif current_state == BotState.COMPLETED:
                logging.info(f"Interaction with @{target_username} completed.")

            time.sleep(random.randint(5, 18))

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            logging.info("Restarting bot after 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()
