from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
import os
from flappy_env import FlappyEnv
import time

class RenderCallback(BaseCallback):
    def __init__(self, env, verbose=0):
        super(RenderCallback, self).__init__(verbose)
        self.env = env

    def _on_step(self) -> bool:
        self.env.render()
        return True

models_dir = f"models/{int(time.time())}/"
logdir = f"logs/{int(time.time())}/"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

env = FlappyEnv()
env.reset()

model = PPO('MlpPolicy', env, verbose=2, tensorboard_log=logdir)
render_callback = RenderCallback(env)

TIMESTEPS = 10000
iters = 0
while True:
    iters += 1
    model.learn(total_timesteps=TIMESTEPS,
                reset_num_timesteps=False,
                tb_log_name=f"PPO",
                callback=render_callback)

    model.save(f"{models_dir}/{TIMESTEPS * iters}")
