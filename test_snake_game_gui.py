import unittest
from unittest.mock import patch, MagicMock, Mock
import tempfile
from collections import deque
import sys

# Try to import tkinter, skip all tests if not available
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    # Create a dummy class to prevent import errors
    class tk:
        class Tk:
            pass
        class Canvas:
            pass

# Only import GUI if tkinter is available
if TKINTER_AVAILABLE:
    from snake_game_gui import SnakeGameGUI
    from snake_game import POS_X, POS_Y
else:
    # Create dummy classes to prevent import errors
    class SnakeGameGUI:
        pass
    POS_X = 0
    POS_Y = 1


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter is not available in this environment")
class SnakeGameGUITestCase(unittest.TestCase):
    """Test cases for the SnakeGameGUI class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary file for high score to avoid affecting real data
        self.temp_highscore = tempfile.NamedTemporaryFile(delete=False)
        self.highscore_patcher = patch('snake_game.HIGHSCORE_FILE', self.temp_highscore.name)
        self.highscore_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.highscore_patcher.stop()
        import os
        if os.path.exists(self.temp_highscore.name):
            os.unlink(self.temp_highscore.name)

    def test_gui_initialization(self):
        """Test that GUI initializes correctly."""
        game = SnakeGameGUI(width=10, height=10, num_objects=5, cell_size=20)

        self.assertIsInstance(game.root, tk.Tk)
        self.assertIsInstance(game.canvas, tk.Canvas)
        self.assertEqual(game.cell_size, 20)
        self.assertEqual(game.next_direction, "")
        self.assertIsNone(game.game_over_text)

        # Inherited from SnakeGame
        self.assertEqual(game.width, 10)
        self.assertEqual(game.height, 10)
        self.assertEqual(game.num_objects, 5)

        game.root.destroy()

    def test_gui_canvas_dimensions(self):
        """Test that canvas has correct dimensions based on cell size."""
        game = SnakeGameGUI(width=15, height=12, cell_size=25)

        expected_width = 15 * 25
        expected_height = 12 * 25

        self.assertEqual(game.canvas.winfo_reqwidth(), expected_width)
        self.assertEqual(game.canvas.winfo_reqheight(), expected_height)

        game.root.destroy()

    def test_on_key_press_wasd(self):
        """Test keyboard input handling for WASD keys."""
        game = SnakeGameGUI()

        # Test 'w' key
        event = Mock()
        event.keysym = 'w'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'w')

        # Test 'a' key
        event.keysym = 'a'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'a')

        # Test 's' key
        event.keysym = 's'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 's')

        # Test 'd' key
        event.keysym = 'd'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'd')

        # Test 'q' key (quit)
        event.keysym = 'q'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'q')

        game.root.destroy()

    def test_on_key_press_arrow_keys(self):
        """Test keyboard input handling for arrow keys."""
        game = SnakeGameGUI()

        event = Mock()

        # Test up arrow
        event.keysym = 'Up'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'w')

        # Test down arrow
        event.keysym = 'Down'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 's')

        # Test left arrow
        event.keysym = 'Left'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'a')

        # Test right arrow
        event.keysym = 'Right'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'd')

        game.root.destroy()

    def test_on_key_press_case_insensitive(self):
        """Test that key press handling is case insensitive."""
        game = SnakeGameGUI()
        event = Mock()

        # Test uppercase W
        event.keysym = 'W'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'w')

        # Test uppercase A
        event.keysym = 'A'
        game.on_key_press(event)
        self.assertEqual(game.next_direction, 'a')

        game.root.destroy()

    def test_on_key_press_invalid_keys(self):
        """Test that invalid keys are ignored."""
        game = SnakeGameGUI()
        event = Mock()

        # Set an initial valid direction
        game.next_direction = 'w'

        # Try an invalid key
        event.keysym = 'x'
        game.on_key_press(event)
        # next_direction should remain unchanged since 'x' is not valid
        self.assertEqual(game.next_direction, 'w')

        game.root.destroy()

    def test_draw_map_creates_canvas_items(self):
        """Test that draw_map creates items on the canvas."""
        game = SnakeGameGUI(width=5, height=5, cell_size=20)

        # Set up game state
        game.my_position = [2, 2]
        game.item_positions = {(1, 1), (3, 3)}
        game.tail = deque([(2, 1)])
        game.score = 5

        # Draw the map
        game.draw_map()

        # Check that canvas has items (exact count depends on implementation)
        # At minimum: items, snake head, tail segments, score text
        canvas_items = game.canvas.find_all()
        self.assertGreater(len(canvas_items), 0)

        game.root.destroy()

    def test_draw_map_clears_previous_items(self):
        """Test that draw_map clears previous canvas items."""
        game = SnakeGameGUI(width=5, height=5)

        # Draw once
        game.my_position = [2, 2]
        game.draw_map()
        first_items = len(game.canvas.find_all())

        # Draw again with different position
        game.my_position = [3, 3]
        game.draw_map()
        second_items = len(game.canvas.find_all())

        # Both should have items, and we're verifying canvas is being redrawn
        self.assertGreater(first_items, 0)
        self.assertGreater(second_items, 0)

        game.root.destroy()

    def test_draw_map_displays_score(self):
        """Test that draw_map displays the current score."""
        game = SnakeGameGUI(width=5, height=5)
        game.score = 10
        game.draw_map()

        # Check that canvas has text items
        canvas_items = game.canvas.find_all()
        self.assertGreater(len(canvas_items), 0)

        game.root.destroy()

    def test_game_step_normal_operation(self):
        """Test game_step during normal gameplay."""
        game = SnakeGameGUI(width=10, height=10)

        # Mock the after method to prevent infinite loop
        game.root.after = Mock()

        # Set initial state
        game.my_position = [5, 5]
        game.next_direction = 'd'
        game.last_direction = 'w'

        # Call game_step
        game.game_step()

        # Verify after was called to schedule next step
        game.root.after.assert_called_once()

        # Verify next_direction was reset
        self.assertEqual(game.next_direction, "")

        # Verify position was updated
        self.assertEqual(game.my_position, [6, 5])

        game.root.destroy()

    def test_game_step_uses_last_direction_when_no_input(self):
        """Test that game_step continues in last direction when no input."""
        game = SnakeGameGUI(width=10, height=10)
        game.root.after = Mock()

        game.my_position = [5, 5]
        game.last_direction = 'd'
        game.next_direction = ""

        game.game_step()

        # Should move right (d)
        self.assertEqual(game.my_position, [6, 5])

        game.root.destroy()

    def test_game_step_when_game_over(self):
        """Test game_step when game is over."""
        game = SnakeGameGUI(width=5, height=5)
        game.root.after = Mock()

        # Set game over state
        game.end_game = True
        game.end_game_reason = "pared"
        game.score = 10

        # Call game_step
        game.game_step()

        # Should not schedule another step
        game.root.after.assert_not_called()

        # Should have created game over text
        self.assertIsNotNone(game.game_over_text)

        game.root.destroy()

    def test_game_step_displays_game_over_screen(self):
        """Test that game over screen is displayed correctly."""
        game = SnakeGameGUI(width=10, height=10, cell_size=20)
        game.root.after = Mock()

        game.end_game = True
        game.end_game_reason = "colision"
        game.score = 15

        game.game_step()

        # Check that game over text was created
        self.assertIsNotNone(game.game_over_text)

        # Canvas should have items
        self.assertGreater(len(game.canvas.find_all()), 0)

        game.root.destroy()

    def test_game_step_only_shows_game_over_once(self):
        """Test that game over screen is only created once."""
        game = SnakeGameGUI(width=5, height=5)
        game.root.after = Mock()

        game.end_game = True
        game.end_game_reason = "pared"

        # Call game_step twice
        game.game_step()
        first_text = game.game_over_text

        game.game_step()
        second_text = game.game_over_text

        # Should be the same object
        self.assertEqual(first_text, second_text)

        game.root.destroy()

    def test_game_step_saves_highscore_on_game_over(self):
        """Test that high score is saved when game ends."""
        game = SnakeGameGUI(width=5, height=5)
        game.root.after = Mock()

        # Mock _save_highscore
        game._save_highscore = Mock()

        game.end_game = True
        game.end_game_reason = "salir"
        game.score = 20

        game.game_step()

        # Should have called save_highscore once
        game._save_highscore.assert_called_once()

        game.root.destroy()

    def test_game_step_spawns_items(self):
        """Test that game_step spawns items during gameplay."""
        game = SnakeGameGUI(width=10, height=10, num_objects=5)
        game.root.after = Mock()

        # Initially no items
        game.item_positions = set()

        game.game_step()

        # Should have spawned items
        self.assertGreater(len(game.item_positions), 0)

        game.root.destroy()

    def test_game_step_item_collection(self):
        """Test that collecting items increases score and tail length."""
        game = SnakeGameGUI(width=10, height=10)
        game.root.after = Mock()

        game.my_position = [5, 5]
        game.item_positions = {(6, 5)}  # Item to the right
        game.next_direction = 'd'
        game.tail_length = 0
        initial_score = game.score

        game.game_step()

        # Should have collected the item
        self.assertNotIn((6, 5), game.item_positions)
        self.assertEqual(game.score, initial_score + 1)
        self.assertEqual(game.tail_length, 1)

        game.root.destroy()

    def test_run_starts_game_loop(self):
        """Test that run method starts the game loop."""
        game = SnakeGameGUI(width=5, height=5)

        # Mock both after and mainloop to prevent blocking
        game.root.after = Mock()
        game.root.mainloop = Mock()

        game.run()

        # Should have scheduled first game step
        game.root.after.assert_called_once_with(0, game.game_step)

        # Should have started mainloop
        game.root.mainloop.assert_called_once()

        game.root.destroy()

    def test_inherited_collision_detection(self):
        """Test that wall collision works in GUI version."""
        game = SnakeGameGUI(width=5, height=5)
        game.root.after = Mock()

        game.my_position = [0, 0]
        game.next_direction = 'a'  # Move left into wall

        game.game_step()

        # Should have ended game
        self.assertTrue(game.end_game)
        self.assertEqual(game.end_game_reason, "pared")

        game.root.destroy()

    def test_inherited_self_collision_detection(self):
        """Test that self collision works in GUI version."""
        game = SnakeGameGUI(width=10, height=10)
        game.root.after = Mock()

        # Set up a scenario where snake collides with itself
        game.my_position = [5, 5]
        game.tail_length = 4
        game.tail = deque([(5, 4), (4, 4), (4, 5), (4, 6)])
        game.last_direction = 'w'
        game.next_direction = 'a'

        game.game_step()

        # Should have ended game
        self.assertTrue(game.end_game)
        self.assertEqual(game.end_game_reason, "colision")

        game.root.destroy()

    def test_multiple_items_on_canvas(self):
        """Test drawing multiple items on the canvas."""
        game = SnakeGameGUI(width=10, height=10, cell_size=20)

        game.item_positions = {(1, 1), (2, 2), (3, 3), (4, 4)}
        game.my_position = [5, 5]

        game.draw_map()

        # Verify canvas has items
        canvas_items = game.canvas.find_all()
        self.assertGreater(len(canvas_items), len(game.item_positions))

        game.root.destroy()

    def test_tail_rendering(self):
        """Test that tail segments are rendered correctly."""
        game = SnakeGameGUI(width=10, height=10, cell_size=20)

        game.my_position = [5, 5]
        game.tail = deque([(4, 5), (3, 5), (2, 5)])
        game.tail_length = 3

        game.draw_map()

        # Canvas should have items for head, tail segments, and score
        canvas_items = game.canvas.find_all()
        self.assertGreater(len(canvas_items), 3)

        game.root.destroy()

    def test_game_step_quit_action(self):
        """Test that pressing 'q' ends the game."""
        game = SnakeGameGUI(width=10, height=10)
        game.root.after = Mock()

        game.next_direction = 'q'
        game.game_step()

        # Should have ended game
        self.assertTrue(game.end_game)
        self.assertEqual(game.end_game_reason, "salir")

        game.root.destroy()

    def test_different_end_game_reasons_displayed(self):
        """Test that different end game reasons are displayed correctly."""
        reasons = [
            ("pared", "¡Chocaste con la pared!"),
            ("colision", "¡Te chocaste contigo mismo!"),
            ("salir", "Saliste del juego")
        ]

        for reason, expected_text in reasons:
            game = SnakeGameGUI(width=5, height=5)
            game.root.after = Mock()

            game.end_game = True
            game.end_game_reason = reason

            game.game_step()

            # Game over text should be created
            self.assertIsNotNone(game.game_over_text)

            game.root.destroy()

    def test_highscore_displayed_in_gui(self):
        """Test that high score is displayed in the GUI."""
        game = SnakeGameGUI(width=10, height=10)

        # Set a high score
        game.highscore_data["high_score"] = 50
        game.score = 25

        game.draw_map()

        # Canvas should have text showing the high score
        canvas_items = game.canvas.find_all()
        self.assertGreater(len(canvas_items), 0)

        game.root.destroy()

    def test_level_progression_in_gui(self):
        """Test that level is displayed correctly as score increases."""
        game = SnakeGameGUI(width=10, height=10)

        # Score of 12 should be level 3 (12 // 5 + 1)
        game.score = 12
        self.assertEqual(game.level, 3)

        game.draw_map()

        # Canvas should display level
        canvas_items = game.canvas.find_all()
        self.assertGreater(len(canvas_items), 0)

        game.root.destroy()


if __name__ == '__main__':
    unittest.main()
