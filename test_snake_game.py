import unittest
from snake_game import SnakeGame


class SnakeGameTestCase(unittest.TestCase):
    def test_initial_state(self):
        game = SnakeGame()
        self.assertEqual(game.my_position, [3, 1])
        self.assertEqual(game.score, 0)
        self.assertFalse(game.end_game)

    def test_spawn_items(self):
        game = SnakeGame(num_objects=5)
        game.spawn_items()
        self.assertEqual(len(game.item_positions), 5)
        self.assertNotIn(game.my_position, game.item_positions)

    def test_move_and_grow(self):
        game = SnakeGame()
        game.item_positions = [[3, 0]]
        game.update_position('w')
        self.assertEqual(game.score, 1)
        self.assertEqual(game.tail_length, 1)
        self.assertEqual(game.my_position, [3, 0])

    def test_level_property(self):
        game = SnakeGame()
        game.score = 12
        self.assertEqual(game.level, 3)

    def test_wall_collision(self):
        game = SnakeGame(width=3, height=3)
        game.my_position = [0, 0]
        game.update_position('a')
        self.assertTrue(game.end_game)

    def test_auto_move(self):
        game = SnakeGame()
        game.update_position('')
        self.assertEqual(game.my_position, [4, 1])

    def test_quit_input(self):
        game = SnakeGame()
        game.update_position('q')
        self.assertTrue(game.end_game)

    def test_direction_reversal_no_tail(self):
        game = SnakeGame()
        game.my_position = [3, 1]
        game.last_direction = 'd'
        game.tail_length = 0 # Ensure no tail
        game.tail = []
        
        game.update_position('a') # Try to reverse
        
        self.assertFalse(game.end_game)
        self.assertEqual(game.my_position, [2, 1]) # Should have moved left
        self.assertEqual(game.last_direction, 'a')

    def test_direction_reversal_with_tail_self_collision(self):
        game = SnakeGame()
        game.my_position = [3, 1] # Head
        game.tail_length = 1
        game.tail = [[2, 1]]      # Tail segment behind the head
        game.last_direction = 'd' # Moving right
        
        # Attempt to reverse direction into the first tail segment
        game.update_position('a') 
        
        self.assertTrue(game.end_game)
        self.assertEqual(game.game_over_message, "You ran into yourself!")

    def test_item_spawning_limited_space(self):
        # Board of 3x1 = 3 cells.
        # Target 3 items, but snake head takes 1 cell, leaving 2 for items.
        game = SnakeGame(width=3, height=1, num_objects=3)
        game.my_position = [0, 0] # Snake at one end
        game.spawn_items()
        # Should only be able to spawn items in the remaining 2 cells.
        self.assertEqual(len(game.item_positions), 2) 
        self.assertNotIn(game.my_position, game.item_positions)

    def test_item_spawning_fills_available_spots_respecting_tail(self):
        # Board of 3x1 = 3 cells.
        game = SnakeGame(width=3, height=1, num_objects=3)
        game.my_position = [1, 0] # Snake head in the middle
        game.tail = [[0,0]]       # Tail at one end
        game.tail_length = 1
        # Snake: T H _  (Tail at [0,0], Head at [1,0])
        # Only one spot [2,0] is available for items.
        
        game.spawn_items()
        
        self.assertEqual(len(game.item_positions), 1)
        self.assertIn([2,0], game.item_positions)
        self.assertNotIn(game.my_position, game.item_positions)
        self.assertNotIn(game.tail[0], game.item_positions)

    def test_item_spawning_stops_if_board_full_no_loop(self):
        # Test that spawn_items terminates even if num_objects is too high for a full board
        # Board 2x1 = 2 cells. Snake head + 1 tail = 2 cells. No space for items.
        game = SnakeGame(width=2, height=1, num_objects=1) # Target 1 item
        game.my_position = [1,0]
        game.tail = [[0,0]]
        game.tail_length = 1
        
        # To simulate the problematic part of spawn_items, we need to control random.randint
        # This is hard without mocking. Instead, we check if it adds items when no space.
        # The current spawn_items loop will not terminate if random always picks occupied spots
        # and num_objects > available_spots. This is a known limitation mentioned in comments.
        # This test will verify it doesn't add items if space is full.
        
        # We can't directly test the infinite loop without mocking random.
        # However, we can test that it doesn't add items if the board is effectively full.
        initial_item_count = len(game.item_positions) # Should be 0
        game.spawn_items()
        self.assertEqual(len(game.item_positions), initial_item_count) # No items should be added


if __name__ == '__main__':
    unittest.main()
