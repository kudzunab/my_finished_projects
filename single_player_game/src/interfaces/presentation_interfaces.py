from __future__ import annotations

from abc import ABC, abstractmethod

from src.dto.entities import (
    Player, Level, MapVisibility, BattleInfo, SessionStats,
)


class IPresentation(ABC):

    @abstractmethod
    def init(self) -> None:
        """Инициализировать curses (initscr, noecho, curs_set, цвета)."""
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Восстановить терминал (endwin)."""
        ...

    @abstractmethod
    def get_input(self) -> int:
        """Ждать нажатия клавиши и вернуть код клавиши из curses getch()."""
        ...


class IMapRenderer(ABC):

    @abstractmethod
    def render_game(
        self,
        player: Player,
        level: Level,
        visibility: MapVisibility,
        battles: list[BattleInfo],
        message_top: str,
        message_mid: str,
    ) -> None:
        """Отрисовать полный игровой экран: карту + HUD.
        message_top/message_mid показываются один кадр."""
        ...


class IScreenRenderer(ABC):

    @abstractmethod
    def show_splash(self) -> None:
        """Показать заставку ROGUE в ASCII-арте. Ждать любую клавишу."""
        ...

    @abstractmethod
    def show_menu(self, selected_index: int) -> None:
        """Показать главное меню с подсветкой на selected_index.
        Пункты: Новая игра, Загрузить, Таблица рекордов, Выход."""
        ...

    @abstractmethod
    def show_inventory(
        self,
        player: Player,
        item_type_label: str,
        items: list[tuple[str, str]],
        allow_zero: bool,
    ) -> None:
        """Показать подменю инвентаря для конкретного типа предметов.
        items — список (название, описание) для слотов 1-9.
        allow_zero=True для оружия (опция снять)."""
        ...

    @abstractmethod
    def show_death_screen(self) -> None:
        """Показать экран смерти. Ждать любую клавишу."""
        ...

    @abstractmethod
    def show_win_screen(self) -> None:
        """Показать экран победы. Ждать любую клавишу."""
        ...

    @abstractmethod
    def show_leaderboard(self, entries: list[SessionStats]) -> None:
        """Показать таблицу рекордов. Ждать ESC."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Очистить экран."""
        ...
