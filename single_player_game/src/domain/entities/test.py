from dataclasses import dataclass
from typing import ClassVar, Dict
from src.domain.entities.entities import StatType


@dataclass
class BaseParam:
    """
    Базовые характеристики сущности (игрока или монстра).
    """

    max_health: float
    health: float
    agility: int
    strength: int

    STATS: ClassVar[Dict["StatType", str]] = {
        StatType.HEALTH: "health",
        StatType.HEALTH: "health",
        StatType.AGILITY: "agility",
        StatType.STRENGTH: "strength",
    }

    def is_alive(self) -> bool:
        """
        Проверка, жива ли сущность.
        """
        return self.health > 0

    def take_damage(self, damage: float) -> None:
        """
        Применение урона.
        """
        self.health -= damage

    def heal(self, value: float) -> None:
        """
        Восстановление здоровья.
        Не может превышать max_health.
        """
        self.health = min(self.max_health, self.health + value)

    def increase_max_health(self, value: float) -> None:
        """
        Увеличение максимального здоровья.
        По ТЗ при увеличении max_health текущее здоровье
        тоже увеличивается на ту же величину.
        """
        self.max_health += value
        self.health += value

    def increase_agility(self, value: int) -> None:
        """
        Увеличение ловкости.
        """
        self.agility += value

    def increase_strength(self, value: int) -> None:
        """
        Увеличение силы.
        """
        self.strength += value

    @classmethod
    def default_player(cls) -> "BaseParam":
        """
        Стартовые параметры игрока.
        """
        return cls(
            max_health=12.0,
            health=12.0,
            agility=1,
            strength=16,
        )

class Const:

    # ===== УРОВЕНЬ =====
    ROOMS_IN_WIDTH = 3
    ROOMS_IN_HEIGHT = 3
    ROOMS_NUMBERS = ROOMS_IN_WIDTH * ROOMS_IN_HEIGHT
    ROOM_NUMBER = ROOMS_NUMBERS

    MAX_PASSAGE_PARTS = 3
    MAX_PASSAGES_NUM = (ROOMS_NUMBERS - 1) * MAX_PASSAGE_PARTS

    REGION_WIDTH = 27
    REGION_HEIGHT = 10

    MIN_ROOM_WIDTH = 6
    MAX_ROOM_WIDTH = REGION_WIDTH - 2

    MIN_ROOM_HEIGHT = 5
    MAX_ROOM_HEIGHT = REGION_HEIGHT - 2

    LEVEL_NUM = 21

    # ===== НАПОЛНЕНИЕ =====
    MAX_CONSUMABLES_PER_ROOM = 3
    MAX_MONSTERS_PER_ROOM = 2
    MAX_PERCENT_FOOD_REGEN_FROM_HEALTH = 20
    LEVEL_UPDATE_DIFFICULTY = 10

    MIN_ELIXIR_DURATION_SECONDS = 30
    MAX_ELIXIR_DURATION_SECONDS = 60

    # ===== БОЕВЫЕ ПАРАМЕТРЫ =====
    INITIAL_HIT_CHANCE = 70
    STANDART_AGILITY = 50
    AGILITY_FACTOR = 0.3

    INITIAL_DAMAGE = 30
    STANDART_STRENGTH = 50
    STRENGTH_FACTOR = 0.3
    STRENGTH_ADDITION = 65

    SLEEP_CHANCE = 15
    MAX_HP_PART = 10

    LOOT_AGILITY_FACTOR = 0.2
    LOOT_HP_FACTOR = 0.5
    LOOT_STRENGTH_FACTOR = 0.5

    MAXIMUM_FIGHTS = 8
    PERCENTS_UPDATE_DIFFICULTY_MONSTERS = 2