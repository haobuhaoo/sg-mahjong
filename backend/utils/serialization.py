from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import Tile


def serialize_tile(tile: Tile) -> dict:
    """Serialize a tile to a JSON-compatible dict."""
    return {"type": type(tile).__name__, "repr": repr(tile)}


def serialize_player(player: Player) -> dict:
    """Serialize a player's state to a JSON-compatible dict."""
    return {
        "position": player.position,
        "seat_wind": player.seat_wind.value,
        "tai": player.tai,
        "hand_tile": [serialize_tile(t) for t in player.hand_tile],
        "open_tile": [serialize_tile(t) for t in player.get_open_tiles()],
        "bonus_tile": [serialize_tile(t) for t in player.bonus_tile],
    }


def serialize_game_state(state: GameState) -> dict:
    """Serialize the shared game state to a JSON-compatible dict."""
    return {
        "num_players": state.num_players,
        "prevalent_wind": state.prevalent_wind.value,
        "current_player": state.current_player,
        "discarded_tiles": [serialize_tile(t) for t in state.discarded_tiles],
    }
