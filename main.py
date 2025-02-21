import pygame

class MainApp:
    WIDTH = 1280
    HEIGHT = 720
    WINDOW_SIZE = (WIDTH,HEIGHT)
    NAME = "SmashBalls"
    def __init__(self):
        pygame.init()
        self.init_game()

    # 初期化
    def init_game(self):
        self.run = True

        pygame.display.set_caption(MainApp.NAME)
        self.window = pygame.display.set_mode(MainApp.WINDOW_SIZE)
        self.clock = pygame.time.Clock()

    # イベント処理
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

    # メインループ(イベントループ処理)
    # メインプロセスで動作すること
    def mainloop(self):
        POLLING_RATE = 1000
        while self.run:
            self.clock.tick(POLLING_RATE)
            self.event_handler()
        pygame.quit()

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()