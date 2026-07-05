from flask import request, jsonify, g

"""
    Никакой нужды в данном классе нет, прекрасно все работало и с g, но в тз четко сказано,
    что нужно использовать метод sign у Request.jwt
"""

class UserAuthenticator:
    #def __init__(self, auth_service: AuthorisationService, jwt_provider: JwtProvider):
    def __init__(self,  auth_service, jwt_provider):
        self.auth_service = auth_service
        self.jwt_provider = jwt_provider

    def authenticate(self, jwt_request):
        return self.auth_service.authorisation(jwt_request)

    def protected_connection(self):
        free_routes = ["/",
                       "/game/registration",
                       "/game/authorisation",
                       "/game/refresh_access"  #,"/game/refresh_tokens"
                       ]

        if request.path in free_routes:
            return None

        auth_header=request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "Вы не авторизованы"}), 401

        access_token = auth_header[7:]

        if not access_token:
            return jsonify({"message": "Вы не авторизованы"}), 401

        pl_uuid=self.jwt_provider.validate_access_token(access_token)

        if not pl_uuid:
            return jsonify({"message": "Токен недействителен или устарел"}), 401

        g.jwt.sign(str(pl_uuid))
        return None


