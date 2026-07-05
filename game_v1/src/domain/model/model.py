import uuid, copy
from enum import Enum

class JoinResult(Enum):
    SUCCESS = "Вы успешно присоединились к игре, ждите хода первого игрока"
    GAME_NOT_FOUND = "Такой игры не существует"
    ALREADY_IN_GAME = "Вы уже играете/закончили эту партию"
    PLAYING_WITH_SELF = "Вы не можете играть сам с собой"
    GAME_FULL = "Эта партия уже занята"

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

    NOT_YOUR_TURN = -3 


class Status(Enum):
    waiting_players = 0
    turn_player_with_UUID = 1
    nobody_wins = 2
    win_player_with_UUID = 3

computer_uuid="00000000-0000-0000-0000-000000000001"
none_uuid="00000000-0000-0000-0000-000000000000"
def generate_uuid():
    new_uuid = None
    while new_uuid in {computer_uuid, none_uuid, None}:
        new_uuid=str(uuid.uuid4())

    return new_uuid


class PlayerSymbol(Enum):
    cross = "x"
    nulls = "o"

class GameType(int, Enum):
    with_computer = 0
    with_player = 1

def create_field():
    return [[-1 for _ in range(3)] for _ in range(3)]

class Game:

    def __init__(self, game_id = None, field = None, turn = 0, game_type=None, player1_uuid=none_uuid,
                 player2_uuid=none_uuid, current_player_uuid=none_uuid,
                 player1_symbol=None, player2_symbol=None, status=None):

        self.UUID = game_id if game_id else generate_uuid()
        self.field = field if field is not None else create_field()
        self.turn = turn
        self.game_type=game_type
        self.current_player_uuid = current_player_uuid
        self.player1_uuid = player1_uuid
        self.player2_uuid = player2_uuid
        self.player1_symbol = player1_symbol
        self.player2_symbol = player2_symbol
        self.status = status
        self.snapshot = copy.deepcopy(field) if field is not None else create_field()

    def change_field(self, mass, turn):
        try:
            if not isinstance(mass, (list, tuple)) or len(mass) != 2:
                return GameError.ERROR_INPUT_TYPE

            # здесь проверяем на ошибки
            if mass[0] not in [0, 1, 2] or mass[1] not in [0, 1, 2]:
                return GameError.ERROR_VALUE

            # здесь пытаемся полу занятое поменять
            if self.field[mass[0]][mass[1]] != -1:
                return GameError.OCCUPIED_CELL

            self.field[mass[0]][mass[1]] = turn
            # копируем ход туда, где мы не сможем ничего поменять
            self.snapshot[mass[0]][mass[1]] = turn
            # переключаем ход на другого игрока
            self.turn = 1 - turn

            # возвращаем в случае успешной операции 1
            return GameError.GOOD_TURN
        except (IndexError, TypeError):
            return GameError.ERROR_VALUE

    # добавляю метод, который сам будет восстанавливать свои поля
    # если пользователь повредил данные
    def restore_field(self):
        self.field = copy.deepcopy(self.snapshot)

    def copy_to_snapshot(self):
        self.snapshot = copy.deepcopy(self.field)

def copy_game(game: Game):

    new_game = Game(game_id=game.UUID, turn=game.turn, status=game.status, game_type=game.game_type)
    new_game.field = copy.deepcopy(game.field)
    new_game.snapshot = copy.deepcopy(game.snapshot)

    return new_game


if __name__ == "__main__":
    print("This is the file test")