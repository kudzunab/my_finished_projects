"""
Модуль отображения строки сообщений игроку.

Содержит простой лог сообщений, который хранит 1
строку текста и выводит ее в отдельное окно curses.
"""
import curses

class MessageHistory:
    """Хранит историю сообщений и отображает ее в окне."""
    def __init__(self, max_messages: int = 100) -> None:
        self._messages: list[str] = []
        self.max_messages = max_messages
        self._scroll_offset = 0

    def add(self, text: str) -> None:
        """Добавляет сообщение в историю"""
        if not text:
            return

        self._messages.append(text)
        if len(self._messages) > self.max_messages:
            overflow = len(self._messages) - self.max_messages
            self._messages = self._messages[overflow:]
        self._scroll_offset = 0

    def scroll_up(self) -> None:
        """Прокручивает к более старым сообщениям"""
        if not self._messages:
            return

        max_offset = len(self._messages) - 1
        self._scroll_offset = min(self._scroll_offset + 1, max_offset)

    def scroll_down(self) -> None:
        """Прокручивает к более новым сообщениям"""
        self._scroll_offset = max(self._scroll_offset - 1, 0)

    def get_current_message(self) -> str:
        """Возвращает текущее сообщение для однострочного лога"""
        if not self._messages:
            return ""

        index = len(self._messages) - 1 - self._scroll_offset
        return self._messages[index]

    def get_recent_messages(self, limit: int) -> list[str]:
        """Возвращает последние сообщения"""
        if limit <= 0:
            return []

        end = len(self._messages) - self._scroll_offset
        start = max(0, end - limit)
        return self._messages[start:end]

    def is_scrolled(self) -> bool:
        """Проверяет, прокручен ли лог"""
        return self._scroll_offset > 0


class MessageLog:
    """
    Компонент для хранения и отображения текущего сообщения
    игроку.

    Используется для вывода подсказок и статуса действий.
    """
    def __init__(self, history: MessageHistory | None = None) -> None:
        """ Создает пустой лог сообщений. """
        self._history = history if history is not None else MessageHistory()

    def set(self, text: str) -> None:
        """ Устанавливает текст текущего сообщения. """
        self._history.add(text)

    def scroll_up(self) -> None:
        """Прокручивает к более старым сообщениям"""
        self._history.scroll_up()

    def scroll_down(self) -> None:
        """Прокручивает к более новым сообщениям"""
        self._history.scroll_down()

    def render(self, message_window) -> None:
        """Отрисовывает одну строку сообщения внизу"""
        message_window.erase()
        text = self._history.get_current_message()
        try:
            message_window.addstr(0, 0, text)
        except curses.error:
            pass
        message_window.refresh()

    def render_panel(self, log_window) -> None:
        """Отрисовывает многострочный лог сообщений"""
        log_window.erase()
        log_window.box()

        height, width = log_window.getmaxyx()
        visible_lines = max(0, height - 1)
        messages = self._history.get_recent_messages(visible_lines)

        for i, text in enumerate(messages):
            trimmed = text[: max(0, width - 2)]
            try:
                log_window.addstr(i + 1, 1, trimmed)
            except curses.error:
                pass
        log_window.refresh()
