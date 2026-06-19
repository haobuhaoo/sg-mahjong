import pytest

from backend.domain.tiles import (
    SuitType,
    Suit,
    DragonType,
    WindType,
    Dragon,
    Wind,
    AnimalType,
    FlowerType,
    SeasonType,
    Animal,
    Flower,
    Season,
    MeldType,
)


class TestSuitType:
    def test_values(self):
        assert SuitType.CHARACTER.value == "Wan"
        assert SuitType.DOT.value == "Tong"
        assert SuitType.BAMBOO.value == "Suo"

    def test_three_members(self):
        assert len(SuitType) == 3


class TestSuit:
    def test_str(self):
        s = Suit(SuitType.CHARACTER, 1)
        assert str(s) == "1 Wan"

    def test_str_different_suits(self):
        assert str(Suit(SuitType.DOT, 5)) == "5 Tong"
        assert str(Suit(SuitType.BAMBOO, 9)) == "9 Suo"

    def test_repr(self):
        s = Suit(SuitType.CHARACTER, 1)
        r = repr(s)
        assert "Suit" in r
        assert "CHARACTER" in r
        assert "1" in r

    def test_eq_same_tile(self):
        a = Suit(SuitType.DOT, 5)
        b = Suit(SuitType.DOT, 5)
        assert a == b

    def test_eq_different_number(self):
        a = Suit(SuitType.DOT, 5)
        b = Suit(SuitType.DOT, 6)
        assert a != b

    def test_eq_different_suit(self):
        a = Suit(SuitType.DOT, 5)
        b = Suit(SuitType.CHARACTER, 5)
        assert a != b

    def test_eq_different_type(self):
        assert Suit(SuitType.DOT, 1) != "string"

    def test_hash_equal_for_equal_tiles(self):
        a = Suit(SuitType.DOT, 5)
        b = Suit(SuitType.DOT, 5)
        assert hash(a) == hash(b)

    def test_hash_not_equal_for_different_tiles(self):
        a = Suit(SuitType.DOT, 5)
        b = Suit(SuitType.DOT, 6)
        assert hash(a) != hash(b)

    def test_set_membership(self):
        s = {Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 1)}
        assert len(s) == 1

    def test_sort_key_character(self):
        s = Suit(SuitType.CHARACTER, 5)
        assert s.sort_key() == (0, 5)

    def test_sort_key_dot(self):
        s = Suit(SuitType.DOT, 5)
        assert s.sort_key() == (1, 5)

    def test_sort_key_bamboo(self):
        s = Suit(SuitType.BAMBOO, 5)
        assert s.sort_key() == (2, 5)

    def test_sort_key_ordering_across_suits(self):
        tiles = [
            Suit(SuitType.BAMBOO, 1),
            Suit(SuitType.CHARACTER, 1),
            Suit(SuitType.DOT, 1),
        ]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].type == SuitType.CHARACTER
        assert tiles[1].type == SuitType.DOT
        assert tiles[2].type == SuitType.BAMBOO

    def test_sort_key_ordering_within_suit(self):
        tiles = [Suit(SuitType.DOT, 9), Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 5)]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].number == 1
        assert tiles[1].number == 5
        assert tiles[2].number == 9

    def test_valid_numbers_1_to_9(self):
        for n in range(1, 10):
            s = Suit(SuitType.DOT, n)
            assert s.number == n

    def test_value_error_for_zero(self):
        with pytest.raises(ValueError, match="Suit tiles are between 1 and 9"):
            Suit(SuitType.DOT, 0)

    def test_value_error_for_ten(self):
        with pytest.raises(ValueError, match="Suit tiles are between 1 and 9"):
            Suit(SuitType.DOT, 10)

    def test_value_error_for_negative(self):
        with pytest.raises(ValueError, match="Suit tiles are between 1 and 9"):
            Suit(SuitType.DOT, -1)


class TestDragonType:
    def test_values(self):
        assert DragonType.ZHONG.value == "Hong Zhong"
        assert DragonType.FA.value == "Fa Cai"
        assert DragonType.BAI.value == "Bai Ban"

    def test_three_members(self):
        assert len(DragonType) == 3


class TestWindType:
    def test_values(self):
        assert WindType.DONG.value == "Dong Feng"
        assert WindType.NAN.value == "Nan Feng"
        assert WindType.XI.value == "Xi Feng"
        assert WindType.BEI.value == "Bei Feng"

    def test_four_members(self):
        assert len(WindType) == 4


class TestDragon:
    def test_str(self):
        assert str(Dragon(DragonType.ZHONG)) == "Hong Zhong"
        assert str(Dragon(DragonType.FA)) == "Fa Cai"
        assert str(Dragon(DragonType.BAI)) == "Bai Ban"

    def test_repr(self):
        d = Dragon(DragonType.ZHONG)
        r = repr(d)
        assert "Dragon" in r

    def test_eq_same_dragon(self):
        a = Dragon(DragonType.ZHONG)
        b = Dragon(DragonType.ZHONG)
        assert a == b

    def test_eq_different_dragon(self):
        a = Dragon(DragonType.ZHONG)
        b = Dragon(DragonType.FA)
        assert a != b

    def test_eq_different_type(self):
        assert Dragon(DragonType.ZHONG) != "string"
        assert Dragon(DragonType.ZHONG) != Wind(WindType.DONG)

    def test_hash_equal_for_equal_dragons(self):
        a = Dragon(DragonType.ZHONG)
        b = Dragon(DragonType.ZHONG)
        assert hash(a) == hash(b)

    def test_hash_not_equal_for_different_dragons(self):
        a = Dragon(DragonType.ZHONG)
        b = Dragon(DragonType.FA)
        assert hash(a) != hash(b)

    def test_set_membership(self):
        s = {Dragon(DragonType.ZHONG), Dragon(DragonType.ZHONG)}
        assert len(s) == 1

    def test_sort_key_ordering(self):
        tiles = [
            Dragon(DragonType.BAI),
            Dragon(DragonType.FA),
            Dragon(DragonType.ZHONG),
        ]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].type == DragonType.ZHONG
        assert tiles[1].type == DragonType.FA
        assert tiles[2].type == DragonType.BAI

    def test_sort_key_values(self):
        assert Dragon(DragonType.ZHONG).sort_key() == (3, 0)
        assert Dragon(DragonType.FA).sort_key() == (4, 0)
        assert Dragon(DragonType.BAI).sort_key() == (5, 0)


class TestWind:
    def test_str(self):
        assert str(Wind(WindType.DONG)) == "Dong Feng"
        assert str(Wind(WindType.NAN)) == "Nan Feng"
        assert str(Wind(WindType.XI)) == "Xi Feng"
        assert str(Wind(WindType.BEI)) == "Bei Feng"

    def test_repr(self):
        w = Wind(WindType.DONG)
        r = repr(w)
        assert "Wind" in r

    def test_eq_same_wind(self):
        a = Wind(WindType.DONG)
        b = Wind(WindType.DONG)
        assert a == b

    def test_eq_different_wind(self):
        a = Wind(WindType.DONG)
        b = Wind(WindType.NAN)
        assert a != b

    def test_eq_different_type(self):
        assert Wind(WindType.DONG) != "string"
        assert Wind(WindType.DONG) != Dragon(DragonType.ZHONG)

    def test_hash_equal_for_equal_winds(self):
        a = Wind(WindType.DONG)
        b = Wind(WindType.DONG)
        assert hash(a) == hash(b)

    def test_hash_not_equal_for_different_winds(self):
        a = Wind(WindType.DONG)
        b = Wind(WindType.NAN)
        assert hash(a) != hash(b)

    def test_set_membership(self):
        s = {Wind(WindType.DONG), Wind(WindType.DONG)}
        assert len(s) == 1

    def test_sort_key_ordering(self):
        tiles = [
            Wind(WindType.BEI),
            Wind(WindType.NAN),
            Wind(WindType.DONG),
            Wind(WindType.XI),
        ]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].type == WindType.DONG
        assert tiles[1].type == WindType.NAN
        assert tiles[2].type == WindType.XI
        assert tiles[3].type == WindType.BEI

    def test_sort_key_values(self):
        assert Wind(WindType.DONG).sort_key() == (6, 0)
        assert Wind(WindType.NAN).sort_key() == (7, 0)
        assert Wind(WindType.XI).sort_key() == (8, 0)
        assert Wind(WindType.BEI).sort_key() == (9, 0)


class TestAnimalType:
    def test_values(self):
        assert AnimalType.CAT.value == ("Cat", -1)
        assert AnimalType.RAT.value == ("Rat", -1)
        assert AnimalType.CHICKEN.value == ("Chicken", -2)
        assert AnimalType.CENTIPEDE.value == ("Centipede", -2)

    def test_four_members(self):
        assert len(AnimalType) == 4


class TestFlowerType:
    def test_values(self):
        assert FlowerType.PLUM.value == ("Plum", 0)
        assert FlowerType.ORCHID.value == ("Orchid", 1)
        assert FlowerType.CHRYSANTHEMUM.value == ("Chrysanthemum", 2)
        assert FlowerType.BAMBOO.value == ("Bamboo", 3)

    def test_four_members(self):
        assert len(FlowerType) == 4


class TestSeasonType:
    def test_values(self):
        assert SeasonType.SPRING.value == ("Spring", 0)
        assert SeasonType.SUMMER.value == ("Summer", 1)
        assert SeasonType.AUTUMN.value == ("Autumn", 2)
        assert SeasonType.WINTER.value == ("Winter", 3)

    def test_four_members(self):
        assert len(SeasonType) == 4


class TestAnimal:
    def test_str(self):
        assert str(Animal(AnimalType.CAT)) == "Cat"
        assert str(Animal(AnimalType.RAT)) == "Rat"
        assert str(Animal(AnimalType.CHICKEN)) == "Chicken"
        assert str(Animal(AnimalType.CENTIPEDE)) == "Centipede"

    def test_repr(self):
        a = Animal(AnimalType.CAT)
        r = repr(a)
        assert "Animal" in r

    def test_eq_all_animals_equal(self):
        assert Animal(AnimalType.CAT) == Animal(AnimalType.RAT)
        assert Animal(AnimalType.CAT) == Animal(AnimalType.CHICKEN)

    def test_eq_different_type(self):
        assert Animal(AnimalType.CAT) != Flower(FlowerType.PLUM)
        assert Animal(AnimalType.CAT) != Season(SeasonType.SPRING)

    def test_hash_all_animals_same(self):
        assert hash(Animal(AnimalType.CAT)) == hash(Animal(AnimalType.RAT))
        assert hash(Animal(AnimalType.CAT)) == hash(Animal(AnimalType.CHICKEN))

    def test_set_membership_all_animals_same(self):
        s = {Animal(AnimalType.CAT), Animal(AnimalType.RAT)}
        assert len(s) == 1

    def test_get_ordering(self):
        assert Animal(AnimalType.CAT).get_ordering() == -1
        assert Animal(AnimalType.RAT).get_ordering() == -1
        assert Animal(AnimalType.CHICKEN).get_ordering() == -2
        assert Animal(AnimalType.CENTIPEDE).get_ordering() == -2

    def test_sort_key_ordering(self):
        tiles = [
            Animal(AnimalType.CENTIPEDE),
            Animal(AnimalType.RAT),
            Animal(AnimalType.CAT),
            Animal(AnimalType.CHICKEN),
        ]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].type == AnimalType.CAT
        assert tiles[1].type == AnimalType.RAT
        assert tiles[2].type == AnimalType.CHICKEN
        assert tiles[3].type == AnimalType.CENTIPEDE

    def test_sort_key_values(self):
        assert Animal(AnimalType.CAT).sort_key() == (0, 0)
        assert Animal(AnimalType.RAT).sort_key() == (0, 1)
        assert Animal(AnimalType.CHICKEN).sort_key() == (0, 2)
        assert Animal(AnimalType.CENTIPEDE).sort_key() == (0, 3)


class TestFlower:
    def test_str(self):
        assert str(Flower(FlowerType.PLUM)) == "Plum"
        assert str(Flower(FlowerType.ORCHID)) == "Orchid"
        assert str(Flower(FlowerType.CHRYSANTHEMUM)) == "Chrysanthemum"
        assert str(Flower(FlowerType.BAMBOO)) == "Bamboo"

    def test_repr(self):
        f = Flower(FlowerType.PLUM)
        r = repr(f)
        assert "Flower" in r

    def test_eq_all_flowers_equal(self):
        assert Flower(FlowerType.PLUM) == Flower(FlowerType.ORCHID)
        assert Flower(FlowerType.PLUM) == Flower(FlowerType.BAMBOO)

    def test_eq_different_type(self):
        assert Flower(FlowerType.PLUM) != Animal(AnimalType.CAT)
        assert Flower(FlowerType.PLUM) != Season(SeasonType.SPRING)

    def test_hash_all_flowers_same(self):
        assert hash(Flower(FlowerType.PLUM)) == hash(Flower(FlowerType.ORCHID))
        assert hash(Flower(FlowerType.PLUM)) == hash(Flower(FlowerType.BAMBOO))

    def test_set_membership_all_flowers_same(self):
        s = {Flower(FlowerType.PLUM), Flower(FlowerType.ORCHID)}
        assert len(s) == 1

    def test_get_ordering(self):
        assert Flower(FlowerType.PLUM).get_ordering() == 0
        assert Flower(FlowerType.ORCHID).get_ordering() == 1
        assert Flower(FlowerType.CHRYSANTHEMUM).get_ordering() == 2
        assert Flower(FlowerType.BAMBOO).get_ordering() == 3

    def test_sort_key_ordering(self):
        tiles = [
            Flower(FlowerType.BAMBOO),
            Flower(FlowerType.ORCHID),
            Flower(FlowerType.PLUM),
            Flower(FlowerType.CHRYSANTHEMUM),
        ]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].type == FlowerType.PLUM
        assert tiles[1].type == FlowerType.ORCHID
        assert tiles[2].type == FlowerType.CHRYSANTHEMUM
        assert tiles[3].type == FlowerType.BAMBOO

    def test_sort_key_values(self):
        assert Flower(FlowerType.PLUM).sort_key() == (1, 0)
        assert Flower(FlowerType.ORCHID).sort_key() == (1, 1)
        assert Flower(FlowerType.CHRYSANTHEMUM).sort_key() == (1, 2)
        assert Flower(FlowerType.BAMBOO).sort_key() == (1, 3)


class TestSeason:
    def test_str(self):
        assert str(Season(SeasonType.SPRING)) == "Spring"
        assert str(Season(SeasonType.SUMMER)) == "Summer"
        assert str(Season(SeasonType.AUTUMN)) == "Autumn"
        assert str(Season(SeasonType.WINTER)) == "Winter"

    def test_repr(self):
        s = Season(SeasonType.SPRING)
        r = repr(s)
        assert "Season" in r

    def test_eq_all_seasons_equal(self):
        assert Season(SeasonType.SPRING) == Season(SeasonType.SUMMER)
        assert Season(SeasonType.SPRING) == Season(SeasonType.WINTER)

    def test_eq_different_type(self):
        assert Season(SeasonType.SPRING) != Animal(AnimalType.CAT)
        assert Season(SeasonType.SPRING) != Flower(FlowerType.PLUM)

    def test_hash_all_seasons_same(self):
        assert hash(Season(SeasonType.SPRING)) == hash(Season(SeasonType.SUMMER))
        assert hash(Season(SeasonType.SPRING)) == hash(Season(SeasonType.WINTER))

    def test_set_membership_all_seasons_same(self):
        s = {Season(SeasonType.SPRING), Season(SeasonType.SUMMER)}
        assert len(s) == 1

    def test_get_ordering(self):
        assert Season(SeasonType.SPRING).get_ordering() == 0
        assert Season(SeasonType.SUMMER).get_ordering() == 1
        assert Season(SeasonType.AUTUMN).get_ordering() == 2
        assert Season(SeasonType.WINTER).get_ordering() == 3

    def test_sort_key_ordering(self):
        tiles = [
            Season(SeasonType.WINTER),
            Season(SeasonType.SUMMER),
            Season(SeasonType.SPRING),
            Season(SeasonType.AUTUMN),
        ]
        tiles.sort(key=lambda t: t.sort_key())
        assert tiles[0].type == SeasonType.SPRING
        assert tiles[1].type == SeasonType.SUMMER
        assert tiles[2].type == SeasonType.AUTUMN
        assert tiles[3].type == SeasonType.WINTER

    def test_sort_key_values(self):
        assert Season(SeasonType.SPRING).sort_key() == (2, 0)
        assert Season(SeasonType.SUMMER).sort_key() == (2, 1)
        assert Season(SeasonType.AUTUMN).sort_key() == (2, 2)
        assert Season(SeasonType.WINTER).sort_key() == (2, 3)


class TestFullSortOrder:
    def test_suits_before_dragons(self):
        tiles = [Dragon(DragonType.ZHONG), Suit(SuitType.CHARACTER, 1)]
        tiles.sort(key=lambda t: t.sort_key())
        assert isinstance(tiles[0], Suit)
        assert isinstance(tiles[1], Dragon)

    def test_dragons_before_winds(self):
        tiles = [Wind(WindType.DONG), Dragon(DragonType.ZHONG)]
        tiles.sort(key=lambda t: t.sort_key())
        assert isinstance(tiles[0], Dragon)
        assert isinstance(tiles[1], Wind)

    def test_bonus_before_non_bonus(self):
        tiles = [Suit(SuitType.DOT, 1), Flower(FlowerType.PLUM)]
        tiles.sort(key=lambda t: t.sort_key())
        assert isinstance(tiles[0], Flower)
        assert isinstance(tiles[1], Suit)

    def test_animals_before_flowers(self):
        tiles = [Flower(FlowerType.PLUM), Animal(AnimalType.CAT)]
        tiles.sort(key=lambda t: t.sort_key())
        assert isinstance(tiles[0], Animal)
        assert isinstance(tiles[1], Flower)

    def test_flowers_before_seasons(self):
        tiles = [Season(SeasonType.SPRING), Flower(FlowerType.PLUM)]
        tiles.sort(key=lambda t: t.sort_key())
        assert isinstance(tiles[0], Flower)
        assert isinstance(tiles[1], Season)


class TestMeldType:
    def test_chi_value(self):
        assert MeldType.CHI == "chi"

    def test_pong_value(self):
        assert MeldType.PONG == "pong"

    def test_gang_value(self):
        assert MeldType.GANG == "gang"
