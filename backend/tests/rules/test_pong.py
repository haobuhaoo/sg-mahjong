from backend.domain.tiles import Suit, SuitType, Wind, WindType, Dragon, DragonType
from backend.rules.pong import get_invalid_pong_discards


class TestGetInvalidPongDiscards:
    def test_blocks_thrown_tile(self):
        tile = Suit(SuitType.DOT, 5)
        result = get_invalid_pong_discards(tile)
        assert result == {tile}

    def test_blocks_wind_tile(self):
        tile = Wind(WindType.DONG)
        result = get_invalid_pong_discards(tile)
        assert result == {tile}

    def test_blocks_dragon_tile(self):
        tile = Dragon(DragonType.ZHONG)
        result = get_invalid_pong_discards(tile)
        assert result == {tile}

    def test_returns_set(self):
        result = get_invalid_pong_discards(Suit(SuitType.DOT, 1))
        assert isinstance(result, set)
        assert len(result) == 1
