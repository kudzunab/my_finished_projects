from src.domain.service.step_by_step_game import StepByStepGame
from src.domain.model import Game
from src.domain.model.model import GameError, Status,computer_uuid #, none_uuid, GameStatus,
import copy

class GameManager:

    def __init__(self, ai_service: StepByStepGame, this_game: Game):
        self.ai = ai_service # один раз создали и используем, здесь набор нужных методов
        self.game = this_game

    # на основании номера клетки мы сможем работать
    def make_turn(self, player_uuid: str):
        if self.game.status in [Status.win_player_with_UUID, Status.nobody_wins]:
            self.game.restore_field()
            return True, self.game.status

        current_field = self.game.field
        self.game.field = copy.deepcopy(self.game.snapshot)
        is_finished = self.ai.check_game_finish(self.game)
        self.game.field = current_field

        if is_finished in [Status.win_player_with_UUID, Status.nobody_wins]:
            self.game.restore_field()
            return True, is_finished

        if player_uuid != self.game.current_player_uuid:
            self.game.restore_field()
            return False, GameError.NOT_YOUR_TURN

        check_status = self.ai.check_correct_game_state(self.game)
        if not check_status:
            self.game.restore_field()
            return False, GameError.ERROR_STATE_CHECK

        if self.game.field == self.game.snapshot:
            return False, GameError.NO_MOVE_MADE

        self.game.copy_to_snapshot() # если все нормально, то скопировали ход игрока

        check_the_end = self.ai.check_game_finish(self.game)
        self.game.status = check_the_end
        if check_the_end in [Status.win_player_with_UUID, Status.nobody_wins]:
            return True, check_the_end

        if self.game.current_player_uuid == self.game.player1_uuid:
            self.game.current_player_uuid = self.game.player2_uuid
            self.game.turn = 1
        else:
            self.game.current_player_uuid = self.game.player1_uuid
            self.game.turn = 0

        if self.game.current_player_uuid == computer_uuid and check_the_end == Status.turn_player_with_UUID: # GameStatus.ongoing:

            coord = self.ai.get_best_turn(self.game, self.game.turn)
            self.game.change_field(coord, self.game.turn)
            self.game.copy_to_snapshot()
            check_the_end = self.ai.check_game_finish(self.game)
            self.game.status = check_the_end
            if check_the_end not in [Status.win_player_with_UUID, Status.nobody_wins]:
                self.game.current_player_uuid = self.game.player1_uuid

        return True,  check_the_end

if __name__ == "__main__":
    print("Так уже не проверить")
    """
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
        GameStatus.ongoing_nulls: "Крестики сделали свой ход",  # Используем уникальные ключи для ходов
        GameStatus.ongoing_cross: "Нолики сделали свой ход"

    }
    # создали экземпляр игры
    game = Game()

    # создали экземпляр класса -оболочки для игровых функций
    my_ai_service = StepByStepGame()

    # cоздали менеджер игры
    game_manager = GameManager(my_ai_service, game)

    # Попытка взлома(пустое поле, ход не сделан)
    _, res = game_manager.make_turn()
    print(f"Тест без хода: {res}")

    #Корректный ход игрока
    game.field[0][0] = 0  # Игрок поставил крестик в [0,0]
    _, res = game_manager.make_turn()
    print(f"После хода игрока и ИИ: {my_dict.get(res, res)}")

    #Попытка взлома (поставили сразу два крестика)
    game.field[1][1] = 0
    game.field[1][2] = 0  # Второй лишний символ
    _, res = game_manager.make_turn()
    print(f"Тест взлома (2 хода): {my_dict.get(res, res)}")

    #Попытка изменить чужой  символ
    game.restore_field()  # Откатываем к стабильному состоянию
    game.field[0][0] = -1
    _, res = game_manager.make_turn()
    print(f"Тест взлома (удаление): {my_dict.get(res, res)}")

    #Попытка сходить в занятую клетку [0][0]
    game.field[0][0] = 1
    success, res = game_manager.make_turn()

    if not success and res == GameError.ERROR_STATE_CHECK:
        print(f"Тест на занятую клетку ПРОЙДЕН: {my_dict[res]}")
    else:
        print(f"Тест ПРОВАЛЕН: статус {res}")

    # Проверка отката: поле должно снова стать таким, каким было после первого хода
    if game.field[0][0] == 0:
        print("Откат данных выполнен верно (клетка [0][0] снова содержит 0)")

    print("Тест завершен")
"""