from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import (
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
from backend.engine.round_engine import RoundEngine


def main():
    try:
        all_tiles = GameState.initialize_wall()
        game_table = GameState(0, WindType.DONG, all_tiles)
        round_manager = RoundEngine(game_table)
        player_1 = Player(0)
        player_2 = Player(1)
        player_3 = Player(2)
        player_4 = Player(3)
        round_manager.deal_starting_tiles(player_1)
        round_manager.deal_starting_tiles(player_2)
        round_manager.deal_starting_tiles(player_3)
        round_manager.deal_starting_tiles(player_4)
        plist = [player_1, player_2, player_3, player_4]

        # t = Suit(SuitType.DOT, 2)
        # t = Dragon(DragonType.FA)
        # player_1.add_tai()
        # player_1.add_tai()
        # player_1.hand_tile = []
        # player_1.open_tile = [t, t, t]
        # player_1.add_to_hand([t, Suit(SuitType.DOT, 8), Suit(SuitType.DOT, 3), Suit(SuitType.DOT, 4), Suit(SuitType.DOT, 5)])
        # print(player_1.check_hand(3, t))
        # print(round_manager.chi_tile(player_1, t))
        # print(player_1)
        # print(player_1.hand_tile)
        # print(player_1.open_tile)
        # return

        skip_draw = True
        for _ in range(20):
            p = plist[game_table.current_player]
            if not skip_draw:
                round_manager.player_draw_tile(p, plist)
            skip_draw = False
            tile_idx = p.pick_tile_to_discard()
            thrown_tile = round_manager.player_discard_tile(p, tile_idx)
            claimed = False
            for other in plist:
                if other is p:
                    continue
                hu, gang, pong, chi = other.check_hand(p.position, thrown_tile)
                if gang or pong:
                    print(f"{"gang " if gang else "pong "}" + thrown_tile.__str__())
                    thrown_tile = (
                        round_manager.gang_tile(other, thrown_tile, plist)
                        if gang
                        else round_manager.pong_tile(other, thrown_tile)
                    )
                    round_manager.finalize_discard(thrown_tile, other)
                    claimed = True
                    print(other)
                    print("---")
                    print(game_table)
                    print("\n")
                    break
                elif chi:
                    print("chi " + thrown_tile.__str__())
                    thrown_tile = round_manager.chi_tile(other, thrown_tile)
                    round_manager.finalize_discard(thrown_tile, other)
                    claimed = True
                    print(other)
                    print("---")
                    print(game_table)
                    print("\n")
                    break
            if not claimed:
                round_manager.finalize_discard(thrown_tile, p)
        print(game_table)
        # print(player_1)
    except Exception as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
