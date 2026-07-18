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
SUO_9 = Suit(SuitType.BAMBOO, 9)

THIRTEEN_WONDERS = {
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

THREE_GREAT_SCHOLARS = {
    ZHONG,
    FA,
    BAI,
}

FOUR_GREAT_BLESSINGS = {
    DONG,
    NAN,
    XI,
    BEI,
}
