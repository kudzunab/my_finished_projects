from enum import IntEnum, auto


class Direction(IntEnum):
    FORWARD = 0
    BACK = 1
    LEFT = 2
    RIGHT = 3
    DIAG_FWD_LEFT = 4
    DIAG_FWD_RIGHT = 5
    DIAG_BACK_LEFT = 6
    DIAG_BACK_RIGHT = 7
    STOP = 8


class HostilityLevel(IntEnum):
    LOW = 0
    AVERAGE = 1
    HIGH = 2


class StatType(IntEnum):
    HEALTH = 0
    AGILITY = 1
    STRENGTH = 2
    HOSTILITY = 3
    NONE = -1


class ConsumableType(IntEnum):
    NONE = -1
    FOOD = 1
    ELIXIR = 2
    WEAPON = 3
    SCROLL = 4
    TREASURE = 5
    KEY = 6

class GameAction(IntEnum):
    SELECT_ITEM_0 = auto()
    SELECT_ITEM_1 = auto()
    SELECT_ITEM_2 = auto()
    SELECT_ITEM_3 = auto()
    SELECT_ITEM_4 = auto()
    SELECT_ITEM_5 = auto()
    SELECT_ITEM_6 = auto()
    SELECT_ITEM_7 = auto()
    SELECT_ITEM_8 = auto()

class GameScene(IntEnum):
    SPLASH = auto()
    MAIN_MENU = auto()
    GAME = auto()
    INVENTORY = auto()
    GAME_OVER_DEATH = auto()
    GAME_OVER_WIN = auto()
    LEADERBOARD = auto()
