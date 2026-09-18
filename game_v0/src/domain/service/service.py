from abc import ABC, abstractmethod

class IGameService(ABC):
    @abstractmethod
    def start_new_game(self):
        pass

    @abstractmethod
    def get_view_model(self, game_id: str, prepare_web_model_func):
        pass

    @abstractmethod
    def process_turn(self, game_id: str, sync_func, incoming_web_model=None):
        pass