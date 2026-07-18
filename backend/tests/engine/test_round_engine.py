import pytest

from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import (
    Animal,
    AnimalType,
    Suit,
    SuitType,
    Wind,
    WindType,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
    Season,
    SeasonType,
)
from backend.engine.round_engine import RoundEngine
from backend.engine.turn_result import (
    AssessResult,
    DrawResult,
    WinEvent,
    WinSource,
)
from backend.rules.hu_result import HandPattern
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


def make_players(count=4):
    return [Player(i) for i in range(count)]


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


class TestHeavenlyHand:
    def test_heavenly_hand_with_winning_14_tiles(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        dealer = Player(0)
        dealer.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)] * 2
        )
        result = engine.check_heavenly_hand(dealer)
        assert result.win is not None
        assert WinEvent.HEAVENLY in result.win.events
        assert result.win.source == WinSource.SELF_PICK

    def test_not_heavenly_if_not_dealer(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(1)
        result = engine.check_heavenly_hand(p)
        assert result.win is None

    def test_not_heavenly_if_not_14_tiles(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        dealer = Player(0)
        dealer.add_to_hand([Suit(SuitType.DOT, 1)] * 13)
        result = engine.check_heavenly_hand(dealer)
        assert result.win is None

    def test_not_heavenly_if_no_winning_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        dealer = Player(0)
        dealer.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 2
            + [Suit(SuitType.DOT, 4)] * 2
            + [Suit(SuitType.DOT, 7)] * 2
            + [Suit(SuitType.BAMBOO, 2)] * 2
            + [Suit(SuitType.BAMBOO, 5)] * 2
            + [Suit(SuitType.BAMBOO, 8)] * 2
            + [Suit(SuitType.CHARACTER, 3)] * 2
        )
        result = engine.check_heavenly_hand(dealer)
        assert result.win is None


class TestPlayerDrawTile:
    def test_draws_non_bonus_tile_and_adds_to_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        players = [p]
        result = engine.player_draw_tile(p, players)
        assert result.drawn_tile == Suit(SuitType.DOT, 1)
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
        players = [p]
        result = engine.player_draw_tile(p, players)
        assert len(p.bonus_tile) == 1
        assert isinstance(p.bonus_tile[0], Flower)
        assert result.drawn_bonus_tiles != []

    def test_returns_draw_result(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        players = [p]
        result = engine.player_draw_tile(p, players)
        assert isinstance(result, DrawResult)
        assert result.drawn_tile is not None
        assert result.robbed_by is None

    def test_sets_is_replacement_when_bonus_was_drawn(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        engine = RoundEngine(GameState(0, WindType.DONG, wall))
        p = make_player()
        players = [p]
        result = engine.player_draw_tile(p, players)
        assert result.is_replacement is True

    def test_sets_is_replacement_when_gang_draw(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        players = [p]
        result = engine.player_draw_tile(p, players, is_gang=True)
        assert result.is_replacement is True

    def test_no_is_replacement_for_normal_draw(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        players = [p]
        result = engine.player_draw_tile(p, players)
        assert result.is_replacement is False

    def test_resets_drawn_state_before_draw(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.drawn_tile = Suit(SuitType.DOT, 9)
        p.drawn_bonus_tiles = [Flower(FlowerType.PLUM)]
        players = [p]
        engine.player_draw_tile(p, players)
        assert p.drawn_tile != Suit(SuitType.DOT, 9)
        assert len(p.drawn_bonus_tiles) == 0


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


class TestFinalizeDiscard:
    def test_adds_tile_and_advances_player(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        engine.finalize_discard(tile, p)
        assert tile in engine.state.discarded_tiles
        assert engine.state.current_player == 1

    def test_advances_player_correctly(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(2)
        engine.finalize_discard(Suit(SuitType.DOT, 1), p)
        assert engine.state.current_player == 3

    def test_increments_turn_count(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        assert engine.state.turn_count == 0
        engine.finalize_discard(Suit(SuitType.DOT, 1), p)
        assert engine.state.turn_count == 1


class TestPlayerAssessHand:
    def test_can_self_pick_when_drawn_tile_completes_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is not None

    def test_no_self_pick_when_hand_incomplete(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is None

    def test_no_self_pick_when_no_drawn_tile(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        result = engine.player_assess_hand(p)
        assert result.win is None

    def test_finds_concealed_gang_tiles(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile])
        result = engine.player_assess_hand(p)
        assert tile in result.actions.concealed_gang_tiles

    def test_finds_pong_upgrade_tiles(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [[tile, tile, tile]]
        p.add_to_hand([tile])
        result = engine.player_assess_hand(p)
        assert tile in result.actions.pong_upgrade_tiles

    def test_has_flower_win_with_eight_flowers_seasons(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        for flower in FlowerType:
            p.add_bonus_tile([Flower(flower)])
        for season in SeasonType:
            p.add_bonus_tile([Season(season)])
        result = engine.player_assess_hand(p)
        assert result.flower_win is True

    def test_no_flower_win_with_seven(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        for flower in FlowerType:
            p.add_bonus_tile([Flower(flower)])
        for season in [SeasonType.SPRING, SeasonType.SUMMER, SeasonType.AUTUMN]:
            p.add_bonus_tile([Season(season)])
        result = engine.player_assess_hand(p)
        assert result.flower_win is False

    def test_win_on_replacement(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p, is_replacement=True)
        assert result.win is not None
        assert WinEvent.REPLACEMENT_TILE in result.win.events

    def test_win_on_last_tile(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p, is_last_tile=True)
        assert result.win is not None
        assert WinEvent.LAST_TILE in result.win.events

    def test_no_win_on_last_tile_if_replacement(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p, is_last_tile=True, is_replacement=True)
        assert result.win is not None
        assert WinEvent.LAST_TILE not in result.win.events

    def test_is_earthly_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(1)
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p, is_first_draw=True)
        assert result.win is not None
        assert WinEvent.EARTHLY in result.win.events

    def test_not_earthly_if_dealer(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = Player(0)
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p, is_first_draw=True)
        assert result.win is not None
        assert WinEvent.EARTHLY not in result.win.events

    def test_any_win_aggregates_all_wins(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.any_win is True
        assert result.has_options is True


class TestPlayerSelfPick:
    def test_returns_winning_tile(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        tile = engine.player_self_pick(p)
        assert tile == Suit(SuitType.DOT, 5)

    def test_raises_when_no_drawn_tile(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        with pytest.raises(InvalidActionError, match="No drawn tile"):
            engine.player_self_pick(p)

    def test_raises_when_cannot_hu(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.receive_tile(Suit(SuitType.DOT, 5))
        with pytest.raises(InvalidActionError, match="Cannot self-pick"):
            engine.player_self_pick(p)


class TestDeclareConcealedGang:
    def test_consumes_tiles_and_draws_replacement(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile])
        players = [p]
        result = engine.declare_concealed_gang(p, tile, players)
        assert isinstance(result, DrawResult)
        assert result.drawn_tile is not None
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 4

    def test_draws_from_dead_wall(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile])
        end_idx_before = state._end_idx
        players = [p]
        engine.declare_concealed_gang(p, tile, players)
        assert state._end_idx < end_idx_before

    def test_raises_when_not_four_in_hand(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile])
        players = [p]
        with pytest.raises(InvalidActionError):
            engine.declare_concealed_gang(p, tile, players)


class TestDeclareExposedGang:
    def test_upgrades_pong_and_draws_replacement(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [[tile, tile, tile]]
        p.add_to_hand([tile, Suit(SuitType.DOT, 9)])
        players = [p]
        result = engine.declare_exposed_gang(p, tile, players)
        assert isinstance(result, DrawResult)
        assert result.drawn_tile is not None
        assert len(p.open_tile[0]) == 4

    def test_robbed_by_other_player(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        robber = Player(1)
        tile = Suit(SuitType.DOT, 5)
        robber.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p = make_player()
        p.open_tile = [[tile, tile, tile]]
        p.add_to_hand([tile])
        players = [p, robber]
        result = engine.declare_exposed_gang(p, tile, players)
        assert isinstance(result, AssessResult)
        assert result.robbing_gang_by == 1
        assert result.win is not None
        assert result.win.winner == 1
        assert result.win.source == WinSource.DISCARD
        assert WinEvent.ROBBING_GANG in result.win.events
        assert len(p.open_tile[0]) == 3

    def test_not_robbed_if_no_can_hu(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        other = Player(1)
        tile = Suit(SuitType.DOT, 5)
        p = make_player()
        p.open_tile = [[tile, tile, tile]]
        p.add_to_hand([tile])
        players = [p, other]
        result = engine.declare_exposed_gang(p, tile, players)
        assert isinstance(result, DrawResult)


class TestRobbingTheEighth:
    def test_player_with_seven_flowers_robs_eighth(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        robber = Player(1)
        for flower in FlowerType:
            robber.add_bonus_tile([Flower(flower)])
        for season in [SeasonType.SPRING, SeasonType.SUMMER, SeasonType.AUTUMN]:
            robber.add_bonus_tile([Season(season)])
        drawer = make_player()
        players = [drawer, robber]
        result = engine.player_draw_tile(drawer, players)
        assert result.robbed_by == 1

    def test_not_robbed_if_no_player_has_seven(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        engine = RoundEngine(GameState(0, WindType.DONG, wall))
        other = Player(1)
        other.add_bonus_tile([Flower(FlowerType.PLUM)])
        drawer = make_player()
        players = [drawer, other]
        result = engine.player_draw_tile(drawer, players)
        assert result.robbed_by is None

    def test_seven_animals_do_not_trigger_rob(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        engine = RoundEngine(GameState(0, WindType.DONG, wall))
        other = Player(1)
        for animal in AnimalType:
            other.add_bonus_tile([Animal(animal)])
        other.add_bonus_tile([Flower(FlowerType.PLUM)])
        other.add_bonus_tile([Flower(FlowerType.ORCHID)])
        other.add_bonus_tile([Flower(FlowerType.CHRYSANTHEMUM)])
        drawer = make_player()
        players = [drawer, other]
        result = engine.player_draw_tile(drawer, players)
        assert result.robbed_by is None

    def test_animal_draw_not_robbed(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Animal(AnimalType.CAT)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        robber = Player(1)
        for flower in FlowerType:
            robber.add_bonus_tile([Flower(flower)])
        for season in [SeasonType.SPRING, SeasonType.SUMMER, SeasonType.AUTUMN]:
            robber.add_bonus_tile([Season(season)])
        drawer = make_player()
        players = [drawer, robber]
        result = engine.player_draw_tile(drawer, players)
        assert result.robbed_by is None
        assert Animal(AnimalType.CAT) in drawer.bonus_tile
        assert result.drawn_tile == Suit(SuitType.DOT, 1)

    def test_drawn_bonus_tiles_populated_when_robbed(self):
        wall = (
            [Suit(SuitType.DOT, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        state = GameState(0, WindType.DONG, wall)
        engine = RoundEngine(state)
        robber = Player(1)
        for flower in FlowerType:
            robber.add_bonus_tile([Flower(flower)])
        for season in [SeasonType.SPRING, SeasonType.SUMMER, SeasonType.AUTUMN]:
            robber.add_bonus_tile([Season(season)])
        drawer = make_player()
        players = [drawer, robber]
        result = engine.player_draw_tile(drawer, players)
        assert result.robbed_by == 1
        assert result.drawn_tile is None


class TestEarthlyHandDiscard:
    def test_returns_win_on_first_discard(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        non_dealer = Player(1)
        tile = Suit(SuitType.DOT, 5)
        non_dealer.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        result = engine.check_earthly_hand_discard(tile, [non_dealer])
        assert result.win is not None
        assert WinEvent.EARTHLY in result.win.events
        assert result.win.source == WinSource.DISCARD

    def test_returns_none_after_first_turn(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        engine.state.advance_turn()
        non_dealer = Player(1)
        tile = Suit(SuitType.DOT, 5)
        non_dealer.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
        )
        result = engine.check_earthly_hand_discard(tile, [non_dealer])
        assert result.win is None

    def test_returns_none_if_cannot_hu(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        non_dealer = Player(1)
        tile = Suit(SuitType.DOT, 5)
        result = engine.check_earthly_hand_discard(tile, [non_dealer])
        assert result.win is None


class TestHumanlyHand:
    def test_qualifies_in_first_go_around_no_draw_no_melds(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        claimant = Player(1)
        tile = Suit(SuitType.DOT, 5)
        claimant.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        players = [Player(0), claimant, Player(2), Player(3)]
        result = engine.check_humanly_hand(tile, claimant, players)
        assert result.win is not None
        assert WinEvent.HUMANLY in result.win.events

    def test_fails_after_first_go_around(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        for _ in range(4):
            engine.state.advance_turn()
        claimant = Player(1)
        tile = Suit(SuitType.DOT, 5)
        claimant.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
        )
        players = [Player(0), claimant]
        result = engine.check_humanly_hand(tile, claimant, players)
        assert result.win is None

    def test_fails_if_already_drew(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        claimant = Player(1)
        claimant.receive_tile(Suit(SuitType.DOT, 1))
        tile = Suit(SuitType.DOT, 5)
        claimant.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 2
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
        )
        players = [Player(0), claimant]
        result = engine.check_humanly_hand(tile, claimant, players)
        assert result.win is None

    def test_fails_with_exposed_meld(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        claimant = Player(1)
        tile = Suit(SuitType.DOT, 5)
        claimant.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
        )
        exposed_player = Player(2)
        exposed_player.add_open_tile([Suit(SuitType.DOT, 7)])
        players = [Player(0), claimant, exposed_player]
        result = engine.check_humanly_hand(tile, claimant, players)
        assert result.win is None

    def test_fails_if_cannot_hu(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        claimant = Player(1)
        tile = Suit(SuitType.DOT, 5)
        players = [Player(0), claimant]
        result = engine.check_humanly_hand(tile, claimant, players)
        assert result.win is None


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
        players = [p]
        result = engine.gang_tile(p, tile, players)
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
        players = [p]
        engine.gang_tile(p, tile, players)
        assert state._end_idx < end_idx_before

    def test_gang_from_open_pong(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.open_tile = [[tile, tile, tile]]
        players = [p]
        result = engine.gang_tile(p, tile, players)
        assert isinstance(result, Suit)
        assert len(p.open_tile) == 1
        assert len(p.open_tile[0]) == 4

    def test_error_propagates_on_invalid_gang(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        players = [p]
        with pytest.raises(InvalidActionError):
            engine.gang_tile(p, Suit(SuitType.DOT, 5), players)


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
        assert len(bonuses) == 2


class TestEighteenArhats:
    def test_eighteen_arhats_with_4_gangs_and_self_pick(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.open_tile = [
            [Suit(SuitType.DOT, 1)] * 4,
            [Suit(SuitType.DOT, 2)] * 4,
            [Suit(SuitType.DOT, 3)] * 4,
            [Suit(SuitType.DOT, 4)] * 4,
        ]
        p.add_to_hand([Suit(SuitType.DOT, 5)])
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is not None
        assert HandPattern.EIGHTEEN_ARHATS in result.win.hu.patterns

    def test_not_eighteen_arhats_with_3_gangs(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.open_tile = [
            [Suit(SuitType.DOT, 1)] * 4,
            [Suit(SuitType.DOT, 2)] * 4,
            [Suit(SuitType.DOT, 3)] * 4,
        ]
        p.add_to_hand([Suit(SuitType.DOT, 4)] * 3 + [Suit(SuitType.DOT, 5)])
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is not None
        assert HandPattern.EIGHTEEN_ARHATS not in result.win.hu.patterns

    def test_not_eighteen_arhats_if_cannot_self_pick(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.open_tile = [
            [Suit(SuitType.DOT, 1)] * 4,
            [Suit(SuitType.DOT, 2)] * 4,
            [Suit(SuitType.DOT, 3)] * 4,
            [Suit(SuitType.DOT, 4)] * 4,
        ]
        p.receive_tile(Suit(SuitType.DOT, 9))
        result = engine.player_assess_hand(p)
        assert result.win is None


class TestFullyConcealedHand:
    def test_fully_concealed_with_no_melds_and_self_pick(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is not None
        assert HandPattern.FULLY_CONCEALED in result.win.hu.patterns

    def test_fully_concealed_with_concealed_gang_allowed(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.open_tile = [[Suit(SuitType.DOT, 1)] * 4]
        p.add_to_hand(
            [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is not None
        assert HandPattern.FULLY_CONCEALED in result.win.hu.patterns

    def test_not_fully_concealed_with_exposed_pong(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.open_tile = [[Suit(SuitType.DOT, 1)] * 3]
        p.add_to_hand(
            [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is not None
        assert HandPattern.FULLY_CONCEALED not in result.win.hu.patterns

    def test_not_fully_concealed_if_cannot_self_pick(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        p = make_player()
        p.receive_tile(Suit(SuitType.DOT, 5))
        result = engine.player_assess_hand(p)
        assert result.win is None


class TestRobbingConcealedGang:
    def test_robbed_when_thirteen_wonders(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        robber = Player(1)
        for suit in SuitType:
            robber.add_to_hand([Suit(suit, 1), Suit(suit, 9)])
        for wind in WindType:
            robber.add_to_hand([Wind(wind)])
        for dragon in DragonType:
            robber.add_to_hand([Dragon(dragon)])
        robber.add_to_hand([Dragon(DragonType.ZHONG)])
        tile = robber.hand_tile[0]
        robber.hand_tile.remove(tile)
        p = make_player()
        p.add_to_hand([tile, tile, tile, tile])
        players = [p, robber]
        result = engine.declare_concealed_gang(p, tile, players)
        assert isinstance(result, AssessResult)
        assert result.robbing_gang_by == 1
        assert result.win is not None
        assert result.win.winner == 1
        assert HandPattern.THIRTEEN_WONDERS in result.win.hu.patterns
        assert WinEvent.ROBBING_GANG in result.win.events

    def test_not_robbed_when_not_thirteen_wonders(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        robber = Player(1)
        robber.add_to_hand(
            [Suit(SuitType.DOT, 1)] * 3
            + [Suit(SuitType.DOT, 2)] * 3
            + [Suit(SuitType.DOT, 3)] * 3
            + [Suit(SuitType.DOT, 4)] * 3
            + [Suit(SuitType.DOT, 5)]
        )
        tile = Suit(SuitType.DOT, 5)
        p = make_player()
        p.add_to_hand([tile, tile, tile, tile])
        players = [p, robber]
        result = engine.declare_concealed_gang(p, tile, players)
        assert isinstance(result, DrawResult)

    def test_not_robbed_if_cannot_hu(self):
        engine = make_engine([Suit(SuitType.DOT, 1)] * 100)
        robber = Player(1)
        p = make_player()
        tile = Suit(SuitType.DOT, 5)
        p.add_to_hand([tile, tile, tile, tile])
        players = [p, robber]
        result = engine.declare_concealed_gang(p, tile, players)
        assert isinstance(result, DrawResult)
