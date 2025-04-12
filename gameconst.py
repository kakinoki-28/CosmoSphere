import dataclasses

@dataclasses.dataclass
class CharacterConst:
    radius: int = 30
    hp_max: int = 200

    speed_max: int = 5              # 最大速度
    friction: float = 0.3125        # 摩擦
    start_condition: float = 1.25   # 初速条件
    start_speed: float = 3.0        # 初速
    accelarate: float = 0.25        # 加速度

    next_jump_interval: int = 10    # (空中)ジャンプ入力の最小受付間隔
    normal_jump: int = 18           # 通常ジャンプの高さ
    air_jump: int = 15              # 空中ジャンプの高さ
    platform_jump: int = 15         # 台の上でのジャンプの高さ
    restrict_jump: int = 12         # 制限付き(ガード時の)ジャンプの高さ

    gravity: float = 1.0            # 重力
    grip_strong: float = 0.75       # 吹っ飛び時の強い空気抵抗
    grip_weak: float = 0.5          # 吹っ飛び時の弱い空気抵抗

    hopping_height: int = 40        # 跳ね時に動力を伝えられる最大高
    air_power: float = 0.125        # 跳ね・吹っ飛び時の動力

    drop_speed: int = 5             # 台からの飛び降り時の初速

@dataclasses.dataclass
class ShieldConst:
    startup: int = 12               # 前隙のフレーム
    recovery: int = 16              # 後隙のフレーム
    instant_block: int = 6          # 直前ガード可能フレーム

    radius_max: int = CharacterConst.radius + 30    # ガード時の大きさ
    radius_first: int = 15                          # 開始時のガードの大きさ



def debug():
    CONST = CharacterConst()
    print(CONST)

if __name__ == '__main__':
    debug()