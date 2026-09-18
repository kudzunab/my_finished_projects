from flask import request, redirect, url_for, jsonify
from src.web.mapper import from_game_to_browser_game
from src.web.mapper import web_turn_synch

def init_routes(app, container):
    game_service = container.game_service()
    @app.route('/')
    def index():
        return redirect(url_for('start_game'))

    @app.route('/game/start')
    def start_game():
        new_game = game_service.start_new_game()
        return jsonify({
            "uuid": new_game.UUID,
            "field": new_game.field,
            "message": "Начало новой игры, ваш ход"
        }), 201

    @app.route('/game/<game_id>', methods = ['POST'])
    def turn(game_id):
        try:
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"message": "Ничего не прислали"}), 400
            if not all(field in data for field in ["uuid", "field"]):  #, "current_turn"
                return jsonify({"message": "Запрос не содержит нужные поля"}), 400

            if data.get("uuid") != game_id:
                return jsonify({"message": "неверный UUID игры"}), 400

            web_model = container.browser_game()
            web_model.uuid = game_id
            web_model.field = data.get("field")
            web_model.current_turn = data.get("current_turn", 0)

            updated_model = game_service.process_turn(
                game_id = game_id,
                sync_func=web_turn_synch,
                incoming_web_model=web_model
            )
            if not updated_model:
                return jsonify({"message": "Игра не найдена"}), 404

            return jsonify({
                "uuid": updated_model.uuid,
                "field": updated_model.field,
                "message": updated_model.message
            }), 200
        except (IndexError, TypeError):
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
            "field": web_model.field,
            "message": web_model.message
        }), 200

