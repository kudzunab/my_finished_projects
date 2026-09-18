"""
Основной экран игры.

Отвечает за отображение уровня, обработку ввода игрока
и взаимодействие с UI-виджетами.
"""
import curses

from src.presentation.render.renderer import render_map
from src.presentation.render.fog import compute_fog
from src.presentation.widgets.message_log import MessageLog
from src.presentation.widgets.statusbar import StatusBar
from src.presentation.input.keymap import (
    QUIT,
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    USE_WEAPON,
    USE_FOOD,
    USE_ELIXIR,
    USE_SCROLL,
    SAVE_GAME,
)
from src.presentation.widgets.inventory import InventoryWidget
from src.domain.entities.entities import (
    Item,
    ItemType,
    Level,
    Player,
    Position,
    StatType,
    Directions,
)
from src.presentation.adapters.level_to_view import build_view_state
from src.presentation.adapters.save_game_adapter import save_current_game
from src.domain.generation.generator import generate_next_level
from src.domain.characters.character_move import (
    move_character_by_direction,
    check_outside_border,
    check_unoccupied_level,
    get_room_number,
)
from src.domain.characters import take_item
from src.domain.characters import find_nearest_monsters, check_player_attack, all_monsters_moving
from src.domain.characters import attack_procedure, remove_dead_monsters, check_battles
from src.domain.characters import BattlePicture
from src.domain.characters import update_the_buff_state

ACTION_TO_DIRECTION = {
    MOVE_UP: Directions.FORWARD,
    MOVE_DOWN: Directions.BACK,
    MOVE_LEFT: Directions.LEFT,
    MOVE_RIGHT: Directions.RIGHT,
}

FINAL_LEVEL_NUM = 21


class GameScreen:
    """
    Экран игрового процесса.

    Инициализирует уровень через доменный генератор, строит представление для
    рендера, рисует карту и обрабатывает перемещения/команды игрока.
    """

    def __init__(
        self,
        map_window: "curses.window",
        status_window: "curses.window",
        message_window: "curses.window",
        player: Player | None = None,
        level: Level | None = None,
    ) -> None:
        """Создает игровой экран и генерирует стартовый уровень"""
        self.map_window = map_window
        self.status_window = status_window
        self.message_window = message_window

        self.message_log = MessageLog()
        self.status_bar = StatusBar()

        self.window_height, self.window_width = self.map_window.getmaxyx()

        self.temp_pos = Position()
        self.battle_picture = BattlePicture()
        self.nearest_monsters = []

        if player is not None and level is not None:
            self.player = player
            self.level = level
        else:
            self.player = Player()
            self.level = Level()
            generate_next_level(self.level, self.player, self.temp_pos)

        self.seen_rooms = [False] * len(self.level.rooms)

        self._refresh_view_state()

        start_room_idx = get_room_number(self.player.position, self.level)
        if start_room_idx != -1:
            self.seen_rooms[start_room_idx] = True

        inner_height = len(self.grid)
        inner_width = len(self.grid[0])
        self.visible_mask = [[True] * inner_width for _ in range(inner_height)]
        self.seen_mask = [[False] * inner_width for _ in range(inner_height)]

        self.message_log.set("Keys: q=quit, WASD=move, h/j/k/e=inventory")

        self.inventory_widget = None
        self.turn_counter = 0
        self.open_inventory_type = None
        self.is_player_dead = False
        self.death_reason = ""
        self.is_player_won = False
        self.is_other_story_exit = self.level.level_num > FINAL_LEVEL_NUM
        if self.is_other_story_exit:
            self.message_log.set("Saving attempt is outside the story. q / Enter — exit.")

    def _draw_other_story_screen(self) -> None:
        """Сохранение с level_num > 21 (например 22 в JSON): шуточный экран, без игры."""
        self._refresh_view_state()
        self.status_bar.render(self.status_window, self.player_status)
        self.map_window.erase()
        self.map_window.box()
        height, width = self.map_window.getmaxyx()

        lines = [
            "Друг, это уже совсем другая история.",
            "Нажми q или Enter для выхода в меню.",
        ]

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

        row0 = max(2, (height - len(lines) - 3) // 2)
        put(row0, "???", curses.A_BOLD)
        for i, line in enumerate(lines, start=1):
            put(row0 + i, line)

        self.map_window.refresh()
        self.message_log.render(self.message_window)

    def _refresh_view_state(self) -> None:
        """Обновляет view state из domain (level, player)"""
        vs = build_view_state(self.level, self.player)
        self.grid = vs.grid
        self.items = vs.items
        self.doors = vs.doors
        self.monsters = vs.monsters
        self.player_status = vs.player_status
        self.player_y = vs.player_y
        self.player_x = vs.player_x

    def draw(self) -> None:
        """Отрисовывает игру или активный виджет"""
        if self.inventory_widget is not None:
            self.inventory_widget.draw()
            return

        if self.is_other_story_exit:
            self._draw_other_story_screen()
            return

        self._refresh_view_state()
        self.status_bar.render(self.status_window, self.player_status)

        rooms_for_fog = []
        for room in self.level.rooms:
            pos = room.position
            rooms_for_fog.append({"x": pos.x, "y": pos.y, "w": pos.dx, "h": pos.dy})

        self.visible_mask = compute_fog(
            self.grid,
            rooms_for_fog,
            self.seen_rooms,
            self.player_x,
            self.player_y,
            self.seen_mask,
        )

        render_map(
            self.map_window,
            self.grid,
            self.player_y,
            self.player_x,
            self.items,
            self.monsters,
            self.visible_mask,
            self.seen_mask,
        )

        self.message_log.render(self.message_window)

    def _handle_inventory_widget(self, action, pressed_key_code) -> bool | None:
        if self.inventory_widget is None:
            return None

        user_interface_action = self.inventory_widget.handle(action, pressed_key_code)

        if user_interface_action.action_type == "close_inventory":
            self.inventory_widget = None
            self.message_log.set("Inventory closed")
            return True

        if user_interface_action.action_type == "use_item":
            payload = user_interface_action.action_payload
            self.inventory_widget = None

            if payload.get("unequip"):
                if self.player.put_weapon_to_inventory(self.level):
                    self.message_log.set("Weapon dropped on the floor")
                else:
                    self.message_log.set("Impossible to drop")
                self.turn_counter += 1
                return True

            item = payload.get("item")
            if item is None:
                self.message_log.set("Invalid selection")
                return True

            item_type = self.open_inventory_type

            if item_type == ItemType.WEAPON:
                can_equip = True
                if self.player.weapon.type != ItemType.NONE:
                    can_equip = self.player.put_weapon_to_inventory(self.level)
                if can_equip:
                    if self.player.equipt_weapon(item):
                        self.message_log.set(f"Equipped {item.name}")
                    else:
                        self.message_log.set("Failed to equip")
                else:
                    self.message_log.set("Impossible to drop here")

            elif item_type in (ItemType.FOOD, ItemType.ELIXIR, ItemType.SCROLL):
                if self.player.use_item(item, self.turn_counter):
                    self.message_log.set(f"Used {item.name}")
                else:
                    self.message_log.set(f"Could not use {item.name}")

            self.turn_counter += 1
            return True
        return True

    def _handle_log_scroll(self, pressed_key_code) -> bool | None:
        if pressed_key_code == curses.KEY_UP:
            self.message_log.scroll_up()
            return True

        if pressed_key_code == curses.KEY_DOWN:
            self.message_log.scroll_down()
            return True

        return None

    def _handle_global_action(self, action) -> bool | None:
        if action == QUIT:
            if not self.is_other_story_exit and not self.is_player_dead:
                save_current_game(self.player, self.level)
            return False

        if action == SAVE_GAME:
            is_saved = save_current_game(self.player, self.level)
            if is_saved:
                self.message_log.set("Game saved")
            else:
                self.message_log.set("Failed to save game")
            return True

        return None

    def _handle_inventory_open(self, action) -> bool | None:
        if action not in (USE_WEAPON, USE_FOOD, USE_ELIXIR, USE_SCROLL):
            return None

        item_type = {
            USE_WEAPON: ItemType.WEAPON,
            USE_FOOD: ItemType.FOOD,
            USE_ELIXIR: ItemType.ELIXIR,
            USE_SCROLL: ItemType.SCROLL,
        }[action]

        items = self.get_inventory_items_by_type(item_type)

        if item_type == ItemType.WEAPON and self.player.weapon.type == ItemType.WEAPON:
            items = [{"name": "Take off weapon", "unequip": True}] + items

        label = self._get_subtypeinventory(item_type)

        if not items:
            self.message_log.set(f"No {label} in inventory")
            return True

        self.open_inventory_type = item_type
        self.inventory_widget = InventoryWidget(
            self.map_window,
            self.status_window,
            self.message_window,
            items,
        )
        self.message_log.set(f"Inventory opened for {label}")
        return True

    @staticmethod
    def _format_death_reason(results: list | None) -> str:
        """Строка для экрана смерти (последний удар в бою)."""
        if not results:
            return "You have been defeated."
        try:
            _gold_or_flag, damage, m_type = results[0]
        except (IndexError, TypeError, ValueError):
            return "You have been defeated."
        try:
            label = m_type.name.replace("_", " ").title()
        except AttributeError:
            label = "Unknown foe"
        if isinstance(damage, int) and damage > 0:
            return f"Slain by {label} ({damage} damage)."
        return f"Slain by {label}."

    def _handle_game_turn(self, action) -> bool:
        """Обработка хода игрока"""
        direction = ACTION_TO_DIRECTION.get(action)
        if direction is None:
            return True

        #======================================================================================
        #== Нужно для активации эликсиров, если не проверять, то они не смогут расходоваться ==
        #======================================================================================
        expired = update_the_buff_state(self.player, self.turn_counter)
        for buff in expired:
            self.message_log.set(f"The elixir's {buff.name} effect has worn off.")

        player_make_turn = False
        self.temp_pos.copy_position(self.player.position)
        move_character_by_direction(direction, self.temp_pos)

        self.nearest_monsters = find_nearest_monsters(self.player, self.level)
        is_hit, current_battle = check_player_attack(
            self.player,
            direction,
            self.battle_picture,
            self.level,
            self.temp_pos,
        )

        can_move = check_outside_border(self.temp_pos, self.level) and check_unoccupied_level(
            self.temp_pos,
            self.level,
            self.player,
        )

        if current_battle and is_hit:
            results = attack_procedure(self.player, self.battle_picture, current_battle, 0)
            if results:
                _, damage, m_type = results[0]
                if damage > 0:
                    self.message_log.set(f"You attack {m_type.name} and make damage {damage}")
                elif damage == -1:
                    self.message_log.set("Player is resting")
                elif damage == 0:
                    self.message_log.set(f"Your attack on {m_type.name} missed!")
            player_make_turn = True

        elif can_move:
            self.player.change_poz(self.temp_pos)
            if (
                self.player.position.x == self.level.end_position.x
                and self.player.position.y == self.level.end_position.y
            ):
                if self.level.level_num == FINAL_LEVEL_NUM:
                    self.is_player_won = True
                    return False
                generate_next_level(self.level, self.player, self.temp_pos)
                self._refresh_view_state()
                save_current_game(self.player, self.level)

                inner_height = len(self.grid)
                inner_width = len(self.grid[0])

                self.visible_mask = [[False] * inner_width for _ in range(inner_height)]
                self.seen_mask = [[False] * inner_width for _ in range(inner_height)]
                self.seen_rooms = [False] * len(self.level.rooms)

                start_room_idx = get_room_number(self.player.position, self.level)
                if start_room_idx != -1:
                    self.seen_rooms[start_room_idx] = True

                self.battle_picture = BattlePicture()
                self.nearest_monsters = []

                self.message_log.set(f"Level {self.level.level_num}")
                return True

            find_item, is_inv_full = take_item(self.player, self.level)
            if find_item:
                self.message_log.set(f"You found {find_item.name}")
            elif is_inv_full:
                self.message_log.set("Inventory is full")

            player_make_turn = True

        else:
            self.message_log.set("Can't move there")

        if player_make_turn:
            self.turn_counter += 1
            if self.turn_counter % 21 == 0:
                if self.player.stats.health < self.player.regen_limit:
                    self.player.stats.health += 1

            self.nearest_monsters = find_nearest_monsters(self.player, self.level)
            check_battles(self.battle_picture, self.nearest_monsters)
            for battle in self.battle_picture.battles:
                if battle.is_finish:
                    continue

                results = attack_procedure(self.player, self.battle_picture, battle, 1)
                if results:
                    _, damage, m_type = results[0]
                    if damage > 0:
                        self.message_log.set(f"{m_type.name} hits you for {damage}!")
                    elif damage == -1:
                        self.message_log.set(f"{m_type.name} is resting")
                    else:
                        self.message_log.set(f"{m_type.name} attack on you missed!!")

                if not self.player.is_alive:
                    self.is_player_dead = True
                    self.death_reason = self._format_death_reason(results)
                    return False

            remove_dead_monsters(self.level)
            all_monsters_moving(self.player, self.level, self.temp_pos)
            self.nearest_monsters = find_nearest_monsters(self.player, self.level)
            check_battles(self.battle_picture, self.nearest_monsters)

        return True

    def handle(self, action, pressed_key_code) -> bool:
        """Управление вызовами"""
        if self.is_other_story_exit:
            if action == QUIT or pressed_key_code in (10, 13, curses.KEY_ENTER):
                return False
            return True

        result = self._handle_inventory_widget(action, pressed_key_code)
        if result is not None:
            return result

        result = self._handle_log_scroll(pressed_key_code)
        if result is not None:
            return result

        result = self._handle_global_action(action)
        if result is not None:
            return result

        result = self._handle_inventory_open(action)
        if result is not None:
            return result

        return self._handle_game_turn(action)

    _STAT_SHORT: dict[int, str] = {
        StatType.HEALTH: "HP",
        StatType.AGILITY: "AGI",
        StatType.STRENGTH: "STR",
    }

    @classmethod
    def _consumable_bonus_label(cls, item: Item) -> str | None:
        """+N HP/AGI/STR по subtype (StatType) и value — для эликсира и свитка."""
        try:
            st = StatType(int(item.subtype))
        except (ValueError, TypeError):
            return None
        label = cls._STAT_SHORT.get(st)
        if label is None:
            return None
        return f"+{int(item.value)} {label}"

    @staticmethod
    def show_food_stat(item: Item) -> str:
        """Короткая подпись для еды в инвентаре, например +5 HP."""
        if item.type != ItemType.FOOD:
            return ""
        return f"+{int(item.health)} HP"

    @classmethod
    def show_elixir_stat(cls, item: Item) -> str:
        """Эликсир: бонус по стату и длительность, например +7 STR (45s)."""
        if item.type != ItemType.ELIXIR:
            return ""
        core = cls._consumable_bonus_label(item)
        if not core:
            return ""
        dur = int(item.duration) if getattr(item, "duration", 0) else 0
        if dur > 0:
            return f"{core} ({dur}s)"
        return core

    @classmethod
    def show_scroll_stat(cls, item: Item) -> str:
        """Свиток: бонус по стату, например +5 AGI."""
        if item.type != ItemType.SCROLL:
            return ""
        return cls._consumable_bonus_label(item) or ""

    @staticmethod
    def show_weapon_stat(item: Item) -> str:
        """Короткая подпись для оружия в инвентаре, например +8 STR."""
        if item.type != ItemType.WEAPON:
            return ""
        return f"+{int(item.strength)} STR"

    @staticmethod
    def _get_subtypeinventory(item_type: ItemType) -> str:
        if item_type == ItemType.FOOD:
            return "food"
        if item_type == ItemType.ELIXIR:
            return "elixir"
        if item_type == ItemType.SCROLL:
            return "scroll"
        if item_type == ItemType.WEAPON:
            return "weapon"
        if item_type == ItemType.TREASURE:
            return "treasure"
        return "unknown"

    def get_inventory_items_by_type(self, item_type: ItemType) -> list[dict]:
        """Возвращает список предметов заданного типа для отображения в InventoryWidget."""
        items = self.player.inventory.storage.get(item_type, [])
        result: list[dict] = []
        for item in items:
            row: dict = {
                "name": item.name,
                "quantity": 1,
                "item": item,
            }
            if item_type == ItemType.FOOD:
                row["stats_short"] = GameScreen.show_food_stat(item)
            elif item_type == ItemType.ELIXIR:
                row["stats_short"] = GameScreen.show_elixir_stat(item)
            elif item_type == ItemType.SCROLL:
                row["stats_short"] = GameScreen.show_scroll_stat(item)
            elif item_type == ItemType.WEAPON:
                row["stats_short"] = GameScreen.show_weapon_stat(item)
            result.append(row)
        return result
