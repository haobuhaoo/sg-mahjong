from backend.entity.game_table import GameTable
from backend.entity.player import Player
from backend.entity.tiles import (
    Animal,
    AnimalType,
    Dragon,
    DragonType,
    Flower,
    FlowerType,
    Season,
    SeasonType,
    Suit,
    SuitType,
    Wind,
    WindType,
)


def main():
    try:
        all_tiles = GameTable.initialize_table()
        game_table = GameTable(0, WindType.DONG, all_tiles)
        player_1 = Player(0)
        player_2 = Player(1)
        player_3 = Player(2)
        player_4 = Player(3)
        game_table.deal_starting_tiles(player_1)
        game_table.deal_starting_tiles(player_2)
        game_table.deal_starting_tiles(player_3)
        game_table.deal_starting_tiles(player_4)
        plist = [player_1, player_2, player_3, player_4]

        # t = Suit(SuitType.DOT, 2)
        # t = Dragon(DragonType.FA)
        # player_1.add_tai()
        # player_1.add_tai()
        # player_1.hand_tile = []
        # player_1.open_tile = [t, t, t]
        # player_1.add_to_hand([t, Suit(SuitType.DOT, 8), Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 5)])
        # print(player_1.check_hand(3, t))
        # print(game_table.chi_tile(player_1, t))
        # print(player_1)
        # print(player_1.hand_tile)
        # print(player_1.open_tile)
        # return

        for _ in range(5):
            for idx, p in enumerate(plist):
                tile_idx = p.pick_tile_to_discard()
                thrown_tile = game_table.player_discard_tile(p, tile_idx)
                for other in plist:
                    if other == p:
                        continue
                    hu, gang, pong, chi = other.check_hand(idx, thrown_tile)
                    if gang or pong:
                        print(f"{"gang " if gang else "pong "}" + thrown_tile.__str__())
                        # print(thrown_tile)
                        thrown_tile = (
                            game_table.gang_tile(other, thrown_tile)
                            if gang
                            else game_table.pong_tile(other, thrown_tile)
                        )
                        game_table.add_to_discard_tile(thrown_tile, other)
                        print(other)
                        print("---")
                        print(game_table)
                        print("\n")
                        # return
                    elif chi:
                        print("chi " + thrown_tile.__str__())
                        # print(thrown_tile)
                        thrown_tile = game_table.chi_tile(other, thrown_tile)
                        game_table.add_to_discard_tile(thrown_tile, other)
                        print(other)
                        print("---")
                        print(game_table)
                        print("\n")
                        # return
                game_table.add_to_discard_tile(thrown_tile, p)
                game_table.player_draw_tile(plist[(idx + 1) % 4])
        print(game_table)
        # print(player_1)
    except Exception as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
