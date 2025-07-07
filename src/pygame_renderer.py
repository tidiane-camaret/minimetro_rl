import pygame
from typing import Dict, Any, Tuple, Optional
#from minimetro_rl.types import StationType, TileType
from src.config import GameConfig


class PygameRenderer:
    def __init__(self, config: GameConfig):
        self.config = config
        self.cell_size = 60
        self.window_width = self.config.grid_size * self.cell_size
        self.window_height = self.config.grid_size * self.cell_size + 100
        
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
        pygame.display.set_caption("MinimetroRL")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
    
    def render(self, observation: Dict[str, Any]) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
        for x in range(self.config.grid_size + 1):
            pygame.draw.line(self.screen, self.colors['grid_line'],
                           (x * self.cell_size, 0),
                           (x * self.cell_size, self.config.grid_size * self.cell_size))
        
        for y in range(self.config.grid_size + 1):
            pygame.draw.line(self.screen, self.colors['grid_line'],
                           (0, y * self.cell_size),
                           (self.config.grid_size * self.cell_size, y * self.cell_size))
    
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
        
        color = self.colors[station_type]
        
        if station_type == 'circle':
            pygame.draw.circle(self.screen, color, (center_x, center_y), size)
        elif station_type == 'square':
            rect = pygame.Rect(center_x - size, center_y - size, size * 2, size * 2)
            pygame.draw.rect(self.screen, color, rect)
        elif station_type == 'triangle':
            points = [
                (center_x, center_y - size),
                (center_x - size, center_y + size),
                (center_x + size, center_y + size)
            ]
            pygame.draw.polygon(self.screen, color, points)
    
    def _draw_lines(self, observation: Dict[str, Any]):
        for i, line_data in enumerate(observation['lines']):
            tracks = line_data['tracks']
            if len(tracks) < 2:
                continue
            
            color = self._get_line_color(i)
            
            for j in range(len(tracks) - 1):
                start_pos = self._grid_to_screen(tracks[j])
                end_pos = self._grid_to_screen(tracks[j + 1])
                pygame.draw.line(self.screen, color, start_pos, end_pos, 4)
    
    def _draw_trains(self, observation: Dict[str, Any]):
        for line_data in observation['lines']:
            if line_data['train_pos']:
                train_pos = self._grid_to_screen(line_data['train_pos'])
                train_rect = pygame.Rect(train_pos[0] - 8, train_pos[1] - 8, 16, 16)
                pygame.draw.rect(self.screen, self.colors['train'], train_rect)
                
                passenger_count = len(line_data['train_passengers'])
                if passenger_count > 0:
                    text = self.font.render(str(passenger_count), True, (255, 255, 255))
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
                text = self.font.render(str(total_passengers), True, self.colors['text'])
                text_rect = text.get_rect(center=(center_x, center_y + 25))
                self.screen.blit(text, text_rect)
    
    def _draw_info(self, observation: Dict[str, Any]):
        info_y = self.config.grid_size * self.cell_size + 10
        
        timestep_text = f"Timestep: {observation['timestep']}"
        score_text = f"Score: {observation['score']}"
        game_over_text = f"Game Over: {observation['game_over']}"
        
        timestep_surface = self.font.render(timestep_text, True, self.colors['text'])
        score_surface = self.font.render(score_text, True, self.colors['text'])
        game_over_surface = self.font.render(game_over_text, True, self.colors['text'])
        
        self.screen.blit(timestep_surface, (10, info_y))
        self.screen.blit(score_surface, (10, info_y + 25))
        self.screen.blit(game_over_surface, (10, info_y + 50))
    
    def _grid_to_screen(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        x, y = pos
        return (x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2)
    
    def _get_line_color(self, line_id: int) -> Tuple[int, int, int]:
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        return colors[line_id % len(colors)]
    
    def close(self):
        pygame.quit()