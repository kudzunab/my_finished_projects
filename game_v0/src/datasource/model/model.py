class GameEntity:
    def __init__(self, _id: str = None, field: list = None, turn: int = 0, message: str = ""):
        self.UUID = _id
        self.field = [[-1]*3 for _ in range(3)]

        if field is not None:
            for i in range(3):
                for j in range(3):
                    self.field[i][j] = field[i][j]
        self.turn = turn
        self.message = message