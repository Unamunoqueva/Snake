"""Snake game logic module."""

import os
import random
import sys
import time
import threading
import queue
from typing import List, Deque, Tuple, Set
from collections import deque

try:
    import readchar  # type: ignore
except ImportError:  # pragma: no cover - fallback for environments without readchar
    readchar = None

POS_X = 0
POS_Y = 1


class InputThread(threading.Thread):
    def __init__(self, read_char_function):
        super().__init__(daemon=True) # Set as daemon thread so it exits when main program exits
        self.read_char_function = read_char_function # This function will do the actual blocking read
        self.key_queue = queue.Queue(maxsize=1)
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            try:
                # The read_char_function is expected to be blocking
                # and return a character (or mapped direction string)
                # or None/raise an exception on timeout/error if it handles that internally.
                # For now, assume it blocks until a key is pressed and returns it.
                char = self.read_char_function() 
                if char: # If a valid character/key was read
                    # Clear the queue to store only the latest key
                    try:
                        self.key_queue.get_nowait()
                    except queue.Empty:
                        pass
                    # Put the new key
                    self.key_queue.put_nowait(char)
                else:
                    # If read_char_function can return None (e.g. on a timeout if not fully blocking)
                    # prevent busy-waiting. A truly blocking read_char_function makes this less critical.
                    time.sleep(0.01) # Small sleep if char is None
            except Exception as e:
                # Handle potential exceptions from read_char_function if necessary,
                # or let them propagate if they indicate a serious issue.
                # For robustness in a thread, it's often good to catch and log/ignore minor issues.
                # print(f"Error in InputThread: {e}") # Optional: for debugging
                if self.stop_event.is_set(): # Exit if stopping
                    break
                time.sleep(0.01) # Prevent busy loop on continuous errors

    def get_key(self):
        try:
            return self.key_queue.get_nowait()
        except queue.Empty:
            return "" # Return empty string if no key is available

    def stop(self):
        self.stop_event.set()


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

        # Initialize and start the input thread
        self.input_thread = InputThread(read_char_function=self._read_keypress_blocking_internal)
        self.input_thread.start()

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

    def _read_keypress_blocking_internal(self) -> str:
        """Reads a single keypress, blocking. Returns mapped direction or empty string."""
        allowed = ("w", "a", "s", "d", "q")
        direction = ""

        arrow_mapping = {}
        if readchar is not None: # This check happens at module load time for readchar itself
                                 # but here it's for initializing the map
            # Ensure readchar and its 'key' attribute are valid before using getattr
            if hasattr(readchar, 'key'):
                # These might fail if readchar.key doesn't have all these (e.g. on some OS)
                # A more robust way might be to try-except getattr for each
                try: ArrowKeyUP = getattr(readchar, "key").UP 
                except AttributeError: ArrowKeyUP = None # Or some other placeholder
                try: ArrowKeyDOWN = getattr(readchar, "key").DOWN
                except AttributeError: ArrowKeyDOWN = None
                try: ArrowKeyLEFT = getattr(readchar, "key").LEFT
                except AttributeError: ArrowKeyLEFT = None
                try: ArrowKeyRIGHT = getattr(readchar, "key").RIGHT
                except AttributeError: ArrowKeyRIGHT = None

                arrow_mapping = {
                    k:v for k,v in { # Filter out None keys if any getattr failed
                        ArrowKeyUP: "w", ArrowKeyDOWN: "s",
                        ArrowKeyLEFT: "a", ArrowKeyRIGHT: "d"
                    }.items() if k is not None
                }

        if os.name == "nt":
            import msvcrt
            char_bytes = msvcrt.getch() # Blocking read
            if char_bytes in (b"\x00", b"\xe0"):  # Arrow key prefix
                second_byte = msvcrt.getch()
                # Mapping for common arrow keys on Windows
                mapping = {b"H": "w", b"P": "s", b"K": "a", b"M": "d"}
                direction = mapping.get(second_byte, "")
            else:
                try:
                    direction = char_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    direction = "" # Or handle error appropriately

        elif readchar is not None:
            # readchar.readchar() is blocking
            key_pressed = readchar.readchar() 
            if key_pressed in arrow_mapping:
                direction = arrow_mapping[key_pressed]
            else:
                direction = key_pressed # Assume it's a direct char like 'q'
        
        else: # Fallback for non-Windows, if readchar is not available
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno()) # Set raw mode
                char = sys.stdin.read(1) # Blocking read of a single character

                if char == "\x1b":  # Start of an escape sequence (likely arrow key)
                    # Try to read the rest of the sequence non-blockingly for a short duration
                    # This part is tricky because sys.stdin.read() in raw mode is blocking.
                    # A true non-blocking read for sequence parts would need select here again,
                    # or a different strategy. For simplicity, this example assumes common sequences.
                    # A common way is to read 2 more chars, but this might block if it's just ESC.
                    # For a robust solution, one might need a small select timeout here.
                    # However, the prompt asked to remove select from the main blocking logic.
                    # Let's assume a simple 3-char sequence for arrows:
                    # This is a simplification; true handling is more complex.
                    # For this exercise, we'll keep it simple as per prompt's focus.
                    # A better way might be to put the read(2) in a try with short select.
                    # Given the constraint to remove select, we'll assume common fixed length sequences.
                    # This will behave poorly for lone ESC or other escape sequences.
                    # The select for 0.01s was a good compromise. Re-adding for just this part:
                    import select
                    if sys.stdin in select.select([sys.stdin], [], [], 0.01)[0]:
                        char += sys.stdin.read(2) 

                # Map common ANSI escape sequences for arrow keys
                if char == "\x1b[A": direction = "w"
                elif char == "\x1b[B": direction = "s"
                elif char == "\x1b[D": direction = "a"
                elif char == "\x1b[C": direction = "d"
                else:
                    direction = char # Normal key like 'q'
            
            finally: # Always restore terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if direction not in allowed:
            return ""
        return direction

    def read_input(self) -> str:
        """Gets the last pressed key from the input thread, non-blocking."""
        return self.input_thread.get_key()

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
        
        # After game loop finishes, stop the input thread
        print("Exiting game, stopping input thread...") # Optional debug print
        self.input_thread.stop()
        self.input_thread.join() # Wait for the thread to finish
        print("Input thread stopped.") # Optional debug print


if __name__ == "__main__":
    # Terminal setup for raw/cbreak mode is often done outside the class,
    # globally for the application's lifetime, especially for the tty part.
    # For example, here or in the run() method before the loop and restored after.
    # However, _read_keypress_blocking_internal handles its own tty settings for now.
    
    # It's also important that if the game crashes, terminal settings are restored.
    # A try/finally block around game.run() in __main__ is good for this.
    
    original_terminal_settings = None
    if os.name != 'nt' and not readchar: # If using tty fallback
        try:
            fd = sys.stdin.fileno()
            original_terminal_settings = termios.tcgetattr(fd)
        except termios.error: # Not a tty (e.g. when piping)
            original_terminal_settings = None

    try:
        game = SnakeGame()
        game.clear_screen()
        game.run()
    finally:
        if original_terminal_settings:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, original_terminal_settings)
                print("Terminal settings restored.")
            except Exception as e:
                print(f"Failed to restore terminal settings: {e}")
        print("Game has exited.")
