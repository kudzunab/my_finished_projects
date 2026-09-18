#from __future__ import annotations

import json
import os
from src.datalayer import load_game
#пока оставим это тут
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
filename = os.path.join(DEFAULT_DATA_DIR, "save.json")
def save_game(player, level, _filename):
    os.makedirs(os.path.dirname(_filename), exist_ok=True)
    data = {
        "player": player.to_dict(),
        "level": level.to_dict()
    }
    try:
        with open(_filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")


# python3 -m src.datalayer.save_manager
# зупуск только из корня, чтобы проверить работу.
# PYTHONPATH=. python3 src/datalayer/save_manager.py
if __name__ =="__main__":
    from src.domain.entities import Player, Level, Position
    from src.domain.generation import generate_next_level, generate_player
    # Создаем объекты
    test_player = Player()
    test_level = Level()
    temp_pos = Position()
    generate_next_level(test_level, test_player, temp_pos)
    generate_player(test_level, test_player)

    # Сохраняем
    if save_game(test_player, test_level, filename):
        print("Данные успешно сохранены в data/save.json!")

    # Пробуем тут же загрузить обратно
    p, l = load_game(filename)
    print(l.init_position.x, l.init_position.y,
          l.end_position.x, l.end_position.y,
          p.type, p.position.x, p.position.y)
    #if p and p.money == 999:
    #    print("Проверка пройдена: данные загружены корректно!")


"""
from src.interfaces.data_interfaces import IDataService
from src.dto.entities import GameState, SessionStats
from src.datalayer.serializers import (
    game_state_to_dict, game_state_from_dict,
    session_stats_to_dict, session_stats_from_dict,
)

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class JsonDataService(IDataService):

    def __init__(self, data_dir: str = DEFAULT_DATA_DIR) -> None:
        self._data_dir = data_dir
        os.makedirs(self._data_dir, exist_ok=True)
        self._save_path = os.path.join(self._data_dir, "save.json")
        self._stats_path = os.path.join(self._data_dir, "statistics.json")
        self._score_path = os.path.join(self._data_dir, "scoreboard.json")

        if not os.path.exists(self._score_path):
            self._write_json(self._score_path, {"sessions": []})

    def save_game(self, state: GameState) -> None:
        self._write_json(self._save_path, game_state_to_dict(state))

    def load_game(self) -> GameState | None:
        data = self._read_json(self._save_path)
        if data is None:
            return None
        try:
            return game_state_from_dict(data)
        except (KeyError, TypeError, ValueError):
            return None

    def has_save(self) -> bool:
        return os.path.isfile(self._save_path)

    def reset_save(self) -> None:
        if os.path.isfile(self._save_path):
            os.remove(self._save_path)

    def save_session_stats(self, stats: SessionStats) -> None:
        self._write_json(self._stats_path, session_stats_to_dict(stats))

    def load_session_stats(self) -> SessionStats:
        data = self._read_json(self._stats_path)
        if data is None:
            return SessionStats()
        return session_stats_from_dict(data)

    def finalize_session(self, stats: SessionStats) -> None:
        data = self._read_json(self._score_path)
        if data is None:
            data = {"sessions": []}
        data["sessions"].append(session_stats_to_dict(stats))
        self._write_json(self._score_path, data)

    def load_leaderboard(self) -> list[SessionStats]:
        data = self._read_json(self._score_path)
        if data is None:
            return []
        entries = [
            session_stats_from_dict(s)
            for s in data.get("sessions", [])
        ]
        entries.sort(key=lambda s: s.treasures, reverse=True)
        return entries

    @staticmethod
    def _write_json(path: str, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _read_json(path: str) -> dict | None:
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
"""