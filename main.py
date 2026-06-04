import pygame as pg
from input import InputHandler
from game_manager import GameManeger
from threading import Thread
import id_maker

class MainApp:
    SCREENRECT = pg.Rect(0, 0, 1280, 720)
    APP_NAME = "SmashBalls"
    FPS = 240

    def __init__(self):
        pg.init()
        self.init_app()

    # 初期化
    def init_app(self):
        self.run = True
        self.winstyle = 0

        self.window = pg.display.set_mode(self.SCREENRECT.size, self.winstyle)
        pg.display.set_caption(self.APP_NAME)

        self.joy_chara_map = {}
        self.chara_input_map = {}
        self.joysticks = {}

        self.game_mgr = GameManeger()
        self.game_mgr.init_game()
        self.key_chara_id = self.add_character("red")

        self.game_thread = Thread(target=self.game_mgr.mainloop, daemon=True)
        self.game_thread.start()

        display_clock = pg.time.Clock()
        self.display_thread = Thread(target=self.display_handler, args=(display_clock,), daemon=True)
        self.display_thread.start()
    
    def add_character(self, color):
        chara_id = id_maker.make_id(self.chara_input_map.values())
        self.game_mgr.add_character(color, chara_id)
        self.chara_input_map[chara_id] = InputHandler()
        return chara_id

    def remove_character(self, chara_id):
        self.game_mgr.remove_character(chara_id)
        del self.chara_input_map[chara_id]

    def display_handler(self, clock):
        while self.run:
            clock.tick(self.FPS)
            #print(f"FPS: {clock.get_fps():.2f}")
            self.game_mgr.draw_game(self.window)
            pg.display.flip()

    # イベント処理
    def event_handler(self):
        input_changed = {chara_id: False for chara_id in self.chara_input_map.keys()}

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False
            # コントローラー接続・切断
            elif event.type == pg.JOYDEVICEADDED:
                joy = pg.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
                self.joy_chara_map[joy.get_instance_id()] = self.add_character("red")
                self.chara_input_map[self.joy_chara_map[joy.get_instance_id()]].connect_joy(joy.get_numbuttons(), joy.get_numaxes(), joy.get_numhats())
                print(f"{joy.get_name()} connencted!")
            elif event.type == pg.JOYDEVICEREMOVED:
                print(f"{self.joysticks[event.instance_id].get_name()} disconnected!")
                self.remove_character(self.joy_chara_map[event.instance_id])
                del self.joy_chara_map[event.instance_id]
                del self.joysticks[event.instance_id]
            # 入力処理
            elif event.type == pg.KEYDOWN:
                input_changed[self.key_chara_id] |= self.chara_input_map[self.key_chara_id].keydown(event.key)
            elif event.type == pg.KEYUP:
                input_changed[self.key_chara_id] |= self.chara_input_map[self.key_chara_id].keyup(event.key)
            elif event.type == pg.JOYBUTTONDOWN:
                input_changed[self.joy_chara_map[event.instance_id]] |= self.chara_input_map[self.joy_chara_map[event.instance_id]].buttondown(event.button)
            elif event.type == pg.JOYBUTTONUP:
                input_changed[self.joy_chara_map[event.instance_id]] |= self.chara_input_map[self.joy_chara_map[event.instance_id]].buttonup(event.button)
            elif event.type == pg.JOYAXISMOTION:
                input_changed[self.joy_chara_map[event.instance_id]] |= self.chara_input_map[self.joy_chara_map[event.instance_id]].axismove(event.axis, event.value)
            elif event.type == pg.JOYHATMOTION:
                input_changed[self.joy_chara_map[event.instance_id]] |= self.chara_input_map[self.joy_chara_map[event.instance_id]].hatmove(event.hat, event.value)

        if any(input_changed.values()):
            for chara_id, changed in input_changed.items():
                if changed:
                    self.game_mgr.regist_input(chara_id, self.chara_input_map[chara_id])
                    print(f"ID({chara_id})'s input : {self.chara_input_map[chara_id]}")

    # メインループ(イベントループ処理)
    # メインスレッドで動作すること
    def mainloop(self):
        POLLING_RATE = 1000
        clock = pg.time.Clock()

        while self.run:
            clock.tick(POLLING_RATE)
            #clock.tick_busy_loop(POLLING_RATE)
            self.event_handler()

        # 正常終了時処理
        self.game_mgr.run = False
        self.display_thread.join()
        self.game_thread.join()
        print("Bye!")

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
    pg.quit()