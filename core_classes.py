"""Содержит основные классы для работы"""


import algorithms


class Level:
    """Класс уровня"""
    def __init__(self, frog_right_up_corner, enters, exits, color_number,
                 roots, balls_number, field_height,
                 field_width, percentage, speed):
        self.enters = enters
        self.exits = exits
        # max - 8, дальше цвета странные какие-то
        self.color_number = color_number
        self.roots = roots
        self.iters = [iter(root) for root in roots]
        self.balls_number = balls_number
        self.field_height = field_height
        self.field_width = field_width
        self.balls_in_root = self.balls_number // len(self.enters)
        self.balls_on_map = []
        self.frog = Frog(*frog_right_up_corner, balls_number + 1)
        self.percentage = percentage
        self.speed = speed
        for i in range(len(self.enters)):
            self.balls_on_map.append([Ball(self.enters[i][1], self.enters[i][
                0], i * self.balls_in_root)])


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


class Frog:
    """Класс стреляющей лягушки"""
    def __init__(self, x, y, color_number):
        self.right_up_corner = (x, y)
        self.shooting_point = Ball(x + 1, y, color_number)
        self.shoot_balls = [self.shooting_point, Ball(x + 1, y + 1,
                                                      color_number + 1)]

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
                                                x0=self.right_up_corner[0],
                                                y0=self.right_up_corner[1] + 1)
