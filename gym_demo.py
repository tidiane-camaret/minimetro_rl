#!/usr/bin/env python3
"""
Demonstration of MinimetroRL gymnasium environment usage.
"""

import numpy as np
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(__file__))

from src.gym_env import MinimetroGymEnv
from src.config import GameConfig, RewardConfig


class RandomAgent:
    """Simple random agent for demonstration."""
    
    def __init__(self, action_space):
        self.action_space = action_space
    
    def act(self, observation):
        """Choose a random action."""
        return self.action_space.sample()


class SimpleHeuristicAgent:
    """Simple heuristic agent that tries to make meaningful moves."""
    
    def __init__(self, action_space, env):
        self.action_space = action_space
        self.env = env
    
    def act(self, observation):
        """Choose an action using simple heuristics."""
        # Get valid actions from environment
        valid_actions = self.env.env.get_valid_actions()
        
        # If we have valid actions other than 'none', prioritize them
        non_none_actions = [a for a in valid_actions if a['action'] != 'none']
        
        if non_none_actions:
            # Choose randomly among valid non-none actions
            chosen_action_dict = np.random.choice(non_none_actions)
            
            # Find the corresponding discrete action
            for action_idx, action_dict in self.env._action_map.items():
                if self._actions_match(action_dict, chosen_action_dict):
                    return action_idx
        
        # Fall back to random action if no valid actions found
        return 0  # 'none' action
    
    def _actions_match(self, action1, action2):
        """Check if two action dictionaries match."""
        if action1['action'] != action2['action']:
            return False
        
        # Check specific parameters for each action type
        if action1['action'] == 'create_line':
            return (action1.get('from') == action2.get('from') and
                    action1.get('to') == action2.get('to'))
        elif action1['action'] == 'extend_line':
            return (action1.get('line_id') == action2.get('line_id') and
                    action1.get('to') == action2.get('to'))
        elif action1['action'] == 'remove_line':
            return action1.get('line_id') == action2.get('line_id')
        
        return True


def run_episode(env, agent, render=False, max_steps=1000):
    """Run a single episode with the given agent."""
    obs, info = env.reset()
    total_reward = 0
    steps = 0
    
    while steps < max_steps:
        if render:
            print(f"\nStep {steps}:")
            print(env.render())
        
        action = agent.act(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        
        total_reward += reward
        steps += 1
        
        if terminated or truncated:
            break
    
    return total_reward, steps, obs['score']


def compare_agents():
    """Compare performance of different agents."""
    print("=== Agent Performance Comparison ===\n")
    
    # Create environment
    config = GameConfig(grid_size=8, max_timesteps=200)
    env = MinimetroGymEnv(config=config)
    
    # Test agents
    agents = {
        'Random': RandomAgent(env.action_space),
        'Simple Heuristic': SimpleHeuristicAgent(env.action_space, env),
    }
    
    num_episodes = 10
    
    for agent_name, agent in agents.items():
        print(f"Testing {agent_name} agent...")
        
        rewards = []
        steps = []
        scores = []
        
        for episode in range(num_episodes):
            total_reward, num_steps, final_score = run_episode(env, agent)
            rewards.append(total_reward)
            steps.append(num_steps)
            scores.append(final_score)
            
            if episode % 5 == 0:
                print(f"  Episode {episode}: reward={total_reward:.1f}, steps={num_steps}, score={final_score:.1f}")
        
        print(f"  Average reward: {np.mean(rewards):.1f} ± {np.std(rewards):.1f}")
        print(f"  Average steps: {np.mean(steps):.1f} ± {np.std(steps):.1f}")
        print(f"  Average score: {np.mean(scores):.1f} ± {np.std(scores):.1f}")
        print()
    
    env.close()


def analyze_observation_space():
    """Analyze the observation space of the environment."""
    print("=== Observation Space Analysis ===\n")
    
    config = GameConfig(grid_size=5, max_timesteps=100)
    env = MinimetroGymEnv(config=config)
    
    print("Observation Space:")
    for key, space in env.observation_space.spaces.items():
        print(f"  {key}: {space}")
    
    print("\nAction Space:")
    print(f"  Discrete actions: {env.action_space.n}")
    
    # Sample observation
    obs, info = env.reset(seed=42)
    print("\nSample Observation:")
    for key, value in obs.items():
        print(f"  {key}: shape={value.shape}, dtype={value.dtype}")
        if key == 'grid':
            print(f"    Sample values: {np.unique(value)}")
        elif key == 'passengers':
            print(f"    Total passengers: {np.sum(value)}")
    
    env.close()


def interactive_demo():
    """Run an interactive demonstration."""
    print("=== Interactive Demo ===\n")
    
    config = GameConfig(grid_size=6, max_timesteps=50)
    env = MinimetroGymEnv(config=config)
    
    agent = SimpleHeuristicAgent(env.action_space, env)
    
    print("Running interactive demo with simple heuristic agent...")
    print("The agent will try to make meaningful moves automatically.\n")
    
    total_reward, steps, final_score = run_episode(env, agent, render=True)
    
    print(f"\nDemo completed!")
    print(f"Total reward: {total_reward}")
    print(f"Steps taken: {steps}")
    print(f"Final score: {final_score}")
    
    env.close()


def main():
    """Main demonstration script."""
    print("MinimetroRL Gymnasium Environment Demo\n")
    
    try:
        # Run different demonstrations
        analyze_observation_space()
        compare_agents()
        interactive_demo()
        
        print("\n=== Demo completed successfully! ===")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())