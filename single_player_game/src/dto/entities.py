from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.dto.enums import HostilityLevel, StatType, Direction
#===============================================
#=============взяла из своего файла=============
#===============================================
from src.domain.entities import MonsterType

# === Геометрия ===

@dataclass
class Position:
    x: int = 0
    y: int = 0


@dataclass
class Size:
    w: int = 1
    h: int = 1


@dataclass
class Rect:
    pos: Position = field(default_factory=Position)
    size: Size = field(default_factory=lambda: Size(1, 1))


# === Предметы ===

@dataclass
class Treasure:
    value: int = 0


@dataclass
class Food:
    to_regen: int = 0
    name: str = ""


@dataclass
class Elixir:
    duration: int = 0
    stat: StatType = StatType.HEALTH
    increase: int = 0
    name: str = ""


@dataclass
class Scroll:
    stat: StatType = StatType.HEALTH
    increase: int = 0
    name: str = ""


@dataclass
class Weapon:
    strength: int = 0
    name: str = ""


# === Предметы в комнате ===

@dataclass
class RoomFood:
    food: Food = field(default_factory=Food)
    geometry: Rect = field(default_factory=Rect)


@dataclass
class RoomElixir:
    elixir: Elixir = field(default_factory=Elixir)
    geometry: Rect = field(default_factory=Rect)


@dataclass
class RoomScroll:
    scroll: Scroll = field(default_factory=Scroll)
    geometry: Rect = field(default_factory=Rect)


@dataclass
class RoomWeapon:
    weapon: Weapon = field(default_factory=Weapon)
    geometry: Rect = field(default_factory=Rect)


@dataclass
class RoomConsumables:
    foods: list[RoomFood] = field(default_factory=list)
    elixirs: list[RoomElixir] = field(default_factory=list)
    scrolls: list[RoomScroll] = field(default_factory=list)
    weapons: list[RoomWeapon] = field(default_factory=list)


# === Персонажи ===

@dataclass
class CharacterStats:
    coords: Rect = field(default_factory=Rect)
    health: float = 0.0
    agility: int = 0
    strength: int = 0


@dataclass
class Monster:
    base_stats: CharacterStats = field(default_factory=CharacterStats)
    type: MonsterType = MonsterType.ZOMBIE
    hostility: HostilityLevel = HostilityLevel.LOW
    is_chasing: bool = False
    direction: Direction = Direction.STOP


# === Система баффов ===

@dataclass
class Buff:
    stat_increase: int = 0
    effect_end: int = 0


@dataclass
class ActiveBuffs:
    health_buffs: list[Buff] = field(default_factory=list)
    agility_buffs: list[Buff] = field(default_factory=list)
    strength_buffs: list[Buff] = field(default_factory=list)


# === Рюкзак ===

MAX_ITEMS_PER_TYPE: int = 9


@dataclass
class Backpack:
    foods: list[Food] = field(default_factory=list)
    elixirs: list[Elixir] = field(default_factory=list)
    scrolls: list[Scroll] = field(default_factory=list)
    weapons: list[Weapon] = field(default_factory=list)
    treasures: Treasure = field(default_factory=Treasure)


# === Игрок ===

@dataclass
class Player:
    base_stats: CharacterStats = field(default_factory=CharacterStats)
    max_health: int = 500
    backpack: Backpack = field(default_factory=Backpack)
    weapon: Weapon = field(default_factory=Weapon)
    buffs: ActiveBuffs = field(default_factory=ActiveBuffs)


# === Комната и уровень ===

@dataclass
class Room:
    coords: Rect = field(default_factory=Rect)
    consumables: RoomConsumables = field(default_factory=RoomConsumables)
    monsters: list[Monster] = field(default_factory=list)


@dataclass
class Passage:
    pos: Position = field(default_factory=Position)
    size: Size = field(default_factory=Size)


ROOMS_NUM: int = 9


@dataclass
class Level:
    coords: Rect = field(default_factory=Rect)
    rooms: list[Room] = field(default_factory=list)
    passages: list[Passage] = field(default_factory=list)
    level_num: int = 0
    exit_pos: Rect = field(default_factory=Rect)


# === Состояние боя ===

@dataclass
class BattleInfo:
    is_fight: bool = False
    enemy: Optional[Monster] = None
    vampire_first_attack: bool = True
    ogre_cooldown: bool = False
    player_asleep: bool = False


# === Туман войны ===

@dataclass
class MapVisibility:
    visible_rooms: list[bool] = field(default_factory=lambda: [False] * ROOMS_NUM)
    visible_passages: list[bool] = field(default_factory=list)


# === Статистика ===

@dataclass
class SessionStats:
    treasures: int = 0
    level: int = 0
    enemies_killed: int = 0
    food_eaten: int = 0
    elixirs_drunk: int = 0
    scrolls_read: int = 0
    attacks_given: int = 0
    hits_taken: int = 0
    tiles_walked: int = 0


# === Полное состояние игры (для сохранения/загрузки) ===

@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    level: Level = field(default_factory=Level)
    visibility: MapVisibility = field(default_factory=MapVisibility)
    battles: list[BattleInfo] = field(default_factory=list)
    stats: SessionStats = field(default_factory=SessionStats)


# === События ===

@dataclass
class UseItemResult:
    success: bool = False
    message: str = ""
