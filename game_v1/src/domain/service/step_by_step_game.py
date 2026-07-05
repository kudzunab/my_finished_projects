from src.domain.model import Game
from src.domain.service import get_best_turn, check_correct_game_state, check_game_finish

# класс обертка, чтобы не лезть напрямую в логику, теперь нужные фунции доступны в качестве методов
# их не надо искать и импортировать больше, достаточно опираться на этот класс и все
class StepByStepGame:

    @staticmethod
    def get_best_turn(game: Game, turn):
        return get_best_turn(game, turn)

    @staticmethod
    def check_correct_game_state(game: Game):
        return check_correct_game_state(game)

    @staticmethod
    def check_game_finish(game: Game):
        return check_game_finish(game)
