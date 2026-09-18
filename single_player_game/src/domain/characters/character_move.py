import random

from src.domain.entities import MonsterType, HostilityType
from src.domain.entities import Position, Monster, Directions
from src.domain.entities import Player, Level
from .character_fight import is_equal_x_y
"""
#    match direction:
#        case Directions.FORWARD:
#            pos.y -= 1
#        case Directions.BACK:
#            pos.y += 1
#        case Directions.LEFT:
#            pos.x -= 1
#        case Directions.RIGHT:
#            pos.x += 1
#        case Directions.D_FORWARD_LEFT:
#            pos.y -= 1
#            pos.x -= 1
#        case Directions.D_FORWARD_RIGHT:
#            pos.y -= 1
#            pos.x += 1
#        case Directions.D_BACK_LEFT:
#            pos.y += 1
#            pos.x -= 1
#        case Directions.D_BACK_RIGHT:
#            pos.y += 1
#            pos.x += 1
#        case _:
#            pass #пока добавила, но скорее всего не нужен

FORWARD = 0  # вперед
BACK = 1  # назад
LEFT = 2  # влево
RIGHT = 3  # вправа
D_FORWARD_LEFT = 4  # влево вверх диагонально
D_FORWARD_RIGHT = 5  # вправо вверх диагонально
D_BACK_LEFT = 6  # влево вниз диагонально
D_BACK_RIGHT = 7  # вправо вниз диагонально
STOP = 8  # не двигаться
"""
class MConst:
    OGRE_STEP = 2
    SIMPLE_DIRECTIONS = 4
    DIAGONAL_DIRECTIONS = 4
    ALL_DIRECTIONS = 8
    SIMPLE_TO_DIAGONAL_SHIFT =  4
    MAX_TRIES_TO_MOVE = 16
    LOW_HOSTILITY_RADIUS = 2
    AVERAGE_HOSTILITY_RADIUS = 4
    HIGH_HOSTILITY_RADIUS = 6
"""!
    Меняет координаты, если нужно проверить, то передавать надо копию объекта
"""
def move_character_by_direction(direction: Directions, pos: Position):
    dx, dy = direction.next_dx_dy_get()
    pos.x += dx
    pos.y += dy

def get_room_number(pos: Position, level: Level):
    for i in range(len(level.rooms)):
        room = level.rooms[i]
        x0, y0, w, h = room.position.x, room.position.y, room.position.dx, room.position.dy
        if x0 < pos.x < x0 + w - 1 and y0 < pos.y < y0 + h - 1: #герой не может заходить на границы комнаты
            return i

    #в коридоре оно, но его там быть не должно
    return -1

"""!
    @brief Проверяем входит ли точка в уровень, проверяет только открытые зоны
    @detail В основном цикле неободимо открывать двери
            room_idx = get_room_number(target_pos, level)
            if room_idx != -1:   # пока логика запирания не реализована
                level.rooms[room_idx].is_visited = True 
    @return True, если объект находится на уровне.
"""
def check_outside_border(cur_pos, level):
    room_num = get_room_number(cur_pos, level)
    if room_num == -1:
        for passage in level.passages:
            for point in passage.passage:
                if is_equal_x_y(point, cur_pos):
                    return True

    else: #eliflevel.rooms[room_num].is_visited:  не проверяем можно ли войти
        level.rooms[room_num].is_visited = True    # нет ключей, просто меняем статус
        return True


    return False
"""!
    @brief Проверяет клетку, на возможность движения в нее
    @detail Если в клетке лежит предмет, то в нее можно встать
    @return True, если клетка свободна от монстров или игрока, т.е. туда можно переместиться
"""
def check_unoccupied_level(cur_pos: Position, level: Level, player: Player, cur_entity=None):

    if is_equal_x_y(player.position, cur_pos):
        return False

    for room in level.rooms:
        if room.is_visited:
            for monster in room.monsters:
                #не дает сравнивать с координатами самого монстра, если он стоит
                if monster is not cur_entity and monster.is_alive and is_equal_x_y(monster.position, cur_pos):
                    return False

    return True

def simple_pattern(monster: Monster, level: Level, temp_pos: Position, player: Player):
    if monster.type in [MonsterType.ZOMBIE, MonsterType.VAMPIRE, MonsterType.SNAKE]:
        monster.direction = Directions.STOP
        cur_pos = temp_pos
        max_dir, init_dir = MConst.SIMPLE_DIRECTIONS, 0
        match monster.type:
            case MonsterType.VAMPIRE:
                max_dir = MConst.ALL_DIRECTIONS
            case MonsterType.SNAKE:
                max_dir, init_dir = MConst.DIAGONAL_DIRECTIONS, MConst.SIMPLE_TO_DIAGONAL_SHIFT
        for _ in range(MConst.MAX_TRIES_TO_MOVE):
            cur_dir = init_dir + random.randint(1, max_dir) % max_dir
            cur_pos.copy_position(monster.position)
            move_character_by_direction(Directions(cur_dir), cur_pos)
            if check_outside_border(cur_pos, level) and check_unoccupied_level(cur_pos, level, player, monster):
                monster.direction = cur_dir
                monster.change_position(cur_pos)
                break
"""!
    @brief Функция движения огра
"""
def pattern_ogr(monster: Monster, level: Level, temp_pos: Position, player: Player):
    cur_pos = temp_pos
    if not monster.is_resting:
        monster.direction = Directions.STOP
        for _ in range(MConst.MAX_TRIES_TO_MOVE):
            cur_dir = random.randint(1, MConst.SIMPLE_DIRECTIONS) % MConst.SIMPLE_DIRECTIONS
            cur_pos.copy_position(monster.position)
            stop = False
            for _ in range(MConst.OGRE_STEP):
                move_character_by_direction(Directions(cur_dir), cur_pos)
                if not check_outside_border(cur_pos, level) or not check_unoccupied_level(cur_pos, level, player,
                                                                                          monster):
                    stop = True
                    break

            if not stop:
                monster.change_position(cur_pos)
                monster.direction = cur_dir
                break

    else:
        monster.is_resting = False  # восстанавливаем значение после хода
"""!
    @brief Функция движения приведение 
"""
def pattern_ghost(monster: Monster, level: Level, temp_pos: Position, player: Player):

    room_num = get_room_number(monster.position, level)
    if room_num == -1: #не перемещается по поридору по умолчанию
        visited_rooms = [r for r in level.rooms if r.is_visited]
        if not visited_rooms:
            return #ждем в коридоре, это в самом начале игры
        room = random.choice(visited_rooms)
    else:
        room = level.rooms[room_num]

    monster.is_invisible = False
    visibility = random.randint(0, 99)
    if visibility < 30:
        monster.is_invisible = True

    for _ in range(MConst.MAX_TRIES_TO_MOVE):
        #не должен телепортироваться на стены
        temp_pos.x = random.randint(room.position.x + 1, room.position.x + room.position.dx - 2)
        temp_pos.y = random.randint(room.position.y + 1, room.position.y + room.position.dy - 2)

        if check_unoccupied_level(temp_pos, level, player, monster):
            monster.change_position(temp_pos)
            break

    monster.direction = Directions.STOP

"""!
    @brief Траектория преследования
"""
def is_player_near(player: Player, monster: Monster):
    dist = max(abs(player.position.x - monster.position.x), abs(player.position.y - monster.position.y))
    match monster.hostility:
        case HostilityType.LOW:
            if dist <= MConst.LOW_HOSTILITY_RADIUS:
                return True

        case HostilityType.AVERAGE:
            if dist <= MConst.AVERAGE_HOSTILITY_RADIUS:
                return True

        case HostilityType.HIGH:
            if dist <= MConst.HIGH_HOSTILITY_RADIUS:
                return True

    return False
"""!
    @brief Траектория преследования
"""
def monster_hunting_trajectory(player: Player, monster: Monster):

    if monster.type == MonsterType.MIMIC:
        return [Directions.STOP]

    monster.is_chasing = True
    res = []
    dx = player.position.x - monster.position.x
    dy = player.position.y - monster.position.y

    #if monster.type in [MonsterType.SNAKE, MonsterType.VAMPIRE, MonsterType.GHOST]:
    # одна траектория для всех, только мимик стоит
    if dx < 0 and dy < 0:
        res.append(Directions.D_FORWARD_LEFT)
    elif dy < 0 < dx:
        res.append(Directions.D_FORWARD_RIGHT)
    elif dx < 0 < dy:
        res.append(Directions.D_BACK_LEFT)
    elif dx > 0 and dy > 0:
        res.append(Directions.D_BACK_RIGHT)

    if abs(dx) < abs(dy):
        if dx < 0: res.append(Directions.LEFT)
        elif dx > 0: res.append(Directions.RIGHT)
        if dy > 0: res.append(Directions.BACK)
        elif dy < 0: res.append(Directions.FORWARD)
    else:
        # меняем порядок добавления, чтобы сначала проверялось более быстрое приближение
        if dy > 0: res.append(Directions.BACK)
        elif dy < 0: res.append(Directions.FORWARD)
        if dx < 0: res.append(Directions.LEFT)
        elif dx > 0: res.append(Directions.RIGHT)
    return res

"""!
    @brief Определение траектории движения конкретного монстра.
    @detail Функция движения монстра. Если он в списке атакующих, то не движется
"""
def monster_moving(player: Player, monster: Monster, level: Level, temp_pos: Position):

#    dist =  max(abs(player.position.x - monster.position.x),
#               abs(player.position.y - monster.position.y))
    dist = abs(player.position.x - monster.position.x) + abs(player.position.y - monster.position.y)
    # не двигаем атакующих монстров и мимка.
    if monster.type == MonsterType.MIMIC or dist <= 1:
        return

    if is_player_near(player, monster): #внутри радиуса чувствительности
        dir_mass = monster_hunting_trajectory(player, monster)
        for _dir in dir_mass:
            temp_pos.copy_position(monster.position)
            move_character_by_direction(_dir, temp_pos)
            can_pass = check_outside_border(temp_pos, level) or monster.type == MonsterType.GHOST
            if can_pass and check_unoccupied_level(temp_pos, level, player, monster):
                monster.direction = _dir
                monster.change_position(temp_pos)
                monster.is_chasing = True
                return

    monster.is_chasing = False #я этот флаг все равно не использую
    monster.pattern(monster, level, temp_pos, player)
    return
"""!
    @brief  Функция движения монстров. Ее нужно использовать в мейне.
    @detail Перемещает всех монстров из посещенных комнат. Остальные монстры в процессе перемещения не участвуют.
    Монстры, которые атакую - наносят удары.
"""
def all_monsters_moving(player: Player, level: Level, temp_pos: Position):
    for room in level.rooms:
        #if room.is_visited: # теперь двигаем просто всех монстров
        for monster in room.monsters:
            monster_moving(player, monster, level, temp_pos)

"""!
    @detail Функция поиска лута в месте нахождения игрока.
    @return объект класса Item либо None. Обязательно проверять перед запросом
    атрибутов во избежание ошибок.
"""
def find_item_in_room(player: Player, level: Level):
    room_num = get_room_number(player.position, level)
    if room_num != -1:
        room = level.rooms[room_num]
        number = -1
        for i in range(len(room.items)):
            if is_equal_x_y(room.items[i].position, player.position):
                number = i
                break

        if number != -1:
            item = room.items[number]
            if player.inventory.add_item(item.type, item):
                item = room.items.pop(number)
                return item

    return None

"""
def pattern_zombie(monster: Monster, level: Level, temp_pos: Position):
    monster.direction = Directions.STOP
    cur_pos = temp_pos
    for _ in range(MConst.MAX_TRIES_TO_MOVE):
        cur_dir = random.randint(1, MConst.SIMPLE_DIRECTIONS) % MConst.SIMPLE_DIRECTIONS
        cur_pos.copy_position(monster.position)
        move_character_by_direction(Directions(cur_dir), cur_pos)
        if not check_outside_border(cur_pos, level) and check_unoccupied_level(cur_pos, level):
            monster.direction = cur_dir
            monster.change_position(cur_pos)
            break

def pattern_vampire(monster: Monster, level: Level, temp_pos: Position):
    monster.direction = Directions.STOP
    cur_pos = temp_pos
    for _ in range(MConst.MAX_TRIES_TO_MOVE):
        cur_dir = random.randint(1, MConst.ALL_DIRECTIONS) % MConst.ALL_DIRECTIONS
        cur_pos.copy_position(monster.position)
        move_character_by_direction(Directions(cur_dir), cur_pos)
        if not check_outside_border(cur_pos, level) and check_unoccupied_level(cur_pos, level):
            monster.direction = cur_dir
            monster.change_position(cur_pos)
            break

def pattern_snake(monster: Monster, level: Level, temp_pos: Position):
    cur_pos = temp_pos
    for _ in range(MConst.MAX_TRIES_TO_MOVE):
        cur_dir = (MConst.SIMPLE_TO_DIAGONAL_SHIFT +
                   random.randint(1, MConst.DIAGONAL_DIRECTIONS) % MConst.DIAGONAL_DIRECTIONS)
        cur_pos.copy_position(monster.position)
        move_character_by_direction(Directions(cur_dir), cur_pos)
        # пусть тупит эта зараза в коридорах, итак ей жирно ходить диагонально
        if not check_outside_border(cur_pos, level) and check_unoccupied_level(cur_pos, level):
            monster.direction = cur_dir
            monster.change_position(cur_pos)
            break
"""