import core_classes
import time
from random import randint
from GameJSONEncoder import MyEncoder
import json
import copy
import os


class Game:
    """Содержит основные методы для игры, обеспечивает игровую логику"""
    def __init__(self, level, balls=None, flying_balls=None,
                 lines=None, putted_balls=None, dead_balls=None, time=0):
        if level is None:
            raise ValueError("Level is empty. Initialize it first")
        level.validate_level()
        self.next_ball_in_root_with_speed = []
        self.indexes = [0] * len(level.enters)
        self._level = level
        self.time = time
        self.lines = lines
        self.flying_balls = flying_balls
        self.balls_in_frog = []
        self.balls_on_map = balls
        self.putted_balls = putted_balls
        self.dead_balls = dead_balls
        self.validate_gamestate()

    def __eq__(self, other):
        pass

    def validate_gamestate(self):
        if self._level._frog and len(self._level._frog.shoot_balls) == 2:
            self.balls_in_frog = self._level._frog.shoot_balls
        else:
            raise ValueError("Invalid frog in level")
        if self.balls_on_map:
            if len(self.balls_on_map) != len(self._level.roots):
                raise ValueError("Invalid state")
            for i in range(len(self._level.roots)):
                first_ball = self.balls_on_map[i][0]
                self.indexes[i] = -1
                for j in range(len(self._level.roots[i])):
                    if (self._level.roots[i][j][1] == first_ball.x and
                            self._level.roots[i][j][0] == first_ball.y):
                        self.indexes[i] = j + 1
                        break
                if self.indexes[i] == -1:
                    if (self._level.enters[i][1] == first_ball.x and
                            self._level.enters[i][0] == first_ball.y):
                        self.indexes[i] = 0
                    elif (self._level.exits[i][1] == first_ball.x and
                          self._level.exits[i][0] == first_ball.y):
                        self.indexes[i] = len(self._level.roots[i]) + 1
                    else:
                        raise ValueError("Invalid state")
                if self.indexes[i] >= len(self._level.roots[i]):
                    self.next_ball_in_root_with_speed.append(
                        (*self._level.exits[i], 10))
                else:
                    self.next_ball_in_root_with_speed.append(
                        self._level.roots[i][self.indexes[i]])
        else:
            self.balls_on_map = []
            for i in range(len(self._level.exits)):
                color = randint(1, self._level.color_number)
                self.balls_on_map.append([core_classes.Ball(
                    self._level.enters[i][1],
                    self._level.enters[i][0], color)])
                self.next_ball_in_root_with_speed.append(
                    self._level.roots[i][0])
        if self.flying_balls:
            if self.lines and len(self.lines) == len(self.flying_balls):
                for i in range(len(self.lines)):
                    if (self.lines[i][0] != self.flying_balls[i].y or
                            self.lines[i][1] != self.flying_balls[i].x):
                        raise ValueError("Invalid state")
            else:
                raise ValueError("Invalid state")
        else:
            if self.lines:
                raise ValueError("Invalid state")
            self.flying_balls = []
            self.lines = []
        if self.time < 0:
            raise ValueError("Invalid state")
        if self.putted_balls:
            if (self.dead_balls is None or
                    len(self.putted_balls) != len(self._level.roots) or
                    len(self.dead_balls) != len(self._level.roots)):
                raise ValueError("Invalid state")
        else:
            if self.dead_balls:
                raise ValueError("Invalid state")
            self.putted_balls = [0] * len(self._level.roots)
            self.dead_balls = [0] * len(self._level.roots)
        for i in range(len(self._level.roots)):
            if (len(self.balls_on_map[i]) + self.dead_balls[i] -
                    self.putted_balls[i] > self._level._balls_in_root):
                raise ValueError("Invalid state")

    def handle_embedding(self, ball):
        """Метод обрабатывает встраивания летящего шара в цепочку шаров"""
        for i in range(len(self.balls_on_map)):
            n = len(self.balls_on_map[i])
            for j in range(self.indexes[i], self.indexes[i] - n - 2, -1):
                if j >= len(self._level.roots[i]):
                    if (ball.x == self._level.exits[i][1] and
                            ball.y == self._level.exits[i][0]):
                        self.balls_on_map[i].insert(0, ball)
                        return i, 0
                elif j < 0:
                    if (ball.x == self._level.enters[i][1] and
                            ball.y == self._level.enters[i][0]):
                        self.balls_on_map[i].append(ball)
                        return i, n
                else:
                    if (ball.x == self._level.roots[i][j][1] and
                            ball.y == self._level.roots[i][j][0]):
                        self.balls_on_map[i].insert(max(0, self.indexes[i] -
                                                        j - 1),
                                                    ball)
                        if (j != self.indexes[i] and
                                self.indexes[i] - 1 - n != j):
                            for k in range(j - 1, self.indexes[i] - n - 2, -1):
                                if k >= len(self._level.roots[i]):
                                    self.balls_on_map[i][
                                        self.indexes[i] - 1 - k].set_x_y(
                                        self._level.exits[i][1],
                                        self._level.exits[i][0])
                                elif k < 0:
                                    self.balls_on_map[i][
                                        self.indexes[i] - 1 - k].set_x_y(
                                        self._level.enters[i][1],
                                        self._level.enters[i][0])
                                else:
                                    self.balls_on_map[i][
                                        self.indexes[i] - 1 - k].set_x_y(
                                        self._level.roots[i][k][1],
                                        self._level.roots[i][k][0])
                        return i, max(0, self.indexes[i] - j - 1)
        return None, None

    def count_scores(self, root_index, ball_position):
        """Считает очки"""
        if root_index is None or ball_position is None:
            return 0
        line = self.balls_on_map[root_index]
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
            self.balls_on_map[root_index] = line
            return count * 10
        return 0

    def process_level(self, score, lives, graphics):
        """Метод воспороизводит уровень"""
        if lives == 0:
            graphics.no_lives()
        begin = time.perf_counter()
        ticker = 0
        speed_segment = 5
        graphics.draw_roots()
        while True:
            graphics.wait(self._level.speed)
            ticker += self._level.speed
            graphics.draw_consist_items(score, lives, self._level.index)
            result = graphics.update_win()
            if result:
                if result[0] == "shoot":
                    self.lines.append(result[1][0])
                    self.flying_balls.append(copy.copy(
                        self._level._frog.shooting_point))
                    graphics.next_ball()
                if result == 'save':
                    self.time = time.perf_counter() - begin
                    self.save_game()
            if self.lines:
                i = -1
                for line in self.lines:
                    i += 1
                    graphics.draw_an_object(line[0][0], line[0][1], " ")
                    if len(line) == 1:
                        self.lines.remove(line)
                        self.flying_balls.pop(i)
                        continue
                    else:
                        line.pop(0)
                    self.flying_balls[i].set_x_y(line[0][1], line[0][0])
                    root, index = self.handle_embedding(
                        self.flying_balls[i])
                    if root is None:
                        graphics.draw_ball(self.flying_balls[i])
                    else:
                        score_delta = self.count_scores(root, index)
                        self.putted_balls[root] += 1
                        graphics.draw_roots()
                        for rout in self.balls_on_map:
                            graphics.draw_balls_in_root(rout)
                        self.lines.pop(i)
                        self.flying_balls.pop(i)
                        if index == 0:
                            self.next_ball_in_root_with_speed[root] = \
                                self.set_next_ball_with_speed(root)
                        score += score_delta
                        if len(self.balls_on_map[root]) == 0:
                            self.indexes[root] = len(self._level.roots[root])
                        if score_delta > 0:
                            self.dead_balls[root] += score_delta // 10
            if ticker % (self._level.speed * speed_segment * 2) == 0:
                is_dying = False
                graphics.draw_roots()
                for i in range(len(self.balls_on_map)):
                    n = len(self.balls_on_map[i])
                    if n == 0:
                        continue
                    graphics.draw_an_object(self.balls_on_map[i][-1].y,
                                            self.balls_on_map[i][-1].x, "-")
                    speed_segment = self.next_ball_in_root_with_speed[i][2]
                    self.next_ball_in_root_with_speed[i] = \
                        self.move_balls_get_next_position(i)
                    if self.indexes[i] > len(self._level.roots[i]):
                        lives -= self._level.percentage / 100
                        self.dead_balls[i] += 1
                        self.balls_on_map[i].pop(0)
                        if lives < 1e-5:
                            is_dying = True
                            break
                        else:
                            graphics.draw_an_object(0, 3,
                                                    f'Score: {score}, '
                                                    f'Lives: {round(lives)}, '
                                                    f'Level: '
                                                    f'{self._level.index}')

                    if (n + self.dead_balls[i] - self.putted_balls[i] <
                            self._level._balls_in_root):
                        self.add_new_ball(i)
                    graphics.draw_balls_in_root(self.balls_on_map[i])
                if is_dying or sum(map(len, self.balls_on_map)) == 0:
                    end = time.perf_counter()
                    break
        graphics.end_win()
        return score, lives, end - begin + self.time

    def add_new_ball(self, index):
        """Метод добавляет новый шар в маршрут"""
        self.balls_on_map[index].append(core_classes.Ball(
            self._level.enters[index][1], self._level.enters[index][0],
            randint(1, self._level.color_number)))

    def move_balls_get_next_position(self, index):
        """Обновляет позицию всех шаров"""
        self.balls_on_map[index][0].set_x_y(
            self.next_ball_in_root_with_speed[index][1],
            self.next_ball_in_root_with_speed[index][0])
        next = self.set_next_ball_with_speed(index)
        self.indexes[index] = min(self.indexes[index] + 1,
                                  len(self._level.roots[index]) + 1)
        self.move_balls_except_first(index)
        return next

    def move_balls_except_first(self, index):
        """Обновляет позицию всех шаров, кроме первого"""
        for j in range(1, len(self.balls_on_map[index])):
            k = self.indexes[index] - 1 - j
            if k > len(self._level.roots[index]):
                self.balls_on_map[index][j].set_x_y(
                    self._level.exits[index][1],
                    self._level.exits[index][0])
            elif k < 0:
                self.balls_on_map[index][j].set_x_y(
                    self._level.enters[index][1],
                    self._level.enters[index][0])
            else:
                self.balls_on_map[index][j].set_x_y(
                    self._level.roots[index][k][1],
                    self._level.roots[index][k][0])

    def set_next_ball_with_speed(self, index_root):
        """Сдвигает указатель на первую позицию шара в маршруте,
        если указатель выходит за границу маршрута, выставляет значение
        default"""
        self.indexes[index_root] = min(self.indexes[index_root] + 1,
                                       len(self._level.roots[index_root]) + 1)
        if self.indexes[index_root] < len(self._level.roots[index_root]):
            return self._level.roots[index_root][self.indexes[index_root]]
        return (*self._level.exits[index_root], 10)

    def save_game(self):
        """Сохранение текущей партии в файл"""
        filename = f"{self._level.index}levelGameState.txt"
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "a") as f:
            for attr in self.__dict__.keys():
                if not attr.startswith('_'):
                    f.write(f'"{attr}":'
                            f' '
                            f'{json.dumps(getattr(self, attr), cls=MyEncoder)}'
                            f',\n')

    @staticmethod
    def get_game(filename):
        """Получение уровня из файла"""
        if not os.path.isfile(filename):
            raise RuntimeError("Level do not exist")
        try:
            index = int(filename[0])
        except ValueError as e:
            raise ValueError("Invalid filename", e)
        with open(filename, 'r') as f:
            data = f.readlines()
        game = Game(core_classes.Level.get_level(f'{index}level.txt'))
        for line in data:
            attr, str_value = line.split(":")
            attr = attr[1:-1]
            str_value = str_value[1:-2]
            value = json.loads(str_value)
            setattr(game, attr, value)
        game.validate_gamestate()
        return game
