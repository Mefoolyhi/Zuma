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
        pair = GameLogic.choose_level(screen, levels_path)
        if pair:
            i = pair[0]
            if i == 0:
                Interface.clean_screen(screen)
                break
            if i == -1:
                Interface.clean_screen(screen)
                index_begin = 0
                for j in range(len(levels_path)):
                    current_highscoretable = HighScoreTable.get(
                        f'{scores_files}{j + 1}.json')
                    if current_highscoretable:
                        Interface.draw_high_score_table_level(
                            screen,
                            current_highscoretable.results,
                            j + 1,
                            index_begin)
                        index_begin += len(current_highscoretable.results) + 6
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
