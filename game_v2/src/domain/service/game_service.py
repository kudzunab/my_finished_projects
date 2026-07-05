from src.domain.interfaces.service import IGameService
from src.domain.model import GameType, PlayerSymbol, computer_uuid, Status, JoinResult, GameError
class GameService(IGameService):
    def __init__(self, repository, manager_factory, browser_factory, game_factory):
        self.repo = repository
        self.manager_factory = manager_factory
        self.browser_factory = browser_factory
        self.game_factory = game_factory

    def start_new_game(self, game_type: GameType, player1_uuid: str, player2_uuid: str | None):
        new_game = self.game_factory()
        new_game.game_type = game_type
        new_game.player1_uuid = player1_uuid
        new_game.player2_uuid = player2_uuid
        new_game.current_player_uuid = player1_uuid
        new_game.player1_symbol=PlayerSymbol.cross.value
        new_game.player2_symbol = PlayerSymbol.nulls.value
        new_game.current_player_uuid = new_game.player1_uuid

        if game_type == GameType.with_computer:
            new_game.player2_uuid = computer_uuid
            new_game.status = Status.turn_player_with_UUID.value
            self.repo.save_game(new_game, "Начало игры")

        else:
            new_game.player2_uuid = None
            new_game.status = Status.waiting_players.value
            self.repo.save_game(new_game, "До начала игры дождитесь второго игрока")

        return new_game

    def process_turn(self, game_id: str, sync_func, player_uuid: str, incoming_web_model=None):
        if not player_uuid:
            return None, "Нет такого пользователя в системе"

        game, _ = self.repo.get_game(game_id)
        if not game:
            return None, "Такой игры в базе нет"

        if game.status in [Status.nobody_wins, Status.win_player_with_UUID]:
            if incoming_web_model:
                web_model = incoming_web_model
                web_model.current_player_uuid = "NOBODY"
                web_model.message = "Эта игра уже завершена"
            else:
                web_model = self.browser_factory()
                web_model.message="нет входящей incoming_web_model у завершенной партии"

            return web_model, web_model.message

        if game.status == Status.waiting_players:
            return None, "Дождитесь подключения второго игрока."

        if player_uuid != game.player2_uuid and player_uuid != game.player1_uuid:
            return None, "Вы не являетесь участником данной игры"

        manager = self.manager_factory(this_game = game)
        web_model = incoming_web_model if incoming_web_model else self.browser_factory()

        web_model, err_code = sync_func(manager, web_model, player_uuid)

        expected_player = "крестики (X)" if web_model.current_turn == 0 else "нолики (O)"
        opposite_player = "нолики (O)" if web_model.current_turn == 0 else "крестики (X)"

        if isinstance(err_code, GameError) and err_code != GameError.GOOD_TURN:
            if err_code == GameError.NOT_YOUR_TURN:
                web_model.message = f"Сейчас ходят {expected_player}! Пожалуйста, {opposite_player}, подождите соперника."
            elif err_code == GameError.NO_MOVE_MADE:
                web_model.message = f"Игрок за {expected_player} не сделал ход! Подождите хода соперника."
            elif err_code == GameError.ERROR_STATE_CHECK:
                web_model.message = f"Ай-ай, некорректное состояние поля из-за вмешательства в данные игрока за {expected_player}!!!"
            elif not web_model.message:
                web_model.message = "Некорректный формат хода или ошибка данных!"
            return web_model, web_model.message

        if isinstance(err_code, Status) or err_code == GameError.GOOD_TURN:
            if manager.game.game_type.value == GameType.with_computer.value and web_model.current_turn == 0:
                web_model.message = "Компьютер сделал свой ход!"
            else:
                web_model.message = f"Ход успешно сделан! Следующими ходят {expected_player}."

        if isinstance(err_code, Status) and err_code in [Status.win_player_with_UUID, Status.nobody_wins]:
            if err_code == Status.nobody_wins:
                web_model.message = "Игра окончена! Боевая ничья!"
                self.repo.change_game_stats(0, manager.game.player1_uuid)
                self.repo.change_game_stats(0, manager.game.player2_uuid)
            else:
                if web_model.current_player_uuid == manager.game.player1_uuid:
                    web_model.message = f"Игра окончена! Победили крестики!"
                    self.repo.change_game_stats(1, manager.game.player1_uuid)
                    self.repo.change_game_stats(0, manager.game.player2_uuid)
                if web_model.current_player_uuid == manager.game.player2_uuid:
                    web_model.message = f"Игра окончена! Победили нолики!"
                    self.repo.change_game_stats(0, manager.game.player1_uuid)
                    self.repo.change_game_stats(1, manager.game.player2_uuid)

        self.repo.save_game(manager.game, web_model.message)

        return web_model, web_model.message

    def join_to_game(self, game_uuid, player2_uuid):
        game, _ = self.repo.get_game(game_uuid)
        if not game:
            return None, JoinResult.GAME_NOT_FOUND, 404

        if player2_uuid == game.player2_uuid:
            return game, JoinResult.ALREADY_IN_GAME, 400

        if game.player1_uuid == player2_uuid:
            return None, JoinResult.PLAYING_WITH_SELF, 400

        if game.status == Status.waiting_players:
            game.player2_uuid = player2_uuid
            game.status = Status.turn_player_with_UUID
            game.current_player_uuid = game.player1_uuid
            self.repo.save_game(game, f"Игрок с {player2_uuid} присоединился к игре")
            return game, JoinResult.SUCCESS, 200

        return None, JoinResult.GAME_FULL, 400

    def get_game_info(self, user_uuid):
        game_list=self.repo.get_finished_game(user_uuid)
        if game_list is None:
            return {"message": "Не удалось загрузить историю игр"}, 500

        return {"games": game_list}, 200

    def best_players_list(self, n=10):
        wins_list = self.repo.get_sorted_stats(n)
        if wins_list is None:
            return {"message": "Не удалось загрузить статистику"}, 500

        return {"best_players": wins_list}, 200
