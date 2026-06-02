from enum import Enum


# Suited tiles
class SuitType(Enum):
    CHARACTER = "Wan"
    DOT = "Tong"
    BAMBOO = "Suo"


class Suit:
    def __init__(self, type: SuitType, number):
        self.type = type
        self.number = number

    def __str__(self):
        return f"{self.number} {self.type.value}"


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


class Honor:
    def __init__(self, type: WindType | DragonType):
        self.type = type

    def __str__(self):
        return f"{self.type.value}"


class Dragon(Honor):
    def __init__(self, type: DragonType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()


class Wind(Honor):
    def __init__(self, type: WindType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()


# Bonus tiles
class AnimalType(Enum):
    CAT = ("Cat", 0)
    RAT = ("Rat", 0)
    CHICKEN = ("Chicken", 0)
    CENTIPEDE = ("Centipede", 0)


class FlowerType(Enum):
    PLUM = ("Plum", 1)
    ORCHID = ("Orchid", 2)
    CHRYSANTHEMUM = ("Chrysanthemum", 3)
    BAMBOO = ("Bamboo", 4)


class SeasonType(Enum):
    SPRING = ("Spring", 1)
    SUMMER = ("Summer", 2)
    AUTUMN = ("Autumn", 3)
    WINTER = ("Winter", 4)


class Bonus:
    def __init__(self, type: AnimalType | FlowerType | SeasonType):
        self.type = type

    def __str__(self):
        return f"{self.type.value[0]}"


class Animal(Bonus):
    def __init__(self, type: AnimalType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()


class Flower(Bonus):
    def __init__(self, type: FlowerType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()


class Season(Bonus):
    def __init__(self, type: SeasonType):
        super().__init__(type)

    def __str__(self):
        return super().__str__()

