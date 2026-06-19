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
    Animal,
    AnimalType,
    Season,
    SeasonType,
)
from backend.utils.serialization import (
    serialize_tile,
    serialize_player,
    serialize_game_state,
)


class TestSerializeTile:
    def test_suit(self):
        result = serialize_tile(Suit(SuitType.DOT, 5))
        assert result == {"type": "Suit", "repr": "Suit(SuitType.DOT, 5)"}

    def test_wind(self):
        result = serialize_tile(Wind(WindType.DONG))
        assert result == {"type": "Wind", "repr": "Wind(WindType.DONG)"}

    def test_dragon(self):
        result = serialize_tile(Dragon(DragonType.ZHONG))
        assert result == {"type": "Dragon", "repr": "Dragon(DragonType.ZHONG)"}

    def test_flower(self):
        result = serialize_tile(Flower(FlowerType.PLUM))
        assert result["type"] == "Flower"

    def test_animal(self):
        result = serialize_tile(Animal(AnimalType.CAT))
        assert result["type"] == "Animal"

    def test_season(self):
        result = serialize_tile(Season(SeasonType.SPRING))
        assert result["type"] == "Season"

    def test_returns_dict(self):
        result = serialize_tile(Suit(SuitType.DOT, 1))
        assert isinstance(result, dict)
        assert "type" in result
        assert "repr" in result


class TestSerializePlayer:
    def test_returns_all_keys(self):
        p = Player(0)
        result = serialize_player(p)
        assert set(result.keys()) == {
            "position",
            "seat_wind",
            "tai",
            "hand_tile",
            "open_tile",
            "bonus_tile",
        }

    def test_position(self):
        p = Player(2)
        result = serialize_player(p)
        assert result["position"] == 2

    def test_seat_wind(self):
        p = Player(2)
        result = serialize_player(p)
        assert result["seat_wind"] == WindType.XI.value

    def test_tai(self):
        p = Player(0, tai=3)
        result = serialize_player(p)
        assert result["tai"] == 3

    def test_empty_hand_and_open_and_bonus(self):
        p = Player(0)
        result = serialize_player(p)
        assert result["hand_tile"] == []
        assert result["open_tile"] == []
        assert result["bonus_tile"] == []

    def test_hand_tiles_serialized(self):
        p = Player(0)
        p.add_to_hand([Suit(SuitType.DOT, 1), Suit(SuitType.DOT, 2)])
        result = serialize_player(p)
        assert len(result["hand_tile"]) == 2
        assert result["hand_tile"][0]["type"] == "Suit"

    def test_open_tiles_serialized(self):
        p = Player(0)
        p.add_open_tile([Suit(SuitType.DOT, 1)])
        result = serialize_player(p)
        assert len(result["open_tile"]) == 1
        assert result["open_tile"][0]["type"] == "Suit"

    def test_bonus_tiles_serialized(self):
        p = Player(0)
        p.add_bonus_tile([Flower(FlowerType.PLUM)])
        result = serialize_player(p)
        assert len(result["bonus_tile"]) == 1
        assert result["bonus_tile"][0]["type"] == "Flower"


class TestSerializeGameState:
    def test_returns_all_keys(self):
        state = GameState(3, WindType.DONG, GameState.initialize_wall())
        result = serialize_game_state(state)
        assert set(result.keys()) == {
            "num_players",
            "prevalent_wind",
            "current_player",
            "discarded_tiles",
        }

    def test_num_players(self):
        state = GameState(3, WindType.DONG, GameState.initialize_wall())
        result = serialize_game_state(state)
        assert result["num_players"] == 3

    def test_prevalent_wind(self):
        state = GameState(3, WindType.NAN, GameState.initialize_wall())
        result = serialize_game_state(state)
        assert result["prevalent_wind"] == WindType.NAN.value

    def test_current_player(self):
        state = GameState(3, WindType.DONG, GameState.initialize_wall())
        result = serialize_game_state(state)
        assert result["current_player"] == 0

    def test_empty_discard_pile(self):
        state = GameState(3, WindType.DONG, GameState.initialize_wall())
        result = serialize_game_state(state)
        assert result["discarded_tiles"] == []

    def test_discarded_tiles_serialized(self):
        state = GameState(3, WindType.DONG, GameState.initialize_wall())
        state.add_to_discard_pile(Suit(SuitType.DOT, 1))
        state.add_to_discard_pile(Wind(WindType.DONG))
        result = serialize_game_state(state)
        assert len(result["discarded_tiles"]) == 2
