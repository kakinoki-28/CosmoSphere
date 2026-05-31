import pygame
from dataclasses import dataclass, field
import os
from random import randint
import gamelogic

IMAGE_FOLDER = "images"

def load_image(file):
    # 画像読み込み用
    file = os.path.join(IMAGE_FOLDER, file)
    try:
        surface = pygame.image.load(file)
    except:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface

""" 画像Surfaceを保持するクラス """
@dataclass
class ImageAssets:
    stage: dict[str, pygame.Surface] = field(default_factory=dict)        # ステージの画像を保持する辞書
    characters: dict[str, pygame.Surface] = field(default_factory=dict)   # キャラクターの画像を保持する辞書
    module: dict[str, pygame.Surface] = field(default_factory=dict)       # キャラが使用する画像を保持する辞書

    def __post_init__(self):
        # 画像の読み込み
        self.stage = {
            "background": load_image("universe_back.png").convert(),
            "stage": load_image("stage.png").convert()
        }
        self.characters = {
            "red": load_image(os.path.join("character", "red.png")).convert_alpha(),
            "green": load_image(os.path.join("character", "green.png")).convert_alpha()
        }
        self.module = {
            "shield": load_image("shield.png").convert_alpha()
        }

def blit_center(dest, source, pos):
    # 画像を中心に描画するための関数
    rect = source.get_rect(center=pos)
    dest.blit(source, rect)

class GameRenderer:
    def __init__(self):
        self.screen = pygame.Surface((gamelogic.Stage.WIDTH, gamelogic.Stage.HEIGHT)).convert_alpha() 
        self.image_assets = ImageAssets()

    def render(self, window, game_state):
        # 背景の描画
        self.screen.blit(self.image_assets.stage["background"], (0, 0))
        # ステージの描画
        self.screen.blit(self.image_assets.stage["stage"], (0, self.screen.get_height()-game_state.stage.GND_HEIGHT))
        # キャラクターの描画
        for chara in game_state.characters_list:
            chara_image = self.image_assets.characters[chara.color].copy()
            X, Y = round(chara.pos.x), round(chara.pos.y)
            # 無敵時の点滅処理
            if chara.no_damage_count>0:
                ratio = 1-abs(chara.no_damage_count%33-16)/16
                if ratio > 0:
                    white_level = int(128*ratio/2+64)
                    chara_image.fill((white_level, white_level, white_level, 0), special_flags = pygame.BLEND_RGBA_ADD)
            # ヒットストップ時の振動
            if chara.stop_frame != 0:
                shake = int(chara.shake_ratio*chara.stop_count/chara.stop_frame)+1
                shake_x = int( ( (-1)**int((chara.stop_count%4-1)/2) )*(randint(0,int(shake/2))+int(shake/2)))
                shake_y = int( ( (-1)**randint(0,1) )*(randint(0,int(shake/2))+int(shake/2)))
                if chara.on_ground:
                    shake_y = 0
            else:
                shake_x = shake_y = 0
            # キャラの描画
            blit_center(self.screen, chara_image, (X+shake_x, self.screen.get_height()-Y+shake_y))

            # シールド
            if chara.shield.status != "wait":
                shield_image = self.image_assets.module["shield"].copy()
                if chara.shield.radius*2 != shield_image.get_width():
                    shield_image = pygame.transform.smoothscale(shield_image, (chara.shield.radius*2,)*2)
                blit_center(self.screen, shield_image, (X, self.screen.get_height()-Y))
        # 描画の反映
        window.blit(self.screen, (0, 0))
