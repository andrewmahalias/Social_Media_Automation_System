import json
import logging
import os
import time

from instabot.bot import ChatBot, MessageHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def wait_for_command(msg_handler, thread_id, user_id, command):
    """
    Continuously checks for the command in new messages.
    :param msg_handler: MessageHandler instance
    :param thread_id: The user's thread ID
    :param user_id: The Instagram user ID
    :param command: The command to wait for
    :return: True if the command is found
    """
    while True:
        msg_handler.search_next_message(thread_id, user_id)
        if msg_handler.search_command(user_id, command):
            return True
        time.sleep(6)


def main():
    config = load_config("insta_config.json")
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")

    bot = ChatBot(username, password, config)
    bot.login()
    msg_handler = MessageHandler(bot.cl)

    while True:
        try:
            media_id = bot.cl.media_pk_from_url(config['post_url'])
            target_username = bot.get_target_username(media_id)

            if not target_username:
                logging.info("No target user found based on the trigger keywords.")
                time.sleep(10)
                continue

            msg_handler.send_message_to_user(target_username, config["messages"]["greeting_message"])
            time.sleep(5)

            user_id = bot.cl.user_id_from_username(target_username)
            thread_id = msg_handler._get_user_thread_id(target_username)

            if not thread_id:
                logging.info(f"No thread found for user @{target_username}.")
                time.sleep(10)
                continue

            logging.info(f"Waiting for 'want' command from @{target_username}...")
            if not wait_for_command(msg_handler, thread_id, user_id, "want"):
                continue

            logging.info(f"User @{target_username} wants access.")
            is_subscribed = bot.is_user_subscribed(target_username)

            if is_subscribed:
                msg_handler.send_message_to_user(target_username, config["messages"]["subscribed_message"])
            else:
                msg_handler.send_message_to_user(target_username, config["messages"]["non_subscribed_messages"])

            time.sleep(5)

            logging.info(f"Waiting for 'watch' command from @{target_username}...")
            if wait_for_command(msg_handler, thread_id, user_id, "watch"):
                msg_handler.send_message_to_user(target_username, "Enjoy the content!")

            time.sleep(10)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            logging.info("Restarting bot after 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()
