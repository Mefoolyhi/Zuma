from interface import Interface
import curses
from game_logic import GameLogic
from core_classes import HighScoreTable
import math

scores_files = "score"


def main(screen):
    score = 0
    lives = 5
    Interface.init_curses()
    levels_path = GameLogic.find_levels()
    while True:
        pair = GameLogic.choose_level(screen, levels_path,
                                      Interface.print_menu)
        if pair:
            i = pair[0]
            if i == -2:
                Interface.clean_screen(screen)
                # магазин
                break
            if i == -1:
                Interface.clean_screen(screen)
                pair2 = GameLogic.choose_level(screen, levels_path,
                                               Interface.print_only_levels)
                if pair2:
                    i = pair2[0]
                    if i > 0:
                        table = HighScoreTable.get(
                            f'{scores_files}{i}.json')
                        Interface.draw_high_score_table_level(screen,
                                                              table.results,
                                                              i)
                        Interface.wait_for_reaction(screen)
                continue
            level = pair[1]
            Interface.clean_screen(screen)
            graphics = Interface(level, screen)
            score, lives, time = GameLogic.process_level(level, score, lives,
                                                         graphics, i)
            graphics.print_results(score, time)
            GameLogic.save_results(score, scores_files, time, i)
            lives = math.floor(lives)
            if lives == 0:
                graphics.game_over()
                break


if __name__ == "__main__":
    curses.wrapper(main)
