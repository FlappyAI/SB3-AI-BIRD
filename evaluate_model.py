from stable_baselines3 import PPO
from flappy_env import FlappyEnv
import numpy as np
import os
import json
from datetime import datetime


def evaluate_model(model_path, num_episodes=10):
    """
    评估强化学习模型的性能
    
    参数:
        model_path (str): 模型文件的路径
        num_episodes (int): 评估的回合数，默认为10回合
    
    功能:
        1. 加载训练好的模型
        2. 运行多个回合进行测试
        3. 收集性能数据
        4. 计算统计指标
        5. 保存评估结果
    """
    # 创建游戏环境实例
    env = FlappyEnv()
    
    # 加载训练好的PPO模型
    # PPO (Proximal Policy Optimization) 是一种强化学习算法
    model = PPO.load(model_path, env=env)
    
    # 初始化数据收集列表
    scores = []      # 记录每个回合的得分
    times = []       # 记录每个回合的存活时间
    rewards = []     # 记录每个回合的总奖励
    pipes_passed = [] # 记录每个回合通过的管道数量
    
    print(f"开始评估模型: {model_path}")
    print(f"计划评估 {num_episodes} 个回合")
    
    # 开始评估循环
    for episode in range(num_episodes):
        # 重置环境，获取初始观察值
        obs, _ = env.reset()
        done = False
        total_reward = 0
        
        # 单个回合的游戏循环
        while not done:
            # 使用模型预测下一步动作
            # deterministic=True 表示使用确定性策略，而不是随机采样
            action, _ = model.predict(obs, deterministic=True)
            
            # 执行动作，获取环境反馈
            # obs: 新的观察值
            # reward: 获得的奖励
            # done: 回合是否结束
            # info: 额外的信息（如得分、存活时间等）
            obs, reward, done, _, info = env.step(action)
            total_reward += reward
            
            # 实时显示评估进度
            print(f"\r回合 {episode + 1}/{num_episodes} | 得分: {info['score']} | 存活时间: {info['time']}", end="")
        
        # 记录回合数据
        scores.append(info['score'])
        times.append(info['time'])
        rewards.append(total_reward)
        pipes_passed.append(info['pipes_passed'])
        
        print(f"\n回合 {episode + 1} 完成")
    
    # 计算统计指标
    stats = {
        '平均得分': np.mean(scores),           # 所有回合的平均得分
        '最高得分': np.max(scores),            # 所有回合中的最高得分
        '平均存活时间': np.mean(times),        # 所有回合的平均存活时间
        '最长存活时间': np.max(times),         # 所有回合中的最长存活时间
        '平均奖励': np.mean(rewards),          # 所有回合的平均奖励
        '平均通过管道数': np.mean(pipes_passed), # 所有回合的平均通过管道数
        '最高通过管道数': np.max(pipes_passed),  # 所有回合中的最高通过管道数
        '标准差': {
            '得分': np.std(scores),            # 得分的标准差，反映稳定性
            '存活时间': np.std(times),         # 存活时间的标准差
            '奖励': np.std(rewards),           # 奖励的标准差
            '通过管道数': np.std(pipes_passed)  # 通过管道数的标准差
        }
    }
    
    # 创建评估结果目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "evaluation_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # 保存评估结果到JSON文件
    results_file = os.path.join(results_dir, f"evaluation_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(stats, f, indent=4)
    
    # 打印评估结果
    print("\n评估完成!")
    print(f"结果已保存到: {results_file}")
    print("\n评估统计:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue:.2f}")
        else:
            print(f"{key}: {value:.2f}")

def main():
    """
    主函数：查找最新的模型文件并开始评估
    
    功能:
        1. 在models目录下查找最新的模型文件
        2. 调用evaluate_model函数进行评估
        3. 处理可能的错误情况
    """
    # 检查模型目录是否存在
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("错误：未找到模型目录")
        return
    
    # 获取所有模型文件（.zip格式）
    model_files = [f for f in os.listdir(models_dir) if f.startswith('model_') and f.endswith('.zip')]
    if not model_files:
        print("错误：未找到模型文件")
        return
    
    # 根据文件名中的步数选择最新的模型
    latest_model = max(model_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
    model_path = os.path.join(models_dir, latest_model)
    
    print(f"找到最新模型: {latest_model}")
    print(f"模型路径: {model_path}")
    
    # 开始评估
    evaluate_model(model_path)

if __name__ == "__main__":
    main() 