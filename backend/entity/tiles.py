from abc import ABC, abstractmethod
from enum import Enum


class Tile(ABC):
    @abstractmethod
    def sort_key(self):
        # Relative order of tiles (ascending):
        # Non-bonus tiles -- Character (1 to 9), Dot (1 to 9), Bamboo (1 to 9),
        #                    Zhong, Fa, Bai, Dong, Nan, Xi, Bei
        # Bonus tiles -- Cat, Rat, Chicken, Centipede, Plum, Orchid, Chrysanthemum,
        #                Bamboo, Spring, Summer, Autumn, Winter
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"


# Suited tiles
class SuitType(Enum):
    CHARACTER = "Wan"
    DOT = "Tong"
    BAMBOO = "Suo"


class Suit(Tile):
    def __init__(self, type: SuitType, number):
        self.type = type
        if number < 1 or number > 9:
            raise ValueError("Suit tiles are between 1 and 9")
        self.number = number

    def __str__(self):
        return f"{self.number} {self.type.value}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type}, {self.number})"

    def sort_key(self):
        order = {
            SuitType.CHARACTER: 0,
            SuitType.DOT: 1,
            SuitType.BAMBOO: 2,
        }
        return (order[self.type], self.number)


# Honor tiles
class DragonType(Enum):
    ZHONG = "Hong Zhong"
    FA = "Fa Cai"
    BAI = "Bai Ban"


class WindType(Enum):
    DONG = "Dong Feng"
    NAN = "Nan Feng"
    XI = "Xi Feng"
    BEI = "Bei Feng"


class Honor(ABC):
    def __init__(self, type: WindType | DragonType):
        self.type = type

    def __str__(self):
        return f"{self.type.value}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type})"


class Dragon(Honor):
    def __init__(self, type: DragonType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()

    def sort_key(self):
        dragon_order = {
            DragonType.ZHONG: 0,
            DragonType.FA: 1,
            DragonType.BAI: 2,
        }
        return (3 + dragon_order[self.type], 0)


class Wind(Honor):
    def __init__(self, type: WindType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()

    def sort_key(self):
        wind_order = {
            WindType.DONG: 0,
            WindType.NAN: 1,
            WindType.XI: 2,
            WindType.BEI: 3,
        }
        return (6 + wind_order[self.type], 0)


# Bonus tiles
class AnimalType(Enum):
    CAT = ("Cat", -1)
    RAT = ("Rat", -1)
    CHICKEN = ("Chicken", -2)
    CENTIPEDE = ("Centipede", -2)


class FlowerType(Enum):
    PLUM = ("Plum", 0)
    ORCHID = ("Orchid", 1)
    CHRYSANTHEMUM = ("Chrysanthemum", 2)
    BAMBOO = ("Bamboo", 3)


class SeasonType(Enum):
    SPRING = ("Spring", 0)
    SUMMER = ("Summer", 1)
    AUTUMN = ("Autumn", 2)
    WINTER = ("Winter", 3)


class Bonus(Tile):
    def __init__(self, type: AnimalType | FlowerType | SeasonType):
        self.type = type

    def __str__(self):
        return f"{self.type.value[0]}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type})"

    def get_ordering(self):
        return self.type.value[1]


class Animal(Bonus):
    def __init__(self, type: AnimalType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()

    def sort_key(self):
        animal_order = {
            AnimalType.CAT: 0,
            AnimalType.RAT: 1,
            AnimalType.CHICKEN: 2,
            AnimalType.CENTIPEDE: 3,
        }
        return (0, animal_order[self.type])


class Flower(Bonus):
    def __init__(self, type: FlowerType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()

    def sort_key(self):
        flower_order = {
            FlowerType.PLUM: 0,
            FlowerType.ORCHID: 1,
            FlowerType.CHRYSANTHEMUM: 2,
            FlowerType.BAMBOO: 3,
        }
        return (1, flower_order[self.type])


class Season(Bonus):
    def __init__(self, type: SeasonType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()

    def sort_key(self):
        season_order = {
            SeasonType.SPRING: 0,
            SeasonType.SUMMER: 1,
            SeasonType.AUTUMN: 2,
            SeasonType.WINTER: 3,
        }
        return (2, season_order[self.type])
