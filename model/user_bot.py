from model.enum_state import StateUser
from model.enum_state_request import StateRequest


class UserBot:

    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.state_bot = StateUser.start
        self.state_request = StateRequest.ok
        self.count_words = 0
        self.count_request = 0
        self.next_request = 0
