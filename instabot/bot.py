import logging

from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()
logger = logging.getLogger()


class CommentsHandler:
    def __init__(self, client, config):
        self.client = client
        self.post_url = config['post_url']
        self.trigger_keywords = config['trigger_keywords']

    def filter_comments_by_keywords(self, comment_message):
        """ Filter comments based on keywords """
        return any(
            keyword.lower() in comment_message.lower()
            for keyword in self.trigger_keywords
        )


class MessageHandler:

    def __init__(self, client, config):
        self.client = client
        self.latest_message = None
        self.config = config
        self.commands = config['commands']
        self.messages = config['messages']

    def get_thread_id_from_user_id(self, user_id):
        try:
            threads = self.client.direct_threads()
            for thread in threads:
                if any(user.pk == user_id for user in thread.users):
                    logging.info(f'Found thread ID for user ID {user_id}: {thread.id}')
                    return thread.id
            logging.warning(f'No thread found for user ID {user_id}')
            return None
        except Exception as e:
            logging.error(f'Error retrieving thread ID: {e}')
            return None

    def find_command(self, message_text):
        for command in self.commands.values():
            if command in message_text.lower():
                return True
        return False

    def send_message_to_user(self, thread_id, message_key):
        try:
            message = self.messages.get(message_key, 'Message not found')
            self.client.direct_send(message, thread_ids=[thread_id])
            print(f'Message sent to thread {thread_id}: {message}')
        except Exception as e:
            print(f'Failed to send message to thread {thread_id}: {e}')


class ChatBot:
    def __init__(self, username, password, config, session_file='session.json'):
        self.config = config
        self.cl = Client()
        self.session_file = session_file
        self.username = username
        self.password = password

    def login(self):
        try:
            self.cl.load_settings(self.session_file)
            self.cl.login(self.username, self.password)
            self.cl.get_timeline_feed()
            print(f'Logged in as {self.username}')
        except Exception as e:
            print(f'Login failed: {e}')

    def get_target_id(self, user_id):
        return user_id

    def get_username(self, username):
        return username

    def is_user_subscribed(self, user_id):
        try:
            relationship = self.cl.user_friendship_v1(user_id)
            if relationship.followed_by:
                logging.info(f'User ID {user_id} is subscribed.')
                return True
            logging.info(f'User ID {user_id} is not subscribed.')
            return False
        except Exception as e:
            logging.error(f'Error checking subscription status for user ID {user_id}: {e}')
            return False


