import json
import os
from instabot.bot import ChatBot, CommentsHandler, MessageHandler


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


config = load_config("insta_config.json")
username = os.getenv("INSTA_USERNAME")
password = os.getenv("INSTA_PASSWORD")

bot = ChatBot(username, password, config)
comments_handler = CommentsHandler(bot.cl, config)
messages_handler = MessageHandler(bot.cl)
bot.login()

bot.cl.base_headers[
    "User-Agent"] = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36"
bot.cl.base_headers["X-IG-App-ID"] = "567067343352427"
bot.cl.base_headers["X-IG-Device-ID"] = "android-49904f1265b9805d"
bot.cl.base_headers["X-IG-Android-ID"] = "android-49904f1265b9805d"
bot.cl.base_headers["X-IG-Connection-Type"] = "WIFI"
bot.cl.base_headers["X-IG-Capabilities"] = "3brTvw=="
bot.cl.base_headers["Accept-Language"] = "en-US"

bot.cl.api_version = "269.0.0.18.75"
bot.cl.device_settings = {
    "manufacturer": "Xiaomi",
    "model": "M2101K6G",
    "android_version": 13,
    "android_release": "33",
}
