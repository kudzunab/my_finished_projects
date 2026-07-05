"""
    python3 -m venv .my_env
    source .my_env/bin/activate

"""

import pytest
import random
import os
"""
deactivate
rm -rf .my_env
python3 -m venv .my_env
source .my_env/bin/activate
pip install pytest

запуск из корня:
PYTHONPATH=. pytest

либо так:
python3 -m pytest src/unit_tests
"""

from src.domain.entities import MonsterType
from src.domain.entities import Room, Level
"""
    rm -rf .my_env && python3 -m venv .my_env
    pip install pytest
    python3 -m pytest -s unit_tests/tests_kudzunab.py
"""

def test_rooms_generator(level):
    results = [[7, 3, 18, 5], [31, 1, 22, 8], [57, 3, 21, 6], [10, 11, 10, 6], [28, 12, 25, 6], [57, 12, 9, 7],
               [1, 22, 23, 7], [37, 23, 16, 6], [58, 21, 21, 7]]

    for i in range(len(level.rooms)):
        assert level.rooms[i].position.x == results[i][0]
        assert level.rooms[i].position.y == results[i][1]
        assert level.rooms[i].position.dx == results[i][2]
        assert level.rooms[i].position.dy == results[i][3]

    print("Checked test 1")

def test_passage_generator(level):
    result = [
    [[8, 9, 1, 1], [8, 11, 1, 1]],
    [[15, 15, 1, 1], [45, 15, 1, 1]],
    [[64, 7, 1, 1], [64, 11, 1, 1]],
    [[45, 16, 1, 1], [40, 21, 1, 1]],
    [[26, 24, 1, 1], [28, 24, 1, 1]],
    [[49, 6, 1, 1], [55, 6, 1, 1]],
    [[49, 8, 1, 1], [49, 13, 1, 1]],
    [[70, 15, 1, 1], [72, 21, 1, 1]]
    ]
    for i in range(len(level.passages)):
        passage = level.passages[i]
        assert passage.entrance.x, result[i][0][0]
        assert passage.entrance.y, result[i][0][1]
        assert passage.entrance.dx, result[i][0][2]
        assert passage.entrance.dy, result[i][0][3]
        assert passage.exit.x, result[i][1][0]
        assert passage.exit.y, result[i][1][1]
        assert passage.exit.dx, result[i][1][2]
        assert passage.exit.dy, result[i][1][3]

    print("Checked test 2")

def test_monsters(level):
    for room in level.rooms:
        for monster in room.monsters:
            assert monster.stats.health > 0  # Живой
            assert 0 <= monster.position.x <= 80  # В пределах экрана
            assert monster.type in MonsterType  # Существующий тип

    print("Checked test 3")

def test_consumables(level):
    for i in range(len(level.rooms)):
        room = level.rooms[i]
        for key in room.items.storage:
            for item in room.items.storage[key]:
                print(i, item.item.type, item.item.name, item.position.x, item.position.y)
    assert True

def test_passage(level):
    res = [
        [[5,40], [5,41], [5,42], [6,40], [7,40], [8,40], [9,40], [10,40], [11,40],
         [12,40], [13,40], [14,40], [15,40]],
        [[26,45], [26,46], [26,47], [26,48], [26,49], [26,50], [26,51], [26,52],
         [26,53], [26,54], [26,55], [26,56], [26,57], [26,58], [26,59], [26,60],
         [26,61], [26,62], [26,63], [26,64], [26,65], [26,66], [26,67], [26,68],
         [24,68], [25,68]],
        [[15,61], [15,62], [15,63], [15,64], [15,65], [15,66], [15,67], [15,68],
         [16,68], [17,68], [18,68], [19,68], [20,68], [21,68], [22,68], [23,68],
         [24,68]],
        [[14,12], [14,13], [14,14], [14,15], [15,12], [16,12], [17,12], [18,12],
         [19,12], [20,12], [21,12], [22,12], [23,12], [24,12], [25,12]],
        [[14,15], [14,16], [14,17], [14,18], [14,19], [14,20], [14,21], [14,22],
         [14,23], [14,24], [14,25], [14,26], [14,27], [14,28], [14,29], [14,30],
         [14,31], [14,32], [14,33], [14,34], [14,35], [14,36], [14,37], [14,38],
         [14,39], [14,40], [15,40]],
        [[15,40], [15,41], [15,42], [15,43], [15,44], [15,45], [15,46], [15,47],
         [15,48], [15,49], [15,50], [15,51], [15,52], [15,53], [15,54], [15,55],
         [15,56], [15,57], [15,58], [15,59], [15,60], [15,61]],
        [[5,15], [5,16], [6,15], [7,15], [8,15], [9,15], [10,15], [11,15], [12,15],
         [13,15], [14,15]],
        [[5,42], [5,43], [5,44], [5,45], [5,46], [5,47], [5,48], [5,49], [5,50],
         [5,51], [5,52], [5,53], [5,54], [5,55], [5,56], [5,57], [5,58], [5,59],
         [5,60], [5,61], [5,62], [5,63], [5,64], [5,65], [5,66], [5,67], [6,67]]
    ]
    for i in range(len(level.passages)):
        passage = level.passages[i]
        #print("new_passage")
        for j in range(len(passage.passage)):
            point = passage.passage[j]
            assert res[i][j][0] == point.y
            assert res[i][j][1] == point.x
            #print("[", point.y,',', point.x, "], ", sep = "", end = "")
        #print("and_passage")
    print("Checked test 4")

def test_level_rooms_save_load():
    lvl = Level()
    room1 = Room(1)
    room1.position.x = 10
    lvl.rooms.append(room1)

    data = lvl.to_dict()

    new_lvl = Level()
    new_lvl.from_dict(data)

    assert len(new_lvl.rooms) == 1
    assert isinstance(new_lvl.rooms[0], Room)
    assert new_lvl.rooms[0].room_num == 1
    assert new_lvl.rooms[0].position.x == 10
