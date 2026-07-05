from abc import ABC, abstractmethod

class JwtProviderModel:
    @staticmethod
    def generate_access_token(uuid: str) -> str | None:
        pass

    @staticmethod
    def generate_refresh_token(uuid: str) -> str | None:
        pass

    @staticmethod
    def validate_access_token(jwt_token: str) -> bool:
        pass

    @staticmethod
    def validate_refresh_token(jwt_token: str) -> bool:
        pass

    @staticmethod
    def get_user_uuid_from_token(jwt_token: str) -> str | None:
        pass


class IAuthorisationService(ABC):
    @abstractmethod
    def registration(self, login: str, password: str) -> bool:
        pass

    @abstractmethod
    def authorisation(self, obj):
        pass

    @abstractmethod
    def refresh_token(self, refresh_token):
        pass

    @abstractmethod
    def refresh_all(self, refresh_token):
        pass
