from src.domain.model import Game, GameError, Status
from src.domain.service.game_manager import GameManager
from src.web.model import BrowserGame

def from_game_to_browser_game(source: Game, target: BrowserGame, status_code):
    target.uuid = str(source.UUID)  # оно и так не число, но подстраховались
    target.current_player_uuid = source.current_player_uuid
    target.current_turn = source.turn
    for i in range(3):
        for j in range(3):
            target.field[i][j] = source.field[i][j]

def from_browser_game_to_game(source: BrowserGame, target: Game):
    for i in range(3):
        for j in range(3):
            target.field[i][j] = source.field[i][j]


def web_turn_synch(manager: GameManager, web_model: BrowserGame, player_uuid: str):
    try:
        from_browser_game_to_game(web_model, manager.game)
        is_success, status_code = manager.make_turn(player_uuid)

    except (TypeError, IndexError):
        import traceback
        traceback.print_exc()
        manager.game.restore_field()
        is_success, status_code = False, GameError.INVALID_FORMAT

    from_game_to_browser_game(manager.game, web_model, status_code)

    return web_model, status_code

"""

def get_text_message(code) -> str:
    if code == "" or code is None:
        return "Игра началась!"

    if isinstance(code, str):
        return code

    if isinstance(code, GameError):
        error_dict = {
            GameError.ERROR_STATE_CHECK: "Ай-ай, не корректное состояние поля из-за вмешательства в данные!!!",
            GameError.ERROR_INPUT_TYPE: "Хакерам тут не рады! Не надо ломать код!",
            GameError.ERROR_VALUE: "Гмм... А ход-то не корректный, за гранью понимания AI",
            GameError.OCCUPIED_CELL: "Эта клетка уже занята, выберите другую",
            GameError.INVALID_FORMAT: "Поле не того формата",
            GameError.NO_MOVE_MADE: "Вы не сделали ход",
            GameError.NOT_YOUR_TURN: "Сейчас не ваш ход! Подождите соперника.",
            GameError.GOOD_TURN: "Ход успешно зафиксирован движком."
        }
        return error_dict.get(code, f"Ошибка игры ({code.name})")

    if isinstance(code, Status):
        status_dict = {
            Status.win_player_with_UUID: "Игра окончена! Победитель определён.",
            Status.nobody_wins: "Боевая ничья! Свободных клеток не осталось.",
            Status.turn_player_with_UUID: "Ход успешно выполнен. Ход следующего игрока"
        }
        return status_dict.get(code, f"Статус игры ({code.name})")

    return f"Неизвестный статус (код {code})"

"""