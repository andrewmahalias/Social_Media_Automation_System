from unittest.mock import MagicMock

import pytest

from instabot import main
from instabot.main import check_subscription
from instabot.state_manager import BotState


def test_handle_comment_updates_state(monkeypatch):
    user_id = 123
    comment_message = "hello bot"
    username = "test_user"

    main.comments_handler = MagicMock()
    main.comments_handler.filter_comments_by_keywords.return_value = True

    main.messages_handler = MagicMock()
    main.messages_handler.get_thread_id_from_user_id.return_value = "thread_123"

    main.config = {"messages": {"greeting_message": "Hi!"}}

    main.state_manager = MagicMock()

    main.handle_comment(user_id, comment_message, username, main.comments_handler, main.messages_handler, main.config,
                        main.state_manager)

    main.comments_handler.filter_comments_by_keywords.assert_called_once_with(comment_message)
    main.messages_handler.get_thread_id_from_user_id.assert_called_once_with(user_id)
    main.messages_handler.send_message_to_user.assert_called_once_with("thread_123", "Hi!")
    main.state_manager.set_state.assert_called_once_with(
        user_id, BotState.WAITING_FOR_WANT, comment_message, username
    )


@pytest.mark.parametrize("is_subscribed,expected_state,expected_msg_key", [
    (True, BotState.WAITING_FOR_WATCH, "subscribed_message"),
    (False, BotState.CHECKING_SUBSCRIPTION, "non_subscribed_messages"),
])
def test_check_subscription(is_subscribed, expected_state, expected_msg_key):
    user_id = 42
    thread_id = "thread-42"

    bot = MagicMock()
    bot.is_user_subscribed.return_value = is_subscribed

    messages_handler = MagicMock()
    config = {"messages": {
        "subscribed_message": "You are subscribed!",
        "non_subscribed_messages": "Please subscribe!"
    }}
    state_manager = MagicMock()

    check_subscription(user_id, thread_id, bot, messages_handler, config, state_manager)

    bot.is_user_subscribed.assert_called_once_with(user_id)
    messages_handler.send_message_to_user.assert_called_once_with(
        thread_id, config["messages"][expected_msg_key]
    )
    state_manager.set_state.assert_called_once_with(user_id, expected_state)

#todo: add test handle_direct_message after state machine is implemented
