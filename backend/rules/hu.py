from collections import Counter

from backend.domain.tiles import Suit, Tile
from backend.utils.hand_types import (
    FOUR_GREAT_BLESSINGS,
    THIRTEEN_WONDERS,
    THREE_GREAT_SCHOLARS,
)
from backend.utils.helper import is_suit_tile


def can_hu(hand_tile: list[Tile], open_tile: list[list[Tile]], tile: Tile) -> bool:
    """
    Check if player can win with the given tile.

    A winning hand requires either:
    1. 4 complete sets + 1 pair from concealed tiles
    2. Thirteen Wonders (13 unique orphans + 1 pair)
    3. Three Great Scholars (3 triplets of all the Dragon tiles;
        rest of the hand is immaterial)
    4. Four Great Blessings (4 triplets of all the Wind tiles;
        rest of the hand is immaterial, no pair required)

    `tile` is the tile just drawn/claimed; it is checked hypothetically and is not
    mutated into `hand_tile`.

    A Short Hand (fewer tiles than expected) or Long Hand (more tiles than expected)
    forfeits the right to win for the current hand, even if the tiles happen to look
    complete.
    """
    if len(hand_tile) + 3 * len(open_tile) < 13:
        return False

    concealed = hand_tile + [tile]
    sets_needed = 4 - len(open_tile)

    if sets_needed < 0:
        return False

    # Standard winning hand: 4 sets + 1 pair
    if len(concealed) == sets_needed * 3 + 2:
        if _can_form_sets_and_pair(concealed, sets_needed):
            return True

    # Special case: Thirteen Wonders (only valid with no open melds)
    if not open_tile and _is_thirteen_wonders(concealed):
        return True

    # Special case: Three Great Scholars
    if _is_three_great_scholars(concealed, open_tile):
        return True

    # Special case: Four Great Blessings
    if _is_four_great_blessings(concealed, open_tile):
        return True

    return False


# Private methods


def _can_form_sets_and_pair(concealed: list[Tile], sets_needed: int) -> bool:
    """
    Try every distinct tile as the hand's pair (eye), then check whether
    the remaining tiles decompose cleanly into `sets_needed` sets.

    Note: `sets_needed` is passed through unchanged here, since removing the
    pair doesn't consume a meld - the decrementing happens inside
    `_can_decompose` each time it peels off a triplet or run.
    """
    counter = Counter(t for t in concealed)

    for tile in list(counter.keys()):
        if counter[tile] >= 2:
            counter[tile] -= 2
            if counter[tile] == 0:
                del counter[tile]

            if _can_decompose(counter, sets_needed):
                counter[tile] = counter.get(tile, 0) + 2
                return True

            counter[tile] = counter.get(tile, 0) + 2

    return False


def _can_decompose(counter: Counter, sets_needed: int) -> bool:
    """
    Recursively check whether `counter` can be split into exactly
    `sets_needed` melds (triplets and/or runs), with nothing left over.

    Always resolves the smallest remaining tile first (via sort_key()):
    since nothing smaller exists in the multiset, that tile can only be
    part of a triplet or the start of a run, never the middle/end of one.
    This keeps the branching correct and small.
    """
    if sets_needed == 0:
        return not counter
    if not counter:
        return False

    tile = min(counter.keys(), key=lambda t: t.sort_key())

    # option 1: pong meld
    if counter[tile] >= 3:
        counter[tile] -= 3
        if counter[tile] == 0:
            del counter[tile]

        if _can_decompose(counter, sets_needed - 1):
            counter[tile] = counter.get(tile, 0) + 3
            return True

        counter[tile] = counter.get(tile, 0) + 3

    # option 2: chi meld - suited tiles only, and only as the start
    # of the run since `tile` is the current smallest remaining.
    if is_suit_tile(tile) and tile.number <= 7:
        t2, t3 = Suit(tile.type, tile.number + 1), Suit(tile.type, tile.number + 2)
        chi_meld = (tile, t2, t3)
        if counter.get(t2, 0) > 0 and counter.get(t3, 0) > 0:
            for t in chi_meld:
                counter[t] -= 1
                if counter[t] == 0:
                    del counter[t]

            if _can_decompose(counter, sets_needed - 1):
                for t in chi_meld:
                    counter[t] = counter.get(t, 0) + 1
                return True

            for t in chi_meld:
                counter[t] = counter.get(t, 0) + 1

    return False


def _is_thirteen_wonders(tiles: list[Tile]) -> bool:
    """
    Thirteen Wonders:

    Exactly the 13 unique orphan tiles (1s/9s of each suit, all 4 Winds, all 3 Dragons)
    plus one duplicate of any one of them, fully concealed (14 tiles total).
    """
    if len(tiles) != 14:
        return False

    counter = Counter(t for t in tiles)
    return len(counter) == 13 and all(t in THIRTEEN_WONDERS for t in tiles)


def _is_three_great_scholars(
    hand_tile: list[Tile], open_tile: list[list[Tile]]
) -> bool:
    """
    Three Great Scholars:

    At least 3 of each of the 3 Dragon tiles, combining concealed tiles and exposed
    melds. The rest of the hand does not need to form a valid set/pair structure once
    this condition is met.
    """
    dragon_tiles = [t for t in hand_tile if t in THREE_GREAT_SCHOLARS]
    dragon_tiles.extend(
        [tile for meld in open_tile for tile in meld if tile in THREE_GREAT_SCHOLARS]
    )
    counter = Counter(t for t in dragon_tiles)
    return len(counter) == 3 and all(c >= 3 for c in counter.values())


def _is_four_great_blessings(
    hand_tile: list[Tile], open_tile: list[list[Tile]]
) -> bool:
    """
    Four Great Blessings:

    At least 3 of each of the 4 Wind tiles, combining concealed tiles and exposed melds.
    The rest of the hand is immaterial once this condition is met - it doesn't even need
    to form a valid pair.
    """
    wind_tiles = [t for t in hand_tile if t in FOUR_GREAT_BLESSINGS]
    wind_tiles.extend(
        [tile for meld in open_tile for tile in meld if tile in FOUR_GREAT_BLESSINGS]
    )
    counter = Counter(t for t in wind_tiles)
    return len(counter) == 4 and all(c >= 3 for c in counter.values())
