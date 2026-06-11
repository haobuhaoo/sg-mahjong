from backend.domain.player import Player
from backend.domain.tiles import WindType


def calculate_score(
    player: Player,
    prevalent_wind: WindType,
    seat_wind: WindType,
) -> int:
    """
    Calculate the score (tai) for a winning hand.

    Args:
        player: The player that wins
        prevalent_wind: The current prevalent wind
        seat_wind: The player's seat wind

    Returns:
        Total tai score
    """
    # TODO: implement scoring logic
    return 0
