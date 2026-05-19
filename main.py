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
        input_changed = False

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
                input_changed = self.Input.keydown(event.key)
            elif event.type == pg.KEYUP:
                input_changed = self.Input.keyup(event.key)
            elif event.type == pg.JOYBUTTONDOWN:
                input_changed = self.Input.buttondown(event.button)
            elif event.type == pg.JOYBUTTONUP:
                input_changed = self.Input.buttonup(event.button)
            elif event.type == pg.JOYAXISMOTION:
                input_changed = self.Input.axismove(event.axis, event.value)
            elif event.type == pg.JOYHATMOTION:
                input_changed = self.Input.hatmove(event.hat, event.value)

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