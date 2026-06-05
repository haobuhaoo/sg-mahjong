import random

from backend.entity.player import Player

from .tiles import (
    Animal,
    AnimalType,
    Bonus,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
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
        self.start_idx = 3 * 16 + 4 + 1
        self.end_idx = -1
        self.prevalent_wind: WindType = prevalent_wind
        self.current_player = 0

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
    def initialize_table():
        all_tiles = []
        for _ in range(4):
            all_tiles.extend(GameTable._create_suit_tiles())
            all_tiles.extend(GameTable._create_honor_tiles())
        all_tiles.extend(GameTable._create_bonus_tiles())

        random.shuffle(all_tiles)
        return all_tiles

    @staticmethod
    def _create_suit_tiles():
        return [Suit(suit, number) for suit in SuitType for number in range(1, 10)]

    @staticmethod
    def _create_honor_tiles():
        return [Wind(wind) for wind in WindType] + [
            Dragon(dragon) for dragon in DragonType
        ]

    @staticmethod
    def _create_bonus_tiles():
        return (
            [Animal(animal) for animal in AnimalType]
            + [Flower(flower) for flower in FlowerType]
            + [Season(season) for season in SeasonType]
        )

    def deal_starting_tiles(self, player: Player):
        starting_hand, bonus_tiles = self._split_tiles(
            self._starting_tile_indices(player.get_position())
        )
        replaced, bonus = self._replace_bonus_tile(bonus_tiles)
        player.add_to_hand(starting_hand + replaced)
        player.add_bonus_tile(bonus)

    def draw_tile(self):
        tile = self.all_tiles[self.start_idx]
        self.start_idx += 1
        return tile

    def replace_tile(self):
        tile = self.all_tiles[self.end_idx]
        self.end_idx -= 1
        return tile

    def is_bonus_tile(self, tile: Tile):
        return isinstance(tile, Bonus)

    def player_draw_tile(self, player: Player):
        tile = self.draw_tile()
        if self.is_bonus_tile(tile):
            replaced, bonus = self._replace_bonus_tile([tile])
            player.add_bonus_tile(bonus)
            player.add_to_hand(replaced)
        else:
            player.receive_tile(tile)

    def player_discard_tile(self, player: Player, idx: int):
        tile = player.discard_tile(idx)
        self.thrown_tile(tile)

    def thrown_tile(self, tile: Tile):
        self.discarded_tiles.append(tile)
        self._next_player()

    def set_player_turn(self, player: int):
        if player < 0 or player > MAX_PLAYERS:
            raise ValueError("Invalid player")
        self.current_player = player

    def _starting_tile_indices(self, position: int):
        indices = [position * 4 + i * 16 + j for i in range(3) for j in range(4)]
        indices.append(3 * 16 + position)
        if position == 0:
            indices.append(3 * 16 + 4)
        return indices

    def _split_tiles(self, indices: list[int]):
        starting_hand: list[Tile] = []
        bonus_tiles: list[Bonus] = []
        for idx in indices:
            tile = self.all_tiles[idx]
            if self.is_bonus_tile(tile):
                bonus_tiles.append(tile)
            else:
                starting_hand.append(tile)
        return starting_hand, bonus_tiles

    def _replace_bonus_tile(self, tiles: list[Bonus]):
        if len(tiles) == 0:
            return ([], [])

        replacement_tiles: list[Tile] = []
        bonus_tiles: list[Bonus] = tiles.copy()
        pending_bonus = tiles.copy()

        while pending_bonus:
            pending_bonus.pop(0)
            tile = self.replace_tile()
            while self.is_bonus_tile(tile):
                bonus_tiles.append(tile)
                pending_bonus.append(tile)
                tile = self.replace_tile()
            replacement_tiles.append(tile)

        return replacement_tiles, bonus_tiles

    def _next_player(self):
        self.current_player = (self.current_player + 1) % 4
