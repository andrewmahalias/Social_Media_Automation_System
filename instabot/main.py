import logging
import time
from instabot.bot_instance import init_bot
from instabot.state_manager import BotState, state_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def handle_comment(user_id, comment_message, username, comments_handler, messages_handler, config, state_manager):
    if comments_handler.filter_comments_by_keywords(comment_message):
        thread_id = messages_handler.get_thread_id_from_user_id(user_id)
        messages_handler.send_message_to_user(thread_id, config['messages']['greeting_message'])
        state_manager.set_state(user_id, BotState.WAITING_FOR_WANT, comment_message, username)

def check_subscription(user_id, thread_id, bot, messages_handler, config, state_manager):
    if bot.is_user_subscribed(user_id):
        messages_handler.send_message_to_user(thread_id, config['messages']['subscribed_message'])
        state_manager.set_state(user_id, BotState.WAITING_FOR_WATCH)
    else:
        messages_handler.send_message_to_user(thread_id, config['messages']['non_subscribed_messages'])
        state_manager.set_state(user_id, BotState.CHECKING_SUBSCRIPTION)

def handle_direct_message(user_id, message_text, bot, messages_handler, config, state_manager): #todo: change using state machine
    thread_id = bot.get_thread_id_from_user_id(user_id)
    current_state = state_manager.get_state(user_id)

    if current_state == BotState.WAITING_FOR_WANT and message_text.lower() == config['commands']['want']:
        check_subscription(user_id, thread_id, bot, messages_handler, config, state_manager)
    elif current_state == BotState.CHECKING_SUBSCRIPTION and message_text.lower() == config['commands']['done']:
        check_subscription(user_id, thread_id, bot, messages_handler, config, state_manager)
    elif current_state == BotState.WAITING_FOR_WATCH and message_text.lower() == config['commands']['watch']:
        messages_handler.send_message_to_user(thread_id, config['messages']['content_getting'])
        state_manager.set_state(user_id, BotState.COMPLETED)
    elif current_state == BotState.COMPLETED:
        messages_handler.send_message_to_user(thread_id, config['messages']['already_completed'])

def main():
    bot, comments_handler, messages_handler, config = init_bot()
    while True:
        user_id, data = state_manager.get_next_user()
        if user_id:
            comment, username = data
            handle_comment(user_id, comment, username, comments_handler, messages_handler, config, state_manager)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
