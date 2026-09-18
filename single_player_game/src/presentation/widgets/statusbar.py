"""
Модуль отображения строки статуса игрока.
"""

import curses

class StatusBar:
    """
    Компонент отображения статусной строки игрока.
    """
    def render(self, status_window, player_status: dict | None = None) -> None:
        """Отрисовывает текущий статус игрока."""
        status_window.erase()
        if player_status:
            text = (
                f"HP: {player_status.get('hp', '--')}/{player_status.get('max_hp', '--')} "
                f"STR: {player_status.get('str', '--')} AGI: {player_status.get('agi', '--')} "
                f"LVL: {player_status.get('lvl', '--')} GOLD: {player_status.get('gold', '--')}"
            )
        else:
            text = "HP: --/-- STR: -- AGI: -- LVL: -- GOLD: --"
        try:
            status_window.addstr(0, 0, text)
        except curses.error:
            pass
        status_window.refresh()
