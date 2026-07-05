from src.domain.service.service import IGameService

class GameService(IGameService):
    def __init__(self, repository, manager_factory, browser_factory, game_factory):
        self.repo = repository
        self.manager_factory = manager_factory # container.game_manager
        self.browser_factory = browser_factory # container.browser_game
        self.game_factory = game_factory

    def start_new_game(self):
        new_game = self.game_factory()
        self.repo.save_game(new_game, "Начало игры")
        return new_game

    def get_view_model(self, game_id: str, prepare_web_model_func):
        game, message = self.repo.get_game(game_id)
        if not game:
            return None

        return prepare_web_model_func(game, self.browser_factory, message)

    def process_turn(self, game_id: str, sync_func, incoming_web_model=None):
        game, _ = self.repo.get_game(game_id)
        if not game:
            return None

        # создаем менеджер для конкретной игры
        manager = self.manager_factory(this_game = game)
        # создаем пустой объект класса web_browser_game
        web_model = incoming_web_model if incoming_web_model else self.browser_factory()

        # выполняем ход и направляем чезультат
        sync_func(manager, web_model)

        self.repo.save_game(manager.game, web_model.message)

        return web_model