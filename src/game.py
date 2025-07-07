from typing import Optional, Dict, Any
from .environment import MinimetroEnvironment
from .pygame_renderer import PygameRenderer
from .config import GameConfig, RewardConfig


class MinimetroGame:
    def __init__(self, config: GameConfig = None, reward_config: RewardConfig = None):
        self.config = config or GameConfig()
        self.reward_config = reward_config or RewardConfig()
        self.env = MinimetroEnvironment(self.config, self.reward_config)
        self.renderer = None
        
        if self.config.mode == 'pygame':
            self.renderer = PygameRenderer(self.config)
    
    def play(self, agent=None, max_steps: Optional[int] = None):
        observation = self.env.reset()
        done = False
        step_count = 0
        
        while not done and (max_steps is None or step_count < max_steps):
            if self.config.mode == 'pygame':
                if not self.renderer.render(observation):
                    break
            elif self.config.mode == 'agent':
                print(self.env.render())
                print("-" * 50)
            
            if agent is not None:
                action = agent.get_action(observation)
            else:
                action = self._get_human_action()
            
            observation, reward, done, info = self.env.step(action)
            step_count += 1
            
            if self.config.mode == 'agent':
                print(f"Action: {action}")
                print(f"Reward: {reward}")
                print(f"Info: {info}")
                print()
        
        if self.renderer:
            self.renderer.close()
        
        return observation
    
    def _get_human_action(self) -> Dict[str, Any]:
        if self.config.mode == 'pygame':
            return {'action': 'none'}
        
        print("Available actions:")
        print("1. Create line (format: create x1,y1 x2,y2)")
        print("2. Extend line (format: extend line_id x,y)")
        print("3. Remove line (format: remove line_id)")
        print("4. No action (format: none)")
        
        try:
            user_input = input("Enter action: ").strip().lower()
            
            if user_input == 'none':
                return {'action': 'none'}
            
            parts = user_input.split()
            
            if parts[0] == 'create' and len(parts) == 3:
                from_coords = tuple(map(int, parts[1].split(',')))
                to_coords = tuple(map(int, parts[2].split(',')))
                return {
                    'action': 'create_line',
                    'from': from_coords,
                    'to': to_coords
                }
            
            elif parts[0] == 'extend' and len(parts) == 3:
                line_id = int(parts[1])
                to_coords = tuple(map(int, parts[2].split(',')))
                return {
                    'action': 'extend_line',
                    'line_id': line_id,
                    'to': to_coords
                }
            
            elif parts[0] == 'remove' and len(parts) == 2:
                line_id = int(parts[1])
                return {
                    'action': 'remove_line',
                    'line_id': line_id
                }
            
            else:
                print("Invalid action format")
                return {'action': 'none'}
        
        except (ValueError, IndexError):
            print("Invalid input format")
            return {'action': 'none'}


class SimpleAgent:
    def __init__(self, env: MinimetroEnvironment):
        self.env = env
    
    def get_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        valid_actions = self.env.get_valid_actions()
        
        create_actions = [a for a in valid_actions if a['action'] == 'create_line']
        if create_actions:
            return self.env.engine.random.choice(create_actions)
        
        extend_actions = [a for a in valid_actions if a['action'] == 'extend_line']
        if extend_actions:
            return self.env.engine.random.choice(extend_actions)
        
        return {'action': 'none'}