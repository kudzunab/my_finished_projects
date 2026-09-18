class BrowserGame:
    def __init__(self, game_id = None, current_turn = 0, message = ''):
        self.uuid = game_id
        self.field = [[-1] * 3 for _ in range(3)]
        self.current_turn = current_turn
        self.message = message