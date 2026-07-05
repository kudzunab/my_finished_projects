from flask import request, jsonify, g #session  #redirect, url_for,
import copy, os
from src.domain.model.model import computer_uuid #, none_uuid
from src.web.mapper import web_turn_synch, from_game_to_browser_game
from src.domain.model.model import PlayerSymbol, GameType

def init_routes(app, container):
    secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SECRET_KEY'] = secret_key
    game_service = container.game_service()
    auth_service = container.auth_service()
    authenticator = container.user_authenticator()

    @app.before_request
    def auto_identification():
        public = ['/', '/game/registration', '/game/authorisation']

        if request.path in public:
            return None

        return authenticator.protected_connection()

    @app.route('/')
    def index():
        return jsonify({"message":"Добро пожаловать в приложение крестики-нолики"}), 200

    @app.route('/game/registration', methods=["POST"])
    def registration():
        data=request.get_json(silent=True)
        if not data or "login" not in data or "password" not in data:
            return jsonify({"message": "не введен логин/пароль"}), 400

        login=data["login"]
        user_login=container.request_factory(login=login, password=data["password"])
        is_registered=auth_service.registration(user_login)
        if is_registered:
            return jsonify({"login": login, "message":"Вы успешно зарегистрировались"}), 200
        else:
            return jsonify({"message": "Пользователь с таким логином уже существует"}), 400

    @app.route('/game/authorisation', methods=["POST"])
    def authorisation():
        auth_result = request.headers.get("Authorization")
        if not auth_result or not auth_result.startswith("Basic "):
            return jsonify({"pl_uuid": "-", "message": "Требуется заголовок Authorization"}), 401

        base64_str = auth_result[6:]
        my_uuid = auth_service.authorisation(base64_str)

        if my_uuid:
            return jsonify({"pl_uuid": my_uuid, "message": "Вы успешно авторизовались"}), 200

        return jsonify({"pl_uuid": "-", "message": "Неверный логин/пароль"}), 401

    @app.route('/game/start', methods=["POST"])
    def start_game():
        data=request.get_json(silent=True)
        if not data or "game_type" not in data:
            return jsonify({"message": "не ввели тип игры/ввели некорректное значение"}), 400

        try:
            if data["game_type"] in GameType.__members__:
                selected_type = GameType[data["game_type"]] #поиск по значению
            else:
                selected_type = GameType(int(data["game_type"])) # поиск по имени
        except (ValueError, TypeError):
            return jsonify({"message": "введено некорректное значение типа игры"}), 400

        current_uuid1 = getattr(g,"pl_uuid", None)
        if selected_type == GameType.with_computer:
            player2_uuid = computer_uuid
        else:
            player2_uuid = None #none_uuid

        new_game = game_service.start_new_game(game_type=selected_type, player1_uuid=current_uuid1,
                                               player2_uuid=player2_uuid) #, current_player_uuid=current_uuid1
        return jsonify({
            "uuid": new_game.UUID,
            "field": new_game.field,
            "message": "Начало новой игры, ваш ход",
            "player1_uuid": current_uuid1,
            "player1_symbol": PlayerSymbol.cross.value
        }), 201  # стандартный код успешного запроса

    @app.route('/game/waiting', methods=['GET'])
    def get_games():
        player_uuid = getattr(g,"pl_uuid", None)
        games_data = game_service.repo.get_new_games(player_uuid)
        result = []
        for g_data in games_data:
            result.append({"game_uuid": g_data.UUID,
                           "player1_uuid": g_data.player1_uuid})
        return jsonify({"available_games": result}), 200

    @app.route('/game/join', methods=["POST"])
    def join_to_game():

        data=request.get_json(silent=True)
        if not data or "uuid" not in data:
            return jsonify({"message": "Не передали UUID игры"}), 400


        game_uuid=str(data["uuid"])
        player2_uuid = getattr(g,"pl_uuid", None) #g.pl_uuid

        updated_game, message = game_service.join_to_game(game_uuid, player2_uuid)
        if not updated_game:
            return jsonify({"message": message.value}), 404

        return jsonify({
            "uuid": updated_game.UUID,
            "field": updated_game.field,
            "message": message.value,
            "player2_uuid": player2_uuid,
            "player2_symbol": PlayerSymbol.nulls.value  # Подключившийся всегда играет ноликами
        }), 200

    @app.route('/game/<game_id>', methods=['POST'])
    def turn(game_id):

        try:
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"message": "Ничего не прислали"}), 400
            if not all(field in data for field in ["uuid", "field"]):  # , "current_turn"
                return jsonify({"message": "Запрос не содержит нужные поля"}), 400

            web_model = container.browser_game()
            web_model.uuid = game_id
            web_model.field = copy.deepcopy(data.get("field"))
            web_model.pl_uuid = getattr(g,"pl_uuid", None) 

            updated_model, message = game_service.process_turn(  
                game_id=game_id,
                sync_func=web_turn_synch,
                incoming_web_model=web_model,
                player_uuid=web_model.pl_uuid
            )
            if not updated_model:
                return jsonify({"message": message}), 404

            return jsonify({
                "uuid": updated_model.uuid,
                "field": updated_model.field,
                "message": message,
                "current_player_uuid": updated_model.current_player_uuid  #getattr(g,"pl_uuid", None) #g.pl_uuid
            }), 200
        except (IndexError, TypeError):
            import traceback
            traceback.print_exc()
            return jsonify({
                "message": "Критическая ошибка данных или формата запроса",
            }), 400

    @app.route('/game/<game_id>', methods=['GET'])
    def get_game_state(game_id):

        game_data = game_service.repo.get_game(game_id)

        if not game_data or not game_data[0]:
            return jsonify({"message": "Игра не найдена"}), 404

        game_domain, message = game_data
        web_model = container.browser_game()
        from_game_to_browser_game(game_domain, web_model, message)
        return jsonify({
            "uuid": web_model.uuid,
            "current_player_uuid": web_model.current_player_uuid,
            "field": web_model.field,
            "message": web_model.message
        }), 200

    @app.route('/game/user_info/<user_uuid>', methods=["GET"])
    def get_user_info(user_uuid):
        login = game_service.repo.get_user_info(user_uuid)
        if not login:
            return jsonify({
                "message": 'Такого пользователя нет'
            }), 404
        game_info = game_service.repo.get_user_game_info(user_uuid)

        return jsonify({
            "login": login,
            "game_information": game_info
        }), 200

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
"""
послать запрос на сервер можно и так:
curl -X POST http://127.0.0 \
     -H "Content-Type: application/json" \
     -d '{"base64_str": "YWRtaW46MTIzNDU="}'
"""