#!/usr/bin/env python3

import pygame
import random
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, List
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


@dataclass
class GameConfig:
    grid_size: int = 8
    max_lines: int = 3
    station_spawn_rate: int = 30
    passenger_spawn_rate: int = 15
    max_timesteps: int = 500
    fps: int = 10


class PygameRenderer:
    def __init__(self, config: GameConfig):
        self.config = config
        self.cell_size = 80
        self.window_width = self.config.grid_size * self.cell_size
        self.window_height = self.config.grid_size * self.cell_size + 150
        
        self.colors = {
            'background': (240, 240, 240),
            'grid_line': (200, 200, 200),
            'empty': (255, 255, 255),
            'circle': (255, 100, 100),
            'square': (100, 100, 255),
            'triangle': (100, 255, 100),
            'line': (80, 80, 80),
            'train': (50, 50, 50),
            'passenger': (20, 20, 20),
            'text': (0, 0, 0)
        }
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("MinimetroRL - Pygame Demo")
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        self.clock = pygame.time.Clock()
    
    def render(self, observation: Dict[str, Any]) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        self.screen.fill(self.colors['background'])
        
        self._draw_grid()
        self._draw_stations(observation)
        self._draw_lines(observation)
        self._draw_trains(observation)
        self._draw_passengers(observation)
        self._draw_info(observation)
        
        pygame.display.flip()
        self.clock.tick(self.config.fps)
        return True
    
    def _draw_grid(self):
        # Draw grid lines
        for x in range(self.config.grid_size + 1):
            pygame.draw.line(self.screen, self.colors['grid_line'],
                           (x * self.cell_size, 0),
                           (x * self.cell_size, self.config.grid_size * self.cell_size))
        
        for y in range(self.config.grid_size + 1):
            pygame.draw.line(self.screen, self.colors['grid_line'],
                           (0, y * self.cell_size),
                           (self.config.grid_size * self.cell_size, y * self.cell_size))
        
        # Fill cells with background
        for x in range(self.config.grid_size):
            for y in range(self.config.grid_size):
                cell_rect = pygame.Rect(x * self.cell_size + 1, y * self.cell_size + 1,
                                      self.cell_size - 2, self.cell_size - 2)
                pygame.draw.rect(self.screen, self.colors['empty'], cell_rect)
    
    def _draw_stations(self, observation: Dict[str, Any]):
        grid = observation['grid']
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] != 'empty':
                    self._draw_station(x, y, grid[y][x])
    
    def _draw_station(self, x: int, y: int, station_type: str):
        center_x = x * self.cell_size + self.cell_size // 2
        center_y = y * self.cell_size + self.cell_size // 2
        size = self.cell_size // 3
        
        color = self.colors.get(station_type, self.colors['empty'])
        
        if station_type == 'circle':
            pygame.draw.circle(self.screen, color, (center_x, center_y), size)
            pygame.draw.circle(self.screen, (0, 0, 0), (center_x, center_y), size, 3)
        elif station_type == 'square':
            rect = pygame.Rect(center_x - size, center_y - size, size * 2, size * 2)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 3)
        elif station_type == 'triangle':
            points = [
                (center_x, center_y - size),
                (center_x - size, center_y + size),
                (center_x + size, center_y + size)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (0, 0, 0), points, 3)
    
    def _draw_lines(self, observation: Dict[str, Any]):
        for i, line_data in enumerate(observation['lines']):
            tracks = line_data['tracks']
            if len(tracks) < 2:
                continue
            
            color = self._get_line_color(i)
            
            for j in range(len(tracks) - 1):
                start_pos = self._grid_to_screen(tracks[j])
                end_pos = self._grid_to_screen(tracks[j + 1])
                pygame.draw.line(self.screen, color, start_pos, end_pos, 6)
    
    def _draw_trains(self, observation: Dict[str, Any]):
        for line_data in observation['lines']:
            if line_data['train_pos']:
                train_pos = self._grid_to_screen(line_data['train_pos'])
                train_rect = pygame.Rect(train_pos[0] - 12, train_pos[1] - 12, 24, 24)
                pygame.draw.rect(self.screen, self.colors['train'], train_rect)
                pygame.draw.rect(self.screen, (255, 255, 255), train_rect, 2)
                
                passenger_count = len(line_data['train_passengers'])
                if passenger_count > 0:
                    text = self.small_font.render(str(passenger_count), True, (255, 255, 255))
                    text_rect = text.get_rect(center=train_pos)
                    self.screen.blit(text, text_rect)
    
    def _draw_passengers(self, observation: Dict[str, Any]):
        passengers = observation['passengers']
        for pos_tuple, passenger_dict in passengers.items():
            x, y = pos_tuple
            center_x = x * self.cell_size + self.cell_size // 2
            center_y = y * self.cell_size + self.cell_size // 2
            
            total_passengers = sum(passenger_dict.values())
            if total_passengers > 0:
                # Draw passenger count
                text = self.small_font.render(str(total_passengers), True, self.colors['text'])
                text_rect = text.get_rect(center=(center_x, center_y + 32))
                
                # Draw background circle for better visibility
                pygame.draw.circle(self.screen, (255, 255, 255), text_rect.center, 12)
                pygame.draw.circle(self.screen, (0, 0, 0), text_rect.center, 12, 2)
                
                self.screen.blit(text, text_rect)
                
                # Draw small colored dots for passenger types
                offset = 0
                for passenger_type, count in passenger_dict.items():
                    if count > 0:
                        color = self.colors.get(passenger_type, self.colors['passenger'])
                        dot_pos = (center_x - 15 + offset * 8, center_y + 15)
                        pygame.draw.circle(self.screen, color, dot_pos, 3)
                        offset += 1
    
    def _draw_info(self, observation: Dict[str, Any]):
        info_y = self.config.grid_size * self.cell_size + 10
        
        # Main info
        timestep_text = f"Timestep: {observation['timestep']}"
        score_text = f"Score: {observation['score']}"
        game_over_text = f"Game Over: {observation['game_over']}"
        
        timestep_surface = self.font.render(timestep_text, True, self.colors['text'])
        score_surface = self.font.render(score_text, True, self.colors['text'])
        game_over_surface = self.font.render(game_over_text, True, self.colors['text'])
        
        self.screen.blit(timestep_surface, (10, info_y))
        self.screen.blit(score_surface, (10, info_y + 30))
        self.screen.blit(game_over_surface, (10, info_y + 60))
        
        # Line info
        lines_text = f"Lines: {len(observation['lines'])}/{self.config.max_lines}"
        lines_surface = self.font.render(lines_text, True, self.colors['text'])
        self.screen.blit(lines_surface, (200, info_y))
        
        # Passenger info
        total_waiting = 0
        if observation['passengers']:
            total_waiting = sum(sum(p.values()) for p in observation['passengers'].values())
        
        passengers_text = f"Waiting: {total_waiting}"
        passengers_surface = self.font.render(passengers_text, True, self.colors['text'])
        self.screen.blit(passengers_surface, (200, info_y + 30))
        
        # Instructions
        instructions = "Press ESC to quit"
        instructions_surface = self.small_font.render(instructions, True, self.colors['text'])
        self.screen.blit(instructions_surface, (10, info_y + 90))
    
    def _grid_to_screen(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        x, y = pos
        return (x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2)
    
    def _get_line_color(self, line_id: int) -> Tuple[int, int, int]:
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        return colors[line_id % len(colors)]
    
    def close(self):
        pygame.quit()


def main():
    print("=== MinimetroRL Pygame Demo ===")
    print("Watch the game simulation with visual rendering")
    print("Press ESC to quit at any time")
    print()
    
    config = GameConfig()
    renderer = PygameRenderer(config)
    
    # Initialize game state
    grid = [[TileType.EMPTY for _ in range(config.grid_size)] 
            for _ in range(config.grid_size)]
    stations = []
    lines = []
    timestep = 0
    score = 0
    game_over = False
    
    try:
        running = True
        while running and not game_over and timestep < config.max_timesteps:
            # Create observation
            grid_obs = [[tile.value for tile in row] for row in grid]
            
            passengers_obs = {}
            for station in stations:
                pos_tuple = (station['pos'].x, station['pos'].y)
                passengers_obs[pos_tuple] = station.get('passengers', {
                    'circle': random.randint(0, 3),
                    'square': random.randint(0, 3),
                    'triangle': random.randint(0, 3)
                })
            
            lines_obs = []
            for line in lines:
                line_obs = {
                    'tracks': [(pos.x, pos.y) for pos in line['tracks']],
                    'train_pos': (line['train_pos'].x, line['train_pos'].y) if line.get('train_pos') else None,
                    'train_passengers': line.get('train_passengers', []),
                    'train_direction': line.get('train_direction', 1)
                }
                lines_obs.append(line_obs)
            
            observation = {
                'grid': grid_obs,
                'passengers': passengers_obs,
                'lines': lines_obs,
                'timestep': timestep,
                'game_over': game_over,
                'score': score
            }
            
            # Render
            running = renderer.render(observation)
            
            # Game logic
            # Spawn stations
            if timestep % config.station_spawn_rate == 0 and len(stations) < 10:
                empty_positions = []
                for y in range(config.grid_size):
                    for x in range(config.grid_size):
                        if grid[y][x] == TileType.EMPTY:
                            empty_positions.append(Position(x, y))
                
                if empty_positions:
                    pos = random.choice(empty_positions)
                    station_type = random.choice(list(StationType))
                    station = {
                        'pos': pos,
                        'type': station_type,
                        'passengers': {
                            'circle': random.randint(0, 2),
                            'square': random.randint(0, 2),
                            'triangle': random.randint(0, 2)
                        }
                    }
                    stations.append(station)
                    grid[pos.y][pos.x] = TileType(station_type.value)
            
            # Simple AI: Create lines occasionally
            if len(lines) < config.max_lines and timestep % 40 == 0 and len(stations) >= 2:
                # Try to connect two stations
                if len(stations) >= 2:
                    station1 = random.choice(stations)
                    station2 = random.choice([s for s in stations if s != station1])
                    
                    # Create a simple line (just two points for demo)
                    line = {
                        'tracks': [station1['pos'], station2['pos']],
                        'train_pos': station1['pos'],
                        'train_passengers': [],
                        'train_direction': 1
                    }
                    lines.append(line)
            
            # Move trains
            for line in lines:
                if line.get('train_pos') and len(line['tracks']) > 1:
                    current_track = line['tracks'][0] if random.random() < 0.5 else line['tracks'][1]
                    line['train_pos'] = current_track
                    line['train_passengers'] = [random.choice(['circle', 'square', 'triangle']) 
                                              for _ in range(random.randint(0, 3))]
            
            # Update passengers
            for station in stations:
                if timestep % config.passenger_spawn_rate == 0:
                    passenger_type = random.choice(['circle', 'square', 'triangle'])
                    if passenger_type in station['passengers']:
                        station['passengers'][passenger_type] = min(
                            station['passengers'][passenger_type] + 1, 5
                        )
            
            score -= 1  # Time penalty
            timestep += 1
            
            # Check for game over (station overflow)
            for station in stations:
                total_passengers = sum(station['passengers'].values())
                if total_passengers >= 10:
                    game_over = True
                    score -= 100
                    break
    
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    
    finally:
        renderer.close()
    
    print(f"\nDemo completed!")
    print(f"Final score: {score}")
    print(f"Final timestep: {timestep}")
    print(f"Stations spawned: {len(stations)}")
    print(f"Lines built: {len(lines)}")


if __name__ == "__main__":
    main()