from src.domain.model.model import Game
from src.datasource.mapper.mapper import from_entity, to_entity
from src.datasource.repository.storage import GameStorage
import copy

class GameRepository:

    def __init__(self, storage: GameStorage=None):
        self.storage = storage

    def save_game(self, game_domain: Game, message: str = ""):
        entity = to_entity(game_domain, str(game_domain.UUID), message)
        entity.message = message
        if self.storage:
            self.storage.save(entity.UUID, entity)


    def get_game(self, game_id: str):
        if self.storage:
            entity = self.storage.get(game_id)
            if entity:
                entity_copy = copy.deepcopy(entity)
                return from_entity(entity_copy)
        return None, ""


if __name__ == "__main__":
    from domain.service import get_best_turn

    game = Game()
    game_rep = GameRepository()
    for _ in range(4):
        cell = get_best_turn(game, 0)
        print(f"компьютер выбрал поле {cell[0]} и {cell[1]}")
        game.field[cell[0]][cell[1]] = 0
        cell = get_best_turn(game, 1)
        game.field[cell[0]][cell[1]] = 1
        print(f"компьютер выбрал поле {cell[0]} и {cell[1]}")

    cell = get_best_turn(game, 0)
    print(f"компьютер выбрал поле {cell[0]} и {cell[1]}")
    game.field[cell[0]][cell[1]] = 0