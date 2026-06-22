from backend.domain.tiles import Tile


class DiscardError(Exception):
    def __init__(self, msg: str, tile: Tile):
        """Raised when tile to be discard is invalid."""
        super().__init__(msg)
        self.tile = tile


class InvalidActionError(Exception):
    def __init__(self, msg: str, action: str, tile: Tile | None):
        """Raised when action done is invalid."""
        super().__init__(msg)
        self.action = action
        self.tile = tile
