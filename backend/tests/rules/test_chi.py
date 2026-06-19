from backend.domain.tiles import Suit, SuitType
from backend.rules.chi import get_invalid_chi_discards


class TestGetInvalidChiDiscards:
    def test_thrown_last_middle_of_range(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 3)],
            Suit(SuitType.DOT, 4),
        )
        assert result == {Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 1)}

    def test_thrown_last_at_lower_boundary(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)],
            Suit(SuitType.DOT, 3),
        )
        assert result == {Suit(SuitType.DOT, 3)}

    def test_thrown_first_middle_of_range(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4)],
            Suit(SuitType.DOT, 2),
        )
        assert result == {Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 5)}

    def test_thrown_first_at_upper_boundary(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 8), Suit(SuitType.DOT, 9)],
            Suit(SuitType.DOT, 7),
        )
        assert result == {Suit(SuitType.DOT, 7)}

    def test_thrown_middle(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 4)],
            Suit(SuitType.DOT, 3),
        )
        assert result == {Suit(SuitType.DOT, 3)}

    def test_different_suit_type_blocks_only_thrown(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.CHARACTER, 2), Suit(SuitType.CHARACTER, 3)],
            Suit(SuitType.DOT, 4),
        )
        assert result == {Suit(SuitType.DOT, 4)}

    def test_mixed_suit_types_in_meld_blocks_only_thrown(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.CHARACTER, 2), Suit(SuitType.DOT, 3)],
            Suit(SuitType.DOT, 4),
        )
        assert result == {Suit(SuitType.DOT, 4)}

    def test_thrown_last_with_gap(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 4)],
            Suit(SuitType.DOT, 5),
        )
        assert result == {Suit(SuitType.DOT, 5), Suit(SuitType.DOT, 1)}

    def test_thrown_first_with_gap(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 6)],
            Suit(SuitType.DOT, 3),
        )
        assert result == {Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 6)}

    def test_thrown_always_blocked_regardless_of_guards(self):
        tile = Suit(SuitType.DOT, 5)
        result = get_invalid_chi_discards([Suit(SuitType.DOT, 1)], tile)
        assert tile in result

    def test_returns_set(self):
        result = get_invalid_chi_discards(
            [Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 3)],
            Suit(SuitType.DOT, 4),
        )
        assert isinstance(result, set)
