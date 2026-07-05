"""
Экран статистики (Scoreboard): топ забегов по собранному золоту (player.money).
"""
from __future__ import annotations

import curses

from src.datalayer.scoreboard_store import format_scoreboard_datetime, get_sorted_entries
from src.presentation.widgets.message_log import MessageLog
from src.presentation.widgets.statusbar import StatusBar
from src.presentation.input.keymap import QUIT, NOOP

_OUTCOME_LABEL = {
    "quit": "quit",
    "death": "death",
    "win": "win",
}


class StatsScreen:
    """Экран таблицы рекордов."""

    def __init__(
        self,
        map_window: "curses.window",
        status_window: "curses.window",
        message_window: "curses.window",
    ) -> None:
        self.map_window = map_window
        self.status_window = status_window
        self.message_window = message_window

        self.message_log = MessageLog()
        self.status_bar = StatusBar()
        self._entries = get_sorted_entries(limit=30)
        self.message_log.set("Scoreboard by gold. Press q to return.")

    def draw(self) -> None:
        """Лейаут экрана"""
        self.status_bar.render(self.status_window)
        self.map_window.erase()

        h, w = self.map_window.getmaxyx()
        if h < 4 or w < 12:
            self.map_window.addstr(0, 0, "Too small")
            self.map_window.refresh()
            self.message_log.render(self.message_window)
            return

        self.map_window.box()
        title = " SCOREBOARD "
        col = max(2, (w - len(title)) // 2)
        try:
            if col + len(title) < w:
                self.map_window.addstr(1, col, title, curses.A_BOLD)
            else:
                self.map_window.addstr(1, 2, title[: max(1, w - 4)], curses.A_BOLD)
        except curses.error:
            pass

        header = f"{'#':>3}  {'gold':>6}   {'end':<6}    date    hh:mm"
        try:
            self.map_window.addstr(
                2, 2, header[: max(0, w - 4)], curses.A_BOLD
            )
        except curses.error:
            pass

        row_y = 3
        max_rows = max(0, h - 4)
        for i, entry in enumerate(self._entries[:max_rows], start=1):
            if row_y >= h - 1:
                break
            try:
                gold = int(entry["gold"])
            except (KeyError, TypeError, ValueError):
                gold = 0
            outcome = _OUTCOME_LABEL.get(str(entry.get("outcome", "")), "?")
            at_disp = format_scoreboard_datetime(str(entry.get("at", "")))
            line = f"{i:>3}  {gold:>6}  {outcome:<6}  {at_disp}   "
            try:
                self.map_window.addstr(row_y, 2, line[: max(0, w - 4)])
            except curses.error:
                pass
            row_y += 1

        if not self._entries:
            msg = "No runs recorded yet."
            try:
                self.map_window.addstr(min(row_y + 1, h - 2), 2, msg[: max(0, w - 4)])
            except curses.error:
                pass

        self.map_window.refresh()
        self.message_log.render(self.message_window)

    def handle(self, action, pressed_key_code) -> bool:
        """Управление клавишами"""
        _ = pressed_key_code

        if action == QUIT:
            return False
        if action == NOOP:
            return True
        return True
