from stable_baselines3 import PPO
from flappy_env import FlappyEnv
import os

def load_and_play(model_path):
    """加载模型并开始游戏"""
    # 创建环境
    env = FlappyEnv()
    
    # 加载模型
    model = PPO.load(model_path, env=env)
    
    print(f"已加载模型: {model_path}")
    print("开始游戏，按 Ctrl+C 退出")
    
    # 开始游戏循环
    obs, _ = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        # 渲染游戏画面
        env.render()
        
        # 使用模型预测动作
        action, _ = model.predict(obs, deterministic=True)
        
        # 执行动作
        obs, reward, done, _, info = env.step(action)
        total_reward += reward
        
        # 显示游戏信息
        print(f"\r得分: {info['score']} | 存活时间: {info['time']} | 总奖励: {total_reward:.2f}", end="")
    
    print("\n游戏结束!")
    print(f"最终得分: {info['score']}")
    print(f"总奖励: {total_reward:.2f}")

def main():
    # 获取最新的模型文件
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("错误：未找到模型目录")
        return
    
    # 获取所有模型文件
    model_files = [f for f in os.listdir(models_dir) if f.startswith('model_') and f.endswith('.zip')]
    if not model_files:
        print("错误：未找到模型文件")
        return
    
    # 获取最新的模型文件
    latest_model = max(model_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
    model_path = os.path.join(models_dir, latest_model)
    
    print(f"找到最新模型: {latest_model}")
    print(f"模型路径: {model_path}")
    
    # 加载并运行模型
    load_and_play(model_path)

if __name__ == "__main__":
    main() 