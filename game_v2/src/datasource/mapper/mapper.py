from src.domain.model.model import Game
from src.datasource.model.model import GameEntity
from typing import Tuple
import copy
def to_entity(game: Game, game_id: str, message: str = "") -> GameEntity:
    return GameEntity(_id = str(game_id), field = copy.deepcopy(game.field),
                      turn = game.turn, message=message, status=game.status, player1_uuid=game.player1_uuid,
                      player2_uuid = game.player2_uuid, current_player_uuid = game.current_player_uuid)

def from_entity(entity: GameEntity) -> Tuple[Game, str]:
    game_domain = Game(game_id=entity.UUID, field=copy.deepcopy(entity.field),
                       turn=entity.turn, game_type=entity.game_type, status = entity.status,
                       player1_uuid=entity.player1_uuid, player2_uuid = entity.player2_uuid,
                       current_player_uuid = entity.current_player_uuid,
                       player1_symbol = entity.player1_symbol, player2_symbol = entity.player2_symbol)

    game_domain.snapshot = copy.deepcopy(entity.field)
    return game_domain, entity.message
