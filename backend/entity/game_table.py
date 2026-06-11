import random

from backend.entity.player import Player
from backend.utility.helper import is_bonus_tile

from .tiles import (
    Animal,
    AnimalType,
    Bonus,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
    Honor,
    Season,
    SeasonType,
    Suit,
    SuitType,
    Tile,
    Wind,
    WindType,
)

MAX_PLAYERS = 3


class GameTable:
    def __init__(
        self, num_players: int, prevalent_wind: WindType, all_tiles: list[Tile]
    ):
        """
        Create a new game table.

        Player 1 (position 0) is always the starting player.

        Args:
            num_players: Number of players (0-3 valid)
            prevalent_wind: The prevalent wind for scoring
            all_tiles: Shuffled list of all tiles for the wall

        Raises:
            IndexError: If num_players is not in [0, 3]
        """
        if num_players < 0 or num_players > MAX_PLAYERS:
            raise IndexError("Number of players must be between 0 and 3")
        self.num_players = num_players
        self.all_tiles: list[Tile] = all_tiles
        self.discarded_tiles: list[Tile] = []
        self.prevalent_wind: WindType = prevalent_wind
        self.current_player = 0

        # internals
        self._start_idx = 3 * 16 + 4 + 1
        self._end_idx = -1

    def __str__(self):
        return (
            f"Prevalent wind: {self.prevalent_wind.value}"
            f"\nCurrent player: Player {self.current_player + 1}"
            + "\nDiscard pile: "
            + ", ".join([str(t) for t in self.discarded_tiles])
        )

    def __repr__(self):
        return (
            f"GameTable(num_players={self.num_players}, prevalent_wind={self.prevalent_wind}, "
            f"current_player={self.current_player}, all_tiles={self.all_tiles}, "
            f"discarded_tiles={self.discarded_tiles})"
        )

    @staticmethod
    def initialize_table() -> list[Tile]:
        """Create the full, shuffled wall of tiles for a new game.

        Returns:
            A shuffled list containing all tiles used in the game.
        """
        all_tiles = []
        for _ in range(4):
            all_tiles.extend(GameTable._create_suit_tiles())
            all_tiles.extend(GameTable._create_honor_tiles())
        all_tiles.extend(GameTable._create_bonus_tiles())

        random.shuffle(all_tiles)
        return all_tiles

    @staticmethod
    def _create_suit_tiles() -> list[Suit]:
        """Create one set of the three suits (1..9 for each suit type)."""
        return [Suit(suit, number) for suit in SuitType for number in range(1, 10)]

    @staticmethod
    def _create_honor_tiles() -> list[Honor]:
        """Create one set of honor tiles (winds and dragons)."""
        return [Wind(wind) for wind in WindType] + [
            Dragon(dragon) for dragon in DragonType
        ]

    @staticmethod
    def _create_bonus_tiles() -> list[Bonus]:
        """Create bonus tiles (animals, flowers, seasons)."""
        return (
            [Animal(animal) for animal in AnimalType]
            + [Flower(flower) for flower in FlowerType]
            + [Season(season) for season in SeasonType]
        )

    def deal_starting_tiles(self, player: Player) -> None:
        """Deal the starting hand and handle any bonus tile replacements for player."""
        starting_hand, bonus_tiles = self._fetch_starting_hand(player)
        replaced, bonus = self._replace_bonus_tile(bonus_tiles)
        self._assign_to_player(player, starting_hand + replaced, bonus)

    def draw_tile(self) -> Tile:
        """Draw the next tile from the live wall (front)."""
        tile = self.all_tiles[self._start_idx]
        self._start_idx += 1
        return tile

    def replace_tile(self) -> Tile:
        """Draw a tile from the dead wall (back)."""
        tile = self.all_tiles[self._end_idx]
        self._end_idx -= 1
        return tile

    def player_draw_tile(self, player: Player, is_gang: bool = False) -> None:
        """
        Give a drawn (or replacement) non-bonus tile to player.

        If is_gang is True, a replacement tile is used instead of drawing from front.
        """
        tile = self._draw_until_non_bonus_tile(player, is_gang)
        player.receive_tile(tile)

    def player_discard_tile(self, player: Player, idx: int) -> Tile:
        """Make player discard the tile at idx from their hand."""
        return player.discard_tile(idx)

    def add_to_discard_tile(self, tile: Tile, player: Player) -> None:
        """Append tile to the discard pile and advance to the next player."""
        self.discarded_tiles.append(tile)
        self._advance_player(player)

    def chi_tile(self, player: Player, tile: Suit) -> Tile:
        """Execute a chi for player on tile and return the automatic discard by player."""
        self.execute_chi(player, tile)
        return self.discard_after_meld(player)

    def execute_chi(self, player: Player, tile: Suit) -> None:
        """Perform the chi action."""
        player.chi_tile(tile)

    def pong_tile(self, player: Player, tile: Tile) -> Tile:
        """Execute a pong for player and return the automatic discard by player."""
        self.execute_pong(player, tile)
        return self.discard_after_meld(player)

    def execute_pong(self, player: Player, tile: Tile) -> None:
        """Perform the pong action and update tai based on the claimed tile."""
        player.pong_tile(tile)
        player.update_tai(tile, self.prevalent_wind)

    def gang_tile(self, player: Player, tile: Tile) -> Tile:
        """Execute a gang for player, draw the replacement tile, and return discard by player."""
        self.execute_gang(player, tile)
        self.player_draw_tile(player, True)
        return self.discard_after_meld(player)

    def execute_gang(self, player: Player, tile: Tile) -> None:
        """Perform the gang action and update tai based on the claimed tile."""
        player.gang_tile(tile)
        player.update_tai(tile, self.prevalent_wind)

    def discard_after_meld(self, player: Player) -> Tile:
        """After a meld, choose and perform the player's discard."""
        tile_idx = player.pick_tile_to_discard()
        return self.player_discard_tile(player, tile_idx)

    # private methods
    def _fetch_starting_hand(self, player: Player) -> tuple[list[Tile], list[Bonus]]:
        """Fetch starting hand tiles and any initial bonus tiles for player."""
        return self._split_tiles(self._starting_tile_indices(player.get_position()))

    def _starting_tile_indices(self, position: int) -> list[int]:
        """Return the indices into the wall for the starting hand of position."""
        indices = [position * 4 + i * 16 + j for i in range(3) for j in range(4)]
        indices.append(3 * 16 + position)
        if position == 0:
            indices.append(3 * 16 + 4)
        return indices

    def _split_tiles(self, indices: list[int]) -> tuple[list[Tile], list[Bonus]]:
        """Split tiles at indices into non-bonus starting hand and bonus tiles."""
        starting_hand: list[Tile] = []
        bonus_tiles: list[Bonus] = []
        for idx in indices:
            tile = self.all_tiles[idx]
            if is_bonus_tile(tile):
                bonus_tiles.append(tile)
            else:
                starting_hand.append(tile)
        return starting_hand, bonus_tiles

    def _replace_bonus_tile(self, tiles: list[Bonus]) -> tuple[list[Tile], list[Bonus]]:
        """
        Replace initial bonus tiles by drawing replacement tiles from the dead wall.

        Returns:
            a tuple (replacement_tiles, all_bonus_tiles):
                replacement_tiles are non-bonus tiles to add to the player's hand and
                all_bonus_tiles is the complete list of bonus tiles collected during replacement
        """
        if len(tiles) == 0:
            return ([], [])

        replacement_tiles: list[Tile] = []
        bonus_tiles: list[Bonus] = tiles.copy()
        pending_bonus = tiles.copy()

        while pending_bonus:
            pending_bonus.pop(0)
            tile = self.replace_tile()
            while is_bonus_tile(tile):
                bonus_tiles.append(tile)
                pending_bonus.append(tile)
                tile = self.replace_tile()
            replacement_tiles.append(tile)

        return replacement_tiles, bonus_tiles

    def _assign_to_player(
        self, player: Player, hand_tiles: list[Tile], bonus_tiles: list[Bonus]
    ) -> None:
        """Assign starting hand and bonus tiles to player."""
        player.add_to_hand(hand_tiles)
        player.add_bonus_tile(bonus_tiles)

    def _advance_player(self, player: Player) -> None:
        """Advance the turn to the next player in seating order."""
        self.current_player = (player.position + 1) % 4

    def _draw_until_non_bonus_tile(self, player: Player, is_gang: bool) -> Tile:
        """
        Draw (or replace) tiles until a non-bonus tile is returned.

        If a bonus tile is drawn, it is given to the player and a replacement is drawn.
        """
        tile = self.draw_tile() if not is_gang else self.replace_tile()
        while player.check_bonus_tile(tile):
            tile = self.replace_tile()

        return tile
