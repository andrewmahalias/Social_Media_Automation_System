from enum import Enum, auto

from instabot.bot_instance import init_bot


class BotState(Enum):
    IDLE = auto()
    WAITING_FOR_WANT = auto()
    CHECKING_SUBSCRIPTION = auto()
    WAITING_FOR_WATCH = auto()
    COMPLETED = auto()


class BotStateMachine: # todo: check it
    def __init__(self):
        self.states = {
            BotState.IDLE: self.idle,
            BotState.WAITING_FOR_WANT: self.waiting_for_want,
            BotState.CHECKING_SUBSCRIPTION: self.checking_subscription,
            BotState.WAITING_FOR_WATCH: self.waiting_for_watch,
            BotState.COMPLETED: self.completed,
        }

    def transition(self, event):
        if event in [config['commands']['want'], config['commands']['done'], config['commands']['watch']]:
            self.current_state = self.states[self.current_state](event)
        else:
            print(f"Invalid event: {event}")

    def idle(self, event):
        return self.waiting_for_want(event)

    def waiting_for_want(self, event):
        if event == config['commands']['want']:
            return self.checking_subscription(event)
        else:
            return self.idle(event)

    def checking_subscription(self, event):
        if event == config['commands']['done']:
            return self.waiting_for_watch(event)
        else:
            return self.checking_subscription(event)

    def waiting_for_watch(self, event):
        if event == config['commands']['watch']:
            return self.completed(event)
        else:
            return self.waiting_for_watch(event)

    def completed(self, event):
        return self.idle(event)

state_manager = BotStateMachine()
config = init_bot()
