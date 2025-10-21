"""Snake game logic module."""

import os
import random
import sys
import time
import json
from pathlib import Path
from typing import List, Deque, Tuple, Set, Dict, Any
from collections import deque

try:
    import readchar  # type: ignore
except ImportError:  # pragma: no cover - fallback for environments without readchar
    readchar = None

POS_X = 0
POS_Y = 1

# High score file location
HIGHSCORE_FILE = Path.home() / ".snake_highscore.json"


class SnakeGame:
    """A simple terminal-based snake game."""

    def __init__(self, width: int = 20, height: int = 10, num_objects: int = 20):
        # Validate parameters
        if width < 1:
            raise ValueError(f"width must be at least 1, got {width}")
        if height < 1:
            raise ValueError(f"height must be at least 1, got {height}")
        if num_objects < 0:
            raise ValueError(f"num_objects must be non-negative, got {num_objects}")

        # Auto-adjust num_objects if it's too large for the board
        max_objects = width * height - 1  # Leave at least 1 cell for the snake head
        if num_objects > max_objects:
            num_objects = max_objects

        self.width = width
        self.height = height
        self.num_objects = num_objects
        # Set initial position to be safe within board bounds
        # Try to use [3, 1] if possible, otherwise adjust to fit board
        self.my_position: List[int] = [min(3, width - 1), min(1, height - 1)]
        self.item_positions: Set[Tuple[int, int]] = set()
        self.tail_length = 0
        self.tail: Deque[Tuple[int, int]] = deque()
        self.end_game = False
        self.end_game_reason = ""
        self.score = 0
        self.last_direction = "d"
        self.highscore_data = self._load_highscore()
        self.game_start_time = time.time()

    def _load_highscore(self) -> Dict[str, Any]:
        """Load high score data from file."""
        default_data = {"high_score": 0, "games_played": 0, "total_score": 0}
        try:
            highscore_path = Path(HIGHSCORE_FILE) if isinstance(HIGHSCORE_FILE, str) else HIGHSCORE_FILE
            if highscore_path.exists():
                with open(highscore_path, 'r') as f:
                    loaded_data = json.load(f)
                    # Validate and sanitize loaded data types
                    validated_data = {}
                    for key in default_data.keys():
                        if key in loaded_data and isinstance(loaded_data[key], int) and loaded_data[key] >= 0:
                            validated_data[key] = loaded_data[key]
                        else:
                            validated_data[key] = default_data[key]
                    return validated_data
            return default_data
        except (json.JSONDecodeError, IOError):
            return default_data

    def _save_highscore(self) -> None:
        """Save high score data to file."""
        try:
            # Update statistics
            self.highscore_data["games_played"] += 1
            self.highscore_data["total_score"] += self.score
            if self.score > self.highscore_data.get("high_score", 0):
                self.highscore_data["high_score"] = self.score

            highscore_path = Path(HIGHSCORE_FILE) if isinstance(HIGHSCORE_FILE, str) else HIGHSCORE_FILE
            with open(highscore_path, 'w') as f:
                json.dump(self.highscore_data, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save

    @property
    def high_score(self) -> int:
        """Get the current high score."""
        return self.highscore_data.get("high_score", 0)

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
        print(f"Score: {self.score} - Level: {self.level} - High Score: {self.high_score}")

    def read_input(self) -> str:
        """Read and validate user input without blocking."""
        allowed = ("w", "a", "s", "d", "q")

        arrow_mapping = {}
        if readchar is not None:
            try:
                arrow_mapping = {
                    getattr(readchar, "key").UP: "w",
                    getattr(readchar, "key").DOWN: "s",
                    getattr(readchar, "key").LEFT: "a",
                    getattr(readchar, "key").RIGHT: "d",
                }
            except (AttributeError, TypeError):
                # Fallback if readchar.key doesn't exist or is malformed
                arrow_mapping = {}


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

            if select.select([sys.stdin], [], [], 0.05)[0]:
                try:
                    direction = readchar.readchar()
                    if isinstance(direction, bytes):
                        direction = direction.decode()

                    direction = arrow_mapping.get(direction, direction)
                except Exception:
                    # Silently ignore read errors and return empty direction
                    direction = ""

        else:
            # Fallback to built-in methods when readchar is unavailable on Unix
            import select
            import termios
            import tty

            if select.select([sys.stdin], [], [], 0.05)[0]:
                try:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)

                        char = sys.stdin.read(1)
                        if char == "\x1b":  # Arrow key
                            # Try to read the next two characters for escape sequence
                            # Use a short timeout to avoid blocking if it's just ESC key
                            if select.select([sys.stdin], [], [], 0.01)[0]:
                                char += sys.stdin.read(2)

                        if char == "\x1b[A":
                            direction = "w"
                        elif char == "\x1b[B":
                            direction = "s"
                        elif char == "\x1b[D":
                            direction = "a"
                        elif char == "\x1b[C":
                            direction = "d"
                        else:
                            direction = char  # For single characters like 'q', 'w', 'a', 's', 'd'

                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except (OSError, termios.error):
                    # Silently ignore if stdin is not a terminal
                    direction = ""
        
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
            self.end_game_reason = "salir"
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
            self.end_game = True
            self.end_game_reason = "pared"
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
            self.end_game = True
            self.end_game_reason = "colision"

    @property
    def level(self) -> int:
        """Calculate the game level based on the score."""
        return self.score // 5 + 1

    def _show_game_over(self, old_high_score: int) -> None:
        """Display game over screen with statistics."""
        self.clear_screen()
        game_duration = int(time.time() - self.game_start_time)

        print("\n" + "=" * 60)
        print("GAME OVER".center(60))
        print("=" * 60)

        if self.end_game_reason == "pared":
            print("Has chocado con la pared".center(60))
        elif self.end_game_reason == "colision":
            print("Te has chocado contigo mismo".center(60))
        elif self.end_game_reason == "salir":
            print("Has salido del juego".center(60))
        else:
            # Fallback for unexpected end_game_reason values
            print("Juego terminado".center(60))

        print()
        print(f"{'ESTADÍSTICAS':^60}")
        print("-" * 60)
        print(f"  Puntuación Final: {self.score}")
        print(f"  Nivel Alcanzado: {self.level}")
        print(f"  Longitud de la Serpiente: {self.tail_length + 1}")
        print(f"  Tiempo de Juego: {game_duration} segundos")
        print()

        is_new_highscore = self.score > old_high_score
        if is_new_highscore:
            print(f"  ¡NUEVO RÉCORD! Puntuación anterior: {old_high_score}")
        else:
            print(f"  Récord Actual: {self.high_score}")

        print()
        # Note: _save_highscore() already updated games_played and total_score
        avg_score = self.highscore_data["total_score"] / self.highscore_data["games_played"]
        print(f"  Partidas Jugadas: {self.highscore_data['games_played']}")
        print(f"  Puntuación Media: {avg_score:.1f}")
        print("=" * 60)
        print()

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

        # Save high score and show game over screen
        old_high_score = self.high_score
        self._save_highscore()
        self._show_game_over(old_high_score)


if __name__ == "__main__":
    game = SnakeGame()
    game.clear_screen()
    game.run()
