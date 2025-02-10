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
            time.sleep(5)
            print(f"Message sent to @{username}: {message}")
        except Exception as e:
            print(f"Failed to send message to @{username}: {e}")

    def check_user_messages(self, username, command):
        """
        Checks if the specified user sent the specified command.
        :param username: Username to check messages for
        :param command: Command to look for in messages
        :return: Boolean indicating if command was found
        """
        try:
            user_id = self.cl.user_id_from_username(username)
            command = command.lower()

            print(f"Checking messages for user @{username} (ID: {user_id})")
            print(f"Looking for command: '{command}'")

            threads = self.cl.direct_threads()
            user_thread = None

            for thread in threads:
                if username in [u.username for u in thread.users]:
                    user_thread = thread.id
                    break

            if not user_thread:
                print(f"No active thread found with @{username}.")
                return False

            print(f"Found thread ID: {user_thread}")

            for attempt in range(5):
                try:
                    last_messages = self.cl.direct_messages(user_thread, amount=1)

                    if not last_messages:
                        print(f"No messages retrieved from @{username}. Possible API restrictions.")
                        return False

                    print(f"\nAttempt {attempt + 1}/5:")
                    print("Retrieved messages:")
                    for msg in last_messages:
                        print(f"- Original text: '{msg.text}'")
                        if msg.text:
                            processed_text = msg.text.strip().lower()
                            print(f"  Processed text: '{processed_text}'")
                            print(f"  Contains '{command}': {command in processed_text}")

                            if command in processed_text:
                                print(f"✓ Command '{command}' found in message from @{username}")
                                return True

                    print(f"✗ Command not found in any message")
                    return False

                except Exception as e:
                    if "500" in str(e):
                        print(f"Server error 500 for @{username}. Retrying in 30 sec... ({attempt + 1}/5)")
                        time.sleep(30)
                    else:
                        print(f"Unexpected error: {str(e)}")
                        raise e

            print(f"Max retries exceeded for @{username}. Skipping.")
            return False

        except Exception as e:
            print(f"Error checking messages: {e}")
            return False

    def is_user_subscribed(self, username):  # check this method. It returns False. Find correct attribute to check subscription
        """
        Checks if the specified user is subscribed to the account.
        :param username:
        :return: True if the user is subscribed, False otherwise.
        """
        try:
            user_info = self.cl.user_info_by_username(username)
            return user_info.is_followed_by
        except Exception as e:
            print(f"Error checking subscription status for @{username}: {e}")
            return False
