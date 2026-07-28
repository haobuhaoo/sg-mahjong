from backend.domain.action_type import ActionType
from backend.domain.tiles import Tile


class DiscardError(Exception):
    """
    Raised when the tile to be discarded is invalid.

    Attributes:
        tile: The tile that could not be discarded.
    """

    def __init__(self, msg: str, tile: Tile):
        """Create a discard error for the given tile."""
        super().__init__(msg)
        self.tile = tile


class InvalidActionError(Exception):
    """
    Raised when a player action (chi/pong/gang/self-pick) is invalid.

    Attributes:
        action: The attempted action.
        tile: The tile involved in the action, if any.
    """

    def __init__(self, msg: str, action: ActionType, tile: Tile | None):
        """Create an invalid action error for the given action and tile."""
        super().__init__(msg)
        self.action = action
        self.tile = tile
