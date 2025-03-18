import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame, random, time
from pygame.locals import *
from game_stats import GameStats  # 导入新的统计系统

# 游戏基本参数设置
SCREEN_WIDHT = 400  # 游戏窗口宽度
SCREEN_HEIGHT = 600  # 游戏窗口高度
SPEED = 20  # 小鸟初始速度
GRAVITY = 2.5  # 重力加速度
GAME_SPEED = 15  # 游戏整体速度

# 地面和管道参数
GROUND_WIDHT = 2 * SCREEN_WIDHT  # 地面宽度
GROUND_HEIGHT= 100  # 地面高度
PIPE_WIDHT = 80  # 管道宽度
PIPE_HEIGHT = 500  # 管道高度
PIPE_GAP = 150  # 管道间隙

# 音效文件路径
wing = 'assets/audio/wing.wav'  # 翅膀扇动音效
hit = 'assets/audio/hit.wav'  # 碰撞音效

class Bird(pygame.sprite.Sprite):
    """小鸟类，继承自pygame的Sprite类"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # 加载小鸟的三个动画帧
        self.images = [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED  # 初始速度
        self.current_image = 0  # 当前动画帧
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)  # 创建碰撞遮罩

        # 设置小鸟初始位置
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def get_center(self, axis):
        """获取小鸟中心点坐标"""
        center_x = self.rect[0] + (self.rect[2] / 2)
        center_y = self.rect[1] + (self.rect[3] / 2)
        if axis == 'x':
            return center_x
        if axis == 'y':
            return center_y

    def update(self):
        """更新小鸟状态"""
        self.current_image = (self.current_image + 1) % 3  # 更新动画帧
        self.image = self.images[self.current_image]
        self.speed += GRAVITY  # 应用重力
        self.rect[1] += self.speed  # 更新位置

    def bump(self):
        """小鸟跳跃"""
        self.speed = -SPEED

    def begin(self):
        """开始动画"""
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

class Pipe(pygame.sprite.Sprite):
    """管道类，继承自pygame的Sprite类"""
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        # 加载管道图片并调整大小
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))
        self.scored = False  # 是否已计分
        self.inverted = inverted  # 是否倒置

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        # 根据是否倒置设置管道位置
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)  # 创建碰撞遮罩

    def update(self):
        """更新管道位置"""
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    """地面类，继承自pygame的Sprite类"""
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        # 加载地面图片并调整大小
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)  # 创建碰撞遮罩

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        """更新地面位置"""
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    """检查精灵是否离开屏幕"""
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    """生成随机高度的管道对"""
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

class FlappyEnv(gym.Env):
    """Flappy Bird游戏环境类，继承自gym.Env"""
    def __init__(self):
        super(FlappyEnv, self).__init__()
        # 定义动作空间（0：不跳，1：跳跃）
        self.action_space = spaces.Discrete(2)
        # 定义观察空间（3个浮点数：到上管道的距离、到下管道的距离、水平距离）
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)
        self.done = False
        self.clock = pygame.time.Clock()
        self.moves = 0
        self.tap = False

        # 初始化游戏统计系统
        self.stats = GameStats()
        self.death_count = self.stats.get_death_count()
        self.high_score = self.stats.get_high_score()
        self.current_score = 0
        self.max_frame = self.stats.get_max_frame()

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)

    def step(self, action):
        """执行一步动作"""
        # 获取小鸟位置
        self.bird_center = (self.bird.get_center("x"), self.bird.get_center("y"))
        self.frame += 1

        # 找到最近的管道对
        first_top_pipe = None
        first_bottom_pipe = None

        for pipe in self.pipe_group:
            if not first_top_pipe and pipe.inverted:
                first_top_pipe = pipe
            elif not first_bottom_pipe and not pipe.inverted:
                first_bottom_pipe = pipe

            if first_top_pipe and first_bottom_pipe:
                break

        # 计算到管道的距离
        self.top_edge = first_top_pipe.rect[0], first_top_pipe.rect[1] + first_top_pipe.rect[3]
        self.bottom_edge = first_bottom_pipe.rect[0], first_bottom_pipe.rect[1]

        # 计算观察值（归一化处理）
        bird_y = self.bird.get_center("y")
        top_y = self.top_edge[1]
        bottom_y = self.bottom_edge[1]
        pipe_x = self.top_edge[0]

        # 归一化距离计算（使用更稳定的计算方式）
        self.bird_to_top = np.clip((bird_y - top_y) / SCREEN_HEIGHT, -1.0, 1.0)
        self.bird_to_bot = np.clip((bird_y - bottom_y) / SCREEN_HEIGHT, -1.0, 1.0)
        self.h_dist = np.clip((pipe_x - self.bird_center[0]) / SCREEN_WIDHT, -1.0, 1.0)

        # 处理游戏事件
        self.clock.tick(15)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

        # 执行动作
        if action == 1:
            self.bird.bump()
            pygame.mixer.music.load(wing)
            self.tap = True
            self.moves += 1
            self.action_history.append(action)
            self.action_history.pop(0)
        elif action == 0:
            self.tap = False
            self.action_history.append(action)
            self.action_history.pop(0)

        # 更新游戏画面
        self.screen.blit(self.BACKGROUND, (0, 0))

        # 更新地面
        if is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDHT - 20)
            self.ground_group.add(new_ground)

        # 更新管道
        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            pipes = get_random_pipes(SCREEN_WIDHT * 2)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

        # 计分系统
        for pipe in self.pipe_group:
            right_edge = pipe.rect[0] + pipe.rect[2]
            if self.bird.rect[0] > right_edge and (pipe.scored == False):
                self.current_score += 1
                self.high_score = max(self.high_score, self.current_score)  # 更新最高分
                pipe.scored = True
                next_pipe_index = self.pipe_group.sprites().index(pipe) + 1
                if next_pipe_index < len(self.pipe_group.sprites()):
                    next_pipe = self.pipe_group.sprites()[next_pipe_index]
                    next_pipe.scored = True

        # 更新所有精灵
        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()

        # 绘制所有精灵
        self.bird_group.draw(self.screen)
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        # 在管道上添加标注
        for pipe in self.pipe_group:
            if not pipe.inverted:  # 只在下管道显示信息
                # 计算管道信息
                pipe_height = pipe.rect[3]  # 管道高度
                pipe_y = pipe.rect[1]  # 管道Y坐标
                gap_y = pipe_y - PIPE_GAP  # 间隙的Y坐标
                
                # 创建信息文本
                info_text = f"H:{pipe_height} Y:{pipe_y:.0f} Gap:{gap_y:.0f}"
                text_surface = self.font.render(info_text, True, (0, 0, 0))
                
                # 在管道上显示信息
                text_x = pipe.rect[0] + 5  # 管道左侧5像素处
                text_y = pipe.rect[1] + 5  # 管道顶部5像素处
                self.screen.blit(text_surface, (text_x, text_y))

        pygame.display.update()

        # 更新最大帧数
        if self.frame > self.max_frame:
            self.max_frame = self.frame
            self.stats.update_max_frame(self.max_frame)

        # 检查是否死亡
        death_penalty = 0
        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask) or
                self.bird.get_center("y") < 0):
            pygame.mixer.music.load(hit)
            time.sleep(1)
            death_penalty = -1
            if self.bird.get_center("y") < 0:
                death_penalty = -2
            self.done = True
            self.death_count += 1  # 增加死亡计数
            self.stats.update_death_count(self.death_count)  # 保存死亡次数
            self.current_score = 0  # 重置当前分数

        # 更新最高分
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.stats.update_high_score(self.high_score)

        # 计算奖励（简化奖励计算）
        move_penalty = self.moves * 0.001
        surival_reward = self.frame * 0.001

        # 构建观察值
        self.observation = np.array([self.bird_to_top, self.bird_to_bot, self.h_dist], dtype=np.float32)
        
        # 计算总奖励
        total_reward = self.current_score - move_penalty + death_penalty + surival_reward
        info = {}
        truncated = False

        return self.observation, total_reward, self.done, truncated, info

    def reset(self, seed=None):
        """重置环境"""
        self.done = False
        self.obs = [0] * 9
        self.action_history = [-1] * 10
        self.moves = 0
        self.frame = 0

        # 初始化观察值为0
        self.bird_to_top = 0.0
        self.bird_to_bot = 0.0
        self.h_dist = 0.0

        self.top_edge = (0, 0)
        self.bottom_edge = (0, 0)

        # 初始化pygame
        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # 加载图片资源
        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
        self.BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

        # 创建精灵组
        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
        self.bird_center = (self.bird.get_center("x"), self.bird.get_center("y"))
        self.bird_group.add(self.bird)

        self.ground_group = pygame.sprite.Group()
        for i in range(2):
            self.ground = Ground(GROUND_WIDHT * i)
            self.ground_group.add(self.ground)

        self.pipe_group = pygame.sprite.Group()
        for i in range(2):
            self.pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
            self.pipe_group.add(self.pipes[0])
            self.pipe_group.add(self.pipes[1])

        self.clock.tick(15)

        self.bird.begin()
        self.ground_group.update()

        self.bird_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        pygame.display.update()

        self.current_score = 0  # 重置当前分数
        # 初始化观察值为0
        self.observation = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        info = {}
        return self.observation, info  # 返回观察值和信息字典

    def render_text(self, text, position, size):
        """渲染文本"""
        self.font = pygame.font.SysFont('Arial', size)
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, position)

    def render(self, mode='human'):
        """渲染游戏画面"""
        if mode == 'human':
            # 渲染游戏统计信息
            self.render_text(f'Score: {self.current_score}', (200, 500), 24)
            self.render_text(f'High Score: {self.high_score}', (200, 520), 24)
            self.render_text(f'Deaths: {self.death_count}', (200, 540), 24)
            self.render_text(f'Frame: {self.frame}', (200, 560), 24)
            self.render_text(f'Max Frame: {self.max_frame}', (200, 580), 24)

            # 渲染观察值
            self.render_text(f'Top: {self.bird_to_top:.2f}', (40, self.bird.get_center('y') - 50), 16)
            self.render_text(f'Bot: {self.bird_to_bot:.2f}', (40, self.bird.get_center('y') + 30), 16)
            self.render_text(f'Dist: {self.h_dist:.2f}', (10, self.bird.get_center('y')), 16)

            # 渲染动作指示器
            pygame.draw.circle(self.screen, (0, 0, 0), (130, 560), 30)
            pygame.draw.circle(self.screen, (255, 0, 0), (130, 560), 25)
            if self.tap:
                pygame.draw.circle(self.screen, (0, 255, 0), (130, 560), 25)
                self.tap = False

            # 渲染距离线
            pygame.draw.line(self.screen, (255, 0, 0), self.bird_center, self.top_edge, 3)
            pygame.draw.line(self.screen, (255, 0, 0), self.bird_center, self.bottom_edge, 3)
            pygame.draw.line(self.screen, (0, 0, 255), self.bird_center, (self.bird_center[0] + self.h_dist, self.bird_center[1]), 3)

            pygame.display.update()

    def close(self):
        """关闭环境"""
        pass