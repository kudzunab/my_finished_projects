from abc import ABC, abstractmethod

class IGameService(ABC):
    @abstractmethod
    def start_new_game(self, game_type, player1_uuid: str, player2_uuid: str):
        pass

    @abstractmethod
    def process_turn(self, game_id: str, sync_func, player_uuid: str, incoming_web_model=None):
        pass
