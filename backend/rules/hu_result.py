from dataclasses import dataclass
from enum import Enum, auto


class HandPattern(Enum):
    """Tile-structure-based winning hand patterns."""

    THIRTEEN_WONDERS = auto()
    THREE_GREAT_SCHOLARS = auto()
    FOUR_GREAT_BLESSINGS = auto()
    EIGHTEEN_ARHATS = auto()
    FULLY_CONCEALED = auto()
    CHICKEN_HAND = auto()
    TRIPLETS_HAND = auto()
    HALF_FLUSH = auto()
    FULL_FLUSH = auto()
    ALL_HONOUR = auto()
    MIXED_TERMINALS = auto()
    PURE_TERMINALS = auto()
    SEQUENCE_HAND = auto()
    THREE_LESSER_SCHOLARS = auto()
    FOUR_LESSER_BLESSINGS = auto()


@dataclass(frozen=True)
class HuResult:
    """Result of running tile-level win detection on a hand.

    Attributes:
        is_winning: Whether the tile + hand + open melds form a winning hand.
        patterns: Set of hand patterns that apply to this hand. Multiple
            patterns can apply (e.g. Triplets Hand + Half Flush).
    """

    is_winning: bool
    patterns: frozenset[HandPattern] = frozenset()
