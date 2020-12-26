from interface import Interface
import curses
from game import Game
from core_classes import HighScoreTable, Level
import math
from random import randint

scores_files = "score"


def choose_menu_option(screen, levels, printingmethod):
    """Метод обеспечивает работу меню"""
    levels_count = len(levels)
    pair = printingmethod(screen, levels_count)
    if pair:
        x, y = pair
        if 0 < y <= levels_count and 0 <= x <= 10:
            return y, Level.get_level(levels[y - 1])
        if y == levels_count + 1 and 0 <= x <= 10:
            i = randint(1, levels_count)
            return i, Level.get_level(levels[i - 1])
        if y == levels_count + 2 and 0 <= x <= 25:
            return -1,
        if y == levels_count + 3 and 0 <= x <= 10:
            return -2,
        return None


def main(screen):
    score = 0
    lives = 5
    Interface.init_curses()
    levels_path = Level.find_levels()
    while True:
        pair = choose_menu_option(screen, levels_path,
                                  Interface.print_menu)
        if pair:
            i = pair[0]
            if i == -2:
                Interface.clean_screen(screen)
                # магазин
                break
            if i == -1:
                Interface.clean_screen(screen)
                pair2 = choose_menu_option(screen, levels_path,
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
            game = Game(level)
            score, lives, time = game.process_level(score, lives, graphics)
            graphics.print_results(score, time)
            HighScoreTable.save_results(score, scores_files, time, i)
            lives = math.floor(lives)
            if lives == 0:
                graphics.no_lives()


if __name__ == "__main__":
    curses.wrapper(main)
