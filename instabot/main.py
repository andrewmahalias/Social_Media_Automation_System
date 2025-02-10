import json
import os
import time

from instabot.bot import ChatBot


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    config = load_config("insta_config.json")
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")

    bot = ChatBot(username, password, config)
    bot.login()

    media_id = bot.cl.media_pk_from_url(config['post_url'])
    target_username = bot.get_target_username(media_id)

    if target_username:
        bot.send_message_to_user(target_username, config["messages"]["greeting_message"])

        time.sleep(10)  # Даємо користувачеві час на відповідь

        if bot.check_user_messages(target_username, "want"):
            if bot.is_user_subscribed(target_username):
                bot.send_message_to_user(target_username, config["messages"]["subscribed_message"])
            else:
                bot.send_message_to_user(target_username, config["messages"]["non_subscribed_messages"])

            # Перевіряємо, чи користувач хоче переглянути контент
            if bot.check_user_messages(target_username, "watch"):
                bot.send_message_to_user(target_username, "Enjoy the content!")

            # Якщо користувач раніше не був підписаний, але виконав "done"
            if not bot.is_user_subscribed(target_username) and bot.check_user_messages(target_username, "done"):
                bot.send_message_to_user(target_username, "Thank you for your action!")

                # Повторно перевіряємо підписку після "done"
                if bot.is_user_subscribed(target_username):
                    bot.send_message_to_user(target_username, config["messages"]["subscribed_message"])
                    # Тепер користувач може дивитися контент
                    if bot.check_user_messages(target_username, "watch"):
                        bot.send_message_to_user(target_username, "Enjoy the content!")
                else:
                    bot.send_message_to_user(target_username, config["messages"]["non_subscribed_message"][1])

    else:
        print("No target user found based on the trigger keywords.")


if __name__ == "__main__":
    main()
