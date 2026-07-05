from src.datasource.model.model import GameEntity
import threading, copy

class GameStorage:
    # работает только с объектами класса GameEntity, которые
    # не знают правил и не усмеют ходить
    def __init__(self):
        # коллекция
        self._data = {}
        self._lock = threading.Lock()

    def save(self, game_id, entity: GameEntity):
        with self._lock:
            self._data[game_id] = copy.deepcopy(entity)

    def get(self, game_id):
        with self._lock:
            return self._data.get(game_id)