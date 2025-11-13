import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Gravity Sandbox"

class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def setup(self):
        pass

    def on_draw(self):
        self.clear()

if __name__ == "__main__":
    window = arcade.Window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WINDOW_TITLE
    )

    game = GameView()
    game.setup()

    window.show_view(game)
    arcade.run()
