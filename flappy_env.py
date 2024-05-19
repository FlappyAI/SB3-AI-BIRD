import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame, random, time
from pygame.locals import *

#VARIABLES
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def get_center(self, axis):
        center_x = self.rect[0] + (self.rect[2] / 2)
        center_y = self.rect[1] + (self.rect[3] / 2)
        if axis == 'x':
            return center_x
        if axis == 'y':
            return center_y

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        # UPDATE HEIGHT
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

class FlappyEnv(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self):
        super(FlappyEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(2)
        # Example for using image as input (channel-first; channel-last also works):
        #self.observation_space = spaces.Box(low=0, high=255,
        #                                    shape=(N_CHANNELS, HEIGHT, WIDTH), dtype=np.uint8)

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(19,),dtype=np.float32)
        self.done = False
        self.clock = pygame.time.Clock()
        self.moves = 0

    def get_observation(self):
        obs = []
        obs.append(self.bird.rect[1])

        for pipe in self.pipe_group:
                obs.append(pipe.rect[0])
                obs.append(pipe.rect[1])
        return obs

    def step(self, action):

        self.clock.tick(15)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

        if action == 1:
            self.bird.bump()
            pygame.mixer.music.load(wing)
            #pygame.mixer.music.play()
            #print("TAP")
            self.moves += 1
            self.action_history.append(action)
            self.action_history.pop(0)
        elif action == 0:
            #print("DO NOTHING")
            self.moves += 1
            self.action_history.append(action)
            self.action_history.pop(0)
        #print(self.action_history)

        self.screen.blit(self.BACKGROUND, (0, 0))

        if is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            self.ground_group.add(new_ground)

        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDHT * 2)

            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

        # score system
        for pipe in self.pipe_group:
            right_edge = pipe.rect[0] + pipe.rect[2]
            if self.bird.rect[0] > right_edge and (pipe.scored == False):
                self.score += 1
                pipe.scored = True
                print(f'Score: {self.score}')

                next_pipe_index = self.pipe_group.sprites().index(pipe) + 1
                if next_pipe_index < len(self.pipe_group.sprites()):
                    next_pipe = self.pipe_group.sprites()[next_pipe_index]
                    next_pipe.scored = True

        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()

        self.bird_group.draw(self.screen)
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        pygame.display.update()

        death_penalty = 0
        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask) or
                self.bird.get_center("y") < 0):
            pygame.mixer.music.load(hit)
            #pygame.mixer.music.play()
            time.sleep(1)
            death_penalty = -10
            self.done = True

        move_penalty = self.moves * 0.1

        self.observation = self.get_observation() + self.action_history
        self.observation = np.array(self.observation, dtype=np.float32)
        total_reward = self.score - move_penalty + death_penalty
        info = {}
        truncated = False

        print(f"Observation space = {self.observation}")
        print(f"Reward: {total_reward}")
        print(" ")

        return self.observation, total_reward, self.done, truncated, info

    def reset(self, seed=None):
        self.done = False
        self.obs = [0] * 9
        self.action_history = [np.nan] * 10
        self.moves = 0

        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
        self.BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
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

        self.score = 0
        self.observation = self.obs + self.action_history
        self.observation = np.array(self.observation, dtype=np.float32)

        info = {}
        return self.observation, info # reward, done, info can't be included



    def render(self, mode='human'):
        pass

    def close(self):
        pass