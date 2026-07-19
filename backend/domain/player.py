from collections import Counter
import random

from backend.domain.meld import Meld
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
from backend.rules.meld_discard_rules import get_invalid_discard_tiles
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
        self.open_tile: list[Meld] = []

        self.drawn_tile: Tile | None = None
        self.drawn_bonus_tiles: list[Tile] = []

        # internals
        self._animals_max_tai = False
        self._flowers_max_tai = False
        self._seasons_max_tai = False
        self._last_meld_type: MeldType | None = None
        self._last_meld_from_hand: list[Tile] = []
        self._invalid_discard_tiles: set[Tile] = set()

    def __str__(self):
        open_tiles = "; ".join(
            ", ".join(str(t) for t in meld.tiles) for meld in self.open_tile
        )
        return (
            f"Player {self.position + 1}"
            f"\nSeat wind: {self.seat_wind.value}"
            f"\nTai: {self.tai}"
            + "\nBonus tiles: "
            + ", ".join([str(t) for t in self.bonus_tile])
            + "\nOpen tiles: "
            + open_tiles
            + "\nHand: "
            + ", ".join([str(t) for t in self.hand_tile])
        )

    def __repr__(self):
        return (
            f"Player(position={self.position}, seat_wind={self.seat_wind}, "
            f"tai={self.tai}, bonus_tile={self.bonus_tile}, "
            f"open_tile={self.open_tile}, hand_tile={self.hand_tile}, "
            f"drawn_tile={self.drawn_tile}, drawn_bonus_tiles={self.drawn_bonus_tiles})"
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

    def add_open_tile(self, open_tile: list[Tile], is_exposed: bool = True) -> None:
        """Add a revealed meld to the player's open melds."""
        self._sort_tiles(open_tile)
        self.open_tile.append(Meld(tiles=open_tile, is_exposed=is_exposed))

    def get_open_tiles(self) -> list[Tile]:
        """Return a flat list of all tiles in the player's opened melds."""
        return [tile for meld in self.open_tile for tile in meld.tiles]

    def count_flower_season_tiles(self) -> int:
        """Return the number of Flower and Season tiles (excluding Animals)."""
        return sum(1 for t in self.bonus_tile if isinstance(t, (Flower, Season)))

    def check_bonus_tile(self, tile: Tile) -> bool:
        """
        Check if tile is a bonus tile, returning True if it is and adding it
        to the player's bonus set. Also appends to `drawn_bonus_tiles` for
        frontend visibility.
        """
        if is_bonus_tile(tile):
            self.add_bonus_tile([tile])
            self.drawn_bonus_tiles.append(tile)
            return True

        return False

    def find_concealed_gang_tiles(self) -> list[Tile]:
        """Return distinct tiles that appear exactly 4 times in the player's hand."""
        counts = Counter(self.hand_tile)
        return [t for t, c in counts.items() if c == 4]

    def find_pong_upgrade_tiles(self) -> list[Tile]:
        """Return hand tiles that match an existing open pong meld (exposed gang candidate)."""
        return [
            tile
            for tile in set(self.hand_tile)
            if any(
                len(meld.tiles) == 3 and all(t == tile for t in meld.tiles)
                for meld in self.open_tile
            )
        ]

    def receive_tile(self, tile: Tile) -> None:
        """Receive a drawn tile into the player's hand and track it as `drawn_tile`."""
        self.add_to_hand([tile])
        self.drawn_tile = tile

    def discard_tile(self, idx: int) -> Tile:
        """
        Discard a tile from the player's hand and clear one-turn invalid discard
        restrictions. Also clears `drawn_tile` and `drawn_bonus_tiles` to signal the end
        of the player's draw-assess window.

        Raises:
            IndexError: If `idx` is out of bounds
            DiscardError: If tile at `idx` is an invalid discard tile
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
        self.drawn_tile = None
        self.drawn_bonus_tiles = []
        return tile

    def pick_tile_to_discard(self) -> int:
        """Choose a random index from the player's hand for discard."""
        # TODO: let user choose tile to discard from hand
        return random.randrange(len(self.hand_tile))

    def chi_tile(self, tile_chi: Suit) -> None:
        """
        Perform chi on the given suit tile and update invalid discard restrictions.

        Raises:
            InvalidActionError: If `tile_chi` has no neighbouring tiles in player's hand
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
            InvalidActionError: If player does not have 2 of `tile_pong` in hand
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
            InvalidActionError: If player does not have 3 of `tile_gang` in hand or
                3 of `tile_gang` in open set
        """
        if not self._check_gang(tile_gang):
            raise InvalidActionError(
                f"Cannot gang {tile_gang}", MeldType.GANG, tile_gang
            )

        self._make_gang_meld(tile_gang)
        self._set_invalid_discard_tiles(MeldType.GANG, tile_gang)

    def make_concealed_gang(self, tile: Tile) -> None:
        """
        Consume 4 identical tiles from hand to form a concealed gang.

        The 4 tiles are removed from the hand and added as an open meld.
        Invalid discard restrictions are set for the gang tile.

        Raises:
            InvalidActionError: If `tile` does not appear exactly 4 times in hand.
        """
        if self.hand_tile.count(tile) != 4:
            raise InvalidActionError(
                f"Cannot form concealed gang with {tile}", MeldType.GANG, tile
            )
        for _ in range(4):
            self._remove_from_hand(tile)
        self.add_open_tile([tile, tile, tile, tile], is_exposed=False)
        self._last_meld_type = MeldType.GANG
        self._last_meld_from_hand = [tile, tile, tile, tile]
        self._set_invalid_discard_tiles(MeldType.GANG, tile)

    def make_exposed_gang(self, tile: Tile) -> None:
        """
        Upgrade an existing open pong to an exposed gang by adding a matching hand tile.

        The hand tile is removed from the hand and appended to the open pong meld,
        making it a 4-tile gang. The last meld tracking is set to indicate this
        came from an open pong upgrade, so update_tai skips re-awarding points.

        Raises:
            InvalidActionError: If `tile` is not in hand or no matching open
                pong meld exists.
        """
        if self.hand_tile.count(tile) < 1:
            raise InvalidActionError(
                f"Cannot form exposed gang with {tile}", MeldType.GANG, tile
            )
        pong_meld = next(
            (
                meld
                for meld in self.open_tile
                if len(meld.tiles) == 3 and all(t == tile for t in meld.tiles)
            ),
            None,
        )
        if pong_meld is None:
            raise InvalidActionError(
                f"No open pong to upgrade with {tile}", MeldType.GANG, tile
            )
        self._remove_from_hand(tile)
        pong_meld.tiles.append(tile)
        self._sort_tiles(pong_meld.tiles)
        self._last_meld_type = MeldType.GANG
        self._last_meld_from_hand = []
        self._set_invalid_discard_tiles(MeldType.GANG, tile)

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

    # Private methods

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

    def _check_pong(self, tile: Tile) -> bool:
        """Return True if the player's hand has enough matching tiles to pong."""
        return 2 <= self.hand_tile.count(tile) <= 3

    def _check_gang(self, tile: Tile) -> bool:
        """Return True if the player can form a gang from hand or an exposed pong."""
        return self.hand_tile.count(tile) == 3 or any(
            len(meld.tiles) == 3 and all(meld_tile == tile for meld_tile in meld.tiles)
            for meld in self.open_tile
        )

    def _find_chi_tiles(self, tile: Suit) -> list[Suit] | None:
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

    def _remove_from_hand(self, tile: Tile) -> Tile:
        """
        Remove and return one instance of the given tile from the hand.

        Unlike `discard_tile`, this has no discard side effects (does not touch
        `drawn_tile`, `drawn_bonus_tiles`, or invalid discard restrictions).

        Raises:
            ValueError: If `tile` is not in the hand
        """
        return self.hand_tile.pop(self.hand_tile.index(tile))

    def _make_chi_meld(self, tile: Suit, neighbour_tiles: list[Suit]) -> None:
        """Consume the two hand tiles needed for a chi and add the meld to open set."""
        first_tile = self._remove_from_hand(neighbour_tiles[0])
        second_tile = self._remove_from_hand(neighbour_tiles[1])
        self.add_open_tile([tile, first_tile, second_tile])
        self._last_meld_type = MeldType.CHI
        self._last_meld_from_hand = [first_tile, second_tile]

    def _make_pong_meld(self, tile: Tile) -> None:
        """Consume two matching hand tiles to form a pong and add it to open set."""
        self._remove_from_hand(tile)
        self._remove_from_hand(tile)
        self.add_open_tile([tile, tile, tile])
        self._last_meld_type = MeldType.PONG
        self._last_meld_from_hand = [tile, tile]

    def _make_gang_meld(self, tile: Tile) -> None:
        """Form a gang from either three hand tiles or an existing open pong."""
        if self.hand_tile.count(tile) == 3:
            self._remove_from_hand(tile)
            self._remove_from_hand(tile)
            self._remove_from_hand(tile)
            self.add_open_tile([tile, tile, tile, tile])
            self._last_meld_type = MeldType.GANG
            self._last_meld_from_hand = [tile, tile, tile]
        else:
            pong_meld = next(
                (
                    meld
                    for meld in self.open_tile
                    if len(meld.tiles) == 3
                    and all(meld_tile == tile for meld_tile in meld.tiles)
                ),
                None,
            )
            if pong_meld is None:
                return

            pong_meld.tiles.append(tile)
            self._sort_tiles(pong_meld.tiles)
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
        self._last_meld_type = None
        self._last_meld_from_hand = []
