from backend.domain.game_state import GameState
from backend.domain.player import Player
from backend.domain.tiles import Suit, WindType
from backend.engine.round_engine import RoundEngine
from backend.utils.errors import DiscardError, InvalidActionError


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
                try:
                    if round_manager.can_hu_discard(thrown_tile, other, plist):
                        claimed = True
                        print(other)
                        print("---")
                        print(game_table)
                        print("\n")
                        break
                    if round_manager.can_gang_discard(thrown_tile, other):
                        thrown_tile = round_manager.gang_tile(other, thrown_tile, plist)
                        round_manager.finalize_discard(thrown_tile, other, plist)
                        claimed = True
                        print(other)
                        print("---")
                        print(game_table)
                        print("\n")
                        break
                    if round_manager.can_pong_discard(thrown_tile, other):
                        thrown_tile = round_manager.pong_tile(other, thrown_tile)
                        round_manager.finalize_discard(thrown_tile, other, plist)
                        claimed = True
                        print(other)
                        print("---")
                        print(game_table)
                        print("\n")
                        break
                    if (
                        (p.position + 1) % 4 == other.position
                        and isinstance(thrown_tile, Suit)
                        and round_manager.can_chi_discard(thrown_tile, other)
                    ):
                        thrown_tile = round_manager.chi_tile(other, thrown_tile)
                        round_manager.finalize_discard(thrown_tile, other, plist)
                        claimed = True
                        print(other)
                        print("---")
                        print(game_table)
                        print("\n")
                        break
                except InvalidActionError as err:
                    print(f"------               Invalid action error: {err}")
                    pass
                except DiscardError as err:
                    print(f"------               Discard error: {err}")
                    pass
            if not claimed:
                round_manager.finalize_discard(thrown_tile, p, plist)
        print(game_table)
    except Exception as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
