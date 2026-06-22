from backend.domain.tiles import Dragon, DragonType, Suit, SuitType, Wind, WindType

ZHONG = Dragon(DragonType.ZHONG)
FA = Dragon(DragonType.FA)
BAI = Dragon(DragonType.BAI)
DONG = Wind(WindType.DONG)
NAN = Wind(WindType.NAN)
XI = Wind(WindType.XI)
BEI = Wind(WindType.BEI)

THIRTEEN_WONDERS = {
    Suit(SuitType.CHARACTER, 1),
    Suit(SuitType.CHARACTER, 9),
    Suit(SuitType.DOT, 1),
    Suit(SuitType.DOT, 9),
    Suit(SuitType.BAMBOO, 1),
    Suit(SuitType.BAMBOO, 9),
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
