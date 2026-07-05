from __future__ import annotations

from src.dto.entities import (
    Player, Level, BattleInfo, MapVisibility, GameState, SessionStats,
)
from src.dto.enums import GameAction, GameScene, ConsumableType
from interfaces.domain_interfaces import (
    ILevelGenerator, IMovementService, ICombatService, IConsumableService,
)
from src.interfaces.presentation_interfaces import (
    IPresentation, IMapRenderer, IScreenRenderer,
)
from src.interfaces.data_interfaces import IDataService
from src.controller.input_handler import map_key_to_action, ACTION_TO_DIRECTION
from src.controller.scene_manager import SceneManager

TOTAL_LEVELS = 21


class GameController:

    def __init__(
        self,
        presentation: IPresentation,
        map_renderer: IMapRenderer,
        screen_renderer: IScreenRenderer,
        level_generator: ILevelGenerator,
        movement: IMovementService,
        combat: ICombatService,
        consumables: IConsumableService,
        data_service: IDataService,
    ) -> None:
        self._ui = presentation
        self._map = map_renderer
        self._screens = screen_renderer
        self._gen = level_generator
        self._move = movement
        self._combat = combat
        self._consumables = consumables
        self._data = data_service
        self._scene = SceneManager()

        self._player = Player()
        self._level = Level()
        self._visibility = MapVisibility()
        self._battles: list[BattleInfo] = []
        self._stats = SessionStats()
        self._message_top = ""
        self._message_mid = ""

    # === Точка входа ===

    def run(self) -> None:
        self._ui.init()
        try:
            self._scene.transition_to(GameScene.SPLASH)
            self._run_splash()
            self._scene.transition_to(GameScene.MAIN_MENU)
            self._run_main_menu()
        finally:
            self._ui.shutdown()

    # === Заставка ===

    def _run_splash(self) -> None:
        self._screens.show_splash()

    # === Главное меню ===

    def _run_main_menu(self) -> None:
        selected = 0
        menu_size = 4  # Новая игра, Загрузить, Рекорды, Выход

        while True:
            self._screens.show_menu(selected)
            key = self._ui.get_input()
            action = map_key_to_action(key)

            if action == GameAction.MOVE_UP:
                selected = max(0, selected - 1)
            elif action == GameAction.MOVE_DOWN:
                selected = min(menu_size - 1, selected + 1)
            elif action == GameAction.MENU_CONFIRM:
                if selected == 0:
                    self._start_new_game()
                    self._run_game_loop()
                elif selected == 1:
                    self._load_saved_game()
                    self._run_game_loop()
                elif selected == 2:
                    self._run_leaderboard()
                elif selected == 3:
                    return

    # === Инициализация игры ===

    def _start_new_game(self) -> None:
        self._player = Player()
        self._level = Level()
        self._visibility = MapVisibility()
        self._battles = []
        self._stats = SessionStats()
        self._gen.init_new_game(self._player, self._level)

    def _load_saved_game(self) -> None:
        state = self._data.load_game()
        if state is None:
            self._start_new_game()
            return
        self._player = state.player
        self._level = state.level
        self._visibility = state.visibility
        self._battles = state.battles if state.battles else []
        self._stats = state.stats

    # === Игровой цикл ===

    def _run_game_loop(self) -> None:
        self._scene.transition_to(GameScene.GAME)
        running = True

        while running:
            self._map.render_game(
                self._player, self._level, self._visibility,
                self._battles, self._message_top, self._message_mid,
            )
            self._message_top = ""
            self._message_mid = ""

            key = self._ui.get_input()
            action = map_key_to_action(key)

            if action == GameAction.ESCAPE:
                running = False
                continue

            if action in ACTION_TO_DIRECTION:
                self._process_movement(action)
            elif action == GameAction.USE_WEAPON:
                self._open_inventory(ConsumableType.WEAPON)
            elif action == GameAction.USE_FOOD:
                self._open_inventory(ConsumableType.FOOD)
            elif action == GameAction.USE_ELIXIR:
                self._open_inventory(ConsumableType.ELIXIR)
            elif action == GameAction.USE_SCROLL:
                self._open_inventory(ConsumableType.SCROLL)

            self._stats.treasures = self._player.backpack.treasures.value
            self._stats.level = self._level.level_num

            # Проверка смерти
            if self._combat.check_player_death(self._player):
                self._data.finalize_session(self._stats)
                self._data.reset_save()
                self._screens.show_death_screen()
                running = False
                continue

            # Проверка выхода с уровня
            if self._move.check_level_exit(self._player, self._level):
                if self._level.level_num >= TOTAL_LEVELS:
                    self._data.finalize_session(self._stats)
                    self._data.reset_save()
                    self._screens.show_win_screen()
                    running = False
                else:
                    self._visibility = MapVisibility()
                    self._gen.generate_next_level(self._level, self._player)
                    self._battles = []
                    self._save_current_state()

            if running:
                self._save_current_state()

    # === Обработка движения ===

    def _process_movement(self, action: GameAction) -> None:
        direction = ACTION_TO_DIRECTION[action]

        self._combat.update_fight_status(
            self._player, self._level, self._battles,
        )

        # Ход игрока: атака если в бою, иначе движение
        attacked_any = False
        for battle in self._battles:
            if battle.is_fight:
                did_attack = self._combat.process_player_attack(
                    self._player, battle, direction,
                )
                if did_attack:
                    attacked_any = True
                    self._stats.attacks_given += 1
                    if (
                        battle.enemy is not None
                        and battle.enemy.base_stats.health <= 0
                    ):
                        self._stats.enemies_killed += 1
                        loot = self._combat.calculate_loot(battle.enemy)
                        self._player.backpack.treasures.value += loot

        if not attacked_any:
            moved = self._move.move_player(
                self._player, self._level, direction,
            )
            if moved:
                self._stats.tiles_walked += 1
                pickup = self._consumables.check_pickup(
                    self._player, self._level,
                )
                if pickup is not None:
                    ctype, cname = pickup
                    self._message_top = f"You picked up {cname}!"

        # Ход монстров
        self._move.move_monsters(
            self._level, self._player, self._battles,
        )
        monster_results = self._combat.process_monster_attacks(
            self._player, self._battles,
        )
        for mname, did_hit in monster_results:
            if did_hit:
                self._stats.hits_taken += 1
                self._message_mid = f"{mname} hit you!"
            else:
                self._message_mid = f"{mname} missed!"

        self._consumables.check_buff_expiry(self._player)

    # === Инвентарь ===

    def _open_inventory(self, item_type: ConsumableType) -> None:
        backpack = self._player.backpack
        stat_names = {0: "health", 1: "agility", 2: "strength"}

        if item_type == ConsumableType.FOOD:
            items = [
                (f.name, f"+{f.to_regen} health") for f in backpack.foods
            ]
            label = "food"
            allow_zero = False
        elif item_type == ConsumableType.ELIXIR:
            items = [
                (e.name, f"+{e.increase} {stat_names[e.stat]} ({e.duration}s)")
                for e in backpack.elixirs
            ]
            label = "elixir"
            allow_zero = False
        elif item_type == ConsumableType.SCROLL:
            items = [
                (s.name, f"+{s.increase} {stat_names[s.stat]}")
                for s in backpack.scrolls
            ]
            label = "scroll"
            allow_zero = False
        elif item_type == ConsumableType.WEAPON:
            items = [
                (w.name, f"+{w.strength} strength") for w in backpack.weapons
            ]
            label = "weapon"
            allow_zero = True
        else:
            return

        if not items and not allow_zero:
            self._message_top = f"No {label} in backpack!"
            return

        self._screens.show_inventory(self._player, label, items, allow_zero)
        key = self._ui.get_input()
        action = map_key_to_action(key)

        index = self._action_to_item_index(action)
        if index is None:
            return

        if item_type == ConsumableType.WEAPON and index == 0:
            index = -1  # снять оружие

        room = self._move.find_current_room(self._player, self._level)
        result = self._consumables.use_consumable(
            self._player, item_type, index, room,
        )
        if result.success:
            self._message_top = result.message
            if item_type == ConsumableType.FOOD:
                self._stats.food_eaten += 1
            elif item_type == ConsumableType.ELIXIR:
                self._stats.elixirs_drunk += 1
            elif item_type == ConsumableType.SCROLL:
                self._stats.scrolls_read += 1

    @staticmethod
    def _action_to_item_index(action: GameAction) -> int | None:
        mapping = {
            GameAction.SELECT_ITEM_0: 0,
            GameAction.SELECT_ITEM_1: 1,
            GameAction.SELECT_ITEM_2: 2,
            GameAction.SELECT_ITEM_3: 3,
            GameAction.SELECT_ITEM_4: 4,
            GameAction.SELECT_ITEM_5: 5,
            GameAction.SELECT_ITEM_6: 6,
            GameAction.SELECT_ITEM_7: 7,
            GameAction.SELECT_ITEM_8: 8,
            GameAction.SELECT_ITEM_9: 9,
        }
        return mapping.get(action)

    # === Сохранение ===

    def _save_current_state(self) -> None:
        state = GameState(
            player=self._player,
            level=self._level,
            visibility=self._visibility,
            battles=self._battles,
            stats=self._stats,
        )
        self._data.save_game(state)

    # === Таблица рекордов ===

    def _run_leaderboard(self) -> None:
        entries = self._data.load_leaderboard()
        self._screens.show_leaderboard(entries)
