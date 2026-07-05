from __future__ import annotations

from abc import ABC, abstractmethod

from src.dto.entities import GameState, SessionStats


class IDataService(ABC):

    @abstractmethod
    def save_game(self, state: GameState) -> None:
        """Сериализовать полное состояние игры в save.json."""
        ...

    @abstractmethod
    def load_game(self) -> GameState | None:
        """Десериализовать состояние игры из save.json.
        Вернуть None, если файл отсутствует или повреждён."""
        ...

    @abstractmethod
    def has_save(self) -> bool:
        """Вернуть True, если файл сохранения существует."""
        ...

    @abstractmethod
    def reset_save(self) -> None:
        """Удалить файл сохранения."""
        ...

    @abstractmethod
    def save_session_stats(self, stats: SessionStats) -> None:
        """Записать текущую статистику сессии в statistics.json."""
        ...

    @abstractmethod
    def load_session_stats(self) -> SessionStats:
        """Загрузить текущую статистику сессии из statistics.json."""
        ...

    @abstractmethod
    def finalize_session(self, stats: SessionStats) -> None:
        """Добавить статистику в таблицу рекордов."""
        ...

    @abstractmethod
    def load_leaderboard(self) -> list[SessionStats]:
        """Вернуть все прошлые сессии, отсортированные по сокровищам."""
        ...
