from pygame.math import lerp, Vector2
from ctypes import windll
from time import perf_counter, sleep
from input import InputHandler
import gameconst


class GameManeger:
    """ ゲーム進行全体の管理 """
    FPS = 64
    FRAME_LATENCY = 1/FPS

    def __init__(self):
        self.init_game()

    """ 初期化 """
    def init_game(self):
        self.run = True
        def pass_func(frame):
            pass
        self.update_func = pass_func
        self.frame_rate = 0

        self.stage = Stage()
        self.characters = []
        self.available_color = ["red", "green"]


    """ キャラの追加 """
    def add_character(self, color):
        character = Character(color=color)
        self.characters.append(character)
        for chara in self.characters:
            chara.target_list = [_ for _ in self.characters if _ != chara]

        return character

    """ キャラの削除 """
    def remove_character(self, character):
        self.characters.remove(character)
        for chara in self.characters:
            chara.target_list = [_ for _ in self.characters if _ != chara]

    """ フレームを更新して生成 """
    def update_frame(self):
        frame = ""
        self.stage.update()
        #frame += self.stage.frame
        # リスト順による判定の優先順位を排除するためキャラ情報を優先して更新
        for chara in self.characters:
            chara.update(self.stage)
        for chara in self.characters:
            chara.objects_update(self.stage)
            frame += chara.frame
        return frame.encode()


    """ ゲームのメイン処理 """
    def mainloop(self):
        # タイマーの精度向上
        windll.winmm.timeBeginPeriod(1)
        frame_time = [perf_counter()]*2
        delay = 0
        while self.run:
            start = perf_counter()

            # フレームupdate
            frame = self.update_frame()

            # フレーム毎実行処理
            self.update_func(frame)

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

class Stage:
    """ ステージ全体の情報の管理 """
    WIDTH = 1280
    HEIGHT = 720
    GND_HEIGHT = 100
    def __init__(self):
        self.init_stage()

    def init_stage(self):
        self.platforms = []
        self.platforms.append( Platform(self.WIDTH*1/4-210/2-15, self.WIDTH*1/4+210/2-15, self.GND_HEIGHT+120) )
        self.platforms.append( Platform(self.WIDTH*2/4-210/2,    self.WIDTH*2/4-210/2,    self.GND_HEIGHT+210) )
        self.platforms.append( Platform(self.WIDTH*3/4-210/2+15, self.WIDTH*3/4+210/2+15, self.GND_HEIGHT+120) )


    def update(self):
        pass

    def get_platforms(self):
        return self.platforms

class Platform:
    """ 空中に浮く台 """
    EDGE_WIDTH = 10
    THICK = 10
    def __init__(self,x1,x2,y):
        self.x = [round(x1), round(x2)]
        self.y = round(y)

    def __contains__(self, item:Vector2):
        return (self.x[0]-self.EDGE_WIDTH <= item[0] <= self.x[1]+self.EDGE_WIDTH and self.y-self.THICK <= item[1] <= self.y)

    def is_above(self, item:Vector2):
        return (self.x[0]-self.EDGE_WIDTH <= item[0] <= self.x[1]+self.EDGE_WIDTH and self.y <= item[1])

    def is_below(self, item:Vector2):
        return (self.x[0]-self.EDGE_WIDTH <= item[0] <= self.x[1]+self.EDGE_WIDTH and item[1] <= self.y-self.THICK)


class GameObject:
    def __init__(self, pos:Vector2, speed:Vector2):
        self.pos = pos
        self.speed = speed

    def update(self):
        self.pos += self.speed


class Character(GameObject):
    def __init__(self, color, my_id="", input=InputHandler()):
        self.CONST = gameconst.CharacterConst()

        self.color = color
        self.radius = self.CONST.radius

        self.id = my_id
        GameObject.__init__( self, Vector2(Stage.WIDTH/4, Stage.GND_HEIGHT+self.radius), Vector2(0,0) )

        self.on_platform = False
        self.on_ground = True
        self.hopping = False        # 跳ね返り
        self.double_jumped = False
        self.restrict_jump = False
        self.jump_interval = 0      # 2段ジャンプまでの間隔

        self.hp = self.CONST.hp_max
        self.combo = 0
        self.combo_count = 0        # コンボ継続時間
        self.no_damage_count = 0    # 無敵継続時間
        self.blowed = False         # 吹っ飛ばされ判定
        self.after_blow_count = 0   # 吹っ飛び直後の特殊動作のカウント
        self.target_list = []
        self.action_busy = False

        self.stop_frame = 0     # ヒットストップする時間を保存
        self.stop_count = 0     # ヒットストップをカウント
        self.shake_ratio = 0
        self.shake_x = 0
        self.shake_y = 0

        self.effects = []
        self.sounds = []
        self.Input = InputHandler()

        # 戦闘機能
        self.shield = Shield(user=self)
        if self.color == "red":
            # 射撃
            self.energy_gun = EnergyGun(user=self)
            self.drone = DroneManager(user=self)
            self.sync_shot = SynchroShot(user=self)
            # ハンマー攻撃
            self.hammer = Hammer(user=self)

    @property
    def frame(self):
        # ヒットストップ時の振動
        if self.stop_frame != 0:
            shake = int(self.shake_ratio*self.stop_count/self.stop_frame)+1
            self.shake_x = int( ((-1)**int((self.stop_count%4-1)/2) )*(random.randint(0,int(shake/2))+int(shake/2)))
            self.shake_y = int( ((-1)**int((self.stop_count%4-1)/2) )*(random.randint(0,int(shake/2))+int(shake/2)))
            if self.on_ground:
                self.shake_y = 0
        else:
            self.shake_x = self.shake_y = 0

        frame = "player,"+ self.color +"," + str(self.hp) +"," + str(self.HP_MAX) +","
        frame += str(round(self.pos.x)+self.shake_x)+","+str(round(self.pos.y)+self.shake_y)+","
        frame += self.motion_id +","+ str(self.motion_count) +","
        frame += str(self.combo_count) +","+ str(self.no_damage_count) + "\n"

        for ef in self.effects:
            frame += ef.frame
        frame += self.shield.frame
        if self.color == "red":
            frame += self.energy_gun.frame
            frame += self.drone.frame
            frame += self.sync_shot.frame
            frame += self.hammer.frame

        return frame

    @property
    def motion_id(self):
        if self.motion == "none":
            return "0"
        elif self.motion == "bounce":
            return "1"
        elif self.motion == "airjump":
            return "2"

    """ 入力の処理 """
    def input_update(self, new_input:InputHandler):

        #近接攻撃 KeyDown
        if (new_input.attack==True and self.Input.attack==False) and (not self.action_busy or self.shield.status=="recovery"):
            if self.color =="red":
                self.hammer.start()
        #近接攻撃 KeyUp
        if (self.Input.attack==True and new_input.attack==False) and (not self.action_busy or self.shield.status=="recovery"):
            pass

        #シールド KeyDown
        if (new_input.shield==True and self.Input.shield==False) and (not self.action_busy or self.shield.status!="wait") and self.no_damage_count==0:
            self.shield.shield_start()
        #シールド KeyUp
        if (self.Input.shield==True and new_input.shield==False):
            self.shield.shield_stop()

        #スキル1 KeyDown
        if (new_input.skills[0]==True and self.Input.skills[0]==False):
            if self.color =="red" and not self.action_busy:
                self.energy_gun.lockon()
        #スキル1 KeyUp
        if (self.Input.skills[0]==True and new_input.skills[0]==False):
            if self.color =="red":
                self.energy_gun.shoot()

        #スキル2 KeyDown
        if (new_input.skills[1]==True and self.Input.skills[1]==False):
            if self.color =="red" and not self.action_busy:
                self.drone.throw_start()
        #スキル2 KeyUp
        if (self.Input.skills[1]==True and new_input.skills[1]==False):
            pass

        #スキル3 KeyDown
        if (new_input.skills[2]==True and self.Input.skills[2]==False):
            if self.color =="red" and (self.sync_shot.shoot_count==self.sync_shot.BULLET_MAX or not self.action_busy):
                self.sync_shot.shoot()
        #スキル2 KeyUp
        if (self.Input.skills[2]==True and new_input.skills[2]==False):
            pass

        self.Input = new_input

    """ 音声情報の追加 """
    def set_sound(self, name):
        self.sounds.append(name)

    """ ヒットストップの設定 """
    def set_stop(self, stop, shake = 0):
        self.stop_count = self.stop_frame = int(stop)
        self.shake_ratio = shake

    """ フレーム毎の更新処理 """
    def update(self, stage:Stage):

        # エフェクト更新
        for ef in self.effects:
            ef.update()
            if not ef.active:
                self.effects.remove(ef)

        # ヒットストップ更新
        if self.stop_count:
            self.stop_count -= 1
            return None
        else:
            self.stop_frame = 0

        # ダメージ直後カウント更新
        if self.after_blow_count>0:
            self.after_blow_count -= 1
        # コンボ継続時間更新
        if self.combo_count>0:
            self.combo_count -= 1
        # 無敵継続時間更新
        elif self.no_damage_count>0:
            self.no_damage_count -= 1
            if self.no_damage_count == 0 and (self.on_ground==False or self.blowed):
                self.no_damage_count = 1
        if self.combo_count==0:
            self.combo = 0

        # シールド継続入力受付
        if self.Input.shield and (not self.action_busy and self.no_damage_count==0):
            self.shield.shield_start()

        # 物理演算
        if self.on_ground:
            # 接地時の判定リセット
            self.hopping = False
            self.jump_interval = 0
            self.double_jumped = False
            # 吹っ飛び判定更新
            if abs(self.speed.x)<self.CONST.speed_max:
                self.blowed = False
            # 跳ね
            if self.speed.y<0:
                self.speed.y = round(abs(self.speed.y)/2)
                if self.speed.y != 0:
                    self.hopping = True
            # 摩擦
            if self.speed.x>0:
                self.speed.x -= self.CONST.friction
                if self.speed.x < self.CONST.friction*2:
                    self.speed.x=0
            elif self.speed.x<0:
                self.speed.x += self.CONST.friction
                if self.speed.x > -self.CONST.friction*2:
                    self.speed.x=0
            # 動力
            if self.Input.direction.x==1:
                # 初速条件 = (水平速度が小さい　もしくは　(跳ねてる　かつ　初速以下))
                if (abs(self.speed.x) < self.CONST.start_condition or (self.hopping and self.speed.x<self.CONST.start_speed)):
                    self.speed.x = self.CONST.start_speed
                else:
                    if self.speed.x>0:
                        self.speed.x += self.CONST.accelarate + self.CONST.friction
                    else:
                        self.speed.x += self.CONST.accelarate
                self.speed.x = min(self.speed.x, self.CONST.speed_max)
            if self.Input.direction.x==-1:
                if (abs(self.speed.x) < self.CONST.start_condition or (self.hopping and self.speed.x>-self.CONST.start_speed)):
                    self.speed.x = -self.CONST.start_speed
                else:
                    if self.speed.x<0:
                        self.speed.x -= self.CONST.accelarate + self.CONST.friction
                    else:
                        self.speed.x -= self.CONST.accelarate
                self.speed.x = max(self.speed.x, -self.CONST.speed_max)
            # ジャンプ
            if self.Input.direction.y==1 and self.hopping==False:
                self.jump_interval = self.CONST.next_jump_interval
                if self.restrict_jump:
                    self.speed.y = self.CONST.restrict_jump
                else:
                    if self.on_platform:
                        self.speed.y = self.CONST.platform_jump
                    else:
                        self.speed.y = self.CONST.normal_jump
            # ステージからの飛び降り
            if self.on_platform and self.Input.direction.y==-1:
                self.speed.y += self.CONST.drop_speed
        else:
            if self.jump_interval>0:
                self.jump_interval -= 1
            # 重力
            if self.after_blow_count>0:
                self.speed.y -= 3/2
            elif self.hopping == False:
                if -1/4 < self.speed.y <= 0:
                    self.speed.y -= 1/8
                elif -3/4 < self.speed.y <= -1/4:
                    self.speed.y -= 1/4
                elif -7/4 < self.speed.y <= -3/4:
                    self.speed.y -= 1/2
                elif -13/4 < self.speed.y <= -7/4:
                    self.speed.y -= 3/4
                elif -5 < self.speed.y <= -13/4:
                    self.speed.y -= 7/8
                elif -30 < self.speed.y:
                    self.speed.y -= self.CONST.gravity
            else:
                self.speed.y -= self.CONST.gravity
            # 空気抵抗(吹っ飛び時)
            if self.blowed:
                if self.after_blow_count>0:
                    grip_ratio = self.CONST.grip_weak
                elif abs(self.speed.x)>self.CONST.speed_max:
                    grip_ratio = self.CONST.grip_strong
                else:
                    grip_ratio = 0
                if self.speed.x>0:
                    self.speed.x -= grip_ratio
                elif self.speed.x<0:
                    self.speed.x += grip_ratio
            # 空中ジャンプ
            if self.Input.direction.y==1 and not self.double_jumped and self.jump_interval==0 and not self.hopping and not self.restrict_jump:
                self.speed.y = self.CONST.air_jump
                self.double_jumped = True
                self.effects.append(Effect("airjump", self.pos))
            # 動力(跳ね・吹っ飛び時のみ)
            jump_height = self.pos.y-self.radius-stage.GND_HEIGHT
            if (self.hopping and jump_height < self.CONST.hopping_height) or self.blowed:
                if self.Input.direction.x==1 and self.speed.x<self.CONST.speed_max:
                    self.speed.x += self.CONST.air_power
                    self.speed.x = min(self.speed.x, self.CONST.speed_max)
                elif self.Input.direction.x==-1 and self.speed.x>-self.CONST.speed_max:
                    self.speed.x -= self.CONST.air_power
                    self.speed.x = max(self.speed.x, -self.CONST.speed_max)

        # 座標更新
        GameObject.update()

        # 座標を調整
        if self.pos.x < self.radius:
            self.pos.x = self.radius
            if self.blowed:
                self.speed.x *= -1
                self.speed.y += 10
        elif self.pos.x > stage.WIDTH-self.radius:
            self.pos.x = stage.WIDTH-self.radius
            if self.blowed:
                self.speed.x *= -1
                self.speed.y += 10
        # 接地判定
        if self.pos.y-self.radius <= stage.GND_HEIGHT:
            self.on_ground = True
            self.on_platform = False
            self.pos.y = stage.GND_HEIGHT + self.radius
        else:
            for platform in stage.platforms:
                foot_pos = self.pos-Vector2(0, self.radius)
                last_pos = foot_pos-self.speed
                if (foot_pos in platform or (platform.is_above(last_pos) and platform.is_below(foot_pos))) and self.speed.y<=0 and not self.Input.direction.y==-1:
                    self.on_ground = True
                    self.on_platform = True
                    self.pos.y = platform.y+self.radius
                    break
            else:
                self.on_ground = False
                self.on_platform = False

    def objects_update(self, stage:Stage):
        self.shield.update()
        if self.color == "red":
            self.hammer.update()
            self.energy_gun.update(stage)
            self.drone.update(stage)
            self.sync_shot.update(stage)

    """ くらい判定の確認をする 返り値:当たったオブジェクトのリスト """
    def hit_check(self, pos:Vector2, r:int, anti_bullet:bool=False, anti_shield:bool=False) -> list[GameObject]:
        hit_objects = []
        hit_objects += self.shield.hit_check(pos, r, anti_bullet=anti_bullet, anti_shield=anti_shield)

        if self.shield.status != "guard" and self.pos.distance_to(pos) < self.radius+r:
            hit_objects.append(self)

        if self.color == "red":
            hit_objects += self.energy_gun.hit_check(pos, r, anti_bullet=anti_bullet, anti_shield=anti_shield)
            hit_objects += self.drone.hit_check(pos, r, anti_bullet=anti_bullet, anti_shield=anti_shield)
            hit_objects += self.sync_shot.hit_check(pos, r, anti_bullet=anti_bullet, anti_shield=anti_shield)
        return hit_objects


    """ ダメージとコンボの処理を行う """
    def damage_process(self, damage:int):
        # 初撃
        if self.no_damage_count==0:
            self.hp -= damage
            self.blowed = True
            self.hammer.reset()
            self.combo += 1
        # コンボ
        elif self.combo_count>0:
            print(f"{self.combo} Combo Damage : {damage}→{int(damage/(self.combo+1))}")
            self.hp -= int(damage/(self.combo+1))
            self.combo += 1


# エフェクト
class Effect:
    def __init__(self, name:str, pos:Vector2):
        self.name = name
        self.pos = pos
        self.count = 0
        self.active = True

    @property
    def frame(self):
        if self.active:
            return "effect"+","+ self.name+","+str(round(self.pos[0]))+","+str(round(self.pos[1]))+","+str(self.count)+"\n"

    def update(self):
        self.count += 1
        if self.name == "airjump" and self.count>10:
            self.active = False

#当たり判定
class Collision_Circle:
    def __init__(self, leng, gap, r, damage):
        self._length = leng
        self._normal_gap = gap  #法線ギャップ
        self._radius = r
        self._damage = damage

    @property
    def length(self):
        return self._length

    @property
    def normal_gap(self):
        return self._normal_gap

    @property
    def radius(self):
        return self._radius

    @property
    def damage(self):
        return self._damage

    def pos(self, pos:Vector2, angle:float):
        return Vector2(0,1).rotate(-angle)*self.length + Vector2(1,0).rotate(-angle)*self.normal_gap


#ここまで完了

# シールド
class Shield:
    def __init__(self, user):
        # 定数
        self.CONST = gameconst.ShieldConst
        # 変数
        self.status = "wait"
        self.user = user
        self.pos = self.user.pos.copy()
        self.radius = self.CONST.radius_first
        self.startup_count = 0
        self.instant_count = 0
        self.recovery_count = 0
        self.hitback_bullets = []

    @property
    def frame(self):
        frame = "shield,"+ self.status +","+ str(round(self.radius)) +"\n"
        for bullet in self.hitback_bullets:
            frame += bullet.frame

        return frame

    """ 入力開始時 """
    def shield_start(self):
        if self.status != "guard":
            self.status = "start_up"
            if self.radius != 0:
                self.startup_count = self.radius/self.CONST.radius_max*self.CONST.startup
        self.user.action_busy = True

    """ 入力終了時 """
    def shield_stop(self):
        if self.status == "start_up" or self.status == "wait":
            self.reset()
        else:
            self.status = "recovery"
            self.startup_count = 0
            self.recovery_count = 0

    def reset(self):
        self.status = "wait"
        self.user.action_busy = False
        self.user.restrict_jump = False
        self.radius = self.CONST.radius_first
        self.startup_count = 0
        self.instant_count = 0
        self.recovery_count = 0

    def hit_check(self, pos, r, anti_bullet=False, anti_shield=False):
        hit_objects = []
        if anti_shield and self.pos.distance_to(pos) < self.radius+r and self.status != "wait":
            hit_objects.append(self)
        for bullet in self.hitback_bullets:
            hit_objects += bullet.hit_check(pos, r, anti_bullet=anti_bullet)

        return hit_objects

    def damage_process(self, damage:int):
        self.reset()
        if self.user.hp > damage:
            self.user.hp -= int(damage/2)


    # シールド判定
    def attack(self):
        # ヒット処理
        for enemy in self.user.target_list:
            # 相手のオブジェクトと衝突判定
            for target in enemy.hit_check(self.pos, self.radius, anti_bullet=True):
                # 弾
                if isinstance(target,Bullet):
                    if target.bounced:
                        target.active = False
                    else:
                        target.bounced = True
                        # 反射位置の調整（互いのキャラが接近中は無効）
                        if self.pos.distance_to(target.user.pos) >= self.radius:
                            if (target.pos-self.pos).length() == 0:
                                target.pos += Vector2(1,0)*(self.radius+target.radius) - (target.pos-self.pos)
                            else:
                                target.pos += (target.pos-self.pos).normalize()*(self.radius+target.radius) - (target.pos-self.pos)

                        # 相手の予測位置へ反射
                        enemy_predict_pos = target.user.pos + target.user.speed - target.pos
                        # 反射するための前処理
                        target.time = 0
                        self.hitback_bullets.append(target)
                        target.user = self.user
                        target.no_damage_count=8
                        # 反射速度を加算(キャラへ反射)
                        target.speed = 1.1*target.speed.length()*enemy_predict_pos

                elif type(target)==Drone:
                    target.active = False

    def update(self):
        self.pos = self.user.pos.copy()
        # 発動前
        if self.status == "start_up":
            if self.startup_count < self.STARTUP:
                self.radius += (self.RADIUS_MAX-self.radius)/(self.STARTUP-self.startup_count)
                self.startup_count += 1
            else:
                self.status = "guard"
                self.user.restrict_jump = True
        # 発動中
        elif self.status == "guard":
            self.radius = self.RADIUS_MAX
            self.attack()
            if self.instant_count < self.INSTANT_BLOCK:
                self.instant_count += 1
        # 発動後
        elif self.status == "recovery":
            if self.recovery_count < self.RECOVERY:
                self.recovery_count += 1
                self.radius -= (self.RADIUS_MAX-self.user.radius)/self.RECOVERY
            else:
                self.reset()

        for bullet in self.hitback_bullets:
            bullet.update()
            if not bullet.active and not bullet.display:
                self.hitback_bullets.remove(bullet)

# 共通弾
class Bullet:
    def __init__(self, name, user, speed, angle, damage):
        # 定数
        self.MAX_TIME = 40
        self.name = name
        self.user = user
        self.SPEED = speed
        self.COMBO_INTERVAL = 0
        self.angle = angle
        self.radius = 10
        # 変数
        self.x = user.x
        self.y = user.y
        self.hp = 10
        self.speed_x = speed*math.sin(math.radians(angle))
        self.speed_y = speed*math.cos(math.radians(angle))
        self.time = 0
        self.active = True
        self.display = True
        self.hitwait_count = 0
        self.no_damage_count = 0
        self.bounced = False
        self.Hit_circle = Collision_Circle(0, 0, self.radius, damage)

    @property
    def frame(self):
        if self.display:
            return "bullet," + self.name +","+ str(round(self.x)) +","+ str(round(self.y)) +","+ str(round(self.angle))+"\n"
        else:
            return ""

    def hit_check(self, pos, r, damage, anti_bullet=False, anti_shield=False):
        if anti_bullet and distance(pos, (self.x, self.y)) < self.radius+r and self.active and self.no_damage_count==0:
            self.hp -= damage
            return [self]
        else:
            return []

    def update(self):
        if self.active:
            self.attack()
            if self.no_damage_count>0:
                self.no_damage_count-=1
            self.x += self.speed_x
            self.y += self.speed_y
            # 台衝突判定
            for each in STAGE:
                if ((self.y-self.speed_y <= each.y-self.radius <= self.y)
                 or (self.y <= each.y+self.radius <= self.y-self.speed_y)) and self.x in each:
                    if self.bounced:
                        self.active = False
                    else:
                        self.speed_y *= -1
                        self.y += self.speed_y
                        self.bounced = True
                    break
            if self.y-self.radius <GND_HEIGHT:
                if self.bounced:
                    self.active = False
                else:
                    self.speed_y *= -1
                    self.bounced = True
            self.time += 1
            if self.hp<0 or self.time>self.MAX_TIME:
                self.active = False
        else:
            if self.hitwait_count>0:
                self.hitwait_count -= 1
            else:
                self.display = False

    def attack(self):
        x,y = self.Hit_circle.pos(self.x, self.y, self.angle)
        damage_ratio = self.Hit_circle.damage/10
        #ターゲット探索
        for enemy in self.user.target_list:
            # 相手のオブジェクトと衝突判定
            for target in enemy.hit_check((x,y), self.Hit_circle.radius, self.Hit_circle.damage, anti_bullet=True):
                # キャラに当たった
                if type(target) == Character:
                    # 無敵処理
                    target.no_damage_count = 16
                    target.combo_count = self.COMBO_INTERVAL
                    # ヒットストップ処理
                    target.set_stop(8*damage_ratio, 8*damage_ratio)
                    self.hitwait_count = int(8*damage_ratio/2)
                self.active = False

# ハンマー攻撃(赤近接)
class Hammer:
    def __init__(self, user):
        # 定数
        self.INTERVAL = 16  # frames
        self.FRAME_DATA = []
        with open("Hammer_data.txt") as f:
            self.STARTUP, self.ATTACKING, self.RECOVERY = [int(_) for _ in f.readline().rstrip('\n').split(',')]
            for line in f:
                value = [int(_) for _ in line.rstrip('\n').split(',')]
                self.FRAME_DATA.append(((value[0],value[1]), value[2]))

        # 変数
        self.active = False
        self.motion_count = -1
        self.motion = "none"
        self.interval = 0
        self.user = user
        self.distance_ratio = 1
        self.direction = "right"

        self.offset = (0,0)
        self.angle = self.degree = 0
        self.Hit_circle = [Collision_Circle(88, 0, 35, 40), Collision_Circle(38, 0, 15, 20)]

    @property
    def frame(self):
        if self.active:
            x, y = self.user.x + self.offset[0] + self.user.shake_x, self.user.y + self.offset[1] + self.user.shake_y
            angle = self.degree
            if self.motion == "attack":
                # 食い込み補正
                if self.direction == "left":
                    x -= (1-self.distance_ratio)*(self.offset[0]+self.FRAME_DATA[self.motion_count-1][0][0])
                    angle -= (1-self.distance_ratio)*(self.degree+self.FRAME_DATA[self.motion_count-1][1])
                else:
                    x -= (1-self.distance_ratio)*(self.offset[0]-self.FRAME_DATA[self.motion_count-1][0][0])
                    angle -= (1-self.distance_ratio)*(self.degree-self.FRAME_DATA[self.motion_count-1][1])
                y -= (1-self.distance_ratio)*(self.offset[1]-self.FRAME_DATA[self.motion_count-1][0][1])

            frame = "hammer,"+str(int(x))+","+str(int(y))+","+str(int(angle))+","+self.motion

            if self.motion == "start_up" or self.motion == "none":
                frame += ","+str(self.motion_count)+","+str(self.STARTUP)
            elif self.motion == "attack":
                frame += ","+str(self.motion_count-self.STARTUP)+","+str(self.ATTACKING)
            elif self.motion == "recovery":
                frame += ","+str(self.motion_count-self.STARTUP-self.ATTACKING)+","+str(self.RECOVERY)
            return frame+"\n"
        else:
            return ""

    def reset(self):
        self.active = self.user.action_busy = False
        self.motion_count = -1
        self.motion = "none"

    def start(self):
        if self.active == False and self.interval == 0:
            self.reset()
            self.active = self.user.action_busy = True
            target = closest(self.user, self.user.target_list)
            if target != None and target.x < self.user.x:
                self.direction = "left"
            else:
                self.direction = "right"

    def update(self):
        if self.active and self.user.stop_frame == 0:
            #更新
            self.motion_count += 1
            self.offset = self.FRAME_DATA[self.motion_count][0]
            self.degree = self.FRAME_DATA[self.motion_count][1]
            self.angle = math.radians(self.FRAME_DATA[self.motion_count][1])
            if self.direction == "left":
                self.offset = (-self.FRAME_DATA[self.motion_count][0][0], self.FRAME_DATA[self.motion_count][0][1])
                self.degree *= -1
                self.angle *= -1

            if 0 <= self.motion_count < self.STARTUP:
                # かまえ
                self.motion = "start_up"
            elif self.STARTUP <= self.motion_count < self.STARTUP+self.ATTACKING:
                # 攻撃
                self.motion = "attack"
                # 攻撃処理
                self.attack()
            elif self.STARTUP+self.ATTACKING <= self.motion_count < self.STARTUP+self.ATTACKING+self.RECOVERY:
                # フォロースルー
                self.motion = "recovery"
            else:
                self.interval = self.INTERVAL
                self.reset()
        else:
            if self.interval > 0:
                self.interval -= 1

    def attack(self):
        for each in self.Hit_circle:
            x,y = each.pos(self.user.x+self.offset[0], self.user.y+self.offset[1], self.angle)
            damage_ratio = each.damage/self.Hit_circle[0].damage
            # ヒット処理
            for enemy in self.user.target_list:
                # 相手のオブジェクトと衝突判定
                hit = False
                for target in enemy.hit_check((x,y), each.radius, each.damage, anti_bullet=True, anti_shield=True):
                    hit = True
                    self.distance_ratio = distance((target.x, target.y), (x,y))/(each.radius + target.radius)
                    #相手に当たった
                    if type(target) == Character:
                        # 無敵処理
                        target.no_damage_count = 96
                        target.after_blow_count = 8
                        # ヒットストップ処理
                        target.set_stop(15*damage_ratio, 15*damage_ratio)
                        self.user.set_stop(12*damage_ratio+4, 3*damage_ratio)
                        # 吹っ飛ばし処理
                        target.speed_y += 16
                        if self.direction == "right":
                            target.speed_x += 21
                        elif self.direction == "left":
                            target.speed_x -= 21
                    #シールドに当たった
                    elif type(target) == Shield:
                        # ヒットストップ処理
                        target.user.set_stop(10*damage_ratio+8, 10*damage_ratio)
                        self.user.set_stop(10*damage_ratio, 3*damage_ratio)
                    #他オブジェクトとの衝突
                    else:
                        # ヒットストップ処理
                        self.user.set_stop(4*damage_ratio, 0)
                if not hit:
                    self.distance_ratio = 1

# エネルギー弾射撃(赤スキル1)
class EnergyGun:
    def __init__(self, user):
        # 定数
        self.STARTUP = 12
        self.CHARGE = 24
        self.INTERVAL = 16 # frame
        self.RELOAD = int(GameManeger.FPS*1.5)   # sec

        self.BULLET_MAX = 7
        self.ANGLERANGE_MAX = 15
        self.ANGLERANGE_MIN = 1
        self.ROTATION_SPEED = 360/64

        # 変数
        self.status = "wait"
        self.user = user
        self.target = None
        self.mag = []

        self.startup_count = 0
        self.charge_count = 0
        self.interval_count = 0
        self.reload_count = 0

        self.angle = 0
        self.angle_range = self.ANGLERANGE_MAX

    @property
    def frame(self):
        frame = "egun,"+ self.status +","+ str(round(self.angle)) +","+ str(self.angle_range) +","
        frame += str(self.charge_count) +","+ str(self.CHARGE) +","
        frame += str(len(self.mag)) +","+ str(self.BULLET_MAX) +","
        frame += str(self.reload_count) +","+ str(self.RELOAD) +"\n"

        for bullet in self.mag:
            frame += bullet.frame

        return frame

    def hit_check(self, pos, r, damage, anti_bullet=False, anti_shield=False):
        bullet_list = []
        for bullet in self.mag:
            bullet_list += bullet.hit_check(pos, r, damage, anti_bullet=anti_bullet)
        # ダメージ0のヒットチェックは反射=所有権の移行
        if damage==0:
            for bullet in bullet_list:
                self.mag.remove(bullet)
        return bullet_list

    def update(self):
        if self.reload_count>0:
            self.reload_count -= 1
            if self.reload_count==0:
                for bullet in self.mag:
                    bullet.active = False
                self.mag.clear()
        if self.interval_count>0:
            self.interval_count -= 1
        if self.status=="charge":
            #角度追尾
            x, y = self.target.x - self.user.x, self.target.y - self.user.y
            angle_gap = gap_angle(slope_angle(x,y), self.angle)
            if abs(angle_gap)>self.ROTATION_SPEED:
                if angle_gap>0:
                    self.angle += self.ROTATION_SPEED
                else:
                    self.angle -= self.ROTATION_SPEED
            else:
                self.angle += angle_gap
            if self.charge_count<self.CHARGE:
                self.charge_count += 1
                self.angle_range = self.ANGLERANGE_MAX + int((self.ANGLERANGE_MIN-self.ANGLERANGE_MAX)*self.charge_count/self.CHARGE)
        elif self.status=="lockon" or self.status=="shoot":
            self.startup_count+=1

            x, y = self.target.x - self.user.x, self.target.y - self.user.y
            # y軸基準, -180~180
            if x>=0:
                self.angle = 90+(slope_angle(x,y)-90)*self.startup_count/self.STARTUP
            else:
                self.angle = -90+(slope_angle(x,y)-(-90))*self.startup_count/self.STARTUP

            if self.startup_count==self.STARTUP:
                self.startup_count = 0
                self.charge_start()

        for each in self.mag:
            each.update()

    def lockon(self):
        if self.reload_count==0:
            self.status = "lockon"
            self.user.action_busy = True
            self.angle = 0
            self.target = closest(self.user, self.user.target_list)
            if self.target is None:
                self.target = self.user

    def charge_start(self):
        if self.status=="shoot":
            self.shoot()
        else:
            self.status = "charge"

    def shoot(self):
        if self.reload_count==0:
            if self.status=="lockon" or self.interval_count>0:        #ロックオン,インターバル中は射撃待機
                self.status = "shoot"
            elif self.status=="charge" or self.status=="shoot":
                #弾生成
                speed = 12 + int((24-12)*(self.charge_count/self.CHARGE))
                angle = self.angle + random.randint(-self.angle_range,self.angle_range)
                damage = 5 + int((20-5)*((self.charge_count/self.CHARGE)**2))
                self.mag.append(Bullet(name="bullet", user=self.user, speed=speed, angle=angle, damage=damage))
                self.mag[-1].MAX_TIME = 20 + int((40-20)*((self.charge_count/self.CHARGE)**2))
                #変数リセット
                self.status = "wait"
                self.user.action_busy = False
                self.angle = 0
                self.angle_range = self.ANGLERANGE_MAX
                self.charge_count = 0
                self.interval_count = self.INTERVAL
                if len(self.mag)==self.BULLET_MAX:
                    self.reload_count = self.RELOAD

# ドローン本体(赤スキル2)
class Drone:
    def __init__(self, user, target):
        # 定数
        self.MAX_TIME = 320
        self.HOMING_INTERVAL = 4
        self.STARTUP = 24
        self.SPEED = 10
        self.radius = 15
        self.damage = 15
        # 変数
        self.x = user.x
        self.y = user.y
        self.hp = 5
        self.user = user
        self.target = target
        self.active = False
        self.wait = True
        self.time = 0
        self.startup_count = 0
        self.homing_count = 0

    @property
    def frame(self):
        if self.active or self.wait:
            return "drone," + str(round(self.x)) +","+ str(round(self.y)) +"\n"
        else:
            return ""

    def hit_check(self, pos, r, damage, anti_bullet=False, anti_shield=False):
        if anti_bullet and distance(pos, (self.x, self.y)) < self.radius+r and self.active:
            self.hp -= damage
            return [self]
        else:
            return []

    def update(self):
        if self.active:
            if self.startup_count>=self.STARTUP:
                self.attack()
                # 追尾
                if self.homing_count>=self.HOMING_INTERVAL:
                    self.homing_count = 0
                    # 速度変更
                    e = unit_vector(self.target.x-self.x, self.target.y-self.y)
                    self.speed_x = 7/8*self.speed_x + e[0]
                    self.speed_y = 7/8*self.speed_y + e[1]
                    length = math.sqrt(self.speed_x**2+self.speed_y**2)
                    # 速度制限
                    if length>self.SPEED:
                        self.speed_x *= self.SPEED/length
                        self.speed_y *= self.SPEED/length
                else:
                    self.homing_count += 1
            else:
                self.startup_count +=1
            # 移動
            self.x += self.speed_x
            self.y += self.speed_y

            self.time += 1
            # 消滅条件
            if self.hp<0 or self.time>self.MAX_TIME:
                self.active = False

    def attack(self):
        #ターゲット探索
        for enemy in self.user.target_list:
            # 相手のオブジェクトと衝突判定
            for target in enemy.hit_check((self.x,self.y), self.radius, self.damage, anti_bullet=True):
                # キャラに当たった
                if type(target) == Character:
                    # 無敵処理
                    target.no_damage_count = 24
                    # ヒットストップ処理
                    target.set_stop(8, 5)
                self.active = False

    def shoot(self, angle_range):
        self.active = True
        self.wait = False
        angle = slope_angle(self.target.x-self.x, self.target.y-self.y) + random.randint(-angle_range,angle_range)
        self.speed_x = self.SPEED*math.sin(math.radians(angle))
        self.speed_y = self.SPEED*math.cos(math.radians(angle))

# ドローン管理(赤スキル2)
class DroneManager:
    def __init__(self, user):
        # 定数
        self.RELOAD = 320   # Frame
        self.BULLET_MAX = 4
        self.THROW_TIME = 24
        self.INTERVAL = 24
        self.ANGLE_RANGE = 20

        # 変数
        self.status = "wait"
        self.user = user
        self.mag = []
        self.angle = 0

        self.throw_count = 0
        self.interval_count = 0
        self.reload_count = 0

    @property
    def frame(self):
        frame = "drone_mgr,"+ self.status +","
        frame += str(len(self.mag)) +","+ str(self.BULLET_MAX) +","
        frame += str(self.reload_count) +","+ str(self.RELOAD) +"\n"

        for drone in self.mag:
            frame += drone.frame

        return frame

    def hit_check(self, pos, r, damage, anti_bullet=False, anti_shield=False):
        drone_list = []
        for drone in self.mag:
            drone_list += drone.hit_check(pos, r, damage, anti_bullet=anti_bullet)
        return drone_list

    def update(self):
        if self.reload_count>0:
            self.reload_count -= 1
            if self.reload_count==0:
                self.mag.clear()
        # 投擲
        if self.status == "throw":
            # 投擲表現
            #target_angle = slope_angle(self.mag[-1].target.x-self.user.x, self.mag[-1].y-self.user.y)
            self.angle = gap_angle(self.angle, 270/self.THROW_TIME)
            self.mag[-1].x = self.user.x + self.user.radius*math.sin(math.radians(self.angle))
            self.mag[-1].y = self.user.y + self.user.radius*math.cos(math.radians(self.angle))

            self.throw_count += 1
            # 投げ終わりで射出
            if self.throw_count >= self.THROW_TIME:
                self.throw_count = 0
                self.mag[-1].shoot(self.ANGLE_RANGE)
                self.status = "wait"
                self.user.action_busy = False
                self.interval_count = self.INTERVAL
                if len(self.mag)==self.BULLET_MAX:
                    self.reload_count = self.RELOAD
        elif self.interval_count>0:
            self.interval_count -= 1

        for each in self.mag:
            each.update()

    def throw_start(self):
        if self.reload_count==0 and self.status == "wait" and self.interval_count==0:
            self.status = "throw"
            #弾生成
            target = closest(self.user, self.user.target_list)
            if target==None:
                target=self.user
            self.mag.append(Drone(user=self.user, target=target))
            self.user.action_busy = True
            target_angle = slope_angle(target.x-self.user.x, target.y-self.user.y)
            self.angle = target_angle

# 時止め弾(赤スキル３)
class SynchroBullet(Bullet):
    def __init__(self, user, speed, angle, damage):
        super().__init__("sync_bullet", user,speed, angle,damage)
        self.MAX_TIME = 60
        self.COMBO_INTERVAL = 8
        self.active = False
        self.wait = True
        self.speed = speed

    def shoot(self, target):
        self.active = True
        self.wait = False
        self.angle = slope_angle(target.x-self.x, target.y-self.y)
        self.speed_x = self.speed*math.sin(math.radians(self.angle))
        self.speed_y = self.speed*math.cos(math.radians(self.angle))

    def update(self):
        super().update()
        if self.wait:
            self.display = True

# 時止め射撃(赤スキル３)
class SynchroShot:
    def __init__(self, user):
        # 定数
        self.RELOAD = 320

        self.BULLET_MAX = 5
        self.BULLET_SPEED = 24
        self.BULLET_DAMAGE = 20

        # 変数
        self.user = user
        self.target = None
        self.mag = []

        self.shoot_count = 0
        self.reload_count = 0

    @property
    def frame(self):
        frame = "syncshot,"+ str(self.shoot_count) +","+ str(self.BULLET_MAX)  +","
        frame += str(self.reload_count) +","+ str(self.RELOAD) +"\n"
        # 弾の表示
        for bullet in self.mag:
            frame += bullet.frame
        return frame

    # くらい処理
    def hit_check(self, pos, r, damage, anti_bullet=False, anti_shield=False):
        bullet_list = []
        for bullet in self.mag:
            bullet_list += bullet.hit_check(pos, r, damage, anti_bullet=anti_bullet)
        # ダメージ0のヒットチェックは反射=所有権の移行
        if damage==0:
            for bullet in bullet_list:
                self.mag.remove(bullet)
        return bullet_list

    def reset(self):
        self.mag.clear()
        self.shoot_count = 0

    # 入力
    def shoot(self):
        if self.reload_count==0:
            # 弾を仕掛ける
            if self.shoot_count < self.BULLET_MAX:
                self.mag.append(SynchroBullet(user=self.user, speed=self.BULLET_SPEED, angle=0, damage=self.BULLET_DAMAGE))
                self.shoot_count+=1
            # 射撃
            else:
                target = closest(self.user, self.user.target_list)
                if target == None:
                    target = self.user
                for bullet in self.mag:
                    bullet.shoot(target)
                self.reload_count = self.RELOAD

    # 更新処理
    def update(self):
        if self.reload_count>0:
            self.reload_count -= 1
            if self.reload_count == 0:
                self.reset()
        for bullet in self.mag:
            bullet.update()

# ユーティリティ関数
def distance(a,b):
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

def closest(user, obj_list):
    if obj_list is None or len(obj_list)==0:
        return None
    distance_list = [distance((user.x, user.y), (each.x, each.y)) for each in obj_list]
    return obj_list[distance_list.index(min(distance_list))]

def slope_angle(x,y):
    # y軸正方向からの角度(-180<θ<180)
    if y==0:
        if x>=0:
            angle = 90
        else:
            angle = -90
    elif y>0:
        angle = math.degrees(math.atan(x/y))
    else:
        if x>=0:
            angle = 180+math.degrees(math.atan(x/y))
        else:
            angle = math.degrees(math.atan(x/y))-180
    return angle

def gap_angle(a, b):
    angle_gap = a-b
    if angle_gap>180:
        angle_gap -= 360
    elif angle_gap<-180:
        angle_gap += 360
    return angle_gap

def unit_vector(x,y):
    length = math.sqrt(x**2+y**2)
    if length != 0:
        return (x/length,y/length)
    else:
        return (0,0)


if __name__ == '__main__':
    c = Character("red")
    classes = [ x[1] for x in inspect.getmembers( inspect.getmodule(Character), inspect.isclass)]
    pack_start = perf_counter()

    var_dict = vars(c)
    frame = json.dumps({k: v for k, v in vars(c).items() if not type(v) in classes}, separators=(',', ':')).encode()
    print(frame)
    print(len(frame))
