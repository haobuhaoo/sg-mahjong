from backend.entity.game_table import GameTable
from backend.entity.player import Player


def main():
    try:
        all_tiles = GameTable.initialize_table()
        game_table = GameTable(0, all_tiles)
        player_1 = Player(0)
        player_2 = Player(1)
        player_3 = Player(2)
        player_4 = Player(3)
        game_table.deal_starting_tiles(player_1)
        game_table.deal_starting_tiles(player_2)
        game_table.deal_starting_tiles(player_3)
        game_table.deal_starting_tiles(player_4)
        print(repr(player_1))
        print(player_2)
        print(player_3)
        print(player_4)
    except ValueError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
