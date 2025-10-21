try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    # Tkinter not available - create dummy to allow module import
    TKINTER_AVAILABLE = False
    class tk:
        """Dummy tkinter module for environments without tkinter."""
        class Tk:
            pass
        class Canvas:
            pass
        class Event:
            pass

import time
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
        self.next_direction = ""
        self.game_over_text = None
        # Bind key press handler AFTER initializing all attributes to avoid race condition
        self.root.bind("<KeyPress>", self.on_key_press)

    def on_key_press(self, event: tk.Event) -> None:
        # Ignore input if game is over
        if self.end_game:
            return

        key = event.keysym.lower()
        mapping = {"up": "w", "down": "s", "left": "a", "right": "d"}
        key = mapping.get(key, key)
        if key in {"w", "a", "s", "d", "q"}:
            self.next_direction = key

    def draw_map(self) -> None:
        self.canvas.delete("all")
        for item in self.item_positions:
            # Validate bounds before drawing
            if 0 <= item[POS_X] < self.width and 0 <= item[POS_Y] < self.height:
                x1 = item[POS_X] * self.cell_size
                y1 = item[POS_Y] * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow")

        for part in [tuple(self.my_position)] + list(self.tail):
            # Validate bounds before drawing
            if 0 <= part[POS_X] < self.width and 0 <= part[POS_Y] < self.height:
                x1 = part[POS_X] * self.cell_size
                y1 = part[POS_Y] * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="green")

        self.canvas.create_text(
            5,
            5,
            anchor="nw",
            text=f"Score: {self.score} | Level: {self.level} | High Score: {self.high_score}",
            fill="white",
            font=("Arial", 10, "bold"),
        )

    def game_step(self) -> None:
        if self.end_game:
            if self.game_over_text is None:
                # Save old high score before updating
                old_high_score = self.high_score

                # Save high score
                self._save_highscore()

                # Display game over screen
                center_x = self.width * self.cell_size / 2
                center_y = self.height * self.cell_size / 2

                self.canvas.create_rectangle(
                    0, 0,
                    self.width * self.cell_size,
                    self.height * self.cell_size,
                    fill="black",
                    stipple="gray50"
                )

                self.game_over_text = self.canvas.create_text(
                    center_x,
                    center_y - 60,
                    text="GAME OVER",
                    fill="red",
                    font=("Arial", 24, "bold"),
                )

                # Determine end reason
                reason_text = ""
                if self.end_game_reason == "pared":
                    reason_text = "¡Chocaste con la pared!"
                elif self.end_game_reason == "colision":
                    reason_text = "¡Te chocaste contigo mismo!"
                elif self.end_game_reason == "salir":
                    reason_text = "Saliste del juego"
                else:
                    # Fallback for unexpected end_game_reason values
                    reason_text = "Juego terminado"

                self.canvas.create_text(
                    center_x,
                    center_y - 30,
                    text=reason_text,
                    fill="white",
                    font=("Arial", 12),
                )

                # Show final score
                self.canvas.create_text(
                    center_x,
                    center_y,
                    text=f"Puntuación Final: {self.score}",
                    fill="yellow",
                    font=("Arial", 14, "bold"),
                )

                # Show high score
                is_new_highscore = self.score > old_high_score
                highscore_text = f"Récord: {self.high_score}"
                if is_new_highscore:
                    highscore_text = f"¡NUEVO RÉCORD! {self.high_score}"

                self.canvas.create_text(
                    center_x,
                    center_y + 25,
                    text=highscore_text,
                    fill="green" if is_new_highscore else "white",
                    font=("Arial", 12, "bold"),
                )

                # Show stats
                game_duration = int(time.time() - self.game_start_time)
                self.canvas.create_text(
                    center_x,
                    center_y + 50,
                    text=f"Nivel: {self.level} | Longitud: {self.tail_length + 1} | Tiempo: {game_duration}s",
                    fill="white",
                    font=("Arial", 10),
                )
            return

        # Update game state first
        direction = self.next_direction or self.last_direction
        self.update_position(direction)
        self.next_direction = ""

        # Always spawn items and redraw to show the final state
        self.spawn_items()
        self.draw_map()

        # Calculate dynamic speed based on level
        sleep_duration = max(0.05, 0.2 - (self.level - 1) * 0.02)
        self.root.after(int(sleep_duration * 1000), self.game_step)

    def run(self) -> None:
        # Initial draw before starting game loop
        self.spawn_items()
        self.draw_map()
        # Calculate initial speed
        sleep_duration = max(0.05, 0.2 - (self.level - 1) * 0.02)
        self.root.after(int(sleep_duration * 1000), self.game_step)
        self.root.mainloop()


if __name__ == "__main__":
    game = SnakeGameGUI()
    game.run()
