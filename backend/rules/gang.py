from backend.domain.tiles import Tile


def get_invalid_gang_discards(thrown_tile: Tile) -> set[Tile]:
    """
    For gang melds, determine blocked tiles.

    Rule: Cannot discard the same tile that was claimed to form the gang.

    Args:
        thrown_tile: The tile that was thrown to trigger the gang

    Returns:
        Set of invalid tiles to discard
    """
    return {thrown_tile}
