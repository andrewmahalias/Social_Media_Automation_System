import time

import requests
from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()


class CommentsHandler:
    def __init__(self, client, config):
        self.client = client
        self.post_url = config['post_url']
        self.trigger_keywords = config['trigger_keywords']

    def fetch_comments(self, media_id):
        try:
            comments = self.client.media_comments(media_id)
            return comments
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []

    def filter_comments_by_keywords(self, comments):
        filtered_comments = [
            comment
            for comment in comments
            if any(
                keyword.lower() in comment.text.lower()
                for keyword in self.trigger_keywords
            )
        ]
        return filtered_comments


class ChatBot:
    def __init__(self, username, password, config):
        self.config = config
        self.cl = Client()
        self.username = username
        self.password = password
        self.comments_handler = CommentsHandler(self.cl, config)

    def login(self):
        try:
            self.cl.login(self.username, self.password)
            print(f"Logged in as {self.username}")
        except requests.exceptions.RetryError as e:
            print("Rate limit exceeded. Pausing...")
            time.sleep(60)
        except Exception as e:
            print(f"Login failed: {e}")
            exit(0)

    def get_target_username(self, media_id):
        """
        Determines the target user based on the trigger keywords.
        :param media_id:
        :return:
        """
        comments = self.comments_handler.fetch_comments(media_id)
        filtered_comments = self.comments_handler.filter_comments_by_keywords(comments)

        if filtered_comments:
            return filtered_comments[0].user.username
        return None

    def send_message_to_user(self, username, message):
        """
        Sends a message to the specified user.
        :param username:
        :param message:
        :return:
        """
        try:
            user_id = self.cl.user_id_from_username(username)
            self.cl.direct_send(message, user_ids=[user_id])
            print(f"Message sent to @{username}: {message}")
        except Exception as e:
            print(f"Failed to send message to @{username}: {e}")

    def check_user_messages(self, username, command):
        """ Перевірка, чи користувач відправив потрібне повідомлення """
        try:
            user_id = self.cl.user_id_from_username(username)

            for attempt in range(5):  # До 5 повторних спроб
                try:
                    last_messages = self.cl.direct_messages(user_id, amount=10)
                    for msg in last_messages:
                        if msg.text.strip().lower() == command:
                            print(f"User @{username} sent '{command}'.")
                            return True
                    return False  # Якщо повідомлення немає, повертаємо False

                except Exception as e:
                    if "500" in str(e):
                        print(f"Server error 500 for @{username}. Retrying in 30 sec... ({attempt + 1}/5)")
                        time.sleep(30)  # Чекаємо перед повторною спробою
                    else:
                        raise e  # Інші помилки пробиваємо далі

            print(f"Max retries exceeded for @{username}. Skipping.")
            return False

        except Exception as e:
            print(f"Error checking messages for @{username}: {e}")
            return False

    def is_user_subscribed(self, username):
        """
        Checks if the specified user is subscribed to the account.
        :param username:
        :return: True if the user is subscribed, False otherwise.
        """
        try:
            user_info = self.cl.user_info_by_username(username)
            return user_info.followed_by  # True, якщо підписаний, False — якщо ні
        except Exception as e:
            print(f"Error checking subscription status for @{username}: {e}")
            return False
