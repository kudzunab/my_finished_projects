"""
Рендеринг карты и сущностей

Рисует:
- Карту (стены, пол, коридоры, двери o/x) с туманом войны
- Монстров (z, v, g, O, s, m) с цветами; мимик маскируется под предмет
- Предметы (%, !, ?, /, *)
- Ключи (k)
- Игрока (@)

КООРДИНАТЫ: grid — 0-based. Окно имеет box(), внутренняя область с (1,1).
Поэтому при отрисовке: window_y = grid_y + 1, window_x = grid_x + 1.
"""
import curses

from src.domain.entities.entities import MonsterType
from src.presentation.render.tiles import (
    ENEMY_CHAR_TO_COLOR_PAIR_ID,
    ITEMS_TILES,
    MONSTER_TYPE_TO_CHAR,
)

# Символы маскировки мимика (как у полезных предметов)
MIMIC_CHARS = ("?", "%", "!", "*", "/")


def draw_char(map_window, window_y, window_x, char):
    """
    Рисует один символ на карте.
    Для символов врагов добавляет цветовую пару, иначе рисует обычным цветом.
    """
    color_pair_id = ENEMY_CHAR_TO_COLOR_PAIR_ID.get(char)
    try:
        if color_pair_id is None:
            map_window.addch(window_y, window_x, ord(char))
        else:
            map_window.addch(window_y, window_x, ord(char), curses.color_pair(color_pair_id))
    except curses.error:
        pass


def render_map(
    map_window: "curses.window",
    grid: list[list[str]],
    player_y: int,
    player_x: int,
    items: list[dict],
    monsters: list[dict],
    visible_mask: list[list[bool]],
    seen_mask: list[list[bool]],
) -> None:
    """
    Отрисовывает текущий кадр игры.
    """
    map_window.erase()
    map_window.box()

    inner_height = len(grid)
    inner_width = len(grid[0]) if grid else 0

    for grid_y in range(inner_height):
        for grid_x in range(inner_width):
            window_y = grid_y + 1
            window_x = grid_x + 1

            if visible_mask[grid_y][grid_x]:
                char_to_draw = grid[grid_y][grid_x]
            elif seen_mask[grid_y][grid_x]:
                char = grid[grid_y][grid_x]
                # ТЗ: просмотренные комнаты — только стены (и двери)
                if char in {"|", "-", "+", "o", "x"}:
                    char_to_draw = char
                else:
                    char_to_draw = " "
            else:
                char_to_draw = " "

            draw_char(map_window, window_y, window_x, char_to_draw)

    for item in items:
        item_y, item_x = item["y"], item["x"]
        if 0 <= item_y < inner_height and 0 <= item_x < inner_width:
            if visible_mask[item_y][item_x]:
                item_char = ITEMS_TILES.get(item["type"])
                if item_char is not None:
                    draw_char(map_window, item_y + 1, item_x + 1, item_char)

    for monster in monsters:
        m_y, m_x = monster["y"], monster["x"]
        if 0 <= m_y < inner_height and 0 <= m_x < inner_width:
            if visible_mask[m_y][m_x]:
                if monster["type"] == MonsterType.MIMIC and not monster.get("is_activated", False):
                    idx = (m_x * 31 + m_y) % len(MIMIC_CHARS)
                    char = MIMIC_CHARS[idx]
                else:
                    char = MONSTER_TYPE_TO_CHAR[monster["type"]]
                if char is not None:
                    draw_char(map_window, m_y + 1, m_x + 1, char)

    map_window.addch(player_y + 1, player_x + 1, ord("@"))

    map_window.refresh()
