"""Snake game logic module."""

import os
import random
import sys
import time
from typing import List, Deque, Tuple, Set
from collections import deque

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
        self.item_positions: Set[Tuple[int, int]] = set()
        self.tail_length = 0
        self.tail: Deque[Tuple[int, int]] = deque()
        self.end_game = False
        self.score = 0
        self.last_direction = "d"

    def clear_screen(self) -> None:
        """Clear the terminal screen using an ANSI escape sequence."""
        print("\x1bc", end="")

    def spawn_items(self) -> None:
        """Ensure there are enough items on the map, trying to place a limited number each tick."""
        # 1. Calculate free_cells and num_to_spawn_this_tick
        total_cells = self.width * self.height
        occupied_by_head = 1
        occupied_by_tail = len(self.tail)
        occupied_by_items_count = len(self.item_positions)

        free_cells = total_cells - occupied_by_head - occupied_by_tail - occupied_by_items_count

        items_to_reach_target = self.num_objects - occupied_by_items_count
        num_to_spawn_this_tick = max(0, min(items_to_reach_target, free_cells))

        if num_to_spawn_this_tick == 0:
            return

        max_placement_attempts_per_item = 50

        # 2. Spawning Loop
        for _ in range(num_to_spawn_this_tick):
            # 3. Individual Item Placement
            for _ in range(max_placement_attempts_per_item): # attempt_num not used
                new_pos_list = [random.randint(0, self.width - 1), random.randint(0, self.height - 1)]
                new_pos_tuple = tuple(new_pos_list)

                # Collision Checks
                head_as_tuple = tuple(self.my_position)

                is_on_item = new_pos_tuple in self.item_positions
                is_on_head = new_pos_tuple == head_as_tuple
                is_on_tail = new_pos_tuple in self.tail

                if not is_on_item and not is_on_head and not is_on_tail:
                    self.item_positions.add(new_pos_tuple)
                    break  # Placed one item, move to the next in num_to_spawn_this_tick

    def draw_map(self) -> None:
        """Draw the game board."""
        board = [[" " for _ in range(self.width)] for _ in range(self.height)]

        for item_pos_tuple in self.item_positions: # item_pos_tuple is (x,y)
            board[item_pos_tuple[POS_Y]][item_pos_tuple[POS_X]] = "*"

        for segment in self.tail:
            board[segment[POS_Y]][segment[POS_X]] = "@"

        board[self.my_position[POS_Y]][self.my_position[POS_X]] = "@"

        print("+" + "-" * self.width * 3 + "+")
        for row in board:
            print("|" + "".join(f" {char} " for char in row) + "|")
        print("+" + "-" * self.width * 3 + "+")
        print(f"Score: {self.score} - Level: {self.level}")

    def read_input(self) -> str:
        """Read and validate user input without blocking."""
        allowed = ("w", "a", "s", "d", "q")

        arrow_mapping = {}
        if readchar is not None:
            arrow_mapping = {
                getattr(readchar, "key").UP: "w",
                getattr(readchar, "key").DOWN: "s",
                getattr(readchar, "key").LEFT: "a",
                getattr(readchar, "key").RIGHT: "d",
            }


        direction = ""

        if os.name == "nt":  # Windows always relies on msvcrt
            import msvcrt

            if msvcrt.kbhit():

                char = msvcrt.getch()
                if char in (b"\x00", b"\xe0"):
                    second = msvcrt.getch()
                    mapping = {b"H": "w", b"P": "s", b"K": "a", b"M": "d"}
                    direction = mapping.get(second, "")
                else:
                    if isinstance(char, bytes):
                        char = char.decode()
                    direction = char


        elif readchar is not None:
            import select

            if select.select([sys.stdin], [], [], 0.02)[0]:
                direction = readchar.readchar()
                if isinstance(direction, bytes):
                    direction = direction.decode()

                direction = arrow_mapping.get(direction, direction)

        else:
            # Fallback to built-in methods when readchar is unavailable
            if os.name == "nt":  # Windows (this branch shouldn't occur)
                import msvcrt

                if msvcrt.kbhit():

                    char = msvcrt.getch()
                    if char in (b"\x00", b"\xe0"):
                        second = msvcrt.getch()
                        mapping = {b"H": "w", b"P": "s", b"K": "a", b"M": "d"}
                        direction = mapping.get(second, "")
                    # This is a nested msvcrt block, the print was added in the primary msvcrt block above.
                    # No duplicate print here.
                    else:
                        if isinstance(char, bytes):
                            char = char.decode()
                        direction = char
                    # This is a nested msvcrt block, the print was added in the primary msvcrt block above.
                    # No duplicate print here.


            else:
                import select
                import termios
                import tty

                if select.select([sys.stdin], [], [], 0.02)[0]:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)

                        char = sys.stdin.read(1)
                        if char == "\x1b": # Arrow key
                            # Try to read the next two characters for escape sequence
                            # Use a short timeout to avoid blocking if it's just ESC key
                            if select.select([sys.stdin], [], [], 0.01)[0]:
                                char += sys.stdin.read(2)
                        

                        if char == "\x1b[A": direction = "w"
                        elif char == "\x1b[B": direction = "s"
                        elif char == "\x1b[D": direction = "a"
                        elif char == "\x1b[C": direction = "d"
                        else:
                            direction = char # For single characters like 'q', 'w', 'a', 's', 'd'
                        

                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        if direction not in allowed:
            return ""
        return direction

    def update_position(self, input_direction: str) -> None:
        """Update the snake position based on the direction."""
        current_direction_to_attempt = input_direction
        if not current_direction_to_attempt:
            current_direction_to_attempt = self.last_direction

        if current_direction_to_attempt == "q":
            self.end_game = True
            return

        final_direction_this_tick = current_direction_to_attempt
        if self.tail_length > 0:
            if (self.last_direction == "w" and current_direction_to_attempt == "s") or \
               (self.last_direction == "s" and current_direction_to_attempt == "w") or \
               (self.last_direction == "a" and current_direction_to_attempt == "d") or \
               (self.last_direction == "d" and current_direction_to_attempt == "a"):
                final_direction_this_tick = self.last_direction

        new_position = self.my_position.copy()

        if final_direction_this_tick == "w":
            new_position[POS_Y] -= 1
        elif final_direction_this_tick == "a":
            new_position[POS_X] -= 1
        elif final_direction_this_tick == "s":
            new_position[POS_Y] += 1
        elif final_direction_this_tick == "d":
            new_position[POS_X] += 1
        else:
            # This case should ideally not be reached if input is validated
            # and 180-degree turn logic defaults to a valid last_direction.
            # If it's reached, it implies an issue with direction handling.
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

        self.tail.appendleft(tuple(self.my_position.copy()))
        if len(self.tail) > self.tail_length:
            self.tail.pop()

        self.my_position = new_position
        
        if final_direction_this_tick in ("w", "a", "s", "d"):
            self.last_direction = final_direction_this_tick

        # Check collisions after moving
        head_pos_tuple = tuple(self.my_position)

        if head_pos_tuple in self.item_positions:
            self.item_positions.remove(head_pos_tuple)
            self.tail_length += 1
            self.score += 1

        if head_pos_tuple in self.tail: # self.tail is Deque[Tuple[int,int]]
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
            
            sleep_duration = max(0.05, 0.2 - (self.level - 1) * 0.02)
            time.sleep(sleep_duration)


if __name__ == "__main__":
    game = SnakeGame()
    game.clear_screen()
    game.run()
