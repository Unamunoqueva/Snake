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
        self.game_over_message = ""

    def clear_screen(self) -> None:
        """Clear the terminal screen in a cross-platform way."""
        os.system("cls" if os.name == "nt" else "clear")

    def spawn_items(self) -> None:
        """Ensure there are enough items on the map, avoiding snake and existing items."""
        # Create a set of all positions occupied by the snake (head + tail) for efficient lookup.
        # Convert positions to tuples because list are not hashable for sets.
        occupied_by_snake = {tuple(self.my_position)}
        for segment in self.tail:
            occupied_by_snake.add(tuple(segment))

        # Create a set of existing item positions (as tuples) for efficient lookup.
        existing_item_positions_set = {tuple(pos) for pos in self.item_positions}

        available_cells_for_items = []
        for y_coord in range(self.height):
            for x_coord in range(self.width):
                pos_tuple = (x_coord, y_coord)
                # Check if the cell is not occupied by the snake or an existing item.
                if pos_tuple not in occupied_by_snake and pos_tuple not in existing_item_positions_set:
                    available_cells_for_items.append(list(pos_tuple)) # Store as list [x, y]
        
        random.shuffle(available_cells_for_items)

        # Add items until the desired number is reached or no more available cells.
        while len(self.item_positions) < self.num_objects and available_cells_for_items:
            self.item_positions.append(available_cells_for_items.pop())

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

    def _read_input_readchar(self) -> str:
        """Read input using readchar library."""
        import select

        if select.select([sys.stdin], [], [], 0.1)[0]:
            char = readchar.readkey()  # readkey already decodes if bytes
            arrow_mapping = {
                readchar.key.UP: "w",
                readchar.key.DOWN: "s",
                readchar.key.LEFT: "a",
                readchar.key.RIGHT: "d",
                readchar.key.ESC: "q",  # Map ESC to 'q' for quit
            }
            # Ensure char is a string if it's not a special key
            if char not in arrow_mapping and not isinstance(char, str):
                 return "" # Not a mapped key and not a string character
            return arrow_mapping.get(char, char if isinstance(char, str) else "")
        return ""

    def _read_input_windows(self) -> str:
        """Read input on Windows using msvcrt."""
        import msvcrt

        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char in (b"\x00", b"\xe0"):  # Arrow keys start with these
                second = msvcrt.getch()
                mapping = {b"H": "w", b"P": "s", b"K": "a", b"M": "d"}  # Up, Down, Left, Right
                return mapping.get(second, "")
            else:
                try:
                    decoded_char = char.decode()
                    return decoded_char
                except UnicodeDecodeError:
                    return ""  # Non-ASCII key, ignore
        return ""

    def _read_input_posix(self) -> str:
        """Read input on POSIX systems using termios and tty."""
        import select
        import termios
        import tty

        if select.select([sys.stdin], [], [], 0.1)[0]:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
                if char == "\x1b":  # ANSI escape sequence for arrow keys
                    # Read the next two characters for arrow key codes
                    # Check if there's more to read for an arrow key sequence
                    is_arrow_sequence = False
                    if select.select([sys.stdin], [], [], 0.01)[0]: # Check for '['
                        next_char = sys.stdin.read(1)
                        char += next_char
                        if next_char == '[':
                            if select.select([sys.stdin], [], [], 0.01)[0]: # Check for A, B, C, D
                                char += sys.stdin.read(1)
                                is_arrow_sequence = True
                            # else: incomplete sequence, char remains e.g. "\x1b[" - will not map below
                        # else: char is e.g. "\x1bO" for some terminals - will not map below
                    
                    if is_arrow_sequence:
                        mapping = {
                            "\x1b[A": "w",  # Up
                            "\x1b[B": "s",  # Down
                            "\x1b[D": "a",  # Left
                            "\x1b[C": "d",  # Right
                        }
                        return mapping.get(char, "")
                    elif char == "\x1b": # Standalone ESC
                        return "q" 
                    # If it was \x1b followed by something not forming a known arrow key,
                    # it will fall through and return char, which then gets filtered by allowed_inputs
                return char # Regular character
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ""

    def read_input(self) -> str:
        """Read and validate user input without blocking, prioritizing readchar."""
        allowed_inputs = ("w", "a", "s", "d", "q")
        direction = ""

        if readchar is not None:
            direction = self._read_input_readchar()
        elif os.name == "nt":
            direction = self._read_input_windows()
        else:  # POSIX-like
            direction = self._read_input_posix()

        if direction in allowed_inputs:
            return direction
        return ""

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
            self.game_over_message = "You hit a wall!"
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
            self.game_over_message = "You ran into yourself!"
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
            if not self.end_game: # Only sleep if game is not over
                time.sleep(0.2)
        
        # Game Over sequence
        self.clear_screen()
        print("+" + "-" * self.width * 3 + "+")
        print("|" + " " * (self.width * 3) + "|")
        game_over_text = "GAME OVER!"
        reason_text = self.game_over_message
        score_text = f"Final Score: {self.score}"

        print(f"|{game_over_text:^{self.width * 3}}|")
        print(f"|{reason_text:^{self.width * 3}}|")
        print(f"|{score_text:^{self.width * 3}}|")
        print("|" + " " * (self.width * 3) + "|")
        print("+" + "-" * self.width * 3 + "+")
        
        time.sleep(2) # Pause for 2 seconds before exiting


if __name__ == "__main__":
    game = SnakeGame()
    game.clear_screen()
    game.run()
