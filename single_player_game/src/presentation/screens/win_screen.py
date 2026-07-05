"""
Экран победы после прохождения последнего уровня.

Выход по q или Enter — возврат в главное меню.
"""

import curses

from src.presentation.widgets.message_log import MessageLog
from src.presentation.widgets.statusbar import StatusBar
from src.presentation.input.keymap import QUIT, NOOP


class WinScreen:
    """Экран победы."""

    def __init__(
        self,
        map_window: "curses.window",
        status_window: "curses.window",
        message_window: "curses.window",
        gold: int = 0,
    ) -> None:
        self.map_window = map_window
        self.status_window = status_window
        self.message_window = message_window
        try:
            self.gold = max(0, int(gold))
        except (TypeError, ValueError):
            self.gold = 0

        self.message_log = MessageLog()
        self.status_bar = StatusBar()
        self.message_log.set("Victory! All 21 levels cleared. Press q or Enter...")

    def draw(self) -> None:
        """Отрисовка экрана"""
        self.status_bar.render(self.status_window)
        self.map_window.erase()
        self.map_window.box()
        height, width = self.map_window.getmaxyx()

        title = " YOU WIN! "
        subtitle = "21 levels completed"
        score_line = f"Score: {self.gold}"
        hint_line = "Press q or Enter to return to menu..."

        def cx(text: str) -> int:
            return max(2, (width - len(text)) // 2)

        def put(row: int, text: str, attr: int = 0) -> None:
            if row < 1 or row >= height - 1:
                return
            s = text[: max(1, width - 4)]
            try:
                if attr:
                    self.map_window.addstr(row, cx(s), s, attr)
                else:
                    self.map_window.addstr(row, cx(s), s)
            except curses.error:
                pass

        row0 = max(2, (height - 5) // 2)
        put(row0, title, curses.A_BOLD)
        put(row0 + 1, subtitle)
        put(row0 + 3, score_line)
        put(row0 + 4, hint_line)

        self.map_window.refresh()
        self.message_log.render(self.message_window)

    def handle(self, action: str, pressed_key_code: int) -> bool:
        """Управление клавишами"""
        if action == QUIT or pressed_key_code in (10, 13, curses.KEY_ENTER):
            return False
        if action == NOOP:
            return True
        return True
