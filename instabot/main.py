from instagrapi import Client
import time
import os
import logging
from instagrapi.mixins import comment


cl = Client()
username = os.getenv("INSTA_USERNAME")
password = os.getenv("INSTA_PASSWORD")
try:
    cl.login(username, password)
except Exception as e:
    print(f"Login failed: {e}")

logging.basicConfig(level=logging.INFO)
logging.info(f"Sending DM to {comment.user.username}")


def fetch_comments(media_id):
    comments = cl.media_comments(media_id)
    return comments

def filter_comments(comments, trigger_keywords):
    filtered = []
    for comment in comments:
        if any(keyword.lower() in comment.text.lower() for keyword in trigger_keywords):
            filtered.append(comment)
    return filtered

def send_dm(user_id, message):
    cl.direct_send(message, [user_id])


def bot_workflow(media_id, trigger_keywords, dm_message):
    # Step 1: Fetch Comments
    comments = fetch_comments(media_id)

    # Step 2: Filter Comments
    filtered_comments = filter_comments(comments, trigger_keywords)

    # Step 3: React to Filtered Comments
    for comment in filtered_comments:
        user_id = comment.user.pk
        print(f"Sending DM to {comment.user.username}")
        send_dm(user_id, dm_message)
        time.sleep(10)  # Avoid spamming


media_id = cl.media_id_from_url("https://www.instagram.com/p/POST_URL/")
trigger_keywords = ["help", "support", "info"]
dm_message = "Hello! We noticed your comment. How can we assist you?"
bot_workflow(media_id, trigger_keywords, dm_message)

