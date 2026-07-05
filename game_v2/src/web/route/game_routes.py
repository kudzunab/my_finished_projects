import copy
from flask import Blueprint, request, jsonify, g
from src.domain.model.model import computer_uuid, Status
from src.web.mapper import web_turn_synch, from_game_to_browser_game
from src.domain.model.model import PlayerSymbol, GameType

game_blueprint = Blueprint('game', __name__)

def game_routes(game_service, container, authenticator):
    @game_blueprint.before_request
    def auto_identification():
        return authenticator.protected_connection()

    @game_blueprint.route('/user_info', methods=["GET"])
    def get_info():
        user_uuid = getattr(g, "pl_uuid", None)

        if not user_uuid:
            return jsonify({"message": "Вы не авторизованы"}), 401

        login = game_service.repo.get_user_info(user_uuid)
        if not login:
            return jsonify({
                "message": 'Такого пользователя нет'
            }), 404
        game_info = game_service.repo.get_user_game_info(user_uuid)

        return jsonify({
            "login": login,
            "user_uuid": user_uuid,
            "game_information": game_info
        }), 200

    @game_blueprint.route('/start', methods=["POST"])
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

    @game_blueprint.route('/waiting', methods=['GET'])
    def get_games():
        player_uuid = getattr(g,"pl_uuid", None)
        games_data = game_service.repo.get_new_games(player_uuid)
        result = []
        for g_data in games_data:
            result.append({"game_uuid": g_data.UUID,
                           "player1_uuid": g_data.player1_uuid})
        return jsonify({"available_games": result}), 200

    @game_blueprint.route('/join', methods=["POST"])
    def join_to_game():

        data=request.get_json(silent=True)
        if not data or "uuid" not in data:
            return jsonify({"message": "Не передали UUID игры"}), 400


        game_uuid=str(data["uuid"])
        player2_uuid = getattr(g,"pl_uuid", None) #g.pl_uuid

        updated_game, message, code = game_service.join_to_game(game_uuid, player2_uuid)

        if not updated_game:
            return jsonify({"message": message.value}), code

        return jsonify({
            "uuid": updated_game.UUID,
            "field": updated_game.field,
            "message": message.value,
            "player2_uuid": player2_uuid,
            "player2_symbol": PlayerSymbol.nulls.value  # Подключившийся всегда играет ноликами
        }), code

    @game_blueprint.route('/<game_id>', methods=['POST'])
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
            #web_model.current_turn = data.get("current_turn", 0)
            web_model.pl_uuid = getattr(g,"pl_uuid", None) #g.pl_uuid

            updated_model, message = game_service.process_turn(  #, message
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
                "message": message, # updated_model.message,
                "current_player_uuid": updated_model.current_player_uuid  #getattr(g,"pl_uuid", None) #g.pl_uuid
            }), 200
        except (IndexError, TypeError):
            import traceback
            traceback.print_exc()
            return jsonify({
                "message": "Критическая ошибка данных или формата запроса",
            }), 400

    @game_blueprint.route('/<game_id>', methods=['GET'])
    def get_game_state(game_id):

        game_data = game_service.repo.get_game(game_id)

        if not game_data or not game_data[0]:
            return jsonify({"message": "Игра не найдена"}), 404

        game_domain, message = game_data
        web_model = container.browser_game()
        from_game_to_browser_game(game_domain, web_model, message)
        if game_domain.status in [Status.nobody_wins, Status.win_player_with_UUID]:
            web_model.current_player_uuid = 'NOBODY'

        return jsonify({
            "uuid": web_model.uuid,
            "current_player_uuid": web_model.current_player_uuid,
            "field": web_model.field,
            "message": web_model.message
        }), 200

    @game_blueprint.route('/user_info/<user_uuid>', methods=["GET"])
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

    @game_blueprint.route('/game_info', methods=["GET"])
    def get_game_history():
        user_uuid = getattr(g, "pl_uuid", None)

        if not user_uuid:
            return jsonify({"message": "Вы не авторизованы"}), 401

        login = game_service.repo.get_user_info(user_uuid)
        if not login:
            return jsonify({
                "message": 'Такого пользователя нет'
            }), 404
        game_info, code = game_service.get_game_info(user_uuid)

        return jsonify({
            "game_information": game_info
        }), code

    @game_blueprint.route('/game_stats/<int:n>', methods=["GET"])
    def get_game_stats(n):
        user_uuid = getattr(g, "pl_uuid", None)

        if not user_uuid:
            return jsonify({"message": "Вы не авторизованы"}), 401

        login = game_service.repo.get_user_info(user_uuid)
        if not login:
            return jsonify({
                "message": 'Такого пользователя нет'
            }), 404
        stats_list, code = game_service.best_players_list(n)

        return jsonify({
            "game_statistics": stats_list
        }), code