from dataclasses import dataclass, field
from enum import Enum, auto

from backend.domain.tiles import Tile
from backend.rules.hu_result import HuResult


@dataclass
class DrawResult:
    """
    Result of the draw phase (Phase 1) of a player's turn.

    Attributes:
        drawn_tile: The non-bonus tile added to the player's hand, or None if the draw was
            interrupted (e.g. by Robbing the Eighth).
        drawn_bonus_tiles: Bonus tiles collected from the live wall during this draw phase, before
            replacements were drawn from the dead wall.
        robbed_by: Position of the player who robbed the drawn bonus tile (Robbing the Eighth), or
            None if no rob occurred.
        is_replacement: True if the final non-bonus tile came from the dead wall (due to bonus
            replacement or gang).
        is_last_tile: True if the draw consumed the last tile of the live wall.
    """

    drawn_tile: Tile | None
    drawn_bonus_tiles: list[Tile] = field(default_factory=list)
    robbed_by: int | None = None
    is_replacement: bool = False
    is_last_tile: bool = False


class WinSource(Enum):
    """How the winning tile entered play."""

    SELF_PICK = auto()
    DISCARD = auto()


class WinEvent(Enum):
    """Game-context circumstances that add scoring bonuses on top of hand patterns."""

    HEAVENLY = auto()
    EARTHLY = auto()
    HUMANLY = auto()
    REPLACEMENT_TILE = auto()
    LAST_TILE = auto()
    ROBBING_GANG = auto()


@dataclass
class WinResult:
    """
    Describe a winning outcome during a player's assess or react phase.

    Attributes:
        hu: The tile-level hand-pattern analysis result.
        source: How the winning tile was acquired.
        winning_tile: The tile that completes the winning hand.
        winner: Seat position of the winning player.
        events: Bonus-scoring game-context circumstances.
    """

    hu: HuResult
    source: WinSource
    winning_tile: Tile
    winner: int
    events: frozenset[WinEvent] = frozenset()


@dataclass
class TurnActions:
    """
    Available non-win actions a player can take during their turn.

    Attributes:
        concealed_gang_tiles: Tiles that appear exactly 4 times in hand and can be declared as a
            concealed gang.
        pong_upgrade_tiles: Tiles in hand that match an existing open pong meld and can be added to
            form an exposed gang.
    """

    concealed_gang_tiles: list[Tile] = field(default_factory=list)
    pong_upgrade_tiles: list[Tile] = field(default_factory=list)


@dataclass
class AssessResult:
    """
    Result of the assess phase (Phase 2) of a player's turn, or a discard-reaction win check.

    Aggregate win outcomes (hand-pattern-based or flower-based) and available non-win actions.

    Attributes:
        win: The win outcome if a hand-pattern win is detected, or None. `win.winner` identifies the
            winning player; when `robbing_gang_by` is set, the win belongs to the robber, not the
            acting player.
        flower_win: True if the player has all 8 Flower+Season tiles (Eight Immortals).
        actions: Available non-win actions (concealed gang, exposed gang upgrade).
        robbing_gang_by: Position of the player who robbed the gang declarer's gang (Robbing the
            Gang), or None. When set, the gang was blocked and never executed.
    """

    win: WinResult | None = None
    flower_win: bool = False
    actions: TurnActions = field(default_factory=TurnActions)
    robbing_gang_by: int | None = None

    @property
    def any_win(self) -> bool:
        """True if any win condition is met (hand-pattern or flower)."""
        return self.win is not None or self.flower_win

    @property
    def has_options(self) -> bool:
        """True if the player has any win or action available (win, concealed gang, gang upgrade)."""
        return (
            self.any_win
            or bool(self.actions.concealed_gang_tiles)
            or bool(self.actions.pong_upgrade_tiles)
        )


@dataclass
class TurnPhase:
    """
    Describe the current phase of a player's turn for the API layer.

    Attributes:
        phase: One of `draw`, `assess`, `discard`, `react`, or `ended`.
        draw_result: The result of the draw phase, if completed.
        assess_result: The result of the assess phase, if completed.
    """

    phase: str
    draw_result: DrawResult | None = None
    assess_result: AssessResult | None = None
