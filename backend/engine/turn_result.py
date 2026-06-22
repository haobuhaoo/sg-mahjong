from dataclasses import dataclass, field

from backend.domain.tiles import Tile


@dataclass
class DrawResult:
    """
    Result of the draw phase (Phase 1) of a player's turn.

    Attributes:
        drawn_tile: The non-bonus tile added to the player's hand, or None
            if the draw was interrupted (e.g. by Robbing the Eighth).
        drawn_bonus_tiles: Bonus tiles collected from the live wall during
            this draw phase, before replacements were drawn from the dead wall.
        robbed_by: Position of the player who robbed the drawn bonus tile
            (Robbing the Eighth), or None if no rob occurred.
        is_replacement: True if the final non-bonus tile came from the dead
            wall (due to bonus replacement or gang).
        is_last_tile: True if the draw consumed the last tile of the live wall.
    """

    drawn_tile: Tile | None
    drawn_bonus_tiles: list[Tile] = field(default_factory=list)
    robbed_by: int | None = None
    is_replacement: bool = False
    is_last_tile: bool = False


@dataclass
class AssessResult:
    """
    Result of the assess phase (Phase 2) of a player's turn.

    Aggregates all win conditions and action options available to the player after
    drawing. Flags event-based wins (Winning on Replacement Tile For Flower, Winning
    on Replacement Tile For Gang, Winning on the Last Available Tile, Earthly Hand) in
    addition to hand-pattern-based wins.

    Attributes:
        can_self_pick: The drawn tile completes a winning hand (Self-Pick).
        concealed_gang_tiles: Tiles that appear exactly 4 times in hand and can be
            declared as a Concealed gang.
        pong_upgrade_tiles: Tiles in hand that match an existing open pong meld and can
            be added to form an Exposed gang.
        has_flower_win: Player has all 8 Flower+Season tiles (Eight Immortals).
        win_on_replacement: Self-pick after drawing from the dead wall (Winning on Replacement
            Tile For Flower, Winning on Replacement Tile For Gang).
        win_on_last_tile: Self-pick on the last tile of the live wall and not a replacement
            draw (Winning on the Last Available Tile).
        is_heavenly_hand: Dealer's 14 dealt tiles already form a winning hand (Heavenly Hand).
        is_earthly_hand: Non-dealer self-picks on their first draw (Earthly Hand).
        robbing_gang_by: Position of the player who robbed this player's exposed gang declaration
            (Robbing the Gang), or None.
        is_eighteen_arhats: Player has performed 4 gangs and self-picks (Eighteen Arhats).
        is_fully_concealed: Player has no exposed melds (except concealed gangs) and
            self-picks (Fully Concealed Hand).
    """

    can_self_pick: bool = False
    concealed_gang_tiles: list[Tile] = field(default_factory=list)
    pong_upgrade_tiles: list[Tile] = field(default_factory=list)
    has_flower_win: bool = False
    win_on_replacement: bool = False
    win_on_last_tile: bool = False
    is_heavenly_hand: bool = False
    is_earthly_hand: bool = False
    robbing_gang_by: int | None = None
    is_eighteen_arhats: bool = False
    is_fully_concealed: bool = False

    @property
    def any_win(self) -> bool:
        """True if any win condition is met (hand-pattern, flower, or event-based)."""
        return (
            self.can_self_pick
            or self.has_flower_win
            or self.is_heavenly_hand
            or self.is_earthly_hand
            or self.robbing_gang_by is not None
        )

    @property
    def has_options(self) -> bool:
        """True if the player has any win or action available (win, concealed gang, gang upgrade)."""
        return (
            self.any_win
            or bool(self.concealed_gang_tiles)
            or bool(self.pong_upgrade_tiles)
        )


@dataclass
class TurnPhase:
    """
    Describes the current phase of a player's turn for the API layer.

    Attributes:
        phase: One of `"draw"`, `"assess"`, `"discard"`, `"react"`, or `"ended"`.
        draw_result: The result of the draw phase, if completed.
        assess_result: The result of the assess phase, if completed.
    """

    phase: str
    draw_result: DrawResult | None = None
    assess_result: AssessResult | None = None
