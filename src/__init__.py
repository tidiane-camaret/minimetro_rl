from gymnasium.envs.registration import register

# Register the MinimetroRL environment
register(
    id="MinimetroRL-v0",
    entry_point="minimetro_rl.src.gym_env:MinimetroGymEnv",
    max_episode_steps=1000,
    reward_threshold=1000.0,
    kwargs={
        "render_mode": None,
    },
)

# Register variants with different configurations
register(
    id="MinimetroRL-Small-v0",
    entry_point="minimetro_rl.src.gym_env:MinimetroGymEnv",
    max_episode_steps=500,
    reward_threshold=500.0,
    kwargs={
        "config": None,  # Will use default small config
        "render_mode": None,
    },
)

register(
    id="MinimetroRL-Visual-v0",
    entry_point="minimetro_rl.src.gym_env:MinimetroGymEnv",
    max_episode_steps=1000,
    reward_threshold=1000.0,
    kwargs={
        "render_mode": "human",
    },
)

# Import main classes for easy access
from .gym_env import MinimetroGymEnv
from .environment import MinimetroEnvironment
from .config import GameConfig, RewardConfig
from .types import Action, Position, StationType

__all__ = [
    "MinimetroGymEnv",
    "MinimetroEnvironment", 
    "GameConfig",
    "RewardConfig",
    "Action",
    "Position",
    "StationType",
]