import pygame, random, time
from pygame.locals import *


# 游戏基本配置参数
SCREEN_WIDHT = 400      # 游戏窗口宽度
SCREEN_HEIGHT = 600     # 游戏窗口高度
SPEED = 20             # 小鸟初始速度
GRAVITY = 2.5          # 重力加速度
GAME_SPEED = 15        # 游戏整体速度

# 游戏元素尺寸配置
GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT = 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

# 音效文件路径
wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'

# 初始化Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# 加载游戏资源
BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

# 创建字体对象用于显示分数
font = pygame.font.Font(None, 36)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))
        self.scored = False
        self.inverted = inverted

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

def show_game_over(screen, score):
    """显示游戏结束画面"""
    game_over_text = font.render(f'游戏结束! 得分: {score}', True, (255, 255, 255))
    restart_text = font.render('按空格键重新开始', True, (255, 255, 255))
    
    screen.blit(game_over_text, (SCREEN_WIDHT/2 - game_over_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
    screen.blit(restart_text, (SCREEN_WIDHT/2 - restart_text.get_width()/2, SCREEN_HEIGHT/2 + 50))
    pygame.display.update()

def main():
    while True:  # 主游戏循环
        # 创建精灵组
        bird_group = pygame.sprite.Group()
        bird = Bird()
        bird_group.add(bird)

        ground_group = pygame.sprite.Group()
        for i in range(2):
            ground = Ground(GROUND_WIDHT * i)
            ground_group.add(ground)

        pipe_group = pygame.sprite.Group()
        for i in range(2):
            pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        clock = pygame.time.Clock()
        score = 0
        game_over = False

        # 开始界面
        begin = True
        while begin:
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        pygame.mixer.music.load(wing)
                        pygame.mixer.music.play()
                        begin = False

            screen.blit(BACKGROUND, (0, 0))
            screen.blit(BEGIN_IMAGE, (120, 150))
            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDHT - 20)
                ground_group.add(new_ground)
            bird.begin()
            ground_group.update()
            bird_group.draw(screen)
            ground_group.draw(screen)
            pygame.display.update()

        # 游戏主循环
        while not game_over:
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        pygame.mixer.music.load(wing)
                        pygame.mixer.music.play()

            screen.blit(BACKGROUND, (0, 0))

            # 更新地面
            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDHT - 20)
                ground_group.add(new_ground)

            # 更新管道
            if is_off_screen(pipe_group.sprites()[0]):
                pipe_group.remove(pipe_group.sprites()[0])
                pipe_group.remove(pipe_group.sprites()[0])
                pipes = get_random_pipes(SCREEN_WIDHT * 2)
                pipe_group.add(pipes[0])
                pipe_group.add(pipes[1])

            # 计分
            for pipe in pipe_group:
                right_edge = pipe.rect[0] + pipe.rect[2]
                if bird.rect[0] > right_edge and not pipe.scored:
                    score += 1
                    pipe.scored = True
                    next_pipe_index = pipe_group.sprites().index(pipe) + 1
                    if next_pipe_index < len(pipe_group.sprites()):
                        pipe_group.sprites()[next_pipe_index].scored = True

            # 更新所有精灵
            bird_group.update()
            ground_group.update()
            pipe_group.update()

            # 绘制所有精灵
            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)

            # 显示分数
            score_text = font.render(f'得分: {score}', True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            pygame.display.update()

            # 碰撞检测
            if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                    pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask) or
                    bird.rect[1] < 0):
                pygame.mixer.music.load(hit)
                pygame.mixer.music.play()
                game_over = True

        # 游戏结束画面
        show_game_over(screen, score)
        
        # 等待重新开始
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        waiting = False

if __name__ == "__main__":
    main() 