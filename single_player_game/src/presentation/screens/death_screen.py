"""
Экран показывающийся после смерти игрока

Выход по q или по Enter
"""

import curses

from src.presentation.widgets.message_log import MessageLog
from src.presentation.widgets.statusbar import StatusBar
from src.presentation.input.keymap import QUIT, NOOP


class DeathScreen:
    """экран смерти игрока"""

    def __init__(
        self,
        map_window: "curses.window",
        status_window: "curses.window",
        message_window: "curses.window",
        gold: int = 0,
        death_reason: str = "",
    ) -> None:

        self.map_window = map_window
        self.status_window = status_window
        self.message_window = message_window
        try:
            self.gold = max(0, int(gold))
        except (TypeError, ValueError):
            self.gold = 0
        self.death_reason = (death_reason or "").strip()

        self.message_log = MessageLog()
        self.status_bar = StatusBar()
        msg = "You are dead. Press q or Enter to continue..."
        if self.death_reason:
            msg = f"{self.death_reason} {msg}"
        self.message_log.set(msg)

    def draw(self) -> None:
        """Отрисовка экрана"""
        self.status_bar.render(self.status_window)
        self.map_window.erase()
        self.map_window.box()
        height, width = self.map_window.getmaxyx()
        title = "GAME OVER"
        title_y = max(1, height // 8)
        title_x = max(2, (width - len(title)) // 2)

        tomb = [
                "      __________      ",
                "     /          \\     ",
                "    /   R.I.P.   \\    ",
                "   |              |   ",
                "   |    PLAYER    |   ",
                "   |              |   ",
                "   |              |   ",
                "   |______________|   ",
        ]

        score_line = f"Score: {self.gold}"
        hint_line = "Press q or Enter to continue..."
        reason_display = self.death_reason[: max(1, width - 4)] if self.death_reason else ""

        tomb_top = title_y + 2
        tomb_left = max(2, (width - len(tomb[0])) // 2)

        try:
            self.map_window.addstr(title_y, title_x, title, curses.A_BOLD)
        except curses.error:
            pass

        for i, line in enumerate(tomb):
            y = tomb_top + i
            if y >= height - 2:
                break
            try:
                self.map_window.addstr(y, tomb_left, line)
            except curses.error:
                pass

        score_y = min(height - 5, tomb_top + len(tomb) + 1)
        score_x = max(2, (width - len(score_line)) // 2)
        reason_y = score_y + 1
        hint_y = min(height - 2, reason_y + (1 if reason_display else 0))
        hint_x = max(2, (width - len(hint_line)) // 2)

        try:
            self.map_window.addstr(score_y, score_x, score_line[: max(1, width - 4)])
        except curses.error:
            pass

        if reason_display and reason_y < height - 2:
            reason_x = max(2, (width - len(reason_display)) // 2)
            try:
                self.map_window.addstr(reason_y, reason_x, reason_display)
            except curses.error:
                pass
            hint_y = min(height - 2, reason_y + 1)

        try:
            if hint_y < height - 1:
                self.map_window.addstr(
                    hint_y, hint_x, hint_line[: max(1, width - 4)]
                )
        except curses.error:
            pass

        self.map_window.refresh()
        self.message_log.render(self.message_window)

    def handle(self, action: str, pressed_key_code: int) -> bool:
        """ False = закрыть экран, True = остаться на этом экране"""
        if action == QUIT or pressed_key_code in (10, 13, curses.KEY_ENTER):
            return False
        if action == NOOP:
            return True
        return True
