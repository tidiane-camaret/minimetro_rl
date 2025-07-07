#!/usr/bin/env python3
"""
Test script for MinimetroRL Gymnasium environment.
"""

import numpy as np
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(__file__))

from src.gym_env import MinimetroGymEnv
from src.config import GameConfig, RewardConfig


def test_basic_functionality():
    """Test basic environment functionality."""
    print("Testing basic gym environment functionality...")
    
    # Create environment
    config = GameConfig(grid_size=5, max_timesteps=100)
    env = MinimetroGymEnv(config=config)
    
    print(f"Action space: {env.action_space}")
    print(f"Observation space keys: {list(env.observation_space.spaces.keys())}")
    print(f"Grid shape: {env.observation_space['grid'].shape}")
    print(f"Passengers shape: {env.observation_space['passengers'].shape}")
    
    # Test reset
    obs, info = env.reset(seed=42)
    print(f"Initial observation keys: {list(obs.keys())}")
    print(f"Initial grid shape: {obs['grid'].shape}")
    print(f"Initial timestep: {obs['timestep']}")
    print(f"Initial score: {obs['score']}")
    
    # Test a few steps
    for i in range(5):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {i+1}: action={action}, reward={reward}, terminated={terminated}, score={obs['score']}")
        
        if terminated:
            print("Episode terminated early!")
            break
    
    env.close()
    print("Basic functionality test completed!\n")


def test_action_mapping():
    """Test action mapping functionality."""
    print("Testing action mapping...")
    
    config = GameConfig(grid_size=3, max_lines=2)
    env = MinimetroGymEnv(config=config)
    
    # Test a few specific actions
    test_actions = [0, 1, 10, 50]
    
    for action in test_actions:
        if action < env.action_space.n:
            action_dict = env._convert_action(action)
            print(f"Action {action} -> {action_dict}")
    
    env.close()
    print("Action mapping test completed!\n")


def test_observation_conversion():
    """Test observation conversion."""
    print("Testing observation conversion...")
    
    config = GameConfig(grid_size=4, max_lines=2)
    env = MinimetroGymEnv(config=config)
    
    obs, info = env.reset(seed=123)
    
    # Check observation structure
    print(f"Observation structure:")
    for key, value in obs.items():
        print(f"  {key}: {value.shape} (dtype: {value.dtype})")
        if key == 'grid':
            print(f"    Grid sample:\n{value}")
    
    env.close()
    print("Observation conversion test completed!\n")


def test_random_episode():
    """Run a complete random episode."""
    print("Testing complete random episode...")
    
    config = GameConfig(grid_size=6, max_timesteps=50)
    env = MinimetroGymEnv(config=config)
    
    obs, info = env.reset(seed=456)
    total_reward = 0
    steps = 0
    
    print(f"Starting episode with {env.action_space.n} possible actions")
    
    while True:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        total_reward += reward
        steps += 1
        
        if steps % 10 == 0:
            print(f"Step {steps}: score={obs['score']}, reward={reward}")
        
        if terminated or truncated:
            print(f"Episode ended after {steps} steps")
            print(f"Final score: {obs['score']}")
            print(f"Total reward: {total_reward}")
            break
    
    env.close()
    print("Random episode test completed!\n")


def main():
    """Run all tests."""
    print("=== MinimetroRL Gymnasium Environment Tests ===\n")
    
    try:
        test_basic_functionality()
        test_action_mapping()
        test_observation_conversion()
        test_random_episode()
        
        print("=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())