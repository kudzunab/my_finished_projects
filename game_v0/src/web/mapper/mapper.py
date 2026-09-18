from src.domain.model import Game, GameError, GameStatus
from src.domain.service.game_manager import GameManager
from src.web.model import BrowserGame

def get_text_message(code) -> str:

    if code == "" or code is None:
        return "Игра началась!"

    if isinstance(code, str):
        return code
    my_dict = {
        GameError.ERROR_STATE_CHECK : "Ай-ай, не корректное состояние поля из-за вмешательства в данные!!!",
        GameError.ERROR_INPUT_TYPE: "Хакерам тут не рады! Не надо ломать код!",
        GameError.ERROR_VALUE: "Гмм... А ход-то не корректный, за гранью понимания AI",
        GameError.OCCUPIED_CELL: "Эта клетка уже занята, выберите другую",

        GameStatus.cross_win: "Поздравляю, вы победили! (Крестики)",
        GameStatus.nulls_win: "ИИ победил! (Нолики)",
        GameStatus.nobody_win: "Боевая ничья",

        GameStatus.ongoing: "Компьютер сделал ход. Теперь ваша очередь!",
        GameStatus.ongoing_nulls: "Крестики сделали свой ход",  # Используем уникальные ключи для ходов
        GameStatus.ongoing_cross: "Нолики сделали свой ход",

        GameError.INVALID_FORMAT: "Поле не того формата",
        GameError.NO_MOVE_MADE: "Вы не сделали ход"
    }
    message = my_dict.get(code)
    if message:
        return message

    return f"Неизвестный статус (код {code})"

def from_game_to_browser_game(source: Game, target: BrowserGame, status_code):

    target.uuid = str(source.UUID) # оно и так не число, но подстраховались
    for  i in range(3):
        for j in range(3):
            target.field[i][j] = source.field[i][j]

    target.message = get_text_message(status_code)

def from_browser_game_to_game(source: BrowserGame, target: Game):
    for  i in range(3):
        for j in range(3):
            target.field[i][j] = source.field[i][j]

def web_turn_synch(manager: GameManager, web_model: BrowserGame):
    try:
        from_browser_game_to_game(web_model, manager.game)
        is_success, status_code = manager.make_turn()
    except (TypeError, IndexError):
        manager.game.restore_field()
        is_success, status_code = False, GameError.INVALID_FORMAT

    from_game_to_browser_game(manager.game, web_model, status_code)

    return is_success