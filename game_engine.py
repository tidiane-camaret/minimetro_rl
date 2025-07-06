import random
from typing import List, Optional, Tuple, Dict, Any
from .types import (
    GameState, Station, Line, Train, Action, Position, 
    StationType, TileType
)
from .config import GameConfig, RewardConfig, STATION_TYPES, EMPTY_TILE


class GameEngine:
    def __init__(self, config: GameConfig, reward_config: RewardConfig = None):
        self.config = config
        self.reward_config = reward_config or RewardConfig()
        self.state = self._initialize_game_state()
        self.random = random.Random()
        self._next_line_id = 0
    
    def _initialize_game_state(self) -> GameState:
        grid = [[TileType.EMPTY for _ in range(self.config.grid_size)] 
                for _ in range(self.config.grid_size)]
        
        return GameState(
            grid=grid,
            stations=[],
            lines=[],
            timestep=0,
            game_over=False,
            score=0
        )
    
    def reset(self) -> GameState:
        self.state = self._initialize_game_state()
        self._next_line_id = 0
        return self.state
    
    def step(self, action: Action) -> Tuple[GameState, int, bool, Dict[str, Any]]:
        if self.state.game_over:
            return self.state, 0, True, {}
        
        reward = self.reward_config.time_penalty
        info = {}
        
        if action.action_type != 'none':
            action_result = self._execute_action(action)
            info['action_result'] = action_result
        
        self._update_trains()
        delivered_passengers = self._handle_passenger_pickup_dropoff()
        reward += delivered_passengers * self.reward_config.passenger_delivered
        
        self._spawn_stations()
        self._generate_passengers()
        
        self.state.timestep += 1
        self.state.score += reward
        
        if self._check_game_over():
            self.state.game_over = True
            reward += self.reward_config.game_over_penalty
        
        info['delivered_passengers'] = delivered_passengers
        
        return self.state, reward, self.state.game_over, info
    
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        result = {'success': False, 'error': None}
        
        try:
            if action.action_type == 'create_line':
                result = self._create_line(action.from_pos, action.to_pos)
            elif action.action_type == 'extend_line':
                result = self._extend_line(action.line_id, action.to_pos)
            elif action.action_type == 'remove_line':
                result = self._remove_line(action.line_id)
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _create_line(self, from_pos: Position, to_pos: Position) -> Dict[str, Any]:
        if len(self.state.lines) >= self.config.max_lines:
            return {'success': False, 'error': 'Maximum lines reached'}
        
        if not self._is_valid_position(from_pos) or not self._is_valid_position(to_pos):
            return {'success': False, 'error': 'Invalid position'}
        
        if not from_pos.is_adjacent(to_pos):
            return {'success': False, 'error': 'Positions must be adjacent'}
        
        line = Line(line_id=self._next_line_id, tracks=[from_pos, to_pos])
        
        self.state.lines.append(line)
        self._next_line_id += 1
        
        return {'success': True, 'line_id': line.line_id}
    
    def _extend_line(self, line_id: int, to_pos: Position) -> Dict[str, Any]:
        line = self.state.get_line_by_id(line_id)
        if not line:
            return {'success': False, 'error': 'Line not found'}
        
        if not self._is_valid_position(to_pos):
            return {'success': False, 'error': 'Invalid position'}
        
        if not line.add_track(to_pos):
            return {'success': False, 'error': 'Cannot extend line to that position'}
        
        return {'success': True}
    
    def _remove_line(self, line_id: int) -> Dict[str, Any]:
        line = self.state.get_line_by_id(line_id)
        if not line:
            return {'success': False, 'error': 'Line not found'}
        
        self.state.lines.remove(line)
        return {'success': True}
    
    def _update_trains(self):
        for line in self.state.lines:
            if not line.train or not line.tracks:
                continue
            
            self._move_train(line)
    
    def _move_train(self, line: Line):
        train = line.train
        current_idx = None
        
        for i, pos in enumerate(line.tracks):
            if pos == train.position:
                current_idx = i
                break
        
        if current_idx is None:
            train.position = line.tracks[0]
            return
        
        next_idx = current_idx + train.direction
        
        if next_idx < 0:
            train.direction = 1
            next_idx = 1
        elif next_idx >= len(line.tracks):
            train.direction = -1
            next_idx = len(line.tracks) - 2
        
        if 0 <= next_idx < len(line.tracks):
            train.position = line.tracks[next_idx]
    
    def _handle_passenger_pickup_dropoff(self) -> int:
        delivered_count = 0
        
        for line in self.state.lines:
            if not line.train:
                continue
            
            train = line.train
            station = self.state.get_station_at(train.position)
            
            if station:
                delivered_count += self._dropoff_passengers(train, station)
                self._pickup_passengers(train, station, line)
        
        return delivered_count
    
    def _dropoff_passengers(self, train: Train, station: Station) -> int:
        delivered = train.remove_passengers(station.station_type)
        return delivered
    
    def _pickup_passengers(self, train: Train, station: Station, line: Line):
        station_types_on_line = line.get_station_types_on_line(self.state.grid)
        
        for destination_type in station_types_on_line:
            if destination_type == station.station_type:
                continue
            
            while (train.has_capacity() and 
                   station.passengers[destination_type] > 0):
                station.remove_passengers(destination_type, 1)
                train.add_passenger(destination_type)
    
    def _spawn_stations(self):
        if (self.state.timestep % self.config.station_spawn_rate == 0 and 
            len(self.state.stations) < self.config.max_stations):
            
            empty_positions = self._get_empty_positions()
            if empty_positions:
                pos = self.random.choice(empty_positions)
                station_type = StationType(self.random.choice(STATION_TYPES))
                
                station = Station(position=pos, station_type=station_type)
                self.state.stations.append(station)
                self.state.grid[pos.y][pos.x] = TileType(station_type.value)
    
    def _generate_passengers(self):
        if self.state.timestep % self.config.passenger_spawn_rate == 0:
            for station in self.state.stations:
                if station.total_passengers() < self.config.station_capacity:
                    available_destinations = [st for st in StationType 
                                            if st != station.station_type]
                    if available_destinations:
                        destination = self.random.choice(available_destinations)
                        station.add_passenger(destination)
    
    def _get_empty_positions(self) -> List[Position]:
        empty_positions = []
        for y in range(self.config.grid_size):
            for x in range(self.config.grid_size):
                if self.state.grid[y][x] == TileType.EMPTY:
                    empty_positions.append(Position(x, y))
        return empty_positions
    
    def _is_valid_position(self, pos: Position) -> bool:
        return (0 <= pos.x < self.config.grid_size and 
                0 <= pos.y < self.config.grid_size)
    
    def _check_game_over(self) -> bool:
        if self.state.timestep >= self.config.max_timesteps:
            return True
        
        for station in self.state.stations:
            if station.total_passengers() >= self.config.station_capacity:
                return True
        
        return False
    
    def get_observation(self) -> Dict[str, Any]:
        grid_obs = [[tile.value for tile in row] for row in self.state.grid]
        
        passengers_obs = {}
        for station in self.state.stations:
            pos_tuple = station.position.to_tuple()
            passengers_obs[pos_tuple] = {
                st.value: station.passengers[st] for st in StationType
            }
        
        lines_obs = []
        for line in self.state.lines:
            line_obs = {
                'tracks': [pos.to_tuple() for pos in line.tracks],
                'train_pos': line.train.position.to_tuple() if line.train else None,
                'train_passengers': [p.value for p in line.train.passengers] if line.train else [],
                'train_direction': line.train.direction if line.train else 1
            }
            lines_obs.append(line_obs)
        
        return {
            'grid': grid_obs,
            'passengers': passengers_obs,
            'lines': lines_obs,
            'timestep': self.state.timestep,
            'game_over': self.state.game_over,
            'score': self.state.score
        }