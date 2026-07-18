from backend.domain.tiles import MeldType, Suit, Tile
from backend.rules.chi import get_invalid_chi_discards
from backend.rules.gang import get_invalid_gang_discards
from backend.rules.pong import get_invalid_pong_discards


def get_invalid_discard_tiles(
    meld_type: MeldType, meld_tiles: list[Tile], thrown_tile: Tile
) -> set[Tile]:
    """
    Generate a set of tiles that cannot be discarded after making a meld.

    Delegates to the appropriate rule module based on meld type.

    Args:
        meld_type: The type of meld done
        meld_tiles: The tiles used from hand in the meld
        thrown_tile: The tile that was thrown to trigger the meld

    Returns:
        Set of tiles that cannot be discarded
    """
    if meld_type == MeldType.PONG:
        return get_invalid_pong_discards(thrown_tile)

    if meld_type == MeldType.GANG:
        return get_invalid_gang_discards(thrown_tile)

    if (
        meld_type == MeldType.CHI
        and isinstance(thrown_tile, Suit)
        and len(meld_tiles) == 2
        and all(isinstance(tile, Suit) for tile in meld_tiles)
    ):
        return get_invalid_chi_discards(meld_tiles, thrown_tile)

    return set()
