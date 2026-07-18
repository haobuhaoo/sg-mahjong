from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import Animal, Flower, Season, Tile


def serialize_tile(tile: Tile) -> dict:
    """Serialize a tile to a JSON-compatible dict."""
    return {"type": type(tile).__name__, "repr": repr(tile)}


def serialize_player(player: Player) -> dict:
    """
    Serialize a player's state to a JSON-compatible dict.

    Includes hand tiles, open melds (grouped per meld), bonus tiles, the
    most-recently drawn tile and bonus tiles (for frontend visibility), and a
    breakdown of bonus tile counts by category (animals, flowers, seasons).
    """
    return {
        "position": player.position,
        "seat_wind": player.seat_wind.value,
        "tai": player.tai,
        "hand_tile": [serialize_tile(t) for t in player.hand_tile],
        "open_tile": [
            [serialize_tile(t) for t in meld] for meld in player.open_tile
        ],
        "bonus_tile": [serialize_tile(t) for t in player.bonus_tile],
        "drawn_tile": serialize_tile(player.drawn_tile) if player.drawn_tile else None,
        "drawn_bonus_tiles": [serialize_tile(t) for t in player.drawn_bonus_tiles],
        "bonus_count": {
            "animals": sum(1 for t in player.bonus_tile if isinstance(t, Animal)),
            "flowers": sum(1 for t in player.bonus_tile if isinstance(t, Flower)),
            "seasons": sum(1 for t in player.bonus_tile if isinstance(t, Season)),
        },
    }


def serialize_game_state(state: GameState) -> dict:
    """Serialize the shared game state to a JSON-compatible dict."""
    return {
        "num_players": state.num_players,
        "prevalent_wind": state.prevalent_wind.value,
        "current_player": state.current_player,
        "discarded_tiles": [serialize_tile(t) for t in state.discarded_tiles],
    }
