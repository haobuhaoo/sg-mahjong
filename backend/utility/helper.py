from backend.entity.tiles import Bonus, Honor, Suit, Tile


def is_suit_tile(tile: Tile) -> bool:
    return isinstance(tile, Suit)


def is_honor_tile(tile: Tile) -> bool:
    return isinstance(tile, Honor)


def is_bonus_tile(tile: Tile) -> bool:
    return isinstance(tile, Bonus)
