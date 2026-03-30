import pygame

# カラーパレット
BG_COLOR = (64,64,64)
ACTIVE_COLOR = (255, 69, 0)
WHITE = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 80)

# フォント
pygame.font.init()
Meiryo_30 = pygame.font.SysFont("Meiryo", 30)
Meiryo_20 = pygame.font.SysFont("Meiryo", 20)
LogoTypeGothic_30 = pygame.font.Font("fonts/ロゴたいぷゴシックCondense.otf", 30)

def pass_func():
    pass

class StretchLine:
    def __init__(self, width):
        self.width = width

    def draw(self, surface, color, start_pos, length):
        pygame.draw.line(surface, color, start_pos, (start_pos[0]+length, start_pos[1]), width=self.width)

class Component:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

        self.bind_method = pass_func
        self.bind_args = ()
        self.bind_kwargs = {}


    def bind(self, callable_method, *args, **kwargs):
        self.bind_method = callable_method
        self.bind_args = args
        self.bind_kwargs = kwargs

class Button(Component):
    def __init__(self, text, font, under_width, rect):
        super().__init__(rect)
        self.text = text
        self.font = font
        self.radius = 12

        self.hover = False
        self.click = False

        self.surface = pygame.Surface(self.rect.size).convert_alpha()

        self.tick_counter = 0
        self.length_rate = 0
        self.under_line = StretchLine(width=under_width)

    def mouse_move(self, mouse_pos):    # MOUSEMOTION
        # マウスホバーで色変更
        if self.rect.collidepoint(mouse_pos):
            self.hover = True
        else:
            self.hover = False
        return self.hover

    def mouse_down(self, mouse_pos):    # MOUSEBUTTONDOWN
        if self.rect.collidepoint(mouse_pos):
            self.click = True

    def mouse_up(self, mouse_pos):      # MOUSEBUTTONUP
        self.click = False
        if self.rect.collidepoint(mouse_pos):
            self.bind_method(*self.bind_args, **self.bind_kwargs)

    def update(self, tick):
        if self.hover:
            self.tick_counter += tick
            if self.tick_counter>1/60 and self.length_rate<10:
                self.tick_counter = 0
                self.length_rate += 1
        else:
            self.tick_counter = 0
            self.length_rate = 0

    def draw(self, screen):
        self.surface.fill((0,0,0,0))
        local_rect = pygame.Rect((0,0),self.rect.size)
        alpha = 255
        if self.click:
            # ボタン外周
            #pygame.draw.rect(self.surface, ACTIVE_COLOR, local_rect, width=2, border_radius=self.radius)
            # テキスト
            text_surf = self.font.render(self.text, True, ACTIVE_COLOR)
            text_rect = text_surf.get_rect(center=local_rect.center)
            self.surface.blit(text_surf, text_rect)
            # アンダーライン
            if self.length_rate>0:
                self.under_line.draw(self.surface, ACTIVE_COLOR, (text_rect.x, text_rect.y+text_rect.h), text_rect.w*self.length_rate/10)
        elif self.hover:
            # ボタン外周
            #pygame.draw.rect(self.surface, WHITE, local_rect, width=2, border_radius=12)
            # テキスト
            text_surf = self.font.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=local_rect.center)
            self.surface.blit(text_surf, text_rect)
            # アンダーライン
            if self.length_rate>0:
                self.under_line.draw(self.surface, WHITE, (text_rect.x, text_rect.y+text_rect.h), text_rect.w*self.length_rate/10)
        else:
            # テキスト
            text_surf = self.font.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=local_rect.center)
            self.surface.blit(text_surf, text_rect)
            alpha = 128

        self.surface.set_alpha(alpha)
        screen.blit(self.surface, self.rect)



def debug():
    pygame.init()

    WIDTH, HEIGHT = 800, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UI Debug")

    clock = pygame.time.Clock()

    # ボタン配置（中央寄せ）
    button = Button("START", LogoTypeGothic_30, 2, (WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60))
    button.bind(print, "button clicked!")

    run = True
    while run:
        tick = clock.tick(60)

        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button.mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                button.mouse_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                button.mouse_move(event.pos)

        button.update(tick)
        button.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    debug()