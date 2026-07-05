from src.domain.model.model import Game
from src.datasource.model.model import GameEntity
from typing import Tuple
import copy
def to_entity(game: Game, game_id: str, message: str = "") -> GameEntity:
    return GameEntity(_id = str(game_id), field = copy.deepcopy(game.field),
                      turn = game.turn, message=message)

def from_entity(entity: GameEntity) -> Tuple[Game, str]:
    game_domain = Game(game_id=entity.UUID, field=copy.deepcopy(entity.field), turn=entity.turn)
    game_domain.snapshot = copy.deepcopy(entity.field)
    return game_domain, entity.message
