import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modern UI Sample")

clock = pygame.time.Clock()

# カラー
BG_COLOR = (255, 255, 255)
BUTTON_COLOR = (45, 140, 240)
HOVER_COLOR = (65, 160, 255)
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 80)

# フォント
font = pygame.font.SysFont("meiryo", 28)

def pass_func():
    pass

class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.base_color = BUTTON_COLOR
        self.hover_color = HOVER_COLOR
        self.current_color = self.base_color
        self.radius = 12

        self.clicked = False
        self.active = False

        self.bind_method = pass_func
        self.bind_kwargs = {}

    def draw(self, surface):
        # 影
        shadow_rect = self.rect.copy()
        shadow_rect.y += 5
        shadow_surface = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow_surface.get_rect(), border_radius=self.radius)
        surface.blit(shadow_surface, shadow_rect.topleft)

        if not self.clicked:
            # ボタン本体
            pygame.draw.rect(surface, self.current_color, self.rect, border_radius=self.radius)
            # テキスト
            text_surf = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        else:
            # ボタン本体
            pygame.draw.rect(surface, self.current_color, self.rect.move(0,3), border_radius=self.radius)
            # テキスト
            text_surf = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.move(0,3).center)
            surface.blit(text_surf, text_rect)


    def bind(self, callable_method, *args, **kwargs):
        self.bind_method = callable_method
        self.bind_args = args
        self.bind_kwargs = kwargs

    def update(self, mouse_pos):
        # マウスホバーで色変更
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color

    def button_down(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = True

    def button_up(self, pos):
        self.clicked = False
        if self.rect.collidepoint(pos):
            self.active = True
            self.bind_method(*self.bind_args, **self.bind_kwargs)


# ボタン配置（中央寄せ）
button = Button("START", WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60)
button.bind(print, "button clicked!")

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button.button_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            button.button_up(event.pos)


    button.update(mouse_pos)
    button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()