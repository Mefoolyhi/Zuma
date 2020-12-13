"""Содержит основные классы для работы"""

import algorithms
from random import randint
import os
import json


class Level:
    """Класс уровня"""
    def __init__(self, frog_right_up_corner=(0, 0), enters=None, exits=None,
                 color_number=0,
                 roots=None, balls_number=0, field_height=0,
                 field_width=0, percentage=0, speed=0):
        if roots is None:
            roots = []
        if exits is None:
            exits = []
        if enters is None:
            enters = []
        self.enters = enters
        self.exits = exits
        # max - 8, дальше цвета странные какие-то
        self.color_number = color_number
        self.roots = roots
        self.balls_number = balls_number
        self.field_height = field_height
        self.field_width = field_width
        self.percentage = percentage
        self.frog_right_up_corner = frog_right_up_corner
        self.speed = speed
        self._frog = None
        self._balls_in_root = 0

    def end_creating_level(self):
        """Валидация корректности заданного уровня"""
        try:
            self._balls_in_root = self.balls_number // len(self.enters)
            if len(self.frog_right_up_corner) != 2:
                raise ValueError("Ошибка в задании лягушки")
            self._frog = Frog(*self.frog_right_up_corner,
                              self.color_number)
            if len(self.enters) != len(self.exits) != len(self.roots):
                raise ValueError("Количество входов, выходов и путей не"
                                 "совпадает")
            for i in range(len(self.enters)):
                if len(self.enters[i]) != 2 or len(self.exits[i]) != 2:
                    raise ValueError("Ошибка в координатах входов и выходов")
                for j in range(len(self.roots[i])):
                    if len(self.roots[i][j]) != 3:
                        raise ValueError("Ошибка в задании путей")
        except BaseException as e:
            print("Invalid Level")
            raise e

    def __eq__(self, other):
        if (len(self.exits) != len(other.exits) !=
                len(self.enters) != len(other.enters) !=
                len(self.roots) != len(other.roots)):
            return False
        for i in range(len(self.enters)):
            if (self.enters[i][0] != other.enters[i][0] or
                    self.enters[i][1] != other.enters[i][1]):
                return False
            if (self.exits[i][0] != other.exits[i][0] or
                    self.exits[i][1] != other.exits[i][1]):
                return False
            for j in range(len(self.roots[i])):
                if (self.roots[i][j][0] != other.roots[i][j][0] or
                        self.roots[i][j][1] != other.roots[i][j][1] or
                        self.roots[i][j][2] != other.roots[i][j][2]):
                    return False
        if (self.frog_right_up_corner[0] != other.frog_right_up_corner[0] or
            self.frog_right_up_corner[1] != other.frog_right_up_corner[1] or
                self.color_number != other.color_number or
                self.speed != other.speed or
                abs(self.percentage - other.percentage) > 1e-3 or
                self.field_width != other.field_width or
                self.field_height != other.field_height or
                self.balls_number != other.balls_number):
            return False
        return True

    @staticmethod
    def get_level(filename):
        """Получение уровня из файла"""
        if not os.path.isfile(filename):
            raise RuntimeError("Level do not exist")
        with open(filename, 'r') as f:
            data = f.readlines()
        level = Level()
        for line in data:
            attr, str_value = line.split(":")
            attr = attr[1:-1]
            str_value = str_value[1:-2]
            value = json.loads(str_value)
            setattr(level, attr, value)
        level.end_creating_level()
        return level

    @staticmethod
    def put_level(index, level):
        """Загрузка уровня в файл"""
        filename = f"{index}level.txt"
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "a") as f:
            for attr in level.__dict__.keys():
                if not attr.startswith('_'):
                    f.write(f'"{attr}": {json.dumps(getattr(level, attr))},\n')


class Ball:
    """Класс шара"""
    def __init__(self, x, y, color_number=0):
        self.x = x
        self.y = y
        self.color_number = color_number

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return self.x * 2971215073 + self.y * 28657 + self.color_number

    def __str__(self):
        return f"x={self.x}, y={self.y}, color number {self.color_number}"

    def __copy__(self):
        return Ball(self.x, self.y, self.color_number)

    def set_x_y(self, x, y):
        self.x = x
        self.y = y


class Frog:
    """Класс стреляющей лягушки"""
    def __init__(self, x, y, color_number):
        self.right_up_corner = (x, y)
        self.shooting_point = Ball(x + 1, y, randint(1, color_number))
        self.shoot_balls = [self.shooting_point, Ball(x + 1, y + 1,
                                                      randint(1,
                                                              color_number))]

    def __str__(self):
        return f"({self.right_up_corner[0]}, {self.right_up_corner[1]})"

    def shoot(self, x, y, field):
        """
        Метод возвращает список точек, через которые идет траектория шара
        от начальной до края поля

        level -- уровень, на котором сейчас игрок
        x, y -- точка, куда выстрелил игрок, через нее будет проходить
        траектория

        Возвращает:
        список точек на растровом поле, которые лежат на луче, начинающемся
        в точке стрельбы уровня,
        проходит через заданную точку и упирается в край поля

        """
        return algorithms.get_vector_to_the_end(width=field[1],
                                                height=field[0],
                                                x1=x, y1=y,
                                                x0=self.shooting_point.x,
                                                y0=self.shooting_point.y)


class HighScoreTable:
    """"Класс описывает таблицу рекордов"""
    def __init__(self, results=None):
        if results:
            self.results = results
        else:
            self.results = []

    @staticmethod
    def get(filename):
        """Метод возвращает таблицу результатов из файла"""
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                results = json.load(f)
        else:
            results = None
        return HighScoreTable(results)


class Game:
    def __init__(self, level):
        pass


