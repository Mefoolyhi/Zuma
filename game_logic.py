"""Содержит основные методы для игры, обеспечивает игровую логику"""

import core_classes
import time
from Interface import Interface
import level_parser
import random
import json
import os.path


def handle_embedding(balls_on_map, ball, last_ball_in_root, next_ball_in_root):
    """Метод обрабатывает встраивания летящего шара в цепочку шаров"""
    for i in range(len(balls_on_map)):
        n = len(balls_on_map[i])
        if ball == last_ball_in_root[i]:
            balls_on_map[i].insert(0, ball)
            return i, 0
        if (len(next_ball_in_root) > i and
                ball == core_classes.Ball(next_ball_in_root[i][1],
                                          next_ball_in_root[i][0])):
            balls_on_map[i].append(ball)
            return i, n
        for j in range(n):
            if ball == balls_on_map[i][j]:
                balls_on_map[i].insert(max(j + 1, 0), ball)
                for t in range(j, 0, -1):
                    balls_on_map[i][t].x = balls_on_map[i][t - 1].x
                    balls_on_map[i][t].y = balls_on_map[i][t - 1].y
                balls_on_map[i][0].x = last_ball_in_root[i].x
                balls_on_map[i][0].y = last_ball_in_root[i].y
                return i, max(j + 1, 0)
    return None, None


def count_scores(balls_on_map, root_index, ball_position):
    if root_index is None or ball_position is None:
        return 0
    line = balls_on_map[root_index]
    count = 1
    color = Interface.get_color_pair(line[ball_position])
    index = ball_position + 1
    while index < len(line) and color == Interface.get_color_pair(line[index]):
        count += 1
        index += 1
    end_index = index - 1
    index = ball_position - 1
    while 0 <= index and color == Interface.get_color_pair(line[index]):
        count += 1
        index -= 1
    start_index = index + 1
    if count >= 3:
        line = line[:start_index] + line[end_index + 1:]
        balls_on_map[root_index] = line
        return count * 10
    return 0


def process_level(level, score, lives, graphics, index):
    """Метод воспороизводит уровень"""
    ticker = 0
    begin = time.perf_counter()
    flying_ball = core_classes.Ball(level.frog.shooting_point.x,
                                    level.frog.shooting_point.y,
                                    level.balls_number + 3)
    last_ball_in_root = []
    next_ball_in_root_with_speed = []
    dead_balls_count = [0] * len(level.roots)
    speed_segment = 5
    graphics.draw_roots()
    while True:
        graphics.wait(level.speed)
        ticker += level.speed
        graphics.draw_consist_items(score, lives, index)
        line = graphics.update_win()
        if line and len(line) > 0:
            graphics.draw_an_object(line[0][0], line[0][1], " ")
            flying_ball.x = line[0][1]
            flying_ball.y = line[0][0]
            score += count_scores(level.balls_on_map, *handle_embedding(
                level.balls_on_map,
                flying_ball,
                last_ball_in_root,
                next_ball_in_root_with_speed))
            line.pop(0)
            if len(line) > 0:
                graphics.draw_ball(flying_ball)
            else:
                graphics.set_flying_ball_color(flying_ball)
                flying_ball = core_classes.Ball(level.frog.shooting_point.x,
                                                level.frog.shooting_point.y,
                                                level.balls_number + 3)
        if ticker % (level.speed * speed_segment) == 0:
            is_dying = False
            graphics.draw_roots()
            for i in range(len(level.balls_on_map)):
                n = len(level.balls_on_map[i])
                if n == 0:
                    break
                graphics.draw_an_object(level.balls_on_map[i][-1].y,
                                        level.balls_on_map[i][-1].x, "-")
                last_ball_in_root.append(
                    core_classes.Ball(level.balls_on_map[i][-1].x,
                                      level.balls_on_map[i][-1].y))
                for j in range(1, n):
                    level.balls_on_map[i][-j].x = level.balls_on_map[i][
                        -j - 1].x
                    level.balls_on_map[i][-j].y = level.balls_on_map[i][
                        -j - 1].y
                    graphics.draw_ball(level.balls_on_map[i][-j])

                if len(next_ball_in_root_with_speed) > i:
                    next_position = next_ball_in_root_with_speed[i]
                    next_ball_in_root_with_speed[i] = next(level.iters[i],
                                                           None)
                else:
                    next_position = (*level.enters[i],
                                     10)
                    next_ball_in_root_with_speed.append(next(level.iters[i],
                                                             None))
                if next_position:
                    level.balls_on_map[i][0].x = next_position[1]
                    level.balls_on_map[i][0].y = next_position[0]
                    graphics.draw_ball(level.balls_on_map[i][0])
                    speed_segment = next_position[2]
                else:
                    lives -= level.percentage / 100
                    dead_balls_count[i] += 1
                    level.balls_on_map[i].pop(0)
                    if lives < 1e-5:
                        is_dying = True
                        break
                    else:
                        graphics.draw_an_object(0, 3,
                                                f'Score: {score}, '
                                                f'Lives: {round(lives)}, '
                                                f'Level: {index}')
                if n + dead_balls_count[i] < level.balls_in_root:
                    level.balls_on_map[i].append(
                        core_classes.Ball(level.enters[i][1],
                                          level.enters[i][0],
                                          level.balls_in_root * i + n))

            if is_dying or sum(map(len, level.balls_on_map)) == 0:
                end = time.perf_counter()
                break
    graphics.end_win()
    return score, lives, end - begin


def choose_level(screen, levels_count):
    """Метод обеспечивает работу меню"""
    x, y = Interface.print_levels(screen, levels_count)
    if y:
        if 0 < y <= levels_count and 0 <= x <= 10:
            return y, level_parser.get_level(y)
        if y == levels_count + 1 and 0 <= x <= 10:
            i = random.randint(1, levels_count)
            return i, level_parser.get_level(i)
        if y == levels_count + 2 and 0 <= x <= 25:
            return -1,
        if y == levels_count + 3 and 0 <= x <= 10:
            return 0,
        return None


def get_results(file):
    """Метод возвращает таблицу результатов"""
    if os.path.isfile(file):
        with open(file, 'r') as f:
            results = json.load(f)
    else:
        results = None
    return results


def save_results(score, filename, level_time, level_index):
    """Метод сохраняет лучшие 9 результатов для каждого уровня"""
    file = f'{filename}{level_index}.json'
    results = get_results(file)
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
