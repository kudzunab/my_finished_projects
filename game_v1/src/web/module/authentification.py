from web.module.authorisation_service import AuthorisationService
from flask import request, jsonify, g
class UserAuthenticator:
    def __init__(self, auth_service: AuthorisationService):
        self.auth_service = auth_service

    def authenticate(self, base64_str: str) -> str | None:
        if not base64_str:
            return None

        return self.auth_service.authorisation(base64_str)

    def protected_connection(self):
        free_routes = ["/", "/game/registration", "/game/authorisation"]
        if request.path in free_routes:
            return None

        auth_result=request.headers.get("Authorization")
        if not auth_result or not auth_result.startswith("Basic "):
            return jsonify({"message": "Нет заголовка авторизации"}), 401

        base64_str=auth_result[6:]
        pl_uuid=self.authenticate(base64_str)

        if not pl_uuid:
            return jsonify({"message": "Неверный логин или пароль"}), 401

        g.pl_uuid=pl_uuid
        return None

