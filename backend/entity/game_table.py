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
    def __init__(self, players: int, all_tiles: list):
        if players < 0 or players > MAX_PLAYERS:
            raise ValueError("Number of players must be between 0 and 3")
        self.players = players
        self.all_tiles = all_tiles
        self.start_idx = 3 * 16 + 4 + 1
        self.end_idx = -1

    @staticmethod
    def _create_suit_tiles():
        return [Suit(suit, number) for suit in SuitType for number in range(1, 10)]

    @staticmethod
    def _create_honor_tiles():
        return [Wind(wind) for wind in WindType] + [Dragon(dragon) for dragon in DragonType]

    @staticmethod
    def _create_bonus_tiles():
        return [Animal(animal) for animal in AnimalType] + [Flower(flower) for flower in FlowerType] + [Season(season) for season in SeasonType]

    @staticmethod
    def initialize_table():
        all_tiles = []
        for _ in range(4):
            all_tiles.extend(GameTable._create_suit_tiles())
            all_tiles.extend(GameTable._create_honor_tiles())
        all_tiles.extend(GameTable._create_bonus_tiles())

        random.shuffle(all_tiles)
        return all_tiles

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

    def deal_starting_tiles(self, player: Player):
        starting_hand, bonus_tiles = self._split_tiles(self._starting_tile_indices(player.get_position()))
        replaced, bonus = self.replace_bonus_tile(bonus_tiles)
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

    def replace_bonus_tile(self, tiles: list[Bonus]):
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

    def is_bonus_tile(self, tile: Tile):
        return isinstance(tile, Bonus)
