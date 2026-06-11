from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import Suit, Tile
from backend.utils.helper import is_bonus_tile


class RoundEngine:
    """
    Orchestrates the flow of a round: dealing, drawing, discarding,
    and executing melds (chi / pong / gang).

    All mutable game state is owned by the injected ``GameState``. This class
    contains only the behavioural logic that acts on that state.
    """

    def __init__(self, state: GameState):
        self.state = state

    # deal
    def deal_starting_tiles(self, player: Player) -> None:
        """Deal the starting hand and handle any bonus tile replacements for player."""
        indices = self.state.get_starting_tile_indices(player.get_position())
        starting_hand, bonus_tiles = self.state.split_starting_tiles(indices)
        replaced, all_bonus = self._replace_bonus_tiles(bonus_tiles)
        player.add_to_hand(starting_hand + replaced)
        player.add_bonus_tile(all_bonus)

    # draw or discard
    def player_draw_tile(self, player: Player, is_gang: bool = False) -> None:
        """
        Give a drawn (or replacement) non-bonus tile to the player.

        If ``is_gang`` is True, a replacement tile is drawn from the dead wall.
        """
        tile = self.state.draw_until_non_bonus(player.check_bonus_tile, is_gang)
        player.receive_tile(tile)

    def player_discard_tile(self, player: Player, idx: int) -> Tile:
        """Make the player discard the tile at ``idx`` from their hand."""
        return player.discard_tile(idx)

    def add_to_discard_pile(self, tile: Tile, player: Player) -> None:
        """Append the tile to the discard pile and advance to the next player."""
        self.state.add_to_discard_pile(tile)
        self.state.advance_player(player.position)

    # melds
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

    def gang_tile(self, player: Player, tile: Tile) -> Tile:
        """Execute a gang for player, draw the replacement tile, and return discard."""
        self.execute_gang(player, tile)
        self.player_draw_tile(player, is_gang=True)
        return self._discard_after_meld(player)

    def execute_gang(self, player: Player, tile: Tile) -> None:
        """Perform the gang action and update tai based on the claimed tile."""
        player.gang_tile(tile)
        player.update_tai(tile, self.state.prevalent_wind)

    # private methods
    def _discard_after_meld(self, player: Player) -> Tile:
        """After a meld, choose and perform the player's discard."""
        tile_idx = player.pick_tile_to_discard()
        return self.player_discard_tile(player, tile_idx)

    def _replace_bonus_tiles(self, tiles: list[Tile]) -> tuple[list[Tile], list[Tile]]:
        """
        Replace initial bonus tiles by drawing replacement tiles from the dead wall.

        Returns:
            A tuple ``(replacement_tiles, all_bonus_tiles)`` where
            ``replacement_tiles`` are non-bonus tiles to add to the player's hand and
            ``all_bonus_tiles`` is the complete list of bonus tiles collected.
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
