import numpy as np
import torch
import time
import threading
import sys

class MagicBotRealEnv:
    def __init__(self, ip="192.168.55.10"):
        # 确保能导入你 PDF 文档里的 SDK
        try:
            import magicdog_python as magicdog
            from magicdog_python import ErrorCode
        except ImportError:
            print("❌ 错误：找不到 magicdog_python SDK，请确保已安装。")
            sys.exit(1)

        # 标称姿态（必须与 Isaac Lab 仿真一致）
        self.nominal_pose = np.array([-0.3, 0.0, 0.0, 0.6, -0.3, 0.0] * 2, dtype=np.float32)
        
        self.robot = magicdog.MagicRobot()
        self.robot.initialize(ip)
        self.robot.connect()
        self.robot.set_motion_control_level(magicdog.ControllerLevel.LOW_LEVEL)
        self.controller = self.robot.get_low_level_motion_controller()
        
        self.latest_obs = None
        self.lock = threading.Lock()
        self.controller.subscribe_leg_state(self._sdk_callback)

    def _sdk_callback(self, msg):
        q = np.array([j.q for j in msg.state])
        dq = np.array([j.dq for j in msg.state])
        # 27维观测：12角度误差 + 12速度 + 3位移误差占位
        obs = np.concatenate([q - self.nominal_pose, dq, [0,0,0]])
        with self.lock:
            # 转换为 Isaac 模型需要的 GPU Tensor
            self.latest_obs = torch.from_numpy(obs).float().unsqueeze(0).cuda()

    def step(self, action_tensor):
        import magicdog_python as magicdog
        act = action_tensor.squeeze().cpu().numpy()
        target_q = self.nominal_pose + act
        
        cmd = magicdog.LegJointCommand()
        for i in range(12):
            cmd.cmd[i].q_des = float(target_q[i])
            cmd.cmd[i].kp, cmd.cmd[i].kd = 60.0, 2.0
        self.controller.publish_leg_command(cmd)
        return self.latest_obs

    def close(self):
        self.robot.shutdown()
