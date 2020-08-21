import core_classes
import time
from interface import Interface
import random
import json
import copy
import glob


class GameLogic:
    """Содержит основные методы для игры, обеспечивает игровую логику"""
    @staticmethod
    def find_levels():
        levels = glob.glob('*level.txt')
        if not levels:
            raise ValueError("We don't have any levels")
        return levels

    @staticmethod
    def handle_embedding(balls_on_map, ball, last_ball_in_root,
                         next_ball_in_root, enters, exits):
        """Метод обрабатывает встраивания летящего шара в цепочку шаров"""
        for i in range(len(balls_on_map)):
            n = len(balls_on_map[i])

            if (last_ball_in_root[i] and
                    ball == last_ball_in_root[i] or
                    last_ball_in_root[i] is None and
                    ball == core_classes.Ball(enters[i][1], enters[i][0])):
                balls_on_map[i].append(copy.copy(ball))
                return i, n

            if (next_ball_in_root[i] and
                    ball == core_classes.Ball(next_ball_in_root[i][1],
                                              next_ball_in_root[i][0]) or
                    next_ball_in_root[i] is None and ball == core_classes.Ball(
                        exits[i][1], exits[i][0])):
                balls_on_map[i].insert(0, copy.copy(ball))
                return i, 0
            for j in range(n):
                if ball == balls_on_map[i][j]:
                    balls_on_map[i].insert(j, copy.copy(ball))
                    for t in range(j + 1, n):
                        balls_on_map[i][t].x = balls_on_map[i][t + 1].x
                        balls_on_map[i][t].y = balls_on_map[i][t + 1].y
                    balls_on_map[i][n].x = last_ball_in_root[i].x
                    balls_on_map[i][n].y = last_ball_in_root[i].y
                    return i, j
        return None, None

    @staticmethod
    def count_scores(balls_on_map, root_index, ball_position):
        if root_index is None or ball_position is None:
            return 0
        line = balls_on_map[root_index]
        count = 1
        color = line[ball_position].color_number
        index = ball_position + 1
        while index < len(line) and color == line[index].color_number:
            count += 1
            index += 1
        end_index = index - 1
        index = ball_position - 1
        while 0 <= index and color == line[index].color_number:
            count += 1
            index -= 1
        start_index = index + 1
        if count >= 3:
            line = line[:start_index] + line[end_index + 1:]
            balls_on_map[root_index] = line
            return count * 10
        return 0

    @staticmethod
    def process_level(level, score, lives, graphics, level_index):
        """Метод воспороизводит уровень"""
        ticker = 0
        begin = time.perf_counter()
        end = begin
        flying_ball = copy.copy(level._frog.shooting_point)
        last_ball_in_root = []
        next_ball_in_root_with_speed = []
        for i in range(len(level.enters)):
            last_ball_in_root.append(core_classes.Ball(level.enters[i][1],
                                                       level.enters[i][0]))
            next_ball_in_root_with_speed.append((*level.enters[i], 10))
        dead_balls_count = [0] * len(level.roots)
        putted_balls = [0] * len(level.roots)
        speed_segment = 5
        graphics.draw_roots()
        line = None
        while True:
            graphics.wait(level.speed)
            ticker += level.speed
            graphics.draw_consist_items(score, lives, level_index)
            result = graphics.update_win()
            if result:
                line = result[0]
            if line:
                graphics.draw_an_object(line[0][0], line[0][1], " ")
                line.pop(0)
                if len(line) > 0:
                    flying_ball.x = line[0][1]
                    flying_ball.y = line[0][0]
                    root, index = GameLogic.handle_embedding(
                        level._balls_on_map,
                        flying_ball,
                        last_ball_in_root,
                        next_ball_in_root_with_speed, level.enters,
                        level.exits)
                    score_delta = GameLogic.count_scores(
                        level._balls_on_map, root, index)
                    if root is None:
                        graphics.draw_ball(flying_ball)
                    else:
                        putted_balls[root] += 1
                        graphics.draw_roots()
                        graphics.draw_balls_in_root(root)
                        line = []
                        if index == 0:
                            next_ball_in_root_with_speed[root] = next(
                                level._iters[root], None)
                        score += score_delta
                        if score_delta > 0:
                            dead_balls_count[root] += score_delta // 10
                        continue
            else:
                flying_ball = copy.copy(level._frog.shooting_point)
            if ticker % (level.speed * speed_segment * 2) == 0:
                is_dying = False
                graphics.draw_roots()
                for i in range(len(level._balls_on_map)):
                    n = len(level._balls_on_map[i])
                    if n == 0:
                        continue
                    graphics.draw_an_object(level._balls_on_map[i][-1].y,
                                            level._balls_on_map[i][-1].x, "-")
                    last_ball_in_root[i] = core_classes.Ball(
                        level._balls_on_map[i][-1].x,
                        level._balls_on_map[i][-1].y)
                    for j in range(1, n):
                        level._balls_on_map[i][-j].x = level._balls_on_map[i][
                            -j - 1].x
                        level._balls_on_map[i][-j].y = level._balls_on_map[i][
                            -j - 1].y

                    next_position = next_ball_in_root_with_speed[i]
                    next_ball_in_root_with_speed[i] = next(level._iters[i],
                                                           None)
                    if next_position:
                        level._balls_on_map[i][0].x = next_position[1]
                        level._balls_on_map[i][0].y = next_position[0]
                        speed_segment = next_position[2]
                    else:
                        lives -= level.percentage / 100
                        dead_balls_count[i] += 1
                        level._balls_on_map[i].pop(0)
                        if lives < 1e-5:
                            is_dying = True
                            break
                        else:
                            graphics.draw_an_object(0, 3,
                                                    f'Score: {score}, '
                                                    f'Lives: {round(lives)}, '
                                                    f'Level: {level_index}')
                    if (n + dead_balls_count[i] - putted_balls[i] <
                            level._balls_in_root):
                        level._balls_on_map[i].append(
                            core_classes.Ball(
                                level.enters[i][1],
                                level.enters[i][0],
                                random.randint(1,
                                               level.color_number)))
                    graphics.draw_balls_in_root(i)

                if is_dying or sum(map(len, level._balls_on_map)) == 0:
                    end = time.perf_counter()
                    break
        graphics.end_win()
        return score, lives, end - begin

    @staticmethod
    def choose_level(screen, levels):
        """Метод обеспечивает работу меню"""
        levels_count = len(levels)
        pair = Interface.print_levels(screen, levels_count)
        if pair:
            x, y = pair
            if 0 < y <= levels_count and 0 <= x <= 10:
                return y, core_classes.Level.get_level(levels[y])
            if y == levels_count + 1 and 0 <= x <= 10:
                i = random.randint(1, levels_count)
                return i, core_classes.Level.get_level(levels[i - 1])
            if y == levels_count + 2 and 0 <= x <= 25:
                return -1,
            if y == levels_count + 3 and 0 <= x <= 10:
                return 0,
            return None

    @staticmethod
    def save_results(score, filename, level_time, level_index):
        """Метод сохраняет лучшие 9 результатов для каждого уровня"""
        file = f'{filename}{level_index}.json'
        results = core_classes.HighScoreTable.get(file).results
        if results:
            current_result = [score, level_time]
            n = len(results)
            for i in range(n):
                if (results[i][0] == current_result[0] and
                        results[i][1] > current_result[1]):
                    results.insert(i, current_result)
                    break
                elif results[i][0] < current_result[0]:
                    results.insert(i, current_result)
                    break
            if len(results) == n:
                results.append(current_result)
        else:
            results = [[score, level_time]]
        with open(file, 'w') as f:
            json.dump(results[:8 + 1], f)
