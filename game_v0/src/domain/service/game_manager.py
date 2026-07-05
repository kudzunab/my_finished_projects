from src.domain.service.step_by_step_game import StepByStepGame
from src.domain.model import Game
from src.domain.model.model import GameError, GameStatus

class GameManager:

    def __init__(self, ai_service: StepByStepGame, this_game: Game):
        self.ai = ai_service
        self.game = this_game

    def make_turn(self):
        _game = self.game

        game_status = self.ai.check_game_finish(_game)
        if game_status != GameStatus.ongoing:
            if _game.field == _game.snapshot:
                return True, game_status

        check_status = self.ai.check_correct_game_state(_game)
        if not check_status:
            self.game.restore_field()
            return False, GameError.ERROR_STATE_CHECK

        if _game.field == _game.snapshot:
            return False, GameError.NO_MOVE_MADE

        _game.copy_to_snapshot()

        check_the_end = self.ai.check_game_finish(_game)
        if check_the_end == GameStatus.ongoing:
            _game.turn = 1 -_game.turn

            coord = self.ai.get_best_turn(_game, _game.turn)
            _game.change_field(coord, _game.turn)
            _game.copy_to_snapshot()
            check_the_end = self.ai.check_game_finish(_game)

        return True, check_the_end

if __name__ == "__main__":
    my_dict = {
        GameError.ERROR_STATE_CHECK : "Ай-ай, не корректное состояние поля из-за вмешательства в данные!!!",
        GameError.ERROR_INPUT_TYPE: "Хакерам тут не рады! Не надо ломать код!",
        GameError.ERROR_VALUE: "Гмм... А ход-то не корректный, за гранью понимания AI",
        GameError.OCCUPIED_CELL: "Эта клетка уже занята, выберите другую",
        -1: "Неправильные координаты хода",
        GameStatus.cross_win: "Крестики выиграли",
        GameStatus.nulls_win: "Нолики выиграли",
        GameStatus.nobody_win: "Боевая ничья",
        3: "Игра окончена",
        GameStatus.ongoing: "Ваш ход",
        GameStatus.ongoing_nulls: "Крестики сделали свой ход",
        GameStatus.ongoing_cross: "Нолики сделали свой ход"

    }
    game = Game()

    my_ai_service = StepByStepGame()

    game_manager = GameManager(my_ai_service, game)

    _, res = game_manager.make_turn()
    print(f"Тест без хода: {res}")

    game.field[0][0] = 0
    _, res = game_manager.make_turn()
    print(f"После хода игрока и ИИ: {my_dict.get(res, res)}")

    game.field[1][1] = 0
    game.field[1][2] = 0
    _, res = game_manager.make_turn()
    print(f"Тест взлома (2 хода): {my_dict.get(res, res)}")

    game.restore_field()
    game.field[0][0] = -1
    _, res = game_manager.make_turn()
    print(f"Тест взлома (удаление): {my_dict.get(res, res)}")

    game.field[0][0] = 1
    success, res = game_manager.make_turn()

    if not success and res == GameError.ERROR_STATE_CHECK:
        print(f"Тест на занятую клетку ПРОЙДЕН: {my_dict[res]}")
    else:
        print(f"Тест ПРОВАЛЕН: статус {res}")

    if game.field[0][0] == 0:
        print("Откат данных выполнен верно (клетка [0][0] снова содержит 0)")

    print("Тест завершен")
