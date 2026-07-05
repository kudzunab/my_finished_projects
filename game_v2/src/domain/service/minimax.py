from src.domain.model import Game, copy_game
from src.domain.service.rules import is_player_win, get_free_cells

def get_score(_game: Game, depth: int = 0):
    # проверка на выиграышь крестиков
    if is_player_win(0, _game) == 1:
        return 10 - depth

    # проверка на выигрыш ноликов
    if is_player_win(1, _game) == 1:
        return - 10 + depth

    # нет свободных клеток и поведителя, если уж
    # мы долшли сюда
    poss_turns = get_free_cells(_game)
    if len(poss_turns) == 0:
        return 0

    # нет конца игры и можно дальше продолжать уходить
    # в рекурсию.
    return None

def minimax(_game, smb_turn: int, depth = 0):
    res = get_score(_game, depth)

    # это окончание игры
    if res is not None:
        return res

    free_cells = get_free_cells(_game)
    scores = [] # массив результатов по играм, из него
                # и будем выбирать лучший ход

    for _cell in free_cells:
        _game.field[_cell[0]][_cell[1]] = smb_turn
        score = minimax(_game, 1 - smb_turn, depth + 1)
        scores.append(score)
        #откат хода в реальном поле
        _game.field[_cell[0]][_cell[1]] = -1

    if smb_turn == 0:
        return max(scores)
    else:
        return min(scores)

def get_best_turn(_game: Game, whom_turn: int):

    best_score = -100 if whom_turn == 0 else 100
    best_turn = None

    c_game = copy_game(_game)
    for _cell in get_free_cells(c_game):
        c_game.field[_cell[0]][_cell[1]] = whom_turn
        score = minimax(c_game, 1 - whom_turn, depth = 1)
        c_game.field[_cell[0]][_cell[1]] = -1

        if (whom_turn == 0 and score > best_score) or \
                (whom_turn == 1 and score < best_score):
                best_score = score
                best_turn = _cell

    return best_turn

if __name__ == "__main__":
    from src.domain.service.rules import  check_correct_game_state
    game = Game()
    for _ in range(4):
        cell = get_best_turn(game, game.turn)
        print(f"компьютер выбрал поле {cell}")
        game.field[cell[0]][cell[1]] = 0
        game.turn = 1 - game.turn
        game.copy_to_snapshot()

        cell = get_best_turn(game, game.turn)
        game.field[cell[0]][cell[1]] = 1
        print(f"компьютер выбрал поле {cell}")
        game.turn = 1 - game.turn
        game.copy_to_snapshot()

    cell = get_best_turn(game, 0)
    print(f"компьютер выбрал поле {cell}")

    ress = check_correct_game_state(game)
    print(f"В матрице все нормально? Ответ {ress}")

    game.field[cell[0]][cell[1]] = 0
    print("This is the file test")

    ress = check_correct_game_state(game)
    print(f"В матрице все нормально? Ответ {ress}")
