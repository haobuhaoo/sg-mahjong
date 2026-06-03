from backend.entity.game_table import GameTable
from backend.entity.player import Player


def main():
    try:
        allTiles = GameTable.initialize_table()
        game_table = GameTable(0, allTiles)
        player = Player()
        game_table.dealStartingTiles(0, player)
        print(player)
    except ValueError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
