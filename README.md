# FlappyAI

使用强化学习（PPO算法）来玩 Flappy Bird 游戏的项目。该项目使用 Gymnasium 作为强化学习环境，Stable-Baselines3 作为强化学习算法实现。

## 项目结构

```
FlappyAI/
├── assets/               # 游戏资源文件
│   ├── audio/           # 音效文件
│   └── sprites/         # 游戏精灵图片
├── models/              # 保存训练好的模型
├── logs/                # 训练日志
├── flappy_env.py        # Flappy Bird 游戏环境
├── flappy_train.py      # 模型训练脚本
├── flappy_agent.py      # 使用预训练模型进行游戏
├── check_all.py         # 环境检查脚本
└── requirements.txt     # 项目依赖
```

## 环境要求

- Python 3.10+
- PyTorch
- Gymnasium
- Stable-Baselines3
- Pygame
- TensorBoard
- TensorFlow (可选)

## 安装

1. 克隆项目：
```bash
git clone https://github.com/yourusername/FlappyAI.git
cd FlappyAI
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 环境检查
运行环境检查脚本，确保所有依赖都正确安装：
```bash
python check_all.py
```

### 训练模型
运行训练脚本：
```bash
python flappy_train.py
```

### 使用预训练模型
使用预训练模型进行游戏：
```bash
python flappy_agent.py
```

## 游戏环境说明

### 观察空间
- 小鸟到上管道的距离
- 小鸟到下管道的距离
- 到下一个管道的水平距离

### 动作空间
- 0: 不跳跃
- 1: 跳跃

### 奖励系统
- 通过管道: +1
- 死亡: -1
- 撞到顶部: -2
- 生存奖励: 每帧 +0.001
- 移动惩罚: 每次移动 -0.001

## 训练参数

- 算法: PPO
- 学习率: 3e-4
- 步数: 2048
- 批次大小: 64
- 训练轮数: 10
- 折扣因子: 0.99
- GAE Lambda: 0.95
- 裁剪范围: 0.2
- 熵系数: 0.01
- 价值函数系数: 0.5
- 最大梯度范数: 0.5
- 目标KL散度: 0.01

## 项目特点

1. 完整的强化学习环境实现
2. 使用 PPO 算法进行训练
3. 实时游戏画面渲染
4. 详细的训练日志记录
5. 环境检查工具
6. 预训练模型支持

## 注意事项

1. 确保有足够的计算资源进行训练
2. 如果使用 GPU，确保已安装 CUDA 和相应的 PyTorch 版本
3. 训练过程中可以随时中断，模型会自动保存
4. 可以通过 TensorBoard 查看训练过程

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

MIT License
