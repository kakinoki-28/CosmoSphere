import pygame as pg
from pygame.math import Vector2
import configparser

class InputHandler:
    """ 各具象入力を抽象入力に変換するクラス """
    FILENAME = "inputconfig.ini"
    def __init__(self):
        self.direction = Vector2(0, 0)
        self.skills = [False] * 3
        self.attack = False
        self.shield = False
        self.actions = []

        # 設定ファイル読み込み
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.load_config()
        # 検証は後で実装

    def __str__(self):
        return f"{self.direction}, {self.skills}, attack={self.attack}, shield={self.shield}"
    
    def copy(self):
        new_handler = InputHandler()
        new_handler.direction = self.direction.copy()
        new_handler.skills = self.skills.copy()
        new_handler.attack = self.attack
        new_handler.shield = self.shield
        new_handler.actions = self.actions.copy()
        return new_handler

    def set_input(self, direction:Vector2, skills:list[bool], attack:bool, shield:bool):
        self.direction = direction
        self.skills = skills
        self.attack = attack
        self.shield = shield

    def get_direction(self):
        return self.direction

    def get_skills(self):
        return self.skills

    def get_attack(self):
        return self.attack

    def get_shield(self):
        return self.shield

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
            depth = float(self.config["JOYSTICK"]["depth"])
            if (not action in self.actions) and value >= depth:
                self.add_action(action)
            elif action in self.actions and value < depth:
                self.remove_action(action)
            else:
                return False
            return True
        else:
            return False

    """ コントローラーハットボタン入力から入力へ変換 """
    def hatmove(self, hat, value):
        using = bool(self.config["JOYSTICK"][f"Hat{hat}"])
        if using:
            self.direction.update(value)
            return True
        return False


    """コントローラー接続時に未設定の処理を追加"""
    def connect_joy(self, num_button, num_axis, num_hat):
        buttons = [k for k in self.config["JOYSTICK"].keys() if "Button" in k]
        axis = [k for k in self.config["JOYSTICK"].keys() if "Axis" in k]
        hats = [k for k in self.config["JOYSTICK"].keys() if "Hat" in k]
        if len(buttons) < num_button:
            for i in range(len(buttons), num_button):
                self.config["JOYSTICK"][f"Button{i}"]=""
        if len(axis) < num_axis:
            for i in range(len(axis),num_axis):
                self.config["JOYSTICK"][f"Axis{i}"]=""
        if len(hats) < num_hat:
            for i in range(len(hats),num_hat):
                self.config["JOYSTICK"][f"Hat{i}"]=""
        if not "depth" in self.config["JOYSTICK"]:
            self.config["JOYSTICK"]["depth"]=0
        if not "threshold" in self.config["JOYSTICK"]:
            self.config["JOYSTICK"]["depth"]=0.5


    """ファイルから入力設定を読み込み"""
    def load_config(self):
        self.config.read(self.FILENAME)

    """入力設定をファイルに更新"""
    def save_config(self):
        with open(self.FILENAME, 'w') as configfile:
            self.config.write(configfile, False)


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
                Input.connect_joy(joy.get_numbuttons(), joy.get_numaxes(), joy.get_numhats())
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

    Input.save_config()
    pg.quit()

if __name__ == '__main__':
    debug()