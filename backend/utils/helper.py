from backend.domain.meld import Meld
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


def is_chi_meld(meld: Meld) -> bool:
    """Return True if the meld is a chi (sequence), i.e. tiles are not all identical."""
    return len(meld.tiles) == 3 and len(set(meld.tiles)) > 1
