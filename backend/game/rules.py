from backend.entity.meld import MeldType
from backend.entity.tiles import Suit, Tile


def get_invalid_discard_tiles(
    meld_type: MeldType, meld_tiles: list[Tile], thrown_tile: Tile
) -> set[Tile]:
    """
    Generate a set of tiles that cannot be discarded after making a meld.

    Rules:
    - For chi: blocks certain tiles based on the chi pattern (suit-specific)
    - For pong/gang: cannot discard the same tile again

    Args:
        meld_type: The type of meld done
        meld_tiles: The tiles used from hand in the meld
        thrown_tile: The tile that was thrown to trigger the meld

    Returns:
        Set of tiles that cannot be discarded
    """
    invalid_tiles: set[Tile] = set()

    if meld_type == MeldType.PONG or meld_type == MeldType.GANG:
        invalid_tiles.add(thrown_tile)
    elif (
        meld_type == MeldType.CHI
        and isinstance(thrown_tile, Suit)
        and len(meld_tiles) == 2
        and all(isinstance(tile, Suit) for tile in meld_tiles)
    ):
        invalid_tiles.update(_get_invalid_chi_discards(meld_tiles, thrown_tile))

    return invalid_tiles


def _get_invalid_chi_discards(meld_tiles: list[Tile], thrown_tile: Suit) -> set[Suit]:
    """
    For chi melds, determine blocked tiles based on the chi pattern.

    Rules based on the chi meld pattern:
    - Chi BC with thrown D -> cannot throw A or D (gap=1, thrown=last)
    - Chi EF with thrown D -> cannot throw D or G (gap=1, thrown=first)
    - Chi CE with thrown D -> cannot throw D (gap=2, thrown=middle)

    Args:
        meld_tiles: Two tiles from hand used in the chi
        thrown_tile: The thrown tile that completed the chi

    Returns:
        Set of invalid tiles to discard
    """
    blocked: set[Suit] = {thrown_tile}

    suit_tiles = [tile for tile in meld_tiles if isinstance(tile, Suit)]
    if len(suit_tiles) != 2 or suit_tiles[0].type != thrown_tile.type:
        return blocked

    thrown_num = thrown_tile.number
    all_nums = sorted([tile.number for tile in suit_tiles] + [thrown_num])

    first_num = all_nums[0]
    if all_nums[-1] == thrown_num:
        if first_num > 1:
            blocked.add(Suit(thrown_tile.type, first_num - 1))
    elif all_nums[0] == thrown_num:
        if first_num + 3 <= 9:
            blocked.add(Suit(thrown_tile.type, first_num + 3))

    return blocked
