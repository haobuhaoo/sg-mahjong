from backend.domain.tiles import Suit, Tile


def get_invalid_chi_discards(meld_tiles: list[Tile], thrown_tile: Suit) -> set[Suit]:
    """
    For chi melds, determine blocked tiles based on the chi pattern.

    Rules based on the chi meld pattern:
    - Chi BC with thrown D -> cannot throw A or D (gap=1, thrown=last)
    - Chi EF with thrown D -> cannot throw D or G (gap=1, thrown=first)
    - Chi CE with thrown D -> cannot throw D (gap=2, thrown=middle)

    Args:
        meld_tiles: Two tiles from hand used in the chi.
        thrown_tile: The thrown tile that completed the chi.

    Returns:
        Set of invalid tiles to discard.
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
