# MinimetroRL - Game Specification

## Overview
MinimetroRL is a simplified mini-metro game environment designed for reinforcement learning. Stations appear on a grid over time, and the agent must build train lines to transport passengers between stations before stations overflow.

## Core Mechanics

### Grid System
- **Size**: N × N tiles (default: 10×10)
- **Tile states**: Empty or Station
- **Station types**: Circle, Square, Triangle
- **Adjacency**: Horizontal and vertical only (no diagonals)

### Stations
- **Spawn rate**: New station appears every K timesteps (default: 50)
- **Spawn location**: Random empty tile
- **Passenger generation**: 1 passenger every M timesteps (default: 10)
- **Passenger destination**: Random station type (different from origin)
- **Capacity**: 10 passengers maximum (overflow causes game over)

### Lines and Trains
- **Maximum lines**: 3
- **Line composition**: Sequence of connected tracks between adjacent tiles
- **Train assignment**: Each line automatically gets 1 train
- **Train movement**: 1 tile per timestep, reverses at endpoints
- **Train capacity**: 6 passengers
- **Passenger handling**: Automatic pickup/dropoff based on destination types

### Actions
The agent can perform one action per timestep:

1. **Create Line**
   ```python
   {'action': 'create_line', 'from': (x1, y1), 'to': (x2, y2)}
   ```
   - Creates new line between two adjacent tiles
   - Only allowed if new line is available 

2. **Extend Line**
   ```python
   {'action': 'extend_line', 'line_id': 0, 'to': (x, y)}
   ```
   - Extends existing line by one track
   - Target tile must be adjacent to one of the line's endpoints

3. **Remove Line**
   ```python
   {'action': 'remove_line', 'line_id': 0}
   ```
   - Removes entire line and its train

4. **No Action**
   ```python
   {'action': 'none'}
   ```

### State Representation
```python
{
    'grid': [[tile_type, ...], ...],  # 'empty', 'circle', 'square', 'triangle'
    'passengers': {(x,y): {'circle': 2, 'square': 1, 'triangle': 0}, ...},
    'lines': [
        {
            'tracks': [(x1,y1), (x2,y2), ...],  # Ordered sequence of tiles
            'train_pos': (x, y),
            'train_passengers': ['circle', 'square', ...],
            'train_direction': 1  # 1 or -1
        },
        ...
    ],
    'timestep': int,
    'game_over': bool,
    'score': int
}
```

### Rewards
- **+10** for each passenger delivered to destination
- **-1** per timestep (time penalty)
- **-100** for game over (station overflow)

### Episode Termination
- Any station reaches 10 passengers (overflow)
- Maximum timesteps reached (default: 1000)

## Implementation Modes

### Agent Mode
- No visualization
- Synchronous step() function for RL training
- Returns: (observation, reward, done, info)
- Optimized for speed

### Pygame Mode
- Visual interface for human play and debugging
- Renders grid, stations, passengers, lines, and trains
- Supports both human input and agent control
- Frame rate: 30 FPS (configurable)
- Visual elements:
  - Stations: Colored shapes (circle, square, triangle)
  - Passengers: Small colored dots at stations
  - Lines: Colored paths between stations
  - Trains: Moving rectangles with passenger indicators

## Configuration Parameters
```python
{
    'grid_size': 10,
    'max_lines': 3,
    'station_spawn_rate': 50,  # timesteps
    'max_stations': 10,
    'passenger_spawn_rate': 10,  # timesteps
    'train_capacity': 6,
    'station_capacity': 10,
    'max_timesteps': 1000,
    'mode': 'agent' | 'pygame'
}
```

## Additional Rules
- Minimum line length: 2 tiles
- Trains pick up passengers automatically if:
  - Train has capacity
  - Passenger's destination type exists somewhere on the line
- Trains drop off passengers automatically at matching stations
- New trains spawn at the first tile of newly created lines
- Lines can cross and share tracks