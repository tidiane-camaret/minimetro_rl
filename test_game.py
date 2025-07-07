import unittest
from src.config import GameConfig, RewardConfig
from src.environment import MinimetroEnvironment
from src.game import MinimetroGame, SimpleAgent
from src.types import Position, StationType, TileType, Action


class TestMinimetroEnvironment(unittest.TestCase):
    def setUp(self):
        self.config = GameConfig(grid_size=5, max_timesteps=100)
        self.env = MinimetroEnvironment(self.config)
    
    def test_reset(self):
        obs = self.env.reset()
        self.assertEqual(len(obs['grid']), 5)
        self.assertEqual(len(obs['grid'][0]), 5)
        self.assertEqual(obs['timestep'], 0)
        self.assertEqual(obs['score'], 0)
        self.assertFalse(obs['game_over'])
    
    def test_create_line_action(self):
        self.env.reset()
        action = {'action': 'create_line', 'from': (0, 0), 'to': (1, 0)}
        obs, reward, done, info = self.env.step(action)
        
        self.assertEqual(len(obs['lines']), 1)
        self.assertEqual(obs['lines'][0]['tracks'], [(0, 0), (1, 0)])
    
    def test_invalid_action(self):
        self.env.reset()
        action = {'action': 'create_line', 'from': (0, 0), 'to': (2, 0)}
        obs, reward, done, info = self.env.step(action)
        
        self.assertEqual(len(obs['lines']), 0)
        self.assertFalse(info['action_result']['success'])
    
    def test_extend_line_action(self):
        self.env.reset()
        
        create_action = {'action': 'create_line', 'from': (0, 0), 'to': (1, 0)}
        self.env.step(create_action)
        
        extend_action = {'action': 'extend_line', 'line_id': 0, 'to': (2, 0)}
        obs, reward, done, info = self.env.step(extend_action)
        
        self.assertEqual(len(obs['lines'][0]['tracks']), 3)
        self.assertEqual(obs['lines'][0]['tracks'], [(0, 0), (1, 0), (2, 0)])
    
    def test_remove_line_action(self):
        self.env.reset()
        
        create_action = {'action': 'create_line', 'from': (0, 0), 'to': (1, 0)}
        self.env.step(create_action)
        
        remove_action = {'action': 'remove_line', 'line_id': 0}
        obs, reward, done, info = self.env.step(remove_action)
        
        self.assertEqual(len(obs['lines']), 0)
    
    def test_max_lines_limit(self):
        self.env.reset()
        
        for i in range(4):
            action = {'action': 'create_line', 'from': (i, 0), 'to': (i, 1)}
            obs, reward, done, info = self.env.step(action)
            
            if i < 3:
                self.assertTrue(info['action_result']['success'])
            else:
                self.assertFalse(info['action_result']['success'])
        
        self.assertEqual(len(obs['lines']), 3)


class TestGameTypes(unittest.TestCase):
    def test_position_adjacency(self):
        pos1 = Position(0, 0)
        pos2 = Position(1, 0)
        pos3 = Position(2, 0)
        
        self.assertTrue(pos1.is_adjacent(pos2))
        self.assertFalse(pos1.is_adjacent(pos3))
    
    def test_position_equality(self):
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = (1, 2)
        
        self.assertEqual(pos1, pos2)
        self.assertEqual(pos1, pos3)
    
    def test_station_passenger_management(self):
        from src.types import Station
        
        station = Station(Position(0, 0), StationType.CIRCLE)
        
        self.assertTrue(station.add_passenger(StationType.SQUARE))
        self.assertEqual(station.passengers[StationType.SQUARE], 1)
        
        self.assertFalse(station.add_passenger(StationType.CIRCLE))
        
        for _ in range(9):
            station.add_passenger(StationType.SQUARE)
        
        self.assertFalse(station.add_passenger(StationType.TRIANGLE))
    
    def test_train_capacity(self):
        from src.types import Train
        
        train = Train(Position(0, 0))
        
        for i in range(6):
            self.assertTrue(train.add_passenger(StationType.CIRCLE))
        
        self.assertFalse(train.add_passenger(StationType.SQUARE))
        
        removed = train.remove_passengers(StationType.CIRCLE)
        self.assertEqual(removed, 6)
        self.assertEqual(len(train.passengers), 0)


class TestGameConfig(unittest.TestCase):
    def test_valid_config(self):
        config = GameConfig(grid_size=10, max_lines=3)
        self.assertEqual(config.grid_size, 10)
        self.assertEqual(config.max_lines, 3)
    
    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            GameConfig(grid_size=2)
        
        with self.assertRaises(ValueError):
            GameConfig(max_lines=0)


class TestSimpleAgent(unittest.TestCase):
    def test_agent_action_generation(self):
        config = GameConfig(grid_size=5)
        env = MinimetroEnvironment(config)
        agent = SimpleAgent(env)
        
        obs = env.reset()
        action = agent.get_action(obs)
        
        self.assertIn('action', action)
        self.assertIn(action['action'], ['create_line', 'extend_line', 'remove_line', 'none'])


if __name__ == '__main__':
    unittest.main()