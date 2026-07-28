from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import Animal, Dragon, Flower, Season, Tile, Wind
from backend.rules.hu_result import HandPattern


def serialize_tile(tile: Tile) -> dict:
    """Serialize a tile to a JSON-compatible dict."""
    return {"type": type(tile).__name__, "repr": repr(tile)}


def serialize_player(
    player: Player,
    *,
    conceal_hand: bool,
    patterns: frozenset[HandPattern],
    requester_position: int | None,
) -> dict:
    """
    Serialize a player's state to a JSON-compatible dict.

    Include hand tiles (filtered when `conceal_hand` is True and the requester is not the winner),
    open melds (grouped per meld), bonus tiles, the most-recently drawn tile and bonus tiles (for
    frontend visibility), and a breakdown of bonus tile counts by category (animals, flowers,
    seasons).
    """
    if conceal_hand and requester_position != player.position:
        hand_tile = _filter_concealed_tiles(player.hand_tile, patterns)
    else:
        hand_tile = player.hand_tile

    return {
        "position": player.position,
        "seat_wind": player.seat_wind.value,
        "tai": player.tai,
        "hand_tile": [serialize_tile(t) for t in hand_tile],
        "open_tile": [
            {
                "tiles": [serialize_tile(t) for t in meld.tiles],
                "is_exposed": meld.is_exposed,
            }
            for meld in player.open_tile
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


def _filter_concealed_tiles(hand_tiles: list[Tile], patterns: frozenset[HandPattern]) -> list[Tile]:
    """
    When a player wins by Three Great Scholars or Four Great Blessings shortcut and must conceal
    non-justifying tiles, return only the tiles that belong to the shortcut pattern: Dragons for
    Three Great Scholars or Winds for Four Great Blessings.
    """
    has_tgs = HandPattern.THREE_GREAT_SCHOLARS in patterns
    has_fgb = HandPattern.FOUR_GREAT_BLESSINGS in patterns

    if has_tgs and has_fgb:
        return [t for t in hand_tiles if isinstance(t, (Dragon, Wind))]

    if has_tgs:
        return [t for t in hand_tiles if isinstance(t, Dragon)]

    if has_fgb:
        return [t for t in hand_tiles if isinstance(t, Wind)]

    return hand_tiles


def serialize_game_state(state: GameState) -> dict:
    """Serialize the shared game state to a JSON-compatible dict."""
    return {
        "num_players": state.num_players,
        "prevalent_wind": state.prevalent_wind.value,
        "current_player": state.current_player,
        "discarded_tiles": [serialize_tile(t) for t in state.discarded_tiles],
    }
