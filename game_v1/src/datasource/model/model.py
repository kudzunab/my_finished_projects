from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.mutable import MutableList
import uuid

class Base(DeclarativeBase):
    pass

def get_new_uuid():
    return str(uuid.uuid4())

class GameBase(Base):
    __tablename__ = "games"
    UUID: Mapped[str] = mapped_column(String(36), primary_key=True)
    field: Mapped[list[list[int]]] = mapped_column(MutableList.as_mutable(JSON))
    turn: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(256))
    game_type: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer)

    player1_uuid: Mapped[str] = mapped_column(String(36), ForeignKey('users_info.uuid', name='fk_game_player1'))
    player2_uuid: Mapped[str | None] = mapped_column(String(36), ForeignKey('users_info.uuid',
                                                                            name='fk_game_player2'), nullable=True)
    current_player_uuid: Mapped[str | None] = mapped_column(String(36), ForeignKey('users_info.uuid',
                                                                                   name='fk_game_current_player'),
                                                            nullable=True)
    player1_symbol: Mapped[str] = mapped_column(String(1))
    player2_symbol: Mapped[str] = mapped_column(String(1))

class UsersInfo(Base):
    __tablename__ = "users_info"
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=get_new_uuid)
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

class GameEntity:
    def __init__(self, _id: str = None, field: list = None, turn: int = 0, message: str = "", game_type=None,
                 status=None, player1_uuid = None, player2_uuid=None, current_player_uuid=None, player1_symbol="x",
                 player2_symbol="o"):
        self.UUID = _id
        self.field = [[-1]*3 for _ in range(3)]
        self.game_type = game_type
        self.status = status
        self.player1_uuid = player1_uuid
        self.player2_uuid = player2_uuid
        self.current_player_uuid = current_player_uuid
        self.player1_symbol = player1_symbol
        self.player2_symbol = player2_symbol
        if field is not None:
            for i in range(3):
                for j in range(3):
                    self.field[i][j] = field[i][j]

        self.turn = turn
        self.message = message
