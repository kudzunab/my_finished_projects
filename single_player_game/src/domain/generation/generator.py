import random
#import sys
#from pathlib import Path
#src_path = str(Path(__file__).resolve().parent.parent.parent)
#if src_path not in sys.path:
#    sys.path.insert(0, src_path)

from src.domain.entities.entities import Item, MonsterType, StatType, ItemType
from src.domain.entities.entities import Position, MonsterDict, Monster, ItemInRoom
from src.domain.entities.entities import Player, Room, Passage, Level, BaseParam, Const
# from src.domain.entities.test import BaseParam, Const
from src.domain.characters.character_move import simple_pattern, pattern_ogr, pattern_ghost
"""!
    @brief экземпляр класса ребро (Edge).
    @detail Это внутренний класс, он не нужен вне этого блока.
    @param u - номер начальной комнаты;
    @param v - номер конечной комнаты.
"""
class _Edge:
    def __init__(self, u: int, v: int):
        self.u = u
        self.v = v
"""!
    @brief экземпляр класса Graph.
    @detail Это внутренний класс, он не нужен вне этого блока. Позволяет использовать графы.
"""
class _Graph:
    def __init__(self):
        self.massive = []
        self.edge_num = 0
    def add_edge(self, u: int, v: int):
        edge = _Edge(u, v)
        self.massive.append(edge)
        self.edge_num += 1

    """!
        @brief метода класса, который генерирует полный список ребер, соединяющих соседний комнаты.
    """
    def generate_all_edges(self):
        height = Const.ROOMS_IN_HEIGHT
        width = Const.ROOMS_IN_WIDTH
        for i1 in range(height):
            for i2 in range(width - 1):
                u = i1*width + i2
                v = u + 1
                self.add_edge(u, v)
        for i1 in range(height - 1):
            for i2 in range(width):
                u = i1*width + i2
                v = u + width
                self.add_edge(u, v)
    """!
        @brief метода класса, который случайным образом перемешивает все полученные ребра случайным
            образом.
    """
    def shuffle_edges(self):
        if self.massive:
            random.shuffle(self.massive)
    """!
        @brief метода класса, который создает минимальное дерево, выбирая Const.ROOM_NUMBER - 1
            ребер из сформированного массива.
    """
    def get_min_tree(self):
        self.massive.clear()
        self.edge_num = 0
        self.generate_all_edges()
        self.shuffle_edges()
        new_mass = [{_} for _ in range(Const.ROOM_NUMBER)]
        min_tree = []

        for edge in self.massive:
            u, v = edge.u, edge.v
            ind1, ind2 = -1, -1
            for j in range(len(new_mass)):
                if u in new_mass[j]:
                    ind1 = j
                if v in new_mass[j]:
                    ind2 = j
                if ind1 != -1 and ind2 !=-1:
                    break

            if ind1 != ind2:
                new_mass[ind1] = new_mass[ind1] | new_mass[ind2]
                min_tree.append(edge)
                new_mass[ind2].clear()
            if len(min_tree) == Const.ROOM_NUMBER - 1:
                break

        return min_tree
"""!
    @brief вспомогательная функция для generate_passages.
    @detail ищет у минимального дереве вершины, которые соединены только с одной вершиной.
    @return список листьев дерева. 
"""
def find_and_fill_exit_and_entr(min_tree: list):
    v_list = [0 for _ in range(Const.ROOM_NUMBER)]
    for edge in min_tree:
        v_list[edge.u] += 1
        v_list[edge.v] += 1
    uniq_list = []
    for i in range(len(v_list)):
        if v_list[i] == 1:
            uniq_list.append(i)

    random.shuffle(uniq_list)
    return uniq_list
"""!
    @brief вспомогательная функция для generate_passages.
    @detail проверяет, нaходится ли точка на границе комнаты и является дверью.
"""
def find_the_door(p: Position, room: Room, passage: Passage, is_init: bool):
    pos = room.position

    #координата в блоках, ровно на стене
    on_v_wall = (p.x == pos.x or p.x == pos.x + pos.dx - 1) and (pos.y < p.y < pos.y + pos.dy - 1)
    on_h_wall = (p.y == pos.y or p.y == pos.y + pos.dy - 1) and (pos.x < p.x < pos.x + pos.dx - 1)

    if on_v_wall or on_h_wall:
        if is_init:
            passage.change_entrance(p)
        else:
            passage.change_exit(p)


def generate_passages(level: Level, _temp_pos: Position):
    min_tree = _Graph().get_min_tree()
    uniq_list = find_and_fill_exit_and_entr(min_tree)
    level.entrance = uniq_list[0]
    level.exit = uniq_list[1]

    for edge in min_tree:
        new_passage = Passage()
        i_room = level.rooms[edge.u]
        f_room = level.rooms[edge.v]
        c_i = [i_room.position.x + i_room.position.dx // 2, i_room.position.y + i_room.position.dy // 2]
        c_f = [f_room.position.x + f_room.position.dx // 2, f_room.position.y + f_room.position.dy // 2]

        for r in [i_room, f_room]:
            if c_i[1] == r.position.y: c_i[1] += 1
            if c_i[1] == r.position.y + r.position.dy - 1: c_i[1] -= 1

        for r in [i_room, f_room]:
            if c_f[0] == r.position.x: c_f[0] += 1
            if c_f[0] == r.position.x + r.position.dx - 1: c_f[0] -= 1

        for x in range(min(c_i[0], c_f[0]), max(c_i[0], c_f[0]) + 1):
            _temp_pos.change_position(x, c_i[1], 1, 1)
            new_passage.add_point(_temp_pos)
            find_the_door(_temp_pos, i_room, new_passage, True)
            find_the_door(_temp_pos, f_room, new_passage, False)

        for y in range(min(c_i[1], c_f[1]), max(c_i[1], c_f[1]) + 1):
            if y == c_i[1]: # убираю дубликат точки из  коридора
                continue

            _temp_pos.change_position(c_f[0], y, 1, 1)
            new_passage.add_point(_temp_pos)
            find_the_door(_temp_pos, i_room, new_passage, True)
            find_the_door(_temp_pos, f_room, new_passage, False)

        level.add_passage(new_passage)
"""!
    @brief Функция генерации количество лута в комнате.
    @detail Произвольным образорм сначала определяется суммарное число лута, а затем отдельно для каждой
        определяется ее тип с увеличением соответствуюего параметра
    @param level_num - номер уровня.
    @return food_num - число объектов класса еда,
        elixir_num - число объектов класса эликсир,
        scroll_num - число объектов класса свиток,
        weapon_num - число объектов класса оружие.
"""
def get_num(level_num):
    max_loot_num = max(1, Const.MAX_CONSUMABLES_PER_ROOM - level_num // (Const.LEVEL_UPDATE_DIFFICULTY * 2))
    sum_num = random.randint(1, max_loot_num)
    treasure_num = 0
    if random.random() < 0.5 + level_num/100:
        treasure_num = 1
    items = [ItemType.FOOD, ItemType.SCROLL, ItemType.ELIXIR, ItemType.WEAPON]
    weights = [40, 25, 25, 10]

    loot_pool = random.choices(items, weights, k = sum_num)
    return (loot_pool.count(ItemType.FOOD),
            loot_pool.count(ItemType.SCROLL),
            loot_pool.count(ItemType.ELIXIR),
            loot_pool.count(ItemType.WEAPON),
            treasure_num)
"""!
    @brief Функция генерации массива комнат уровня.
    @detail Функция создает и частично заполняет экземпляры класса Room(генерит число лута в
        каждой комнате, определяет размеры комнат) и добавляет их в массив комнат.
    @return массив экземпляров класса Room с заполненными значениями атрибута Position и number.
"""
def generate_rooms_in_level():
    rooms = []
    for i in range(Const.ROOM_NUMBER):
        room_width = random.randint(Const.MIN_ROOM_WIDTH, Const.MAX_ROOM_WIDTH)
        min_x_in_room = (i % Const.ROOMS_IN_WIDTH)*Const.REGION_WIDTH + 1
        max_x_in_room = (i % Const.ROOMS_IN_WIDTH + 1)*Const.REGION_WIDTH - room_width - 1
        x_coord = random.randint(min_x_in_room, max_x_in_room)

        room_height = random.randint(Const.MIN_ROOM_HEIGHT, Const.MAX_ROOM_HEIGHT)
        min_y_in_room = (i // Const.ROOMS_IN_WIDTH)*Const.REGION_HEIGHT + 1
        max_y_in_room = (i // Const.ROOMS_IN_WIDTH + 1)*Const.REGION_HEIGHT - room_height - 1
        y_coord = random.randint(min_y_in_room, max_y_in_room)
        my_room = Room(i)
        my_room.position.change_position(x_coord, y_coord, room_width, room_height)
        rooms.append(my_room)
    return rooms
"""!
    @brief уснатонва игрока в начальную позицию.
"""
def generate_player(level: Level, player: Player):
    player_room = level.entrance
    pos = level.init_position
    player.type = MonsterType.PLAYER
    player.is_first_hit = True
    player.change_poz(pos)
    return player_room

"""!
    @brief Генерация входа
    @param level - объект класса Level;
    @param player - объект класса Player.
    @return номер входной комнаты.
"""
def generate_entrance(level: Level):
    entrance_room_num = level.entrance
    entrance_room = level.rooms[entrance_room_num]
    position = generate_position(entrance_room)
    level.entrance = entrance_room_num
    level.init_position = position
    return entrance_room_num

def generate_exit_point(level: Level):

    exit_room_num = level.exit
    room = level.rooms[exit_room_num]
    x_center = room.position.x + room.position.dx//2
    y_center = room.position.y + room.position.dy//2

    level.end_position.x = x_center #random.randint(x_center - 1, x_center + 1)
    level.end_position.y = y_center #random.randint(y_center - 1, y_center + 1)
    level.end_position.dx = 1
    level.end_position.dy = 1
"""!
    @brief Функция проверки, возможно ли поместить указанный объект в указанную клетку уровня.
    @param level - объект класса Level;
    
    @return 0 - если клетка свободна, 1 - если в клетке расходник, 2 - если в клетке монстр,
        3 - если выход с уровня, -1 - генерация на месте входа на уровень
    пока без корридоров, потом добавлю
"""
def checked_is_occupied(level: Level, room_number: int, x: int, y: int):

    is_occupied = 0 # 2 - занято монстром, 1 - расходником, 0 - свободно, 3 - выход из уровня
    this_room = level.rooms[room_number]

    if level.entrance == room_number:
        if x == level.init_position.x and y == level.init_position.y:
            is_occupied = -1

    if level.exit == room_number:
        if x == level.end_position.x and y == level.end_position.y:
            is_occupied = 3

    if is_occupied == 0:
        for items in this_room.items.storage.values():
            for item in items:
                if x == item.position.x and y == item.position.y:
                    is_occupied = 1
                    break

    if is_occupied == 0:
        for m in this_room.monsters:
            if x == m.position.x and y == m.position.y:
                is_occupied = 2
                break

    return is_occupied

"""!
    @brief Функция генерации обхекта класса Position.
    @detail На основе данных класса Room создается экземпляр класса Position, в котором случайным образом генерятся
        параметры X и Y, а значения dX и dY устанавливаются равными 1.
    @param room - экземпляр класса Room, внутри которого будет располагать объект.
    @return новый заполненный экземпляр класса Position, находящийся внутри экземпляра класса room.
"""
def generate_position(room: Room):

    position = Position()

    min_obj_x = room.position.x + 1
    min_obj_y = room.position.y + 1
    max_obj_x = min_obj_x + room.position.dx - 3
    max_obj_y = min_obj_y + room.position.dy - 3
    obj_x = random.randint(min_obj_x, max_obj_x)
    obj_y = random.randint(min_obj_y, max_obj_y)
    position.change_position(obj_x, obj_y, 1, 1)
    return position
"""!
    @brief Функция заполнения параметров монстров.
    @detail На основе данных об уровня у сгенерированных объектов класса Monster устанавливаются параметры с учетом
        уровня.
    @param monster - экземпляр класса Monster;
    @param level_num - номер уровня.
"""
def generate_monster_stats(monster: Monster, level_num: int):

    all_types = list(MonsterDict.stats.keys())
    if level_num <= 3:
        possible_types = [m for m in all_types if m not in [MonsterType.OGRE, MonsterType.SNAKE]]
    else:
        possible_types = all_types

    monster_type = random.choice(possible_types)
    percent_update = Const.PERCENTS_UPDATE_DIFFICULTY_MONSTERS * level_num/100
    my_inf = MonsterDict.stats[monster_type]
    monster.type = monster_type
    monster.hostility = int(my_inf[StatType.HOSTILITY])
    monster.stats.health = int(my_inf[StatType.HEALTH]*BaseParam.STATS[StatType.HEALTH]*(1 + percent_update))
    monster.stats.agility = int(my_inf[StatType.AGILITY]*BaseParam.STATS[StatType.AGILITY]*(1 + percent_update))
    monster.stats.strength = int(my_inf[StatType.STRENGTH]*BaseParam.STATS[StatType.STRENGTH]*(1 + percent_update))

    if monster_type in [MonsterType.VAMPIRE, MonsterType.ZOMBIE, MonsterType.SNAKE]:
        monster.pattern = simple_pattern
    elif monster_type == MonsterType.GHOST:
        monster.pattern = pattern_ghost
    elif monster_type == MonsterType.OGRE:
        monster.pattern = pattern_ogr
"""!
    @brief Функция генерации и добавления монстров в комнаты уровня
    @detail Заполняет монстрами не больше половины комнаты
    @param _temp_pos - буфер для координат. Можно использовать 
"""

def generate_monsters(level: Level, level_num: int, entrance_num: int, _temp_pos: Position):
    level.level_num = level_num
    max_monster_num = Const.MAX_MONSTERS_PER_ROOM + level.level_num // Const.LEVEL_UPDATE_DIFFICULTY
    for i in range(Const.ROOM_NUMBER):
        my_room = level.rooms[i]
        if i != entrance_num:
            total_cells = (my_room.position.dx - 3) * (my_room.position.dy - 3)
            monster_num = min(random.randint(0, max_monster_num), total_cells // 2)
            for j in range(monster_num):
                room_monster = Monster()
                generate_monster_stats(room_monster, level_num)

                attempts = 0
                added = False
                spawn_pos = None
                while attempts < 50:
                    spawn_pos = generate_position(my_room)
                    is_occupied = checked_is_occupied(level, i, spawn_pos.x, spawn_pos.y)

                    if is_occupied == 0:
                        added = True
                        break

                    attempts += 1

                if added:
                    room_monster.change_position(spawn_pos)
                    my_room.add_monster(room_monster)
                
                
"""!
    brief Функция определения верхнего порога для указанного типа параметра.
"""
def increase_calc(player: Player, level_num: int, item_type: ItemType):
    if item_type == ItemType.FOOD:
        val = int(player.regen_limit * Const.MAX_PERCENT_FOOD_REGEN_FROM_HEALTH / 100)
        #max_increase = max(5, val)
        return random.randint(15, max(15, val)) + level_num // 3
    elif item_type == ItemType.WEAPON:
        #base_power = random.randint(50, 150) + level_num // 2
        base_power = random.randint(5, 15) + level_num // 2
        dop_bonus = 1 if (level_num > 10 and random.random() < 0.2) else 0
        return base_power + dop_bonus
    elif item_type in [ItemType.ELIXIR, ItemType.SCROLL]:
          #max_increase = 1
        return random.randint(5, 10) + level_num // 3
    elif item_type == ItemType.TREASURE:
        min_gold = 10 + 5 * level_num
        max_gold = 50 + 10 * level_num
        return random.randint(min_gold, max_gold)
    else:
        max_increase = 0
    return max_increase
"""!
@brief Заполняем общие параметры
"""
def fill_item_common_data(item: Item, item_type: ItemType, player: Player, level_num: int):
    item.type = item_type
    return increase_calc(player, level_num, item_type)
"""!
    brief Функция генерация объекта класса Food
"""
def generate_food_data(item: Item, player: Player, level_num: int):
    names = ["Ration of the Ironclad", "Crimson Berry Cluster",
             "Loaf of the Forgotten Baker", "Smoked Wyrm Jerky",
             "Golden Apple of Vitality", "Hardtack of the Endless March",
             "Spiced Venison Strips", "Honeyed Nectar Bread",
             "Dried Mushrooms of the Deep"]
    item.health = fill_item_common_data(item, ItemType.FOOD, player, level_num)
    item.name = random.choice(names)
"""!
    brief Функция генерация объекта класса Elixir
"""
def generate_elixir_data(item: Item, player: Player, level_num: int):
    names = ["Elixir of the Jade Serpent", "Potion of the Phantom's Breath",
        "Vial of Crimson Vitality", "Draught of the Frozen Star",
        "Elixir of the Shattered Mind", "Potion of the Wandering Soul",
        "Vial of Ember Essence", "Elixir of the Obsidian Veil",
        "Potion of the Howling Wind"]

    p_stats = [StatType.HEALTH, StatType.AGILITY, StatType.STRENGTH]
    stat_type = random.choice(p_stats)
    item.subtype = stat_type
    item.value = fill_item_common_data(item, ItemType.ELIXIR, player, level_num)
    item.duration = random.randint(Const.MIN_ELIXIR_DURATION_SECONDS, Const.MAX_ELIXIR_DURATION_SECONDS)
    item.name = random.choice(names)
"""!
    @brief Функция генерации обекта класса Scroll.
"""
def generate_scroll_data(item: Item, player: Player, level_num: int):
    names = ["Scroll of Shadowstep", "Parchment of Eternal Flame",
        "Manuscript of Forgotten Truths", "Scroll of Iron Will",
        "Vellum of the Void", "Scroll of Whispers",
        "Tome of the Lost King", "Scroll of Unseen Paths",
        "Parchment of Thunderous Roar"]
    p_stats = [StatType.HEALTH, StatType.AGILITY, StatType.STRENGTH]
    stat_type = random.choice(p_stats)
    item.subtype = stat_type
    item.name = random.choice(names)
    item.value = fill_item_common_data(item, ItemType.SCROLL, player, level_num)

"""!
    @brief Функция генерации объекта класса Weapon.
"""
def generate_weapon_data(item: Item, player: Player, level_num: int):
    names = ["Blade of the Forgotten Dawn", "Obsidian Reaver",
        "Fang of the Shadow Wolf", "Ironclad Cleaver",
        "Crimson Talon", "Thunderstrike Maul",
        "Serpent's Kiss Dagger","Voidrend Sword",
        "Ebonheart Spear"]
    item.name = random.choice(names)
    item.strength = fill_item_common_data(item, ItemType.WEAPON, player, level_num)
"""!
    @brief Функция генерации объекта класса Weapon.
"""
def generate_treasure_data(item: Item, player: Player, level_num: int):
    item.name = 'Gold'
    item.value = fill_item_common_data(item, ItemType.TREASURE, player, level_num)
"""!
    @brief Функция генерации ключа.
"""
def generate_key_data(item: Item, locked_room_num: int):
    item.type = ItemType.KEY
    #item.subtype - цвет
    item.value = locked_room_num # номер замертой двери

"""!
    @brief Функция генерации расходника.
    @detail Функция генерирует экземпляр расходника типа item_type, затем случайным образом координату внутри выбранной
        комнаты, после чего помещает туда объект класса FoodInRoom/ElixirInRoom/WeaponInRoom/ScrollInRoom
        в зависимости от типа.
    @param level объект класса Level;
    @param room_number - номер комнаты, в которой будет находится расходник;
    @param item_type - объект класса ItemType;
    @param player - объект класса Player.
"""

def generate_item(level: Level, room_number: int, item_type: ItemType, player: Player, _temp_pos: Position):
    items_config = {
        ItemType.FOOD: generate_food_data,
        ItemType.ELIXIR: generate_elixir_data,
        ItemType.WEAPON: generate_weapon_data,
        ItemType.SCROLL: generate_scroll_data,
        ItemType.TREASURE: generate_treasure_data,
        ItemType.KEY: generate_key_data
    }
    if item_type not in items_config:
        return

    generate_func = items_config[item_type]
    my_room = level.rooms[room_number]
    attempt = 0
    is_occupied = 0
    pos = None
    while attempt < 100:
        pos = generate_position(my_room)
        is_occupied = checked_is_occupied(level, room_number, pos.x, pos.y)
        attempt += 1
        if is_occupied == 0:
            break
    if is_occupied != 0:
        return

    new_item = Item(item_type)

    if item_type == ItemType.KEY:
        generate_func(new_item, -1) #пока не знаю номер двери
    else:
        generate_func(new_item, player, level.level_num)

    item_in_room = ItemInRoom(new_item, pos)
    level.rooms[room_number].items.add_item(item_type, item_in_room)

"""!
    @brief Функция генерации расходников уровня.
    @detail Функция создает разные типы расходников для всех комнат уровня и сохраняет
        соответствующие параметры в объекте класса level.
    @param level - объект класса Level;
    @param player - объект класса Player.
"""
def generate_consumables(level: Level, player: Player, _temp_pos: Position):
    for i in range(Const.ROOM_NUMBER):

        food_num, elixir_num, scroll_num, weapon_num, treasure_num = get_num(level.level_num)

        if i == level.entrance:
            #print(f"DEBUG: Создаю оружие в стартовой комнате {i}")
            if weapon_num == 0 and level.level_num == 1:
                weapon_num += 1
        for _ in range(food_num): generate_item(level, i, ItemType.FOOD, player, _temp_pos)
        for _ in range(elixir_num): generate_item(level, i, ItemType.ELIXIR, player, _temp_pos)
        for _ in range(scroll_num): generate_item(level, i, ItemType.SCROLL, player, _temp_pos)
        for _ in range(weapon_num): generate_item(level, i, ItemType.WEAPON, player, _temp_pos)
        for _ in range(treasure_num): generate_item(level, i, ItemType.TREASURE, player, _temp_pos)
"""!
    @brief Функция очистки данных уровня.
    @param level - объект класса Level.
"""
def clean_data(level: Level):
    level.init_position = Position()
    level.entrance = -1
    level.exit = -1
    level.end_position = Position()
    for i in range(Const.ROOM_NUMBER):
        room = level.rooms[i]
        room.monster_num = 0
        room.food_num = 0
        room.items.total_sum = 0
        room.items.food_num = 0
        room.items.elixir_num = 0
        room.items.scroll_num = 0
        room.items.weapon_num = 0
        room.items.treasure_num = 0
        for item_type in room.items.storage:
            room.items.storage[item_type].clear()

        room.monsters.clear()
    level.rooms_with_key.clear()
    level.rooms.clear()  #добавила очистку
    level.passages.clear() #добавила очистку

def generate_next_level(level: Level, player: Player, _temp_pos: Position):
    # защита от глюков загрузки
    if level.level_num >=0:
        level.level_num += 1
    else: level.level_num = 0

    if level.level_num > 1:
        clean_data(level)

    level.rooms = generate_rooms_in_level()
    level.passages.clear()
    generate_passages(level, _temp_pos)
    generate_entrance(level)
    generate_exit_point(level)
    room_number = generate_player(level, player) # перенесла выше
    # надо здесь ключи добавить
    generate_consumables(level, player, _temp_pos)
    generate_monsters(level, level.level_num, level.entrance, _temp_pos)
    level.rooms[room_number].is_visited = True

if __name__ =="__main__":
    from src.domain.entities import Player, Level, Position
    from src.domain.generation import generate_next_level, generate_player
    # Создаем объекты
    test_player = Player()
    test_level = Level()
    temp_pos = Position()
    generate_next_level(test_level, test_player, temp_pos)
    print(test_level.entrance, test_level.init_position.x, test_level.init_position.y)
    print(test_player.position.x, test_player.position.y)
    #if p and p.money == 999:
    #    print("Проверка пройдена: данные загружены корректно!")
