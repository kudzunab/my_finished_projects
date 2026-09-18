"""
НА ДАННЫЙ МОМЕНТ ПОЧТИ НЕ ИСПОЛЬЗУЕТСЯ
позже можно будет убрать
Контроллер ввода.

Считывает нажатую клавишу из curses-окна и преобразует её
в действие (action) с помощью таблицы KEY_TO_ACTION.
"""

import curses
from src.presentation.input.keymap import KEY_TO_ACTION, NOOP


class InputController:
    """Преобразует коды клавиш curses в логические действия (action)."""
    def read(self, window: "curses.window") -> tuple[str, int]:
        """
        Считывает клавишу из окна и возвращает (action, pressed_key_code).

        action берётся из KEY_TO_ACTION, а если клавиша неизвестна —
        возвращается NOOP.
        """
        pressed_key_code = window.getch()
        action = KEY_TO_ACTION.get(pressed_key_code, NOOP)
        return action, pressed_key_code
