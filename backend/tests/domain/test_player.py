import pytest

from backend.domain.meld import Meld
from backend.domain.player import Player
from backend.domain.tiles import (
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
from backend.domain.action_type import ActionType
from backend.utils.errors import DiscardError, InvalidActionError


def make_player(position=0, tai=0):
    return Player(position, tai)


class TestInit:
    def test_valid_positions(self):
        for pos in range(4):
            p = Player(pos)
            assert p.position == pos

    def test_invalid_position_negative(self):
        with pytest.raises(IndexError, match="Starting position must be between 0 and 3"):
            Player(-1)

    def test_invalid_position_too_high(self):
        with pytest.raises(IndexError, match="Starting position must be between 0 and 3"):
            Player(4)

    def test_default_tai_zero(self):
        p = make_player()
        assert p.tai == 0

    def test_custom_tai(self):
        p = Player(0, tai=5)
        assert p.tai == 5

    def test_seat_wind_matches_position(self):
        expected = [WindType.DONG, WindType.NAN, WindType.XI, WindType.BEI]
        for pos in range(4):
            p = Player(pos)
            assert p.seat_wind == expected[pos]

    def test_hand_tile_empty_initially(self):
        p = make_player()
        assert p.hand_tile == []

    def test_bonus_tile_empty_initially(self):
        p = make_player()
        assert p.bonus_tile == []

    def test_open_tile_empty_initially(self):
        p = make_player()
        assert p.open_tile == []

    def test_internal_state_defaults(self):
        p = make_player()
        assert p._animals_max_tai is False
        assert p._flowers_max_tai is False
        assert p._seasons_max_tai is False
        assert p._last_meld_type is None
        assert p._last_meld_from_hand == []
        assert p._invalid_discard_tiles == set()


class TestGetPosition:
    def test_returns_position(self):
        p = Player(2)
        assert p.get_position() == 2


class TestAddTai:
    def test_default_increment(self):
        p = make_player()
        p.add_tai()
        assert p.tai == 1

    def test_custom_increment(self):
        p = make_player()
        p.add_tai(3)
        assert p.tai == 3

    def test_multiple_increments(self):
        p = make_player()
        p.add_tai()
        p.add_tai()
        p.add_tai(2)
        assert p.tai == 4


class TestAddBonusTile:
    def test_adds_tiles_to_bonus_list(self):
        p = make_player()
        bonus = [Flower(FlowerType.PLUM)]
        p.add_bonus_tile(bonus)
        assert Flower(FlowerType.PLUM) in p.bonus_tile

    def test_bonus_tiles_are_sorted(self):
        p = make_player()
        bonus = [Flower(FlowerType.BAMBOO), Flower(FlowerType.PLUM)]
        p.add_bonus_tile(bonus)
        keys = [t.sort_key() for t in p.bonus_tile]
        assert keys == sorted(keys)

    def test_awards_tai_for_matching_flower(self):
        p = Player(2)
        p.add_bonus_tile([Flower(FlowerType.CHRYSANTHEMUM)])
        assert p.tai == 1

    def test_no_tai_for_non_matching_flower(self):
        p = Player(2)
        p.add_bonus_tile([Flower(FlowerType.PLUM)])
        assert p.tai == 0

    def test_awards_tai_for_any_animal(self):
        p = Player(2)
        p.add_bonus_tile([Animal(AnimalType.CAT)])
        assert p.tai == 1

    def test_awards_tai_for_complete_animal_set(self):
        p = make_player()
        animals = [
            Animal(AnimalType.CAT),
            Animal(AnimalType.RAT),
            Animal(AnimalType.CHICKEN),
            Animal(AnimalType.CENTIPEDE),
        ]
        p.add_bonus_tile(animals)
        assert p.tai == 5

    def test_complete_set_awarded_only_once(self):
        p = make_player()
        animals = [
            Animal(AnimalType.CAT),
            Animal(AnimalType.RAT),
            Animal(AnimalType.CHICKEN),
            Animal(AnimalType.CENTIPEDE),
        ]
        p.add_bonus_tile(animals)
        p.add_bonus_tile([])
        assert p._animals_max_tai is True
        assert p.tai == 5


class TestAddToHand:
    def test_adds_tiles(self):
        p = make_player()
        tiles = [Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)]
        p.add_to_hand(tiles)
        assert Suit(SuitType.DOT, 1) in p.hand_tile
        assert Suit(SuitType.DOT, 2) in p.hand_tile

    def test_sorts_hand(self):
        p = make_player()
        tiles = [Suit(SuitType.DOT, 9), Suit(SuitType.DOT, 1)]
        p.add_to_hand(tiles)
        keys = [t.sort_key() for t in p.hand_tile]
        assert keys == sorted(keys)


class TestAddOpenTile:
    def test_adds_tiles(self):
        p = make_player()
        tiles = [Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 1)]
        p.add_open_tile(tiles)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 3

    def test_sorts_open_tiles(self):
        p = make_player()
        tiles = [Suit(SuitType.DOT, 9), Suit(SuitType.DOT, 1)]
        p.add_open_tile(tiles)
        keys = [t.sort_key() for t in p.open_tile[0].tiles]
        assert keys == sorted(keys)


class TestCheckBonusTile:
    def test_returns_true_for_bonus_tile(self):
        p = make_player()
        result = p.check_bonus_tile(Flower(FlowerType.PLUM))
        assert result is True
        assert len(p.bonus_tile) == 1

    def test_returns_false_for_non_bonus_tile(self):
        p = make_player()
        result = p.check_bonus_tile(Suit(SuitType.DOT, 1))
        assert result is False
        assert len(p.bonus_tile) == 0


class TestReceiveTile:
    def test_adds_tile_to_hand(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.receive_tile(tile)
        assert tile in p.hand_tile
        assert len(p.hand_tile) == 1


class TestDiscardTile:
    def test_discards_tile_and_returns_it(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)])
        tile = p.discard_tile(0)
        assert tile == Suit(SuitType.DOT, 1)
        assert len(p.hand_tile) == 1

    def test_clears_invalid_discard_tiles(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)])
        p._invalid_discard_tiles = {Suit(SuitType.DOT, 3)}
        p.discard_tile(0)
        assert p._invalid_discard_tiles == set()

    def test_raises_index_error_for_negative_index(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1)])
        with pytest.raises(IndexError, match="Invalid tile position chosen"):
            p.discard_tile(-1)

    def test_raises_index_error_for_too_large_index(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1)])
        with pytest.raises(IndexError, match="Invalid tile position chosen"):
            p.discard_tile(1)

    def test_raises_index_error_when_hand_empty(self):
        p = make_player()
        with pytest.raises(IndexError, match="Invalid tile position chosen"):
            p.discard_tile(0)

    def test_raises_discard_error_for_invalid_discard_tile(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 1)
        p.add_to_hand([tile])
        p._invalid_discard_tiles = {tile}
        with pytest.raises(DiscardError, match="Cannot discard"):
            p.discard_tile(0)


class TestPickTileToDiscard:
    def test_returns_valid_index(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1)] * 5)
        idx = p.pick_tile_to_discard()
        assert 0 <= idx < 5

    def test_returns_zero_when_one_tile(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1)])
        idx = p.pick_tile_to_discard()
        assert idx == 0

    def test_raises_when_hand_empty(self):
        p = make_player()
        with pytest.raises(ValueError):
            p.pick_tile_to_discard()


class TestChiTile:
    def test_performs_chi_happy_path(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4)])
        p.chi_tile(Suit(SuitType.DOT, 5))
        assert Suit(SuitType.DOT, 3) in p.get_open_tiles()
        assert Suit(SuitType.DOT, 4) in p.get_open_tiles()
        assert Suit(SuitType.DOT, 5) in p.get_open_tiles()
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 3
        assert len(p.hand_tile) == 0

    def test_sets_invalid_discard_tiles_after_chi(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4)])
        p.chi_tile(Suit(SuitType.DOT, 5))
        assert len(p._invalid_discard_tiles) > 0

    def test_raises_invalid_action_error_when_no_chi_possible(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)])
        with pytest.raises(InvalidActionError, match="Cannot chi"):
            p.chi_tile(Suit(SuitType.DOT, 9))

    def test_chi_with_gap(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 2), Suit(SuitType.DOT, 4)])
        p.chi_tile(Suit(SuitType.DOT, 3))
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 3
        assert Suit(SuitType.DOT, 3) in p.get_open_tiles()


class TestPongTile:
    def test_performs_pong_happy_path(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile])
        p.pong_tile(tile)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 3
        assert len(p.hand_tile) == 0

    def test_sets_invalid_discard_tiles_after_pong(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile])
        p.pong_tile(tile)
        assert tile in p._invalid_discard_tiles

    def test_raises_invalid_action_error_when_insufficient_tiles(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 5)])
        with pytest.raises(InvalidActionError, match="Cannot pong"):
            p.pong_tile(Suit(SuitType.DOT, 5))

    def test_raises_invalid_action_error_when_tile_not_in_hand(self):
        p = make_player()
        with pytest.raises(InvalidActionError, match="Cannot pong"):
            p.pong_tile(Suit(SuitType.DOT, 5))


class TestGangTile:
    def test_gang_from_hand(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        p.gang_tile(tile)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 4
        assert len(p.hand_tile) == 0

    def test_gang_from_open_pong(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [Meld(tiles=[tile, tile, tile], is_exposed=True)]
        p.gang_tile(tile)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 4

    def test_sets_invalid_discard_tiles_after_gang(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        p.gang_tile(tile)
        assert tile in p._invalid_discard_tiles

    def test_raises_invalid_action_error_when_insufficient_tiles(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 5), Suit(SuitType.DOT, 5)])
        with pytest.raises(InvalidActionError, match="Cannot gang"):
            p.gang_tile(Suit(SuitType.DOT, 5))

    def test_raises_invalid_action_error_when_tile_not_in_hand_or_open(self):
        p = make_player()
        with pytest.raises(InvalidActionError, match="Cannot gang"):
            p.gang_tile(Suit(SuitType.DOT, 5))


class TestUpdateTai:
    def test_dragon_adds_one_tai(self):
        p = make_player()
        p.update_tai(Dragon(DragonType.ZHONG), WindType.DONG)
        assert p.tai == 1

    def test_seat_wind_adds_one_tai(self):
        p = Player(0)
        p.update_tai(Wind(WindType.DONG), WindType.NAN)
        assert p.tai == 1

    def test_prevalent_wind_adds_one_tai(self):
        p = Player(1)
        p.update_tai(Wind(WindType.DONG), WindType.DONG)
        assert p.tai == 1

    def test_both_seat_and_prevalent_wind_adds_two_tai(self):
        p = Player(0)
        p.update_tai(Wind(WindType.DONG), WindType.DONG)
        assert p.tai == 2

    def test_suit_tile_adds_no_tai(self):
        p = make_player()
        p.update_tai(Suit(SuitType.DOT, 5), WindType.DONG)
        assert p.tai == 0

    def test_resets_last_meld_tracking_after_update(self):
        p = make_player()
        p._last_meld_type = ActionType.PONG
        p._last_meld_from_hand = [Suit(SuitType.DOT, 1)]
        p.update_tai(Suit(SuitType.DOT, 5), WindType.DONG)
        assert p._last_meld_type is None
        assert p._last_meld_from_hand == []

    def test_gang_from_open_skips_tai_and_resets_tracking(self):
        p = make_player()
        p._last_meld_type = ActionType.GANG
        p._last_meld_from_hand = []
        p.update_tai(Dragon(DragonType.ZHONG), WindType.DONG)
        assert p.tai == 0
        assert p._last_meld_type is None
        assert p._last_meld_from_hand == []

    def test_gang_from_hand_proceeds_to_tai_update(self):
        p = make_player()
        p._last_meld_type = ActionType.GANG
        p._last_meld_from_hand = [Suit(SuitType.DOT, 1)]
        p.update_tai(Dragon(DragonType.FA), WindType.DONG)
        assert p.tai == 1
        assert p._last_meld_type is None


class TestStrAndRepr:
    def test_str_contains_player_number(self):
        p = Player(2)
        assert "Player 3" in str(p)

    def test_str_contains_seat_wind(self):
        p = Player(2)
        assert WindType.XI.value in str(p)

    def test_str_contains_tai(self):
        p = Player(0, tai=3)
        assert "3" in str(p)

    def test_str_contains_hand_tiles(self):
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1)])
        assert "1 Tong" in str(p)

    def test_str_contains_open_tiles(self):
        p = make_player()
        p.add_open_tile([Suit(SuitType.DOT, 1)])
        assert "1 Tong" in str(p)

    def test_str_contains_bonus_tiles(self):
        p = make_player()
        p.add_bonus_tile([Flower(FlowerType.PLUM)])
        assert "Plum" in str(p)

    def test_repr_contains_class_name(self):
        p = make_player()
        assert "Player" in repr(p)

    def test_repr_contains_position(self):
        p = Player(1)
        assert "position=1" in repr(p)


class TestDrawnTileTracking:
    def test_drawn_tile_set_by_receive_tile(self):
        p = make_player()
        p.receive_tile(Suit(SuitType.DOT, 5))
        assert p.drawn_tile == Suit(SuitType.DOT, 5)

    def test_drawn_tile_none_initially(self):
        p = make_player()
        assert p.drawn_tile is None

    def test_drawn_bonus_tiles_set_by_check_bonus_tile(self):
        p = make_player()
        p.check_bonus_tile(Flower(FlowerType.PLUM))
        assert len(p.drawn_bonus_tiles) == 1
        assert isinstance(p.drawn_bonus_tiles[0], Flower)

    def test_drawn_bonus_tiles_empty_initially(self):
        p = make_player()
        assert p.drawn_bonus_tiles == []

    def test_drawn_bonus_tiles_not_set_for_non_bonus(self):
        p = make_player()
        result = p.check_bonus_tile(Suit(SuitType.DOT, 1))
        assert result is False
        assert p.drawn_bonus_tiles == []

    def test_drawn_bonus_tiles_accumulates_multiple(self):
        p = make_player()
        p.check_bonus_tile(Flower(FlowerType.PLUM))
        p.check_bonus_tile(Flower(FlowerType.ORCHID))
        assert len(p.drawn_bonus_tiles) == 2

    def test_drawn_state_cleared_on_discard(self):
        p = make_player()
        p.receive_tile(Suit(SuitType.DOT, 5))
        p.check_bonus_tile(Flower(FlowerType.PLUM))
        assert p.drawn_tile is not None
        assert len(p.drawn_bonus_tiles) == 1
        p.discard_tile(0)
        assert p.drawn_tile is None
        assert p.drawn_bonus_tiles == []


class TestCountFlowerSeasonTiles:
    def test_counts_only_flowers_and_seasons(self):
        p = make_player()
        p.add_bonus_tile([Flower(FlowerType.PLUM)])
        p.add_bonus_tile([Flower(FlowerType.ORCHID)])
        p.add_bonus_tile([Season(SeasonType.SPRING)])
        assert p.count_flower_season_tiles() == 3

    def test_excludes_animals(self):
        p = make_player()
        p.add_bonus_tile([Flower(FlowerType.PLUM)])
        p.add_bonus_tile([Animal(AnimalType.CAT)])
        assert p.count_flower_season_tiles() == 1

    def test_returns_zero_for_no_bonus(self):
        p = make_player()
        assert p.count_flower_season_tiles() == 0

    def test_returns_eight_for_full_set(self):
        p = make_player()
        for flower in FlowerType:
            p.add_bonus_tile([Flower(flower)])
        for season in SeasonType:
            p.add_bonus_tile([Season(season)])
        assert p.count_flower_season_tiles() == 8


class TestFindConcealedGangTiles:
    def test_returns_tile_with_four_in_hand(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile])
        result = p.find_concealed_gang_tiles()
        assert result == [tile]

    def test_returns_multiple_when_multiple(self):
        p = make_player()
        t1 = Suit(SuitType.DOT, 5)
        t2 = Wind(WindType.DONG)
        p.add_to_hand([t1, t1, t1, t1, t2, t2, t2, t2])
        result = p.find_concealed_gang_tiles()
        assert len(result) == 2

    def test_returns_empty_when_no_four_in_hand(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        assert p.find_concealed_gang_tiles() == []

    def test_returns_empty_when_hand_empty(self):
        p = make_player()
        assert p.find_concealed_gang_tiles() == []


class TestMakeConcealedGang:
    def test_consumes_four_tiles_from_hand(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile, Suit(SuitType.DOT, 9)])
        p.make_concealed_gang(tile)
        assert tile not in p.hand_tile
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0].tiles) == 4

    def test_raises_when_not_four_in_hand(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        with pytest.raises(InvalidActionError, match="Cannot form concealed gang"):
            p.make_concealed_gang(tile)

    def test_raises_when_tile_not_in_hand(self):
        p = make_player()
        with pytest.raises(InvalidActionError, match="Cannot form concealed gang"):
            p.make_concealed_gang(Suit(SuitType.DOT, 5))

    def test_sets_hand_count_to_four_after_gang(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile])
        initial_count = len(p.hand_tile)
        p.make_concealed_gang(tile)
        assert len(p.hand_tile) == initial_count - 4


class TestFindPongUpgradeTiles:
    def test_returns_tile_when_hand_matches_open_pong(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [Meld(tiles=[tile, tile, tile], is_exposed=True)]
        p.add_to_hand([tile])
        result = p.find_pong_upgrade_tiles()
        assert tile in result

    def test_returns_empty_when_no_open_pong(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile])
        assert p.find_pong_upgrade_tiles() == []

    def test_returns_empty_when_hand_does_not_match(self):
        p = make_player()
        tile_pong = Suit(SuitType.DOT, 5)
        tile_hand = Suit(SuitType.DOT, 9)
        p.open_tile = [Meld(tiles=[tile_pong, tile_pong, tile_pong], is_exposed=True)]
        p.add_to_hand([tile_hand])
        assert p.find_pong_upgrade_tiles() == []


class TestMakeExposedGang:
    def test_upgrades_existing_pong(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [Meld(tiles=[tile, tile, tile], is_exposed=True)]
        p.add_to_hand([tile])
        p.make_exposed_gang(tile)
        assert len(p.open_tile[0].tiles) == 4

    def test_removes_hand_tile(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [Meld(tiles=[tile, tile, tile], is_exposed=True)]
        p.add_to_hand([tile, Suit(SuitType.DOT, 9)])
        p.make_exposed_gang(tile)
        assert tile not in p.hand_tile

    def test_raises_when_no_open_pong(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile])
        with pytest.raises(InvalidActionError, match="No open pong to upgrade"):
            p.make_exposed_gang(tile)

    def test_raises_when_hand_does_not_have_tile(self):
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [Meld(tiles=[tile, tile, tile], is_exposed=True)]
        with pytest.raises(InvalidActionError, match="Cannot form exposed gang"):
            p.make_exposed_gang(tile)


class TestVerifyTileCount:
    def test_defaults_false(self):
        p = make_player()
        assert p.forfeits_win is False
        assert p.forfeits_gang is False

    def test_normal_hand_no_open(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.verify_tile_count(expected=13)
        assert p.forfeits_win is False
        assert p.forfeits_gang is False

    def test_normal_hand_with_open_melds(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.open_tile = [Meld(tiles=[Suit(SuitType.DOT, 4)] * 3, is_exposed=True)]
        p.verify_tile_count(expected=13)
        assert p.forfeits_win is False
        assert p.forfeits_gang is False

    def test_short_hand_no_open(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
        )
        p.verify_tile_count(expected=13)
        assert p.forfeits_win is True
        assert p.forfeits_gang is False

    def test_long_hand_no_open(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)] * 2
        )
        p.verify_tile_count(expected=13)
        assert p.forfeits_win is True
        assert p.forfeits_gang is True

    def test_normal_after_draw(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)] * 2
        )
        p.verify_tile_count(expected=14)
        assert p.forfeits_win is False
        assert p.forfeits_gang is False

    def test_short_after_draw(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.verify_tile_count(expected=14)
        assert p.forfeits_win is True
        assert p.forfeits_gang is False

    def test_long_after_draw(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 4
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)] * 2
        )
        p.verify_tile_count(expected=14)
        assert p.forfeits_win is True
        assert p.forfeits_gang is True

    def test_count_normalizes_after_recovery(self):
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
        )
        p.verify_tile_count(expected=13)
        assert p.forfeits_win is True
        p.add_to_hand([Suit(SuitType.DOT, 5)])
        p.verify_tile_count(expected=13)
        assert p.forfeits_win is False
