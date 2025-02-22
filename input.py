import pygame as pg
from pygame.math import Vector2
import configparser

class InputHandler:
    """ 各具象入力を抽象入力に変換するクラス """
    def __init__(self):
        self.direction = Vector2(0, 0)
        self.skills = [False] * 3
        self.attack = False
        self.shield = False

        self.key_map = {}
        # 設定ファイル読み込み
        self.config = configparser.ConfigParser()
        self.config.read("keyconfig.ini")
        # 検証は後で実装

    """ キーボード入力から抽象入力へ変換 """
    def keydown(self, key):
        if pg.key.name(key) in self.config["KEY"].values():
            for action in [k for k, v in self.config["KEY"].items() if v==pg.key.name(key)]:
                if action == "up" and self.direction[1]<=0:
                    self.direction += Vector2(0,1)
                elif action == "down" and self.direction[1]>=0:
                    self.direction += Vector2(0,-1)
                elif action == "left" and self.direction[0]>=0:
                    self.direction += Vector2(-1,0)
                elif action == "right" and self.direction[0]<=0:
                    self.direction += Vector2(1,0)

    def keyup(self, key):
        if pg.key.name(key) in self.config["KEY"].values():
            for action in [k for k, v in self.config["KEY"].items() if v==pg.key.name(key)]:
                if action == "up" and self.direction[1]>=0:
                    self.direction -= Vector2(0,1)
                elif action == "down" and self.direction[1]<=0:
                    self.direction -= Vector2(0,-1)
                elif action == "left" and self.direction[0]<=0:
                    self.direction -= Vector2(-1,0)
                elif action == "right" and self.direction[0]>=0:
                    self.direction -= Vector2(1,0)

""" デバッグ用 """
def debug():
    pg.init()
    pg.display.set_mode((160,90))

    Input = InputHandler()

    run = True
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run=False
            elif event.type == pg.KEYDOWN:
                Input.keydown(event.key)
                print(Input.direction)
            elif event.type == pg.KEYUP:
                Input.keyup(event.key)
                print(Input.direction)

    pg.quit()

if __name__ == '__main__':
    debug()