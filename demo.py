#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import random
from config import GameConfig, RewardConfig
from game_engine import GameEngine
from types import Action, Position


def main():
    print("=== MinimetroRL Demo ===")
    
    config = GameConfig(
        grid_size=5,
        max_timesteps=50,
        mode='agent',
        station_spawn_rate=10,
        passenger_spawn_rate=5
    )
    
    engine = GameEngine(config)
    
    print("Running demo with simple AI agent...")
    print("Configuration:")
    print(f"  Grid size: {config.grid_size}x{config.grid_size}")
    print(f"  Max timesteps: {config.max_timesteps}")
    print(f"  Station spawn rate: {config.station_spawn_rate}")
    print(f"  Passenger spawn rate: {config.passenger_spawn_rate}")
    print()
    
    engine.reset()
    done = False
    step_count = 0
    
    while not done and step_count < 20:
        print(f"Step {step_count + 1}:")
        obs = engine.get_observation()
        print(f"Timestep: {obs['timestep']}, Score: {obs['score']}")
        print(f"Stations: {len(engine.state.stations)}, Lines: {len(obs['lines'])}")
        
        # Simple agent logic - try to create a line
        if len(obs['lines']) < config.max_lines and engine.state.stations:
            # Try to create a line between two adjacent positions
            for x in range(config.grid_size - 1):
                for y in range(config.grid_size):
                    from_pos = Position(x, y)
                    to_pos = Position(x + 1, y)
                    action = Action(action_type='create_line', from_pos=from_pos, to_pos=to_pos)
                    break
                break
        else:
            action = Action(action_type='none')
        
        state, reward, done, info = engine.step(action)
        print(f"Action: {action.action_type}")
        print(f"Reward: {reward}")
        print(f"Info: {info}")
        print("-" * 50)
        
        step_count += 1
    
    final_obs = engine.get_observation()
    
    print("\n=== Game Complete ===")
    print(f"Final score: {final_obs['score']}")
    print(f"Final timestep: {final_obs['timestep']}")
    print(f"Game over: {final_obs['game_over']}")
    print(f"Lines built: {len(final_obs['lines'])}")
    
    if final_obs['passengers']:
        total_waiting = sum(sum(p.values()) for p in final_obs['passengers'].values())
        print(f"Passengers still waiting: {total_waiting}")


if __name__ == "__main__":
    main()