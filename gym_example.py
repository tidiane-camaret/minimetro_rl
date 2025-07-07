#!/usr/bin/env python3
"""
Simple example showing how to use the MinimetroRL gymnasium environment.
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(__file__))

from src.gym_env import MinimetroGymEnv
from src.config import GameConfig


def main():
    """Basic usage example."""
    print("MinimetroRL Gymnasium Environment - Basic Usage Example\n")
    
    # Create environment with custom configuration
    config = GameConfig(
        grid_size=8,           # 8x8 grid
        max_timesteps=500,     # Maximum episode length
        max_lines=3,           # Maximum number of train lines
        station_spawn_rate=50, # Station spawns every 50 timesteps
        passenger_spawn_rate=10 # Passengers spawn every 10 timesteps
    )
    
    env = MinimetroGymEnv(config=config)
    
    print(f"Action space: {env.action_space}")
    print(f"Observation space: {env.observation_space}")
    print()
    
    # Run a simple episode
    print("Running a simple episode...")
    obs, info = env.reset(seed=42)
    
    total_reward = 0
    for step in range(20):
        # Take a random action
        action = env.action_space.sample()
        
        # Step the environment
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        print(f"Step {step+1}: action={action}, reward={reward}, score={obs['score']}")
        
        if terminated or truncated:
            print(f"Episode terminated after {step+1} steps")
            break
    
    print(f"\nEpisode completed! Total reward: {total_reward}")
    
    # Close the environment
    env.close()


if __name__ == "__main__":
    main()