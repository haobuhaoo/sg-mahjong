from collections import Counter

import pytest

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
    _is_four_great_blessings,
    _is_three_great_scholars,
    _is_thirteen_wonders,
    can_hu,
)
from backend.rules.hu_result import HandPattern
from backend.rules.hand_patterns import FOUR_GREAT_BLESSINGS, THREE_GREAT_SCHOLARS


def _s(n, count=1):
    return [Suit(SuitType.DOT, n) for _ in range(count)]


def _w(wind, count=1):
    return [Wind(wind) for _ in range(count)]


def _d(dragon, count=1):
    return [Dragon(dragon) for _ in range(count)]


class TestCanHuStandardHand:
    def test_all_triplets_hand(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.CHICKEN_HAND in result.patterns
        assert HandPattern.FULLY_CONCEALED in result.patterns

    def test_all_sequences_hand(self):
        hand = (
            _s(1)
            + _s(2, 2)
            + _s(3, 2)
            + _s(4, 2)
            + _s(5, 2)
            + _s(6)
            + _s(7)
            + _s(8)
            + _s(9)
        )
        result = can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED in result.patterns

    def test_mixed_triplets_and_sequences(self):
        hand = _s(1, 3) + _s(2) + _s(3) + _s(4) + _s(5, 3) + _s(7) + _s(8) + _s(9, 2)
        result = can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is True

    def test_incomplete_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3)
        result = can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is False

    def test_short_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 3)
        result = can_hu(hand, [], Suit(SuitType.DOT, 3))
        assert result.is_winning is False

    def test_hand_with_unsplittable_remainder_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        result = can_hu(hand, [], Suit(SuitType.DOT, 9))
        assert result.is_winning is False

    def test_with_open_pong_reduces_sets_needed(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(5, 1)
        open_tile = [[Suit(SuitType.DOT, 4)] * 3]
        result = can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED not in result.patterns

    def test_with_open_chi_reduces_sets_needed(self):
        hand = _s(1, 3) + _s(2) + _s(3) + _s(4) + _s(5, 3) + _s(9)
        open_tile = [
            [Suit(SuitType.DOT, 6), Suit(SuitType.DOT, 7), Suit(SuitType.DOT, 8)]
        ]
        result = can_hu(hand, open_tile, Suit(SuitType.DOT, 9))
        assert result.is_winning is True

    def test_too_many_open_melds_returns_false(self):
        hand = _s(5, 2)
        open_tile = [[Suit(SuitType.DOT, 1)] * 3] * 5
        result = can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is False

    def test_long_hand_returns_false(self):
        hand = _s(1, 3) + _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 2)
        result = can_hu(hand, [], Suit(SuitType.DOT, 5))
        assert result.is_winning is False

    def test_eighteen_arhats_pattern(self):
        hand = _s(5, 1)
        open_tile = [
            [Suit(SuitType.DOT, 1)] * 4,
            [Suit(SuitType.DOT, 2)] * 4,
            [Suit(SuitType.DOT, 3)] * 4,
            [Suit(SuitType.DOT, 4)] * 4,
        ]
        result = can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.EIGHTEEN_ARHATS in result.patterns

    def test_eighteen_arhats_not_triggered_with_3_gangs(self):
        hand = _s(4, 3) + _s(5, 1)
        open_tile = [
            [Suit(SuitType.DOT, 1)] * 4,
            [Suit(SuitType.DOT, 2)] * 4,
            [Suit(SuitType.DOT, 3)] * 4,
        ]
        result = can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.EIGHTEEN_ARHATS not in result.patterns

    def test_fully_concealed_with_concealed_gang(self):
        hand = _s(2, 3) + _s(3, 3) + _s(4, 3) + _s(5, 1)
        open_tile = [[Suit(SuitType.DOT, 1)] * 4]
        result = can_hu(hand, open_tile, Suit(SuitType.DOT, 5))
        assert result.is_winning is True
        assert HandPattern.FULLY_CONCEALED in result.patterns


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
        tiles = (
            _s(1, 2) + _s(3, 2) + _s(5, 2) + _s(7, 2) + _s(9, 2) + _s(2, 2) + _s(4, 2)
        )
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
        open_tile = [[Dragon(DragonType.BAI)] * 3]
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
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 3)
        )
        assert _is_four_great_blessings(hand, []) is True

    def test_valid_with_open_melds(self):
        hand = _w(WindType.DONG, 3) + _w(WindType.NAN, 3) + _w(WindType.XI, 3)
        open_tile = [[Wind(WindType.BEI)] * 3]
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
        hand = (
            _w(WindType.DONG, 2)
            + _w(WindType.NAN, 2)
            + _w(WindType.XI, 2)
            + _w(WindType.BEI, 2)
        )
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
            if can_hu(remaining, [], tile).is_winning:
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
        result = can_hu(hand, [], Suit(SuitType.DOT, 2))
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
        result = can_hu(hand, [], Suit(SuitType.DOT, 1))
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
            if can_hu(remaining, [[Suit(SuitType.DOT, 1)] * 3], tile).is_winning:
                pytest.fail("Thirteen Wonders with open melds should return False")
