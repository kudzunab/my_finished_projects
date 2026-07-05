"""
Туман войны
- visible_mask: что видно сейчас
- seen_mask: что было увидено ранее
"""


def point_inside_room(x: int, y: int, room: dict[str, int]) -> bool:
    """Точка внутри прямоугольника комнаты, включая границы."""
    return (
        room["x"] <= x <= room["x"] + room["w"] - 1
        and room["y"] <= y <= room["y"] + room["h"] - 1
    )


def get_room_index_by_coord(x: int, y: int, rooms: list[dict[str, int]]) -> int:
    """Индекс комнаты для координаты или -1 вне комнат."""
    for i, room in enumerate(rooms):
        if point_inside_room(x, y, room):
            return i
    return -1


def reveal_room_full(seen_mask: list[list[bool]], room: dict[str, int]) -> None:
    """Помечает как виденные только границу комнаты (стены по ТЗ), не весь пол."""
    x0 = room["x"]
    y0 = room["y"]
    x1 = room["x"] + room["w"] - 1
    y1 = room["y"] + room["h"] - 1

    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            on_border = x == x0 or x == x1 or y == y0 or y == y1
            if on_border:
                seen_mask[y][x] = True


def compute_fog(
    grid: list[list[str]],
    rooms: list[dict[str, int]],
    seen_rooms: list[bool],
    player_x: int,
    player_y: int,
    seen_mask: list[list[bool]],
) -> list[list[bool]]:
    """
    Считает visible_mask и обновляет seen_mask / seen_rooms.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    visible_mask = [[False] * width for _ in range(height)]

    player_room_index = get_room_index_by_coord(player_x, player_y, rooms)

    for i, room in enumerate(rooms):
        if i != player_room_index and seen_rooms[i]:
            reveal_room_full(seen_mask, room)

    if player_room_index != -1:
        room = rooms[player_room_index]
        x0 = room["x"]
        y0 = room["y"]
        x1 = room["x"] + room["w"] - 1
        y1 = room["y"] + room["h"] - 1

        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                visible_mask[y][x] = True
                seen_mask[y][x] = True

        seen_rooms[player_room_index] = True
    else:
        reveal_los_by_rays(
            grid,
            visible_mask,
            seen_mask,
            player_x,
            player_y,
            radius=10,
        )

    if 0 <= player_y < height and 0 <= player_x < width:
        visible_mask[player_y][player_x] = True
        seen_mask[player_y][player_x] = True

    return visible_mask


def _in_bounds(x: int, y: int, width: int, height: int) -> bool:
    return 0 <= x < width and 0 <= y < height


def _is_opaque(tile: str) -> bool:
    """Стены и закрытая дверь блокируют луч; пол, коридор, открытая дверь, лестница — нет"""
    return tile in {"|", "-", "+", "x"}


def _bresenham_line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Алгоритм Брезенхэма для рисования прямой линии"""
    points: list[tuple[int, int]] = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    return points


def _cast_ray_line(
    grid: list[list[str]],
    visible_mask: list[list[bool]],
    seen_mask: list[list[bool]],
    line: list[tuple[int, int]],
) -> None:
    """Проверяет видимость точки на линии"""
    height = len(grid)
    width = len(grid[0]) if height else 0

    for x, y in line:
        if not _in_bounds(x, y, width, height):
            break

        visible_mask[y][x] = True
        seen_mask[y][x] = True

        if _is_opaque(grid[y][x]):
            break


def reveal_los_by_rays(
    grid: list[list[str]],
    visible_mask: list[list[bool]],
    seen_mask: list[list[bool]],
    player_x: int,
    player_y: int,
    radius: int = 10,
) -> None:
    """
    Прямая видимость в коридоре: лучи Брезенхэма к периметру квадрата вокруг игрока.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    targets: set[tuple[int, int]] = set()

    x0 = max(0, player_x - radius)
    x1 = min(width - 1, player_x + radius)
    y0 = max(0, player_y - radius)
    y1 = min(height - 1, player_y + radius)

    for x in range(x0, x1 + 1):
        targets.add((x, y0))
        targets.add((x, y1))
    for y in range(y0, y1 + 1):
        targets.add((x0, y))
        targets.add((x1, y))

    for tx, ty in targets:
        line = _bresenham_line(player_x, player_y, tx, ty)
        _cast_ray_line(grid, visible_mask, seen_mask, line)
