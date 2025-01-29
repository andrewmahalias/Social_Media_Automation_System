import os
import time
import json
import requests
from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()


class Comments:
    def __init__(self, client, trigger_keywords, post_url):
        self.client = client
        self.post_url = post_url
        self.trigger_keywords = trigger_keywords

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


class InstagramBot:
    def __init__(self, username, password, message, trigger_keywords, post_url):
        self.cl = Client()
        self.username = username
        self.password = password
        self.message = message
        self.trigger_keywords = trigger_keywords
        self.post_url = post_url
        self.comments_handler = Comments(self.cl, trigger_keywords, post_url)

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
        comments = self.comments_handler.fetch_comments(media_id)
        filtered_comments = self.comments_handler.filter_comments_by_keywords(comments)

        if filtered_comments:
            return filtered_comments[0].user.username
        return None

    def send_message_to_user(self, username):
        try:
            user_id = self.cl.user_id_from_username(username)
            self.cl.direct_send(self.message, user_ids=[user_id])
            print(f"Message sent to @{username}: {self.message}")
        except Exception as e:
            print(f"Failed to send message to @{username}: {e}")


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    config = load_config("instabot/insta_config.json")

    trigger_keywords = config['trigger_keywords']
    post_url = config['post_url']
    messages = config['messages']

    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")
    message = messages['greeting_message']

    bot = InstagramBot(username, password, message, trigger_keywords, post_url)

    bot.login()

    media_id = bot.cl.media_pk_from_url(post_url)

    target_username = bot.get_target_username(media_id)

    if target_username:
        bot.send_message_to_user(target_username)
    else:
        print("No target user found based on the trigger keywords.")


if __name__ == "__main__":
    main()
