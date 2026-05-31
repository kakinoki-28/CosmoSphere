from gamelogic import GameState
from time import perf_counter, sleep
from ctypes import windll


""" ゲーム進行の管理 """
class GameManeger:
    FPS = 64
    FRAME_LATENCY = 1/FPS

    def __init__(self):
        self.run = True
        def dummy(frame):
            pass
        self.update_func = dummy    # ゲームが更新される際に呼び出される関数(通信等)
        self.frame_rate = 0         # フレームレートの保存

        self.available_color = ["red", "green"] # 利用可能なキャラの色
        self.state = GameState()

    """ ゲームの初期化 """
    def init_game(self):
        self.state.init_game()

    """ キャラの追加 """
    def add_character(self, color, id):
        if color in self.available_color:
            return self.state.add_character(color, id)
        else:
            raise ValueError(f"{color} is not available color")

    """ キャラの削除 """
    def remove_character(self, character):
        self.state.remove_character(character)

    """ ゲームのメイン処理 """
    def mainloop(self):
        windll.winmm.timeBeginPeriod(1)     # タイマーの精度向上
        frame_time = [perf_counter()]*2     # フレームレートの観測用リスト
        delay = 0
        while self.run:
            start = perf_counter()

            frame = self.state.update()     # ゲーム状況を更新
            self.update_func(frame)         # フレーム毎実行処理

            # フレーム計測
            frame_time[1] = perf_counter()
            self.frame_rate = 1/(frame_time[1]-frame_time[0])
            frame_time[0] = perf_counter()

            # フレーム遅延処理
            delay = perf_counter()-start
            if self.FRAME_LATENCY-delay > 0.001:
                sleep(int((self.FRAME_LATENCY-delay)/0.001)*0.001)
            while perf_counter()-start < self.FRAME_LATENCY:
                pass
        windll.winmm.timeEndPeriod(1)


