from backend.domain.meld import Meld
from backend.domain.player import Player
from backend.domain.tiles import (
    Animal,
    AnimalType,
    Dragon,
    DragonType,
    Suit,
    SuitType,
    Wind,
    WindType,
)
from backend.engine.turn_result import WinEvent, WinSource
from backend.rules.hand_patterns import HandPattern, SPECIAL_HAND_PATTERNS
from backend.rules.hu_result import HuResult
from backend.rules.scoring import (
    POINT_LIMIT,
    _concealed_hand_tai,
    _include_composite_hand_patterns,
    _winning_hand_tai,
    calculate_tai,
)


def _c(n, count=1):
    return [Suit(SuitType.CHARACTER, n) for _ in range(count)]


def _w(wind, count=1):
    return [Wind(wind) for _ in range(count)]


def _d(dragon, count=1):
    return [Dragon(dragon) for _ in range(count)]


def _m(tiles, is_exposed=True):
    return Meld(tiles=tiles, is_exposed=is_exposed)


class TestConcealedHandTai:
    def test_hidden_dragon_pong_awards_one(self):
        hand = _d(DragonType.ZHONG, 3) + _c(1, 10)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 1

    def test_two_hidden_dragon_pongs_award_two(self):
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 3) + _c(1, 7)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 2

    def test_dragon_pair_not_awarded(self):
        hand = _d(DragonType.ZHONG, 2) + _c(1, 11)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 0

    def test_hidden_seat_wind_pong_awards_one(self):
        hand = _w(WindType.DONG, 3) + _c(1, 10)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.NAN,
        )
        assert result == 1

    def test_hidden_prevalent_wind_pong_awards_one(self):
        hand = _w(WindType.NAN, 3) + _c(1, 10)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.NAN,
        )
        assert result == 1

    def test_wind_both_seat_and_prevalent_awards_two(self):
        hand = _w(WindType.DONG, 3) + _c(1, 10)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 2

    def test_non_matching_wind_awards_zero(self):
        hand = _w(WindType.XI, 3) + _c(1, 10)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.NAN,
        )
        assert result == 0

    def test_suit_tiles_never_awarded(self):
        hand = _c(1, 14)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 0

    def test_discard_win_appends_winning_tile(self):
        hand = _d(DragonType.ZHONG, 2) + _c(1, 11)
        winning_tile = Dragon(DragonType.ZHONG)
        result = _concealed_hand_tai(
            hand,
            WinSource.DISCARD,
            winning_tile,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 1

    def test_gang_four_copies_count_as_one_pong(self):
        hand = _d(DragonType.ZHONG, 4) + _c(1, 9)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 1

    def test_five_copies_still_one_pong(self):
        hand = _d(DragonType.ZHONG, 5) + _c(1, 8)
        result = _concealed_hand_tai(
            hand,
            WinSource.SELF_PICK,
            None,
            WindType.DONG,
            WindType.DONG,
        )
        assert result == 1


class TestIncludeCompositeHandPatterns:
    def test_hidden_treasure_added(self):
        patterns = frozenset({HandPattern.TRIPLETS_HAND, HandPattern.FULLY_CONCEALED})
        result = _include_composite_hand_patterns(patterns, WinSource.SELF_PICK)
        assert HandPattern.HIDDEN_TREASURE in result

    def test_hidden_treasure_not_added_without_self_pick(self):
        patterns = frozenset({HandPattern.TRIPLETS_HAND, HandPattern.FULLY_CONCEALED})
        result = _include_composite_hand_patterns(patterns, WinSource.DISCARD)
        assert HandPattern.HIDDEN_TREASURE not in result

    def test_full_flush_triplets_added(self):
        patterns = frozenset({HandPattern.FULL_FLUSH, HandPattern.TRIPLETS_HAND})
        result = _include_composite_hand_patterns(patterns, WinSource.SELF_PICK)
        assert HandPattern.FULL_FLUSH_TRIPLETS_HAND in result

    def test_full_flush_sequence_added(self):
        patterns = frozenset({HandPattern.FULL_FLUSH, HandPattern.SEQUENCE_HAND})
        result = _include_composite_hand_patterns(patterns, WinSource.SELF_PICK)
        assert HandPattern.FULL_FLUSH_SEQUENCE_HAND in result

    def test_full_flush_lesser_sequence_not_composited(self):
        patterns = frozenset({HandPattern.FULL_FLUSH, HandPattern.LESSER_SEQUENCE_HAND})
        result = _include_composite_hand_patterns(patterns, WinSource.SELF_PICK)
        assert HandPattern.FULL_FLUSH_SEQUENCE_HAND not in result

    def test_original_patterns_preserved(self):
        patterns = frozenset({HandPattern.TRIPLETS_HAND, HandPattern.FULLY_CONCEALED})
        result = _include_composite_hand_patterns(patterns, WinSource.SELF_PICK)
        assert HandPattern.TRIPLETS_HAND in result
        assert HandPattern.FULLY_CONCEALED in result

    def test_no_composite_when_no_match(self):
        patterns = frozenset({HandPattern.CHICKEN_HAND})
        result = _include_composite_hand_patterns(patterns, WinSource.SELF_PICK)
        assert result == patterns


class TestWinningHandTai:
    def test_chicken_hand_awards_zero(self):
        assert _winning_hand_tai(frozenset({HandPattern.CHICKEN_HAND}), POINT_LIMIT) == 0

    def test_triplets_hand_awards_two(self):
        assert _winning_hand_tai(frozenset({HandPattern.TRIPLETS_HAND}), POINT_LIMIT) == 2

    def test_half_flush_awards_two(self):
        assert _winning_hand_tai(frozenset({HandPattern.HALF_FLUSH}), POINT_LIMIT) == 2

    def test_full_flush_awards_four(self):
        assert _winning_hand_tai(frozenset({HandPattern.FULL_FLUSH}), POINT_LIMIT) == 4

    def test_sequence_hand_awards_four(self):
        assert _winning_hand_tai(frozenset({HandPattern.SEQUENCE_HAND}), POINT_LIMIT) == 4

    def test_lesser_sequence_hand_awards_one(self):
        assert _winning_hand_tai(frozenset({HandPattern.LESSER_SEQUENCE_HAND}), POINT_LIMIT) == 1

    def test_fully_concealed_awards_one(self):
        assert _winning_hand_tai(frozenset({HandPattern.FULLY_CONCEALED}), POINT_LIMIT) == 1

    def test_mixed_terminals_awards_two(self):
        assert _winning_hand_tai(frozenset({HandPattern.MIXED_TERMINALS}), POINT_LIMIT) == 2

    def test_three_lesser_scholars_awards_one(self):
        assert _winning_hand_tai(frozenset({HandPattern.THREE_LESSER_SCHOLARS}), POINT_LIMIT) == 1

    def test_four_lesser_blessings_awards_two(self):
        assert _winning_hand_tai(frozenset({HandPattern.FOUR_LESSER_BLESSINGS}), POINT_LIMIT) == 2

    def test_multiple_non_special_sums(self):
        patterns = frozenset(
            {
                HandPattern.TRIPLETS_HAND,
                HandPattern.HALF_FLUSH,
                HandPattern.FULLY_CONCEALED,
            }
        )
        assert _winning_hand_tai(patterns, POINT_LIMIT) == 5

    def test_capped_at_point_limit(self):
        patterns = frozenset(
            {
                HandPattern.FULL_FLUSH,
                HandPattern.TRIPLETS_HAND,
                HandPattern.FULLY_CONCEALED,
            }
        )
        assert _winning_hand_tai(patterns, POINT_LIMIT) == 5

    def test_special_pattern_returns_limit(self):
        for pattern in SPECIAL_HAND_PATTERNS:
            assert _winning_hand_tai(frozenset({pattern}), POINT_LIMIT) == POINT_LIMIT

    def test_special_pattern_short_circuits_before_sum(self):
        patterns = frozenset({HandPattern.ALL_HONOUR, HandPattern.CHICKEN_HAND})
        assert _winning_hand_tai(patterns, POINT_LIMIT) == POINT_LIMIT

    def test_mixed_terminals_with_triplets_sums_four(self):
        patterns = frozenset({HandPattern.MIXED_TERMINALS, HandPattern.TRIPLETS_HAND})
        assert _winning_hand_tai(patterns, POINT_LIMIT) == 4

    def test_full_flush_lesser_sequence_sums_five(self):
        patterns = frozenset({HandPattern.FULL_FLUSH, HandPattern.LESSER_SEQUENCE_HAND})
        assert _winning_hand_tai(patterns, POINT_LIMIT) == 5

    def test_respects_custom_point_limit(self):
        patterns = frozenset({HandPattern.HALF_FLUSH, HandPattern.TRIPLETS_HAND})
        assert _winning_hand_tai(patterns, 3) == 3


class TestCalculateTai:
    def test_non_winning_returns_zero(self):
        player = Player(0)
        result = calculate_tai(
            HuResult(False),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 0

    def test_chicken_hand_no_bonus(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 0

    def test_chicken_hand_with_hidden_dragon_pong(self):
        player = Player(0)
        hand = _d(DragonType.ZHONG, 3) + _c(1, 11)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND, HandPattern.FULLY_CONCEALED})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 2

    def test_player_tai_included(self):
        player = Player(0, tai=3)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 3

    def test_player_tai_plus_hidden_dragon(self):
        player = Player(0, tai=1)
        hand = _d(DragonType.FA, 3) + _c(1, 11)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 2

    def test_three_lesser_scholars_total_three(self):
        player = Player(0, tai=2)
        hand = _d(DragonType.ZHONG, 2) + _c(1, 7)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(
                True, frozenset({HandPattern.THREE_LESSER_SCHOLARS, HandPattern.CHICKEN_HAND})
            ),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 3

    def test_three_lesser_scholars_all_hidden(self):
        player = Player(0)
        hand = _d(DragonType.ZHONG, 3) + _d(DragonType.FA, 3) + _d(DragonType.BAI, 2) + _c(1, 5)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(
                True, frozenset({HandPattern.THREE_LESSER_SCHOLARS, HandPattern.CHICKEN_HAND})
            ),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 3

    def test_four_lesser_blessings_all_hidden(self):
        player = Player(0)
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 2)
            + _c(1, 2)
        )
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(
                True,
                frozenset({HandPattern.FOUR_LESSER_BLESSINGS, HandPattern.CHICKEN_HAND}),
            ),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 4

    def test_special_pattern_always_limit(self):
        player = Player(0, tai=2)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.THIRTEEN_WONDERS})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_replacement_tile_bonus(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.FULL_FLUSH})),
            WinSource.SELF_PICK,
            frozenset({WinEvent.REPLACEMENT_TILE}),
            player,
            None,
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_last_tile_bonus(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.HALF_FLUSH})),
            WinSource.SELF_PICK,
            frozenset({WinEvent.LAST_TILE}),
            player,
            None,
            WindType.DONG,
        )
        assert result == 3

    def test_robbing_gang_bonus(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.DISCARD,
            frozenset({WinEvent.ROBBING_GANG}),
            player,
            None,
            WindType.DONG,
        )
        assert result == 1

    def test_heavenly_event_always_limit(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.SELF_PICK,
            frozenset({WinEvent.HEAVENLY}),
            player,
            None,
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_earthly_event_always_limit(self):
        player = Player(1)
        hand = _c(1, 13)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.DISCARD,
            frozenset({WinEvent.EARTHLY}),
            player,
            Suit(SuitType.CHARACTER, 1),
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_capped_at_point_limit(self):
        player = Player(0, tai=3)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.FULL_FLUSH, HandPattern.SEQUENCE_HAND})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_hidden_treasure_via_composite(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(
                True,
                frozenset({HandPattern.TRIPLETS_HAND, HandPattern.FULLY_CONCEALED}),
            ),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_full_flush_triplets_via_composite(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(
                True,
                frozenset({HandPattern.FULL_FLUSH, HandPattern.TRIPLETS_HAND}),
            ),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == POINT_LIMIT

    def test_multiple_events_sum_correctly(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.SELF_PICK,
            frozenset({WinEvent.REPLACEMENT_TILE, WinEvent.LAST_TILE}),
            player,
            None,
            WindType.DONG,
        )
        assert result == 2

    def test_wind_pong_combined_with_blessings(self):
        player = Player(0, tai=0)
        hand = (
            _w(WindType.DONG, 3)
            + _w(WindType.NAN, 3)
            + _w(WindType.XI, 3)
            + _w(WindType.BEI, 2)
            + _c(1, 2)
        )
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(
                True,
                frozenset(
                    {
                        HandPattern.FOUR_LESSER_BLESSINGS,
                        HandPattern.CHICKEN_HAND,
                        HandPattern.TRIPLETS_HAND,
                    }
                ),
            ),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 5

    def test_bonus_tile_tai_in_player_tai_contributes(self):
        player = Player(0)
        player.add_bonus_tile([Animal(AnimalType.CAT)])
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.CHICKEN_HAND})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
        )
        assert result == 1

    def test_custom_point_limit(self):
        player = Player(0)
        hand = _c(1, 14)
        player.hand_tile = hand
        result = calculate_tai(
            HuResult(True, frozenset({HandPattern.TRIPLETS_HAND, HandPattern.HALF_FLUSH})),
            WinSource.SELF_PICK,
            frozenset(),
            player,
            None,
            WindType.DONG,
            point_limit=3,
        )
        assert result == 3
