# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MinimetroRL is a simplified mini-metro game environment designed for reinforcement learning. The project simulates a grid-based transport system where an agent must build train lines to transport passengers between stations before stations overflow.

## Development Commands

### Running the Application
```bash
# Run simple demo
python simple_demo.py

# Run comprehensive tests
python -m pytest test_game.py -v

# Note: The main.py requires package installation due to relative imports
# For development, use simple_demo.py or the test suite
```

### Package Management
```bash
# Install dependencies
pip install pygame>=2.0.0

# For development tools
pip install pytest>=6.0.0 black>=22.0.0 flake8>=4.0.0 mypy>=0.910
```

## Architecture

### Core Game Mechanics
- **Grid System**: N×N tiles (default 10×10) with stations appearing randomly
- **Station Types**: Circle, Square, Triangle with different passenger generation
- **Lines and Trains**: Maximum 3 lines, each with 1 train (6 passenger capacity)
- **Game Modes**: "agent" mode (no visualization) and "pygame" mode (visual interface)

### Key Components
- **State Management**: Grid-based representation with tiles, stations, passengers, lines, and trains
- **Action Space**: create_line, extend_line, remove_line, none
- **Reward System**: +10 per delivered passenger, -1 per timestep, -100 for game over
- **Termination**: Station overflow (10 passengers) or max timesteps (1000)

### Implementation Structure
The project is currently minimal with:
- `main.py`: Entry point with basic "Hello World" functionality
- `pyproject.toml`: Python package configuration
- `README.md` & `specs.md`: Comprehensive game documentation

### Configuration Parameters
Default settings include:
- Grid size: 10×10
- Max lines: 3
- Station spawn rate: 50 timesteps
- Passenger spawn rate: 10 timesteps
- Train capacity: 6 passengers
- Station capacity: 10 passengers

## Development Notes

The project is in early development stage with core game mechanics documented but implementation pending. The architecture supports both RL training (agent mode) and human interaction (pygame mode).

When implementing the game environment, focus on:
1. Core grid and station management
2. Line and train logic with automatic passenger handling
3. State representation for RL agents
4. Pygame visualization for debugging and human play