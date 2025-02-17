import json
import logging
import os
import time

from instabot.bot import ChatBot, MessageHandler

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
    msg_handler = MessageHandler(bot.cl)

    while True:
        try:
            media_id = bot.cl.media_pk_from_url(config['post_url'])
            target_username = bot.get_target_username(media_id)

            if target_username:
                msg_handler.send_message_to_user(target_username, config["messages"]["greeting_message"])
                time.sleep(10)

                user_id = bot.cl.user_id_from_username(target_username)
                thread_id = msg_handler._get_user_thread_id(target_username)

                if thread_id:
                    # Wait for the next message from the user (this is a blocking call)
                    msg_handler.search_next_message(thread_id, user_id)

                    # Now that we've waited for a message, check for commands
                    if msg_handler._search_command(thread_id, user_id, "want"):
                        logging.info(f"User @{target_username} wants access.")

                    if bot.is_user_subscribed(target_username):
                        msg_handler.send_message_to_user(target_username, config["messages"]["subscribed_message"])
                        if msg_handler._search_command(thread_id, user_id, "watch"):
                            msg_handler.send_message_to_user(target_username, "Enjoy the content!")
                    else:
                        msg_handler.send_message_to_user(target_username, config["messages"]["non_subscribed_messages"])

                        if msg_handler._search_command(thread_id, user_id, "done"):
                            msg_handler.send_message_to_user(target_username, "Thank you for your action!")
                            if bot.is_user_subscribed(target_username):
                                msg_handler.send_message_to_user(target_username,
                                                                 config["messages"]["subscribed_message"])
                                if msg_handler._search_command(thread_id, user_id, "watch"):
                                    msg_handler.send_message_to_user(target_username, "Enjoy the content!")
                            else:
                                msg_handler.send_message_to_user(target_username,
                                                                 config["messages"]["non_subscribed_message"][1])
                else:
                    logging.info(f"User @{target_username} did not send 'want'.")

            else:
                logging.info("No target user found based on the trigger keywords.")

            time.sleep(10)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            logging.info("Restarting bot after 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()
