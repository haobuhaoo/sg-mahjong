from abc import ABC, abstractmethod
from enum import Enum, StrEnum


class Tile(ABC):
    """Abstract base class for all mahjong tiles."""

    @abstractmethod
    def sort_key(self):
        """
        Sort the tiles in relative order (ascending):

        Non-bonus tiles: Character (1 to 9), Dot (1 to 9), Bamboo (1 to 9), Zhong, Fa, Bai, Dong,
        Nan, Xi, Bei

        Bonus tiles: Cat, Rat, Chicken, Centipede, Plum, Orchid, Chrysanthemum, Bamboo, Spring,
        Summer, Autumn, Winter
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"


# Suited tiles
class SuitType(Enum):
    """The three suit categories: Character, Dot, and Bamboo."""

    CHARACTER = "Wan"
    DOT = "Tong"
    BAMBOO = "Suo"


class Suit(Tile):
    """A suited tile with a suit category and a number from 1 to 9."""

    def __init__(self, type: SuitType, number: int):
        """
        Create a suited tile.

        Args:
            type: The suit category of the tile
            number: The tile number (1-9 valid)

        Raises:
            ValueError: If number is not in [1, 9]
        """
        self.type = type
        if number < 1 or number > 9:
            raise ValueError("Suit tiles are between 1 and 9")
        self.number = number

    def __str__(self):
        return f"{self.number} {self.type.value}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type}, {self.number})"

    def __eq__(self, value):
        return isinstance(value, Suit) and self.type == value.type and self.number == value.number

    def __hash__(self):
        return hash((self.type, self.number))

    def sort_key(self):
        """Order suits as Character, Dot, Bamboo, then by number."""
        order = {
            SuitType.CHARACTER: 0,
            SuitType.DOT: 1,
            SuitType.BAMBOO: 2,
        }
        return (order[self.type], self.number)


# Honor tiles
class DragonType(Enum):
    """The three dragon variants: Zhong, Fa, and Bai."""

    ZHONG = "Hong Zhong"
    FA = "Fa Cai"
    BAI = "Bai Ban"


class WindType(Enum):
    """The four wind variants: Dong, Nan, Xi, and Bei."""

    DONG = "Dong Feng"
    NAN = "Nan Feng"
    XI = "Xi Feng"
    BEI = "Bei Feng"


class Honor(Tile):
    """Abstract base class for honor tiles (winds and dragons)."""

    def __init__(self, type: WindType | DragonType):
        """
        Create an honor tile.

        Args:
            type: The wind or dragon variant of the tile
        """
        self.type = type

    def __str__(self):
        return f"{self.type.value}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type})"

    def __hash__(self):
        return hash(self.type)


class Dragon(Honor):
    """A dragon honor tile."""

    def __init__(self, type: DragonType):
        """
        Create a dragon tile.

        Args:
            type: The dragon variant of the tile
        """
        super().__init__(type)

    def __eq__(self, value):
        return isinstance(value, Dragon) and self.type == value.type

    def __hash__(self):
        return super().__hash__()

    def sort_key(self):
        """Order dragons after suits: Zhong, Fa, Bai."""
        dragon_order = {
            DragonType.ZHONG: 0,
            DragonType.FA: 1,
            DragonType.BAI: 2,
        }
        return (3 + dragon_order[self.type], 0)


class Wind(Honor):
    """A wind honor tile."""

    def __init__(self, type: WindType):
        """
        Create a wind tile.

        Args:
            type: The wind variant of the tile
        """
        super().__init__(type)

    def __eq__(self, value):
        return isinstance(value, Wind) and self.type == value.type

    def __hash__(self):
        return super().__hash__()

    def sort_key(self):
        """Order winds after dragons: Dong, Nan, Xi, Bei."""
        wind_order = {
            WindType.DONG: 0,
            WindType.NAN: 1,
            WindType.XI: 2,
            WindType.BEI: 3,
        }
        return (6 + wind_order[self.type], 0)


# Bonus tiles
class AnimalType(Enum):
    """The four animal variants. Each value is (display name, ordering value) tuple."""

    CAT = ("Cat", -1)
    RAT = ("Rat", -1)
    CHICKEN = ("Chicken", -2)
    CENTIPEDE = ("Centipede", -2)


class FlowerType(Enum):
    """The four flower variants. Each value is (display name, matching seat position) tuple."""

    PLUM = ("Plum", 0)
    ORCHID = ("Orchid", 1)
    CHRYSANTHEMUM = ("Chrysanthemum", 2)
    BAMBOO = ("Bamboo", 3)


class SeasonType(Enum):
    """The four season variants. Each value is (display name, matching seat position) tuple."""

    SPRING = ("Spring", 0)
    SUMMER = ("Summer", 1)
    AUTUMN = ("Autumn", 2)
    WINTER = ("Winter", 3)


class Bonus(Tile):
    """Abstract base class for bonus tiles (animals, flowers, seasons)."""

    def __init__(self, type: AnimalType | FlowerType | SeasonType):
        """
        Create a bonus tile.

        Args:
            type: The animal, flower, or season variant of the tile
        """
        self.type = type

    def __str__(self):
        return f"{self.type.value[0]}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type})"

    def __hash__(self):
        return hash(self.type)

    def get_ordering(self):
        """Return the tile's ordering value (matching seat position for flowers/seasons)."""
        return self.type.value[1]


class Animal(Bonus):
    """An animal bonus tile."""

    def __init__(self, type: AnimalType):
        """
        Create an animal tile.

        Args:
            type: The animal variant of the tile
        """
        super().__init__(type)

    def __eq__(self, value):
        return isinstance(value, Animal) and self.type == value.type

    def __hash__(self):
        return super().__hash__()

    def sort_key(self):
        """Order animals first among bonus tiles: Cat, Rat, Chicken, Centipede."""
        animal_order = {
            AnimalType.CAT: 0,
            AnimalType.RAT: 1,
            AnimalType.CHICKEN: 2,
            AnimalType.CENTIPEDE: 3,
        }
        return (0, animal_order[self.type])


class Flower(Bonus):
    """A flower bonus tile."""

    def __init__(self, type: FlowerType):
        """
        Create a flower tile.

        Args:
            type: The flower variant of the tile
        """
        super().__init__(type)

    def __eq__(self, value):
        return isinstance(value, Flower) and self.type == value.type

    def __hash__(self):
        return super().__hash__()

    def sort_key(self):
        """Order flowers after animals: Plum, Orchid, Chrysanthemum, Bamboo."""
        flower_order = {
            FlowerType.PLUM: 0,
            FlowerType.ORCHID: 1,
            FlowerType.CHRYSANTHEMUM: 2,
            FlowerType.BAMBOO: 3,
        }
        return (1, flower_order[self.type])


class Season(Bonus):
    """A season bonus tile."""

    def __init__(self, type: SeasonType):
        """
        Create a season tile.

        Args:
            type: The season variant of the tile
        """
        super().__init__(type)

    def __eq__(self, value):
        return isinstance(value, Season) and self.type == value.type

    def __hash__(self):
        return super().__hash__()

    def sort_key(self):
        """Order seasons after flowers: Spring, Summer, Autumn, Winter."""
        season_order = {
            SeasonType.SPRING: 0,
            SeasonType.SUMMER: 1,
            SeasonType.AUTUMN: 2,
            SeasonType.WINTER: 3,
        }
        return (2, season_order[self.type])


class MeldType(StrEnum):
    """The three claimable meld types."""

    CHI = "chi"
    PONG = "pong"
    GANG = "gang"
