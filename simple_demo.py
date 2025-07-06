#!/usr/bin/env python3

import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
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
    
    def is_adjacent(self, other: 'Position') -> bool:
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)


@dataclass
class GameConfig:
    grid_size: int = 5
    max_lines: int = 3
    station_spawn_rate: int = 10
    passenger_spawn_rate: int = 5
    max_timesteps: int = 100


def main():
    print("=== MinimetroRL Simple Demo ===")
    
    config = GameConfig()
    
    # Initialize game state
    grid = [[TileType.EMPTY for _ in range(config.grid_size)] 
            for _ in range(config.grid_size)]
    stations = []
    lines = []
    timestep = 0
    score = 0
    
    print("Configuration:")
    print(f"  Grid size: {config.grid_size}x{config.grid_size}")
    print(f"  Max timesteps: {config.max_timesteps}")
    print(f"  Station spawn rate: {config.station_spawn_rate}")
    print(f"  Passenger spawn rate: {config.passenger_spawn_rate}")
    print()
    
    # Run simulation
    for step in range(20):
        print(f"Step {step + 1}:")
        print(f"Timestep: {timestep}, Score: {score}")
        print(f"Stations: {len(stations)}, Lines: {len(lines)}")
        
        # Spawn station
        if timestep % config.station_spawn_rate == 0:
            empty_positions = []
            for y in range(config.grid_size):
                for x in range(config.grid_size):
                    if grid[y][x] == TileType.EMPTY:
                        empty_positions.append(Position(x, y))
            
            if empty_positions:
                pos = random.choice(empty_positions)
                station_type = random.choice(list(StationType))
                stations.append({'pos': pos, 'type': station_type})
                grid[pos.y][pos.x] = TileType(station_type.value)
                print(f"  New station spawned at ({pos.x}, {pos.y}): {station_type.value}")
        
        # Simple agent action - try to create a line
        if len(lines) < config.max_lines and step % 3 == 0:
            for x in range(config.grid_size - 1):
                for y in range(config.grid_size):
                    from_pos = Position(x, y)
                    to_pos = Position(x + 1, y)
                    lines.append({'from': from_pos, 'to': to_pos})
                    print(f"  Created line from ({from_pos.x}, {from_pos.y}) to ({to_pos.x}, {to_pos.y})")
                    break
                break
        
        # Display grid
        print("  Grid:")
        for y in range(config.grid_size):
            row = "    "
            for x in range(config.grid_size):
                tile = grid[y][x]
                if tile == TileType.EMPTY:
                    row += "."
                elif tile == TileType.CIRCLE:
                    row += "O"
                elif tile == TileType.SQUARE:
                    row += "□"
                elif tile == TileType.TRIANGLE:
                    row += "△"
                row += " "
            print(row)
        
        score -= 1  # Time penalty
        timestep += 1
        print("-" * 50)
    
    print("\n=== Game Complete ===")
    print(f"Final score: {score}")
    print(f"Final timestep: {timestep}")
    print(f"Lines built: {len(lines)}")
    print(f"Stations spawned: {len(stations)}")


if __name__ == "__main__":
    main()