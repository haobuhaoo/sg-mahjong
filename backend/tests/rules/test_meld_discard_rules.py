from backend.domain.action_type import ActionType
from backend.domain.tiles import Suit, SuitType, Wind, WindType
from backend.rules.meld_discard_rules import get_invalid_discard_tiles


class TestGetInvalidDiscardTiles:
    def test_pong_delegates(self):
        tile = Suit(SuitType.DOT, 5)
        result = get_invalid_discard_tiles(ActionType.PONG, [], tile)
        assert result == {tile}

    def test_gang_delegates(self):
        tile = Wind(WindType.DONG)
        result = get_invalid_discard_tiles(ActionType.GANG, [], tile)
        assert result == {tile}

    def test_chi_delegates_with_valid_inputs(self):
        result = get_invalid_discard_tiles(
            ActionType.CHI,
            [Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 3)],
            Suit(SuitType.DOT, 4),
        )
        assert result == {Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 1)}

    def test_chi_returns_empty_when_thrown_not_suit(self):
        result = get_invalid_discard_tiles(
            ActionType.CHI,
            [Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 3)],
            Wind(WindType.DONG),
        )
        assert result == set()

    def test_chi_returns_empty_when_fewer_than_two_meld_tiles(self):
        result = get_invalid_discard_tiles(
            ActionType.CHI,
            [Suit(SuitType.DOT, 2)],
            Suit(SuitType.DOT, 4),
        )
        assert result == set()

    def test_chi_returns_empty_when_meld_tiles_contain_non_suit(self):
        result = get_invalid_discard_tiles(
            ActionType.CHI,
            [Suit(SuitType.DOT, 2), Wind(WindType.DONG)],
            Suit(SuitType.DOT, 4),
        )
        assert result == set()

    def test_unknown_meld_type_returns_empty(self):
        result = get_invalid_discard_tiles(
            "unknown",
            [Suit(SuitType.DOT, 2)],
            Suit(SuitType.DOT, 4),
        )
        assert result == set()

    def test_returns_set(self):
        result = get_invalid_discard_tiles(ActionType.PONG, [], Suit(SuitType.DOT, 1))
        assert isinstance(result, set)
