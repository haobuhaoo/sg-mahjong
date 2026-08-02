from dataclasses import dataclass

from backend.rules.hand_patterns import HandPattern


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
