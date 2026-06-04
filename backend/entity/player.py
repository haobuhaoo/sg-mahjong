from backend.entity.tiles import Animal, Bonus, Flower, Season, Tile


class Player:
    def __init__(self, position: int, tai: int = 0):
        if position < 0 or position > 3:
            raise ValueError("Starting position must be between 0 and 3")
        self.position = position
        self.tai = tai
        self.hand_tile: list[Tile] = []
        self.bonus_tile: list[Bonus] = []
        self.animals = 0
        self.flowers = 0
        self.seasons = 0
        self.animals_max_tai = False
        self.flowers_max_tai = False
        self.seasons_max_tai = False

    def __str__(self):
        return (
            f"Tai: {self.tai}"
            + "\nBonus tiles: "
            + ", ".join([str(t) for t in self.bonus_tile])
            + "\nHand: "
            + ", ".join([str(t) for t in self.hand_tile])
        )

    def get_position(self):
        return self.position

    def add_tai(self, increment: int = 1):
        self.tai += increment

    def add_bonus_tile(self, bonus: list[Bonus]):
        self.tabulate_bonus_tile(bonus)
        self.bonus_tile += bonus
        self.sort_tiles(self.bonus_tile)

    def add_to_hand(self, hand_tile: list[Tile]):
        self.hand_tile += hand_tile
        self.sort_tiles(self.hand_tile)

    def sort_tiles(self, tiles: list[Tile]):
        tiles.sort(key=lambda tile: tile.sort_key())

    def tabulate_bonus_tile(self, bonus_tile: list[Bonus]):
        for tile in bonus_tile:
            order = tile.get_ordering()
            if isinstance(tile, Animal):
                self.add_tai()
                self.animals += 1
            elif isinstance(tile, Flower) or isinstance(tile, Season):
                if order == self.position:
                    self.add_tai()
                if tile.__class__.__name__ == "Flower":
                    self.flowers += 1
                else:
                    self.seasons += 1

        if not self.animals_max_tai and self.animals == 4:
            self.add_tai()
            self.animals_max_tai = True
        if not self.flowers_max_tai and self.flowers == 4:
            self.add_tai()
            self.flowers_max_tai = True
        if not self.seasons_max_tai and self.seasons == 4:
            self.add_tai()
            self.seasons_max_tai = True
