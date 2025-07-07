from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Literal
from enum import Enum


class StationType(Enum):
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'


class TileType(Enum):
    EMPTY = 'empty'
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'


@dataclass
class Position:
    x: int
    y: int
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, (tuple, list)) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return False
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def is_adjacent(self, other: 'Position') -> bool:
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)


@dataclass
class Station:
    position: Position
    station_type: StationType
    passengers: Dict[StationType, int] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.passengers:
            self.passengers = {st: 0 for st in StationType}
    
    def total_passengers(self) -> int:
        return sum(self.passengers.values())
    
    def add_passenger(self, destination: StationType) -> bool:
        if destination == self.station_type:
            return False
        if self.total_passengers() >= 10:
            return False
        self.passengers[destination] += 1
        return True
    
    def remove_passengers(self, destination: StationType, count: int) -> int:
        available = self.passengers[destination]
        removed = min(available, count)
        self.passengers[destination] -= removed
        return removed


@dataclass
class Train:
    position: Position
    passengers: List[StationType] = field(default_factory=list)
    direction: int = 1
    
    def has_capacity(self) -> bool:
        return len(self.passengers) < 6
    
    def add_passenger(self, passenger_type: StationType) -> bool:
        if not self.has_capacity():
            return False
        self.passengers.append(passenger_type)
        return True
    
    def remove_passengers(self, destination: StationType) -> int:
        passengers_to_remove = [p for p in self.passengers if p == destination]
        for p in passengers_to_remove:
            self.passengers.remove(p)
        return len(passengers_to_remove)


@dataclass
class Line:
    line_id: int
    tracks: List[Position] = field(default_factory=list)
    train: Optional[Train] = None
    
    def __post_init__(self):
        if self.tracks and not self.train:
            self.train = Train(position=self.tracks[0])
    
    def add_track(self, position: Position) -> bool:
        if not self.tracks:
            self.tracks.append(position)
            self.train = Train(position=position)
            return True
        
        if position in self.tracks:
            return False
        
        if self.tracks[0].is_adjacent(position):
            self.tracks.insert(0, position)
            return True
        elif self.tracks[-1].is_adjacent(position):
            self.tracks.append(position)
            return True
        
        return False
    
    def get_station_types_on_line(self, grid: List[List[TileType]]) -> set:
        station_types = set()
        for pos in self.tracks:
            tile_type = grid[pos.y][pos.x]
            if tile_type != TileType.EMPTY:
                station_types.add(StationType(tile_type.value))
        return station_types
    
    def is_valid(self) -> bool:
        return len(self.tracks) >= 2


@dataclass
class Action:
    action_type: Literal['create_line', 'extend_line', 'remove_line', 'none']
    from_pos: Optional[Position] = None
    to_pos: Optional[Position] = None
    line_id: Optional[int] = None


@dataclass
class GameState:
    grid: List[List[TileType]]
    stations: List[Station]
    lines: List[Line]
    timestep: int = 0
    game_over: bool = False
    score: int = 0
    
    def get_station_at(self, position: Position) -> Optional[Station]:
        for station in self.stations:
            if station.position == position:
                return station
        return None
    
    def get_line_by_id(self, line_id: int) -> Optional[Line]:
        for line in self.lines:
            if line.line_id == line_id:
                return line
        return None