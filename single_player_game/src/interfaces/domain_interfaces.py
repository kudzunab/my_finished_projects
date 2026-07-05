from __future__ import annotations

from abc import ABC, abstractmethod

from src.dto.entities import (
    Player, Level, Monster, BattleInfo, Room, UseItemResult,
)
from src.dto.enums import Direction, ConsumableType


class ILevelGenerator(ABC):

    @abstractmethod
    def generate_next_level(self, level: Level, player: Player) -> None:
        """Увеличить level_num, сгенерировать комнаты, коридоры, монстров,
        предметы, разместить игрока и выход. Мутирует level на месте."""
        ...

    @abstractmethod
    def init_new_game(self, player: Player, level: Level) -> None:
        """Задать начальные характеристики игрока и сгенерировать уровень 1."""
        ...


class IMovementService(ABC):

    @abstractmethod
    def move_player(
        self, player: Player, level: Level, direction: Direction
    ) -> bool:
        """Переместить игрока на одну клетку в заданном направлении.
        Вернуть True, если игрок действительно переместился."""
        ...

    @abstractmethod
    def move_monsters(
        self, level: Level, player: Player, battles: list[BattleInfo]
    ) -> None:
        """Переместить всех монстров согласно их паттернам движения."""
        ...

    @abstractmethod
    def check_level_exit(self, player: Player, level: Level) -> bool:
        """Вернуть True, если игрок стоит на выходе с уровня."""
        ...

    @abstractmethod
    def find_current_room(
        self, player: Player, level: Level
    ) -> Room | None:
        """Вернуть комнату, в которой находится игрок, или None."""
        ...


class ICombatService(ABC):

    @abstractmethod
    def update_fight_status(
        self, player: Player, level: Level, battles: list[BattleInfo]
    ) -> None:
        """Проверить новые контакты, инициировать бои.
        Удалить мёртвых монстров и завершённые бои."""
        ...

    @abstractmethod
    def process_player_attack(
        self, player: Player, battle: BattleInfo, direction: Direction
    ) -> bool:
        """Попытка атаки игрока. Вернуть True, если атака была совершена.
        Мутирует здоровье врага в battle."""
        ...

    @abstractmethod
    def process_monster_attacks(
        self, player: Player, battles: list[BattleInfo]
    ) -> list[tuple[str, bool]]:
        """Все активные враги атакуют игрока.
        Вернуть список (имя_типа_монстра, попал_ли)."""
        ...

    @abstractmethod
    def check_player_death(self, player: Player) -> bool:
        """Вернуть True, если здоровье игрока <= 0."""
        ...

    @abstractmethod
    def calculate_loot(self, monster: Monster) -> int:
        """Вернуть стоимость сокровищ за убийство этого монстра."""
        ...


class IConsumableService(ABC):

    @abstractmethod
    def check_pickup(
        self, player: Player, level: Level
    ) -> tuple[ConsumableType, str] | None:
        """Проверить наличие предметов на позиции игрока.
        Автоподбор, если в рюкзаке есть место.
        Вернуть (тип, имя) если подобрано, иначе None."""
        ...

    @abstractmethod
    def use_consumable(
        self,
        player: Player,
        item_type: ConsumableType,
        index: int,
        current_room: Room | None,
    ) -> UseItemResult:
        """Использовать предмет по индексу из рюкзака.
        Для оружия index=-1 означает снять оружие.
        current_room нужен для сброса старого оружия на пол."""
        ...

    @abstractmethod
    def check_buff_expiry(self, player: Player) -> None:
        """Удалить истёкшие временные баффы.
        Если здоровье упало до <=0, установить его в 1."""
        ...
