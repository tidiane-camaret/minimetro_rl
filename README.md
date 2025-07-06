A mini-metro game environment for reinforcement learning

MinimetroRL is a mini-metro game environment designed for reinforcement learning tasks. It provides a simplified version of the mini-metro game, allowing a controler agent to learn and optimize a routing strategy.

The environment is a grid of N x N tiles, where each tile can be either empty or occupied by a station. Over time, new stations appear, and the agent must learn to place tracks to connect these stations efficiently. The agent receives a reward based on the number of passengers transported and the efficiency of the track layout.

One track can connect two stations, and the time it takes for a wagon to travel between two stations is proportionnal to the distance between them. 

The environment can be seen as a graph, where nodes are tiles with the following properties:
- station_type : A string representing the type of station (e.g., 'A', 'B', 'C') or 'empty' if the tile is not a station.
- Passengers : An dictionary representing the number of passengers waiting at the station, with keys as destination types and values as the number of passengers.

Edges in the graph represent relationships between two adjacent tiles, with the following properties:
- tracks : A list of tracks connecting the two tiles, empty if no track exists.
- wagons : A list of wagons currently traveling between the two tiles, and for each wagon, the number of passengers of each type it is carrying.

At each step, the agent can perform the following actions:
- Place a track between two adjacent tiles
- Extend an existing track to an adjacent tile
- Remove an entire track
- Add a wagon to a track
- Remove a wagon from a track

Parameters : 
- `grid_size` : The size of the grid (N)
- `max_stations` : The maximum number of stations that can appear in the environment
- 'action_every_n_steps' : the number of game steps after which the agent can perform an action
- `max_passengers` : The maximum number of passengers that can wait at a station

Game state :
- `grid` : A 2D array representing the grid, where each tile is a dictionary with properties like `station_type`, `passengers`, `tracks`, and `wagons`.
- `stations` : A list of all stations in the grid, each represented by a dictionary with properties like `type`, `passengers`, and `position`.
- `time_step` : The current time step in the game.
- `remaining_wagons` : The number of wagons available for the agent to use.
- `remaining_tracks` : The number of tracks available for the agent to use.