from werkzeug.security import generate_password_hash, check_password_hash
import base64
from src.web.model.model import SignUpRequest
from src.domain.service.user_service import UserService

class AuthorisationService:
    def __init__(self, user_service: UserService): # добавить в контейнер и user_service
        self.user_service = user_service

    def registration(self, obj: SignUpRequest):
        if not self.user_service:
            return False

        if ":" in obj.login or  ":" in obj.password:
            return False

        hashed = generate_password_hash(obj.password)

        return self.user_service.add_user(login=obj.login, hashed_password=hashed)

    def authorisation(self, base64_str: str) -> str | None:
        if not self.user_service:
            return None

        in_bytes = base64.b64decode(base64_str.encode('utf-8'))
        dec_str = in_bytes.decode('utf-8')

        try:
            login, password = dec_str.split(":", 1)
        except ValueError:
            return None

        user = self.user_service.get_user_by_login(login)
        if not user:
            return None

        if not check_password_hash(user.password, password):
            return None

        return user.uuid
