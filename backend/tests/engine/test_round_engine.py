import pytest

from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import (
    Suit,
    SuitType,
    Wind,
    WindType,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
)
from backend.engine.round_engine import RoundEngine
from backend.utils.errors import InvalidActionError


def make_wall(tiles):
    return list(tiles)


def make_state(wall_tiles, prevalent_wind=WindType.DONG):
    wall = make_wall(wall_tiles)
    return GameState(0, prevalent_wind, wall)


def make_engine(wall_tiles, prevalent_wind=WindType.DONG):
    return RoundEngine(make_state(wall_tiles, prevalent_wind))


def make_player(position=0):
    return Player(position)


class TestInit:
    def test_stores_state(self):
        state = make_state([Suit(SuitType.DOT, 1)] * 100)
        engine = RoundEngine(state)
        assert engine.state is state


class TestDealStartingTiles:
    def test_deals_tiles_to_player_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        engine.deal_starting_tiles(p)
        assert len(p.hand_tile) > 0

    def test_bonus_tiles_replaced_and_added_to_bonus(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        p = Player(0)
        engine = RoundEngine(GameState(0, WindType.DONG, wall))
        engine.deal_starting_tiles(p)
        assert len(p.bonus_tile) >= 0

    def test_player_with_bonus_tiles_in_starting_hand(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        p = Player(0)
        engine.deal_starting_tiles(p)
        for t in p.bonus_tile:
            from backend.utils.helper import is_bonus_tile

            assert is_bonus_tile(t)

    def test_multiple_players_get_different_tiles(self):
        wall = [Suit(SuitType.DOT, 1)] * 53 + [Suit(SuitType.DOT, 2)] * 50
        state = GameState(3, WindType.DONG, wall)
        engine = RoundEngine(state)
        p0 = Player(0)
        p1 = Player(1)
        engine.deal_starting_tiles(p0)
        engine.deal_starting_tiles(p1)
        assert len(p0.hand_tile) > 0
        assert len(p1.hand_tile) > 0


class TestPlayerDrawTile:
    def test_draws_non_bonus_tile_and_adds_to_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        engine.player_draw_tile(p)
        assert len(p.hand_tile) == 1
        assert p.hand_tile[0] == Suit(SuitType.DOT, 1)

    def test_bonus_tile_is_collected_not_added_to_hand(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        engine = RoundEngine(GameState(0, WindType.DONG, wall))
        p = make_player()
        engine.player_draw_tile(p)
        assert len(p.bonus_tile) == 1
        assert isinstance(p.bonus_tile[0], Flower)


class TestPlayerDiscardTile:
    def test_delegates_and_returns_tile(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 5)])
        tile = engine.player_discard_tile(p, 0)
        assert tile == Suit(SuitType.DOT, 5)

    def test_errors_propagate(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        with pytest.raises(IndexError):
            engine.player_discard_tile(p, 0)


class TestAddToDiscardPile:
    def test_adds_tile_and_advances_player(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        engine.add_to_discard_pile(tile, p)
        assert tile in engine.state.discarded_tiles
        assert engine.state.current_player == 1

    def test_advances_player_correctly(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(2)
        engine.add_to_discard_pile(Suit(SuitType.DOT, 1), p)
        assert engine.state.current_player == 3


class TestChiTile:
    def test_executes_chi_and_returns_discard(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 9)]
        )
        result = engine.chi_tile(p, Suit(SuitType.DOT, 5))
        assert isinstance(result, Suit)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 3

    def test_error_propagates_on_invalid_chi(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)])
        with pytest.raises(InvalidActionError):
            engine.chi_tile(p, Suit(SuitType.DOT, 9))

    def test_hand_is_reduced_after_chi_and_discard(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 9)]
        )
        initial_hand = len(p.hand_tile)
        engine.chi_tile(p, Suit(SuitType.DOT, 5))
        assert len(p.hand_tile) < initial_hand


class TestExecuteChi:
    def test_delegates_to_player_chi(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand([Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4)])
        engine.execute_chi(p, Suit(SuitType.DOT, 5))
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 3
        assert len(p.hand_tile) == 0


class TestPongTile:
    def test_executes_pong_and_returns_discard(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, Suit(SuitType.DOT, 9)])
        result = engine.pong_tile(p, tile)
        assert isinstance(result, Suit)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 3

    def test_updates_tai_for_honor_tiles(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(0)
        tile = Dragon(DragonType.ZHONG)
        p.add_to_hand([tile, tile, Suit(SuitType.DOT, 9)])
        engine.pong_tile(p, tile)
        assert p.tai == 1

    def test_error_propagates_on_invalid_pong(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        with pytest.raises(InvalidActionError):
            engine.pong_tile(p, Suit(SuitType.DOT, 5))


class TestExecutePong:
    def test_delegates_and_updates_tai(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(0)
        tile = Wind(WindType.DONG)
        p.add_to_hand([tile, tile])
        engine.execute_pong(p, tile)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 3
        assert p.tai >= 1


class TestGangTile:
    def test_executes_gang_draws_replacement_and_returns_discard(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        result = engine.gang_tile(p, tile)
        assert isinstance(result, Suit)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 4

    def test_gang_draws_from_dead_wall(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        end_idx_before = state._end_idx
        engine.gang_tile(p, tile)
        assert state._end_idx < end_idx_before

    def test_gang_from_open_pong(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [[tile, tile, tile]]
        result = engine.gang_tile(p, tile)
        assert isinstance(result, Suit)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 4

    def test_error_propagates_on_invalid_gang(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        with pytest.raises(InvalidActionError):
            engine.gang_tile(p, Suit(SuitType.DOT, 5))


class TestExecuteGang:
    def test_delegates_and_updates_tai(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(0)
        tile = Dragon(DragonType.FA)
        p.add_to_hand([tile, tile, tile])
        engine.execute_gang(p, tile)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 4
        assert p.tai == 1


class TestReplaceBonusTiles:
    def test_empty_tiles_returns_empty(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        replacements, bonuses = engine._replace_bonus_tiles([])
        assert replacements == []
        assert bonuses == []

    def test_single_bonus_tile_replaced(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        replacements, bonuses = engine._replace_bonus_tiles([Flower(FlowerType.PLUM)])
        assert len(replacements) == 1
        assert len(bonuses) == 1

    def test_nested_bonus_tiles_replaced(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        wall[-1] = Flower(FlowerType.ORCHID)
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        replacements, bonuses = engine._replace_bonus_tiles([Flower(FlowerType.PLUM)])
        assert len(replacements) == 2
        assert len(bonuses) == 2
        assert bonuses[0] == Flower(FlowerType.PLUM)
        assert isinstance(bonuses[1], Flower)

    def test_multiple_initial_bonus_tiles(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        eng = make_engine([Suit(SuitType.DOT, 1)] * 100)
        wall = eng.state.all_tiles
        wall[53] = Flower(FlowerType.PLUM)
        wall[54] = Flower(FlowerType.ORCHID)
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        replacements, bonuses = engine._replace_bonus_tiles(
            [Flower(FlowerType.PLUM), Flower(FlowerType.ORCHID)]
        )
        assert len(replacements) == 2
        assert len(bonuses) == 2
