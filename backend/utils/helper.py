from backend.domain.tiles import Bonus, Honor, Suit, Tile


def is_suit_tile(tile: Tile) -> bool:
    """Return True if tile is Suit"""
    return isinstance(tile, Suit)


def is_honor_tile(tile: Tile) -> bool:
    """Return True if tile is Honor"""
    return isinstance(tile, Honor)


def is_bonus_tile(tile: Tile) -> bool:
    """Return True if tile is Bonus"""
    return isinstance(tile, Bonus)
