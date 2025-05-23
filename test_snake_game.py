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

    # --- Tests for read_input logic ---

    @patch('select.select') # Mock select to control execution path
    @patch('snake_game.readchar') # Mock the readchar module used in SnakeGame
    def test_read_input_readchar_arrow_keys_mapping(self, mock_readchar_module, mock_select):
        game = SnakeGame()

        # Configure mock_readchar_module to simulate readchar being available
        # and having the 'key' attribute with UP, DOWN, LEFT, RIGHT
        mock_readchar_module.key = unittest.mock.MagicMock()
        mock_readchar_module.key.UP = "KEY_UP_CONST" # Arbitrary unique strings
        mock_readchar_module.key.DOWN = "KEY_DOWN_CONST"
        mock_readchar_module.key.LEFT = "KEY_LEFT_CONST"
        mock_readchar_module.key.RIGHT = "KEY_RIGHT_CONST"

        # Ensure os.name is not 'nt' so it tries the readchar branch
        with patch('os.name', 'posix'):
            # Simulate select indicating input is available on sys.stdin
            mock_select.return_value = ([sys.stdin], [], [])

            # Test UP arrow
            mock_readchar_module.readchar.return_value = "KEY_UP_CONST"
            self.assertEqual(game.read_input(), "w", "UP arrow should map to 'w'")

            # Test DOWN arrow
            mock_readchar_module.readchar.return_value = "KEY_DOWN_CONST"
            self.assertEqual(game.read_input(), "s", "DOWN arrow should map to 's'")

            # Test LEFT arrow
            mock_readchar_module.readchar.return_value = "KEY_LEFT_CONST"
            self.assertEqual(game.read_input(), "a", "LEFT arrow should map to 'a'")

            # Test RIGHT arrow
            mock_readchar_module.readchar.return_value = "KEY_RIGHT_CONST"
            self.assertEqual(game.read_input(), "d", "RIGHT arrow should map to 'd'")

            # Test a non-arrow key character pass-through
            mock_readchar_module.readchar.return_value = "q"
            self.assertEqual(game.read_input(), "q", "Non-arrow 'q' should pass through")
    
    @patch('select.select')
    @patch('snake_game.readchar')
    def test_read_input_allowed_filtering(self, mock_readchar_module, mock_select):
        game = SnakeGame()
        
        # Ensure os.name is not 'nt' for readchar path
        with patch('os.name', 'posix'):
            mock_select.return_value = ([sys.stdin], [], [])

            # Valid inputs
            for valid_key in ["w", "a", "s", "d", "q"]:
                mock_readchar_module.readchar.return_value = valid_key
                self.assertEqual(game.read_input(), valid_key, f"Valid key '{valid_key}' should pass filter")

            # Invalid inputs
            for invalid_key in ["x", "z", " ", "\n", "W"]:
                mock_readchar_module.readchar.return_value = invalid_key
                self.assertEqual(game.read_input(), "", f"Invalid key '{invalid_key}' should be filtered to ''")
            
            # Test select timeout (no input)
            mock_select.return_value = ([], [], []) # Simulate no input available
            self.assertEqual(game.read_input(), "", "No input should result in ''")

    @patch('os.name', 'nt') # Simulate Windows
    # No kbhit mock needed as _read_keypress_blocking_internal calls getch directly
    @patch('msvcrt.getch')
    def test_blocking_internal_msvcrt_keys(self, mock_getch):
        game = SnakeGame()
        # Test a normal allowed key
        mock_getch.return_value = b'w'
        self.assertEqual(game._read_keypress_blocking_internal(), 'w')

        # Test an arrow key sequence (e.g., UP arrow b'\xe0' then b'H')
        mock_getch.side_effect = [b'\xe0', b'H']
        self.assertEqual(game._read_keypress_blocking_internal(), 'w')
        
        # Test a disallowed key
        mock_getch.side_effect = None # Clear side_effect
        mock_getch.return_value = b'x'
        self.assertEqual(game._read_keypress_blocking_internal(), '')
        
        # Stop the thread started by SnakeGame constructor
        game.input_thread.stop()
        game.input_thread.join()

    # Renaming previous tests to reflect they test the internal blocking method now
    @patch('select.select') 
    @patch('snake_game.readchar') 
    def test_blocking_internal_readchar_arrow_keys_mapping(self, mock_readchar_module, mock_select):
        game = SnakeGame()
        mock_readchar_module.key = unittest.mock.MagicMock()
        mock_readchar_module.key.UP = "KEY_UP_CONST"
        mock_readchar_module.key.DOWN = "KEY_DOWN_CONST"
        mock_readchar_module.key.LEFT = "KEY_LEFT_CONST"
        mock_readchar_module.key.RIGHT = "KEY_RIGHT_CONST"

        with patch('os.name', 'posix'):
            # For _read_keypress_blocking_internal, select is only used inside tty for escape seq
            # For readchar path, readchar.readchar() is called directly.
            # So, we don't need to mock select's return value for the primary readchar call.
            
            # Test UP arrow
            mock_readchar_module.readchar.return_value = "KEY_UP_CONST"
            self.assertEqual(game._read_keypress_blocking_internal(), "w", "UP arrow should map to 'w'")

            mock_readchar_module.readchar.return_value = "KEY_DOWN_CONST"
            self.assertEqual(game._read_keypress_blocking_internal(), "s", "DOWN arrow should map to 's'")

            mock_readchar_module.readchar.return_value = "KEY_LEFT_CONST"
            self.assertEqual(game._read_keypress_blocking_internal(), "a", "LEFT arrow should map to 'a'")

            mock_readchar_module.readchar.return_value = "KEY_RIGHT_CONST"
            self.assertEqual(game._read_keypress_blocking_internal(), "d", "RIGHT arrow should map to 'd'")

            mock_readchar_module.readchar.return_value = "q"
            self.assertEqual(game._read_keypress_blocking_internal(), "q", "Non-arrow 'q' should pass through")
        
        game.input_thread.stop()
        game.input_thread.join()

    @patch('select.select') # select is used in tty fallback for escape sequences
    @patch('snake_game.readchar')
    def test_blocking_internal_allowed_filtering(self, mock_readchar_module, mock_select):
        game = SnakeGame()
        with patch('os.name', 'posix'):
            # Valid inputs
            for valid_key in ["w", "a", "s", "d", "q"]:
                mock_readchar_module.readchar.return_value = valid_key
                self.assertEqual(game._read_keypress_blocking_internal(), valid_key, f"Valid key '{valid_key}' should pass filter")

            # Invalid inputs
            for invalid_key in ["x", "z", " ", "\n", "W"]:
                mock_readchar_module.readchar.return_value = invalid_key
                self.assertEqual(game._read_keypress_blocking_internal(), "", f"Invalid key '{invalid_key}' should be filtered to ''")
        
        game.input_thread.stop()
        game.input_thread.join()

    # New tests for InputThread and SnakeGame.read_input()
    @patch('time.sleep', return_value=None) # Patch time.sleep in InputThread to speed up test
    def test_input_thread_queue_logic(self, mock_sleep):
        mock_blocking_read = unittest.mock.MagicMock()
        # Import InputThread locally if it's not available at module level of test file
        # from snake_game import InputThread # Assuming it's available via snake_game import
        
        # Need to access InputThread from the snake_game module
        # This is a bit of a workaround if InputThread is not directly importable
        # If snake_game.InputThread is how it's accessed, fine.
        # For this test, let's assume we can get InputThread class
        InputThread_class = getattr(sys.modules['snake_game'], 'InputThread')

        input_thread = InputThread_class(read_char_function=mock_blocking_read)
        input_thread.start()

        # Simulate read_char_function returning a key
        mock_blocking_read.return_value = "w"
        # Give thread time to process. Loop until key is available or timeout.
        key = ""
        for _ in range(10): # Try up to 10 times (equiv to 10 * 0.01s if sleep wasn't mocked)
            key = input_thread.get_key()
            if key: break
            time.sleep(0.005) # Small sleep to yield execution
        self.assertEqual(key, "w")
        self.assertEqual(input_thread.key_queue.qsize(), 0, "Queue should be empty after get_key")


        # Simulate multiple keys rapidly: only last should be kept
        mock_blocking_read.side_effect = ["a", "s", "d"]
        # The thread's loop will call read_char_function multiple times.
        # We need to ensure it runs enough times to process these.
        # The queue clearing logic means only the last one processed before get_key will be there.
        
        # First 'a'
        time.sleep(0.05) # Allow thread to process 'a'
        self.assertEqual(input_thread.get_key(), "a")
        
        # Then 's'
        time.sleep(0.05) # Allow thread to process 's'
        self.assertEqual(input_thread.get_key(), "s")

        # Then 'd'
        time.sleep(0.05) # Allow thread to process 'd'
        self.assertEqual(input_thread.get_key(), "d")
        
        # Verify get_key returns "" if queue is empty
        self.assertEqual(input_thread.get_key(), "")

        input_thread.stop()
        input_thread.join()

    def test_snake_game_read_input_integration(self):
        game = SnakeGame()
        # Mock the input_thread.get_key directly on the instance
        game.input_thread.get_key = unittest.mock.MagicMock(return_value="test_key")
        
        self.assertEqual(game.read_input(), "test_key")
        game.input_thread.get_key.assert_called_once()
        
        game.input_thread.stop() # Stop the original thread
        game.input_thread.join()

    def test_input_thread_stop_event(self):
        mock_blocking_read = unittest.mock.MagicMock(return_value="w")
        InputThread_class = getattr(sys.modules['snake_game'], 'InputThread')
        input_thread = InputThread_class(read_char_function=mock_blocking_read)
        
        self.assertFalse(input_thread.stop_event.is_set())
        input_thread.stop()
        self.assertTrue(input_thread.stop_event.is_set())
        # Note: .join() is not called here as the thread isn't started for this specific test.
        # If it were started, join would be appropriate.


if __name__ == '__main__':
    unittest.main()
