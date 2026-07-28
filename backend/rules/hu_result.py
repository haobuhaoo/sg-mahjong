from dataclasses import dataclass
from enum import Enum, auto


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
    PURE_TERMINALS = auto()
    MIXED_TERMINALS = auto()
    FULLY_CONCEALED = auto()
    SEQUENCE_HAND = auto()
    LESSER_SEQUENCE_HAND = auto()
    FULL_FLUSH = auto()
    HALF_FLUSH = auto()
    TRIPLETS_HAND = auto()
    CHICKEN_HAND = auto()


@dataclass(frozen=True)
class HuResult:
    """
    Result of running tile-level win detection on a hand.

    Attributes:
        is_winning: Whether the tile + hand + open melds form a winning hand.
        patterns: Set of hand patterns that apply to this hand. Multiple patterns can apply
            (e.g. Triplets Hand + Half Flush).
        conceal_hand: True when the winner holds a shortcut Three Great Scholars or Four Great
            Blessings (detected without Chicken Hand) and must conceal non-justifying hand tiles
            from other players. The API layer uses this to filter hand tiles in the serialized
            response.
    """

    is_winning: bool
    patterns: frozenset[HandPattern] = frozenset()
    conceal_hand: bool = False
