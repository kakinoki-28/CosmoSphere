import pygame as pg
from input import InputHandler

class MainApp:
    SCREENRECT = pg.Rect(0, 0, 1280, 720)
    APP_NAME = "SmashBalls"

    def __init__(self):
        pg.init()
        self.init_game()

    # 初期化
    def init_game(self):
        self.run = True
        self.winstyle = 0

        self.window = pg.display.set_mode(self.SCREENRECT.size, self.winstyle)
        pg.display.set_caption(self.APP_NAME)

        self.thread_list = []

        self.Input = InputHandler

    # イベント処理
    def event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False
            elif event.type == pg.KEYDOWN:
                self.Input.keydown(event.key)

    # メインループ(イベントループ処理)
    # メインスレッドで動作すること
    def mainloop(self):
        POLLING_RATE = 1000
        clock = pg.time.Clock()

        while self.run:
            clock.tick(POLLING_RATE)
            self.event_handler()

        # 正常終了時処理
        for th in self.thread_list:
            th.join()
        print("Bye!")

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
    pg.quit()