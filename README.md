
MagicLab RL Lab (Isaac Lab)-UPDATE版
📖 Overview
本项目是基于 NVIDIA Isaac Lab 开发的强化学习环境，专为 MagicLab Z1-12dof 人形机器人设计。
它支持大规模并行仿真训练，并提供完整的 Sim-to-Real (仿真到真机) 部署工具链。


目前支持的任务：
Velocity Tracking: 基础行走与速度跟踪。
Wiping Task: 擦玻璃任务（基于右腿末端轨迹跟踪）。



🛠 Installation
1. 环境依赖
Isaac Lab: 请先按照 Isaac Lab 官方指南 完成安装。
MagicDog SDK: 真机部署需要安装官方 Python SDK（参考 magicdog_sdk 文档）。
2. 下载与安装本项目
克隆仓库并将其安装为独立扩展包：
code
Bash
# 克隆仓库
git clone https://github.com/MagiclabRoboticsrobotics/magiclab_rl_lab.git
cd magiclab_rl_lab

# 激活 Isaac Lab 环境
conda activate env_isaaclab

# 安装项目依赖并注册扩展
./magiclab_rl_lab.sh -i
🚀 Usage (One-Click Pipeline)
为了简化操作，项目提供了一个一键式总控脚本 run_pipeline.py。
code
Bash
python run_pipeline.py
选项说明：
[Isaac仿真训练]: 启动 GPU 并行训练（默认 4096 台机器人）。
[仿真效果预览]: 开启 MuJoCo/Isaac 窗口，预览练好的模型效果（Sim2Sim）。
[真机部署运行]: 连接真实 Z1 机器人，加载训练好的 .pt 大脑。
📋 Available Tasks
任务 ID	说明	训练命令 (--task)
Magiclab-Z1-12dof-Velocity	基础行走/速度跟踪	python scripts/rsl_rl/train.py --task Magiclab-Z1-12dof-Velocity --headless
Magiclab-Z1-12dof-Wiping	擦玻璃任务	python scripts/rsl_rl/train.py --task Magiclab-Z1-12dof-Wiping --headless
🤖 Real Robot Deployment (Sim-to-Real)
1. 网络配置
使用网线连接机器人，将本机 IP 设置为静态：192.168.55.10。
配置组播路由 (必须):
code
Bash
sudo ifconfig <网卡名> multicast
sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev <网卡名>
2. 部署运行
确保机器人处于安全位置（建议悬空或由支架支撑）：
code
Bash
python run_pipeline.py  # 选择选项 3
⚠️ Safety Warning
紧急停止: 在进行真机实验时，请务必确保手指放在机器人的 物理急停按钮 上。
保护架: 首次测试新模型时，务必使用吊装架，防止机器人由于输出异常力矩导致摔跌或机械损坏。
低压保护: 请监控电池状态，低压可能导致控制延迟或姿态崩塌。
🤝 Acknowledgements
本项目基于以下开源项目构建：
IsaacLab: 核心仿真框架。
rsl_rl: 高效的强化学习算法库。
magicdog_sdk: 官方底层通讯 SDK。
💡 修改说明：
增加了 Wiping Task：明确列出了新开发的擦玻璃任务。
强化了 run_pipeline.py：将其作为新手友好的主要入口。
补充了网络配置：很多人 Sim2Real 失败是因为忘了配置组播路由，这里特别标出。
加入了安全警告：对于人形机器人 Z1 来说，安全预防措施是必须写在 README 里的。
规范了安装流程：确保用户知道必须先激活 conda 环境。
