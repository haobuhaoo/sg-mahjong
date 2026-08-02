import pytest

from backend.domain.game_state import GameState
from backend.domain.tiles import (
    Animal,
    AnimalType,
    Bonus,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
    Honor,
    Season,
    SeasonType,
    Suit,
    SuitType,
    Wind,
    WindType,
)
from backend.utils.helper import is_bonus_tile


def make_wall():
    return GameState.initialize_wall()


def make_state(num_players=3, prevalent_wind=WindType.DONG):
    return GameState(num_players, prevalent_wind, make_wall())


class TestInit:
    def test_valid_num_players(self):
        for n in range(4):
            state = GameState(n, WindType.DONG, make_wall())
            assert state.num_players == n

    def test_invalid_num_players_negative(self):
        with pytest.raises(ValueError, match="Number of players must be between 0 and 3"):
            GameState(-1, WindType.DONG, make_wall())

    def test_invalid_num_players_too_high(self):
        with pytest.raises(ValueError, match="Number of players must be between 0 and 3"):
            GameState(4, WindType.DONG, make_wall())

    def test_default_current_player(self):
        state = make_state()
        assert state.current_player == 0

    def test_discarded_tiles_empty_initially(self):
        state = make_state()
        assert state.discarded_tiles == []

    def test_prevalent_wind_set_correctly(self):
        for wind in WindType:
            state = GameState(3, wind, make_wall())
            assert state.prevalent_wind == wind

    def test_all_tiles_stored(self):
        wall = make_wall()
        state = GameState(3, WindType.DONG, wall)
        assert state.all_tiles is wall

    def test_internal_indices_initialized(self):
        state = make_state()
        assert state._start_idx == 3 * 16 + 4 + 1
        assert state._end_idx == -1


class TestInitializeWall:
    def test_total_tile_count(self):
        wall = GameState.initialize_wall()
        assert len(wall) == 148

    def test_contains_suit_tiles(self):
        wall = GameState.initialize_wall()
        suits = [t for t in wall if isinstance(t, Suit)]
        assert len(suits) == 108

    def test_contains_honor_tiles(self):
        wall = GameState.initialize_wall()
        honors = [t for t in wall if isinstance(t, (Wind, Dragon))]
        assert len(honors) == 28

    def test_contains_bonus_tiles(self):
        wall = GameState.initialize_wall()
        bonuses = [t for t in wall if isinstance(t, Bonus)]
        assert len(bonuses) == 12

    def test_is_shuffled_by_default(self):
        walls = [GameState.initialize_wall() for _ in range(5)]
        first_wall = walls[0]
        assert any(w != first_wall for w in walls[1:])


class TestCreateSuitTiles:
    def test_count(self):
        suits = GameState._create_suit_tiles()
        assert len(suits) == 27

    def test_all_numbers_present(self):
        suits = GameState._create_suit_tiles()
        for st in SuitType:
            for n in range(1, 10):
                assert Suit(st, n) in suits


class TestCreateHonorTiles:
    def test_count(self):
        honors = GameState._create_honor_tiles()
        assert len(honors) == 7

    def test_winds_present(self):
        honors = GameState._create_honor_tiles()
        for wind in WindType:
            assert Wind(wind) in honors

    def test_dragons_present(self):
        honors = GameState._create_honor_tiles()
        for dragon in DragonType:
            assert Dragon(dragon) in honors


class TestCreateBonusTiles:
    def test_count(self):
        bonuses = GameState._create_bonus_tiles()
        assert len(bonuses) == 12

    def test_animals_present(self):
        bonuses = GameState._create_bonus_tiles()
        for animal in AnimalType:
            assert Animal(animal) in bonuses

    def test_flowers_present(self):
        bonuses = GameState._create_bonus_tiles()
        for flower in FlowerType:
            assert Flower(flower) in bonuses

    def test_seasons_present(self):
        bonuses = GameState._create_bonus_tiles()
        for season in SeasonType:
            assert Season(season) in bonuses


class TestDrawTile:
    def test_returns_tile(self):
        state = make_state()
        tile = state.draw_tile()
        TileLike = Suit, Honor, Bonus
        assert isinstance(tile, TileLike)

    def test_advances_start_index(self):
        state = make_state()
        idx_before = state._start_idx
        state.draw_tile()
        assert state._start_idx == idx_before + 1

    def test_returns_correct_tile_from_wall(self):
        state = make_state()
        expected = state.all_tiles[state._start_idx]
        tile = state.draw_tile()
        assert tile is expected

    def test_multiple_draws_advance_correctly(self):
        state = make_state()
        tiles = [state.draw_tile() for _ in range(10)]
        assert len(tiles) == 10
        TileLike = Suit, Honor, Bonus
        assert all(isinstance(t, TileLike) for t in tiles)

    def test_raises_index_error_when_wall_exhausted(self):
        wall = [Suit(SuitType.DOT, 1)] * 5
        state = GameState(0, WindType.DONG, wall)
        state._start_idx = len(wall)
        with pytest.raises(IndexError):
            state.draw_tile()


class TestReplaceTile:
    def test_returns_tile(self):
        state = make_state()
        tile = state.replace_tile()
        TileLike = Suit, Honor, Bonus
        assert isinstance(tile, TileLike)

    def test_retreats_end_index(self):
        state = make_state()
        idx_before = state._end_idx
        state.replace_tile()
        assert state._end_idx == idx_before - 1

    def test_returns_correct_tile_from_end(self):
        state = make_state()
        expected = state.all_tiles[state._end_idx]
        tile = state.replace_tile()
        assert tile is expected

    def test_multiple_replacements_retreat_correctly(self):
        state = make_state()
        tiles = [state.replace_tile() for _ in range(10)]
        assert len(tiles) == 10
        TileLike = Suit, Honor, Bonus
        assert all(isinstance(t, TileLike) for t in tiles)

    def test_raises_index_error_when_dead_wall_exhausted(self):
        wall = [Suit(SuitType.DOT, 1)] * 5
        state = GameState(0, WindType.DONG, wall)
        state._end_idx = -6
        with pytest.raises(IndexError):
            state.replace_tile()


class TestAddToDiscardPile:
    def test_appends_tile(self):
        state = make_state()
        tile = Suit(SuitType.DOT, 1)
        state.add_to_discard_pile(tile)
        assert state.discarded_tiles == [tile]

    def test_multiple_tiles_appended(self):
        state = make_state()
        tiles = [Suit(SuitType.DOT, i) for i in range(1, 6)]
        for t in tiles:
            state.add_to_discard_pile(t)
        assert state.discarded_tiles == tiles

    def test_does_not_modify_other_state(self):
        state = make_state()
        prev_player = state.current_player
        tile = Suit(SuitType.DOT, 1)
        state.add_to_discard_pile(tile)
        assert state.current_player == prev_player


class TestAdvancePlayer:
    def test_cycles_0_to_1(self):
        state = make_state()
        state.advance_player(0)
        assert state.current_player == 1

    def test_cycles_1_to_2(self):
        state = make_state()
        state.advance_player(1)
        assert state.current_player == 2

    def test_cycles_2_to_3(self):
        state = make_state()
        state.advance_player(2)
        assert state.current_player == 3

    def test_cycles_3_to_0(self):
        state = make_state()
        state.advance_player(3)
        assert state.current_player == 0

    def test_full_cycle(self):
        state = make_state()
        pos = 0
        for _ in range(8):
            state.advance_player(pos)
            pos = (pos + 1) % 4
            assert state.current_player == pos


class TestGetStartingTileIndices:
    def test_position_0_returns_14_indices(self):
        state = make_state()
        indices = state.get_starting_tile_indices(0)
        assert len(indices) == 14

    def test_position_1_returns_13_indices(self):
        state = make_state()
        indices = state.get_starting_tile_indices(1)
        assert len(indices) == 13

    def test_position_2_returns_13_indices(self):
        state = make_state()
        indices = state.get_starting_tile_indices(2)
        assert len(indices) == 13

    def test_position_3_returns_13_indices(self):
        state = make_state()
        indices = state.get_starting_tile_indices(3)
        assert len(indices) == 13

    def test_all_indices_unique(self):
        state = make_state()
        all_indices = []
        for pos in range(4):
            all_indices.extend(state.get_starting_tile_indices(pos))
        assert len(all_indices) == len(set(all_indices))

    def test_position_0_includes_extra_tile(self):
        state = make_state()
        indices_p0 = state.get_starting_tile_indices(0)
        indices_p1 = state.get_starting_tile_indices(1)
        assert len(indices_p0) == len(indices_p1) + 1


class TestSplitStartingTiles:
    def test_returns_tuple_of_lists(self):
        state = make_state()
        indices = state.get_starting_tile_indices(0)
        hand, bonuses = state.split_starting_tiles(indices)
        assert isinstance(hand, list)
        assert isinstance(bonuses, list)

    def test_bonus_tiles_separated(self):
        wall = make_wall()
        state = GameState(3, WindType.DONG, wall)
        indices = state.get_starting_tile_indices(0)
        hand, bonuses = state.split_starting_tiles(indices)
        for t in bonuses:
            assert is_bonus_tile(t)
        for t in hand:
            assert not is_bonus_tile(t)

    def test_total_tiles_preserved(self):
        state = make_state()
        indices = state.get_starting_tile_indices(0)
        hand, bonuses = state.split_starting_tiles(indices)
        assert len(hand) + len(bonuses) == len(indices)

    def test_with_no_bonus_tiles_in_indices(self):
        wall = [
            Suit(SuitType.CHARACTER, 1),
            Suit(SuitType.DOT, 2),
            Suit(SuitType.BAMBOO, 3),
        ]
        state = GameState(0, WindType.DONG, wall)
        hand, bonuses = state.split_starting_tiles([0, 1, 2])
        assert len(hand) == 3
        assert len(bonuses) == 0

    def test_raises_index_error_on_out_of_bounds_index(self):
        wall = [Suit(SuitType.DOT, 1)] * 5
        state = GameState(0, WindType.DONG, wall)
        with pytest.raises(IndexError):
            state.split_starting_tiles([0, 1, 999])


class TestDrawUntilNonBonus:
    def test_returns_non_bonus_tile_when_first_is_not_bonus(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        state = GameState(0, WindType.DONG, wall)
        collector_called = []

        def collector(tile):
            collector_called.append(tile)
            return is_bonus_tile(tile)

        tile = state.draw_until_non_bonus(collector)
        assert not is_bonus_tile(tile)
        assert len(collector_called) == 1
        assert not is_bonus_tile(collector_called[0])

    def test_collector_called_for_bonus_tiles(self):
        wall = (
            [Suit(SuitType.CHARACTER, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 50
        )
        state = GameState(0, WindType.DONG, wall)
        collected = []

        def collector(tile):
            collected.append(tile)
            return is_bonus_tile(tile)

        tile = state.draw_until_non_bonus(collector)
        assert not is_bonus_tile(tile)
        assert len(collected) == 2
        assert isinstance(collected[0], Flower)
        assert not is_bonus_tile(collected[1])

    def test_multiple_consecutive_bonus_tiles(self):
        wall = (
            [Suit(SuitType.CHARACTER, 1)] * 53
            + [Flower(FlowerType.PLUM)]
            + [Suit(SuitType.DOT, 1)] * 40
        )
        wall[-1] = Flower(FlowerType.ORCHID)
        state = GameState(0, WindType.DONG, wall)
        collected = []

        def collector(tile):
            collected.append(tile)
            return is_bonus_tile(tile)

        tile = state.draw_until_non_bonus(collector)
        assert not is_bonus_tile(tile)
        assert len(collected) == 3
        assert isinstance(collected[0], Flower)
        assert isinstance(collected[1], Flower)
        assert not is_bonus_tile(collected[2])

    def test_gang_mode_draws_from_dead_wall(self):
        wall = [Suit(SuitType.DOT, 1)] * 100
        state = GameState(0, WindType.DONG, wall)
        end_idx_before = state._end_idx
        start_idx_before = state._start_idx

        def collector(tile):
            return False

        tile = state.draw_until_non_bonus(collector, is_gang=True)
        assert state._end_idx < end_idx_before
        assert state._start_idx == start_idx_before
        assert tile is wall[end_idx_before]

    def test_gang_mode_with_bonus_tile(self):
        wall = [Suit(SuitType.CHARACTER, 1)] * 53 + [Suit(SuitType.DOT, 1)] * 40
        wall[-1] = Flower(FlowerType.PLUM)
        state = GameState(0, WindType.DONG, wall)
        collected = []

        def collector(tile):
            collected.append(tile)
            return is_bonus_tile(tile)

        tile = state.draw_until_non_bonus(collector, is_gang=True)
        assert not is_bonus_tile(tile)
        assert len(collected) == 2
        assert isinstance(collected[0], Flower)
        assert not is_bonus_tile(collected[1])

    def test_raises_index_error_when_live_wall_exhausted(self):
        wall = [Suit(SuitType.DOT, 1)] * 5
        state = GameState(0, WindType.DONG, wall)
        state._start_idx = len(wall)

        def collector(tile):
            return False

        with pytest.raises(IndexError):
            state.draw_until_non_bonus(collector)

    def test_raises_index_error_when_dead_wall_exhausted_during_bonus_loop(self):
        wall = [Flower(FlowerType.PLUM)] * 58
        state = GameState(0, WindType.DONG, wall)

        def collector(tile):
            return is_bonus_tile(tile)

        with pytest.raises(IndexError):
            state.draw_until_non_bonus(collector)


class TestStrAndRepr:
    def test_str_contains_prevalent_wind(self):
        state = GameState(3, WindType.NAN, make_wall())
        s = str(state)
        assert WindType.NAN.value in s

    def test_str_contains_current_player(self):
        state = make_state()
        s = str(state)
        assert "Player 1" in s

    def test_str_contains_discard_pile_label(self):
        state = make_state()
        s = str(state)
        assert "Discard pile" in s

    def test_str_with_discarded_tiles(self):
        state = make_state()
        state.add_to_discard_pile(Suit(SuitType.DOT, 1))
        s = str(state)
        assert "1 Tong" in s

    def test_repr_contains_class_name(self):
        state = make_state()
        r = repr(state)
        assert "GameState" in r

    def test_repr_contains_num_players(self):
        state = GameState(2, WindType.DONG, make_wall())
        r = repr(state)
        assert "num_players=2" in r


class TestTurnCount:
    def test_initial_turn_count_zero(self):
        state = make_state()
        assert state.turn_count == 0

    def test_advance_turn_increments(self):
        state = make_state()
        state.advance_turn()
        assert state.turn_count == 1
        state.advance_turn()
        state.advance_turn()
        assert state.turn_count == 3


class TestWallExhaustion:
    def make_custom_wall(self, tile_count=60):
        return [Suit(SuitType.DOT, 1)] * tile_count

    def test_last_live_tile_idx_initial(self):
        wall = self.make_custom_wall(100)
        state = GameState(0, WindType.DONG, wall)
        assert state._last_live_tile_idx == 84

    def test_last_live_tile_idx_after_replacements(self):
        wall = self.make_custom_wall(100)
        state = GameState(0, WindType.DONG, wall)
        state.replace_tile()
        state.replace_tile()
        assert state._last_live_tile_idx == 82

    def test_remaining_live_tiles_initial(self):
        wall = self.make_custom_wall(100)
        state = GameState(0, WindType.DONG, wall)
        assert state.remaining_live_tiles == 32

    def test_remaining_live_tiles_after_draw(self):
        wall = self.make_custom_wall(100)
        state = GameState(0, WindType.DONG, wall)
        state.draw_tile()
        assert state.remaining_live_tiles == 31

    def test_remaining_live_tiles_after_replacements(self):
        wall = self.make_custom_wall(100)
        state = GameState(0, WindType.DONG, wall)
        state.replace_tile()
        state.replace_tile()
        assert state.remaining_live_tiles == 30

    def test_remaining_live_tiles_never_negative(self):
        wall = self.make_custom_wall(68)
        state = GameState(0, WindType.DONG, wall)
        state.draw_tile()
        assert state.remaining_live_tiles == 0

    def test_is_last_live_tile_true(self):
        wall = self.make_custom_wall(69)
        state = GameState(0, WindType.DONG, wall)
        assert state.is_last_live_tile is True

    def test_is_last_live_tile_false(self):
        wall = self.make_custom_wall(100)
        state = GameState(0, WindType.DONG, wall)
        assert state.is_last_live_tile is False

    def test_is_live_wall_exhausted_false(self):
        wall = self.make_custom_wall(69)
        state = GameState(0, WindType.DONG, wall)
        assert state.is_live_wall_exhausted is False

    def test_is_live_wall_exhausted_true_after_last_draw(self):
        wall = self.make_custom_wall(69)
        state = GameState(0, WindType.DONG, wall)
        state.draw_tile()
        assert state.is_live_wall_exhausted is True
