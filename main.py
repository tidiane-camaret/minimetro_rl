import argparse
import sys
sys.path.append('..')  # Adjust path to import GameConfig
from src.config import GameConfig
from src.game import MinimetroGame, SimpleAgent
from src.environment import MinimetroEnvironment


def main():
    parser = argparse.ArgumentParser(description='MinimetroRL Game')
    parser.add_argument('--mode', choices=['agent', 'pygame'], default='agent',
                        help='Game mode: agent (text) or pygame (visual)')
    parser.add_argument('--grid-size', type=int, default=15,
                        help='Grid size (default: 15)')
    parser.add_argument('--max-lines', type=int, default=3,
                        help='Maximum number of lines (default: 3)')
    parser.add_argument('--max-steps', type=int, default=None,
                        help='Maximum number of steps (default: unlimited)')
    parser.add_argument('--demo', action='store_true',
                        help='Run with simple AI agent')
    
    args = parser.parse_args()
    
    config = GameConfig(
        mode=args.mode,
        grid_size=args.grid_size,
        max_lines=args.max_lines
    )
    
    game = MinimetroGame(config)
    
    if args.demo:
        print("Running demo with simple AI agent...")
        agent = SimpleAgent(game.env)
        game.play(agent=agent, max_steps=args.max_steps)
    else:
        print("Starting interactive game...")
        game.play(max_steps=args.max_steps)


if __name__ == "__main__":
    main()
