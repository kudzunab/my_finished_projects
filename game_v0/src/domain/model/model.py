import uuid
from enum import Enum

class GameError(Enum):
    # состояние поля некорректно, поэтому с сам запрос нет смысла рассматривать
    ERROR_STATE_CHECK = -10
    # состояние поля корректно, но ввели в поле ввода какую-то гадость
    ERROR_INPUT_TYPE = -9
    # состояние поля корректно, ввели число, но  оно не в рабочем диапазоне
    ERROR_VALUE = -8
    # все соответствует, но клетка уже занята
    OCCUPIED_CELL = -7
    # здесь добавлена проверка ошибки странного размера
    INVALID_FORMAT = -6
    # не сделано хода
    NO_MOVE_MADE = -5
    # все соответствует и нет ошибок
    GOOD_TURN = 0

class GameStatus(Enum):
    cross_win = 0
    nulls_win = 1
    nobody_win = 2
    ongoing = -1
    ongoing_cross = 100
    ongoing_nulls = 101

def create_field():
    return [[-1 for _ in range(3)] for _ in range(3)]

class Game:

    def __init__(self, game_id = None, field = None, turn = 0):

        self.UUID = game_id if game_id else str(uuid.uuid4())
        self.field = field if field is not None else create_field()
        self.turn = turn
        self.snapshot = create_field()

        if field is not None:
            for i in range(3):
                for j in range(3):
                    self.snapshot[i][j] = field[i][j]


    def change_field(self, mass, turn):
        try:
            if not isinstance(mass, (list, tuple)) or len(mass) != 2:
                return GameError.ERROR_INPUT_TYPE

            if mass[0] not in [0, 1, 2] or mass[1] not in [0, 1, 2]:
                return GameError.ERROR_VALUE

            if self.field[mass[0]][mass[1]] != -1:
                return GameError.OCCUPIED_CELL

            self.field[mass[0]][mass[1]] = turn
            self.snapshot[mass[0]][mass[1]] = turn
            self.turn = 1 - turn

            return GameError.GOOD_TURN
        except (IndexError, TypeError):
            return GameError.ERROR_VALUE

    def restore_field(self):
        for i in range(3):
            for j in range(3):
                self.field[i][j] = self.snapshot[i][j]

    def copy_to_snapshot(self):
        for i in range(3):
            for j in range(3):
                self.snapshot[i][j] = self.field[i][j]

def copy_game(game: Game):

    new_game = Game(game_id=game.UUID, turn=game.turn)
    for i in range(3):
        for j in range(3):
            new_game.field[i][j] = game.field[i][j]
    return new_game

if __name__ == "__main__":
    print("This is the file test")

