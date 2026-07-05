from flask import Blueprint, request, jsonify

auth_blueprint = Blueprint('auth', __name__)
def auth_routes(auth_service, container):
    @auth_blueprint.route('/registration', methods=["POST"])
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

    @auth_blueprint.route('/authorisation', methods=["POST"])
    def authorisation():
        data=request.get_json(silent=True)
        if not data or "login" not in data or "password" not in data:
            return jsonify({"message": "не введен логин/пароль"}), 400

        login=data["login"]
        user_login=container.request_factory(login=login, password=data["password"])
        jwt_response = auth_service.authorisation(user_login)
        if not jwt_response or not jwt_response.accessToken or not jwt_response.refreshToken:
            return jsonify({"message": "Неверный логин/пароль"}), 401

        return jsonify({"accessToken": jwt_response.accessToken,
                        "refreshToken": jwt_response.refreshToken,
                        "message": "Вы успешно авторизованы"}), 200

    @auth_blueprint.route('/refresh_access', methods=["POST"])
    def refresh_access_token():
        data = request.get_json(silent=True)
        if not data or not data.get("refreshToken"):
            return jsonify({"message": "нет нужных полей"}), 400
        refresh_token=data.get("refreshToken")
        result=auth_service.refresh_token(refresh_token)
        if not result or not result.accessToken:
            return jsonify({"message": "обновите refreshToken"}), 401

        return jsonify({"accessToken": result.accessToken,
                        "refreshToken": result.refreshToken,
                        "message": "Успешно обновлен accessToken"}), 200


    @auth_blueprint.route('/refresh_tokens', methods=["POST"])
    def refresh_tokens():
        data = request.get_json(silent=True)
        if not data or not data.get("refreshToken"):
            return jsonify({"message": "нет нужных полей"}), 400
        refresh_token = data.get("refreshToken")
        result = auth_service.refresh_all(refresh_token)

        if not result or not result.accessToken:
            return jsonify({"message": "вы не зарегистрированы"}), 401

        return jsonify({"accessToken": result.accessToken,
                        "refreshToken": result.refreshToken,
                        "message": "Успешно обновлен accessToken"}), 200