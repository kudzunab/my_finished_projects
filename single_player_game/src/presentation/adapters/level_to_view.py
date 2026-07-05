"""
Адаптер преобразования доменной модели уровня в представление для рендера.

Преобразует объекты Level, Player в простые структуры данных для слоя presentation.
Символы карты: " " — пустота, "." — пол комнаты, "-"|"|" — стены, "+" — углы,
"#" — коридор, "o" — открытая дверь, "x" — закрытая дверь.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.entities import ItemType, MonsterType


@dataclass
class ViewState:
    """Данные для отрисовки одного кадра."""
    grid: list[list[str]]
    player_y: int
    player_x: int
    monsters: list[dict]
    items: list[dict]
    doors: list[dict]
    keys: list[dict]
    player_status: dict


def _point_inside_any_room(x: int, y: int, rooms: list) -> bool:
    """Точка внутри прямоугольника комнаты (включая стены)."""
    for room in rooms:
        pos = room.position
        if pos.x <= x <= pos.x + pos.dx - 1 and pos.y <= y <= pos.y + pos.dy - 1:
            return True
    return False


def build_view_state(level, player) -> ViewState:
    """
    Строит представление уровня для слоя отображения.

    Схема grid:
    - " " — пустота (вне комнат и коридоров)
    - "." — пол комнаты
    - "-" — горизонтальная стена
    - "|" — вертикальная стена
    - "+" — угол комнаты
    - "#" — коридор
    - "o" — открытая дверь
    - "x" — закрытая дверь
    """
    max_x = 0
    max_y = 0

    for room in level.rooms:
        pos = room.position
        max_x = max(max_x, pos.x + pos.dx)
        max_y = max(max_y, pos.y + pos.dy)

    for passage in level.passages:
        for p in passage.passage:
            max_x = max(max_x, p.x + 1)
            max_y = max(max_y, p.y + 1)
        max_x = max(max_x, passage.entrance.x + 1, passage.exit.x + 1)
        max_y = max(max_y, passage.entrance.y + 1, passage.exit.y + 1)

    grid = [[" " for _ in range(max_x)] for _ in range(max_y)]

    for room in level.rooms:
        pos = room.position
        for i in range(pos.dy):
            for j in range(pos.dx):
                y, x = pos.y + i, pos.x + j
                if i == 0 or i == pos.dy - 1:
                    char = "-" if (j != 0 and j != pos.dx - 1) else "+"
                elif j == 0 or j == pos.dx - 1:
                    char = "|" if (i != 0 and i != pos.dy - 1) else "+"
                else:
                    char = "."
                grid[y][x] = char

    for passage in level.passages:
        door_positions = {
            (passage.entrance.x, passage.entrance.y),
            (passage.exit.x, passage.exit.y),
        }
        for p in passage.passage:
            if (p.x, p.y) in door_positions:
                continue
            if 0 <= p.y < max_y and 0 <= p.x < max_x:
                if not _point_inside_any_room(p.x, p.y, level.rooms):
                    grid[p.y][p.x] = "#"

        door_char = "o" if passage.is_locked else "o"
        for door_pos in (passage.entrance, passage.exit):
            if 0 <= door_pos.y < max_y and 0 <= door_pos.x < max_x:
                grid[door_pos.y][door_pos.x] = door_char

    if 0 <= level.end_position.y < max_y and 0 <= level.end_position.x < max_x:
        grid[level.end_position.y][level.end_position.x] = ">"

    items = []
    keys = []
    for room in level.rooms:
        for item_type, item_list in room.items.storage.items():
            for item_in_room in item_list:
                pos = item_in_room.position
                if item_type == ItemType.KEY:
                    keys.append({"y": pos.y, "x": pos.x})
                else:
                    items.append({"y": pos.y, "x": pos.x, "type": item_type})

    monsters = []
    for room in level.rooms:
        for monster in room.monsters:
            if monster.is_alive:
                pos = monster.position
                if monster.type == MonsterType.MIMIC:
                    monsters.append({
                        "y": pos.y,
                        "x": pos.x,
                        "type": MonsterType.MIMIC,
                        "is_activated": monster.is_activated,
                    })
                else:
                    monsters.append({"y": pos.y, "x": pos.x, "type": monster.type})

    doors = []
    for passage in level.passages:
        if passage.is_locked:
            doors.append({
                "y": passage.entrance.y,
                "x": passage.entrance.x,
                "is_open": False,
            })
            doors.append({
                "y": passage.exit.y,
                "x": passage.exit.x,
                "is_open": False,
            })
        else:
            doors.append({
                "y": passage.entrance.y,
                "x": passage.entrance.x,
                "is_open": True,
            })
            doors.append({
                "y": passage.exit.y,
                "x": passage.exit.x,
                "is_open": True,
            })

    player_status = {
        "hp": int(player.stats.health),
        "max_hp": int(player.regen_limit),
        "str": int(player.stats.strength),
        "agi": int(player.stats.agility),
        "lvl": level.level_num,
        "gold": player.money,
    }

    return ViewState(
        grid=grid,
        player_y=player.position.y,
        player_x=player.position.x,
        monsters=monsters,
        items=items,
        doors=doors,
        keys=keys,
        player_status=player_status,
    )
