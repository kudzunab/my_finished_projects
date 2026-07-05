from src.domain.model import Game
from src.domain.model.model import Status #, GameStatus

"""
    @brief Функция проверки выигрыша на указанном ходе в данной игре
"""
def is_player_win(turn: int, _game: Game):
    if turn not in [0, 1]:
        return -1

    # проверяем наличие трех нулей или крестиков
    # 0 - крестик в данной клетке, 1 - нолик в указанной клетке
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
    # проверяем на выигрыщш кого-либо из участников
    if is_player_win(0, _game) == 1:
        return Status.win_player_with_UUID #GameStatus.cross_win
    if is_player_win(1, _game) == 1:
        return Status.win_player_with_UUID #GameStatus.nulls_win

    # проверяем на наличие пустых клеток на поле игры
    free_cells = get_free_cells(_game)

    # нет полей для дальнейшей игры
    if not free_cells:
        return Status.nobody_wins #GameStatus.nobody_win

    # если дошли сюда, значит игра продолжается - есть клетки для хода и нет выигрывших
    return Status.turn_player_with_UUID #GameStatus.ongoing

"""
    @brief Функция проверки состояния игрового поля
"""
def check_correct_game_state(_game: Game):
    if _game is None or _game.turn not in [0, 1]:
        print("ВЫЛЕТ: неверный ход или пустая игра")
        return False

    diff_count = 0
    for i in range(3):
        for j in range(3):
            # сверяет прошлое и пришедшим на предмет изменений
            # по заполненным полям
            if _game.snapshot[i][j] != -1:
                if _game.field[i][j] != _game.snapshot[i][j]:
                    print(f"ВЫЛЕТ: изменилась старая клетка [{i}][{j}]")
                    return False

            # клетка была пустой но ее заняли
            if _game.snapshot[i][j] == -1 and _game.field[i][j] != -1:
                diff_count += 1
                # если поставили не тот символ на ходе
                if _game.field[i][j] != _game.turn:
                    print(f"ВЫЛЕТ: не тот символ в новой клетке. Ждали {_game.turn}, пришло {_game.field[i][j]}")
                    return False
    if diff_count > 1:
        print("ВЫЛЕТ: сделано больше одного хода за раз!")
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


#    # после ода крестиков их на один больше
#    if _game.turn == 0:
#        if not (cross_num == null_num or cross_num == null_num + 1):
#            return False

#    # после хода ноликов их столько же, сколько и крестиков
#    elif _game.turn == 1:
#        if null_num != cross_num:
#            return False
    if not (cross_num == null_num or cross_num == null_num + 1):
        return False

    cross_win = is_player_win(0, _game)
    null_win = is_player_win(1, _game)

    if cross_win == 1 and null_win == 1:
        return False

    if (cross_win == 1 and cross_num != null_num + 1) \
            or (null_win == 1 and cross_num != null_num):
        return False

    return True
