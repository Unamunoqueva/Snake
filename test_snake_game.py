import unittest
from unittest.mock import patch
import io
import sys
from collections import deque
from typing import Set, Tuple, Deque # Not strictly necessary for tests but good for clarity

from snake_game import SnakeGame, POS_X, POS_Y


class SnakeGameTestCase(unittest.TestCase):
    def test_initial_state(self):
        game = SnakeGame()
        self.assertEqual(game.my_position, [3, 1])
        self.assertEqual(game.score, 0)
        self.assertFalse(game.end_game)
        self.assertEqual(game.item_positions, set()) # Updated
        self.assertIsInstance(game.item_positions, set) # Ensure it's a set
        self.assertEqual(game.tail, deque())         # Updated
        self.assertIsInstance(game.tail, deque)      # Ensure it's a deque
        self.assertEqual(game.last_direction, "d")

    def test_spawn_items(self):
        game = SnakeGame(num_objects=5, width=10, height=10) # Ensure enough space
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 5)
        for item_pos in game.item_positions:
            self.assertIsInstance(item_pos, tuple) # Items are tuples
            self.assertNotEqual(item_pos, tuple(game.my_position)) # Not on head (tuple comparison)
        # Test that spawn_items respects num_objects and doesn't overpopulate
        game.spawn_items() # Call again
        self.assertEqual(len(game.item_positions), 5)


    def test_move_and_grow(self):
        game = SnakeGame(width=5, height=5)
        # Item is at (3,0) as a tuple in a set
        game.item_positions = {(3, 0)}
        game.my_position = [3,1] # Start below item
        
        game.update_position('w') # Move up to consume item
        
        self.assertEqual(game.score, 1)
        self.assertEqual(game.tail_length, 1)
        self.assertEqual(game.my_position, [3, 0]) # Head moved
        self.assertEqual(game.tail, deque([(3,1)])) # Tail has previous head pos as tuple
        self.assertEqual(len(game.item_positions), 0) # Item consumed

    def test_level_property(self):
        game = SnakeGame()
        game.score = 12
        self.assertEqual(game.level, 3) # 12 // 5 + 1 = 3

    def test_wall_collision(self):
        game = SnakeGame(width=3, height=3)
        game.my_position = [0, 0] # Top-left corner
        game.update_position('a') # Move left into wall
        self.assertTrue(game.end_game)

        game = SnakeGame(width=3, height=3)
        game.my_position = [0, 0]
        game.update_position('w') # Move up into wall
        self.assertTrue(game.end_game)

    def test_auto_move(self):
        game = SnakeGame()
        initial_pos_x, initial_pos_y = game.my_position[POS_X], game.my_position[POS_Y]
        game.last_direction = "d" # Explicitly set for clarity
        game.update_position('')  # Auto-move in last_direction
        self.assertEqual(game.my_position, [initial_pos_x + 1, initial_pos_y])
        self.assertEqual(game.last_direction, "d")

    @patch('random.randint')
    def test_item_not_spawn_on_tail(self, mock_randint):
        game = SnakeGame(width=3, height=1, num_objects=1)
        game.my_position = [0, 0]
        game.tail = deque([(1,0), (2,0)]) # Tail fills (1,0) and (2,0)
        game.tail_length = 2

        # Attempt 1: Try to spawn on tail segment (1,0)
        mock_randint.side_effect = [1, 0] # item_x = 1, item_y = 0
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 0, "Item should not spawn on tail")

        # Attempt 2: Try to spawn on another tail segment (2,0)
        mock_randint.side_effect = [2, 0] # item_x = 2, item_y = 0
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 0, "Item should not spawn on tail again")
        
        # Attempt 3: Board is full (head at (0,0), tail at (1,0), (2,0)), no space for item
        # spawn_items should not add any items if no free cells
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 0, "Item should not spawn if board is full")

        # Attempt 4: Free up space and spawn
        game = SnakeGame(width=2, height=1, num_objects=1)
        game.my_position = [0,0] # Head at (0,0)
        game.tail_length = 0; game.tail.clear() # No tail
                                 # (1,0) is free
        mock_randint.side_effect = [1, 0] # item_x = 1, item_y = 0
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 1, "Item should spawn in free cell")
        self.assertIn((1,0), game.item_positions)


    def test_item_spawning_limited_space(self):
        game = SnakeGame(width=3, height=1, num_objects=3) # Board: (0,0), (1,0), (2,0)
        
        # Scenario 1: Head at (0,0), no tail. 2 free cells.
        game.my_position = [0,0]
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 2) # Max 2 items can spawn

        # Scenario 2: Head at (1,0), tail at (0,0). 1 free cell.
        game.item_positions.clear() # Clear items for fresh count
        game.tail.appendleft(tuple(game.my_position)) # Old head [0,0] becomes tail
        game.tail_length = 1
        game.my_position = [1,0] # New head
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 1) # Max 1 item at (2,0)

        # Scenario 3: Head at (2,0), tail at (1,0), (0,0). 0 free cells.
        game.item_positions.clear()
        game.tail.appendleft(tuple(game.my_position)) # Old head [1,0] becomes tail
        game.tail_length = 2
        game.my_position = [2,0] # New head
        # Tail is now ((1,0), (0,0))
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 0) # No space left

    def test_prevent_180_degree_turns(self):
        game = SnakeGame(width=10, height=10)
        game.my_position = [5,5]
        game.last_direction = "d"
        
        # With tail
        game.tail.appendleft((4,5)) # Previous position before moving "d"
        game.tail_length = 1
        
        game.update_position("a") # Attempt 180-degree turn (left, opposite of right)
        self.assertEqual(game.my_position, [6,5], "Should continue in last_direction 'd'")
        self.assertEqual(game.last_direction, "d")

        # Without tail (180-degree turn should be allowed)
        game.tail_length = 0
        game.tail.clear()
        game.my_position = [5,5] # Reset position
        game.last_direction = "d" # Reset last direction
        
        game.update_position("a") # Attempt 180-degree turn
        self.assertEqual(game.my_position, [4,5], "Should move 'a' as no tail")
        self.assertEqual(game.last_direction, "a")

    def test_draw_map_output(self):
        game = SnakeGame(width=3, height=3)
        game.my_position = [1,1] # Center
        game.item_positions = {(0,0)} # Item at top-left
        game.tail = deque([(1,0)]) # Tail segment above head
        game.tail_length = 1
        game.score = 5 # Level 2

        expected_output_lines = [
            "+---------+",
            "| *  @  . |", # Item, Tail, Empty (assuming . is empty, but game uses space)
            "| .  @  . |", # Empty, Head, Empty
            "| .  .  . |", # All empty
            "+---------+",
            "Score: 5 - Level: 2"
        ]
        # The game actually prints " " for empty, not "."
        # And it prints " @ " for snake parts, " * " for items
        expected_board_drawing = [
            "+---------+",
            "| *  @    |", # Item, Tail, Empty
            "|    @    |", # Empty, Head, Empty
            "|         |", # All empty
            "+---------+",
            "Score: 5 - Level: 2"
        ]


        captured_output = io.StringIO()
        sys.stdout = captured_output # Redirect stdout
        game.draw_map()
        sys.stdout = sys.__stdout__ # Reset stdout

        # Normalize line endings and strip trailing spaces from lines
        output_lines = [line.rstrip() for line in captured_output.getvalue().strip().split('\n')]
        expected_board_drawing_stripped = [line.rstrip() for line in expected_board_drawing]
        
        # Print for debugging if test fails
        # print("\nExpected:")
        # for line in expected_board_drawing_stripped: print(f"'{line}'")
        # print("\nGot:")
        # for line in output_lines: print(f"'{line}'")

        self.assertEqual(output_lines, expected_board_drawing_stripped)


if __name__ == '__main__':
    unittest.main()
