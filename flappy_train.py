from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
import os
from flappy_env import FlappyEnv
import time
import json
import numpy as np

class RenderCallback(BaseCallback):
    """自定义回调类，用于在训练过程中渲染游戏画面"""
    def __init__(self, env, verbose=0):
        super(RenderCallback, self).__init__(verbose)
        self.env = env

    def _on_step(self) -> bool:
        """在每个训练步骤后渲染环境"""
        self.env.render()
        return True

class SaveCallback(BaseCallback):
    """自定义回调类，用于保存训练状态"""
    def __init__(self, save_path, verbose=0):
        super(SaveCallback, self).__init__(verbose)
        self.save_path = save_path
        self.best_mean_reward = -np.inf

    def _on_step(self) -> bool:
        """在每个训练步骤后保存模型"""
        if self.n_calls % 10000 == 0:  # 每10000步保存一次
            self.model.save(f"{self.save_path}/model_{self.n_calls}")
            # 保存训练状态
            training_state = {
                'n_calls': self.n_calls,
                'best_mean_reward': self.best_mean_reward,
                'last_save': time.time()
            }
            with open(f"{self.save_path}/training_state.json", 'w') as f:
                json.dump(training_state, f)
        return True

def load_latest_model(models_dir):
    """加载最新的模型"""
    if not os.path.exists(models_dir):
        return None, 0
    
    # 获取所有模型目录
    model_dirs = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    if not model_dirs:
        return None, 0
    
    # 获取所有模型文件
    all_model_files = []
    for dir_name in model_dirs:
        dir_path = os.path.join(models_dir, dir_name)
        model_files = [f for f in os.listdir(dir_path) if f.startswith('model_') and f.endswith('.zip')]
        for file in model_files:
            all_model_files.append((os.path.join(dir_path, file), file))
    
    if not all_model_files:
        return None, 0
    
    # 获取最新的模型文件
    latest_model, latest_file = max(all_model_files, key=lambda x: int(x[1].split('_')[1].split('.')[0]))
    steps = int(latest_file.split('_')[1].split('.')[0])
    
    return latest_model, steps

def main():
    # 创建模型和日志目录
    model_code = int(time.time())
    models_dir = f"models/{model_code}/"
    logdir = f"logs/{model_code}/"

    # 确保目录存在
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # 创建和初始化环境
    env = FlappyEnv()
    env.reset()

    # 尝试加载最新的模型
    latest_model, start_steps = load_latest_model("models")
    if latest_model:
        print(f"加载已有模型: {latest_model}")
        model = PPO.load(latest_model, env=env, tensorboard_log=logdir)
        print(f"已加载 {start_steps} 步的训练结果")
    else:
        print("创建新模型")
        model = PPO(
            'MlpPolicy',
            env,
            tensorboard_log=logdir,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            clip_range_vf=None,
            normalize_advantage=True,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            target_kl=0.01,
            policy_kwargs=None,
            verbose=2
        )
        start_steps = 0

    # 创建回调
    render_callback = RenderCallback(env)
    save_callback = SaveCallback(models_dir)

    # 训练参数
    TIMESTEPS = 10000  # 每次训练的时间步数
    iters = start_steps // TIMESTEPS

    print(f"开始训练，从 {start_steps} 步继续")
    print(f"模型保存在: {models_dir}")
    print(f"日志保存在: {logdir}")

    # 开始训练循环
    while True:
        iters += 1
        # 训练模型
        model.learn(
            total_timesteps=TIMESTEPS,
            reset_num_timesteps=False,
            tb_log_name=f"PPO",
            callback=[render_callback, save_callback]
        )

        # 保存模型
        model.save(f"{models_dir}/model_{TIMESTEPS * iters}")
        print(f"保存模型到: {models_dir}/model_{TIMESTEPS * iters}")

if __name__ == "__main__":
    main()
