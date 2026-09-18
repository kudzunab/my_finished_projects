import os, pathlib
import json

#DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
#filename = os.path.join(DEFAULT_DATA_DIR, "save.json")

def return_path(_my_file):
    try:
        _path = pathlib.Path(__file__).resolve().parent
    except NameError:
        _path = pathlib.Path.cwd()
    return _path.joinpath(_my_file).resolve()

filename = return_path("save.json")

def load_game(_filename=filename):
    from src.domain.entities import Player
    from src.domain.entities import Level, MonsterType
    from src.domain.characters import simple_pattern, pattern_ogr, pattern_ghost
    if not os.path.exists(_filename):
        return None, None

    try:
        with open(_filename, "r", encoding='utf-8') as file:
            data = json.load(file)

        player = Player()
        player.from_dict(data["player"])

        level = Level()
        level.from_dict(data["level"])

        for room in level.rooms:
            for monster in room.monsters:
                if monster.type in [MonsterType.VAMPIRE, MonsterType.ZOMBIE, MonsterType.SNAKE]:
                    monster.pattern = simple_pattern
                elif monster.type == MonsterType.GHOST:
                    monster.pattern = pattern_ghost
                elif monster.type == MonsterType.OGRE:
                    monster.pattern = pattern_ogr
                elif monster.type == MonsterType.MIMIC:
                    monster.pattern = None
                else:
                    #вызываем исключение, так как такое нельзя пускать в игру
                    raise ValueError(f"Unknown monster type: {monster.type}")

        return player, level

    except json.JSONDecodeError:
        # Файл поврежден или пуст (невалидный JSON)
        return None, None

    except KeyError:
        # В JSON нет ключа "player" или "level"
        return None, None

    except (TypeError, ValueError):
        # Ошибки типов данных внутри from_dict
        return None, None

    except (OSError, PermissionError):
        # Ошибка доступа к файлу на уровне системы
        return None, None

    except (ImportError, AttributeError):
        # Если в characters.py больше нет нужного паттерна
        return None, None

"""
    # Сохранение (где-то в handle или меню)
    save_game(self.player, self.level)

    # Загрузка
    new_player, new_level = load_game()
    if new_player:
        self.player = new_player
        self.level = new_level
"""