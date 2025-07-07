import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union

from .environment import MinimetroEnvironment
from .config import GameConfig, RewardConfig
from .types import Position, StationType


class MinimetroGymEnv(gym.Env):
    """
    Gymnasium environment wrapper for MinimetroRL game.
    
    This environment provides a standard gym interface for the MinimetroRL game,
    with discrete action space and multi-dimensional observation space.
    """
    
    metadata = {
        "render_modes": ["human", "rgb_array", "text"],
        "render_fps": 30,
    }
    
    def __init__(
        self,
        config: Optional[GameConfig] = None,
        reward_config: Optional[RewardConfig] = None,
        render_mode: Optional[str] = None,
    ):
        super().__init__()
        
        self.config = config or GameConfig()
        self.reward_config = reward_config or RewardConfig()
        self.render_mode = render_mode
        
        # Initialize the core environment
        self.env = MinimetroEnvironment(self.config, self.reward_config)
        
        # Define action space (discrete)
        self.action_space = self._create_action_space()
        
        # Define observation space
        self.observation_space = self._create_observation_space()
        
        # Initialize state
        self._state = None
        self._info = {}
        
        # Action mapping
        self._action_map = self._create_action_map()
        
    def _create_action_space(self) -> spaces.Discrete:
        """
        Create discrete action space.
        
        Actions are:
        0: none
        1-N: create_line actions (from each position to adjacent positions)
        N+1-M: extend_line actions (extend each line to adjacent positions)
        M+1-L: remove_line actions (remove each line)
        """
        # Calculate maximum possible actions
        grid_size = self.config.grid_size
        max_lines = self.config.max_lines
        
        # none action
        total_actions = 1
        
        # create_line actions: each position can connect to 4 adjacent positions
        # but we need to be more conservative to avoid overflow
        max_create_actions = grid_size * grid_size * 4
        total_actions += max_create_actions
        
        # extend_line actions: each line can be extended from either end to 4 directions
        max_extend_actions = max_lines * 2 * 4
        total_actions += max_extend_actions
        
        # remove_line actions: can remove each line
        max_remove_actions = max_lines
        total_actions += max_remove_actions
        
        return spaces.Discrete(total_actions)
        
    def _create_observation_space(self) -> spaces.Dict:
        """Create observation space matching the game's observation format."""
        grid_size = self.config.grid_size
        max_lines = self.config.max_lines
        
        return spaces.Dict({
            # Grid: 2D array of tile types (0=empty, 1=circle, 2=square, 3=triangle)
            "grid": spaces.Box(
                low=0, high=3, shape=(grid_size, grid_size), dtype=np.int32
            ),
            
            # Passenger counts at each position (3D: position x station_type)
            "passengers": spaces.Box(
                low=0, high=50, shape=(grid_size, grid_size, 3), dtype=np.int32
            ),
            
            # Line information (tracks, train position, train passengers)
            "lines": spaces.Box(
                low=0, high=grid_size*grid_size, shape=(max_lines, grid_size*grid_size + 2 + 3), dtype=np.int32
            ),
            
            # Game state
            "timestep": spaces.Box(low=0, high=self.config.max_timesteps, shape=(), dtype=np.int32),
            "score": spaces.Box(low=-float('inf'), high=float('inf'), shape=(), dtype=np.float32),
            "game_over": spaces.Box(low=0, high=1, shape=(), dtype=np.int32),
        })
        
    def _create_action_map(self) -> Dict[int, Dict[str, Any]]:
        """Create mapping from discrete action indices to action dictionaries."""
        action_map = {}
        action_idx = 0
        
        # none action
        action_map[action_idx] = {"action": "none"}
        action_idx += 1
        
        # create_line actions
        for y in range(self.config.grid_size):
            for x in range(self.config.grid_size):
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.config.grid_size and 0 <= ny < self.config.grid_size:
                        action_map[action_idx] = {
                            "action": "create_line",
                            "from": (x, y),
                            "to": (nx, ny)
                        }
                        action_idx += 1
        
        # extend_line actions (for each possible line)
        for line_id in range(self.config.max_lines):
            for is_end in [False, True]:  # start or end of line
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    action_map[action_idx] = {
                        "action": "extend_line",
                        "line_id": line_id,
                        "from_end": is_end,
                        "direction": (dx, dy)
                    }
                    action_idx += 1
        
        # remove_line actions
        for line_id in range(self.config.max_lines):
            action_map[action_idx] = {
                "action": "remove_line",
                "line_id": line_id
            }
            action_idx += 1
        
        return action_map
        
    def _convert_action(self, action: int) -> Dict[str, Any]:
        """Convert discrete action to action dictionary."""
        if action not in self._action_map:
            return {"action": "none"}
            
        action_dict = self._action_map[action].copy()
        
        # Handle extend_line actions that need position calculation
        if action_dict["action"] == "extend_line":
            line_id = action_dict["line_id"]
            
            # Check if line exists
            if line_id >= len(self.env.engine.state.lines):
                return {"action": "none"}
                
            line = self.env.engine.state.lines[line_id]
            from_end = action_dict["from_end"]
            dx, dy = action_dict["direction"]
            
            # Get position to extend from
            pos = line.tracks[-1] if from_end else line.tracks[0]
            to_pos = Position(pos.x + dx, pos.y + dy)
            
            # Check bounds
            if not (0 <= to_pos.x < self.config.grid_size and 0 <= to_pos.y < self.config.grid_size):
                return {"action": "none"}
                
            return {
                "action": "extend_line",
                "line_id": line_id,
                "to": to_pos.to_tuple()
            }
            
        return action_dict
        
    def _convert_observation(self, obs: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Convert environment observation to gym observation format."""
        grid_size = self.config.grid_size
        max_lines = self.config.max_lines
        
        # Convert grid to numeric format
        grid = np.zeros((grid_size, grid_size), dtype=np.int32)
        for y in range(grid_size):
            for x in range(grid_size):
                tile = obs["grid"][y][x]
                if tile == "circle":
                    grid[y, x] = 1
                elif tile == "square":
                    grid[y, x] = 2
                elif tile == "triangle":
                    grid[y, x] = 3
                else:
                    grid[y, x] = 0
                    
        # Convert passengers to 3D array
        passengers = np.zeros((grid_size, grid_size, 3), dtype=np.int32)
        for pos_tuple, passenger_dict in obs["passengers"].items():
            x, y = pos_tuple
            passengers[y, x, 0] = passenger_dict.get("circle", 0)
            passengers[y, x, 1] = passenger_dict.get("square", 0)
            passengers[y, x, 2] = passenger_dict.get("triangle", 0)
            
        # Convert lines to fixed-size arrays
        lines = np.zeros((max_lines, grid_size*grid_size + 2 + 3), dtype=np.int32)
        for i, line_data in enumerate(obs["lines"][:max_lines]):
            # Encode tracks as flattened positions
            for j, track in enumerate(line_data["tracks"][:grid_size*grid_size]):
                if isinstance(track, tuple):
                    x, y = track
                else:
                    x, y = track.x, track.y
                lines[i, j] = y * grid_size + x
                
            # Encode train position
            if line_data["train_pos"]:
                if isinstance(line_data["train_pos"], tuple):
                    tx, ty = line_data["train_pos"]
                else:
                    tx, ty = line_data["train_pos"].x, line_data["train_pos"].y
                lines[i, grid_size*grid_size] = ty * grid_size + tx
                
            # Encode train passengers
            train_passengers = line_data["train_passengers"]
            lines[i, grid_size*grid_size + 1] = len(train_passengers)
            
            # Count passengers by type
            passenger_counts = [0, 0, 0]
            for passenger in train_passengers:
                if hasattr(passenger, 'destination_type'):
                    if passenger.destination_type == StationType.CIRCLE:
                        passenger_counts[0] += 1
                    elif passenger.destination_type == StationType.SQUARE:
                        passenger_counts[1] += 1
                    elif passenger.destination_type == StationType.TRIANGLE:
                        passenger_counts[2] += 1
            
            lines[i, grid_size*grid_size + 2:grid_size*grid_size + 5] = passenger_counts
            
        return {
            "grid": grid,
            "passengers": passengers,
            "lines": lines,
            "timestep": np.array(obs["timestep"], dtype=np.int32),
            "score": np.array(obs["score"], dtype=np.float32),
            "game_over": np.array(1 if obs["game_over"] else 0, dtype=np.int32),
        }
        
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """Reset the environment."""
        super().reset(seed=seed)
        
        if seed is not None:
            np.random.seed(seed)
            
        obs = self.env.reset()
        self._state = obs
        self._info = {}
        
        return self._convert_observation(obs), self._info
        
    def step(
        self, action: int
    ) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict[str, Any]]:
        """Execute one step in the environment."""
        # Convert discrete action to action dictionary
        action_dict = self._convert_action(action)
        
        # Execute action
        obs, reward, terminated, info = self.env.step(action_dict)
        
        self._state = obs
        self._info = info
        
        # Convert observation
        gym_obs = self._convert_observation(obs)
        
        # Gymnasium API requires terminated and truncated separately
        truncated = False  # This game doesn't truncate, only terminates
        
        return gym_obs, reward, terminated, truncated, info
        
    def render(self) -> Optional[Union[np.ndarray, str]]:
        """Render the environment."""
        if self.render_mode == "text":
            return self.env.render()
        elif self.render_mode == "human":
            # For human rendering, we'll use the pygame renderer if available
            if hasattr(self.env, 'renderer') and self.env.renderer:
                self.env.renderer.render(self.env.engine.state)
                return None
            else:
                # Fall back to text rendering
                print(self.env.render())
                return None
        elif self.render_mode == "rgb_array":
            # For rgb_array mode, we would need to capture the pygame surface
            # This is a placeholder - full implementation would require pygame surface capture
            return None
        
        return None
        
    def close(self) -> None:
        """Close the environment."""
        if hasattr(self.env, 'renderer') and self.env.renderer:
            self.env.renderer.close()