class BrowserGame:
    def __init__(self, game_id = None, current_turn = 0, message = '', player_uuid = None):
        self.uuid = game_id
        self.field = [[-1] * 3 for _ in range(3)]
        self.current_turn = current_turn
        self.message = message
        self.current_player_uuid = player_uuid


class SignUpRequest:
    def __init__(self,login, password):
        self.login=login
        self.password=password
