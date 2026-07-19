from backend.domain.meld import Meld
from backend.domain.tiles import Suit, SuitType


class TestMeld:
    def test_default_is_exposed_false(self):
        meld = Meld()
        assert meld.is_exposed is False

    def test_default_tiles_empty(self):
        meld = Meld()
        assert meld.tiles == []

    def test_tiles_attr(self):
        tiles = [Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 3)]
        meld = Meld(tiles=tiles, is_exposed=True)
        assert meld.tiles == tiles
        assert meld.is_exposed is True

    def test_concealed_gang(self):
        tiles = [Suit(SuitType.DOT, 1)] * 4
        meld = Meld(tiles=tiles, is_exposed=False)
        assert meld.is_exposed is False
        assert len(meld.tiles) == 4
