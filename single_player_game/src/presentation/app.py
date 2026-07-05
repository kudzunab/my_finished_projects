"""
Точка входа в приложение.
Отвечает за инициализацию cures, создание окон интерфейса
и управление переходами между экранами.
"""

import curses

from src.presentation import curses_runtime
from src.presentation.input.controller import InputController
from src.presentation.screens.game_screen import GameScreen
from src.presentation.screens.menu_screen import MenuScreen, MenuResult
from src.presentation.screens.stats_screen import StatsScreen
from src.presentation.screens.death_screen import DeathScreen
from src.presentation.screens.win_screen import WinScreen
from src.presentation.adapters.save_game_adapter import load_saved_game
from src.datalayer.scoreboard_store import record_session_score


def run_screen(
    controller: InputController,
    stdscr: "curses.window",
    map_window,
    screen_obj,
) -> None:
    """Запускает цикл обработки конкретного экрана"""
    is_running = True
    while is_running:
        curses_runtime.check_terminal_size(stdscr)
        screen_obj.draw()
        action, pressed_key_code = controller.read(map_window)
        is_running = screen_obj.handle(action, pressed_key_code)

def run_menu_screen(controller, stdscr, map_window, status_window, message_window):
    """Запускает цикл обработки меню"""
    menu_screen = MenuScreen(map_window, status_window, message_window)
    run_screen(controller, stdscr, map_window, menu_screen)
    return menu_screen.selected

def run_new_game_screen(
    controller, stdscr, map_window, status_window, message_window
) -> GameScreen:
    """Запускает цикл обработки игрового экрана. Возвращает экран для записи scoreboard."""
    game_screen = GameScreen(map_window, status_window, message_window)
    run_screen(controller, stdscr, map_window, game_screen)
    return game_screen

def run_stats_screen(controller, stdscr, map_window, status_window, message_window):
    """Запускает цикл обработки экрана стат"""
    stats_screen = StatsScreen(map_window, status_window, message_window)
    run_screen(controller, stdscr, map_window, stats_screen)

def run_death_screen(
    controller,
    stdscr,
    map_window,
    status_window,
    message_window,
    *,
    gold: int = 0,
    death_reason: str = "",
):
    """Запускает экран смерти; gold — счёт (как в scoreboard) death_reason — текст на английском."""
    death_screen = DeathScreen(
        map_window,
        status_window,
        message_window,
        gold=gold,
        death_reason=death_reason,
    )
    run_screen(controller, stdscr, map_window, death_screen)


def run_win_screen(
    controller, stdscr, map_window, status_window, message_window, *, gold: int = 0
):
    """Экран победы после прохождения всех уровней."""
    win_screen = WinScreen(map_window, status_window, message_window, gold=gold)
    run_screen(controller, stdscr, map_window, win_screen)


def run_loaded_game_screen(
    controller, stdscr, map_window, status_window, message_window, player, level
) -> GameScreen:
    """Запускает цикл обработки игрового экрана. Возвращает экран для записи scoreboard."""
    game_screen = GameScreen(
        map_window,
        status_window,
        message_window,
        player=player,
        level=level,
    )
    run_screen(controller, stdscr, map_window, game_screen)
    return game_screen

def main(screen: "curses.window") -> None:
    """
    Главная точка входа.
    Выполняет инициализацию curses, создает layout окон
    и управляет основным циклом экранов.
    """
    curses_runtime.init_curses()
    curses_runtime.init_colors()

    map_window, status_window, message_window = curses_runtime.create_layout(screen)
    map_window.keypad(True)

    controller = InputController()

    while True:
        selected = run_menu_screen(
            controller, screen, map_window, status_window, message_window
        )

        if selected == MenuResult.NEW_GAME:
            game_session = run_new_game_screen(
                controller,
                screen,
                map_window,
                status_window,
                message_window,
            )
            record_session_score(
                game_session.player.money,
                is_dead=game_session.is_player_dead,
                is_win=game_session.is_player_won,
            )
            if game_session.is_player_won:
                run_win_screen(
                    controller,
                    screen,
                    map_window,
                    status_window,
                    message_window,
                    gold=game_session.player.money,
                )
            elif game_session.is_player_dead:
                run_death_screen(
                    controller,
                    screen,
                    map_window,
                    status_window,
                    message_window,
                    gold=game_session.player.money,
                    death_reason=game_session.death_reason,
                )

        elif selected == MenuResult.LOAD_GAME:
            player, level = load_saved_game()
            if player is not None and level is not None:
                game_session = run_loaded_game_screen(
                    controller,
                    screen,
                    map_window,
                    status_window,
                    message_window,
                    player,
                    level,
                )
                record_session_score(
                    game_session.player.money,
                    is_dead=game_session.is_player_dead,
                    is_win=game_session.is_player_won,
                )
                if game_session.is_player_won:
                    run_win_screen(
                        controller,
                        screen,
                        map_window,
                        status_window,
                        message_window,
                        gold=game_session.player.money,
                    )
                elif game_session.is_player_dead:
                    run_death_screen(
                        controller,
                        screen,
                        map_window,
                        status_window,
                        message_window,
                        gold=game_session.player.money,
                        death_reason=game_session.death_reason,
                    )
            else:
                screen.clear()
                screen.addstr(0, 0, "No saved game found. Press q ...")
                screen.refresh()
                screen.getch()
        elif selected == MenuResult.SCOREBOARD:
            run_stats_screen(
                controller,
                screen,
                map_window,
                status_window,
                message_window,
            )

        else:
            break

def run() -> None:
    """
    Запускает приложение в режиме curses.
    """
    curses_runtime.run_curses(main)
