import enum


class StateUser(enum.Enum):
    start = 1
    dict = 2
    key_add = 3
    key_del = 4
    key_next = 5
