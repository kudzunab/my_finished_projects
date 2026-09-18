"""
Модуль с маппингом клавиатуры.

Движение (WASD → изменение координат):
  W (MOVE_UP)    → y -= 1  (вверх)
  S (MOVE_DOWN)  → y += 1  (вниз)
  A (MOVE_LEFT)  → x -= 1  (влево)
  D (MOVE_RIGHT) → x += 1  (вправо)
"""

QUIT = "QUIT"
MOVE_UP = "MOVE_UP"
MOVE_DOWN = "MOVE_DOWN"
MOVE_LEFT = "MOVE_LEFT"
MOVE_RIGHT = "MOVE_RIGHT"
NOOP = "NOOP"
INVENTORY = "INVENTORY"
USE_WEAPON = "USE_WEAPON"
USE_FOOD = "USE_FOOD"
USE_ELIXIR = "USE_ELIXIR"
USE_SCROLL = "USE_SCROLL"
SELECT_ITEM_0 = "SELECT_ITEM_0"
SELECT_ITEM_1 = "SELECT_ITEM_1"
SELECT_ITEM_2 = "SELECT_ITEM_2"
SELECT_ITEM_3 = "SELECT_ITEM_3"
SELECT_ITEM_4 = "SELECT_ITEM_4"
SELECT_ITEM_5 = "SELECT_ITEM_5"
SELECT_ITEM_6 = "SELECT_ITEM_6"
SELECT_ITEM_7 = "SELECT_ITEM_7"
SELECT_ITEM_8 = "SELECT_ITEM_8"
SELECT_ITEM_9 = "SELECT_ITEM_9"
SAVE_GAME = "SAVE_GAME"

KEY_TO_ACTION = {
    ord("q"): QUIT,
    ord("Q"): QUIT,

    ord("w"): MOVE_UP,
    ord("W"): MOVE_UP,
    ord("s"): MOVE_DOWN,
    ord("S"): MOVE_DOWN,
    ord("a"): MOVE_LEFT,
    ord("A"): MOVE_LEFT,
    ord("d"): MOVE_RIGHT,
    ord("D"): MOVE_RIGHT,
    ord("i"): INVENTORY,
    ord("I"): INVENTORY,
    ord("h"): USE_WEAPON,
    ord("H"): USE_WEAPON,
    ord("j"): USE_FOOD,
    ord("J"): USE_FOOD,
    ord("k"): USE_ELIXIR,
    ord("K"): USE_ELIXIR,
    ord("e"): USE_SCROLL,
    ord("E"): USE_SCROLL,
    ord('0'): SELECT_ITEM_0,
    ord('1'): SELECT_ITEM_1,
    ord('2'): SELECT_ITEM_2,
    ord('3'): SELECT_ITEM_3,
    ord('4'): SELECT_ITEM_4,
    ord('5'): SELECT_ITEM_5,
    ord('6'): SELECT_ITEM_6,
    ord('7'): SELECT_ITEM_7,
    ord('8'): SELECT_ITEM_8,
    ord('9'): SELECT_ITEM_9,
    ord("`"): SAVE_GAME,
    ord("~"): SAVE_GAME,
}
