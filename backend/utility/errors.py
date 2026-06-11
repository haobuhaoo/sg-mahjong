from backend.entity.meld import MeldType
from backend.entity.tiles import Tile


class DiscardError(Exception):
    def __init__(self, msg: str, tile: Tile):
        """Raised when tile to be discard is invalid."""
        super().__init__(msg)
        self.tile = tile


class InvalidActionError(Exception):
    def __init__(self, msg: str, action: MeldType, tile: Tile):
        """Raised when action done is invalid."""
        super().__init__(msg)
        self.action = action
        self.tile = tile
