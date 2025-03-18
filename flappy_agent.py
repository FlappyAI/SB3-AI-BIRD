from stable_baselines3 import PPO
import gymnasium as gym
import os
from flappy_env import FlappyEnv
import time

# 加载预训练模型
model_code = 1716117777  # 模型编号
step = 290000  # 训练步数

# 设置模型路径
models_dir = f"models/{model_code}"
model_path = f"{models_dir}/{step}.zip"

# 创建和初始化环境
env = FlappyEnv()
env.reset()

# 加载预训练模型
model = PPO.load(model_path, env=env, tensorboard_log=models_dir)

# 设置测试回合数
episodes = 50

# 开始测试循环
for episode in range(episodes):
    done = False
    obs, _ = env.reset()  # 获取观察值和信息
    while not done:
        env.render("human")  # 渲染游戏画面
        action, _ = model.predict(obs)  # 使用模型预测动作
        obs, reward, done, truncated, info = env.step(action)  # 执行动作

env.close()  # 关闭环境
