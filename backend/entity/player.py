from collections import Counter
import random

from backend.entity.tiles import (
    Animal,
    Bonus,
    Dragon,
    Flower,
    Season,
    Suit,
    Tile,
    Wind,
    WindType,
)
from backend.utility.helper import is_bonus_tile, is_honor_tile, is_suit_tile


class MeldType:
    NONE = "none"
    PONG = "pong"
    GANG = "gang"


class Player:
    def __init__(self, position: int, tai: int = 0):
        if position < 0 or position > 3:
            raise ValueError("Starting position must be between 0 and 3")
        self.position = position
        self.seat_wind = list(WindType)[position]
        self.tai = tai
        self.hand_tile: list[Tile] = []
        self.bonus_tile: list[Bonus] = []
        self.open_tile: list[Tile] = []

        # internals
        self._animals_max_tai = False
        self._flowers_max_tai = False
        self._seasons_max_tai = False
        self._last_meld_type: MeldType = MeldType.NONE
        self._last_meld_from_hand: bool = False

    def __str__(self):
        return (
            f"Player {self.position + 1}"
            f"\nSeat wind: {self.seat_wind.value}"
            f"\nTai: {self.tai}"
            + "\nBonus tiles: "
            + ", ".join([str(t) for t in self.bonus_tile])
            + "\nOpen tiles: "
            + ", ".join([str(t) for t in self.open_tile])
            + "\nHand: "
            + ", ".join([str(t) for t in self.hand_tile])
        )

    def __repr__(self):
        return (
            f"Player(position={self.position}, seat_wind={self.seat_wind}, "
            f"tai={self.tai}, bonus_tile={self.bonus_tile}, "
            f"open_tile={self.open_tile}, hand_tile={self.hand_tile})"
        )

    def get_position(self) -> int:
        return self.position

    def add_tai(self, increment: int = 1) -> None:
        self.tai += increment

    def add_bonus_tile(self, bonus: list[Bonus]) -> None:
        self.bonus_tile += bonus
        self._update_bonus_tai(bonus)
        self._sort_tiles(self.bonus_tile)

    def add_to_hand(self, hand_tile: list[Tile]) -> None:
        self.hand_tile += hand_tile
        self._sort_tiles(self.hand_tile)

    def add_open_tile(self, open_tile: list[Tile]) -> None:
        self.open_tile += open_tile
        self._sort_tiles(self.open_tile)

    def check_bonus_tile(self, tile: Tile) -> bool:
        if is_bonus_tile(tile):
            self.add_bonus_tile([tile])
            return True

        return False

    def check_hand(self, prev_player: int, tile: Tile) -> tuple[bool, bool, bool, bool]:
        return (
            self.can_hu(tile),
            self.can_gang(tile),
            self.can_pong(tile),
            self.can_chi(prev_player, tile),
        )

    def can_hu(self, tile: Tile) -> bool:
        return self._check_hu(tile)

    def can_gang(self, tile: Tile) -> bool:
        return self._check_gang(tile)

    def can_pong(self, tile: Tile) -> bool:
        return self._check_pong(tile)

    def can_chi(self, prev_player: int, tile: Tile) -> bool:
        return (
            (prev_player + 1) % 4 == self.position
            and is_suit_tile(tile)
            and self._check_chi(tile)
        )

    def receive_tile(self, tile: Tile) -> None:
        self.add_to_hand([tile])

    def discard_tile(self, idx: int) -> Tile:
        if idx < 0 or idx >= len(self.hand_tile):
            raise ValueError(
                f"Invalid tile position chosen. Tile position between 0 and {len(self.hand_tile) - 1}"
            )

        return self.hand_tile.pop(idx)

    def pick_tile_to_discard(self) -> int:
        return random.Random().randint(0, len(self.hand_tile) - 1)

    def chi_tile(self, tile: Suit) -> None:
        neighbour_tiles = self._find_chi_tiles(tile)
        if neighbour_tiles is None:
            raise ValueError(f"Cannot chi {tile}")

        self._make_chi_meld(tile, neighbour_tiles)

    def pong_tile(self, tile: Tile) -> None:
        if not self._check_pong(tile):
            raise ValueError(f"Cannot pong {tile}")

        self._make_pong_meld(tile)

    def gang_tile(self, tile: Tile) -> None:
        if not self._check_gang(tile):
            raise ValueError(f"Cannot gang {tile}")

        self._make_gang_meld(tile)

    def update_tai(self, tile: Tile, prevalent_wind: WindType) -> None:
        if self._last_meld_type == MeldType.GANG and not self._last_meld_from_hand:
            self._last_meld_type = MeldType.NONE
            self._last_meld_from_hand = False
            return

        if is_honor_tile(tile):
            if isinstance(tile, Dragon):
                self.add_tai()
            elif isinstance(tile, Wind):
                if tile.type == self.seat_wind:
                    self.add_tai()
                if tile.type == prevalent_wind:
                    self.add_tai()

        self._last_meld_type = MeldType.NONE
        self._last_meld_from_hand = False

    # private methods
    def _sort_tiles(self, tiles: list[Tile]) -> None:
        tiles.sort(key=lambda tile: tile.sort_key())

    def _update_bonus_tai(self, bonus_tile: list[Bonus]) -> None:
        self._award_bonus_tile_tai(bonus_tile)
        self._award_bonus_set_tai()

    def _award_bonus_tile_tai(self, bonus_tile: list[Bonus]) -> None:
        for tile in bonus_tile:
            order = tile.get_ordering()
            if isinstance(tile, Animal):
                self.add_tai()
            elif isinstance(tile, Flower) or isinstance(tile, Season):
                if order == self.position:
                    self.add_tai()

    def _award_bonus_set_tai(self) -> None:
        counts = Counter(tile.__class__.__name__ for tile in self.bonus_tile)
        animals = counts[Animal.__name__]
        flowers = counts[Flower.__name__]
        seasons = counts[Season.__name__]

        if not self._animals_max_tai and animals == 4:
            self.add_tai()
            self._animals_max_tai = True
        if not self._flowers_max_tai and flowers == 4:
            self.add_tai()
            self._flowers_max_tai = True
        if not self._seasons_max_tai and seasons == 4:
            self.add_tai()
            self._seasons_max_tai = True

    def _check_chi(self, tile: Suit) -> bool:
        return self._find_chi_tiles(tile) is not None

    def _check_pong(self, tile: Tile) -> bool:
        return 2 <= self.hand_tile.count(tile) <= 3

    def _check_gang(self, tile: Tile) -> bool:
        return self.hand_tile.count(tile) == 3 or self.open_tile.count(tile) == 3

    def _check_hu(self, tile: Tile) -> bool:
        return True

    def _find_chi_tiles(self, tile: Suit) -> list[Suit, Suit] | None:
        suits_type = tile.type
        suits_value = tile.number
        lookup = {(t.type, t.number) for t in self.hand_tile if is_suit_tile(t)}

        if (suits_type, suits_value + 1) in lookup and (
            suits_type,
            suits_value + 2,
        ) in lookup:
            return [
                Suit(suits_type, suits_value + 1),
                Suit(suits_type, suits_value + 2),
            ]
        if (suits_type, suits_value - 1) in lookup and (
            suits_type,
            suits_value + 1,
        ) in lookup:
            return [
                Suit(suits_type, suits_value - 1),
                Suit(suits_type, suits_value + 1),
            ]
        if (suits_type, suits_value - 2) in lookup and (
            suits_type,
            suits_value - 1,
        ) in lookup:
            return [
                Suit(suits_type, suits_value - 2),
                Suit(suits_type, suits_value - 1),
            ]

        return None

    def _make_chi_meld(self, tile: Suit, neighbour_tiles: list[Suit]) -> None:
        first_tile = self.discard_tile(self.hand_tile.index(neighbour_tiles[0]))
        second_tile = self.discard_tile(self.hand_tile.index(neighbour_tiles[1]))
        self.add_open_tile([tile, first_tile, second_tile])

    def _make_pong_meld(self, tile: Tile) -> None:
        self.discard_tile(self.hand_tile.index(tile))
        self.discard_tile(self.hand_tile.index(tile))
        self.add_open_tile([tile, tile, tile])
        self._last_meld_type = MeldType.PONG
        self._last_meld_was_hand_gang = True

    def _make_gang_meld(self, tile: Tile) -> None:
        if self.hand_tile.count(tile) == 3:
            self.discard_tile(self.hand_tile.index(tile))
            self.discard_tile(self.hand_tile.index(tile))
            self.discard_tile(self.hand_tile.index(tile))
            self.add_open_tile([tile, tile, tile, tile])
            self._last_meld_type = MeldType.GANG
            self._last_meld_from_hand = True
        elif self.open_tile.count(tile) == 3:
            self.add_open_tile([tile])
            self._last_meld_type = MeldType.GANG
            self._last_meld_from_hand = False
