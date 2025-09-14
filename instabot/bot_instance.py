import json
import os
from instabot.bot import ChatBot, CommentsHandler, MessageHandler


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def init_bot(config_path="insta_config.json"):
    config = load_config(config_path)
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")

    bot = ChatBot(username, password, config)
    comments_handler = CommentsHandler(bot.cl, config)
    messages_handler = MessageHandler(bot.cl, config)
    bot.login()

    bot.cl.base_headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
        "X-IG-App-ID": "567067343352427",
        "X-IG-Device-ID": "android-49904f1265b9805d",
        "X-IG-Android-ID": "android-49904f1265b9805d",
        "X-IG-Connection-Type": "WIFI",
        "X-IG-Capabilities": "3brTvw==",
        "Accept-Language": "en-US",
    })

    bot.cl.api_version = "269.0.0.18.75"
    bot.cl.device_settings = {
        "manufacturer": "Xiaomi",
        "model": "M2101K6G",
        "android_version": 13,
        "android_release": "33",
    }

    return bot, comments_handler, messages_handler, config
