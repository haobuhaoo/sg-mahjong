"""Tile-set constants used to detect set-based winning hand patterns."""

from backend.domain.tiles import Dragon, DragonType, Suit, SuitType, Wind, WindType

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
