from enum import Enum, auto

from backend.domain.tiles import Dragon, DragonType, Suit, SuitType, Wind, WindType


class HandPattern(Enum):
    """Tile-structure-based winning hand patterns."""

    THIRTEEN_WONDERS = auto()
    THREE_GREAT_SCHOLARS = auto()
    THREE_LESSER_SCHOLARS = auto()
    FOUR_GREAT_BLESSINGS = auto()
    FOUR_LESSER_BLESSINGS = auto()
    EIGHTEEN_ARHATS = auto()
    NINE_GATES = auto()
    PURE_GREEN_SUIT = auto()
    ALL_HONOUR = auto()
    HIDDEN_TREASURE = auto()
    PURE_TERMINALS = auto()
    MIXED_TERMINALS = auto()
    FULLY_CONCEALED = auto()
    FULL_FLUSH_SEQUENCE_HAND = auto()
    FULL_FLUSH_TRIPLETS_HAND = auto()
    SEQUENCE_HAND = auto()
    LESSER_SEQUENCE_HAND = auto()
    FULL_FLUSH = auto()
    HALF_FLUSH = auto()
    TRIPLETS_HAND = auto()
    CHICKEN_HAND = auto()


SPECIAL_HAND_PATTERNS = frozenset(
    {
        HandPattern.THIRTEEN_WONDERS,
        HandPattern.THREE_GREAT_SCHOLARS,
        HandPattern.FOUR_GREAT_BLESSINGS,
        HandPattern.EIGHTEEN_ARHATS,
        HandPattern.NINE_GATES,
        HandPattern.PURE_GREEN_SUIT,
        HandPattern.ALL_HONOUR,
        HandPattern.HIDDEN_TREASURE,
        HandPattern.PURE_TERMINALS,
        HandPattern.FULL_FLUSH_SEQUENCE_HAND,
        HandPattern.FULL_FLUSH_TRIPLETS_HAND,
    }
)


ZHONG = Dragon(DragonType.ZHONG)
FA = Dragon(DragonType.FA)
BAI = Dragon(DragonType.BAI)
DONG = Wind(WindType.DONG)
NAN = Wind(WindType.NAN)
XI = Wind(WindType.XI)
BEI = Wind(WindType.BEI)
WAN_1 = Suit(SuitType.CHARACTER, 1)
WAN_9 = Suit(SuitType.CHARACTER, 9)
TONG_1 = Suit(SuitType.DOT, 1)
TONG_9 = Suit(SuitType.DOT, 9)
SUO_1 = Suit(SuitType.BAMBOO, 1)
SUO_2 = Suit(SuitType.BAMBOO, 2)
SUO_3 = Suit(SuitType.BAMBOO, 3)
SUO_4 = Suit(SuitType.BAMBOO, 4)
SUO_6 = Suit(SuitType.BAMBOO, 6)
SUO_8 = Suit(SuitType.BAMBOO, 8)
SUO_9 = Suit(SuitType.BAMBOO, 9)


THIRTEEN_WONDERS = frozenset(
    {
        WAN_1,
        WAN_9,
        TONG_1,
        TONG_9,
        SUO_1,
        SUO_9,
        ZHONG,
        FA,
        BAI,
        DONG,
        NAN,
        XI,
        BEI,
    }
)

THREE_GREAT_SCHOLARS = frozenset(
    {
        ZHONG,
        FA,
        BAI,
    }
)

FOUR_GREAT_BLESSINGS = frozenset(
    {
        DONG,
        NAN,
        XI,
        BEI,
    }
)

PURE_GREEN_SUIT_TILES = frozenset(
    {
        SUO_2,
        SUO_3,
        SUO_4,
        SUO_6,
        SUO_8,
        FA,
    }
)
