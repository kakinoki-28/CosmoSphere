import pygame
import UI

LogoTypeGothic_45 = pygame.font.Font("fonts/ロゴたいぷゴシックCondense.otf", 45)
LogoTypeGothic_90 = pygame.font.Font("fonts/ロゴたいぷゴシックCondense.otf", 90)
LogoTypeGothic_100 = pygame.font.Font("fonts/ロゴたいぷゴシックCondense.otf", 100)

# タイトルなど動作のないテキストは先に描画を済ませる
class RenderedText:
    def __init__(self, text, size, color):
        self.font = pygame.font.Font("fonts/ロゴたいぷゴシックCondense.otf", size)
        self.surface = self.font.render(text, True, color)


class MainMenu:
    def __init__(self):
        self.select = 0

        self.option_list = [
            UI.Button("オンライン対戦", LogoTypeGothic_90, 2, (80, 120, 720, 180)),
            UI.Button("ひとりでプレイ", LogoTypeGothic_90, 2, (80, 360, 720, 180)),
            UI.Button("プロフィール", LogoTypeGothic_45, 2, (840, 300, 360, 90)),
            UI.Button("設定", LogoTypeGothic_45, 2, (840, 420, 360, 90))
        ]

        self.option_list[0].bind(print, "button clicked!")

    def update(self, tick):
        for option in self.option_list:
            option.update(tick)

    def draw(self, screen):
        for option in self.option_list:
            option.draw(screen)

    def mouse_move(self, mouse_pos):    # MOUSEMOTION
        for option in self.option_list:
            option.mouse_move(mouse_pos)

    def mouse_down(self, mouse_pos):    # MOUSEBUTTONDOWN
        for option in self.option_list:
            option.mouse_down(mouse_pos)

    def mouse_up(self, mouse_pos):      # MOUSEBUTTONUP
        for option in self.option_list:
            option.mouse_up(mouse_pos)


def debug():
    pygame.init()
    WIDTH, HEIGHT = 1280, 720

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Menu Debug")


    clock = pygame.time.Clock()

    # メニュー定義
    menu = MainMenu()

    run = True
    while run:
        tick = clock.tick(60)

        window.fill((96,96,96))
        #window.blit(background,(0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                menu.mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                menu.mouse_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                menu.mouse_move(event.pos)

        menu.update(tick)
        menu.draw(window)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    debug()