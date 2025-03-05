import logging
import time

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

load_dotenv()
logger = logging.getLogger()


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


class MessageHandler:
    """Handles checking user messages for specific commands in Instagram DMs."""

    def __init__(self, client):
        """
        Initializes the MessageHandler.
        :param client: Instagram client instance (e.g., instagrapi.Client)
        """
        self.client = client
        self.latest_message = None

    def _get_user_thread_id(self, username):
        """
        Finds the thread ID for a conversation with the given username.
        :param username: The Instagram username
        :return: Thread ID or None if not found
        """
        try:
            threads = self.client.direct_threads()

            for thread in threads:
                if username in [u.username for u in thread.users]:
                    logging.info(f"Found thread ID for @{username}: {thread.id}")
                    return thread.id

            return None

        except Exception as e:
            logging.error(f"Error retrieving thread ID for @{username}: {e}")
            return None

    def search_next_message(self, thread_id, user_id):
        """
        Continuously checks for new messages in the thread without handling commands.
        When a new message appears, it is passed to search_command for processing.
        :param thread_id: The ID of the direct message thread
        :param user_id: The Instagram user ID
        :return: The message text if a new message is found, else None
        """
        last_checked_message = None

        while True:
            try:
                last_messages = self.client.direct_messages(thread_id, amount=1)
                logging.info(f"Direct messages response: {last_messages}")

                if last_messages and last_messages[0]:
                    self.latest_message = last_messages[0]

                    if self.latest_message.user_id == user_id and self.latest_message.id != last_checked_message:
                        last_checked_message = self.latest_message.id
                        logging.info(f"New message received: {self.latest_message.text}")
                        return self.latest_message.text

                time.sleep(5)

            except AttributeError:
                logging.error("Error: Attempted to access attributes of NoneType. No valid messages retrieved.")
                return None  # Замість помилки повертаємо `None`

            except Exception as e:
                logging.error(f"Error while checking for new messages: {e}")
                time.sleep(5)

    def search_command(self, user_id, command):
        """
        Searches for the specified command in the latest messages.
        :param user_id: The Instagram user ID
        :param command: The command to search for
        :return: Boolean indicating if the command was found
        """
        try:
            if not self.latest_message or not hasattr(self.latest_message, "text"):
                logging.warning(f"No messages retrieved from user ID {user_id}.")
                return False

            processed_text = self.latest_message.text.strip().lower()
            logging.info(f"Latest message: {processed_text}")

            if command.lower() in processed_text:
                logging.info(f"✓ Command '{command}' found in message from user ID {user_id}.")
                return True

            return False

        except Exception as e:
            logging.error(f"Unexpected error during message retrieval: {e}")
            return False

    def send_message_to_user(self, username, message):
        """
        Sends a message to the specified user.
        :param username:
        :param message:
        :return:
        """
        try:
            user_id = self.client.user_id_from_username(username)
            self.client.direct_send(message, user_ids=[user_id])
            time.sleep(5)
            print(f"Message sent to @{username}: {message}")
        except Exception as e:
            print(f"Failed to send message to @{username}: {e}")


class ChatBot:
    def __init__(self, username, password, config, session_file="session.json"):
        self.config = config
        self.cl = Client()
        self.session_file = session_file
        self.username = username
        self.password = password
        self.comments_handler = CommentsHandler(self.cl, config)

    def login(self):
        """Login to Instagram using session file or credentials."""
        try:
            self.cl.load_settings(self.session_file)
            self.cl.login(self.username, self.password)
            try:
                self.cl.get_timeline_feed()
                print(f"Logged in using session for {self.username}")
                return
            except LoginRequired:
                print("Session expired, re-logging...")
        except Exception as e:
            print(f"Couldn't load session: {e}")

        try:
            self.cl.login(self.username, self.password)
            print(f"Logged in as {self.username}")
            self.cl.dump_settings(self.session_file)
            print(f"New session saved for {self.username}")
        except Exception as e:
            print(f"Login failed: {e}")
            exit(1)

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

    def is_user_subscribed(self,
                           username):  # check this method. It returns False. Find the correct attribute to check subscription
        """
        Checks if the specified user is subscribed to the account.
        :param username:
        :return: True if the user is subscribed, False otherwise.
        """
        try:
            user_id = self.cl.user_id_from_username(username)
            relationships = self.cl.user_friendship_v1(user_id)
            print(f'Subscription status for @{username} - {relationships.followed_by}')

            if relationships:
                return relationships.followed_by

            return False
        except Exception as e:
            print(f"Error checking subscription status for @{username}: {e}")
            return False
