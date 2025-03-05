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

    def set_state(self, user_id, state: BotState):
        self.states[user_id] = state

    def get_state(self, user_id):
        return self.states.get(user_id, BotState.IDLE)
