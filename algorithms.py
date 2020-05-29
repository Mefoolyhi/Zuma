"""
Сожержит все алгоритмы, необходимые для работы программы.

Методы:
algo_for_drawing_lines -- по двум точкам возвращает отрезок
get_vector_to_the_end -- по двум точкам возвращает луч

"""


def algo_for_drawing_lines(x1, y1, x2, y2):
    """Метод возвращает координаты точек на растровой плоскости отрезка
    от точки А до точки Б, которые находятся алгоритмом Брезенхема

    Аргументы:
    x1, y1 -- координаты точки А
    x2, y2 -- координаты точки Б

    Возвращаемое значение:
    line -- список точек отрезка, представленные в виде (y, x)

    """
    dx = x2 - x1
    dy = y2 - y1

    vector_x = 1 if dx > 0 else -1 if dx < 0 else 0
    vector_y = 1 if dy > 0 else -1 if dy < 0 else 0

    if dx < 0:
        dx = -dx
    if dy < 0:
        dy = -dy

    if dx > dy:
        step_x, step_y = vector_x, 0
        small_delta, bid_delta = dy, dx
    else:
        step_x, step_y = 0, vector_y
        small_delta, bid_delta = dx, dy

    x, y = x1, y1
    line = []
    error, t = bid_delta, 0
    line.append((y, x))

    while t < bid_delta:
        error -= 2 * small_delta
        if error < 0:
            error += 2 * bid_delta
            x += vector_x
            y += vector_y
        else:
            x += step_x
            y += step_y
        t += 1
        line.append((y, x))
    return line


def get_vector_to_the_end(height, width, x0, y0, x1, y1):
    """Метод для получения координат точек на растровой плоскости луча
    от точки А, проходящего через точку Б, до конца плоскости

    Аргументы:
    height -- высота поля (растровой плоскости)
    width -- ширина поля (растровой плоскости)
    x0, y0 -- координаты точки А
    x1, y1 -- координаты точки Б

    Возвращаемое значение:
    список координат точек луча, пренадлежащие ограничнному полю,
    которые представлены в виде пары (y, x)

    """

    dx = x1 - x0
    dy = y1 - y0

    max_y = height - 1 if dy > 0 else 0 if dy < 0 else y0
    max_x = width - 1 if dx > 0 else 0 if dx < 0 else x0

    x_max_y = dx * (max_y - y0) / dy + x0 if dy != 0 else max_x
    y_max_x = dy * (max_x - x0) / dx + y0 if dx != 0 else max_y

    r_max_y = (x_max_y - x1) * (x_max_y - x1)
    r_max_y += (max_y - y1) * (max_y - y1)

    r_max_x = (max_x - x1) * (max_x - x1)
    r_max_x += (y1 - y_max_x) * (y1 - y_max_x)

    if r_max_x < r_max_y:
        error = abs(y_max_x - round(y_max_x))
        if y_max_x != 0:
            error /= y_max_x
        y_max_x = round(y_max_x)
        return algo_for_drawing_lines(x0, y0, x1, y1)[:-1] + algo_for_drawing_lines(x1, y1, max_x, y_max_x), 2 * error
    else:
        error = abs(x_max_y - round(x_max_y))
        if x_max_y != 0:
            error /= x_max_y
        x_max_y = round(x_max_y)
        return algo_for_drawing_lines(x0, y0, x1, y1)[:-1] + algo_for_drawing_lines(x1, y1, x_max_y, max_y), 2 * error

