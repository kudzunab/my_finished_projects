import pytest, random

from src.domain.entities import Item, Dimension, MonsterType, HostilityType, MonsterType, StatType, ItemType
from src.domain.entities import Directions, Position, Character, MonsterDict, Monster, ItemInRoom, ItemsInRoom
from src.domain.entities import Inventory, Buff, Buffs, Player, Room, Passage, Level, BaseParam, Const, Entity
from src.domain.generation import generate_next_level

@pytest.fixture
def player():
    p = Player()
    return p

@pytest.fixture
def position():
    p = Position()
    return p

@pytest.fixture
def level(player, position):
    l = Level()
    random.seed(0)
    generate_next_level(l, player, position)
    return l