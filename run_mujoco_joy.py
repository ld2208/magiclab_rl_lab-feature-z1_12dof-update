import numpy as np
import time
import sys
import termios
import tty
import select
import os
import mujoco
import gymnasium as gym
from gymnasium import spaces

# ==========================================
# 配置 (必须与 XML 一致)
# ==========================================
class RobotConfig:
    # 这里的 XML 路径就是你之前下载的官方文件
    XML_PATH = "z1_12dof.xml"
    
    # 动作维度
    ACTION_DIM = 12
    
    # 初始站立姿态 (左腿6个，右腿6个)
    # 0.6 是膝盖弯曲，-0.3 是髋/踝的反向补偿，保持直立
    NOMINAL_POSE = np.array([
        -0.3, 0.0, 0.0, 0.6, -0.3, 0.0,  # 左腿
        -0.3, 0.0, 0.0, 0.6, -0.3, 0.0   # 右腿
    ], dtype=np.float32)
    
    KP = 60.0 # 刚度
    KD = 2.0  # 阻尼
    DT = 0.002 # 500Hz

# ==========================================
# MuJoCo 仿真环境
# ==========================================
class MagicDogMuJoCoEnv(gym.Env):
    def __init__(self):
        super().__init__()
        
        if not os.path.exists(RobotConfig.XML_PATH):
            print(f"❌ 错误：找不到 {RobotConfig.XML_PATH}")
            print("请确保你已经把官方的 XML 和 meshes 文件夹放到了这里！")
            sys.exit(1)
            
        print(f"[MuJoCo] 正在加载模型: {RobotConfig.XML_PATH}")
        
        # 动态注入地板 (因为官方 XML 可能只有机器人没有地板)
        self.full_xml = self._add_floor(RobotConfig.XML_PATH)
        
        self.model = mujoco.MjModel.from_xml_path(self.full_xml)
        self.data = mujoco.MjData(self.model)
        
        # 仿真步长
        self.model.opt.timestep = RobotConfig.DT

    def _add_floor(self, xml_path):
        """给机器人脚下加个地板，不然会掉进深渊"""
        with open(xml_path, 'r') as f: content = f.read()
        if "plane" in content: return xml_path # 如果已有地板直接返回
        
        # 注入地板和光照
        scene = """
        <worldbody>
            <light pos="0 0 3" dir="0 0 -1" />
            <geom name="floor_generated" type="plane" size="10 10 0.1" rgba=".8 .8 .8 1"/>
        """
        # 插入到 <mujoco> 标签后，或者替换第一个 <worldbody>
        if "<worldbody>" in content:
            new_content = content.replace("<worldbody>", scene)
        else:
            # 如果没有 worldbody (通常只有 include)，则包裹一层
            new_content = content.replace("</mujoco>", scene + "</worldbody></mujoco>")
            
        with open("temp_mujoco_preview.xml", "w") as f: f.write(new_content)
        return "temp_mujoco_preview.xml"

    def reset(self):
        mujoco.mj_resetData(self.model, self.data)
        
        # 1. 设置高度 (防止卡在地里)
        self.data.qpos[2] = 0.8 
        
        # 2. 设置初始关节角度
        # 这里的 7 是因为前 7 个值是基座的 (x,y,z) 和 (qw,qx,qy,qz)
        self.data.qpos[7 : 7+12] = RobotConfig.NOMINAL_POSE
        
        # 3. 预热几步
        mujoco.mj_forward(self.model, self.data)
        for _ in range(50): 
            mujoco.mj_step(self.model, self.data)
            
        return self._get_obs()

    def step(self, action):
        # 动作叠加到标称姿态上
        target_q = RobotConfig.NOMINAL_POSE + action
        
        # 手写 PD 控制器 (模拟真实电机)
        current_q = self.data.qpos[7 : 7+12]
        current_dq = self.data.qvel[6 : 6+12]
        
        # τ = Kp * (target - current) - Kd * velocity
        torques = RobotConfig.KP * (target_q - current_q) - RobotConfig.KD * current_dq
        self.data.ctrl[:] = torques
        
        mujoco.mj_step(self.model, self.data)
        return self._get_obs()

    def _get_obs(self):
        return np.concatenate([
            self.data.qpos[7:19], 
            self.data.qvel[6:18]
        ])

# ==========================================
# 键盘控制逻辑
# ==========================================
class KeyboardController:
    def __init__(self):
        self.action = np.zeros(12)
        print("\n=== 🎮 MuJoCo 键盘控制台 ===")
        print(" W/S : 左髋 (抬腿/放腿)")
        print(" I/K : 右髋 (抬腿/放腿)")
        print(" Q   : 退出")
        print("============================")

    def get_action(self):
        key = self._get_key()
        step = 0.05
        
        # 控制逻辑 (对应 RobotConfig.NOMINAL_POSE 的索引)
        if key == 'w': self.action[0] += step  # 左 Hip Pitch
        elif key == 's': self.action[0] -= step
        elif key == 'i': self.action[6] += step # 右 Hip Pitch
        elif key == 'k': self.action[6] -= step
        elif key == 'q': return None
        
        # 自动回中 (松手后腿会慢慢放回去)
        self.action *= 0.95
        return self.action

    def _get_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            r, _, _ = select.select([sys.stdin], [], [], 0.01)
            if r: return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return None

# ==========================================
# 主运行入口
# ==========================================
def main():
    # 1. 启动环境
    env = MagicDogMuJoCoEnv()
    controller = KeyboardController()
    
    # 2. 启动查看器 (Viewer)
    import mujoco.viewer
    
    print(">>> 正在启动 MuJoCo 查看器...")
    print(">>> 请点击查看器窗口，然后在终端按键盘控制机器人")
    
    with mujoco.viewer.launch_passive(env.model, env.data) as viewer:
        env.reset()
        while viewer.is_running():
            # 获取键盘指令
            action = controller.get_action()
            if action is None: break
            
            # 物理步进
            env.step(action)
            
            # 刷新画面
            viewer.sync()
            time.sleep(RobotConfig.DT)

if __name__ == "__main__":
    # 确保安装了 mujoco 库
    try:
        import mujoco.viewer
        main()
    except ImportError:
        print("请先安装 MuJoCo: pip install mujoco")
