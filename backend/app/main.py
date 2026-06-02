import random

from backend.entity.tiles import (
    Animal,
    AnimalType,
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


def main():
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
    handTiles = []
    for i in range(3):
        for j in range(4):
            handTiles.append(allTiles[j + i * 16])
    handTiles.append(allTiles[48])
    handTiles.append(allTiles[52])
    print(", ".join([str(t) for t in handTiles]))


if __name__ == "__main__":
    main()
