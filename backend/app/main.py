from backend.entity.game_table import GameTable
from backend.entity.player import Player


def main():
    try:
        all_tiles = GameTable.initialize_table()
        game_table = GameTable(0, all_tiles)
        player = Player(0)
        game_table.deal_starting_tiles(player)
        print(player)
    except ValueError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
