from src.datasource.model.model import UsersInfo
from sqlalchemy import select
import uuid

class UserService:
    def __init__(self, session_factory=None):
        self.session_factory = session_factory


    def add_user(self, login:str, hashed_password:str)-> bool:
        if not self.session_factory:
            return False

        with (self.session_factory() as session):
            with session.begin():
                query = session.scalar(select(UsersInfo).where(UsersInfo.login == login))

                if query:
                    return False

                db_users = UsersInfo(uuid=str(uuid.uuid4()), login=login, password=hashed_password)
                session.merge(db_users)

                return True

    def get_user_by_login(self, login: str):
        with (self.session_factory() as session):
            query = session.scalar(select(UsersInfo).where(UsersInfo.login == login))
            return query
