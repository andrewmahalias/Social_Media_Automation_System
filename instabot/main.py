import logging

import uvicorn

from bot_instance import bot, messages_handler, comments_handler, config
from instabot.state_manager import StateManager, BotState
from instabot.webhook_server import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

state_manager = StateManager()


def handle_comment(user_id, comment_message, username):
    """ Handle new comment """
    if comments_handler.filter_comments_by_keywords(comment_message):
        logging.info(f"New comment from @{username}: {comment_message}")
        thread_id = bot.get_thread_id_from_user_id(user_id)

        messages_handler.send_message_to_user(thread_id, config['messages']['greeting_message'])

        state_manager.set_state(user_id, BotState.WAITING_FOR_WANT, comment_message, username)


def check_subscription(user_id, thread_id):
    """ Check subscription """
    if bot.is_user_subscribed(user_id):
        messages_handler.send_message_to_user(thread_id, config['messages']['subscribed_message'])
        state_manager.set_state(user_id, BotState.WAITING_FOR_WATCH)
    else:
        messages_handler.send_message_to_user(thread_id, config['messages']['non_subscribed_messages'])
        state_manager.set_state(user_id, BotState.CHECKING_SUBSCRIPTION)


def handle_direct_message(user_id, message_text):
    """ Handle direct message """
    thread_id = bot.get_thread_id_from_user_id(user_id)
    current_state = state_manager.get_state(user_id)

    if current_state == BotState.WAITING_FOR_WANT:
        if message_text.lower() == config['commands']['want']:
            check_subscription(user_id, thread_id)

    elif current_state == BotState.CHECKING_SUBSCRIPTION:
        if message_text.lower() == config['commands']['done']:
            check_subscription(user_id, thread_id)

    elif current_state == BotState.WAITING_FOR_WATCH:
        if message_text.lower() == config['commands']['watch']:
            messages_handler.send_message_to_user(thread_id, config['messages']['content_getting'])
            state_manager.set_state(user_id, BotState.COMPLETED)

    elif current_state == BotState.COMPLETED:
        messages_handler.send_message_to_user(thread_id, config['messages']['already_completed'])


if __name__ == "__main__":  # todo: test the logic in Postman
    uvicorn.run(app, host="0.0.0.0", port=8000)
