import random
from collections.abc import Callable

from backend.domain.tiles import (
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
from backend.utils.helper import is_bonus_tile


class GameState:
    """
    Hold the shared mutable state of a game: the wall, the discard pile, the prevalent wind,
    whose turn it is, and the turn counter.

    Tile drawing is split into two directions:
      - Live wall (front): `draw_tile()` advances `_start_idx` forward
      - Dead wall (back): `replace_tile()` retreats `_end_idx` backward

    The dead wall is always the last 15 tiles, so the last live tile shifts down as tiles are
    consumed from the dead wall. The game ends in a draw when `is_live_wall_exhausted` becomes
    True.
    """

    MAX_PLAYERS = 3
    NUM_SEATS = 4
    TILES_PER_HAND = 13
    TILES_PER_BATCH = 4
    DEAD_WALL_SIZE = 15

    def __init__(self, num_players: int, prevalent_wind: WindType, all_tiles: list[Tile]):
        """
        Create a new game state.

        Player 1 (position 0) is always the starting player.

        Args:
            num_players: Number of players (0-3 valid)
            prevalent_wind: The prevalent wind for scoring
            all_tiles: Shuffled list of all tiles for the wall

        Raises:
            IndexError: If num_players is not in [0, 3]
        """
        if num_players < 0 or num_players > GameState.MAX_PLAYERS:
            raise IndexError(f"Number of players must be between 0 and {GameState.MAX_PLAYERS}")
        self.num_players = num_players
        self.all_tiles: list[Tile] = all_tiles
        self.discarded_tiles: list[Tile] = []
        self.prevalent_wind: WindType = prevalent_wind
        self.current_player = 0
        self.turn_count = 0

        # internals
        self._start_idx = GameState.NUM_SEATS * GameState.TILES_PER_HAND + 1
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
            f"GameState(num_players={self.num_players}, prevalent_wind={self.prevalent_wind}, "
            f"current_player={self.current_player}, all_tiles={self.all_tiles}, "
            f"discarded_tiles={self.discarded_tiles})"
        )

    @staticmethod
    def initialize_wall() -> list[Tile]:
        """
        Create the full, shuffled wall of tiles for a new game.

        Returns:
            A shuffled list containing all tiles used in the game.
        """
        all_tiles = []
        for _ in range(4):
            all_tiles.extend(GameState._create_suit_tiles())
            all_tiles.extend(GameState._create_honor_tiles())
        all_tiles.extend(GameState._create_bonus_tiles())

        random.shuffle(all_tiles)
        return all_tiles

    @staticmethod
    def _create_suit_tiles() -> list[Suit]:
        """Create one set of the three suits (1..9 for each suit type)."""
        return [Suit(suit, number) for suit in SuitType for number in range(1, 10)]

    @staticmethod
    def _create_honor_tiles() -> list[Honor]:
        """Create one set of honor tiles (winds and dragons)."""
        return [Wind(wind) for wind in WindType] + [Dragon(dragon) for dragon in DragonType]

    @staticmethod
    def _create_bonus_tiles() -> list[Bonus]:
        """Create bonus tiles (animals, flowers, seasons)."""
        return (
            [Animal(animal) for animal in AnimalType]
            + [Flower(flower) for flower in FlowerType]
            + [Season(season) for season in SeasonType]
        )

    @property
    def _last_live_tile_idx(self) -> int:
        """Index of the last drawable tile from the live wall (16th from the dead wall end)."""
        return len(self.all_tiles) + self._end_idx - GameState.DEAD_WALL_SIZE

    @property
    def remaining_live_tiles(self) -> int:
        """Number of tiles still available in the live wall (never negative)."""
        return max(0, self._last_live_tile_idx - self._start_idx + 1)

    @property
    def is_last_live_tile(self) -> bool:
        """True when the next `draw_tile()` will pull the last tile of the live wall."""
        return self.remaining_live_tiles == 1

    @property
    def is_live_wall_exhausted(self) -> bool:
        """True when no tiles remain in the live wall - game ends in a draw."""
        return self.remaining_live_tiles == 0

    def draw_tile(self) -> Tile:
        """Return the next tile from the live wall."""
        tile = self.all_tiles[self._start_idx]
        self._start_idx += 1
        return tile

    def replace_tile(self) -> Tile:
        """Return the next tile from the dead wall."""
        tile = self.all_tiles[self._end_idx]
        self._end_idx -= 1
        return tile

    def add_to_discard_pile(self, tile: Tile) -> None:
        """Append a tile to the discard pile."""
        self.discarded_tiles.append(tile)

    def advance_player(self, current_position: int) -> None:
        """Advance the turn to the next player in seating order."""
        self.current_player = (current_position + 1) % GameState.NUM_SEATS

    def advance_turn(self) -> None:
        """Increment the turn counter. Called after each discard + reaction completes."""
        self.turn_count += 1

    def get_starting_tile_indices(self, position: int) -> list[int]:
        """Return the wall indices for the starting hand of the given seat position."""
        batch_stride = GameState.NUM_SEATS * GameState.TILES_PER_BATCH
        indices = [
            position * GameState.TILES_PER_BATCH + i * batch_stride + j
            for i in range(3)
            for j in range(GameState.TILES_PER_BATCH)
        ]
        indices.append(3 * batch_stride + position)

        if position == 0:
            indices.append(3 * batch_stride + GameState.NUM_SEATS)
        return indices

    def split_starting_tiles(self, indices: list[int]) -> tuple[list[Tile], list[Bonus]]:
        """Split tiles at the given wall indices into hand tiles and bonus tiles."""
        starting_hand: list[Tile] = []
        bonus_tiles: list[Bonus] = []

        for idx in indices:
            tile = self.all_tiles[idx]
            if is_bonus_tile(tile):
                bonus_tiles.append(tile)
            else:
                starting_hand.append(tile)

        return starting_hand, bonus_tiles

    def draw_until_non_bonus(
        self, collector: Callable[[Tile], bool], is_gang: bool = False
    ) -> Tile:
        """
        Draw (or replace) tiles until a non-bonus tile is returned.

        If a bonus tile is drawn, it is passed to `collector(tile)` and a replacement tile is drawn
        from the dead wall.

        Args:
            collector: Callable that accepts a bonus tile (e.g. player.check_bonus_tile)
            is_gang: If True, draw from the dead wall instead of the live wall

        Returns:
            The first non-bonus tile drawn
        """
        tile = self.draw_tile() if not is_gang else self.replace_tile()
        while collector(tile):
            tile = self.replace_tile()

        return tile
