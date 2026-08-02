from backend.domain.tiles import Tile


def get_invalid_pong_discards(thrown_tile: Tile) -> set[Tile]:
    """
    For pong melds, determine blocked tiles.

    Rule: Cannot discard the same tile that was claimed to form the pong.

    Args:
        thrown_tile: The tile that was thrown to trigger the pong.

    Returns:
        Set of invalid tiles to discard.
    """
    return {thrown_tile}
