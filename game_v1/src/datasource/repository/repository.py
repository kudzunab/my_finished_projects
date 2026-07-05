from src.domain.model.model import Game, Status, GameType
from src.datasource.mapper.mapper import from_entity, to_entity
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from src.datasource.model import GameEntity
from src.datasource.model.model import GameBase, UsersInfo
from sqlalchemy.orm.attributes import flag_modified
import copy

class GameRepository:

    def __init__(self, session_factory):
        self.session_factory=session_factory

    def save_game(self, game_domain: Game, message: str = ""):
        entity = to_entity(game_domain, str(game_domain.UUID), message)  # GameBase
        entity.message = message
        try:
            with self.session_factory() as session:
                with session.begin():
                    current_status=game_domain.status.value if hasattr(game_domain.status, 'value'
                                                                       ) else game_domain.status
                    field_copy=copy.deepcopy(entity.field)
                    db_game = GameBase(UUID=entity.UUID, field=field_copy, turn=entity.turn, message=entity.message,
                                       status=current_status, game_type=game_domain.game_type.value,
                                       current_player_uuid=game_domain.current_player_uuid,
                                       player1_uuid=game_domain.player1_uuid, player2_uuid=game_domain.player2_uuid,
                                       player1_symbol=game_domain.player1_symbol,
                                       player2_symbol=game_domain.player2_symbol)
                    saved_game = session.merge(db_game)
                    flag_modified(saved_game, "field")
            return True
        except SQLAlchemyError as exc:
            print("Ошибка сохранения в базу данных:", exc)
            return False

    def get_game(self, game_id: str) -> tuple:
        try:
            with self.session_factory() as session:
                db_game:GameBase | None = session.get(GameBase, game_id)
                if not db_game:
                    return None,  "Игра не найдена"


                print(f" debug db_game.status тип: {type(db_game.status)}, значение: '{db_game.status}'")
                my_status = db_game.status
                if my_status == "waiting_players":
                    my_status = 0
                current_status = Status(my_status)
                my_game_type = db_game.game_type
                if db_game.game_type == "with_player":
                    my_game_type = 1

                current_game_type = GameType(my_game_type)
                entity_copy = GameEntity(_id=db_game.UUID, field=db_game.field, turn=db_game.turn,
                                         message=db_game.message, status=current_status, game_type=current_game_type,
                                         player1_uuid=db_game.player1_uuid, player2_uuid=db_game.player2_uuid,
                                         current_player_uuid=db_game.current_player_uuid,
                                         player1_symbol=db_game.player1_symbol,
                                         player2_symbol=db_game.player2_symbol
                                        )
                session.close()
                return from_entity(entity_copy)


        except SQLAlchemyError as exc:
            print("Ошибка загрузки из базы данных:", exc)
            return None, "Ошибка базы данных"

    def get_new_games(self, player_uuid):
        try:

            with (self.session_factory() as session):
                query = select(GameBase).where(
                    GameBase.status == 0,
                    GameBase.player1_uuid != player_uuid)

                return session.scalars(query).all()

        except SQLAlchemyError as exc:
            print("Ошибка загрузки из базы данных:", exc)
            return None

    def get_user_info(self, player_uuid):
        try:
            with (self.session_factory() as session):
                query = select(UsersInfo.login).where(
                    UsersInfo.uuid == player_uuid)

                return session.scalars(query).first()

        except SQLAlchemyError as exc:
            print("Ошибка загрузки из базы данных:", exc)
            return None

    def get_user_game_info(self, player_uuid):
        try:
            with (self.session_factory() as session):
                query = select(GameBase.UUID, GameBase.game_type, GameBase.status).where(
                    or_(
                        GameBase.player1_uuid == player_uuid,
                        GameBase.player2_uuid == player_uuid
                    )
                )
                result = session.execute(query).all()
                my_list = []
                for line in result:
                    my_list.append({
                        'game_uuid': line.UUID,
                        'game_status': line.status,
                        'game_type': line.game_type
                    })
                return my_list

        except SQLAlchemyError as exc:
            print("Ошибка загрузки из базы данных:", exc)
            return None

if __name__ == '__main__':
    print("Пока тут ничего нет")