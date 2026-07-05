"""
Настройка и запуск curses-среды:

Модуль отвечает за:
- проверка размера терминала (мин 80х24);
- создание базового layout(окна, сообщения, карта, статус);
- инициализация режима curses и цветовых пар;
- запуск приложения через curses.wrapper();
"""
import curses
import sys


SCREEN_HEIGHT = 24
SCREEN_WIDTH = 80

TERMINAL_TOO_SMALL_MESSAGE = (
    "Terminal is too small. Please resize your terminal(min 80x24) and run the game again."
)


class TerminalTooSmallError(Exception):
    """Текущий размер stdscr меньше SCREEN_WIDTH×SCREEN_HEIGHT."""


def check_terminal_size(screen: "curses.window") -> None:
    """Бросает TerminalTooSmallError, если терминал уже требуемого layout."""
    ulc = getattr(curses, "update_lines_cols", None)
    if ulc is not None:
        try:
            ulc()
        except curses.error:
            pass
    height, width = screen.getmaxyx()
    if height < SCREEN_HEIGHT or width < SCREEN_WIDTH:
        raise TerminalTooSmallError

MESSAGE_LINE_INDEX = 0
MAP_START_LINE_INDEX = 1
MAP_HEIGHT = 22
STATUS_LINE_INDEX = 23


def create_layout(screen: "curses.window"):
    """
    Создает layout окон:
    - окно сообщения;
    - окно карты;
    - окно статуса.
    """
    check_terminal_size(screen)
    terminal_height, terminal_width = screen.getmaxyx()
    status_window = screen.derwin(1, terminal_width, 0, 0)
    message_window = screen.derwin(1, terminal_width, terminal_height - 1, 0)
    map_window = screen.derwin(terminal_height - 2, terminal_width, 1, 0)
    return map_window, status_window, message_window


def init_curses():
    """
    Выполняет базовую настройку режима curses.
    """
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()

def init_colors():
    """
    Инициализирует цветовые пары.
    """
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_WHITE, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)

def run_curses(main_fn):
    """
    Запускает приложение в безопасной оболочке.
    """
    try:
        curses.wrapper(main_fn)
    except TerminalTooSmallError:
        print(TERMINAL_TOO_SMALL_MESSAGE, file=sys.stderr)
        raise SystemExit(1) from None
