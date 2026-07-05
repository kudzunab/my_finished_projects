from flask import request, jsonify, g
import os
from flask_jwt_extended import JWTManager
from src.web.route import auth_routes, auth_blueprint, game_routes, game_blueprint
from src.web.model.model import RequestJwtExtension
from sqlalchemy.exc import TimeoutError

def init_routes(app, container):
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY must be set in environment variables!")
    app.config['SECRET_KEY'] = secret_key
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    JWTManager(app)
    game_service = container.game_service()
    auth_service = container.auth_service()
    authenticator = container.user_authenticator()

    @app.before_request
    def auto_identification():

        g.jwt = RequestJwtExtension()

        return authenticator.protected_connection()

    @app.route('/')
    def index():
        return jsonify({"message":"Добро пожаловать в приложение крестики-нолики"}), 200

    auth_routes(auth_service, container)
    app.register_blueprint(auth_blueprint, url_prefix='/game')
    game_routes(game_service, container, authenticator)
    app.register_blueprint(game_blueprint, url_prefix='/game')

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({
            "error": "Not Found",
            "message": "Запрашиваемый адрес не существует. Проверьте корректность URL."
        }), 404

    @app.errorhandler(405)
    def error_fixer(e):
        return jsonify({
            "error": "Method Not Allowed",
            "message": f"Метод {request.method} не поддерживается"
        }), 405

    @app.errorhandler(TimeoutError)
    def handle_db_timeout(error):
        return {"error": "Сервер перегружен, попробуйте позже"}, 503
"""
послать запрос на сервер можно и так:
curl -X POST http://127.0.0 \
     -H "Content-Type: application/json" \
     -d '{"base64_str": "YWRtaW46MTIzNDU="}'
"""

