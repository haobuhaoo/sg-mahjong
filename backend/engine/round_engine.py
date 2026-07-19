from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import Flower, Season, Suit, Tile
from backend.engine.turn_result import (
    AssessResult,
    DrawResult,
    TurnActions,
    WinEvent,
    WinResult,
    WinSource,
)
from backend.rules.hu import can_hu
from backend.rules.hu_result import HandPattern
from backend.utils.errors import InvalidActionError
from backend.utils.helper import is_bonus_tile


class RoundEngine:
    """
    Orchestrates the flow of a round following the `Draw → Assess → Act → Discard`
    turn structure.

    Each player's turn proceeds through four phases:
      1. **Draw** — draw a tile from the live wall, recursively replacing bonus tiles.
      2. **Assess** — check for wins (self-pick, flower win, event-based wins) and
         available actions (concealed gang, exposed gang upgrade).
      3. **Act** — player chooses to self-pick, declare a gang, or proceed.
      4. **Discard** — player discards; other players may intercept (hu/gang/pong/chi).

    All mutable game state is owned by the injected `GameState`. This class
    contains only the behavioural logic that acts on that state.
    """

    def __init__(self, state: GameState):
        """Create a round engine that operates on the given game state."""
        self.state = state

    # Setup

    def deal_starting_tiles(self, player: Player) -> None:
        """Deal the starting hand and handle any bonus tile replacements for player."""
        indices = self.state.get_starting_tile_indices(player.get_position())
        starting_hand, bonus_tiles = self.state.split_starting_tiles(indices)
        replaced, all_bonus = self._replace_bonus_tiles(bonus_tiles)
        player.add_to_hand(starting_hand + replaced)
        player.add_bonus_tile(all_bonus)

    def check_heavenly_hand(self, player: Player) -> AssessResult:
        """
        Check if the dealer has a winning hand immediately after dealing and bonus
        replacement (Heavenly Hand). Only valid for position 0 with 14 tiles.

        Iterates over each tile in the dealer's 14-tile hand, removes it, and
        checks whether the remaining 13 + that tile form a winning hand.
        """
        if player.position != 0 or len(player.hand_tile) != 14:
            return AssessResult()
        for i in range(len(player.hand_tile)):
            tile = player.hand_tile[i]
            remaining = player.hand_tile[:i] + player.hand_tile[i + 1 :]
            hu_result = can_hu(
                remaining,
                player.open_tile,
                tile,
                seat_wind=player.seat_wind,
                prevalent_wind=self.state.prevalent_wind,
                bonus_count=len(player.bonus_tile),
            )
            if hu_result.is_winning:
                return AssessResult(
                    win=WinResult(
                        hu=hu_result,
                        source=WinSource.SELF_PICK,
                        winning_tile=tile,
                        winner=player.position,
                        events=frozenset({WinEvent.HEAVENLY}),
                    ),
                    actions=TurnActions(
                        concealed_gang_tiles=player.find_concealed_gang_tiles(),
                        pong_upgrade_tiles=player.find_pong_upgrade_tiles(),
                    ),
                )
        return AssessResult()

    # Phase 1: Draw

    def player_draw_tile(
        self, player: Player, players: list[Player], is_gang: bool = False
    ) -> DrawResult:
        """
        Phase 1: Draw.

        Pulls a tile from the live wall (or dead wall if `is_gang`), recursively
        replacing bonus tiles. Returns a `DrawResult` so the API can surface what
        was drawn.

        If another player has 7 Flower+Season tiles and this draw yields the 8th bonus
        tile, that player robs it (Robbing the Eighth) and `DrawResult.robbed_by` is set.

        Args:
            player: The player whose turn it is.
            players: All players in the game (needed for Robbing the Eighth detection).
            is_gang: If True, draw the initial tile from the dead wall
                (used after a gang declaration).
        """
        player.drawn_tile = None
        player.drawn_bonus_tiles = []

        is_last = not is_gang and self.state.is_last_live_tile
        had_bonus = False
        robbed: Player | None = None

        def collector_with_rob(tile: Tile) -> bool:
            """
            Bonus-tile callback for `draw_until_non_bonus` that intercepts
            Robbing the Eighth before the drawing player collects the tile.

            For each bonus tile drawn:
            1. If the tile is a Flower or Season and any other player already
               has 7 Flower+Season tiles, the tile is robbed — `robbed` is set
               and the loop stops. Animals are never robbed.
            2. Otherwise, the tile is collected normally by the drawing player
               via `player.check_bonus_tile` and `had_bonus` is flagged.

            Returns:
                True if the tile was collected and another replacement should
                be drawn from the dead wall; False to stop the loop.
            """
            nonlocal had_bonus, robbed
            if not is_bonus_tile(tile):
                return False
            if isinstance(tile, (Flower, Season)):
                for p in players:
                    if p is not player and p.count_flower_season_tiles() == 7:
                        robbed = p
                        return False
            had_bonus = True
            return player.check_bonus_tile(tile)

        tile = self.state.draw_until_non_bonus(collector_with_rob, is_gang)

        if robbed is not None:
            robbed.add_bonus_tile([tile])
            return DrawResult(
                drawn_tile=None,
                drawn_bonus_tiles=list(player.drawn_bonus_tiles),
                robbed_by=robbed.position,
                is_replacement=False,
                is_last_tile=is_last,
            )

        player.receive_tile(tile)
        return DrawResult(
            drawn_tile=tile,
            drawn_bonus_tiles=list(player.drawn_bonus_tiles),
            is_replacement=had_bonus or is_gang,
            is_last_tile=is_last,
        )

    # Phase 2: Assess

    def player_assess_hand(
        self,
        player: Player,
        is_replacement: bool = False,
        is_last_tile: bool = False,
        is_first_draw: bool = False,
    ) -> AssessResult:
        """
        Phase 2: Assess.

        After drawing, checks all win conditions and available actions (concealed gang,
        exposed gang upgrade).

        Accepts draw-context flags (from `DrawResult`) to detect event-based wins:
        - Winning on Replacement Tile (`is_replacement`)
        - Winning on the Last Available Tile (`is_last_tile` without `is_replacement`)
        - Earthly Hand (`is_first_draw` for non-dealer).

        Args:
            player: The player whose hand is being assessed.
            is_replacement: The drawn tile came from the dead wall.
            is_last_tile: The draw consumed the last live wall tile.
            is_first_draw: This is the player's first draw of the game.
        """
        actions = TurnActions(
            concealed_gang_tiles=player.find_concealed_gang_tiles(),
            pong_upgrade_tiles=player.find_pong_upgrade_tiles(),
        )

        if player.count_flower_season_tiles() == 8:
            return AssessResult(flower_win=True, actions=actions)

        tile = player.drawn_tile
        if tile is not None:
            hu_result = can_hu(
                self._hand_without_drawn_tile(player),
                player.open_tile,
                tile,
                seat_wind=player.seat_wind,
                prevalent_wind=self.state.prevalent_wind,
                bonus_count=len(player.bonus_tile),
            )
            if hu_result.is_winning:
                events: set[WinEvent] = set()
                if is_replacement:
                    events.add(WinEvent.REPLACEMENT_TILE)
                if is_last_tile and not is_replacement:
                    events.add(WinEvent.LAST_TILE)
                if is_first_draw and player.position != 0:
                    events.add(WinEvent.EARTHLY)
                return AssessResult(
                    win=WinResult(
                        hu=hu_result,
                        source=WinSource.SELF_PICK,
                        winning_tile=tile,
                        winner=player.position,
                        events=frozenset(events),
                    ),
                    actions=actions,
                )

        return AssessResult(actions=actions)

    # Phase 2a: Self-pick win

    def player_self_pick(self, player: Player) -> Tile:
        """
        Player declares self-pick win (Self-Pick).

        Returns the winning tile.

        Raises:
            InvalidActionError: If the player cannot hu with the drawn tile
        """
        tile = player.drawn_tile
        if tile is None:
            raise InvalidActionError(
                "No drawn tile to self-pick with", "self-pick", tile
            )
        hand_without_tile = self._hand_without_drawn_tile(player)
        if not can_hu(
            hand_without_tile,
            player.open_tile,
            tile,
            seat_wind=player.seat_wind,
            prevalent_wind=self.state.prevalent_wind,
            bonus_count=len(player.bonus_tile),
        ).is_winning:
            raise InvalidActionError(f"Cannot self-pick with {tile}", "self-pick", tile)
        return tile

    # Phase 2b: Concealed gang

    def declare_concealed_gang(
        self, player: Player, tile: Tile, players: list[Player]
    ) -> DrawResult | AssessResult:
        """
        Player declares a Concealed gang. Consumes 4 identical tiles from hand, draws
        a replacement, and returns the draw result.

        Before executing, checks if any other player can rob the concealed gang —
        only allowed when the robber is waiting for the tile to complete Thirteen
        Wonders (Robbing the Gang special condition).

        Caller should re-run assess after this (the replacement could win).
        """
        for p in players:
            if p is not player:
                hu_result = can_hu(
                    p.hand_tile,
                    p.open_tile,
                    tile,
                    seat_wind=p.seat_wind,
                    prevalent_wind=self.state.prevalent_wind,
                    bonus_count=len(p.bonus_tile),
                )
                if (
                    hu_result.is_winning
                    and HandPattern.THIRTEEN_WONDERS in hu_result.patterns
                ):
                    return AssessResult(
                        robbing_gang_by=p.position,
                        win=WinResult(
                            hu=hu_result,
                            source=WinSource.DISCARD,
                            winning_tile=tile,
                            winner=p.position,
                            events=frozenset({WinEvent.ROBBING_GANG}),
                        ),
                    )

        player.make_concealed_gang(tile)
        player.update_tai(tile, self.state.prevalent_wind)
        return self.player_draw_tile(player, players, is_gang=True)

    # Phase 2c: Exposed gang (pong upgrade)

    def declare_exposed_gang(
        self, player: Player, tile: Tile, players: list[Player]
    ) -> AssessResult | DrawResult:
        """
        Player upgrades an open pong to an exposed gang by adding a matching
        hand tile. Before executing, checks if any other player can rob the
        gang.

        If no one robs, returns a `DrawResult` for the replacement draw.
        Caller should re-run assess after this.
        """
        for p in players:
            if p is not player:
                hu_result = can_hu(
                    p.hand_tile,
                    p.open_tile,
                    tile,
                    seat_wind=p.seat_wind,
                    prevalent_wind=self.state.prevalent_wind,
                    bonus_count=len(p.bonus_tile),
                )
                if hu_result.is_winning:
                    return AssessResult(
                        robbing_gang_by=p.position,
                        win=WinResult(
                            hu=hu_result,
                            source=WinSource.DISCARD,
                            winning_tile=tile,
                            winner=p.position,
                            events=frozenset({WinEvent.ROBBING_GANG}),
                        ),
                    )

        player.make_exposed_gang(tile)
        player.update_tai(tile, self.state.prevalent_wind)
        return self.player_draw_tile(player, players, is_gang=True)

    # Phase 3: Discard

    def player_discard_tile(self, player: Player, idx: int) -> Tile:
        """Make the player discard the tile at `idx` from their hand."""
        return player.discard_tile(idx)

    def finalize_discard(self, tile: Tile, player: Player) -> None:
        """Append the tile to the discard pile, advance to the next player,
        and increment the turn counter."""
        self.state.add_to_discard_pile(tile)
        self.state.advance_player(player.position)
        self.state.advance_turn()

    # Phase 4: React (meld claims on discard)

    def chi_tile(self, player: Player, tile: Suit) -> Tile:
        """Execute a chi for player on tile and return the automatic discard."""
        self.execute_chi(player, tile)
        return self._discard_after_meld(player)

    def execute_chi(self, player: Player, tile: Suit) -> None:
        """Perform the chi action."""
        player.chi_tile(tile)

    def pong_tile(self, player: Player, tile: Tile) -> Tile:
        """Execute a pong for player and return the automatic discard."""
        self.execute_pong(player, tile)
        return self._discard_after_meld(player)

    def execute_pong(self, player: Player, tile: Tile) -> None:
        """Perform the pong action and update tai based on the claimed tile."""
        player.pong_tile(tile)
        player.update_tai(tile, self.state.prevalent_wind)

    def gang_tile(self, player: Player, tile: Tile, players: list[Player]) -> Tile:
        """
        Execute a gang (from discard claim) for player, draw the replacement
        tile from the dead wall, and return the automatic discard.
        """
        self.execute_gang(player, tile)
        self.player_draw_tile(player, players, is_gang=True)
        return self._discard_after_meld(player)

    def execute_gang(self, player: Player, tile: Tile) -> None:
        """Perform the gang action and update tai based on the claimed tile."""
        player.gang_tile(tile)
        player.update_tai(tile, self.state.prevalent_wind)

    # Phase 4: Special discard-triggered wins

    def check_earthly_hand_discard(
        self, tile: Tile, non_dealers: list[Player]
    ) -> AssessResult:
        """
        After the dealer's first discard, check non-dealers for Earthly Hand.

        Returns an AssessResult with the win if a non-dealer qualifies,
        or an empty AssessResult.
        """
        if self.state.turn_count != 0:
            return AssessResult()
        for p in non_dealers:
            hu_result = can_hu(
                p.hand_tile,
                p.open_tile,
                tile,
                seat_wind=p.seat_wind,
                prevalent_wind=self.state.prevalent_wind,
                bonus_count=len(p.bonus_tile),
            )
            if hu_result.is_winning:
                return AssessResult(
                    win=WinResult(
                        hu=hu_result,
                        source=WinSource.DISCARD,
                        winning_tile=tile,
                        winner=p.position,
                        events=frozenset({WinEvent.EARTHLY}),
                    )
                )
        return AssessResult()

    def check_humanly_hand(
        self, tile: Tile, claimant: Player, all_players: list[Player]
    ) -> AssessResult:
        """
        Check if a non-dealer qualifies for Humanly Hand on a discard:
        - First go-around (within first 4 turns)
        - Claimant has not yet drawn a tile
        - No player has any exposed meld

        Returns an AssessResult with the win if the claimant qualifies,
        or an empty AssessResult.
        """
        if self.state.turn_count >= 4:
            return AssessResult()
        if claimant.drawn_tile is not None:
            return AssessResult()
        if any(p.open_tile for p in all_players):
            return AssessResult()
        hu_result = can_hu(
            claimant.hand_tile,
            claimant.open_tile,
            tile,
            seat_wind=claimant.seat_wind,
            prevalent_wind=self.state.prevalent_wind,
            bonus_count=len(claimant.bonus_tile),
        )
        if hu_result.is_winning:
            return AssessResult(
                win=WinResult(
                    hu=hu_result,
                    source=WinSource.DISCARD,
                    winning_tile=tile,
                    winner=claimant.position,
                    events=frozenset({WinEvent.HUMANLY}),
                )
            )
        return AssessResult()

    # Private methods

    def _hand_without_drawn_tile(self, player: Player) -> list[Tile]:
        """Return a copy of the player's hand with the drawn tile removed."""
        hand_without_tile = list(player.hand_tile)
        if player.drawn_tile in hand_without_tile:
            hand_without_tile.remove(player.drawn_tile)
        return hand_without_tile

    def _discard_after_meld(self, player: Player) -> Tile:
        """After a meld, choose and perform the player's discard."""
        tile_idx = player.pick_tile_to_discard()
        return self.player_discard_tile(player, tile_idx)

    def _replace_bonus_tiles(self, tiles: list[Tile]) -> tuple[list[Tile], list[Tile]]:
        """
        Replace initial bonus tiles by drawing replacement tiles from the dead wall.

        Returns:
            A tuple `(replacement_tiles, all_bonus_tiles)` where `replacement_tiles`
            are non-bonus tiles to add to the player's hand and `all_bonus_tiles` is
            the complete list of bonus tiles collected.
        """
        if not tiles:
            return [], []

        replacement_tiles: list[Tile] = []
        bonus_tiles: list[Tile] = list(tiles)
        pending_bonus = list(tiles)

        while pending_bonus:
            pending_bonus.pop(0)
            tile = self.state.replace_tile()
            while is_bonus_tile(tile):
                bonus_tiles.append(tile)
                pending_bonus.append(tile)
                tile = self.state.replace_tile()
            replacement_tiles.append(tile)

        return replacement_tiles, bonus_tiles
