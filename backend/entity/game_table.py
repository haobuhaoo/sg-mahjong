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
    Wind,
    WindType,
)

MAX_PLAYERS = 3


class GameTable:
    start_idx = 53
    end_idx = -1

    def __init__(self, players: int, allTiles: list):
        if players < 0 or players > MAX_PLAYERS:
            raise ValueError("Number of players must be between 0 and 3")
        self.players = players
        self.allTiles = allTiles

    @staticmethod
    def initialize_table():
        suits = []
        for suit in SuitType:
            for number in range(1, 10):
                suits.append(Suit(suit, number))

        honors = []
        for wind in WindType:
            honors.append(Wind(wind))
        for dragon in DragonType:
            honors.append(Dragon(dragon))

        bonus = []
        for animal in AnimalType:
            bonus.append(Animal(animal))
        for flower in FlowerType:
            bonus.append(Flower(flower))
        for season in SeasonType:
            bonus.append(Season(season))

        allTiles = suits + honors
        for _ in range(2):
            allTiles.extend(allTiles)
        allTiles.extend(bonus)

        random.shuffle(allTiles)
        return allTiles

    def dealStartingTiles(self, position: int, player: Player):
        if position < 0 or position > 3:
            raise ValueError("Starting position must be between 0 and 3")

        startingHand = []
        bonusTiles: list[Bonus] = []
        for i in range(3):
            for j in range(4):
                tile = self.allTiles[j + position * 4 + i * 16]
                if isinstance(tile, Bonus):
                    bonusTiles.append(tile)
                else:
                    startingHand.append(tile)
        tile = self.allTiles[3 * 16 + position]
        if isinstance(tile, Bonus):
            bonusTiles.append(tile)
        else:
            startingHand.append(tile)
        if position == 0:
            tile = self.allTiles[3 * 16 + 4]
            if isinstance(tile, Bonus):
                bonusTiles.append(tile)
            else:
                startingHand.append(tile)

        if len(bonusTiles) != 0:
            animals = 0
            flowers = 0
            seasons = 0
            for t in bonusTiles:
                order = t.getOrdering()
                if isinstance(t, Animal):
                    player.addTai()
                    animals += 1
                elif isinstance(t, Flower) or isinstance(t, Season):
                    if order == position:
                        player.addTai()
                    if t.__class__.__name__ == "Flower":
                        flowers += 1
                    else:
                        seasons += 1

            if animals == 4:
                player.addTai()
            if flowers == 4:
                player.addTai()
            if seasons == 4:
                player.addTai()

        for t in bonusTiles:
            startingHand.append(self.replaceTile())

        player.addBonusTile(bonusTiles)
        player.assignHand(startingHand)

    def drawTile(self):
        tile = self.allTiles[self.start_idx]
        self.start_idx += 1
        return tile

    def replaceTile(self):
        tile = self.allTiles[self.end_idx]
        self.end_idx -= 1
        return tile
