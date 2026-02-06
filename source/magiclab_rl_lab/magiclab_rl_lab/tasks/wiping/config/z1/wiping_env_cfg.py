import math
import torch
from omni.isaac.lab.utils import configclass
from omni.isaac.lab.managers import RewardTermCfg as RewTerm
from omni.isaac.lab.envs import ManagerBasedRLEnvCfg
# 引用同目录层级的 locomotion 配置作为基础
from magiclab_rl_lab.tasks.locomotion.velocity.config.z1.rough_env_cfg import Z1RoughEnvCfg

@configclass
class Z1WipingEnvCfg(Z1RoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        # 设置并行环境数量
        self.scene.num_envs = 4096
        self.scene.robot.init_state.pos = (0.0, 0.0, 0.6)
        
        # 注入擦玻璃专用奖励
        # 1. 追踪红球奖励：让右脚末端(link 12)靠近目标
        self.rewards.terms["track_wiping_target"] = RewTerm(
            func=self._reward_track_target, weight=15.0
        )
        # 2. 躯干稳定性奖励：防止摔倒
        self.rewards.terms["base_stability"] = RewTerm(
            func=self._reward_base_stability, weight=2.0
        )

    def _reward_track_target(self, env):
        # 目标点在 X=0.4m 平面画圆
        t = env.sim.current_time
        target_y = 0.15 * math.sin(t * 3.0)
        target_z = 0.5 + 0.15 * math.cos(t * 3.0)
        target_pos = torch.tensor([0.4, target_y, target_z], device=env.device)
        
        # 获取机器人右脚末端位置
        current_pos = env.scene["robot"].data.body_pos_w[:, 12] 
        dist = torch.norm(current_pos - target_pos, dim=-1)
        return torch.exp(-10.0 * dist)

    def _reward_base_stability(self, env):
        # 奖励躯干指向上方
        return env.scene["robot"].data.root_quat_w[:, 2]
