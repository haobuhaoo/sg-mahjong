from collections import Counter

import pytest

from backend.domain.meld import Meld
from backend.domain.tiles import (
    Dragon,
    DragonType,
    Suit,
    SuitType,
    Wind,
    WindType,
)
from backend.rules.hu import (
    _can_decompose,
    _can_form_sets_and_pair,
    _classify_concealed_sets,
    _has_exposed_meld,
    _is_all_honour,
    _is_eighteen_arhats,
    _is_four_great_blessings,
    _is_four_lesser_blessings,
    _is_full_flush,
    _is_half_flush,
    _is_mixed_terminals,
    _is_nine_gates,
    _is_pure_green_suit,
    _is_pure_terminals,
    _is_sequence_structure,
    _is_three_great_scholars,
    _is_three_lesser_scholars,
    _is_thirteen_wonders,
    _is_triplets_hand,
    _try_decompose,
    can_hu,
)
from backend.rules.hu_result import HandPattern


def _s(n, count=1):
    return [Suit(SuitType.DOT, n) for _ in range(count)]


def _b(n, count=1):
    return [Suit(SuitType.BAMBOO, n) for _ in range(count)]


def _w(wind, count=1):
    return [Wind(wind) for _ in range(count)]


def _d(dragon, count=1):
    return [Dragon(dragon) for _ in range(count)]


def _m(tiles, is_exposed=True):
    return Meld(tiles=tiles, is_exposed=is_exposed)


def _can_hu(
    hand,
    open_tile,
    tile,
    *,
    seat_wind=WindType.DONG,
    prevalent_wind=WindType.DONG,
    bonus_count=0,
    **kwargs
):
    return can_hu(
        hand,
        open_tile,
        tile,
        seat_wind=seat_wind,
        prevalent_wind=prevalent_wind,
        bonus_count=bonus_count,
        **kwargs
    )


class TestCanHuStandardHand:
    def test_all_triplets_hand(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.CHICKEN_HAND in result.patterns
        assert HandPattern.FULLY_CONCEALED in result.patterns

    def test_all_sequences_hand(self):
        hand = _s(1) + _s(2, 2) + _s(3, 2) + _s(4, 2) + _s(5, 2) + _s(6) + _s(7) + _s(8) + _s(9)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED in result.patterns

    def test_mixed_triplets_and_sequences(self):
        hand = _s(1, 3) + _s(2) + _s(3) + _s(4) + _s(5, 3) + _s(7) + _s(8) + _s(9, 2)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True

    def test_incomplete_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is False

    def test_short_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 3)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 3))
        assert result.is_winning is False

    def test_hand_with_unsplittable_remainder_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is False

    def test_with_open_pong_reduces_sets_needed(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(5, 1)
        open_tile = [_m([Suit(SuitType.DOT, 4)] * 3)]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED not in result.patterns

    def test_with_open_chi_reduces_sets_needed(self):
        hand = _s(1, 3) + _s(2) + _s(3) + _s(4) + _s(5, 3) + _s(9)
        open_tile = [_m([Suit(SuitType.DOT, 6), Suit(SuitType.DOT, 7), Suit(SuitType.DOT, 8)])]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 9))
        assert result.is_winning is True

    def test_too_many_open_melds_returns_false(self):
        hand = _s(5, 2)
        open_tile = [_m([Suit(SuitType.DOT, 1)] * 3) for _ in range(5)]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is False

    def test_long_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 2)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is False

    def test_eighteen_arhats_pattern(self):
        hand = _s(5, 1)
        open_tile = [
            _m([Suit(SuitType.DOT, 1)] * 4),
            _m([Suit(SuitType.DOT, 2)] * 4),
            _m([Suit(SuitType.DOT, 3)] * 4),
            _m([Suit(SuitType.DOT, 4)] * 4),
        ]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.EIGHTEEN_ARHATS in result.patterns

    def test_eighteen_arhats_not_triggered_with_3_gangs(self):
        hand = _s(4, 3) + _s(5, 1)
        open_tile = [
            _m([Suit(SuitType.DOT, 1)] * 4),
            _m([Suit(SuitType.DOT, 2)] * 4),
            _m([Suit(SuitType.DOT, 3)] * 4),
        ]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.EIGHTEEN_ARHATS not in result.patterns

    def test_fully_concealed_with_concealed_gang(self):
        hand = _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        open_tile = [_m([Suit(SuitType.DOT, 1)] * 4, is_exposed=False)]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED in result.patterns

    def test_exposed_gang_disqualifies_fully_concealed(self):
        hand = _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        open_tile = [_m([Suit(SuitType.DOT, 1)] * 4)]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED not in result.patterns


class TestCanFormSetsAndPair:
    def test_decomposes_all_triplets(self):
        tiles = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 2)
        assert _can_form_sets_and_pair(tiles, 4) is True

    def test_decomposes_all_sequences(self):
        tiles = _s(1) + _s(2, 2) + _s(3, 3) + _s(4, 3) + _s(5, 2) + _s(6) + _s(7, 2)
        assert _can_form_sets_and_pair(tiles, 4) is True

    def test_decomposes_mixed(self):
        tiles = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4) + _s(5) + _s(6) + _s(7, 2)
        assert _can_form_sets_and_pair(tiles, 4) is True

    def test_fails_with_unsplittable_tiles(self):
        tiles = _s(1, 2) + _s(3, 2) + _s(5, 2) + _s(7, 2) + _s(9, 2) + _s(2, 2) + _s(4, 2)
        assert _can_form_sets_and_pair(tiles, 4) is False

    def test_fails_with_odd_count(self):
        tiles = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5)
        assert _can_form_sets_and_pair(tiles, 4) is False

    def test_honor_tiles_only_triplets(self):
        tiles = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _d(DragonType.ZHONG, 3)
            + _w(WindType.BEI, 2)
        )
        assert _can_form_sets_and_pair(tiles, 4) is True

    def test_honor_tiles_cannot_form_sequences(self):
        tiles = (
            _w(WindType.DONG)
            + _w(WindType.NAN)
            + _w(WindType.XI)
            + _w(WindType.BEI, 3)
            + _d(DragonType.ZHONG, 3)
            + _d(DragonType.FA, 3)
            + _d(DragonType.BAI, 2)
        )
        assert _can_form_sets_and_pair(tiles, 4) is False


class TestCanDecompose:
    def test_empty_counter_with_zero_sets(self):
        assert _can_decompose(Counter(), 0) is True

    def test_empty_counter_with_sets_needed(self):
        assert _can_decompose(Counter(), 1) is False

    def test_zero_sets_with_remaining_tiles(self):
        assert _can_decompose(Counter(_s(1, 2)), 0) is False

    def test_decompose_triplet_only(self):
        assert _can_decompose(Counter(_s(1, 3)), 1) is True

    def test_decompose_sequence_only(self):
        assert _can_decompose(Counter(_s(1) + _s(2) + _s(3)), 1) is True

    def test_decompose_consecutive_sequences(self):
        c = Counter(_s(1) + _s(2) + _s(3) + _s(4) + _s(5) + _s(6))
        assert _can_decompose(c, 2) is True

    def test_cannot_decompose_pair(self):
        assert _can_decompose(Counter(_s(1, 2)), 1) is False

    def test_single_tile_fails(self):
        assert _can_decompose(Counter(_s(1)), 1) is False


class TestIsThirteenWonders:
    def test_valid_thirteen_wonders(self):
        tiles = []
        for suit in SuitType:
            tiles.append(Suit(suit, 1))
            tiles.append(Suit(suit, 9))
        for wind in WindType:
            tiles.append(Wind(wind))
        for dragon in DragonType:
            tiles.append(Dragon(dragon))
        tiles.append(Dragon(DragonType.ZHONG))
        assert _is_thirteen_wonders(tiles) is True

    def test_wrong_count_returns_false(self):
        tiles = [
            Suit(SuitType.DOT, 1),
            Suit(SuitType.DOT, 9),
        ]
        assert _is_thirteen_wonders(tiles) is False

    def test_missing_orphan_returns_false(self):
        tiles = []
        for suit in SuitType:
            tiles.append(Suit(suit, 1))
            tiles.append(Suit(suit, 9))
        for wind in WindType:
            tiles.append(Wind(wind))
        for dragon in DragonType:
            tiles.append(Dragon(dragon))
        tiles.append(Suit(SuitType.DOT, 2))
        assert _is_thirteen_wonders(tiles) is False

    def test_extra_tile_not_an_orphan(self):
        tiles = []
        for suit in SuitType:
            tiles.append(Suit(suit, 1))
            tiles.append(Suit(suit, 9))
        for wind in WindType:
            tiles.append(Wind(wind))
        for dragon in DragonType:
            tiles.append(Dragon(dragon))
        tiles.append(Suit(SuitType.DOT, 5))
        assert _is_thirteen_wonders(tiles) is False

    def test_all_unique_orphans_no_duplicate(self):
        tiles = []
        for suit in SuitType:
            tiles.append(Suit(suit, 1))
            tiles.append(Suit(suit, 9))
        for wind in WindType:
            tiles.append(Wind(wind))
        for dragon in DragonType:
            tiles.append(Dragon(dragon))
        assert _is_thirteen_wonders(tiles) is False


class TestIsThreeGreatScholars:
    def test_valid_all_concealed(self):
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 3) + _d(DragonType.BAI, 3)
        assert _is_three_great_scholars(hand, []) is True

    def test_valid_with_open_melds(self):
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 3)
        open_tile = [_m([Dragon(DragonType.BAI)] * 3)]
        assert _is_three_great_scholars(hand, open_tile) is True

    def test_extra_non_dragon_tiles_still_valid(self):
        hand = (
            _d(DragonType.ZHONG, 3)
            + _d(DragonType.FA, 3)
            + _d(DragonType.BAI, 3)
            + _s(1, 3)
            + _s(2)
        )
        assert _is_three_great_scholars(hand, []) is True

    def test_only_two_of_each_returns_false(self):
        hand = _d(DragonType.ZHONG, 2) + _d(DragonType.FA, 2) + _d(DragonType.BAI, 2)
        assert _is_three_great_scholars(hand, []) is False

    def test_missing_one_dragon_returns_false(self):
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 3)
        assert _is_three_great_scholars(hand, []) is False

    def test_empty_hand_returns_false(self):
        assert _is_three_great_scholars([], []) is False


class TestIsFourGreatBlessings:
    def test_valid_all_concealed(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _w(WindType.XI, 3) + _w(WindType.BEI, 3)
        assert _is_four_great_blessings(hand, []) is True

    def test_valid_with_open_melds(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _w(WindType.XI, 3)
        open_tile = [_m([Wind(WindType.BEI)] * 3)]
        assert _is_four_great_blessings(hand, open_tile) is True

    def test_extra_non_wind_tiles_still_valid(self):
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 3)
            + _s(1, 2)
        )
        assert _is_four_great_blessings(hand, []) is True

    def test_only_three_winds_returns_false(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _w(WindType.XI, 3)
        assert _is_four_great_blessings(hand, []) is False

    def test_only_two_of_each_returns_false(self):
        hand = _w(WindType.DONG, 2) + _w(WindType.NAN, 2) + _w(WindType.XI, 2) + _w(WindType.BEI, 2)
        assert _is_four_great_blessings(hand, []) is False

    def test_empty_hand_returns_false(self):
        assert _is_four_great_blessings([], []) is False


class TestCanHuSpecialHands:
    def test_thirteen_wonders_via_can_hu(self):
        hand = []
        for suit in SuitType:
            hand.append(Suit(suit, 1))
            hand.append(Suit(suit, 9))
        for wind in WindType:
            hand.append(Wind(wind))
        for dragon in DragonType:
            hand.append(Dragon(dragon))
        hand.append(Dragon(DragonType.ZHONG))
        for i in range(len(hand)):
            tile = hand[i]
            remaining = hand[:i] + hand[i + 1 :]
            if _can_hu(remaining, [], tile).is_winning:
                return
        pytest.fail("Thirteen Wonders should return True via can_hu")

    def test_three_great_scholars_via_can_hu(self):
        hand = (
            _d(DragonType.ZHONG, 3)
            + _d(DragonType.FA, 3)
            + _d(DragonType.BAI, 3)
            + _s(1, 3)
            + _s(2)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 2))
        assert result.is_winning is True
        assert HandPattern.THREE_GREAT_SCHOLARS in result.patterns

    def test_four_great_blessings_via_can_hu(self):
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 3)
            + _s(1, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 1))
        assert result.is_winning is True
        assert HandPattern.FOUR_GREAT_BLESSINGS in result.patterns

    def test_thirteen_wonders_rejected_with_open_melds(self):
        hand = []
        for suit in SuitType:
            hand.append(Suit(suit, 1))
            hand.append(Suit(suit, 9))
        for wind in WindType:
            hand.append(Wind(wind))
        for dragon in DragonType:
            hand.append(Dragon(dragon))
        hand.append(Dragon(DragonType.ZHONG))
        for i in range(len(hand)):
            tile = hand[i]
            remaining = hand[:i] + hand[i + 1 :]
            if _can_hu(remaining, [_m([Suit(SuitType.DOT, 1)] * 3)], tile).is_winning:
                pytest.fail("Thirteen Wonders with open melds should return False")


class TestTripletsHand:
    def test_all_triplets_concealed(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.TRIPLETS_HAND in result.patterns

    def test_mixed_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 1) + _s(3, 1) + _s(4, 1) + _s(5, 3) + _s(7, 1) + _s(8, 1) + _s(9, 2)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True
        assert HandPattern.TRIPLETS_HAND not in result.patterns

    def test_with_open_pong(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(5, 1)
        open_tile = [_m([Suit(SuitType.DOT, 4)] * 3)]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.TRIPLETS_HAND in result.patterns

    def test_open_chi_disqualifies(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(5, 1)
        open_tile = [_m([Suit(SuitType.DOT, 6), Suit(SuitType.DOT, 7), Suit(SuitType.DOT, 8)])]
        result = _can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.TRIPLETS_HAND not in result.patterns


class TestHalfFlush:
    def test_same_suit_with_honors(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _w(WindType.DONG, 1)
        result = _can_hu(hand, [], Wind(WindType.DONG))
        assert result.is_winning is True
        assert HandPattern.HALF_FLUSH in result.patterns

    def test_no_honors_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.HALF_FLUSH not in result.patterns

    def test_multiple_suits_returns_false(self):
        hand = (
            _s(1, 3)
            + _s(2, 3)
            + _s(3, 3)
            + [Suit(SuitType.CHARACTER, 1)] * 3
            + _w(WindType.DONG, 1)
        )
        result = _can_hu(hand, [], Wind(WindType.DONG))
        assert result.is_winning is True
        assert HandPattern.HALF_FLUSH not in result.patterns

    def test_with_open_melds(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _w(WindType.DONG, 1)
        open_tile = [_m([Dragon(DragonType.ZHONG)] * 3)]
        result = _can_hu(hand, open_tile, Wind(WindType.DONG))
        assert result.is_winning is True
        assert HandPattern.HALF_FLUSH in result.patterns


class TestFullFlush:
    def test_all_same_suit_only(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULL_FLUSH in result.patterns

    def test_with_honors_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _w(WindType.DONG, 1)
        result = _can_hu(hand, [], Wind(WindType.DONG))
        assert result.is_winning is True
        assert HandPattern.FULL_FLUSH not in result.patterns

    def test_multiple_suits_returns_false(self):
        hand = (
            _s(1, 3)
            + _s(2, 3)
            + [Suit(SuitType.CHARACTER, 1)] * 3
            + [Suit(SuitType.CHARACTER, 2)] * 3
            + _s(5, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULL_FLUSH not in result.patterns


class TestAllHonour:
    def test_all_winds_and_dragons(self):
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _d(DragonType.ZHONG, 3)
            + _w(WindType.BEI, 1)
        )
        result = _can_hu(hand, [], Wind(WindType.BEI))
        assert result.is_winning is True
        assert HandPattern.ALL_HONOUR in result.patterns

    def test_with_suit_tile_returns_false(self):
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _s(1, 3)
            + _w(WindType.BEI, 1)
        )
        result = _can_hu(hand, [], Wind(WindType.BEI))
        assert result.is_winning is True
        assert HandPattern.ALL_HONOUR not in result.patterns


class TestMixedTerminals:
    def test_ones_nines_and_honors_with_triplets(self):
        hand = (
            _s(1, 3)
            + [Suit(SuitType.CHARACTER, 9)] * 3
            + _w(WindType.DONG, 3)
            + _d(DragonType.ZHONG, 3)
            + _s(9, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True
        assert HandPattern.MIXED_TERMINALS in result.patterns

    def test_with_non_terminal_suit_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _d(DragonType.ZHONG, 3) + _s(9, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True
        assert HandPattern.MIXED_TERMINALS not in result.patterns

    def test_requires_triplets_hand(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + [Suit(SuitType.CHARACTER, 9)] * 3
            + [Suit(SuitType.DOT, 1)] * 3
            + _d(DragonType.ZHONG, 1)
        )
        result = _can_hu(hand, [], Dragon(DragonType.ZHONG))
        assert result.is_winning is True
        assert HandPattern.MIXED_TERMINALS not in result.patterns


class TestPureTerminals:
    def test_only_ones_and_nines(self):
        hand = (
            _s(1, 3)
            + [Suit(SuitType.CHARACTER, 9)] * 3
            + [Suit(SuitType.CHARACTER, 1)] * 3
            + [Suit(SuitType.BAMBOO, 9)] * 3
            + _s(9, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True
        assert HandPattern.PURE_TERMINALS in result.patterns

    def test_with_non_terminal_returns_false(self):
        hand = (
            _s(1, 3)
            + _s(2, 3)
            + [Suit(SuitType.CHARACTER, 9)] * 3
            + [Suit(SuitType.BAMBOO, 1)] * 3
            + [Suit(SuitType.DOT, 9)] * 1
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True
        assert HandPattern.PURE_TERMINALS not in result.patterns

    def test_with_honors_returns_false(self):
        hand = (
            _s(1, 3)
            + [Suit(SuitType.CHARACTER, 9)] * 3
            + [Suit(SuitType.BAMBOO, 1)] * 3
            + _s(9, 3)
            + _w(WindType.DONG, 1)
        )
        result = _can_hu(hand, [], Wind(WindType.DONG))
        assert result.is_winning is True
        assert HandPattern.PURE_TERMINALS not in result.patterns


class TestSequenceHand:
    def test_four_sequences_with_valid_pair(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(4, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 4))
        assert result.is_winning is True
        assert HandPattern.SEQUENCE_HAND in result.patterns

    def test_dragon_pair_disqualifies(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _d(DragonType.ZHONG, 1)
        )
        result = _can_hu(hand, [], Dragon(DragonType.ZHONG))
        assert result.is_winning is True
        assert HandPattern.SEQUENCE_HAND not in result.patterns

    def test_seat_wind_pair_disqualifies(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _w(WindType.DONG, 1)
        )
        result = _can_hu(hand, [], Wind(WindType.DONG), seat_wind=WindType.DONG)
        assert result.is_winning is True
        assert HandPattern.SEQUENCE_HAND not in result.patterns

    def test_bonus_tiles_disqualifies(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(4, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 4), bonus_count=1)
        assert result.is_winning is True
        assert HandPattern.SEQUENCE_HAND not in result.patterns


class TestThreeLesserScholars:
    def test_two_dragon_pongs_one_dragon_pair(self):
        hand = (
            _d(DragonType.ZHONG, 3)
            + _d(DragonType.FA, 3)
            + _d(DragonType.BAI, 2)
            + _s(1, 3)
            + _s(2, 2)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 2))
        assert result.is_winning is True
        assert HandPattern.THREE_LESSER_SCHOLARS in result.patterns
        assert HandPattern.THREE_GREAT_SCHOLARS not in result.patterns

    def test_with_three_great_scholars(self):
        hand = (
            _d(DragonType.ZHONG, 3)
            + _d(DragonType.FA, 3)
            + _d(DragonType.BAI, 3)
            + _s(1, 1)
            + _s(2, 3)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 1))
        assert result.is_winning is True
        assert HandPattern.THREE_LESSER_SCHOLARS in result.patterns
        assert HandPattern.THREE_GREAT_SCHOLARS in result.patterns

    def test_only_one_pong_returns_false(self):
        hand = _d(DragonType.ZHONG, 3) + _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 4))
        assert result.is_winning is True
        assert HandPattern.THREE_LESSER_SCHOLARS not in result.patterns


class TestFourLesserBlessings:
    def test_three_wind_pongs_one_wind_pair(self):
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 1)
            + _s(1, 3)
        )
        result = _can_hu(hand, [], Wind(WindType.BEI))
        assert result.is_winning is True
        assert HandPattern.FOUR_LESSER_BLESSINGS in result.patterns
        assert HandPattern.FOUR_GREAT_BLESSINGS not in result.patterns

    def test_with_four_great_blessings(self):
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 3)
            + _s(1, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 1))
        assert result.is_winning is True
        assert HandPattern.FOUR_LESSER_BLESSINGS in result.patterns
        assert HandPattern.FOUR_GREAT_BLESSINGS in result.patterns

    def test_only_two_pongs_returns_false(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _s(1, 3) + _s(2, 3) + _s(3, 1)
        result = _can_hu(hand, [], Suit(SuitType.DOT, 3))
        assert result.is_winning is True
        assert HandPattern.FOUR_LESSER_BLESSINGS not in result.patterns


class TestHasExposedMeld:
    def test_empty_returns_false(self):
        assert _has_exposed_meld([]) is False

    def test_exposed_pong_returns_true(self):
        meld = _m([Suit(SuitType.DOT, 1)] * 3)
        assert _has_exposed_meld([meld]) is True

    def test_concealed_gang_returns_false(self):
        meld = _m([Suit(SuitType.DOT, 1)] * 4, is_exposed=False)
        assert _has_exposed_meld([meld]) is False

    def test_exposed_gang_returns_true(self):
        meld = _m([Suit(SuitType.DOT, 1)] * 4, is_exposed=True)
        assert _has_exposed_meld([meld]) is True


class TestTryDecompose:
    def test_returns_list_of_set_types(self):
        result = _try_decompose(Counter(_s(1, 3) + _s(2) + _s(3) + _s(4)), 2)
        assert result == ["triplet", "sequence"]

    def test_allow_triplets_only_on_mixed_hand_returns_none(self):
        result = _try_decompose(Counter(_s(1, 3) + _s(2) + _s(3) + _s(4)), 2, allow_sequences=False)
        assert result is None

    def test_allow_sequences_only_on_all_triplet_hand_returns_none(self):
        result = _try_decompose(Counter(_s(1, 3) + _s(2, 3)), 2, allow_triplets=False)
        assert result is None

    def test_allow_sequences_only_on_mixed_hand_returns_sequences(self):
        result = _try_decompose(
            Counter(_s(1) + _s(2) + _s(3) + _s(1) + _s(2) + _s(3)),
            2,
            allow_triplets=False,
        )
        assert result == ["sequence", "sequence"]


class TestClassifyConcealedSets:
    def test_all_triplets(self):
        concealed = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 2)
        result = _classify_concealed_sets(concealed, 4, allow_sequences=False)
        assert result == ["triplet", "triplet", "triplet", "triplet"]

    def test_all_sequences(self):
        concealed = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(4, 2)
        )
        result = _classify_concealed_sets(concealed, 4, allow_triplets=False)
        assert result == ["sequence", "sequence", "sequence", "sequence"]

    def test_returns_none_when_impossible(self):
        concealed = _s(1, 2) + _s(3, 2) + _s(5, 2) + _s(7, 2) + _s(9, 2) + _s(2, 2) + _s(4, 2)
        result = _classify_concealed_sets(concealed, 4, allow_triplets=False)
        assert result is None


class TestIsSequenceStructure:
    def test_sequence_structure_true(self):
        concealed = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(4, 2)
        )
        assert _is_sequence_structure(concealed, 4, WindType.DONG, WindType.DONG) is True

    def test_prevalent_wind_pair_disqualifies(self):
        concealed = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _w(WindType.DONG, 2)
        )
        assert _is_sequence_structure(concealed, 4, WindType.NAN, WindType.DONG) is False


class TestIsThreeLesserScholars:
    def test_true_with_two_pongs_one_pair(self):
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 3) + _d(DragonType.BAI, 2)
        assert _is_three_lesser_scholars(hand, []) is True

    def test_false_with_only_one_pong(self):
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 2) + _d(DragonType.BAI, 1)
        assert _is_three_lesser_scholars(hand, []) is False


class TestIsFourLesserBlessings:
    def test_true_with_three_pongs_one_pair(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _w(WindType.XI, 3) + _w(WindType.BEI, 2)
        assert _is_four_lesser_blessings(hand, []) is True

    def test_false_with_only_two_pongs(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _w(WindType.XI, 2) + _w(WindType.BEI, 1)
        assert _is_four_lesser_blessings(hand, []) is False


class TestIsAllHonour:
    def test_true(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _d(DragonType.ZHONG, 2)
        assert _is_all_honour(hand, []) is True

    def test_false_with_suit_tile(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _s(1, 2)
        assert _is_all_honour(hand, []) is False

    def test_true_with_open_melds(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 2)
        open_tile = [_m([Dragon(DragonType.ZHONG)] * 3)]
        assert _is_all_honour(hand, open_tile) is True


class TestIsEighteenArhats:
    def test_true(self):
        open_tile = [
            _m([Suit(SuitType.DOT, 1)] * 4),
            _m([Suit(SuitType.DOT, 2)] * 4),
            _m([Suit(SuitType.DOT, 3)] * 4),
            _m([Suit(SuitType.DOT, 4)] * 4),
        ]
        assert _is_eighteen_arhats(open_tile) is True

    def test_false_with_three_gangs(self):
        open_tile = [
            _m([Suit(SuitType.DOT, 1)] * 4),
            _m([Suit(SuitType.DOT, 2)] * 4),
            _m([Suit(SuitType.DOT, 3)] * 4),
        ]
        assert _is_eighteen_arhats(open_tile) is False


class TestIsFullFlush:
    def test_true(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 2)
        assert _is_full_flush(hand, []) is True

    def test_false_with_multiple_suits(self):
        hand = _s(1, 3) + [Suit(SuitType.CHARACTER, 1)] * 3 + _s(2, 2)
        assert _is_full_flush(hand, []) is False

    def test_false_with_honors(self):
        hand = _s(1, 3) + _s(2, 3) + _w(WindType.DONG, 2)
        assert _is_full_flush(hand, []) is False


class TestIsHalfFlush:
    def test_true(self):
        hand = _s(1, 3) + _s(2, 3) + _w(WindType.DONG, 2)
        assert _is_half_flush(hand, []) is True

    def test_false_with_no_honors(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 2)
        assert _is_half_flush(hand, []) is False

    def test_false_with_multiple_suits(self):
        hand = _s(1, 3) + [Suit(SuitType.CHARACTER, 1)] * 3 + _w(WindType.DONG, 2)
        assert _is_half_flush(hand, []) is False


class TestIsMixedTerminals:
    def test_true(self):
        hand = _s(1, 3) + _s(9, 3) + _w(WindType.DONG, 2)
        assert _is_mixed_terminals(hand, []) is True

    def test_false_with_non_terminal(self):
        hand = _s(1, 3) + _s(2, 3) + _s(9, 2)
        assert _is_mixed_terminals(hand, []) is False


class TestIsPureTerminals:
    def test_true(self):
        hand = _s(1, 3) + _s(9, 3) + [Suit(SuitType.CHARACTER, 1)] * 2
        assert _is_pure_terminals(hand, []) is True

    def test_false_with_honors(self):
        hand = _s(1, 3) + _s(9, 3) + _w(WindType.DONG, 2)
        assert _is_pure_terminals(hand, []) is False

    def test_false_with_non_terminal(self):
        hand = _s(1, 3) + _s(2, 3) + _s(9, 2)
        assert _is_pure_terminals(hand, []) is False


class TestIsTripletsHand:
    def test_true(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 2)
        assert _is_triplets_hand(hand, 4, []) is True

    def test_false_with_chi_in_open(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 2)
        open_tile = [_m([Suit(SuitType.DOT, 6), Suit(SuitType.DOT, 7), Suit(SuitType.DOT, 8)])]
        assert _is_triplets_hand(hand, 3, open_tile) is False

    def test_false_with_sequence_in_concealed(self):
        hand = (
            _s(1, 3)
            + _s(2, 3)
            + _s(3, 1)
            + _s(4, 1)
            + _s(5, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(6, 2)
        )
        assert _is_triplets_hand(hand, 4, []) is False


class TestIsNineGates:
    def test_valid_bamboo_nine_gates(self):
        hand = (
            _b(1, 3)
            + _b(2, 1)
            + _b(3, 1)
            + _b(4, 1)
            + _b(5, 1)
            + _b(6, 1)
            + _b(7, 1)
            + _b(8, 1)
            + _b(9, 3)
        )
        result = _can_hu(hand, [], Suit(SuitType.BAMBOO, 5))
        assert result.is_winning is True
        assert HandPattern.NINE_GATES in result.patterns

    def test_valid_character_nine_gates(self):
        hand = (
            [Suit(SuitType.CHARACTER, 1)] * 3
            + [Suit(SuitType.CHARACTER, n) for n in range(2, 9)]
            + [Suit(SuitType.CHARACTER, 9)] * 3
        )
        result = _can_hu(hand, [], Suit(SuitType.CHARACTER, 5))
        assert result.is_winning is True
        assert HandPattern.NINE_GATES in result.patterns

    def test_rejected_with_open_meld(self):
        hand = _b(1, 3) + _b(2, 3) + _b(3, 3) + _b(4, 1)
        open_tile = [_m([Suit(SuitType.BAMBOO, 5)] * 3)]
        result = _can_hu(hand, open_tile, Suit(SuitType.BAMBOO, 4))
        assert result.is_winning is True
        assert HandPattern.NINE_GATES not in result.patterns

    def test_wrong_counts_returns_false(self):
        hand = (
            _b(1, 3)
            + _b(2, 1)
            + _b(3, 1)
            + _b(4, 1)
            + _b(5, 1)
            + _b(6, 1)
            + _b(7, 1)
            + _b(8, 1)
            + _b(9, 2)
            + _b(5, 1)
        )
        assert _is_nine_gates(hand, Suit(SuitType.BAMBOO, 5)) is False

    def test_wrong_suit_tile_returns_false(self):
        hand = (
            _b(1, 3)
            + _b(2, 1)
            + _b(3, 1)
            + _b(4, 1)
            + _b(5, 1)
            + _b(6, 1)
            + _b(7, 1)
            + _b(8, 1)
            + _b(9, 3)
        )
        assert _is_nine_gates(hand, Suit(SuitType.DOT, 5)) is False

    def test_missing_number_returns_false(self):
        hand = _b(1, 3) + _b(2, 1) + _b(3, 1) + _b(4, 1) + _b(5, 1) + _b(7, 1) + _b(8, 1) + _b(9, 4)
        assert _is_nine_gates(hand, Suit(SuitType.BAMBOO, 9)) is False

    def test_honor_tile_returns_false(self):
        hand = (
            _b(1, 3)
            + _b(2, 1)
            + _b(3, 1)
            + _b(4, 1)
            + _b(5, 1)
            + _b(6, 1)
            + _b(7, 1)
            + _b(8, 1)
            + _b(9, 3)
        )
        assert _is_nine_gates(hand, Dragon(DragonType.ZHONG)) is False


class TestIsPureGreenSuit:
    def test_all_bamboo_green(self):
        hand = _b(2, 3) + _b(3, 3) + _b(4, 3) + _b(6, 3) + _b(8, 1)
        result = _can_hu(hand, [], Suit(SuitType.BAMBOO, 8))
        assert result.is_winning is True
        assert HandPattern.PURE_GREEN_SUIT in result.patterns

    def test_with_green_dragon(self):
        hand = _b(2, 3) + _b(3, 3) + _b(4, 3) + _d(DragonType.FA, 3) + _b(6, 1)
        result = _can_hu(hand, [], Suit(SuitType.BAMBOO, 6))
        assert result.is_winning is True
        assert HandPattern.PURE_GREEN_SUIT in result.patterns

    def test_disallowed_bamboo_returns_false(self):
        hand = _b(2, 3) + _b(3, 3) + _b(5, 3) + _b(6, 3) + _b(8, 1)
        result = _can_hu(hand, [], Suit(SuitType.BAMBOO, 8))
        assert result.is_winning is True
        assert HandPattern.PURE_GREEN_SUIT not in result.patterns

    def test_with_open_melds(self):
        hand = _b(2, 3) + _b(3, 3) + _b(4, 3) + _b(8, 1)
        open_tile = [_m([Suit(SuitType.BAMBOO, 6)] * 3)]
        result = _can_hu(hand, open_tile, Suit(SuitType.BAMBOO, 8))
        assert result.is_winning is True
        assert HandPattern.PURE_GREEN_SUIT in result.patterns

    def test_unit_function_true(self):
        hand = _b(2, 3) + _b(3, 3) + _b(4, 3) + _b(6, 3) + _b(8, 2)
        assert _is_pure_green_suit(hand, []) is True

    def test_unit_function_false(self):
        hand = _b(2, 3) + _b(3, 3) + _b(5, 3) + _b(6, 3) + _b(8, 2)
        assert _is_pure_green_suit(hand, []) is False

    def test_unit_function_empty_returns_false(self):
        assert _is_pure_green_suit([], []) is False


class TestLesserSequenceHand:
    def test_sequence_structure_with_bonus(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(4, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 4), bonus_count=1)
        assert result.is_winning is True
        assert HandPattern.LESSER_SEQUENCE_HAND in result.patterns
        assert HandPattern.SEQUENCE_HAND not in result.patterns

    def test_zero_bonus_does_not_trigger_lesser(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _s(4, 1)
        )
        result = _can_hu(hand, [], Suit(SuitType.DOT, 4), bonus_count=0)
        assert result.is_winning is True
        assert HandPattern.SEQUENCE_HAND in result.patterns
        assert HandPattern.LESSER_SEQUENCE_HAND not in result.patterns

    def test_dragon_pair_disqualifies_lesser(self):
        hand = (
            _s(1, 2)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 1)
            + _s(5, 1)
            + _s(6, 1)
            + _s(7, 1)
            + _s(8, 1)
            + _s(9, 1)
            + _d(DragonType.ZHONG, 1)
        )
        result = _can_hu(hand, [], Dragon(DragonType.ZHONG), bonus_count=1)
        assert result.is_winning is True
        assert HandPattern.LESSER_SEQUENCE_HAND not in result.patterns
