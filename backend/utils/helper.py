from backend.domain.tiles import Bonus, Honor, Suit, Tile


def is_suit_tile(tile: Tile) -> bool:
    """Return True if tile is a Suit tile."""
    return isinstance(tile, Suit)


def is_honor_tile(tile: Tile) -> bool:
    """Return True if tile is an Honor tile (wind or dragon)."""
    return isinstance(tile, Honor)


def is_bonus_tile(tile: Tile) -> bool:
    """Return True if tile is a Bonus tile (animal, flower, or season)."""
    return isinstance(tile, Bonus)
