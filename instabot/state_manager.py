from enum import Enum, auto

class BotState(Enum):
    IDLE = auto()
    WAITING_FOR_WANT = auto()
    CHECKING_SUBSCRIPTION = auto()
    WAITING_FOR_WATCH = auto()
    COMPLETED = auto()

class StateManager:
    def __init__(self):
        self.states = {}
        self.user_data = {}

    def set_state(self, user_id, state: BotState, comment_message=None, username=None):
        self.states[user_id] = state
        if comment_message and username:
            self.user_data[user_id] = (comment_message, username)

    def get_state(self, user_id):
        return self.states.get(user_id, BotState.IDLE)

    def get_next_user(self):
        if self.user_data:
            user_id, data = self.user_data.popitem()
            return user_id, data
        return None, (None, None)

state_manager = StateManager()

