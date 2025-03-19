import sys
import pkg_resources
import subprocess
import platform
import logging
import torch
import tensorflow as tf
from stable_baselines3.common.env_checker import check_env
from flappy_env import FlappyEnv

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

def check_system_info():
    """检查系统基本信息"""
    print("\n=== 系统信息 ===")
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python路径: {sys.executable}")
    print("\n")

def check_dependencies():
    """检查项目依赖"""
    print("=== 依赖检查 ===")
    required_packages = [
        'gymnasium',
        'stable-baselines3',
        'pygame',
        'numpy',
        'torch',
        'tensorboard',
        'tensorflow'
    ]
    
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"{package}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"{package}: 未安装")
    print("\n")

def check_gpu_support():
    """检查GPU支持情况"""
    print("=== GPU支持检查 ===")
    
    # PyTorch GPU检查
    print("PyTorch GPU信息:")
    print(f"CUDA是否可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"当前设备: {torch.cuda.get_device_name(0)}")
    print("\n")
    
    # TensorFlow GPU检查
    print("TensorFlow GPU信息:")
    print(f"TensorFlow版本: {tf.__version__}")
    print(f"可用GPU数量: {len(tf.config.list_physical_devices('GPU'))}")
    print("\n")

def check_gymnasium_env():
    """检查Gymnasium环境"""
    print("=== Gymnasium环境检查 ===")
    try:
        import gymnasium as gym
        print(f"Gymnasium版本: {gym.__version__}")
        print(f"可用环境: {gym.envs.registry.keys()}")
    except ImportError:
        print("Gymnasium未安装")
    print("\n")

def check_flappy_env():
    """检查Flappy Bird环境"""
    print("=== Flappy Bird环境检查 ===")
    try:
        env = FlappyEnv()
        print("环境创建成功")
        
        # 检查环境接口
        print("\n检查环境接口:")
        check_env(env)
        
        # 测试环境运行
        print("\n测试环境运行:")
        obs, _ = env.reset()
        print(f"初始观察值: {obs}")
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"执行动作后的观察值: {obs}")
        print(f"奖励: {reward}")
        print(f"是否结束: {done}")
        print(f"是否截断: {truncated}")
        print(f"信息: {info}")
        
        env.close()
        print("\n环境测试完成")
    except Exception as e:
        print(f"环境检查失败: {e}")
    print("\n")

def main():
    print("=== FlappyAI 环境检查报告 ===\n")
    check_system_info()
    check_dependencies()
    check_gpu_support()
    check_gymnasium_env()
    check_flappy_env()
    print("=== 检查完成 ===\n")

if __name__ == "__main__":
    main() 