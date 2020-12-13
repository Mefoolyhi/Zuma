import core_classes
import time
from random import randint
import json
import copy
import glob


class GameLogic:
    """Содержит основные методы для игры, обеспечивает игровую логику"""

    @staticmethod
    def find_levels():
        """Ищет уровни"""
        levels = glob.glob('*level.txt')
        if not levels:
            raise ValueError("We don't have any levels")
        return levels

    @staticmethod
    def handle_embedding(balls_on_map, ball, indexes, roots, enters, exits):
        """Метод обрабатывает встраивания летящего шара в цепочку шаров"""
        for i in range(len(balls_on_map)):
            n = len(balls_on_map[i])
            for j in range(indexes[i], indexes[i] - n - 2, -1):
                if j >= len(roots[i]):
                    if (ball.x == exits[i][1] and
                            ball.y == exits[i][0]):
                        balls_on_map[i].insert(0, ball)
                        return i, 0
                elif j < 0:
                    if (ball.x == enters[i][1] and
                            ball.y == enters[i][0]):
                        balls_on_map[i].append(ball)
                        return i, n
                else:
                    if (ball.x == roots[i][j][1] and
                            ball.y == roots[i][j][0]):
                        balls_on_map[i].insert(max(0, indexes[i] - j - 1),
                                               ball)
                        if j != indexes[i] and indexes[i] - 1 - n != j:
                            for k in range(j - 1, indexes[i] - n - 2, -1):
                                if k >= len(roots[i]):
                                    balls_on_map[i][
                                        indexes[i] - 1 - k].set_x_y(
                                        exits[i][1], exits[i][0])
                                elif k < 0:
                                    balls_on_map[i][
                                        indexes[i] - 1 - k].set_x_y(
                                        enters[i][1], enters[i][0])
                                else:
                                    balls_on_map[i][
                                        indexes[i] - 1 - k].set_x_y(
                                        roots[i][k][1], roots[i][k][0])
                        return i, max(0, indexes[i] - j - 1)
        return None, None

    @staticmethod
    def count_scores(balls_on_map, root_index, ball_position):
        """Считает очки"""
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
        flying_balls = []
        balls_on_map = []
        indexes = [0] * len(level.enters)

        next_ball_in_root_with_speed = []
        for i in range(len(level.exits)):
            color = randint(1, level.color_number)
            balls_on_map.append([core_classes.Ball(level.enters[i][1],
                                                   level.enters[i][0],
                                                   color)])
            next_ball_in_root_with_speed.append(level.roots[i][0])
        dead_balls_count = [0] * len(level.roots)
        putted_balls = [0] * len(level.roots)
        speed_segment = 5
        graphics.draw_roots()
        lines = []
        while True:
            graphics.wait(level.speed)
            ticker += level.speed
            graphics.draw_consist_items(score, lives, level_index)
            result = graphics.update_win()
            if result:
                if result[0] == "shoot":
                    lines.append(result[1][0])
                    flying_balls.append(copy.copy(level._frog.shooting_point))
                    graphics.next_ball()
                if result[0] == "save":
                    level.save_game(level)
            if lines:
                i = -1
                for line in lines:
                    i += 1
                    graphics.draw_an_object(line[0][0], line[0][1], " ")
                    if len(line) == 1:
                        lines.remove(line)
                        flying_balls.pop(i)
                        continue
                    else:
                        line.pop(0)
                    flying_balls[i].set_x_y(line[0][1], line[0][0])
                    root, index = GameLogic.handle_embedding(
                        balls_on_map,
                        flying_balls[i],
                        indexes,
                        level.roots, level.enters,
                        level.exits)
                    if root is None:
                        graphics.draw_ball(flying_balls[i])
                    else:
                        score_delta = GameLogic.count_scores(
                            balls_on_map, root, index)
                        putted_balls[root] += 1
                        graphics.draw_roots()
                        for rout in balls_on_map:
                            graphics.draw_balls_in_root(rout)
                        lines.pop(i)
                        flying_balls.pop(i)
                        if index == 0:
                            next_ball_in_root_with_speed[root] = \
                                GameLogic.set_next_ball_with_speed(
                                    indexes[root],
                                    len(level.roots[root]),
                                    level.roots[root],
                                    level.exits[root]
                                )
                            indexes[root] = min(indexes[root] + 1,
                                                len(level.roots[root]) + 1)
                        score += score_delta
                        if len(balls_on_map[root]) == 0:
                            indexes[root] = len(level.roots[root])
                        if score_delta > 0:
                            dead_balls_count[root] += score_delta // 10
            if ticker % (level.speed * speed_segment * 2) == 0:
                is_dying = False
                graphics.draw_roots()
                for i in range(len(balls_on_map)):
                    n = len(balls_on_map[i])
                    if n == 0:
                        continue
                    graphics.draw_an_object(balls_on_map[i][-1].y,
                                            balls_on_map[i][-1].x, "-")
                    speed_segment = next_ball_in_root_with_speed[i][2]
                    next_ball_in_root_with_speed[i], indexes[i] = \
                        GameLogic.move_balls_get_next_position(
                            balls_on_map[i],
                            next_ball_in_root_with_speed[i],
                            indexes[i],
                            level.roots[i],
                            level.exits[i],
                            level.enters[i])
                    if indexes[i] > len(level.roots[i]):
                        lives -= level.percentage / 100
                        dead_balls_count[i] += 1
                        balls_on_map[i].pop(0)
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
                        GameLogic.add_new_ball(balls_on_map[i],
                                               level.enters[i],
                                               level.color_number)
                    graphics.draw_balls_in_root(balls_on_map[i])
                if is_dying or sum(map(len, balls_on_map)) == 0:
                    end = time.perf_counter()
                    break
        graphics.end_win()
        return score, lives, end - begin

    @staticmethod
    def add_new_ball(balls_on_map, enter, color_number):
        """Метод добавляет новый шар в маршрут"""
        balls_on_map.append(core_classes.Ball(enter[1], enter[0],
                                              randint(1, color_number)))

    @staticmethod
    def move_balls_get_next_position(balls_on_map, next_position, index,
                                     root, exit, enter):
        """Обновляет позицию всех шаров"""
        balls_on_map[0].set_x_y(next_position[1], next_position[0])
        next = GameLogic.set_next_ball_with_speed(index, len(root), root,
                                                  (*exit, 10))
        index = min(index + 1, len(root) + 1)
        GameLogic.move_balls_except_first(root,
                                          len(balls_on_map), balls_on_map,
                                          index, enter, exit)
        return next, index

    @staticmethod
    def move_balls_except_first(rout, n, balls_on_map, index, enter, exit):
        """Обновляет позицию всех шаров, кроме первого"""
        for j in range(1, n):
            k = index - 1 - j
            if k > len(rout):
                balls_on_map[j].set_x_y(exit[1], exit[0])
            elif k < 0:
                balls_on_map[j].set_x_y(enter[1], enter[0])
            else:
                balls_on_map[j].set_x_y(rout[k][1], rout[k][0])

    @staticmethod
    def set_next_ball_with_speed(index, n, rout, default):
        """Сдвигает указатель на первую позицию шара в маршруте,
        если указатель выходит за границу маршрута, выставляет значение
        default"""
        index += 1
        if index < n:
            return rout[index]
        return default

    @staticmethod
    def choose_level(screen, levels, printingmethod):
        """Метод обеспечивает работу меню"""
        levels_count = len(levels)
        pair = printingmethod(screen, levels_count)
        if pair:
            x, y = pair
            if 0 < y <= levels_count and 0 <= x <= 10:
                return y, core_classes.Level.get_level(levels[y - 1])
            if y == levels_count + 1 and 0 <= x <= 10:
                i = randint(1, levels_count)
                return i, core_classes.Level.get_level(levels[i - 1])
            if y == levels_count + 2 and 0 <= x <= 25:
                return -1,
            if y == levels_count + 3 and 0 <= x <= 10:
                return -2,
            return None

    @staticmethod
    def save_game():
        pass

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
