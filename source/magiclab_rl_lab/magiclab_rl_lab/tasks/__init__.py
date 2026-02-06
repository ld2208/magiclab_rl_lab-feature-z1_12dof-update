##
# Register Gym environments.
##

from isaaclab_tasks.utils import import_packages

# The blacklist is used to prevent importing configs from sub-packages
_BLACKLIST_PKGS = []
# Import all configs in this package
import_packages(__name__, _BLACKLIST_PKGS)

import gymnasium as gym
from .wiping.config.z1.wiping_env_cfg import Z1WipingEnvCfg

gym.register(
    id="Magiclab-Z1-12dof-Wiping",
    entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "cfg": Z1WipingEnvCfg(),
        "rsl_rl_cfg_entry_point": "magiclab_rl_lab.config.z1.agents.rsl_rl_cfg:Z1FlatPPOCfg",
    },
)


