from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy import String, Integer, Float, JSON, ForeignKey, DateTime, func
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

    player1_uuid: Mapped[str | None] = mapped_column(String(36), ForeignKey('users_info.uuid',
                                                                            name='fk_game_player1',
                                                                            ondelete="SET NULL"), nullable=True)
    player2_uuid: Mapped[str | None] = mapped_column(String(36), ForeignKey('users_info.uuid',
                                                                            name='fk_game_player2',
                                                                            ondelete="SET NULL"), nullable=True)
    current_player_uuid: Mapped[str | None] = mapped_column(String(36), ForeignKey('users_info.uuid',
                                                                                   name='fk_game_current_player',
                                                                                   ondelete="SET NULL"),
                                                            nullable=True)
    player1_symbol: Mapped[str] = mapped_column(String(1))
    player2_symbol: Mapped[str] = mapped_column(String(1))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class UsersInfo(Base):
    __tablename__ = "users_info"
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=get_new_uuid)
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

class GameStats(Base):
    __tablename__ = "users_stats"
    user_uuid: Mapped[str] = mapped_column(String(36), ForeignKey('users_info.uuid',
                                                                  name='fk_game_player_uuid', ondelete="CASCADE"),
                                           primary_key=True)
    wins_count: Mapped[int] = mapped_column(Integer, default=0)
    games_count: Mapped[int] = mapped_column(Integer, default=0)
    wins_rate: Mapped[float|None] = mapped_column(Float, default=None)

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


    """
        UPDATE games
        SET current_player_uuid = player2_uuid
        WHERE player2_uuid = '00000000-0000-0000-0000-000000000001' AND status = 3
    
    
        INSERT INTO users_stats (user_uuid, wins_count, games_count, wins_rate)
        SELECT 
            user_uuid, SUM(win_games) AS wins_count, SUM(full_games) AS games_count,
            CASE 
                WHEN SUM(full_games) > 0 THEN ROUND(SUM(win_games)::numeric / SUM(full_games), 4)
                ELSE 0.0 
            END AS wins_rate
        FROM (
            SELECT 
                player1_uuid AS user_uuid, 
                COUNT(*) FILTER (WHERE status = 3 AND current_player_uuid = player1_uuid) AS win_games, 
                COUNT(*) FILTER (WHERE status = 2 OR status = 3) AS full_games 
            FROM games 
            WHERE player1_uuid IS NOT NULL
            GROUP BY player1_uuid

            UNION ALL

            SELECT 
                player2_uuid AS user_uuid, 
                COUNT(*) FILTER (WHERE status = 3 AND current_player_uuid = player2_uuid) AS win_games, 
                COUNT(*) FILTER (WHERE status = 2 OR status = 3) AS full_games 
            FROM games 
            WHERE player2_uuid IS NOT NULL
            GROUP BY player2_uuid
        ) AS combined_history
    GROUP BY user_uuid
    ON CONFLICT (user_uuid) 
    DO UPDATE SET 
        wins_count = EXCLUDED.wins_count,
        games_count = EXCLUDED.games_count,
        wins_rate = EXCLUDED.wins_rate;
    """