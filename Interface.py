import curses
import random


class Interface:
    """Класс отвечает за всю визуализацию в игре"""
    def __init__(self, level):
        self.level = level
        self.win = self.init_win()
        self.initialize_colours()

    @staticmethod
    def init_curses():
        """Первоначальная инициализация библиотеки curses"""
        curses.mousemask(1)
        curses.curs_set(0)
        curses.use_default_colors()

    @staticmethod
    def print_levels(screen, levels_count):
        """Отображение меню"""
        screen.addstr(0, 1, "Choose the menu item by mouse clicking")
        for i in range(levels_count):
            screen.addstr(i + 1, 1, f"Level {i + 1}")
        screen.addstr(levels_count + 1, 1, "Random Level")
        screen.addstr(levels_count + 2, 1, "See high score table")
        screen.addstr(levels_count + 3, 1, "Exit")
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
    def draw_high_score_table_level(screen, results, index, y_begin):
        """Отображение таблицы лучших результатов"""
        screen.addstr(y_begin, 1, f"High Score Table Level {index}")
        screen.addstr(y_begin + 2, 1, f"Place Score {'Time'.rjust(5)}")
        for i in range(len(results)):
            screen.addstr(y_begin + i + 3, 1, f"{str(i + 1).rjust(5)} "
                                              f"{str(results[i][0]).rjust(5)} "
                                              f"{'%.2f' % results[i][1]}")
        screen.addstr(y_begin + len(results) + 5, 1, 'Click to exit to menu')
        screen.refresh()
        key = screen.getch()
        if key == curses.KEY_MOUSE:
            Interface.clean_screen(screen)
            return

    @staticmethod
    def print_results(screen, score, time):
        """Отображение текуших результатов завершенного уровня"""
        screen.addstr(0, 0, "Level End")
        screen.addstr(2, 0, f'Score: {score}')
        screen.addstr(3, 0, f'Time: {time:0.2f} seconds')
        screen.addstr(5, 0, "Click to continue")
        screen.refresh()
        key = screen.getch()
        if key == curses.KEY_MOUSE:
            Interface.clean_screen(screen)
            return

    @staticmethod
    def game_over(screen):
        """Обработка конца игры"""
        screen.addstr(0, 0, 'Sorry, Game Over')
        screen.refresh()
        key = screen.getch()
        if key == curses.KEY_MOUSE:
            Interface.clean_screen(screen)
            return

    def wait(self, time_in_millisec):
        self.win.timeout(time_in_millisec)

    def init_win(self):
        """Инициализация нового окна"""
        win = curses.newwin(self.level.field_height,
                            self.level.field_width, 0, 0)
        win.border(0)
        win.nodelay(1)
        win.timeout(100)
        return win

    def draw_consist_items(self, score, lives, level_index):
        """Отображение основных элементов: текущий счет, входы и выходы,
        лягушка"""
        self.draw_an_object(0, 3, f'Score: {score}, Lives: {round(lives)},'
                                  f' Level: {level_index}')
        for ex in self.level.exits:
            self.draw_an_object(ex[0], ex[1], '#')
        for ent in self.level.enters:
            self.draw_an_object(ent[0], ent[1], '$')
        self.draw_a_frog()

    def draw_roots(self):
        """Отображение марщрутов, по которым едут шары"""
        for root in self.level.roots:
            for cell in root:
                self.draw_an_object(cell[0], cell[1], '-')

    def draw_an_object(self, y, x, text):
        self.win.addstr(y, x, text)

    def draw_ball(self, ball):
        self.win.addstr(ball.y, ball.x, '*',
                        curses.color_pair(ball.color_number))

    def initialize_colours(self):
        """Инициализация всех цветов, используемых в игре"""
        for i in range(self.level.balls_number):
            curses.init_pair(i + 1,
                             random.randint(8, 8 + self.level.color_number),
                             -1)
            # шары с 1 по их количество
        curses.init_pair(self.level.balls_number + 1,
                         random.randint(8, 8 + self.level.color_number), -1)
        curses.init_pair(self.level.balls_number + 2,
                         random.randint(8, 8 + self.level.color_number), -1)
        # летящий шар
        curses.init_pair(self.level.balls_number + 3,
                         *curses.pair_content(self.level.balls_number + 1))

    def draw_a_frog(self):
        """ Метод отрисовывает лягушку и шары для стрельбы"""
        x = self.level.frog.right_up_corner[0]
        y = self.level.frog.right_up_corner[1]
        self.draw_an_object(y, x, '/')
        self.draw_an_object(y, x + 2, '\\')
        self.draw_an_object(y + 1, x, '\\')
        self.draw_an_object(y + 1, x + 2, '/')
        self.draw_ball(self.level.frog.shoot_balls[0])
        self.draw_ball(self.level.frog.shoot_balls[1])

    def update_win(self):
        """Обновление игрового окна, обработка нажатия"""
        key = self.win.getch()
        if key == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            line = self.level.frog.shoot(x, y, (self.level.field_height,
                                                self.level.field_width))[:-1]
            self.next_ball()
            return line

    def next_ball(self):
        """Обновление цветов после выстрела"""
        curses.init_pair(self.level.frog.shoot_balls[0].color_number,
                         *Interface.get_color_pair(
                             self.level.frog.shoot_balls[1]))
        curses.init_pair(self.level.frog.shoot_balls[1].color_number,
                         random.randint(8, 8 + self.level.color_number), -1)

    def set_flying_ball_color(self, flying_ball):
        """Обновление цвета летающего шара"""
        curses.init_pair(flying_ball.color_number,
                         *curses.pair_content(
                             self.level.frog.shoot_balls[0].color_number))

    def end_win(self):
        """Чистит и стирает основной игровой экран"""
        Interface.clean_screen(self.win)
        self.win = None

    @staticmethod
    def get_color_pair(ball):
        return curses.pair_content(ball.color_number)
