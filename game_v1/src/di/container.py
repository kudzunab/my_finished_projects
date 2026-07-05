from dependency_injector import containers, providers
from src.domain.service.game_manager import GameManager
from src.web.model import BrowserGame
from src.domain.service.step_by_step_game import StepByStepGame
from src.domain.model import Game
from src.domain.model.model import GameError, Status
from src.datasource.repository.repository import GameRepository
from src.domain.service.game_service import GameService
from src.domain.service.user_service import UserService
from web.module.authorisation_service import AuthorisationService
from src.datasource.repository.connection import init_my_db
from src.web.model.model import SignUpRequest
from web.module.authentification import UserAuthenticator
class Container(containers.DeclarativeContainer):
    session_factory = providers.Singleton(init_my_db)
    # игра, с которой может работать вся логика игры
    game = providers.Factory(Game)
    browser_game = providers.Factory(BrowserGame)

    game_repository = providers.Singleton(
        GameRepository,
        session_factory=session_factory
    )

    my_game_logic = providers.Singleton(StepByStepGame)

    # отвечает за процесс игры, есть три метода
    game_manager = providers.Factory(GameManager, ai_service=my_game_logic)

    #
    game_service = providers.Factory(
        GameService,
        repository=game_repository,
        manager_factory = game_manager.provider,
        browser_factory = browser_game.provider,
        game_factory = game.provider
    )

    user_service = providers.Factory(UserService, session_factory=session_factory)

    auth_service = providers.Factory(AuthorisationService, user_service=user_service)

    request_factory = providers.Factory(SignUpRequest)

    user_authenticator = providers.Factory(UserAuthenticator, auth_service=auth_service)
"""
class Container(containers.DeclarativeContainer):
    my_game_logic = providers.Singleton(StepByStepGame)
    game = providers.Factory(Game)
    game_manager = providers.Factory(GameManager, ai_service = my_game_logic)
    browser_game = providers.Factory(BrowserGame)
"""
    # game_manager = providers.Factory(GameManager, ai_service = my_game_logic)
    # это имеет смысл, если к менеджеру будет жестко привящзана конкретная партия

if __name__ == "__main__":

    from src.domain.model import Game

    mess_dict = {
        GameError.ERROR_STATE_CHECK: "Ай-ай, не корректное состояние поля из-за вмешательства в данные!!!",
        GameError.ERROR_INPUT_TYPE: "Хакерам тут не рады! Не надо ломать код!",
        GameError.ERROR_VALUE: "Гмм... А ход-то не корректный, за гранью понимания AI",
        GameError.OCCUPIED_CELL: "Эта клетка уже занята, выберите другую",

        # Результаты финиша
        Status.win_player_with_UUID: "Крестики выиграли!",
        Status.nobody_wins: "Боевая ничья!",

        # Промежуточные состояния (заменили магические числа на объекты)
        Status.turn_player_with_UUID: "Ваш ход"
    }
    container = Container()
    current_game = container.game()
    manager = container.game_manager(this_game=current_game)

    def get_answer() -> int:
        try:
            _key = int(input("Выберите номер клетки (0 - 8) либо -1 для хода ИИ:"))
        except (ValueError, TypeError):
            _key = -1

        return _key

    my_dict = {0: "X", 1: "O", -1: "_"}

    while True:
        ind = get_answer()
        if 0 <= ind <= 8:
            row, col = divmod(ind, 3)
            current_game.field[row][col] = 0
        else:
            print("Некорректный ввод")
            continue
        is_turn, message = manager.make_turn()
        for i in range(3):
            print(*(my_dict[current_game.field[i][j]] for j in range(3)))

        print(mess_dict.get(message, message))
        if message in [Status.win_player_with_UUID, Status.nobody_wins]:
            break
