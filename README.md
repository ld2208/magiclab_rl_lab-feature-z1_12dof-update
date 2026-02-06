
# MagicLab RL Lab (Isaac Lab)

## 📖 项目概述
本项目是基于 **NVIDIA Isaac Lab** 构建的强化学习扩展库，专为 **MagicLab Z1-12dof** 人形机器人设计。它支持大规模并行仿真训练，并提供从仿真到真机（Sim-to-Real）的完整部署方案。

目前支持的任务：
*   **Velocity Tracking**: 基础移动与全向速度指令跟踪。
*   **Wiping Task**: 擦玻璃任务（基于右腿末端轨迹跟踪与三腿支撑平衡）。

---

## 🛠 安装指南

### 1. 基础环境
*   **Isaac Lab**: 请确保已安装并配置好 [Isaac Lab](https://isaac-sim.github.io/IsaacLab/) 环境。
*   **MagicDog SDK**: 真机部署需要官方 Python SDK 驱动支持。

### 2. 下载与部署项目
请将本项目克隆至 Isaac Lab 目录之外，并执行安装脚本：

```bash
# 克隆仓库
git clone https://github.com/ld2208/magiclab_rl_lab-feature-z1_12dof-update.git
cd magiclab_rl_lab

# 激活环境
conda activate env_isaaclab

# 安装扩展并注册任务
./magiclab_rl_lab.sh -i
```

---

## 🚀 快速开始 (一键流水线)
项目根目录提供了一个总控脚本 `run_pipeline.py`，建议通过此脚本进行所有操作：

```bash
python run_pipeline.py
```

**菜单选项说明：**
1.  **[Isaac仿真训练]**: 在 GPU 上并行启动 4096 个环境进行高强度训练。
2.  **[仿真效果预览]**: 启动图形化窗口，验证训练好的模型是否能正确擦玻璃。
3.  **[真机部署运行]**: 连接网线，将训练产出的 `.pt` 权重下发给真实 Z1 机器人。

---

## 📋 任务列表

| 任务 ID | 功能描述 | 手动训练命令 |
| :--- | :--- | :--- |
| `Magiclab-Z1-12dof-Velocity` | 基础行走训练 | `python scripts/rsl_rl/train.py --task Magiclab-Z1-12dof-Velocity --headless` |
| `Magiclab-Z1-12dof-Wiping` | 擦玻璃任务 | `python scripts/rsl_rl/train.py --task Magiclab-Z1-12dof-Wiping --headless` |

---

## 🤖 真机部署 (Sim-to-Real)

### 1. 网络环境配置
真机部署要求本机与机器人处于同一网段：
*   **本机静态 IP**: `192.168.55.10`
*   **机器人 IP**: `192.168.55.200`

**必须配置组播路由（否则无法获取传感器回传）：**
```bash
# 将 <interface> 替换为你的有线网卡名（如 eno1）
sudo ifconfig <interface> multicast
sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev <interface>
```

### 2. 部署运行
确保机器人周围空旷，运行 `run_pipeline.py` 并选择选项 **3**。

---

## ⚠️ 安全守则
*   **急停**: 进行真机部署时，手指必须时刻放在机器人的 **物理急停开关** 上。
*   **防护**: 首次运行新策略模型，建议将机器人进行 **吊装保护**，防止异常动作导致机械损坏。
*   **监控**: 通过终端日志观察实时状态误差，若出现高频震荡请立即终止程序。

---

## 🤝 致谢
本项目基于以下开源框架构建：
*   **IsaacLab**: 核心物理引擎与并行架构。
*   **rsl_rl**: 强化学习训练算法。
*   **magicdog_sdk**: 官方底层通讯接口。
```
