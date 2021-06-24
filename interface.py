import curses
import random


class Interface:
    """Класс отвечает за всю визуализацию в игре"""

    def __init__(self, level, screen):
        self.level = level
        self.win = screen
        self.init_win()
        self.initialize_colours()

    @staticmethod
    def init_curses():
        """Первоначальная инициализация библиотеки curses"""
        curses.mousemask(1)
        curses.curs_set(0)
        curses.use_default_colors()

    @staticmethod
    def print_only_levels(screen, levels_count):
        """Отображает только список уровней для меню таблицы результатов"""
        screen.addstr(0, 1, "Choose the level by mouse clicking to see its "
                            "highscore table")
        for i in range(levels_count):
            screen.addstr(i + 1, 1, f"Level {i + 1}")
        screen.addstr(levels_count + 1, 1, "Random Level")
        screen.refresh()
        key = screen.getch()
        if key == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            return x, y

    @staticmethod
    def print_menu(screen, levels_count):
        """Отображение меню"""
        screen.addstr(0, 1, "Choose the menu item by mouse clicking")
        for i in range(levels_count):
            screen.addstr(i + 1, 1, f"Level {i + 1}")
        screen.addstr(levels_count + 1, 1, "Random Level")
        screen.addstr(levels_count + 2, 1, "See high score table")
        screen.addstr(levels_count + 3, 1, "Shop")
        screen.addstr(levels_count + 4, 1, "Upload level")
        screen.addstr(levels_count + 5, 1, "Exit")
        screen.refresh()
        key = screen.getch()
        if key == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            return x, y

    @staticmethod
    def clean_screen(screen):
        """Очистка экрана"""
        screen.clear()
        screen.refresh()

    @staticmethod
    def draw_high_score_table_level(screen, results, index):
        """Отображение таблицы лучших результатов"""
        Interface.clean_screen(screen)
        screen.addstr(0, 1, f"High Score Table Level {index}")
        screen.addstr(1, 1, f"Place Score {'Time'.rjust(5)}")
        for i in range(len(results)):
            screen.addstr(i + 2, 1,
                          f"{str(i + 1).rjust(5)} "
                          f"{str(results[i][0]).rjust(5)} "
                          f"{'%.2f' % results[i][1]}")
        screen.addstr(len(results) + 3, 1, 'Press any key or '
                                           'click '
                                           'to exit to menu')
        screen.refresh()

    def print_results(self, score, time):
        """Отображение текуших результатов завершенного уровня"""
        self.win.addstr(0, 0, "Level End")
        self.win.addstr(2, 0, f'Score: {score}')
        self.win.addstr(3, 0, f'Time: {time:0.2f} seconds')
        self.win.addstr(5, 0, "Click or press any key to continue")
        self.win.refresh()
        Interface.wait_for_reaction(self.win)

    @staticmethod
    def wait_for_reaction(screen):
        """Ждет пока что-то нажмут"""
        key = screen.getch()
        while key < 0:
            key = screen.getch()
        Interface.clean_screen(screen)

    def no_lives(self):
        """Обработка нулевых жизней"""
        self.win.addstr(0, 0, 'Sorry, You can\'t play a level, because your '
                              'lives = 0')
        self.win.addstr(2, 0, 'Press any key or click')
        self.win.refresh()
        Interface.wait_for_reaction(self.win)

    def wait(self, time_in_millisec):
        """Просто ждет"""
        self.win.timeout(time_in_millisec)

    def init_win(self):
        """Инициализация нового окна"""
        self.win.nodelay(1)
        self.win.timeout(100)

    def draw_consist_items(self, score, lives, level_index):
        """Отображение основных элементов: текущий счет, входы и выходы,
        лягушка"""
        self.draw_border()
        self.draw_an_object(0, 3, f'Score: {score}, Lives: {round(lives)},'
                                  f' Level: {level_index}')
        for ex in self.level.exits:
            self.draw_an_object(ex[0], ex[1], '#')
        for ent in self.level.enters:
            self.draw_an_object(ent[0], ent[1], '$')
        self.draw_a_frog()

    def draw_border(self):
        """Рисует границы"""
        for i in range(self.level.field_height - 1):
            self.draw_an_object(i, 0, '|')
            self.draw_an_object(i, self.level.field_width - 1, '|')
        for i in range(self.level.field_width):
            self.draw_an_object(0, i, '_')
            if 0 < i < self.level.field_width - 1:
                self.draw_an_object(self.level.field_height - 2, i, '_')

    def draw_roots(self):
        """Отображение марщрутов, по которым едут шары"""
        for root in self.level.roots:
            for cell in root:
                self.draw_an_object(cell[0], cell[1], '-')

    def draw_an_object(self, y, x, text):
        """Рисует любой объект"""
        self.win.addstr(y, x, text)

    def draw_ball(self, ball):
        """Рисует шар"""
        self.win.addstr(ball.y, ball.x, '*',
                        curses.color_pair(ball.color_number))

    def initialize_colours(self):
        """Инициализация всех цветов, используемых в игре"""
        for i in range(self.level.color_number):
            curses.init_pair(i + 1, 8 + i, -1)
            # для каждого цвета - своя пара

    def draw_a_frog(self):
        """ Метод отрисовывает лягушку и шары для стрельбы"""
        x = self.level._frog.right_up_corner[0]
        y = self.level._frog.right_up_corner[1]
        self.draw_an_object(y, x, '/')
        self.draw_an_object(y, x + 2, '\\')
        self.draw_an_object(y + 1, x, '\\')
        self.draw_an_object(y + 1, x + 2, '/')
        self.draw_ball(self.level._frog.shoot_balls[0])
        self.draw_ball(self.level._frog.shoot_balls[1])

    def update_win(self):
        """Обновление игрового окна, обработка нажатия"""
        key = self.win.getch()
        if key == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            line = self.level._frog.shoot(x, y, (self.level.field_height,
                                                 self.level.field_width))[:-1]
            return "shoot", line
        if key == 115:
            return "save"

    def next_ball(self):
        """Обновление цветов после выстрела"""
        color = random.randint(1, self.level.color_number)
        self.level._frog.shoot_balls[0].color_number = \
            self.level._frog.shoot_balls[1].color_number
        self.level._frog.shoot_balls[1].color_number = color

    def end_win(self):
        """Чистит и стирает основной игровой экран"""
        Interface.clean_screen(self.win)

    def draw_balls_in_root(self, balls_on_map):
        """Рисует все шары, которые есть на поле на данной маршруте"""
        for ball in balls_on_map:
            self.draw_ball(ball)
