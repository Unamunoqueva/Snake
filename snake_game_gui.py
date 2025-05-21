import tkinter as tk
from snake_game import SnakeGame, POS_X, POS_Y


class SnakeGameGUI(SnakeGame):
    """Snake game with a simple Tkinter GUI."""

    def __init__(self, width: int = 20, height: int = 10, num_objects: int = 20, cell_size: int = 20) -> None:
        super().__init__(width, height, num_objects)
        self.cell_size = cell_size
        self.root = tk.Tk()
        self.root.title("Snake")
        self.canvas = tk.Canvas(
            self.root,
            width=self.width * self.cell_size,
            height=self.height * self.cell_size,
            bg="black",
        )
        self.canvas.pack()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.next_direction = ""
        # For game over UI elements
        self.game_over_text_id = None
        self.restart_button_widget = None
        self.restart_button_window_id = None
        self.quit_button_widget = None
        self.quit_button_window_id = None
        
        # Initial setup
        self.spawn_items() # Ensure items are there at the very beginning

    def on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        mapping = {"up": "w", "down": "s", "left": "a", "right": "d"}
        key = mapping.get(key, key)
        if key in {"w", "a", "s", "d", "q"}:
            self.next_direction = key

    def draw_map(self) -> None:
        self.canvas.delete("all")
        for item in self.item_positions:
            x1 = item[POS_X] * self.cell_size
            y1 = item[POS_Y] * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow")

        for part in [self.my_position] + self.tail:
            x1 = part[POS_X] * self.cell_size
            y1 = part[POS_Y] * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="green")

        self.canvas.create_text(
            5,
            5,
            anchor="nw",
            text=f"Score: {self.score} Level: {self.level}",
            fill="white",
        )

    def game_step(self) -> None:
        if self.end_game:
            # self.game_over_text_id is handled by _show_game_over_elements
            self._show_game_over_elements() 
            return
        
        # If game is running, ensure game over elements are hidden
        self._hide_game_over_elements()

        self.spawn_items()
        self.draw_map()
        direction = self.next_direction or self.last_direction
        # If 'q' was pressed, self.next_direction will be 'q'.
        # update_position handles self.end_game = True if direction is 'q'.
        if self.next_direction == 'q': 
            self.end_game = True # Explicitly set end_game if 'q' is from GUI key press
            # Game will end and show Game Over screen on the next game_step
            self.root.after(120, self.game_step)
            return

        self.update_position(direction)
        self.next_direction = "" # Clear after use

        if self.end_game: # Check if update_position caused game over
            # Game ended due to collision, call game_step immediately to show Game Over screen
            # without the usual delay.
            self.root.after(0, self.game_step) 
        else:
            self.root.after(120, self.game_step)

    def _reset_game_state(self) -> None:
        """Resets the game to its initial state."""
        # Reset core game logic by re-initializing from the base class
        # This will reset score, snake position, tail, items, end_game flag, last_direction
        super().__init__(width=self.width, height=self.height, num_objects=self.num_objects)
        
        # Reset GUI specific state
        self.next_direction = ""
        # self.last_direction is reset by super().__init__
        
        self._hide_game_over_elements()
        self.spawn_items() # Initial items for the new game
        self.draw_map() # Draw initial map

    def _restart_game_command(self) -> None:
        """Command for the Restart button."""
        self._reset_game_state()
        self.game_step() # Start the game loop again

    def _quit_game_command(self) -> None:
        """Command for the Quit button."""
        self.root.destroy()

    def _show_game_over_elements(self) -> None:
        """Displays 'Game Over' text and Restart/Quit buttons."""
        if self.game_over_text_id is None:
            self.game_over_text_id = self.canvas.create_text(
                self.width * self.cell_size / 2,
                self.height * self.cell_size / 3, # Positioned higher
                text="Game Over",
                fill="red",
                font=("Arial", 24, "bold"),
                tag="gameover"
            )

        button_y_offset = self.height * self.cell_size / 2
        if self.restart_button_widget is None:
            self.restart_button_widget = tk.Button(self.root, text="Restart", command=self._restart_game_command)
            self.restart_button_window_id = self.canvas.create_window(
                self.width * self.cell_size / 2, button_y_offset, window=self.restart_button_widget, tag="gameover"
            )

        if self.quit_button_widget is None:
            self.quit_button_widget = tk.Button(self.root, text="Quit", command=self._quit_game_command)
            self.quit_button_window_id = self.canvas.create_window(
                self.width * self.cell_size / 2, button_y_offset + 40, window=self.quit_button_widget, tag="gameover"
            )
        
        # Ensure all game over elements are on top
        self.canvas.lift("gameover")


    def _hide_game_over_elements(self) -> None:
        """Hides 'Game Over' text and Restart/Quit buttons."""
        if self.game_over_text_id is not None:
            self.canvas.delete(self.game_over_text_id)
            self.game_over_text_id = None
        
        if self.restart_button_widget is not None:
            # self.canvas.delete(self.restart_button_window_id) # Widget is destroyed by .destroy()
            self.restart_button_widget.destroy()
            self.restart_button_widget = None
            self.restart_button_window_id = None # ID becomes invalid once widget is destroyed

        if self.quit_button_widget is not None:
            # self.canvas.delete(self.quit_button_window_id)
            self.quit_button_widget.destroy()
            self.quit_button_widget = None
            self.quit_button_window_id = None

    def run(self) -> None:
        self.root.after(0, self.game_step)
        self.root.mainloop()


if __name__ == "__main__":
    game = SnakeGameGUI()
    game.run()
