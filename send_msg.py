import time
import os
import requests
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

cl = Client()

username = os.getenv("INSTA_USERNAME")
password = os.getenv("INSTA_PASSWORD")
target_username = os.getenv("TARGET_USERNAME")
message = os.getenv("MESSAGE")
post_url = os.getenv("POST_URL")
trigger_keywords = os.getenv("TRIGGER_KEYWORDS")

try:
    cl.login(username, password)
except requests.exceptions.RetryError as e:
    print("Rate limit exceeded. Pausing...")
    time.sleep(60)

def fetch_comments(media_id):
    """Fetch comments from the post by media ID."""
    comments = cl.media_comments(media_id)
    return comments


def filter_comments_by_keywords(comments, keywords):
    """Filter comments containing any of the keywords."""
    filtered_comments = []
    for comment in comments:
        if any(keyword.lower() in comment.text.lower() for keyword in keywords):
            filtered_comments.append(comment)
    return filtered_comments


def send_message_to_user(target_username, message):
    user_id = cl.user_id_from_username(target_username)

    cl.direct_send(message, user_ids=[user_id])
    print(f"Message sent to {target_username}: {message}")


def main():
    # Get media ID from the post URL
    media_id = cl.media_pk_from_url(post_url)

    # Fetch comments from the post
    comments = fetch_comments(media_id)

    # Filter comments based on keywords
    filtered_comments = filter_comments_by_keywords(comments, trigger_keywords)

    # Send message to users who left filtered comments
    for comment in filtered_comments:
        user_id = comment.user.pk
        send_message_to_user(comment.user.username, message)
        time.sleep(10)  # Avoid spamming, adjust as needed


if __name__ == "__main__":
    main()
