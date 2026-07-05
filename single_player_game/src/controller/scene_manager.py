from src.dto.enums import GameScene


class SceneManager:

    def __init__(self) -> None:
        self._scene: GameScene = GameScene.SPLASH

    @property
    def current(self) -> GameScene:
        return self._scene

    def transition_to(self, scene: GameScene) -> None:
        self._scene = scene
