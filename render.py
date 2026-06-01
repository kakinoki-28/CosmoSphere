import pygame
from dataclasses import dataclass, field
import os
import math
from random import randint
import gamelogic

IMAGE_FOLDER = "images"

SILVER = (192, 192, 192)

def load_image(file):
    # 画像読み込み用
    file = os.path.join(IMAGE_FOLDER, file)
    try:
        surface = pygame.image.load(file)
    except:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface

""" おうぎ形を描画する関数 """
def draw_pie(screen, color, pos, radius, angle, angle_range):
    import pygame.gfxdraw
    p=[pos]
    for n in range(angle-angle_range,angle+angle_range):
        x = pos[0]+round(radius*math.sin(n*math.pi/180))
        y = pos[1]-round(radius*math.cos(n*math.pi/180))
        p.append((x, y))
    pygame.gfxdraw.filled_polygon(screen, p, color)
    pygame.gfxdraw.aapolygon(screen, p, color)

""" 画像Surfaceを保持するクラス """
@dataclass
class ImageAssets:
    stage: dict[str, pygame.Surface] = field(default_factory=dict)      # ステージの画像を保持する辞書
    character: dict[str, pygame.Surface] = field(default_factory=dict)  # キャラクターの画像を保持する辞書
    shield: dict[str, pygame.Surface] = field(default_factory=dict)     # シールドの画像
    melee: dict[str, pygame.Surface] = field(default_factory=dict)      # 近接攻撃の画像を保持する辞書
    bullet: dict[str, pygame.Surface] = field(default_factory=dict)     # キャラが使用する弾の画像を保持する辞書
    effect: dict[str, pygame.Surface] = field(default_factory=dict)     # エフェクトの画像を保持する辞書

    def __post_init__(self):
        # 画像の読み込み
        self.stage = {
            "background": load_image("universe_back.png").convert(),
            "stage": load_image("stage.png").convert(),
            "platform": load_image("platform.png").convert_alpha()
        }
        self.character = {
            "red": load_image(os.path.join("character", "red.png")).convert_alpha(),
            "green": load_image(os.path.join("character", "green.png")).convert_alpha()
        }
        self.shield = {
            "default": load_image("shield.png").convert_alpha()
        }
        self.melee = {
            "hammer": load_image("hammer.png").convert_alpha()
        }
        self.bullet = {
            "liner_bullet": load_image("liner_bullet.png").convert_alpha(),
            "drone": load_image("drone.png").convert_alpha(),
            "sync_bullet": load_image("sync_bullet.png").convert_alpha()
        }
        self.effect = {
            "airjump": load_image("airjump.png").convert_alpha()
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
        # 台の描画
        for platform in game_state.stage.platforms:
            self.screen.blit(self.image_assets.stage["platform"], (platform.x[0], self.screen.get_height()-platform.y))
        
        # エフェクト表示
        for chara in game_state.characters_list:
            for effect in chara.effects:
                effect_image = self.image_assets.effect[effect.name].copy()
                # エフェクト別処理
                if effect.name == "airjump":
                    effect_image = pygame.transform.smoothscale(effect_image, (20+int(4*effect.count), 8+int(effect.count/2)))
                    if effect.count >= 4:
                        effect_image.set_alpha(255-int(240*(effect.count-4)/6))
                    else:
                        effect_image.set_alpha(255)
                self.screen.blit(effect_image, dest=(effect.pos.x-int(effect_image.get_width()/2), self.screen.get_height()-effect.pos.y-int(effect_image.get_height()/2)))


        # キャラクターの描画
        for chara in game_state.characters_list:
            chara_image = self.image_assets.character[chara.color].copy()
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
            X, Y = round(chara.pos + (shake_x, shake_y))
            blit_center(self.screen, chara_image, (X, self.screen.get_height()-Y))

            # シールド
            if chara.shield.status != "wait":
                shield_image = self.image_assets.shield["default"].copy()
                if chara.shield.radius*2 != shield_image.get_width():
                    shield_image = pygame.transform.smoothscale(shield_image, (chara.shield.radius*2,)*2)
                blit_center(self.screen, shield_image, (X, self.screen.get_height()-Y))
        # 攻撃系の描画
        for chara in game_state.characters_list:
            # 反射した弾の描画
            for bullet in chara.shield.hitback_bullets:
                if bullet.display:
                    blit_center(self.screen, self.image_assets.bullet[bullet.CONST.name], (bullet.pos.x, self.screen.get_height()-bullet.pos.y))
            if chara.color == "red":
                # 近接攻撃の描画
                if chara.hammer.active:
                    hammer_image = self.image_assets.melee["hammer"].copy()
                    if chara.hammer.angle != 0:
                        hammer_image = pygame.transform.rotozoom(hammer_image, -chara.hammer.angle, 1)
                    root_pos = round(chara.pos)+(chara.hammer.offset)
                    hammer_pos = root_pos+pygame.Vector2(0, hammer_image.get_height()//2).rotate(-chara.hammer.angle)
                    blit_center(self.screen, hammer_image, (hammer_pos.x, self.screen.get_height()-hammer_pos.y))
                # スキル1:エネルギーガン
                if not (chara.energy_gun.status == "wait" or chara.energy_gun.status == "wait_interval"):
                    draw_pie(self.screen, SILVER, (chara.pos.x, self.screen.get_height()-chara.pos.y), 
                             40+10*chara.energy_gun.charge_count/chara.energy_gun.CONST.charge, 
                             round(chara.energy_gun.angle), round(chara.energy_gun.angle_range))
                    if chara.energy_gun.angle == 0:
                        print(f"status: {chara.energy_gun.status}, charge: {chara.energy_gun.charge_count}, angle: {chara.energy_gun.angle}, angle_range: {chara.energy_gun.angle_range}")
                for bullet in chara.energy_gun.magazine:
                    if bullet.display:
                        blit_center(self.screen, self.image_assets.bullet[bullet.CONST.name], (bullet.pos.x, self.screen.get_height()-bullet.pos.y))
                # スキル2:ドローン
                for drone in chara.drone.magazine:
                    if drone.active or drone.wait:
                        blit_center(self.screen, self.image_assets.bullet["drone"], (drone.pos.x, self.screen.get_height()-drone.pos.y))
                # スキル3:時止め弾
                for bullet in chara.sync_shot.magazine:
                    if bullet.display:
                        blit_center(self.screen, self.image_assets.bullet[bullet.CONST.name], (bullet.pos.x, self.screen.get_height()-bullet.pos.y))
                    
        # 描画の反映
        window.blit(self.screen, (0, 0))
