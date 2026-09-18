from src.dto.enums import GameAction, Direction

_KEY_MAP: dict[int, GameAction] = {
    ord('w'): GameAction.MOVE_UP,
    ord('W'): GameAction.MOVE_UP,
    ord('a'): GameAction.MOVE_LEFT,
    ord('A'): GameAction.MOVE_LEFT,
    ord('s'): GameAction.MOVE_DOWN,
    ord('S'): GameAction.MOVE_DOWN,
    ord('d'): GameAction.MOVE_RIGHT,
    ord('D'): GameAction.MOVE_RIGHT,
    ord('h'): GameAction.USE_WEAPON,
    ord('H'): GameAction.USE_WEAPON,
    ord('j'): GameAction.USE_FOOD,
    ord('J'): GameAction.USE_FOOD,
    ord('k'): GameAction.USE_ELIXIR,
    ord('K'): GameAction.USE_ELIXIR,
    ord('e'): GameAction.USE_SCROLL,
    ord('E'): GameAction.USE_SCROLL,
    27: GameAction.ESCAPE,
    10: GameAction.MENU_CONFIRM,
    ord('0'): GameAction.SELECT_ITEM_0, #зачем тебе 0?
    ord('1'): GameAction.SELECT_ITEM_1,
    ord('2'): GameAction.SELECT_ITEM_2,
    ord('3'): GameAction.SELECT_ITEM_3,
    ord('4'): GameAction.SELECT_ITEM_4,
    ord('5'): GameAction.SELECT_ITEM_5,
    ord('6'): GameAction.SELECT_ITEM_6,
    ord('7'): GameAction.SELECT_ITEM_7,
    ord('8'): GameAction.SELECT_ITEM_8,
    ord('9'): GameAction.SELECT_ITEM_9,
}

ACTION_TO_DIRECTION: dict[GameAction, Direction] = {
    GameAction.MOVE_UP: Direction.FORWARD,
    GameAction.MOVE_DOWN: Direction.BACK,
    GameAction.MOVE_LEFT: Direction.LEFT,
    GameAction.MOVE_RIGHT: Direction.RIGHT,
}


def map_key_to_action(key: int) -> GameAction:
    return _KEY_MAP.get(key, GameAction.NONE)
