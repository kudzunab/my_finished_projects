from src.domain.entities import Player, Level, Item, ItemInRoom, Position
from . import move_character_by_direction
from .character_fight import is_equal_x_y
from .character_move import get_room_number
from .character_move import check_outside_border
from ..entities import ItemType, Directions

"""!
    @detail Функция исследования клетки, возвращает объект класса ItemInRoom.
    Проверяем. 
    ! Изменила на позицию игрока
"""
def get_item_in_room(player_pos: Position, level: Level):
    room_num = get_room_number(player_pos, level)
    if room_num == -1:
        return None, -1  # просто там не может быть опций
    else:
        room = level.rooms[room_num]
        # room.items is ItemsInRoom. ItemsInRoom.storage is dict
        for items_type_list in room.items.storage.values():
            for item_in_room in items_type_list:
                if is_equal_x_y(item_in_room.position, player_pos):
                    return item_in_room, room_num

        return None, room_num  # нашли опцию и добавим


"""!
    @detail Функция сброса в комнате(в коридоре скинуть не получится) в месте нахождения игрока.
    @return True, если можно бросить, то добавляет объект в комнату, присваивая ему
    координаты игрока.
    должна выкидываться по какой-то клавише?
"""


def drop_item_in_room(player: Player, level: Level, item: Item):
    poss_poz = Position()
    for direction in [Directions.RIGHT, Directions.LEFT, Directions.BACK, Directions.FORWARD,
                      Directions.STOP]:  # Directions.STOP

        poss_poz.copy_position(player.position)
        move_character_by_direction(direction, poss_poz)
        if check_outside_border(poss_poz, level):
            _item, room_num = get_item_in_room(poss_poz, level)
            if _item is None and room_num != -1:
                item_in_room = ItemInRoom(item, poss_poz)
                level.rooms[room_num].items.storage[item.type].append(item_in_room)
                level.rooms[room_num].items.change_num(item.type, 1)  # обновляю счетчики, но я не использую ограничения
                level.rooms[room_num].items.total_sum += 1
                # обновляю счетчики, но они походу лишние.
                if item == player.weapon:
                    player.weapon = Item(ItemType.NONE)
                    player.weapon.name = "NO WEAPON"

                else:
                    player.inventory.del_item(item.type, item)
                return True
    return False


"""!
    @detail подбираем предмет с пола, проходя. Автоматически добавляется в инвентарь,
    если есть свободное место, для логов можно использовать результат,
    запускаем на каждом ходу технически.
    @return item, is_full. Если предмета нет, то вместо предмета возвращаем None.
    чтобы отличить полон ли инвентарь ввели флаг is_full. Если не влезло в инвентарь,
    то флаг вернет True, что можно отразить в логе.

    Работает в геймплее отлично. Подбирается все, что нужно. Выводит сообщение.
"""


def take_item(player: Player, level: Level):
    is_occupied = True
    item_in_room, room_num = get_item_in_room(player.position, level)
    if room_num == -1 or item_in_room is None:
        is_occupied = False
        return None, is_occupied  # ничего не надо писать в случае отсутствия в данной клетке предмета
    if player.add_item_to_inventory(item_in_room):

        # определяем тип найденного предмета
        item_type = item_in_room.item.type

        # находим список предметов нужного типа в словаре
        list_of_items = level.rooms[room_num].items.storage[item_type]
        find_ind = list_of_items.index(item_in_room)
        level.rooms[room_num].items.del_item(item_type, find_ind)
        is_occupied = False
        return item_in_room.item, is_occupied  # для лога, чтобы посмотреть название и тип или еще чего

    return None, is_occupied  # нет места в инвентаре


"""!
    Функция для применения чего-либо
    return_option_type - возвращает номер позиции в словаре. -1, если не оно
    return_item_index - возвращает номер в списке, -1, если не оно
    Оружие, эликсиры, еда, знаки и прочее.
"""

"""
def use_item(player: Player, item_type: ItemType, number_in_list, level: Level, turn_to_deactivate):
    # эти цифрв должны передаваться через действия при нажатии клавишь с
    # клавиатуры, подозреваю,
    #
    # что после обращения к инвентарю должна сначала
    # нажиматься клавиша с типом, а потом с номером
    if item_type == -1 or number_in_list == -1:
        return False

    choose_item = player.inventory.take_item(item_type, number_in_list)
    if not choose_item:
        return False

    if item_type == ItemType.WEAPON:
        player.put_weapon_to_inventory(level)
        # Теперь вызываем экипировку
        return player.equipt_weapon(choose_item)
    else:
        player.use_item(choose_item, turn_to_deactivate)
        return True

"""
"""
    По идее мы его запускаем на каждом ходе игрока, если в buffs что-то есть.
    Возвращает тип bool. Но он нигде особо применения не имеет.
"""


def update_the_buff_state(player: Player, counts: int):
    health = player.buffs.current_health_buff_num
    strength = player.buffs.current_strength_buff_num
    agility = player.buffs.current_agility_buff_num

    if health == 0 and strength == 0 and agility == 0:
        return []

    # cur_time = int(time.time())
    d_buffs = player.check_the_buff_state(counts)

    return d_buffs

"""
# я бы положила это в контроллеры, на я не знаю, где у тебя замаскирован Level? ему место в handler.py
# это кусок кода, возможно, будет работать сразу, но не уверена, но логика тут подробная. Не настаивают
def work_with_dir_action(action: KEY_TO_ACTION, level: Level, player: Player, temp_pos: Position,
                         battle_picture: BattlePicture):
    res = []
    _dict = {KEY_TO_ACTION.MOVE_UP: Directions.FORWARD,
             KEY_TO_ACTION.MOVE_DOWN: Directions.BACK,
             KEY_TO_ACTION.MOVE_LEFT: Directions.LEFT,
             KEY_TO_ACTION.MOVE_RIGHT: Directions.RIGHT}
    direction = _dict.get(action, Directions.STOP)
    if action in _dict:
        nearest_monsters = find_nearest_monsters(player, level)
        is_hit, current_battle = check_player_attack(player, direction, battle_picture, nearest_monsters, temp_pos)
        if current_battle and is_hit:
            results = attack_procedure(player, battle_picture, current_battle, 0)
            res.extend(results)
            # nearest_monsters = find_nearest_monsters(player, level)
            all_monsters_moving(player, level, temp_pos)  # , nearest_monsters
            results = attack_procedure(player, battle_picture, current_battle, 1)
            res.extend(results)
            remove_dead_monsters(level)

        else:
            move_character_by_direction(direction, temp_pos)
            if check_outside_border(temp_pos, level):
                player.position.change_position(temp_pos)
                all_monsters_moving(player, level, temp_pos)  # , nearest_monsters
                res.append("moving")
                # сюда еще можно добавить подбор опции из кода ниже
            else:
                res.append("impossible to move")

    return res
"""