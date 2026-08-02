from collections import Counter

from backend.domain.player import Player
from backend.domain.tiles import Dragon, Tile, Wind, WindType
from backend.engine.turn_result import WinEvent, WinSource
from backend.rules.hand_patterns import SPECIAL_HAND_PATTERNS, HandPattern
from backend.rules.hu_result import HuResult

POINT_LIMIT = 5

NON_SPECIAL_HAND_PATTERN_POINTS = {
    HandPattern.THREE_LESSER_SCHOLARS: 1,
    HandPattern.FOUR_LESSER_BLESSINGS: 2,
    HandPattern.MIXED_TERMINALS: 2,
    HandPattern.FULLY_CONCEALED: 1,
    HandPattern.SEQUENCE_HAND: 4,
    HandPattern.LESSER_SEQUENCE_HAND: 1,
    HandPattern.FULL_FLUSH: 4,
    HandPattern.HALF_FLUSH: 2,
    HandPattern.TRIPLETS_HAND: 2,
    HandPattern.CHICKEN_HAND: 0,
}

WIN_EVENT_BONUS_POINTS = {
    WinEvent.HEAVENLY: POINT_LIMIT,
    WinEvent.EARTHLY: POINT_LIMIT,
    WinEvent.HUMANLY: POINT_LIMIT,
    WinEvent.REPLACEMENT_TILE: 1,
    WinEvent.LAST_TILE: 1,
    WinEvent.ROBBING_GANG: 1,
}


def calculate_tai(
    hu_result: HuResult,
    win_source: WinSource,
    win_events: frozenset[WinEvent],
    player: Player,
    winning_tile: Tile,
    prevalent_wind: WindType,
    *,
    point_limit: int = POINT_LIMIT,
) -> int:
    """
    Calculate the tai earned by the winning player.

    Args:
        hu_result: The tile-level analysis result.
        win_source: The winning circumstance.
        win_events: The bonus-scoring game-context circumstances.
        player: The player that wins.
        winning_tile: The tile that completes the winning hand.
        prevalent_wind: The table's wind.
        point_limit: The game's point limit set.

    Returns:
        Total accumulated tai (capped at `point_limit`) or 0 if did not win.
    """
    if not hu_result.is_winning:
        return 0

    patterns = _include_composite_hand_patterns(hu_result.patterns, win_source)
    total = player.tai
    total += _concealed_hand_tai(
        player.hand_tile, win_source, winning_tile, player.seat_wind, prevalent_wind
    )
    total += _winning_hand_tai(patterns, point_limit)
    total += sum(WIN_EVENT_BONUS_POINTS.get(e, 0) for e in win_events)
    return min(total, point_limit)


# Private methods


def _include_composite_hand_patterns(
    hand_patterns: frozenset[HandPattern], win_source: WinSource
) -> frozenset[HandPattern]:
    """Add composite hand patterns to the existing set of hand patterns."""
    pattern = set(hand_patterns)
    if {
        HandPattern.TRIPLETS_HAND,
        HandPattern.FULLY_CONCEALED,
    } <= pattern and win_source == WinSource.SELF_PICK:
        pattern.add(HandPattern.HIDDEN_TREASURE)

    if {HandPattern.FULL_FLUSH, HandPattern.TRIPLETS_HAND} <= pattern:
        pattern.add(HandPattern.FULL_FLUSH_TRIPLETS_HAND)

    if {HandPattern.FULL_FLUSH, HandPattern.SEQUENCE_HAND} <= pattern:
        pattern.add(HandPattern.FULL_FLUSH_SEQUENCE_HAND)

    return frozenset(pattern)


def _concealed_hand_tai(
    hand_tiles: list[Tile],
    win_source: WinSource,
    winning_tile: Tile,
    seat_wind: WindType,
    prevalent_wind: WindType,
) -> int:
    """Return the tai that is hidden within `hand_tiles`, not counted by `Player.tai`."""
    tiles = list(hand_tiles)
    if win_source == WinSource.DISCARD:
        tiles.append(winning_tile)

    counter = Counter(tiles)
    tai = 0
    for tile, count in counter.items():
        if count >= 3:
            if isinstance(tile, Dragon):
                tai += 1
            elif isinstance(tile, Wind):
                if tile.type == seat_wind:
                    tai += 1
                if tile.type == prevalent_wind:
                    tai += 1

    return tai


def _winning_hand_tai(hand_pattern: frozenset[HandPattern], point_limit: int) -> int:
    """Return the total tai awarded for the hand patterns, capped at `point_limit`."""
    tai = 0
    for pattern in hand_pattern:
        if pattern in SPECIAL_HAND_PATTERNS:
            return point_limit

        tai += NON_SPECIAL_HAND_PATTERN_POINTS.get(pattern, 0)

    return min(tai, point_limit)
