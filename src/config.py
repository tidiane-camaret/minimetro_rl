from dataclasses import dataclass
from typing import Literal


@dataclass
class GameConfig:
    grid_size: int = 20
    max_lines: int = 3
    station_spawn_rate: int = 100
    max_stations: int = 10
    passenger_spawn_rate: int = 50
    train_capacity: int = 6
    station_capacity: int = 10
    max_timesteps: int = 10000
    mode: Literal['agent', 'pygame'] = 'agent'
    fps: int = 30
    
    def __post_init__(self):
        if self.grid_size < 3:
            raise ValueError("Grid size must be at least 3")
        if self.max_lines < 1:
            raise ValueError("Must allow at least 1 line")
        if self.station_spawn_rate < 1:
            raise ValueError("Station spawn rate must be positive")
        if self.passenger_spawn_rate < 1:
            raise ValueError("Passenger spawn rate must be positive")


@dataclass
class RewardConfig:
    passenger_delivered: int = 10
    time_penalty: int = -1
    game_over_penalty: int = -100


STATION_TYPES = ['circle', 'square', 'triangle']
EMPTY_TILE = 'empty'