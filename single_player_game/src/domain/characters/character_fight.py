import random
from src.domain.entities.entities import MonsterType, ItemType, Directions
from src.domain.entities.entities import Position, Monster
from src.domain.entities.entities import Player, Level, Entity
from dataclasses import dataclass

@dataclass(frozen=True)
class FConst:
    INITIAL_HIT_CHANCE = 70
    STANDARD_AGILITY = 50
    AGILITY_FACTOR = 0.3
    INITIAL_DAMAGE = 30
    STANDARD_STRENGTH = 50
    STRENGTH_FACTOR = 0.3
    STRENGTH_ADDITION = 65
    SLEEP_CHANCE = 15
    MAX_HP_PART = 10
    LOOT_AGILITY_FACTOR = 0.2
    LOOT_HP_FACTOR = 0.5
    LOOT_STRENGTH_FACTOR = 0.5
    MAXIMUM_FIGHTS = 8

class Battle:
    __slots__ = ('monster', 'is_attack', 'is_finish')
    def __init__(self, monster: Monster, is_attack):
        self.monster = monster
        self.is_attack = is_attack
        self.is_finish = False

class BattlePicture:
    __slots__ = ('battles', 'killed_monsters')
    def __init__(self):
        self.battles = []
        self.killed_monsters = []
    def clear(self):
        self.battles.clear()
        self.killed_monsters.clear()
    def battle_num(self):
        return len(self.battles)

    def killed_num(self):
        return len(self.killed_monsters)

    def add_battle(self, new_battle: Battle):
        #if new_battle.is_attack:
        self.battles.append(new_battle)

    def del_battle(self, cur_battle: Battle):
        if cur_battle.is_finish: # and new_battle.is_killed:

            if cur_battle in self.battles:
                self.battles.remove(cur_battle)

            if cur_battle not in self.killed_monsters:
                self.killed_monsters.append(cur_battle)

"""!
    @brief Вспомогательная функция calc_attack_result.
    @detail Функция, вычисляющая награду игроку за убийство монстра.
    @return -1 - если объект не монстр и количество золота в противном случае.
"""
def calculation_loot(monster: Entity):
    if isinstance(monster, Monster):
        gold = (monster.stats.agility * FConst.LOOT_AGILITY_FACTOR +
                monster.stats.health * FConst.LOOT_HP_FACTOR +
                monster.stats.strength * FConst.LOOT_STRENGTH_FACTOR +
                random.randrange(20))

        return int(gold)
    return -1
"""!
    @brief Вспомогательная функция calc_attack_result.
    @detail Функция, вычисляющая возможность попадания.
    @return True - если есть попадание, False - в противном случае.
"""
def is_hit_to_goal(attacker: Entity, defender: Entity):
    if defender.type == MonsterType.VAMPIRE and defender.is_first_hit:
        defender.is_first_hit = False
        return False

    chance_to_hit = (attacker.stats.agility - defender.stats.agility)/2 + 70
    chance_to_hit = max(5, min(95, chance_to_hit))

    if attacker.type != MonsterType.OGRE and random.randint(1,100) > chance_to_hit:
        return False

    if attacker.type == MonsterType.OGRE:
        attacker.is_resting = True

    return True
"""!
    @brief Вспомогательная функция calc_attack_result.
    @detail Функция, вычисляющая урон одного объекта по другому, на основе характеристик и эффеектов.
        @param attacker нападающий объект класса Entity(Monster/Player);
        @param defender объект класса Entity, получающий урон.
    @return damage - урон (int), который был нанесен объекту, на который напали.
"""
def damage_calc(attacker: Entity, defender: Entity):
    strength_bonus = (attacker.stats.strength - FConst.STANDARD_STRENGTH)*FConst.STRENGTH_FACTOR
    damage0 = FConst.INITIAL_DAMAGE + strength_bonus

    if attacker.type == MonsterType.PLAYER:
        if attacker.weapon.type == ItemType.NONE:
            damage = damage0
        else:
            # искуственно ограничиваем, ради красоты логов
            damage = min(damage0 + attacker.weapon.strength*10, defender.stats.health) #FConst.STRENGTH_ADDITION

    elif attacker.type == MonsterType.VAMPIRE:
        damage = defender.regen_limit / FConst.MAX_HP_PART

    else:
        damage = damage0

    return max(0, int(damage))
"""
    @detail Одиночный удар по персонажу, учитывает состояние отдыха, если оно было True - то
    восстанавливает на False.
    @return gold, damage. Возможны исходы: -1, damage — монстр убил игрока,
        0, damage — если оба живы(damage = 0 в случае промаха, в случае пропуска damage = -1),
        gold, damage - если выиграл игрок;
"""
def calc_attack_result(attacker: Entity, defender: Entity):
    if attacker.is_resting:
        attacker.is_resting = False
        return 0, -1

    damage = 0
    if is_hit_to_goal(attacker, defender):
        damage = damage_calc(attacker, defender)
        is_dead = defender.take_damage(damage)

        # вампир ворует здоровье максимальное при успешном ударе
        if attacker.type == MonsterType.VAMPIRE and defender.type == MonsterType.PLAYER:
            defender.regen_limit = max(1, defender.regen_limit - 1)

        # змей может заморозить игрока на ход
        if attacker.type == MonsterType.SNAKE and defender.type == MonsterType.PLAYER:
            if random.random() < FConst.SLEEP_CHANCE / 100:
                defender.is_resting = True

        # проверка смерти обороняющейся стороны
        if is_dead:
            if isinstance(attacker, Player) and defender.type != MonsterType.PLAYER:
                gold = calculation_loot(defender)
                if gold > 0:
                    attacker.money += gold
                return gold, damage
            elif defender.type == MonsterType.PLAYER:
                return -1, damage

    return 0, damage
"""!
    @brief Вспомогательная функция find_nearest_monsters.
    @detail Функция возвращает True, если указанные позиции находятся на расстоянии 1 по любому из направлений,
    включая диагональ. 
"""
def is_equal_x_y(pos1: Position, pos2: Position):
    return pos1.x == pos2.x and pos1.y == pos2.y
"""!
    @brief Вспомогательная функция is_contact, find_nearest_monsters.
    @detail Функция возвращает True, если указанные позиции находятся на расстоянии 1 по вертикали
    или горизонтали.
"""
def is_gv_neighbor(pos1: Position, pos2: Position):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y) == 1
"""!
    @brief Вспомогательная функция find_nearest_monsters.
    @detail Функция возвращает True, если указанные позиции находятся на расстоянии 1 по любому из
    направлений, включая диагональ. 
"""
def is_neighbor(pos1: Position, pos2: Position):
    return max(abs(pos1.x - pos2.x), abs(pos1.y - pos2.y)) == 1
"""!
    @brief Вспомогательная функция check_battles.
    @detail Функция проверки бедет ли контакт с монстром при координате игрока, сооттветствующей pos.
        @param pos - обеъект класса Position.
        @param monster - объект класса Monster.
"""
def is_contact(pos: Position, monster: Monster):
    return is_gv_neighbor(pos, monster.position)

"""!
    @brief Функция поиска монстров, которые могут и ударят игрока.
    @detail Учитываются только живые монстры, находящиеся на расстоянии удара. Все монстры, кроме мимика
    бьют только по горизонтали или вертикали.
        @param player объект класса Player.
        @param level объект класса Level.
    @return массив монстров, которые находятся на расстоянии удара по игроку
"""
def find_nearest_monsters(player: Player, level: Level):
    monsters = []
    for room in level.rooms:
        #if room.is_visited:
        for monster in room.monsters:
            if monster.type == MonsterType.MIMIC:
                if monster.is_alive and is_neighbor(monster.position, player.position):
                    monsters.append(monster)
                    monster.is_activated = True

            elif monster.is_alive and is_gv_neighbor(monster.position, player.position):
                monsters.append(monster)

    return monsters

"""!
    @brief Вспомогательная функция check_player_attack и check_battles.
    @detail Возвращает ссылку на монстра, если битва с его участием уже есть в battle_picture, в противном случае
    возвращается None.
        @param monster объект класса Monster;
        @param battle_picture объект класса BattlePicture.
    @return Monster/None.
"""
def get_battle(monster: Monster, battle_picture: BattlePicture):
    obj = None
    for b in battle_picture.battles:
        if b.monster == monster:
            return b
    return obj


"""!
    @brief Функция проверки атаки игрока.
    @detail Проверяем список битв, которые есть и возвращаем активную, если ее еще нет, то создаем.
        @param player объект класса Player; 
        @param direct - выбранное направление движения; 
        @param battle_picture объект класса BattlePicture; 
        @param nearest_monsters - список монстров, которые приблизились на расстоянии удара;
        @param pos_copy объекь класса Position, вводится, чтобы не плодить лишние объекты, анимающие резурсы компа;
    @return True/False, current_battle/None.
"""
def check_player_attack(player: Player, direct: Directions, battle_picture: BattlePicture, level: Level,
                        pos_copy: Position):

    from .character_move import move_character_by_direction

    pos_copy.change_position(player.position.x, player.position.y, player.position.dx, player.position.dy)
    move_character_by_direction(direct, pos_copy)

    # обновляем список монстров, которых можно атаковать, прямо перед атакой
    for room in level.rooms:
        for m in room.monsters:
            if m.is_alive and is_equal_x_y(pos_copy, m.position):
                cur_battle = get_battle(m, battle_picture)
                if cur_battle is None:
                    cur_battle = Battle(m, True) #будет атаковать на следующем ходе, они не убегают
                    battle_picture.add_battle(cur_battle)
                return True, cur_battle

    return False, None

"""!
    @brief Функция обновления битв.
    @detail Если разорвана дистанция с вампиром, то у него обновляется щит. Статус is_active - означает,
        что монстр может быть включен в список атакующих монстров.
    @param player объект класса Player; 
    @param battle_picture объект BattlePicture;  
    @param nearest_monsters - массив монстров, которые смогут и будут атаковать игрока на своем ходу.
"""
def check_battles(battle_picture: BattlePicture,  nearest_monsters):

    for monster in nearest_monsters:
        if get_battle(monster, battle_picture) is None:
            battle_picture.add_battle(Battle(monster, True))

    for battle in battle_picture.battles:
        if battle.monster.is_alive:
            if battle.monster in nearest_monsters:
                battle.is_attack = True
            else:
                # монстр далеко для атаки, и его считать в ударе не надо
                battle.is_attack = False
"""!
    @brief Описание процесса атаки.
    @detail Если gold = 0, значит был нанесен урон.
    @param player - объект класса Player;
    @param battle_picture объект класса BattlePicture;
    @param battle объект класса Battle; 
    @param turn - число типа int. 0 - ходит игрок, любое другое значение - ход монстра. Полезно для написания логов.
    @return [gold, damage, battle.monster.type]. Если gold > 0, то монстр был убит, если gold == -1, то был убит игрок,
        третим аргументом всегда возвращается тип монстра. Полезно для написания логов.
"""
def attack_procedure(player: Player, battle_picture: BattlePicture, battle: Battle, turn: int):
    result = []
    if turn == 0:
        #если в списке битв есть монсты, то игрок точно атакует, т.к объект туда добавляется при атаке игрока
        if battle is not None:
            gold, damage = calc_attack_result(player, battle.monster)
            result.append([gold, damage, battle.monster.type])

            if gold > 0:
                battle.is_finish = True
                battle.monster.is_alive = False
                battle_picture.del_battle(battle)
    else:
        if battle_picture.battles:
            for b in battle_picture.battles:
                if b.is_attack and not b.is_finish:
                    gold, damage = calc_attack_result(b.monster, player)
                    result.append([gold, damage, b.monster.type])
                    if gold == -1:
                        #игрока убили
                        player.is_alive = False
                        return result

    return result
"""!
    @brief Функция очистки
    @detail Удаляет убитых монстров из комнат, чтобы не делать лишнюю работу
"""
def remove_dead_monsters(level: Level):
    for room in level.rooms:
        # не иохраняем его для прорисовки трупов, это нам не надо
        room.monsters = [m for m in room.monsters if m.is_alive]

