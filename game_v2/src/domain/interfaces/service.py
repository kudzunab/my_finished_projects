from abc import ABC, abstractmethod

class IGameService(ABC):
    @abstractmethod
    def start_new_game(self, game_type, player1_uuid: str, player2_uuid: str | None):
        # для создания новой игры
        pass

    @abstractmethod
    def process_turn(self, game_id: str, sync_func, player_uuid: str, incoming_web_model=None):
        # для хода
        pass

    @abstractmethod
    def join_to_game(self, game_uuid: str, player2_uuid: str):
        # для подключения к игре второго игрока
        pass

    @abstractmethod
    def get_game_info(self, user_uuid: str):
        # для получения информации о законченных играх
        pass
