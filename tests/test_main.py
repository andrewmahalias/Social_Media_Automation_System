# test_handle_comment.py
import pytest
from unittest.mock import MagicMock

from instabot.main import handle_comment
from instabot.state_manager import BotState, state_manager

@pytest.fixture
def setup_mocks(monkeypatch):
    # Мокаємо метод фільтрації коментарів
    from instabot.bot_instance import comments_handler, messages_handler

    comments_handler.filter_comments_by_keywords = MagicMock(return_value=True)
    messages_handler.get_thread_id_from_user_id = MagicMock(return_value="thread_123")
    messages_handler.send_message_to_user = MagicMock()

    return comments_handler, messages_handler

def test_handle_comment_updates_state(setup_mocks):
    user_id = 111
    comment_message = "info"
    username = "test_user"

    # Спочатку стан IDLE
    state_manager.set_state(user_id, BotState.IDLE)

    handle_comment(user_id, comment_message, username)

    # Перевіряємо, що стан змінився
    assert state_manager.get_state(user_id) == BotState.WAITING_FOR_WANT

    # Перевіряємо, що метод send_message_to_user був викликаний
    _, messages_handler = setup_mocks
    messages_handler.send_message_to_user.assert_called_once_with(
        "thread_123",
        pytest.anything()  # тут можна перевірити точний ключ або повідомлення
    )
