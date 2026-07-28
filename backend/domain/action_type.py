from enum import StrEnum


class ActionType(StrEnum):
    """The legal actions a player can take during their turn."""

    CHI = "chi"
    PONG = "pong"
    GANG = "gang"
    SELF_PICK = "self-pick"
