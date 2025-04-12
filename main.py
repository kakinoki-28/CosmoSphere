import pygame as pg
from input import InputHandler

class MainApp:
    SCREENRECT = pg.Rect(0, 0, 1280, 720)
    APP_NAME = "SmashBalls"

    def __init__(self):
        pg.init()
        self.init_app()

    # 初期化
    def init_app(self):
        self.run = True
        self.winstyle = 0

        self.window = pg.display.set_mode(self.SCREENRECT.size, self.winstyle)
        pg.display.set_caption(self.APP_NAME)

        self.thread_list = []

        self.Input = InputHandler()
        self.joysticks = []

    # イベント処理
    def event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False
            # コントローラー接続・切断
            elif event.type == pg.JOYDEVICEADDED:
                joy = pg.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
                self.Input.connect_joy(joy.get_numbuttons(), joy.get_numaxes(), joy.get_numhats())
                print(f"{joy.get_name()} connencted!")
            elif event.type == pg.JOYDEVICEREMOVED:
                print(f"{self.joysticks[event.instance_id].get_name()} disconnected!")
                del self.joysticks[event.instance_id]
            # 入力処理
            elif event.type == pg.KEYDOWN:
                if self.Input.keydown(event.key):
                    input_changed = True
            elif event.type == pg.KEYUP:
                if self.Input.keyup(event.key):
                    input_changed = True
            elif event.type == pg.JOYBUTTONDOWN:
                if self.Input.buttondown(event.button):
                    input_changed = True
            elif event.type == pg.JOYBUTTONUP:
                if self.Input.buttonup(event.button):
                    input_changed = True
            elif event.type == pg.JOYAXISMOTION:
                if self.Input.axismove(event.axis, event.value):
                    input_changed = True
            elif event.type == pg.JOYHATMOTION:
                if self.Input.hatmove(event.hat, event.value):
                    input_changed = True

        if input_changed:
            print(self.Input)

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