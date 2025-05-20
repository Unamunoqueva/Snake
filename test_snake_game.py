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


if __name__ == '__main__':
    unittest.main()
