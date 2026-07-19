from backend.domain.meld import Meld
from backend.domain.tiles import (
    Suit,
    SuitType,
    Wind,
    WindType,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
    Animal,
    AnimalType,
    Season,
    SeasonType,
)
from backend.utils.helper import is_suit_tile, is_honor_tile, is_bonus_tile, is_chi_meld


class TestIsSuitTile:
    def test_true_for_suit(self):
        assert is_suit_tile(Suit(SuitType.DOT, 5)) is True

    def test_false_for_wind(self):
        assert is_suit_tile(Wind(WindType.DONG)) is False

    def test_false_for_dragon(self):
        assert is_suit_tile(Dragon(DragonType.ZHONG)) is False

    def test_false_for_bonus(self):
        assert is_suit_tile(Flower(FlowerType.PLUM)) is False
        assert is_suit_tile(Animal(AnimalType.CAT)) is False
        assert is_suit_tile(Season(SeasonType.SPRING)) is False


class TestIsHonorTile:
    def test_true_for_wind(self):
        assert is_honor_tile(Wind(WindType.DONG)) is True

    def test_true_for_dragon(self):
        assert is_honor_tile(Dragon(DragonType.ZHONG)) is True

    def test_false_for_suit(self):
        assert is_honor_tile(Suit(SuitType.DOT, 5)) is False

    def test_false_for_bonus(self):
        assert is_honor_tile(Flower(FlowerType.PLUM)) is False
        assert is_honor_tile(Animal(AnimalType.CAT)) is False
        assert is_honor_tile(Season(SeasonType.SPRING)) is False


class TestIsBonusTile:
    def test_true_for_flower(self):
        assert is_bonus_tile(Flower(FlowerType.PLUM)) is True

    def test_true_for_animal(self):
        assert is_bonus_tile(Animal(AnimalType.CAT)) is True

    def test_true_for_season(self):
        assert is_bonus_tile(Season(SeasonType.SPRING)) is True

    def test_false_for_suit(self):
        assert is_bonus_tile(Suit(SuitType.DOT, 5)) is False

    def test_false_for_wind(self):
        assert is_bonus_tile(Wind(WindType.DONG)) is False

    def test_false_for_dragon(self):
        assert is_bonus_tile(Dragon(DragonType.ZHONG)) is False


class TestIsChiMeld:
    def test_true_for_chi(self):
        meld = Meld(
            tiles=[
                Suit(SuitType.DOT, 1),
                Suit(SuitType.DOT, 2),
                Suit(SuitType.DOT, 3),
            ]
        )
        assert is_chi_meld(meld) is True

    def test_false_for_pong(self):
        meld = Meld(tiles=[Suit(SuitType.DOT, 1)] * 3)
        assert is_chi_meld(meld) is False

    def test_false_for_gang(self):
        meld = Meld(tiles=[Suit(SuitType.DOT, 1)] * 4)
        assert is_chi_meld(meld) is False
