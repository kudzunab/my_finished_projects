from dependency_injector import containers, providers
from src.domain.service.game_manager import GameManager
from src.web.model import BrowserGame
from src.domain.service.step_by_step_game import StepByStepGame
from src.domain.model import Game
from src.web.model.model import JwtRequest
from src.datasource.repository.repository import GameRepository
from src.domain.service.game_service import GameService
from src.domain.service.user_service import UserService
from web.service.authorisation_service import AuthorisationService
from src.datasource.repository.connection import init_my_db
from web.service.jwt_service import JwtProvider
from web.service.authentification import UserAuthenticator
from dotenv import load_dotenv
#from src.domain.model.model import GameError, Status #, GameStatus

class Container(containers.DeclarativeContainer):
    load_dotenv()
    session_factory = providers.Singleton(init_my_db)
    game_repository = providers.Singleton(
        GameRepository,
        session_factory=session_factory
    )
    # игра, с которой может работать вся логика игры
    game = providers.Factory(Game)
    browser_game = providers.Factory(BrowserGame)
    my_game_logic = providers.Singleton(StepByStepGame)
    game_manager = providers.Factory(GameManager, ai_service=my_game_logic)

    game_service = providers.Factory(
        GameService,
        repository=game_repository,
        manager_factory = game_manager.provider,
        browser_factory = browser_game.provider,
        game_factory = game.provider
    )

    user_service = providers.Factory(UserService,
                                     session_factory=session_factory)
    jwt_provider = providers.Singleton(JwtProvider)

    auth_service = providers.Factory(AuthorisationService,
                                     user_service=user_service,
                                     jwt_provider=jwt_provider)

    request_factory = providers.Factory(JwtRequest)

    user_authenticator = providers.Factory(UserAuthenticator,
                                           auth_service=auth_service,
                                           jwt_provider=jwt_provider)
    

if __name__ == "__main__":
    print("Здесь уже ничего нет")
