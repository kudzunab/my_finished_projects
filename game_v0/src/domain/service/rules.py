from src.domain.model import Game
from src.domain.model.model import GameStatus

"""
    @brief Функция проверки выигрыша на указанном ходе в данной игре
"""
def is_player_win(turn: int, _game: Game):
    if turn not in [0, 1]:
        return -1

    m = _game.field
    for i in range(3):
        if (m[0][i] == m[1][i] == m[2][i] == turn) or \
                (m[i][0] == m[i][1] == m[i][2] == turn):
            return 1

    if m[1][1] == turn:
        if m[0][0] == m[2][2] == turn or m[2][0] == m[0][2] == turn:
            return 1

    return 0

"""
    @brief Поиск сободных клеток, куда можно сходить
"""
def get_free_cells(_game: Game):
    result = []
    m = _game.field
    for  i in range(3):
        for j in range(3):
            if m[i][j] == -1:
                result.append([i, j])

    return result

"""
    @brief Проверка окончания игры
"""
def check_game_finish(_game: Game):
    if is_player_win(0, _game) == 1:
        return GameStatus.cross_win
    if is_player_win(1, _game) == 1:
        return GameStatus.nulls_win

    free_cells = get_free_cells(_game)

    if not free_cells:
        return GameStatus.nobody_win

    return GameStatus.ongoing

"""
    @brief Функция проверки состояния игрового поля
"""
def check_correct_game_state(_game: Game):
    if _game is None or _game.turn not in [0, 1]:
        return False

    diff_count = 0
    for i in range(3):
        for j in range(3):
            if _game.snapshot[i][j] != -1:
                if _game.field[i][j] != _game.snapshot[i][j]:
                    return False

            if _game.snapshot[i][j] == -1 and _game.field[i][j] != -1:
                diff_count += 1
                if _game.field[i][j] != _game.turn:
                    return False
    if diff_count > 1:
        return False

    cross_num, null_num = 0, 0
    for i in range(3):
        for j in range(3):

            if _game.field[i][j] not in [-1, 0, 1]:
                return False

            if _game.field[i][j] == 0:
                cross_num += 1
            elif _game.field[i][j] == 1:
                null_num += 1

    if _game.turn == 0:
        if not (cross_num == null_num or cross_num == null_num + 1):
            return False

    elif _game.turn == 1:
        if null_num != cross_num:
            return False


    cross_win = is_player_win(0, _game)
    null_win = is_player_win(1, _game)

    if cross_win == 1 and null_win == 1:
        return False

    if (cross_win == 1 and cross_num != null_num + 1) \
            or (null_win == 1 and cross_num != null_num):
        return False

    return True
