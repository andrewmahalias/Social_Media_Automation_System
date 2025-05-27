import logging
import time

from bot_instance import bot, messages_handler, comments_handler, config

from instabot.state_manager import StateManager, BotState

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    state_manager = StateManager()

    # todo: add general bot logic
    while True:
        try:
            user_id, (comment_message, username) = state_manager.get_next_user()
            if user_id is not None:
                current_state = state_manager.get_state(user_id)
                if current_state == BotState.IDLE:
                    (comments_handler.filter_comments_by_keywords(comment_message))
                    logging.info(f"New comment from @{username}: {comment_message}")
                    thread_id = bot.get_thread_id_from_user_id(user_id)
                    messages_handler.send_message_to_user(thread_id, config['messages']['greeting_message'])
                    state_manager.set_state(user_id, BotState.WAITING_FOR_WANT)

                    message_text = messages_handler.find_command(message_text)
                    if state_manager.get_state(user_id) == BotState.WAITING_FOR_WANT:
                        messages_handler.find_command(message_text=config['commands']['want'])
                        state_manager.set_state(user_id, BotState.CHECKING_SUBSCRIPTION)

                        if bot.is_user_subscribed(user_id):
                            messages_handler.send_message_to_user(thread_id, config['messages']['subscribed_message'])
                            state_manager.set_state(user_id, BotState.WAITING_FOR_WATCH)
                        else:
                            messages_handler.send_message_to_user(thread_id,
                                                                  config['messages']['non_subscribed_messages'])
                            state_manager.set_state(user_id, BotState.IDLE)


        except Exception as e:
            logging.error(f"Error occurred: {e}")
            logging.info("Restarting bot after 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()
