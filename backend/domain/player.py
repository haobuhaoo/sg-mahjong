from collections import Counter
import random

from backend.domain.tiles import (
    Animal,
    Bonus,
    Dragon,
    Flower,
    Season,
    Suit,
    Tile,
    Wind,
    WindType,
    MeldType,
)
from backend.rules.init import get_invalid_discard_tiles
from backend.utils.errors import DiscardError, InvalidActionError
from backend.utils.helper import is_bonus_tile, is_honor_tile, is_suit_tile


class Player:
    def __init__(self, position: int, tai: int = 0):
        """
        Creates a new player.

        Args:
            position: The position of the player (0-3 valid)
            tai: The number of tai for the player (default 0)

        Raises:
            IndexError: If position is not in [0, 3]
        """
        if position < 0 or position > 3:
            raise IndexError("Starting position must be between 0 and 3")
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
        self._last_meld_type: MeldType = None
        self._last_meld_from_hand: list[Tile] = []
        self._invalid_discard_tiles: set[Tile] = set()

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
        """Return the player's seating position (0-3)."""
        return self.position

    def add_tai(self, increment: int = 1) -> None:
        """Increase the player's tai score by the given increment (default 1)."""
        self.tai += increment

    def add_bonus_tile(self, bonus: list[Bonus]) -> None:
        """Add bonus tiles to the player and update any bonus-related tai."""
        self.bonus_tile += bonus
        self._update_bonus_tai(bonus)
        self._sort_tiles(self.bonus_tile)

    def add_to_hand(self, hand_tile: list[Tile]) -> None:
        """Add tiles to the player's hand and keep the hand sorted."""
        self.hand_tile += hand_tile
        self._sort_tiles(self.hand_tile)

    def add_open_tile(self, open_tile: list[Tile]) -> None:
        """Add tiles to the player's open set and keep them sorted."""
        self.open_tile += open_tile
        self._sort_tiles(self.open_tile)

    def check_bonus_tile(self, tile: Tile) -> bool:
        """Check if tile is a bonus tile, returning True if it is and adding it
        to the player's bonus set."""
        if is_bonus_tile(tile):
            self.add_bonus_tile([tile])
            return True

        return False

    def check_hand(self, prev_player: int, tile: Tile) -> tuple[bool, bool, bool, bool]:
        """Check if the player can hu, gang, pong, or chi the given tile."""
        return (
            self.can_hu(tile),
            self.can_gang(tile),
            self.can_pong(tile),
            self.can_chi(prev_player, tile),
        )

    def can_hu(self, tile: Tile) -> bool:
        """Return True if the player can declare hu on the given tile."""
        return self._check_hu(tile)

    def can_gang(self, tile: Tile) -> bool:
        """Return True if the player can form a gang with the given tile."""
        return self._check_gang(tile)

    def can_pong(self, tile: Tile) -> bool:
        """Return True if the player can form a pong with the given tile."""
        return self._check_pong(tile)

    def can_chi(self, prev_player: int, tile: Tile) -> bool:
        """Return True if the player can chi the given tile from the previous player."""
        return (
            (prev_player + 1) % 4 == self.position
            and is_suit_tile(tile)
            and self._check_chi(tile)
        )

    def receive_tile(self, tile: Tile) -> None:
        """Receive a drawn tile into the player's hand."""
        self.add_to_hand([tile])

    def discard_tile(self, idx: int) -> Tile:
        """
        Discard a tile from the player's hand and clear one-turn invalid discard restrictions.

        Raises:
            IndexError: If ``idx`` is out of bounds
            DiscardError: If tile at ``idx`` is an invalid discard tile
        """
        if idx < 0 or idx >= len(self.hand_tile):
            raise IndexError(
                f"Invalid tile position chosen. Tile position between 0 and {len(self.hand_tile) - 1}"
            )

        tile = self.hand_tile[idx]
        if tile in self._invalid_discard_tiles:
            raise DiscardError(f"Cannot discard {tile}", tile)

        tile = self.hand_tile.pop(idx)
        self._clear_invalid_discard_tiles()
        return tile

    def pick_tile_to_discard(self) -> int:
        """Choose a random index from the player's hand for discard."""
        # TODO: let user choose tile to discard from hand
        return random.Random().randint(0, len(self.hand_tile) - 1)

    def chi_tile(self, tile_chi: Suit) -> None:
        """
        Perform chi on the given suit tile and update invalid discard restrictions.

        Raises:
            InvalidActionError: If ``tile_chi`` has no neighbouring tiles in player's hand
        """
        neighbour_tiles = self._find_chi_tiles(tile_chi)
        if neighbour_tiles is None:
            raise InvalidActionError(f"Cannot chi {tile_chi}", MeldType.CHI, tile_chi)

        self._make_chi_meld(tile_chi, neighbour_tiles)
        self._set_invalid_discard_tiles(MeldType.CHI, tile_chi)

    def pong_tile(self, tile_pong: Tile) -> None:
        """
        Perform pong on the given tile and update invalid discard restrictions.

        Raises:
            InvalidActionError: If player does not have 2 of ``tile_pong`` in hand
        """
        if not self._check_pong(tile_pong):
            raise InvalidActionError(
                f"Cannot pong {tile_pong}", MeldType.PONG, tile_pong
            )

        self._make_pong_meld(tile_pong)
        self._set_invalid_discard_tiles(MeldType.PONG, tile_pong)

    def gang_tile(self, tile_gang: Tile) -> None:
        """
        Perform gang on the given tile and update invalid discard restrictions.

        Raises:
            InvalidActionError: If player does not have 3 of ``tile_gang`` in hand or
                3 of ``tile_gang`` in open set
        """
        if not self._check_gang(tile_gang):
            raise InvalidActionError(
                f"Cannot gang {tile_gang}", MeldType.GANG, tile_gang
            )

        self._make_gang_meld(tile_gang)
        self._set_invalid_discard_tiles(MeldType.GANG, tile_gang)

    def update_tai(self, tile: Tile, prevalent_wind: WindType) -> None:
        """Update tai from a claimed tile, resetting last meld tracking when appropriate."""
        if (
            self._last_meld_type == MeldType.GANG
            and len(self._last_meld_from_hand) == 0
        ):
            self._last_meld_type = None
            self._last_meld_from_hand = []
            return

        if is_honor_tile(tile):
            if isinstance(tile, Dragon):
                self.add_tai()
            elif isinstance(tile, Wind):
                if tile.type == self.seat_wind:
                    self.add_tai()
                if tile.type == prevalent_wind:
                    self.add_tai()

        self._last_meld_type = None
        self._last_meld_from_hand = []

    # private methods
    def _sort_tiles(self, tiles: list[Tile]) -> None:
        """Sort a list of tiles in place using the tile sort key."""
        tiles.sort(key=lambda tile: tile.sort_key())

    def _update_bonus_tai(self, bonus_tile: list[Bonus]) -> None:
        """Update tai bonuses for newly acquired bonus tiles."""
        self._award_bonus_tile_tai(bonus_tile)
        self._award_bonus_set_tai()

    def _award_bonus_tile_tai(self, bonus_tile: list[Bonus]) -> None:
        """Award tai for each individual bonus tile added to the player."""
        for tile in bonus_tile:
            order = tile.get_ordering()
            if isinstance(tile, Animal):
                self.add_tai()
            elif isinstance(tile, Flower) or isinstance(tile, Season):
                if order == self.position:
                    self.add_tai()

    def _award_bonus_set_tai(self) -> None:
        """Award tai for collecting a complete set of bonus tiles."""
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
        """Return True if the player's hand contains a valid chi for the given suit tile."""
        return self._find_chi_tiles(tile) is not None

    def _check_pong(self, tile: Tile) -> bool:
        """Return True if the player's hand has enough matching tiles to pong."""
        return 2 <= self.hand_tile.count(tile) <= 3

    def _check_gang(self, tile: Tile) -> bool:
        """Return True if the player can form a gang from hand or open set."""
        return self.hand_tile.count(tile) == 3 or self.open_tile.count(tile) == 3

    def _check_hu(self, tile: Tile) -> bool:
        """Return True if the player can hu on the given tile (placeholder logic)."""
        # TODO: implement hu logic
        return True

    def _find_chi_tiles(self, tile: Suit) -> list[Suit, Suit] | None:
        """Find and return a valid chi pair from the hand for the given suit tile."""
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
        """Consume the two hand tiles needed for a chi and add the meld to open set."""
        first_tile = self.discard_tile(self.hand_tile.index(neighbour_tiles[0]))
        second_tile = self.discard_tile(self.hand_tile.index(neighbour_tiles[1]))
        self.add_open_tile([tile, first_tile, second_tile])
        self._last_meld_from_hand = [first_tile, second_tile]

    def _make_pong_meld(self, tile: Tile) -> None:
        """Consume two matching hand tiles to form a pong and add it to open set."""
        self.discard_tile(self.hand_tile.index(tile))
        self.discard_tile(self.hand_tile.index(tile))
        self.add_open_tile([tile, tile, tile])
        self._last_meld_type = MeldType.PONG
        self._last_meld_from_hand = [tile, tile]

    def _make_gang_meld(self, tile: Tile) -> None:
        """Form a gang from either three hand tiles or an existing open pong."""
        if self.hand_tile.count(tile) == 3:
            self.discard_tile(self.hand_tile.index(tile))
            self.discard_tile(self.hand_tile.index(tile))
            self.discard_tile(self.hand_tile.index(tile))
            self.add_open_tile([tile, tile, tile, tile])
            self._last_meld_type = MeldType.GANG
            self._last_meld_from_hand = [tile, tile, tile]
        elif self.open_tile.count(tile) == 3:
            self.add_open_tile([tile])
            self._last_meld_type = MeldType.GANG
            self._last_meld_from_hand = []

    def _set_invalid_discard_tiles(
        self, meld_type: MeldType, thrown_tile: Tile
    ) -> None:
        """Compute and store invalid discard tiles after a meld restriction."""
        self._invalid_discard_tiles = get_invalid_discard_tiles(
            meld_type, self._last_meld_from_hand, thrown_tile
        )

    def _clear_invalid_discard_tiles(self) -> None:
        """Remove one-turn discard restrictions after a valid discard."""
        self._invalid_discard_tiles = set()
        self._last_meld_from_hand = []
