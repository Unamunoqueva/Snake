"""Snake game logic module."""

import os
import random
import sys
import time
from typing import List

try:
    import readchar  # type: ignore
except ImportError:  # pragma: no cover - fallback for environments without readchar
    readchar = None

POS_X = 0
POS_Y = 1


class SnakeGame:
    """A simple terminal-based snake game."""

    def __init__(self, width: int = 20, height: int = 10, num_objects: int = 20):
        self.width = width
        self.height = height
        self.num_objects = num_objects
        self.my_position: List[int] = [3, 1]
        self.item_positions: List[List[int]] = []
        self.tail_length = 0
        self.tail: List[List[int]] = []
        self.end_game = False
        self.score = 0
        self.last_direction = "d"

    def clear_screen(self) -> None:
        """Clear the terminal screen in a cross-platform way."""
        os.system("cls" if os.name == "nt" else "clear")

    def spawn_items(self) -> None:
        """Ensure there are enough items on the map."""
        while len(self.item_positions) < self.num_objects:
            new_position = [random.randint(0, self.width - 1), random.randint(0, self.height - 1)]
            if new_position not in self.item_positions and new_position != self.my_position:
                self.item_positions.append(new_position)

    def draw_map(self) -> None:
        """Draw the game board."""
        print("+" + "-" * self.width * 3 + "+")
        for coordinate_y in range(self.height):
            print("|", end="")
            for coordinate_x in range(self.width):
                char_to_draw = " "

                for item_position in self.item_positions:
                    if item_position[POS_X] == coordinate_x and item_position[POS_Y] == coordinate_y:
                        char_to_draw = "*"

                for tail_piece in self.tail:
                    if tail_piece[POS_X] == coordinate_x and tail_piece[POS_Y] == coordinate_y:
                        char_to_draw = "@"

                if self.my_position[POS_X] == coordinate_x and self.my_position[POS_Y] == coordinate_y:
                    char_to_draw = "@"

                print(f" {char_to_draw} ", end="")
            print("|")
        print("+" + "-" * self.width * 3 + "+")
        print(f"Score: {self.score} - Level: {self.level}")

    def read_input(self) -> str:
        """Read and validate user input without blocking."""
        allowed = ("w", "a", "s", "d", "q")
        direction = ""

        if os.name == "nt":  # Windows always relies on msvcrt
            import msvcrt

            if msvcrt.kbhit():
                direction = msvcrt.getch()
                if isinstance(direction, bytes):
                    direction = direction.decode()
        elif readchar is not None:
            import select

            if select.select([sys.stdin], [], [], 0.1)[0]:
                direction = readchar.readchar()
                if isinstance(direction, bytes):
                    direction = direction.decode()
        else:
            # Fallback to built-in methods when readchar is unavailable
            if os.name == "nt":  # Windows (this branch shouldn't occur)
                import msvcrt

                if msvcrt.kbhit():
                    direction = msvcrt.getch()
                    if isinstance(direction, bytes):
                        direction = direction.decode()
            else:
                import select
                import termios
                import tty

                if select.select([sys.stdin], [], [], 0.1)[0]:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)
                        direction = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if direction not in allowed:
            return ""
        return direction

    def update_position(self, direction: str) -> None:
        """Update the snake position based on the direction."""
        if direction == "":
            direction = self.last_direction

        if direction == "q":
            self.end_game = True
            return

        new_position = self.my_position.copy()

        if direction == "w":
            new_position[POS_Y] -= 1
        elif direction == "a":
            new_position[POS_X] -= 1
        elif direction == "s":
            new_position[POS_Y] += 1
        elif direction == "d":
            new_position[POS_X] += 1
        else:
            return

        # Wall collision detection
        if (
            new_position[POS_X] < 0
            or new_position[POS_X] >= self.width
            or new_position[POS_Y] < 0
            or new_position[POS_Y] >= self.height
        ):
            print("Has chocado con la pared")
            self.end_game = True
            return

        self.tail.insert(0, self.my_position.copy())
        self.tail = self.tail[: self.tail_length]
        self.my_position = new_position
        self.last_direction = direction

        # Check collisions after moving
        if self.my_position in self.item_positions:
            self.item_positions.remove(self.my_position)
            self.tail_length += 1
            self.score += 1

        if self.my_position in self.tail:
            print("Has muerto")
            self.end_game = True

    @property
    def level(self) -> int:
        """Calculate the game level based on the score."""
        return self.score // 5 + 1

    def run(self) -> None:
        """Run the main game loop."""
        while not self.end_game:
            self.spawn_items()
            self.clear_screen()
            self.draw_map()
            direction = self.read_input()
            self.update_position(direction)
            time.sleep(0.2)


if __name__ == "__main__":
    game = SnakeGame()
    game.clear_screen()
    game.run()
