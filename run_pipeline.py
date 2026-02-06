import os
import subprocess
import torch
import time
import sys

def main():
    print("\n" + "="*40)
    print("   MagicLab Z1 擦玻璃 Sim-to-Real")
    print("="*40)
    print("1. [仿真] 开始 Isaac Lab 训练 (GPU 加速)")
    print("2. [预览] 查看仿真效果 (MuJoCo 窗口)")
    print("3. [真机] 部署到 Z1 机器人")
    choice = input("\n请选择 (1/2/3): ")

    # 任务 ID 必须与你在 __init__.py 注册的一致
    task_id = "Magiclab-Z1-12dof-Wiping"

    if choice == "1":
        print("\n>>> 正在启动训练...")
        subprocess.run([sys.executable, "scripts/rsl_rl/train.py", "--task", task_id, "--headless"])
        
    elif choice == "2":
        print("\n>>> 正在启动仿真预览...")
        subprocess.run([sys.executable, "scripts/rsl_rl/play.py", "--task", task_id])
        
    elif choice == "3":
        from robot_interfaces import MagicBotRealEnv
        # 对应 rsl_rl 默认保存路径
        model_path = "logs/rsl_rl/magiclab_z1_12dof_wiping/model.pt"
        if not os.path.exists(model_path):
            print(f"❌ 找不到模型文件: {model_path}")
            return
            
        policy = torch.jit.load(model_path).cuda()
        env = MagicBotRealEnv()
        
        print("🤖 开始连接真机执行动作... (Ctrl+C 停止)")
        try:
            while True:
                obs = env.latest_obs
                if obs is not None:
                    with torch.no_grad():
                        action = policy(obs)
                    env.step(action)
                time.sleep(0.02)
        except KeyboardInterrupt:
            env.close()

if __name__ == "__main__":
    main()
