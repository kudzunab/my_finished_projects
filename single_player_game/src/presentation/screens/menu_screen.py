"""
Экран главного меню.

Отображает список пунктов меню и позволяет выбрать действие.
"""

import curses
from enum import Enum, auto

from src.presentation.widgets.message_log import MessageLog
from src.presentation.widgets.statusbar import StatusBar
from src.presentation.input.keymap import (
    QUIT, MOVE_UP, MOVE_DOWN, NOOP
)


class MenuResult(Enum):
    """Результат выбора пункта меню."""
    NEW_GAME = auto()
    LOAD_GAME = auto()
    SCOREBOARD = auto()
    EXIT = auto()


class MenuScreen:
    """
    Экран меню.
    Рисует заголовок и список пунктов, хранит выбранный пункт
    и возвращает управление наружу после подтверждения выбора.
    """
    def __init__(
        self,
        map_window: "curses.window",
        status_window: "curses.window",
        message_window: "curses.window",
    ) -> None:
        """Инициализирует меню и выставляет курсор на первый пункт."""
        self.map_window = map_window
        self.status_window = status_window
        self.message_window = message_window

        self.message_log = MessageLog()
        self.status_bar = StatusBar()

        self.items: list[tuple[str, MenuResult]] = [
            ("New game", MenuResult.NEW_GAME),
            ("Load game", MenuResult.LOAD_GAME),
            ("Scoreboard", MenuResult.SCOREBOARD),
            ("Exit", MenuResult.EXIT),
        ]
        self.selected_idx: int = 0
        self.selected: MenuResult | None = None

        self.message_log.set("↑/↓ (или W/S) — выбор, Enter — подтвердить, q — выход")

    def draw(self) -> None:
        """Отрисовывает окно меню и подсказку управления."""
        self.status_bar.render(self.status_window)

        self.map_window.erase()
        height, width = self.map_window.getmaxyx()

        title = "ROGUE"
        title_y = max(1, height // 4)
        title_x = max(1, (width - len(title)) // 2)

        self.map_window.box()

        try:
            self.map_window.addstr(title_y, title_x, title, curses.A_BOLD)
        except curses.error:
            pass

        menu_top = title_y + 3
        for i, (label, _) in enumerate(self.items):
            y = menu_top + i
            x = max(2, (width - len(label)) // 2)

            text_attribute = curses.A_REVERSE if i == self.selected_idx else curses.A_NORMAL
            try:
                self.map_window.addstr(y, x, label, text_attribute)
            except curses.error:
                pass

        self.map_window.refresh()
        self.message_log.render(self.message_window)

    def handle(self, action: str, pressed_key_code: int) -> bool:
        """
        Обрабатывает ввод пользователя.

        Возвращает False, когда меню завершено (выбор сделан или выход).
        """
        if action == QUIT:
            self.selected = MenuResult.EXIT
            return False

        if action == MOVE_UP:
            self.selected_idx = (self.selected_idx - 1) % len(self.items)
            return True

        if action == MOVE_DOWN:
            self.selected_idx = (self.selected_idx + 1) % len(self.items)
            return True

        if self._is_enter(pressed_key_code):
            _, result = self.items[self.selected_idx]
            self.selected = result
            return False

        if action == NOOP:
            return True

        return True

    def _is_enter(self, key_code: int) -> bool:
        """Проверяет что нажат Enter"""
        return key_code in (10, 13, curses.KEY_ENTER)
