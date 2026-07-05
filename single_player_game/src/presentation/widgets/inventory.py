"""
Виджет инвентаря.

Отображает список предметов, отвечает за перемещение курсора,
возвращает UIAction при закрытии окна или выборе предмета.
"""

import curses
from typing import Any, Optional
from dataclasses import dataclass

from src.presentation.widgets.message_log import MessageLog
from src.presentation.widgets.statusbar import StatusBar
from src.presentation.input.keymap import (
    QUIT,
    MOVE_UP,
    MOVE_DOWN,
    NOOP,
    SELECT_ITEM_0,
    SELECT_ITEM_1,
    SELECT_ITEM_2,
    SELECT_ITEM_3,
    SELECT_ITEM_4,
    SELECT_ITEM_5,
    SELECT_ITEM_6,
    SELECT_ITEM_7,
    SELECT_ITEM_8,
    SELECT_ITEM_9,
)

@dataclass(frozen=True)
class UIAction:
    """
    Результат взаимодействия пользователя с UI.

    action_type: тип действия (например, "close_inventory" или "use_item").
    action_payload: доп. нагрузка (например, выбранный предмет).
    """
    action_type: str
    action_payload: Optional[Any] = None


class InventoryWidget:
    """
    Экран инвентаря.

    Рисует заголовок и нумерованный список предметов.
    Управление: стрелки/WS - перемещение, Enter - использовать,
    q/i - закрыть.
    """
    def __init__(
        self,
        map_window: "curses.window",
        status_window: "curses.window",
        message_window: "curses.window",
        inventory_items: list[Any],
    ) -> None :
        """
        Рисует окно инвентаря.
        inventory_items: список предметов в произвольном формате.
        """
        self.map_window = map_window
        self.status_window = status_window
        self.message_window = message_window

        self.message_log = MessageLog()
        self.status_bar = StatusBar()


        self.inventory_items = inventory_items

        self.selected_item_index = 0

        self.message_log.set(
            "↑/↓ или W/S — выбор, Enter — использовать, q / i — закрыть"
        )

    def draw(self) -> None:
        """
        Рисует окно инвентаря и строку подсказки.

        Если инвентарь пуст, выводит сообщение "empty".
        """
        self.status_bar.render(self.status_window)

        self.map_window.erase()
        window_height, window_width = self.map_window.getmaxyx()
        self.map_window.box()

        title_text = "INVENTORY"
        title_position_y = max(1, window_height // 6)
        title_position_x = max(
            2, (window_width - len(title_text)) // 2
        )

        try:
            self.map_window.addstr(
                title_position_y,
                title_position_x,
                title_text,
                curses.A_BOLD,
            )
        except curses.error:
            pass

        if not self.inventory_items:
            empty_message = "(empty)"
            empty_position_y = title_position_y + 2
            empty_position_x = max(
                2, (window_width - len(empty_message)) // 2
            )

            try:
                self.map_window.addstr(
                    empty_position_y,
                    empty_position_x,
                    empty_message,
                )
            except curses.error:
                pass

            self.map_window.refresh()
            self.message_log.render(self.message_window)
            return

        first_item_position_y = title_position_y + 2

        for index, inventory_item in enumerate(self.inventory_items):
            line_text = self._format_item_line(
                index,
                inventory_item,
            )

            line_position_y = first_item_position_y + index
            line_position_x = 3

            if index == self.selected_item_index:
                text_attribute = curses.A_REVERSE
            else:
                text_attribute = curses.A_NORMAL

            try:
                self.map_window.addstr(
                    line_position_y,
                    line_position_x,
                    line_text[: max(0, window_width - 4)],
                    text_attribute,
                )
            except curses.error:
                pass

        self.map_window.refresh()
        self.message_log.render(self.message_window)

    def handle(self, action: str, pressed_key_code: int) -> UIAction:
        """
        Обрабатывает ввод и возвращает действие UI.

        Возвращает:
        - close_inventory - закрыть инвентарь
        - use_item - использовать выбранный предмет
        - noop - ничего не делать
        """
        if action == QUIT or self._is_inventory_key(pressed_key_code):
            return UIAction("close_inventory")

        if action == MOVE_UP and self.inventory_items:
            self.selected_item_index = (
                self.selected_item_index - 1
            ) % len(self.inventory_items)
            return UIAction("noop")

        if action == MOVE_DOWN and self.inventory_items:
            self.selected_item_index = (
                self.selected_item_index + 1
            ) % len(self.inventory_items)
            return UIAction("noop")

        if self._is_enter_key(pressed_key_code) and self.inventory_items:
            selected_item = self.inventory_items[
                self.selected_item_index
            ]
            return UIAction("use_item", selected_item)

        digit_actions = {
            SELECT_ITEM_0, SELECT_ITEM_1, SELECT_ITEM_2, SELECT_ITEM_3, SELECT_ITEM_4,
            SELECT_ITEM_5, SELECT_ITEM_6, SELECT_ITEM_7, SELECT_ITEM_8, SELECT_ITEM_9
        }

        if action in digit_actions and self.inventory_items:
            num = int(action.split("_")[-1])

            has_unequip = (
                isinstance(self.inventory_items[0], dict)
                and self.inventory_items[0].get("unequip") is True
            )

            if has_unequip:
                idx = num
            else:
                if num == 0:
                    return UIAction("noop")
                idx = num - 1

            if 0 <= idx < len(self.inventory_items):
                return UIAction("use_item", self.inventory_items[idx])
            return UIAction("noop")

        if action == NOOP:
            return UIAction("noop")

        return UIAction("noop")

    def _is_enter_key(self, key_code: int) -> bool:
        """Проверяет что нажат Enter (10, 13 - варианты кодов в curses)"""
        return key_code in (10, 13, curses.KEY_ENTER)

    def _is_inventory_key(self, key_code: int) -> bool:
        """Проверяет клавишу открытия/закрытия инвентаря"""
        if 0 <= key_code < 256:
            pressed_character = chr(key_code)
            return pressed_character == "i" or pressed_character == "I"
        return False

    def _format_item_line(self, index, inventory_item) -> str:
        """
        Преобразует элемент инвентаря в строку для отображения.
        
        Поддерживает dict с полями name/quantity, tuple(name, quantity)
        и произвольные значения.
        """
        if isinstance(inventory_item, dict):
            item_name = inventory_item.get("name", "item")
            item_quantity = inventory_item.get("quantity", 1)
            line = f"{index + 1}) {item_name} x{item_quantity}"
            stats_short = inventory_item.get("stats_short")
            if stats_short:
                line += f" ({stats_short})"
            return line

        if isinstance(inventory_item, tuple):
            if len(inventory_item) == 1:
                return f"{index + 1}) {inventory_item[0]}"
            if len(inventory_item) >= 2:
                return f"{index + 1}) {inventory_item[0]} x{inventory_item[1]}"

        return f"{index + 1}) {str(inventory_item)}"
