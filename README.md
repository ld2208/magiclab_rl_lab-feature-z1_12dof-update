MagicLab RL Lab (Isaac Lab)
📖 Overview
本项目是基于 NVIDIA Isaac Lab 开发的强化学习环境扩展包，专为 MagicLab Z1-12dof 人形机器人定制。它利用 GPU 并行加速实现大规模仿真训练，并提供从仿真到真机（Sim-to-Real）的一键部署工具。
目前支持的任务：
Velocity Tracking: 基础行走与速度跟踪。
Wiping Task: 擦玻璃任务（基于右腿末端轨迹跟踪）。
🛠 Installation
1. 环境依赖
Isaac Lab: 请确保已安装 Isaac Lab。
MagicDog SDK: 真机部署需安装官方 Python SDK（参考 magicdog_sdk 文档）。
2. 下载与安装本项目
请在 Isaac Lab 目录之外克隆本项目：
code
Bash
# 克隆仓库
git clone https://github.com/MagiclabRoboticsrobotics/magiclab_rl_lab.git
cd magiclab_rl_lab

# 激活 Isaac Lab 环境
conda activate env_isaaclab

# 安装依赖并注册项目扩展
./magiclab_rl_lab.sh -i
🚀 Usage (One-Click Pipeline)
项目提供了一个集成化的总控脚本 run_pipeline.py，屏蔽了复杂的命令行参数。
code
Bash
python run_pipeline.py
选项说明：
[Isaac仿真训练]: 启动 GPU 并行训练模式（默认开启 4096 个环境）。
[仿真效果预览]: 开启图形化窗口，查看练好的模型在仿真中的表现（Sim2Sim）。
[真机部署运行]: 连接真实的 Z1 机器人，加载训练产出的 .pt 策略模型。
📋 Available Tasks
任务 ID	说明	训练命令 (--task)
Magiclab-Z1-12dof-Velocity	基础行走/速度跟踪	python scripts/rsl_rl/train.py --task Magiclab-Z1-12dof-Velocity --headless
Magiclab-Z1-12dof-Wiping	擦玻璃任务	python scripts/rsl_rl/train.py --task Magiclab-Z1-12dof-Wiping --headless
🤖 Real Robot Deployment (Sim-to-Real)
1. 网络配置
使用网线连接机器人，将本机 IP 设置为静态：192.168.55.10。
配置组播路由（必须执行，否则无法收到传感器数据）：
code
Bash
# 请将 <网卡名> 替换为你的有线网卡名称（如 eno1）
sudo ifconfig <网卡名> multicast
sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev <网卡名>
2. 部署运行
运行 run_pipeline.py 并选择 选项 3。系统将自动寻找 logs/ 文件夹下最新的模型并下发给硬件。
⚠️ Safety Warning
急停准备: 在真机实验时，手指必须时刻放在机器人的 物理急停按钮 上。
吊装保护: 首次测试新练成的模型时，务必使用吊装架或支架支撑机器人。
环境安全: 确保机器人周围 2 米范围内无障碍物及人员。
🤝 Acknowledgements
本项目基于以下开源项目构建：
IsaacLab: 核心仿真框架。
rsl_rl: 强化学习算法库。
magicdog_sdk: 官方底层通讯 SDK 接口。
💡 提示
如果你想手动修改训练参数或奖励函数，请查看：
source/magiclab_rl_lab/magiclab_rl_lab/tasks/wiping/config/z1/wiping_env_cfg.py
