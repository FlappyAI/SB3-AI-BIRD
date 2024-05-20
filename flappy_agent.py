from stable_baselines3 import PPO
import gymnasium as gym
import os
from flappy_env import FlappyEnv
import time

model_code = 1716117777
step = 290000

models_dir = f"models/{model_code}"
model_path = f"{models_dir}/{step}.zip"

env = FlappyEnv()
env.reset()

model = PPO.load(model_path, env=env, tensorboard_log=models_dir)

episodes = 50

for episode in range(episodes):
    done = False
    obs = env.reset()
    while not done:  #not done:
        env.render("human")
        action, _ = model.predict(obs)
        # print("action", random_action)
        obs, reward, done, truncated ,info = env.step(action)
        # print('reward', reward)
env.close()
