from werkzeug.security import generate_password_hash, check_password_hash
from src.web.model.model import JwtRequest, JwtResponse

class AuthorisationService:
    def __init__(self, user_service, jwt_provider): # добавить в контейнер и user_service
        self.user_service = user_service
        self.jwt_provider = jwt_provider

    def registration(self, login: str, password: str):
        if not self.user_service:
            return False

        hashed = generate_password_hash(password)

        return self.user_service.add_user(login=login, hashed_password=hashed)

    def authorisation(self, obj: JwtRequest) -> JwtResponse:
        if not obj:
            return JwtResponse("", "")

        if not self.user_service or not self.jwt_provider:
            return JwtResponse("", "")

        user = self.user_service.get_user_by_login(obj.login)
        if not user or not check_password_hash(user.password, obj.password):
            return JwtResponse("", "")

        result = JwtResponse(self.jwt_provider.generate_access_token(user.uuid),
                             self.jwt_provider.generate_refresh_token(user.uuid))

        return result

    def refresh_token(self, refresh_token):
        if not refresh_token:
            return JwtResponse("", "")

        uuid=self.jwt_provider.validate_refresh_token(refresh_token)
        if not uuid:
            return JwtResponse("", "")

        return JwtResponse(self.jwt_provider.generate_access_token(str(uuid)),
                           refresh_token)

    def refresh_all(self, refresh_token):
        if not refresh_token:
            return JwtResponse("", "")

        uuid=self.jwt_provider.validate_refresh_token(refresh_token)
        if not uuid:
            return JwtResponse("", "")
        return JwtResponse(self.jwt_provider.generate_access_token(str(uuid)),
                           self.jwt_provider.generate_refresh_token(str(uuid)))
"""
    это надо добавить в container.py:
    user_service = UserService(session_factory=session_factory)
    auth_service = AuthorisationService(user_service=user_service)
"""