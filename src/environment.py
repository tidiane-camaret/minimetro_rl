from typing import Dict, Any, Tuple, Optional
from .game_engine import GameEngine
from .types import Action, Position
from .config import GameConfig, RewardConfig


class MinimetroEnvironment:
    def __init__(self, config: GameConfig = None, reward_config: RewardConfig = None):
        self.config = config or GameConfig()
        self.reward_config = reward_config or RewardConfig()
        self.engine = GameEngine(self.config, self.reward_config)
    
    def reset(self) -> Dict[str, Any]:
        self.engine.reset()
        return self.engine.get_observation()
    
    def step(self, action_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], int, bool, Dict[str, Any]]:
        action = self._parse_action(action_dict)
        state, reward, done, info = self.engine.step(action)
        observation = self.engine.get_observation()
        return observation, reward, done, info
    
    def _parse_action(self, action_dict: Dict[str, Any]) -> Action:
        action_type = action_dict.get('action', 'none')
        
        if action_type == 'create_line':
            from_pos = Position(*action_dict['from'])
            to_pos = Position(*action_dict['to'])
            return Action(action_type=action_type, from_pos=from_pos, to_pos=to_pos)
        
        elif action_type == 'extend_line':
            line_id = action_dict['line_id']
            to_pos = Position(*action_dict['to'])
            return Action(action_type=action_type, line_id=line_id, to_pos=to_pos)
        
        elif action_type == 'remove_line':
            line_id = action_dict['line_id']
            return Action(action_type=action_type, line_id=line_id)
        
        else:
            return Action(action_type='none')
    
    def render(self) -> Optional[str]:
        if self.config.mode == 'agent':
            return self._render_text()
        return None
    
    def _render_text(self) -> str:
        obs = self.engine.get_observation()
        lines = []
        
        lines.append(f"Timestep: {obs['timestep']}, Score: {obs['score']}")
        lines.append(f"Game Over: {obs['game_over']}")
        #lines.append()
        
        grid = obs['grid']
        for y in range(len(grid)):
            row = ""
            for x in range(len(grid[y])):
                tile = grid[y][x]
                if tile == 'empty':
                    row += "."
                elif tile == 'circle':
                    row += "O"
                elif tile == 'square':
                    row += "□"
                elif tile == 'triangle':
                    row += "△"
                row += " "
            lines.append(row)
        
        #lines.append()
        
        for i, line_data in enumerate(obs['lines']):
            lines.append(f"Line {i}: {len(line_data['tracks'])} tracks")
            if line_data['train_pos']:
                lines.append(f"  Train at {line_data['train_pos']} with {len(line_data['train_passengers'])} passengers")
        
        if obs['passengers']:
            #lines.append()
            lines.append("Passengers waiting:")
            for pos, passenger_dict in obs['passengers'].items():
                total = sum(passenger_dict.values())
                if total > 0:
                    lines.append(f"  {pos}: {total} passengers")
        
        return "\n".join(lines)
    
    def get_valid_actions(self) -> list:
        valid_actions = [{'action': 'none'}]
        
        if len(self.engine.state.lines) < self.config.max_lines:
            for y in range(self.config.grid_size):
                for x in range(self.config.grid_size):
                    pos = Position(x, y)
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        adj_pos = Position(x + dx, y + dy)
                        if (0 <= adj_pos.x < self.config.grid_size and 
                            0 <= adj_pos.y < self.config.grid_size):
                            valid_actions.append({
                                'action': 'create_line',
                                'from': pos.to_tuple(),
                                'to': adj_pos.to_tuple()
                            })
        
        for line in self.engine.state.lines:
            valid_actions.append({
                'action': 'remove_line',
                'line_id': line.line_id
            })
            
            for endpoint in [line.tracks[0], line.tracks[-1]]:
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    adj_pos = Position(endpoint.x + dx, endpoint.y + dy)
                    if (0 <= adj_pos.x < self.config.grid_size and 
                        0 <= adj_pos.y < self.config.grid_size and
                        adj_pos not in line.tracks):
                        valid_actions.append({
                            'action': 'extend_line',
                            'line_id': line.line_id,
                            'to': adj_pos.to_tuple()
                        })
        
        return valid_actions