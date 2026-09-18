"""
Адаптер для сохранения и загрузки игры.
"""

from __future__ import annotations

from pathlib import Path

from src.datalayer import load_game, save_game, return_path

SAVE_FILE_NAME = "save.json"

def get_save_path() -> Path:
    """Возвращает полный путь к файлу сохранения"""
    return Path(return_path(SAVE_FILE_NAME)).resolve()

def save_current_game(player, level) -> bool:
    """Сохраняет текущего игрока и текущий уровень """

    save_path = get_save_path()

    try:
        save_game(player, level, save_path)
        return True
    except (OSError, TypeError, ValueError, AttributeError):
        return False

def load_saved_game():
    """Загружает сохраненную игру"""

    save_path = get_save_path()
    return load_game(save_path)

def has_saved_game() -> bool:
    """Проверяет, есть ли файл сохранения"""
    save_path = get_save_path()
    return save_path.exists()
