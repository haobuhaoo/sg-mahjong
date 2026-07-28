from collections import Counter

from backend.domain.meld import Meld
from backend.domain.tiles import Dragon, Suit, Tile, Wind, WindType
from backend.rules.hu_result import HandPattern, HuResult
from backend.rules.hand_patterns import (
    FOUR_GREAT_BLESSINGS,
    PURE_GREEN_SUIT_TILES,
    THIRTEEN_WONDERS,
    THREE_GREAT_SCHOLARS,
)
from backend.utils.helper import is_chi_meld, is_honor_tile, is_suit_tile


def can_hu(
    hand_tile: list[Tile],
    open_tile: list[Meld],
    tile: Tile,
    *,
    seat_wind: WindType,
    prevalent_wind: WindType,
    bonus_count: int,
) -> HuResult:
    """
    Check if player can win with the given tile and classify the hand patterns. Detect both
    independent win conditions (any one of which makes the hand winning) and classification patterns
    that describe tile composition or hand structure.

    Independent win conditions:
        - 4 complete sets + 1 pair (standard hand)
        - Thirteen Wonders (13 unique orphans + 1 duplicate)
        - Nine Gates (1112345678999 of a single suit + any tile of that suit, no open melds)
        - Three Great Scholars (3 of each Dragon; rest is immaterial)
        - Four Great Blessings (3 of each Wind; rest is immaterial)

    Classification patterns detected on a winning hand:
        Three Lesser Scholars, Four Lesser Blessings, Sequence Hand, Lesser Sequence Hand, Triplets
        Hand, Fully Concealed, Eighteen Arhats, Half Flush, Full Flush, All Honour, Pure Terminals,
        Mixed Terminals, Pure Green Suit, Chicken Hand.

    A Short Hand (fewer tiles than expected) or Long Hand (more tiles than expected) forfeits the
    right to win for the current hand, even if the tiles happen to look complete.

    Args:
        hand_tile: The player's hand tiles.
        open_tile: The player's open tiles.
        tile: The tile just drawn/claimed. It is checked hypothetically and is not mutated into
            `hand_tile`.
        seat_wind: The player's wind.
        prevalent_wind: The table's wind.
        bonus_count: The number of bonus tiles the player holds.

    Returns:
        HuResult with `is_winning=True`, the set of applicable hand patterns, and `conceal_hand`
        set to True when a shortcut Three Great Scholars or Four Great Blessings win requires
        concealing non-justifying tiles from other players. Returns `HuResult(False)` if the hand
        is not winning.
    """
    if len(hand_tile) + 3 * len(open_tile) != 13:
        return HuResult(False)

    concealed = hand_tile + [tile]
    sets_needed = 4 - len(open_tile)

    if sets_needed < 0:
        return HuResult(False)

    patterns: set[HandPattern] = set()

    # Standard winning hand: 4 sets + 1 pair
    if len(concealed) == sets_needed * 3 + 2:
        if _can_form_sets_and_pair(concealed, sets_needed):
            patterns.add(HandPattern.CHICKEN_HAND)
            if _is_eighteen_arhats(open_tile):
                patterns.add(HandPattern.EIGHTEEN_ARHATS)
            if _is_pure_green_suit(concealed, open_tile):
                patterns.add(HandPattern.PURE_GREEN_SUIT)
            if not _has_exposed_meld(open_tile):
                patterns.add(HandPattern.FULLY_CONCEALED)
            if _is_half_flush(concealed, open_tile):
                patterns.add(HandPattern.HALF_FLUSH)
            if _is_full_flush(concealed, open_tile):
                patterns.add(HandPattern.FULL_FLUSH)
            if _is_all_honour(concealed, open_tile):
                patterns.add(HandPattern.ALL_HONOUR)
            if _is_pure_terminals(concealed, open_tile):
                patterns.add(HandPattern.PURE_TERMINALS)
            if _is_triplets_hand(concealed, sets_needed, open_tile):
                patterns.add(HandPattern.TRIPLETS_HAND)
                if _is_mixed_terminals(concealed, open_tile):
                    patterns.add(HandPattern.MIXED_TERMINALS)
            if _is_sequence_structure(concealed, sets_needed, seat_wind, prevalent_wind):
                if bonus_count == 0:
                    patterns.add(HandPattern.SEQUENCE_HAND)
                else:
                    patterns.add(HandPattern.LESSER_SEQUENCE_HAND)

    # Special case: Thirteen Wonders (only valid with no open melds)
    if not open_tile and _is_thirteen_wonders(concealed):
        patterns.add(HandPattern.THIRTEEN_WONDERS)

    # Special case: Nine Gates (only valid with no open melds)
    if not open_tile and _is_nine_gates(hand_tile, tile):
        patterns.add(HandPattern.NINE_GATES)

    # Special case: Three Great/Lesser Scholars
    if _is_three_great_scholars(concealed, open_tile):
        patterns.add(HandPattern.THREE_GREAT_SCHOLARS)
    if _is_three_lesser_scholars(concealed, open_tile):
        patterns.add(HandPattern.THREE_LESSER_SCHOLARS)

    # Special case: Four Great/Lesser Blessings
    if _is_four_great_blessings(concealed, open_tile):
        patterns.add(HandPattern.FOUR_GREAT_BLESSINGS)
    if _is_four_lesser_blessings(concealed, open_tile):
        patterns.add(HandPattern.FOUR_LESSER_BLESSINGS)

    if patterns:
        conceal_hand = (
            HandPattern.THREE_GREAT_SCHOLARS in patterns
            or HandPattern.FOUR_GREAT_BLESSINGS in patterns
        ) and HandPattern.CHICKEN_HAND not in patterns
        return HuResult(True, frozenset(patterns), conceal_hand=conceal_hand)

    return HuResult(False)


# Private methods


def _can_form_sets_and_pair(concealed: list[Tile], sets_needed: int) -> bool:
    """
    Try every distinct tile as the hand's pair (eye), then check whether the remaining tiles
    decompose cleanly into `sets_needed` sets.
    """
    counter = Counter(concealed)

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
    Check whether `counter` can be split into exactly `sets_needed` melds (triplets and/or runs),
    with nothing left over.
    """
    return _try_decompose(counter, sets_needed) is not None


def _try_decompose(
    counter: Counter,
    sets_needed: int,
    *,
    allow_triplets: bool = True,
    allow_sequences: bool = True,
) -> list[str] | None:
    """
    Recursively split `counter` into exactly `sets_needed` melds, returning the list of set types
    ('triplet' / 'sequence') on success, or None.

    `allow_triplets` and `allow_sequences` gate which meld types are legal. When both are True the
    search is triplet-first; when only one is True the search is strict - only that meld type is
    attempted.
    """
    if sets_needed == 0:
        return [] if not counter else None
    if not counter:
        return None

    tile = min(counter.keys(), key=lambda t: t.sort_key())

    # option 1: pong meld
    if allow_triplets and counter[tile] >= 3:
        counter[tile] -= 3
        if counter[tile] == 0:
            del counter[tile]

        result = _try_decompose(
            counter,
            sets_needed - 1,
            allow_triplets=allow_triplets,
            allow_sequences=allow_sequences,
        )
        if result is not None:
            counter[tile] = counter.get(tile, 0) + 3
            return ["triplet"] + result

        counter[tile] = counter.get(tile, 0) + 3

    # option 2: chi meld - suited tiles only, and only as the start of the run since `tile` is the
    # current smallest remaining.
    if allow_sequences and is_suit_tile(tile) and tile.number <= 7:
        t2, t3 = Suit(tile.type, tile.number + 1), Suit(tile.type, tile.number + 2)
        chi_meld = (tile, t2, t3)
        if counter.get(t2, 0) > 0 and counter.get(t3, 0) > 0:
            for t in chi_meld:
                counter[t] -= 1
                if counter[t] == 0:
                    del counter[t]

            result = _try_decompose(
                counter,
                sets_needed - 1,
                allow_triplets=allow_triplets,
                allow_sequences=allow_sequences,
            )
            if result is not None:
                for t in chi_meld:
                    counter[t] = counter.get(t, 0) + 1
                return ["sequence"] + result

            for t in chi_meld:
                counter[t] = counter.get(t, 0) + 1

    return None


def _classify_concealed_sets(
    concealed: list[Tile],
    sets_needed: int,
    *,
    allow_triplets: bool = True,
    allow_sequences: bool = True,
) -> list[str] | None:
    """
    Try every distinct tile as the hand's pair (eye), then decompose the remaining tiles into
    `sets_needed` melds of the allowed types.

    Returns:
        The list of set types ('triplet' / 'sequence') for the first successful decomposition, or
        None if no decomposition is possible.
    """
    counter = Counter(concealed)

    for tile in list(counter.keys()):
        if counter[tile] >= 2:
            counter[tile] -= 2
            if counter[tile] == 0:
                del counter[tile]

            result = _try_decompose(
                counter,
                sets_needed,
                allow_triplets=allow_triplets,
                allow_sequences=allow_sequences,
            )
            counter[tile] = counter.get(tile, 0) + 2

            if result is not None:
                return result

    return None


def _is_thirteen_wonders(tiles: list[Tile]) -> bool:
    """
    Thirteen Wonders:

    Exactly the 13 unique orphan tiles (1s/9s of each suit, all 4 Winds, all 3 Dragons) plus one
    duplicate of any one of them, fully concealed (14 tiles total).
    """
    if len(tiles) != 14:
        return False

    counter = Counter(tiles)
    return len(counter) == 13 and all(t in THIRTEEN_WONDERS for t in tiles)


def _is_three_great_scholars(hand_tile: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Three Great Scholars:

    At least 3 of each of the 3 Dragon tiles, combining concealed tiles and exposed melds. The rest
    of the hand does not need to form a valid set/pair structure once this condition is met.
    """
    dragon_tiles = [t for t in hand_tile if t in THREE_GREAT_SCHOLARS]
    dragon_tiles.extend(
        [tile for meld in open_tile for tile in meld.tiles if tile in THREE_GREAT_SCHOLARS]
    )
    counter = Counter(dragon_tiles)
    return len(counter) == 3 and all(c >= 3 for c in counter.values())


def _is_three_lesser_scholars(hand_tile: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Three Lesser Scholars:

    At least 2 of the 3 Dragon types appear 3 or more times, and the remaining Dragon type appears
    at least 2 times, across hand and open melds.
    """
    dragon_tiles = [t for t in hand_tile if t in THREE_GREAT_SCHOLARS]
    dragon_tiles.extend(
        [tile for meld in open_tile for tile in meld.tiles if tile in THREE_GREAT_SCHOLARS]
    )
    counter = Counter(dragon_tiles)
    if len(counter) != 3:
        return False

    counts = sorted(counter.values())
    return counts[0] >= 2 and counts[1] >= 3


def _is_four_great_blessings(hand_tile: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Four Great Blessings:

    At least 3 of each of the 4 Wind tiles, combining concealed tiles and exposed melds. The rest of
    the hand is immaterial once this condition is met - it doesn't even need to form a valid pair.
    """
    wind_tiles = [t for t in hand_tile if t in FOUR_GREAT_BLESSINGS]
    wind_tiles.extend(
        [tile for meld in open_tile for tile in meld.tiles if tile in FOUR_GREAT_BLESSINGS]
    )
    counter = Counter(wind_tiles)
    return len(counter) == 4 and all(c >= 3 for c in counter.values())


def _is_four_lesser_blessings(hand_tile: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Four Lesser Blessings:

    At least 3 of the 4 Wind types appear 3 or more times, and the remaining Wind type appears at
    least 2 times, across hand and open melds.
    """
    wind_tiles = [t for t in hand_tile if t in FOUR_GREAT_BLESSINGS]
    wind_tiles.extend(
        [tile for meld in open_tile for tile in meld.tiles if tile in FOUR_GREAT_BLESSINGS]
    )
    counter = Counter(wind_tiles)
    if len(counter) != 4:
        return False

    counts = sorted(counter.values())
    return counts[0] >= 2 and counts[1] >= 3


def _is_eighteen_arhats(open_tile: list[Meld]) -> bool:
    """
    Eighteen Arhats:

    Exactly 4 gangs (all open melds length 4).
    """
    return len(open_tile) == 4 and all(len(meld.tiles) == 4 for meld in open_tile)


def _is_nine_gates(hand_tile: list[Tile], tile: Tile) -> bool:
    """
    Nine Gates:

    The 13 concealed hand tiles must be exactly 1112345678999 of a single suit, and the winning tile
    must be from the same suit.
    """
    if not is_suit_tile(tile):
        return False
    if not hand_tile or not all(is_suit_tile(t) for t in hand_tile):
        return False

    suit = tile.type
    hand_suits = {t.type for t in hand_tile}
    if hand_suits != {suit}:
        return False

    counter: dict[int, int] = {}
    for t in hand_tile:
        counter[t.number] = counter.get(t.number, 0) + 1

    expected = {1: 3, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 3}
    return counter == expected


def _is_pure_green_suit(concealed: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Pure Green Suit:

    Every tile across hand and open melds must be one of the allowed tiles: Bamboo 2, 3, 4, 6, 8 or
    Fa Cai.
    """
    all_tiles = concealed + [t for meld in open_tile for t in meld.tiles]
    if not all_tiles:
        return False

    return all(t in PURE_GREEN_SUIT_TILES for t in all_tiles)


def _is_all_honour(concealed: list[Tile], open_tile: list[Meld]) -> bool:
    """
    All Honour:

    Every tile across hand and open melds must be a Wind or Dragon.
    """
    all_tiles = concealed + [t for meld in open_tile for t in meld.tiles]
    return all_tiles and all(is_honor_tile(t) for t in all_tiles)


def _is_pure_terminals(concealed: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Pure Terminals:

    All tiles must be suited tiles with number 1 or 9. No honor tiles.
    """
    all_tiles = concealed + [t for meld in open_tile for t in meld.tiles]
    if not all_tiles:
        return False

    return all(is_suit_tile(t) and t.number in (1, 9) for t in all_tiles)


def _is_mixed_terminals(concealed: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Mixed Terminals:

    All tiles must be either suited tiles with number 1 or 9, or honor tiles. Requires the hand to
    also be a TRIPLETS_HAND (enforced by the caller).
    """
    all_tiles = concealed + [t for meld in open_tile for t in meld.tiles]
    if not all_tiles:
        return False

    for t in all_tiles:
        if is_suit_tile(t):
            if t.number not in (1, 9):
                return False
        elif not is_honor_tile(t):
            return False

    return True


def _is_full_flush(concealed: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Full Flush:

    Every tile must be a suited tile and all must be from the same suit. No honor tiles allowed.
    """
    all_tiles = concealed + [t for meld in open_tile for t in meld.tiles]
    if not all_tiles:
        return False

    suit_types = {t.type for t in all_tiles if is_suit_tile(t)}
    has_honor = any(is_honor_tile(t) for t in all_tiles)
    return len(suit_types) == 1 and not has_honor


def _is_half_flush(concealed: list[Tile], open_tile: list[Meld]) -> bool:
    """
    Half Flush:

    All suited tiles must belong to exactly one suit, and at least one honor tile must be present.
    """
    all_tiles = concealed + [t for meld in open_tile for t in meld.tiles]
    suit_types = {t.type for t in all_tiles if is_suit_tile(t)}
    has_honor = any(is_honor_tile(t) for t in all_tiles)
    return len(suit_types) == 1 and has_honor


def _is_triplets_hand(concealed: list[Tile], sets_needed: int, open_tile: list[Meld]) -> bool:
    """
    Triplets Hand:

    All 4 sets must be triplets (pongs/gangs) - no sequences allowed.
    """
    if any(is_chi_meld(meld) for meld in open_tile):
        return False

    return _classify_concealed_sets(concealed, sets_needed, allow_sequences=False) is not None


def _has_exposed_meld(open_tile: list[Meld]) -> bool:
    """
    Return True if the player has any exposed meld (chi, pong, exposed gang, or pong-upgrade gang).
    A concealed gang formed from four hand tiles does not count as exposed.
    """
    return any(meld.is_exposed for meld in open_tile)


def _is_sequence_structure(
    concealed: list[Tile],
    sets_needed: int,
    seat_wind: WindType,
    prevalent_wind: WindType,
) -> bool:
    """
    Return True if concealed tiles can be decomposed into `sets_needed` sequences + 1 pair. The pair
    must not be a dragon, the seat wind, or the prevalent wind.
    """
    counter = Counter(concealed)

    for pair_tile in list(counter.keys()):
        if counter[pair_tile] < 2:
            continue
        if isinstance(pair_tile, Dragon):
            continue
        if isinstance(pair_tile, Wind) and pair_tile.type in (seat_wind, prevalent_wind):
            continue

        counter[pair_tile] -= 2
        if counter[pair_tile] == 0:
            del counter[pair_tile]

        result = _try_decompose(counter, sets_needed, allow_triplets=False)
        counter[pair_tile] = counter.get(pair_tile, 0) + 2

        if result is not None:
            return True

    return False
