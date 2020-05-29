from Interface import Interface
import curses
import game_logic
import math

levels_count = 2
scores_files = "score"


def main(screen):
    score = 0
    lives = 5
    Interface.init_curses()
    while True:
        pair = game_logic.choose_level(screen, levels_count)
        if pair:
            i = pair[0]
            if i == 0:
                Interface.clean_screen(screen)
                break
            if i == -1:
                Interface.clean_screen(screen)
                index_begin = 0
                for j in range(levels_count):
                    current_results = game_logic.get_results(''.join([
                        scores_files, str(j + 1), '.json']))
                    if current_results:
                        Interface.draw_high_score_table_level(screen,
                                                              current_results,
                                                              j + 1,
                                                              index_begin)
                        index_begin += len(current_results) + 5
                continue
            level = pair[1]
            graphics = Interface(level)
            score, lives, time = game_logic.process_level(level, score, lives,
                                                          graphics, i)
            Interface.print_results(screen, score, time)
            game_logic.save_results(score, scores_files, time, i)
            lives = math.floor(lives)
            if lives == 0:
                Interface.game_over(screen)
                break


if __name__ == "__main__":
    curses.wrapper(main)