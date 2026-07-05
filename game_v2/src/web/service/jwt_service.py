from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from jwt.exceptions import InvalidTokenError
from src.web.interface.service import JwtProviderModel

class JwtProvider(JwtProviderModel):
    @staticmethod
    def generate_access_token(uuid):
        return create_access_token(identity=str(uuid))

    @staticmethod
    def generate_refresh_token(uuid):
        return create_refresh_token(identity=str(uuid))

    @staticmethod
    def validate_access_token(jwt_token):
        uuid = JwtProvider.get_user_uuid_from_token(jwt_token)
        if uuid:
            try:
                data = decode_token(jwt_token)
                if data["type"] == 'access':
                    return uuid
            except (InvalidTokenError, KeyError):
                pass
        return None
    @staticmethod
    def validate_refresh_token(jwt_token):
        uuid=JwtProvider.get_user_uuid_from_token(jwt_token)
        if uuid:
            try:
                data = decode_token(jwt_token)
                if data["type"] == 'refresh':
                    return uuid
            except (InvalidTokenError, KeyError):
                pass
        return None

    @staticmethod
    def get_user_uuid_from_token(jwt_token):
        try:
            data=decode_token(jwt_token)
            token_type=data["type"]
            if token_type in ["access", "refresh"]:
                user_uuid = data["sub"]
            else:
                user_uuid = None
        except (InvalidTokenError, KeyError):
            user_uuid=None
        return user_uuid