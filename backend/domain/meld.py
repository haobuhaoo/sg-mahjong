from dataclasses import dataclass, field

from backend.domain.tiles import Tile


@dataclass
class Meld:
    """A revealed meld (chi, pong, or gang) with its exposure status.

    Attributes:
        tiles: The tiles that make up this meld.
        is_exposed: True if this meld was formed using a tile claimed from a
            discard (chi, pong, exposed gang, pong-upgrade gang). False only
            for concealed gangs.
    """

    tiles: list[Tile] = field(default_factory=list)
    is_exposed: bool = False
