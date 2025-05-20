# 🐍 Snake Game

¡Bienvenido a este pequeño proyecto de la serpiente en la terminal!

Este repositorio contiene una implementación sencilla del clásico juego **Snake** escrito en Python. Está pensado para ejecutarse directamente desde la terminal y ofrece una mecánica rápida y divertida.

## 🚀 Comenzar

1. (Opcional) Instala `readchar` para una experiencia de entrada de teclas mejorada:
   ```bash
   pip install readchar
   ```
2. Ejecuta el juego con:
   ```bash
   python snake_game.py
   ```

## ⌨️ Controles

- `w` ↑  mover arriba
- `s` ↓  mover abajo
- `a` ←  mover izquierda
- `d` →  mover derecha
- `q`  salir del juego

## 🧪 Pruebas

Puedes ejecutar las pruebas unitarias con:
```bash
python -m unittest
```

## 📁 Estructura del proyecto

- `snake_game.py` – Lógica principal del juego.
- `maze.py` – Arranque rápido para iniciar la partida.
- `test_snake_game.py` – Conjunto de pruebas que validan el comportamiento del juego.

## 🔍 Detalles del código

El corazón del proyecto está en `snake_game.py` dentro de la clase **`SnakeGame`**:

- **`__init__(width, height, num_objects)`** – prepara el tablero y las variables básicas (posición inicial, puntuación, cola).
- **`clear_screen()`** – limpia la terminal para que cada fotograma se muestre fresco.
- **`spawn_items()`** – genera los `*` en posiciones aleatorias hasta alcanzar el número deseado.
- **`draw_map()`** – dibuja los bordes, la serpiente `@` y los objetos, además de mostrar la puntuación y el nivel.
- **`read_input()`** – captura una tecla (`w`, `a`, `s`, `d` o `q`) de forma multiplataforma, utilizando `readchar` si está disponible.
- **`update_position(direction)`** – actualiza la posición según la dirección, crece al comer y detecta colisiones.
- **`level`** – propiedad que aumenta la dificultad cada 5 puntos de puntuación.
- **`run()`** – bucle principal que enlaza todo lo anterior hasta que el jugador pierde o pulsa `q`.

Para lanzar el juego rápidamente también existe `maze.py`, que simplemente crea una instancia y ejecuta `run()`.

## 🙌 Contribución

👍 ¡Las contribuciones, ideas y mejoras son bienvenidas!

Si encuentras algún problema o quieres proponer una nueva característica, no dudes en abrir un *issue* o enviar un *pull request*.

🚀 ¡Diviértete programando y jugando!
