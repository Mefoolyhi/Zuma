"""Модуль тестирования"""

import unittest
from game_logic import GameLogic
import core_classes
import algorithms
import copy
import json
import os


class TestAlgorithms(unittest.TestCase):
    """Класс тестирует алгоритмы, находящиеся в модуле algorithms"""

    def test_line(self):
        """Метод содержит тестовые случаи и запускает теситрование"""
        test_cases = [[(1, 1), (11, 2)], [(0, 0), (1, 3)], [(1, 8), (2, 10)],
                      [(35, 0), (37, 3)], [(1, 1), (3, 0)],
                      [(2, 4), (0, 6)], [(11, 6), (3, 10)], [(11, 4), (10, 9)],
                      [(11, 11), (3, 5)],
                      [(10, 1), (8, 6)], [(10, 1), (3, 1)], [(11, 5), (13, 5)],
                      [(3, 11), (3, 5)],
                      [(3, 7), (3, 10)], [(3, 10), (3, 10)]]
        for test in test_cases:
            result = self.check_line_from_point_to_point(*test)
            self.assertEqual(1, len(result))
            self.assertTrue(result[0])

            result = self.check_line_from_point_to_border(12, 40, *test)
            self.assertEqual(1, len(result))
            self.assertTrue(result[0])

    def check_line_from_point_to_point(self, a, b):
        """
        Метод проверяет корректность отрезка от А до Б
        """
        result = algorithms.algo_for_drawing_lines(*a, *b)
        dy = b[1] - a[1]
        dx = b[0] - a[0]
        self.assertEqual(a[::-1], result[0])
        self.assertEqual(b[::-1], result[-1])
        return self.check_if_point_connected(result, dx, dy, a[0], a[1])

    def check_line_from_point_to_border(self, height, width, a, b):
        """
        Метод проверяет корректность отрезка от точки А, проходящего через
        точку Б, до одной из границ поля

        :param height: высота поля
        :param width: ширина поля
        :param a: координаты точки А (x, y)
        :param b: координаты точки Б (x, y)
        """
        if a == b:
            b = (a[0], a[1] + 1)
        result, error = algorithms.get_vector_to_the_end(height, width, *a, *b)
        self.assertEqual(a[::-1], result[0])
        self.assertEqual(True, result[-1][0] == 0 or
                         result[-1][0] == height - 1 or
                         result[-1][1] == 0 or result[-1][1] == width - 1)
        return self.check_if_point_connected(result, result[-1][1] - a[0],
                                             result[-1][0] - a[1], a[0], a[1],
                                             error)

    def check_if_point_connected(self, line, dx, dy, x, y, error=0):
        """
        Метод проверяет связность растрового отрезка

        :param line: отрезок, связность которого проверяется
        :param dx: разность координат х начальной и конечной точек отрезка
        :param dy:разность координат у начальной и конечной точек отрезка
        :param x: координата х начальной точки
        :param y: координата у начальной точки
        :param error: корректировка точности вычислений
        :return: пару (bool -- связен ли отрезок, (у, х) -- координаты точки,
        на которой связность прервалась, если отрезок не связен)
        """
        prev_point = None
        if dx == dy == 0:
            return len(line) == 1,
        for point in line:
            if prev_point:
                self.assertTrue(abs(prev_point[0] - point[0]) == 1 or
                                abs(prev_point[1] - point[1]) == 1)
            prev_point = point
            if abs(dy) > abs(dx) or dx == 0:
                if (abs(point[1] - ((point[0] - y) * dx / dy + x)) > 0.5 +
                        error):
                    return False, point
            else:
                if (abs(point[0] - ((point[1] - x) * dy / dx + y)) > 0.5 +
                        error):
                    return False, point
        return True,


class TestGameLogic(unittest.TestCase):
    """Класс тестирует модуль game_logic"""

    def test_saving_results(self):
        """Проверка метода game_logic.save_results"""
        results = [[10, 2], [9, 2], [9, 6], [8, 5], [8, 7], [7, 3],
                   [6, 6], [5, 3], [5, 4]]
        filename = 'testscore'
        level_index = 1
        scores_and_times = [(4, 4), (10, 1), (9, 4), (9, 7), (8, 3)]
        GameLogic.save_results(1, filename, 1, level_index)
        with open(f'{filename}{level_index}.json',
                  'r') as f:
            new_results = json.load(f)
        self.assertEqual(1, len(new_results))
        self.assertEqual([[1, 1]], new_results)
        for score, time in scores_and_times:
            with open(f'{filename}{level_index}.json',
                      'w') as f:
                json.dump(results, f)
            GameLogic.save_results(score, filename, time, level_index)
            with open(f'{filename}{level_index}.json',
                      'r') as f:
                new_results = json.load(f)
            self.assertEqual(9, len(new_results))
            prev_res = None
            for result in new_results:
                if prev_res:
                    self.assertTrue(prev_res[0] > result[0] or
                                    (prev_res[0] == result[0] and
                                     prev_res[1] < result[1]))
                prev_res = result
        os.remove(f'{filename}{level_index}.json')

    def test_embedding(self):
        """Проверка метода game_logic.handle_embedding"""
        line = [[core_classes.Ball(5, 6), core_classes.Ball(5, 7),
                 core_classes.Ball(5, 8)],
                [core_classes.Ball(3, 1), core_classes.Ball(3, 2),
                 core_classes.Ball(3, 3), core_classes.Ball(3, 4)],
                [core_classes.Ball(7, 7, 2),
                 core_classes.Ball(8, 8, 3), core_classes.Ball(9, 9, 4)]]
        old_line = copy.deepcopy(line)
        enters = [(9, 5), (6, 3), (12, 12)]
        exits = [(4, 5), (0, 2), (6, 6)]
        indexes = [3, 5, 5]
        roots = [[(8, 5), (7, 5), (6, 5), (5, 5)],
                 [(5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (0, 3)],
                 [(11, 11), (10, 10), (9, 9), (8, 8), (7, 7)]]
        ball_first = core_classes.Ball(5, 5)
        ball_last = core_classes.Ball(3, 5)
        ball_center = core_classes.Ball(8, 8)
        ball_beggining = core_classes.Ball(5, 4)
        ball_end = core_classes.Ball(3, 6)
        ball_no_root = core_classes.Ball(1, 1)
        root, index = GameLogic.handle_embedding(line, ball_no_root,
                                                 indexes, roots, enters, exits)
        self.assertEqual(old_line, line)
        self.assertEqual(None, root)
        self.assertEqual(None, index)
        root, index = GameLogic.handle_embedding(line, ball_first,
                                                 indexes, roots, enters, exits)
        old_line[0].insert(0, ball_first)
        self.assertEqual(old_line, line)
        self.assertEqual(0, root)
        self.assertEqual(0, index)
        indexes[0] += 1
        root, index = GameLogic.handle_embedding(line, ball_beggining,
                                                 indexes, roots, enters, exits)
        old_line[0].insert(0, ball_beggining)
        self.assertEqual(old_line, line)
        self.assertEqual(0, root)
        self.assertEqual(0, index)
        root, index = GameLogic.handle_embedding(line, ball_last,
                                                 indexes, roots, enters, exits)
        old_line[1].append(ball_last)
        self.assertEqual(old_line, line)
        self.assertEqual(1, root)
        self.assertEqual(4, index)
        root, index = GameLogic.handle_embedding(line, ball_end,
                                                 indexes, roots, enters, exits)
        old_line[1].append(ball_end)
        self.assertEqual(old_line, line)
        self.assertEqual(1, root)
        self.assertEqual(5, index)
        root, index = GameLogic.handle_embedding(line, ball_center,
                                                 indexes, roots, enters, exits)
        old_line[2].append(core_classes.Ball(10, 10, 4))
        self.assertEqual(old_line, line)
        self.assertEqual(4, line[2][-1].color_number)
        self.assertEqual(2, root)
        self.assertEqual(1, index)

    def test_check_score_counting(self):
        ball_on_map = [[core_classes.Ball(5, 5, 1), core_classes.Ball(5, 6, 1),
                        core_classes.Ball(5, 7, 2),
                        core_classes.Ball(5, 8, 3)],
                       [core_classes.Ball(3, 0, 3), core_classes.Ball(3, 1, 3),
                        core_classes.Ball(3, 2, 3),
                        core_classes.Ball(3, 3, 3),
                        core_classes.Ball(3, 4, 4)],
                       [core_classes.Ball(5, 4, 1), core_classes.Ball(5, 5, 1),
                        core_classes.Ball(6, 6, 3),
                        core_classes.Ball(7, 7, 3), core_classes.Ball(8, 8, 3),
                        core_classes.Ball(9, 9, 4)]]
        old_balls = ball_on_map.copy()
        score = 0
        score += GameLogic.count_scores(ball_on_map, 0, 0)
        self.assertEqual(0, score)
        self.assertEqual(old_balls, ball_on_map)
        score += GameLogic.count_scores(ball_on_map, 0, 2)
        self.assertEqual(0, score)
        self.assertEqual(old_balls, ball_on_map)
        score += GameLogic.count_scores(ball_on_map, 1, 0)
        self.assertEqual(40, score)
        old_balls[1] = [core_classes.Ball(3, 4, 4)]
        self.assertEqual(old_balls, ball_on_map)
        score += GameLogic.count_scores(ball_on_map, 2, 4)
        self.assertEqual(70, score)
        old_balls[2] = [core_classes.Ball(5, 4, 1), core_classes.Ball(5, 5, 1),
                        core_classes.Ball(9, 9, 4)]
        self.assertEqual(old_balls, ball_on_map)


class TestParser(unittest.TestCase):
    def test_parser(self):
        level1 = core_classes.Level((18, 10), [(10, 1)], [(10, 38)], 3,
                                    [[(9, 1, 5), (8, 1, 5), (7, 1, 5),
                                      (6, 1, 5), (5, 1, 5), (5, 2, 5),
                                      (5, 3, 5), (5, 4, 5), (5, 5, 5),
                                      (5, 6, 7), (5, 7, 7), (5, 8, 7),
                                      (5, 9, 7), (5, 10, 7), (5, 11, 7),
                                      (5, 12, 7), (5, 13, 7), (5, 14, 7),
                                      (5, 15, 5), (5, 16, 5), (5, 17, 5),
                                      (5, 18, 5), (5, 19, 5), (5, 20, 5),
                                      (5, 21, 7), (5, 22, 7), (5, 23, 7),
                                      (5, 24, 7), (5, 25, 7), (5, 26, 7),
                                      (5, 27, 7), (5, 28, 7), (5, 29, 7),
                                      (5, 30, 5), (5, 31, 5), (5, 32, 5),
                                      (5, 33, 5), (5, 34, 5), (5, 35, 5),
                                      (5, 36, 5), (5, 37, 5), (5, 38, 5),
                                      (6, 38, 5), (7, 38, 5), (8, 38, 5),
                                      (9, 38, 5)]],
                                    10, 12, 40, 25, 150)
        level1.end_creating_level()
        core_classes.Level.put_level(1, level1)
        level2 = core_classes.Level((18, 10), [(10, 1)], [(10, 38)], 5,
                                    [[(9, 1, 5), (8, 1, 5), (7, 1, 5),
                                      (6, 1, 5), (5, 1, 5), (5, 2, 5),
                                      (5, 3, 5), (5, 4, 5), (5, 5, 5),
                                      (5, 6, 7), (5, 7, 7), (5, 8, 7),
                                      (5, 9, 7), (5, 10, 7), (5, 11, 7),
                                      (5, 12, 7), (5, 13, 7), (5, 14, 7),
                                      (5, 15, 5), (5, 16, 5), (5, 17, 5),
                                      (5, 18, 5), (5, 19, 5), (5, 20, 5),
                                      (5, 21, 7), (5, 22, 7), (5, 23, 7),
                                      (5, 24, 7), (5, 25, 7), (5, 26, 7),
                                      (5, 27, 7), (5, 28, 7), (5, 29, 7),
                                      (5, 30, 10), (5, 31, 10), (5, 32, 10),
                                      (5, 33, 10), (5, 34, 10), (5, 35, 10),
                                      (5, 36, 10), (5, 37, 10), (5, 38, 10),
                                      (6, 38, 10), (7, 38, 10), (8, 38, 10),
                                      (9, 38, 10)]],
                                    5, 12, 40, 33.3, 100)
        level2.end_creating_level()
        core_classes.Level.put_level(2, level2)
        new_level1 = core_classes.Level.get_level("1level.txt")
        new_level2 = core_classes.Level.get_level("2level.txt")
        self.assertEqual(level1, new_level1)
        self.assertEqual(level2, new_level2)


if __name__ == '__main__':
    unittest.main()
