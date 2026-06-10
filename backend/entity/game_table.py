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
        if num_players < 0 or num_players > MAX_PLAYERS:
            raise ValueError("Number of players must be between 0 and 3")
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
        all_tiles = []
        for _ in range(4):
            all_tiles.extend(GameTable._create_suit_tiles())
            all_tiles.extend(GameTable._create_honor_tiles())
        all_tiles.extend(GameTable._create_bonus_tiles())

        random.shuffle(all_tiles)
        return all_tiles

    @staticmethod
    def _create_suit_tiles() -> list[Suit]:
        return [Suit(suit, number) for suit in SuitType for number in range(1, 10)]

    @staticmethod
    def _create_honor_tiles() -> list[Honor]:
        return [Wind(wind) for wind in WindType] + [
            Dragon(dragon) for dragon in DragonType
        ]

    @staticmethod
    def _create_bonus_tiles() -> list[Bonus]:
        return (
            [Animal(animal) for animal in AnimalType]
            + [Flower(flower) for flower in FlowerType]
            + [Season(season) for season in SeasonType]
        )

    def deal_starting_tiles(self, player: Player) -> None:
        starting_hand, bonus_tiles = self._fetch_starting_hand(player)
        replaced, bonus = self._replace_bonus_tile(bonus_tiles)
        self._assign_to_player(player, starting_hand + replaced, bonus)

    def draw_tile(self) -> Tile:
        tile = self.all_tiles[self._start_idx]
        self._start_idx += 1
        return tile

    def replace_tile(self) -> Tile:
        tile = self.all_tiles[self._end_idx]
        self._end_idx -= 1
        return tile

    def player_draw_tile(self, player: Player, is_gang: bool = False) -> None:
        tile = self._draw_until_non_bonus_tile(player, is_gang)
        player.receive_tile(tile)

    def player_discard_tile(self, player: Player, idx: int) -> Tile:
        return player.discard_tile(idx)

    def add_to_discard_tile(self, tile: Tile, player: Player) -> None:
        self.discarded_tiles.append(tile)
        self._advance_player(player)

    def chi_tile(self, player: Player, tile: Suit) -> Tile:
        self.execute_chi(player, tile)
        return self.discard_after_meld(player)

    def execute_chi(self, player: Player, tile: Suit) -> None:
        player.chi_tile(tile)

    def pong_tile(self, player: Player, tile: Tile) -> Tile:
        self.execute_pong(player, tile)
        return self.discard_after_meld(player)

    def execute_pong(self, player: Player, tile: Tile) -> None:
        player.pong_tile(tile)
        player.update_tai(tile, self.prevalent_wind)

    def gang_tile(self, player: Player, tile: Tile) -> Tile:
        self.execute_gang(player, tile)
        self.player_draw_tile(player, True)
        return self.discard_after_meld(player)

    def execute_gang(self, player: Player, tile: Tile) -> None:
        player.gang_tile(tile)
        player.update_tai(tile, self.prevalent_wind)

    def discard_after_meld(self, player: Player) -> Tile:
        tile_idx = player.pick_tile_to_discard()
        return self.player_discard_tile(player, tile_idx)

    # private methods
    def _fetch_starting_hand(self, player: Player) -> tuple[list[Tile], list[Bonus]]:
        return self._split_tiles(self._starting_tile_indices(player.get_position()))

    def _starting_tile_indices(self, position: int) -> list[int]:
        indices = [position * 4 + i * 16 + j for i in range(3) for j in range(4)]
        indices.append(3 * 16 + position)
        if position == 0:
            indices.append(3 * 16 + 4)
        return indices

    def _split_tiles(self, indices: list[int]) -> tuple[list[Tile], list[Bonus]]:
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
        player.add_to_hand(hand_tiles)
        player.add_bonus_tile(bonus_tiles)

    def _advance_player(self, player: Player) -> None:
        self.current_player = (player.position + 1) % 4

    def _draw_until_non_bonus_tile(self, player: Player, is_gang: bool) -> Tile:
        tile = self.draw_tile() if not is_gang else self.replace_tile()
        while player.check_bonus_tile(tile):
            tile = self.replace_tile()

        return tile
