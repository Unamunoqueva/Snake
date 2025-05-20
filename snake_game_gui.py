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
        self.game_over_text = None

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
            if self.game_over_text is None:
                self.game_over_text = self.canvas.create_text(
                    self.width * self.cell_size / 2,
                    self.height * self.cell_size / 2,
                    text="Game Over",
                    fill="red",
                    font=("Arial", 16),
                )
            return
        self.spawn_items()
        self.draw_map()
        direction = self.next_direction or self.last_direction
        self.update_position(direction)
        self.next_direction = ""
        self.root.after(200, self.game_step)

    def run(self) -> None:
        self.root.after(0, self.game_step)
        self.root.mainloop()


if __name__ == "__main__":
    game = SnakeGameGUI()
    game.run()
