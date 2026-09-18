"""
Символы и цветовые пары для отображения сущностей.
"""

from src.domain.entities.entities import ItemType, MonsterType



ENEMY_CHAR_TO_COLOR_PAIR_ID: dict[str, int] = {
    "z": 1,  # Zombie -> green
    "v": 2,  # Vampire -> red
    "g": 3,  # Ghost -> white
    "O": 4,  # Ogre -> yellow
    "s": 3,  # Snake-mage -> white
    "m": 3,  # Mimic -> white
}

MONSTER_TYPE_TO_CHAR: dict[MonsterType, str] = {
    MonsterType.ZOMBIE: "z",
    MonsterType.VAMPIRE: "v",
    MonsterType.GHOST: "g",
    MonsterType.OGRE: "O",
    MonsterType.SNAKE: "s",
    MonsterType.MIMIC: "m",
}

ITEMS_TILES: dict[ItemType, str] = {
    ItemType.FOOD: "%",
    ItemType.ELIXIR:"!",
    ItemType.SCROLL: "?",
    ItemType.WEAPON: "/",
    ItemType.TREASURE: "*",
}
