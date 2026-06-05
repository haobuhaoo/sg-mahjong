import random

from backend.entity.game_table import GameTable
from backend.entity.player import Player
from backend.entity.tiles import WindType


def main():
    try:
        all_tiles = GameTable.initialize_table()
        game_table = GameTable(0, WindType.DONG, all_tiles)
        player_1 = Player(0)
        game_table.deal_starting_tiles(player_1)
        print(player_1)
        ran = random.Random(1)
        for _ in range(20):
            game_table.player_discard_tile(player_1, ran.randint(0, 13))
            game_table.player_draw_tile(player_1)
        print(game_table)
        print(player_1)

        # player_2 = Player(1)
        # player_3 = Player(2)
        # player_4 = Player(3)
        # game_table.deal_starting_tiles(player_2)
        # game_table.deal_starting_tiles(player_3)
        # game_table.deal_starting_tiles(player_4)
        # print(player_2)
        # print(player_3)
        # print(player_4)
    except ValueError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
