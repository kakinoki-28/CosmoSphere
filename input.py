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
        self.actions = []

        self.key_map = {}
        # 設定ファイル読み込み
        self.config = configparser.ConfigParser()
        self.config.read("inputconfig.ini")
        # 検証は後で実装

    def __str__(self):
        return f"{self.direction}, {self.skills}, attack={self.attack}, shield={self.shield}"

    def set_input(self, direction:Vector2, skills:list[bool], attack:bool, shield:bool):
        self.direction = direction
        self.skills = skills
        self.attack = attack
        self.shield = shield

    """ 各アクションから抽象入力へ変換 """
    def add_action(self, action):
        self.actions.append(action)
        if action == "up" and self.direction[1]<=0:
            self.direction += Vector2(0,1)
        elif action == "down" and self.direction[1]>=0:
            self.direction += Vector2(0,-1)
        elif action == "left" and self.direction[0]>=0:
            self.direction += Vector2(-1,0)
        elif action == "right" and self.direction[0]<=0:
            self.direction += Vector2(1,0)
        elif action[:5] == "skill":
            self.skills[int(action[5])-1]=True
        elif action == "attack":
            self.attack = True
        elif action == "shield":
            self.shield = True

    def remove_action(self, action):
        self.actions.remove(action)
        if action == "up" and self.direction[1]>0:
            self.direction -= Vector2(0,1)
        elif action == "down" and self.direction[1]<0:
            self.direction -= Vector2(0,-1)
        elif action == "left" and self.direction[0]<0:
            self.direction -= Vector2(-1,0)
        elif action == "right" and self.direction[0]>0:
            self.direction -= Vector2(1,0)
        elif action[:5] == "skill":
            self.skills[int(action[5])-1]=False
        elif action == "attack":
            self.attack = False
        elif action == "shield":
            self.shield = False

    """ キーボード入力からアクションへ変換 """
    def keydown(self, key):
        if pg.key.name(key) in self.config["KEY"].values():
            for action in [k for k, v in self.config["KEY"].items() if v==pg.key.name(key)]:
                if not action in self.actions:
                    self.add_action(action)
            return True
        else:
            return False

    def keyup(self, key):
        if pg.key.name(key) in self.config["KEY"].values():
            for action in [k for k, v in self.config["KEY"].items() if v==pg.key.name(key)]:
                if action in self.actions:
                    self.remove_action(action)
            return True
        else:
            return False

    """ コントローラーボタン入力からアクションへ変換 """
    def buttondown(self, button):
        action = self.config["JOYSTICK"][f"Button{button}"]
        if action!="" and (not action in self.actions):
            self.add_action(action)
            return True
        else:
            return False

    def buttonup(self, button):
        action = self.config["JOYSTICK"][f"Button{button}"]
        if action!="" and action in self.actions:
            self.remove_action(action)
            return True
        else:
            return False

    """ コントローラー軸入力からアクションへ変換 """
    def axismove(self, axis, value):
        action = self.config["JOYSTICK"][f"Axis{axis}"]
        threshold = float(self.config["JOYSTICK"]["threshold"])
        if action=="0":
            if (not "right" in self.actions) and value >= threshold:
                self.add_action("right")
            elif (not "left" in self.actions) and value <= -threshold:
                self.add_action("left")
            elif "right" in self.actions and value < threshold:
                self.remove_action("right")
            elif "left" in self.actions and value > -threshold:
                self.remove_action("left")
            else:
                return False
            return True
        elif action=="1":
            if (not "down" in self.actions) and value >= threshold:
                self.add_action("down")
            elif (not "up" in self.actions) and value <= -threshold:
                self.add_action("up")
            elif "down" in self.actions and value < threshold:
                self.remove_action("down")
            elif "up" in self.actions and value > -threshold:
                self.remove_action("up")
            else:
                return False
            return True
        elif action!="":
            if (not action in self.actions) and value >= threshold:
                self.add_action(action)
            elif action in self.actions and value < threshold:
                self.remove_action(action)
            else:
                return False
            return True
        else:
            return False

    """ コントローラーハットボタン入力から入力へ変換 """
    def hatmove(self, hat, value):
        using = self.config["JOYSTICK"][f"Hat{hat}"]
        if using:
            self.direction.update(value)
            return True
        return False


""" デバッグ用関数 """
def debug():
    pg.init()
    pg.display.set_mode((160,90))

    Input = InputHandler()
    joysticks = {}
    input_changed=False

    run = True
    while run:
        input_changed=False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run=False
            elif event.type == pg.KEYDOWN:
                if Input.keydown(event.key):
                    input_changed = True
            elif event.type == pg.KEYUP:
                if Input.keyup(event.key):
                    input_changed = True
            elif event.type == pg.JOYDEVICEADDED:
                joy = pg.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"{joy.get_name()} connencted!")
            elif event.type == pg.JOYDEVICEREMOVED:
                print(f"{joysticks[event.instance_id].get_name()} disconnected!")
                del joysticks[event.instance_id]
            elif event.type == pg.JOYBUTTONDOWN:
                if Input.buttondown(event.button):
                    input_changed = True
            elif event.type == pg.JOYBUTTONUP:
                if Input.buttonup(event.button):
                    input_changed = True
            elif event.type == pg.JOYAXISMOTION:
                if Input.axismove(event.axis, event.value):
                    input_changed = True
            elif event.type == pg.JOYHATMOTION:
                if Input.hatmove(event.hat, event.value):
                    input_changed = True

        if input_changed:
            print(Input)


    pg.quit()

if __name__ == '__main__':
    debug()