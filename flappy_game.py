import pygame, random, time
from pygame.locals import *

# 游戏基本配置参数
SCREEN_WIDHT = 400      # 游戏窗口宽度
SCREEN_HEIGHT = 600     # 游戏窗口高度
SPEED = 20             # 小鸟初始速度
GRAVITY = 2.5          # 重力加速度
GAME_SPEED = 15        # 游戏整体速度（影响管道和地面的移动速度）

# 游戏元素尺寸配置
GROUND_WIDHT = 2 * SCREEN_WIDHT  # 地面宽度（设置为屏幕宽度的2倍，实现无缝滚动）
GROUND_HEIGHT = 100              # 地面高度

PIPE_WIDHT = 80        # 管道宽度
PIPE_HEIGHT = 500      # 管道高度
PIPE_GAP = 150         # 上下管道之间的间隙

# 音效文件路径
wing = 'assets/audio/wing.wav'   # 小鸟翅膀扇动音效
hit = 'assets/audio/hit.wav'     # 碰撞音效

# 初始化Pygame音频系统
pygame.mixer.init()

class Bird(pygame.sprite.Sprite):
    """
    小鸟类：实现小鸟的动画和物理效果
    
    属性:
        images: 小鸟动画帧列表
        speed: 当前速度
        current_image: 当前显示的动画帧索引
        image: 当前显示的图像
        mask: 碰撞检测用的遮罩
        rect: 小鸟的位置和大小矩形
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # 加载小鸟的三帧动画图像
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]

        self.speed = SPEED
        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)  # 创建碰撞检测遮罩

        # 设置小鸟初始位置
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6    # 水平位置在屏幕左侧1/6处
        self.rect[1] = SCREEN_HEIGHT / 2   # 垂直位置在屏幕中央

    def get_center(self, axis):
        """
        获取小鸟的中心点坐标
        
        参数:
            axis: 'x' 或 'y'，指定要获取的坐标轴
        返回:
            对应轴的中心点坐标
        """
        center_x = self.rect[0] + (self.rect[2] / 2)
        center_y = self.rect[1] + (self.rect[3] / 2)
        if axis == 'x':
            return center_x
        if axis == 'y':
            return center_y

    def update(self):
        """更新小鸟状态：动画和物理效果"""
        # 更新动画帧
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        
        # 应用重力
        self.speed += GRAVITY
        
        # 更新位置
        self.rect[1] += self.speed

    def bump(self):
        """小鸟跳跃：给予向上的速度"""
        self.speed = -SPEED

    def begin(self):
        """开始界面动画：只更新动画帧，不改变位置"""
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

class Pipe(pygame.sprite.Sprite):
    """
    管道类：实现管道的显示和移动
    
    属性:
        image: 管道图像
        scored: 是否已经计分
        inverted: 是否是倒置的管道
        rect: 管道的位置和大小矩形
        mask: 碰撞检测用的遮罩
    """
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        # 加载并缩放管道图像
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))
        self.scored = False
        self.inverted = inverted

        # 设置管道位置
        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        # 根据是否是倒置管道设置位置
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        # 创建碰撞检测遮罩
        self.mask = pygame.mask.from_surface(self.image)

    def get_edge(self):
        """获取管道的边缘位置"""
        if self.inverted:
            return self.rect.top
        else:
            return self.rect.bottom

    def update(self):
        """更新管道位置：向左移动"""
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    """
    地面类：实现地面的显示和滚动效果
    
    属性:
        image: 地面图像
        mask: 碰撞检测用的遮罩
        rect: 地面的位置和大小矩形
    """
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        # 加载并缩放地面图像
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        # 创建碰撞检测遮罩
        self.mask = pygame.mask.from_surface(self.image)

        # 设置地面位置
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        """更新地面位置：向左移动"""
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    """
    检查精灵是否移出屏幕
    
    参数:
        sprite: 要检查的精灵对象
    返回:
        bool: 是否移出屏幕
    """
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    """
    生成随机高度的管道对
    
    参数:
        xpos: 管道的水平位置
    返回:
        tuple: (上管道, 下管道)
    """
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# 加载游戏背景和开始界面图像
BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

# 创建精灵组
bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()
# 创建两个地面精灵实现无缝滚动
for i in range(2):
    ground = Ground(GROUND_WIDHT * i)
    ground_group.add(ground)

# 创建管道组
pipe_group = pygame.sprite.Group()
# 创建初始管道
for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])

# 创建时钟对象控制游戏帧率
clock = pygame.time.Clock()

# 开始界面循环
begin = True
while begin:
    clock.tick(15)  # 限制帧率为15FPS

    # 处理事件
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                pygame.mixer.music.load(wing)
                pygame.mixer.music.play()
                begin = False

    # 绘制游戏画面
    screen.blit(BACKGROUND, (0, 0))
    screen.blit(BEGIN_IMAGE, (120, 150))

    # 更新地面位置
    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDHT - 20)
        ground_group.add(new_ground)

    # 更新小鸟动画和地面位置
    bird.begin()
    ground_group.update()

    # 绘制精灵
    bird_group.draw(screen)
    ground_group.draw(screen)

    pygame.display.update()

# 游戏主循环
score = 0
while True:
    clock.tick(15)  # 限制帧率为15FPS

    # 处理事件
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                pygame.mixer.music.load(wing)
                pygame.mixer.music.play()

    # 绘制背景
    screen.blit(BACKGROUND, (0, 0))

    # 更新地面位置
    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDHT - 20)
        ground_group.add(new_ground)

    # 更新管道位置
    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])
        pipes = get_random_pipes(SCREEN_WIDHT * 2)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    # 计分系统
    for pipe in pipe_group:
        right_edge = pipe.rect[0] + pipe.rect[2]
        if bird.rect[0] > right_edge and (pipe.scored == False):
            score += 1
            pipe.scored = True
            print(f'Score: {score}')

            # 同时标记下一个管道为已计分
            next_pipe_index = pipe_group.sprites().index(pipe) + 1
            if next_pipe_index < len(pipe_group.sprites()):
                next_pipe = pipe_group.sprites()[next_pipe_index]
                next_pipe.scored = True

    # 更新所有精灵
    bird_group.update()
    ground_group.update()
    pipe_group.update()

    # 绘制所有精灵
    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)

    # 绘制调试线条（用于AI训练）
    bird_center = (bird.get_center("x"), bird.get_center("y"))
    first_top_pipe = None
    first_bottom_pipe = None

    # 找到最近的管道对
    for pipe in pipe_group:
        if not first_top_pipe and pipe.inverted:
            first_top_pipe = pipe
        elif not first_bottom_pipe and not pipe.inverted:
            first_bottom_pipe = pipe

        if first_top_pipe and first_bottom_pipe:
            break

    # 绘制到管道的距离线
    if first_top_pipe:
        top_pipe_edge = (first_top_pipe.rect[0], first_top_pipe.rect[1] + first_top_pipe.rect[3])
        pygame.draw.line(screen, (255, 0, 0), bird_center, top_pipe_edge, 3)
    if first_bottom_pipe:
        bottom_pipe_edge = (first_bottom_pipe.rect[0], first_bottom_pipe.rect[1])
        pygame.draw.line(screen, (255, 0, 0), bird_center, bottom_pipe_edge, 3)

    # 计算并显示距离信息（用于AI训练）
    h_dist = top_pipe_edge[0] - bird.get_center("x") - 12
    pygame.draw.line(screen, (0, 0, 255), bird_center, (bird_center[0] + h_dist, bird_center[1]), 3)
    bird_to_top = -((bird.get_center("y") - top_pipe_edge[1]) / 500)
    bird_to_bot = -((bird.get_center("y") - bottom_pipe_edge[1]) / 500)
    print(f"bird to top: {bird_to_top}\nbird to bot: {bird_to_bot}\n")
    print(f"HORIZONTAL TO BIRD: {h_dist}\n")

    pygame.display.update()

    # 碰撞检测
    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask) or
            bird.get_center("y") < 0):
        # 播放碰撞音效
        pygame.mixer.music.load(hit)
        pygame.mixer.music.play()
        time.sleep(1)
        break

