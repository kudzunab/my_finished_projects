from flask import g
class RequestJwtExtension:
    def sign(self, user_uuid: str):
        g.pl_uuid = user_uuid

class JwtRequest:
    def __init__(self, login, password):
        self.login=login
        self.password=password

class JwtResponse:
    def __init__(self, access_token: str, refresh_token: str, token_type="Bearer"):
        self.type=token_type
        self.accessToken=access_token
        self.refreshToken=refresh_token

class RefreshJwtRequest:
    def __init__(self, refresh_token: str):
        self.refreshToken=refresh_token

class BrowserGame:
    def __init__(self, game_id = None, current_turn = 0, message = '', player_uuid = None):
        self.uuid = game_id
        self.field = [[-1] * 3 for _ in range(3)]
        self.current_turn = current_turn
        self.message = message
        self.current_player_uuid = player_uuid

