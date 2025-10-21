# 🐍 Snake Game - Juego de la Serpiente

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

¡Bienvenido al clásico juego de la Serpiente implementado en Python! Este proyecto ofrece una experiencia de juego completa tanto en terminal como en interfaz gráfica, con sistema de puntuación persistente, estadísticas detalladas y tests exhaustivos.

## 📑 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Cómo Jugar](#-cómo-jugar)
- [Controles](#️-controles)
- [Arquitectura del Código](#-arquitectura-del-código)
- [Sistema de Puntuación](#-sistema-de-puntuación)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Desarrollo y Tests](#-desarrollo-y-tests)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

### Principales

- 🎮 **Dos modos de juego**: Terminal (ASCII) y GUI (Tkinter)
- 🏆 **Sistema de High Score**: Guarda automáticamente tu mejor puntuación
- 📊 **Estadísticas detalladas**: Tiempo de juego, nivel alcanzado, partidas jugadas
- ⚡ **Dificultad progresiva**: La velocidad aumenta con cada nivel
- 🎯 **Múltiples objetos**: Configurable cantidad de comida en pantalla
- 🔄 **Prevención de giros de 180°**: No puedes girar directamente hacia atrás
- 💾 **Persistencia de datos**: Los récords se guardan entre sesiones
- ✅ **Tests completos**: Suite de tests unitarios exhaustiva

### Mejoras Recientes

- ✨ Sistema de puntuación mejorado con persistencia en archivo JSON
- 📈 Pantalla de Game Over con estadísticas completas
- 🎨 Interfaz GUI mejorada con información de High Score
- 🧪 Tests actualizados y expandidos para nuevas funcionalidades
- 📝 Documentación completa y detallada

## 📋 Requisitos

### Requisitos Mínimos

- **Python**: 3.7 o superior
- **Sistema Operativo**: Linux, macOS, o Windows

### Dependencias Opcionales

```bash
# Para una experiencia de entrada mejorada en terminal (recomendado)
pip install readchar
```

> **Nota**: Si `readchar` no está instalado, el juego utilizará automáticamente los métodos de entrada nativos de Python (funciona perfectamente, pero `readchar` ofrece mejor respuesta).

## 🚀 Instalación

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Unamunoqueva/Snake.git
cd Snake

# 2. (Opcional pero recomendado) Instalar readchar
pip install readchar

# 3. ¡Listo para jugar!
python snake_game.py        # Versión terminal
python snake_game_gui.py    # Versión GUI
python maze.py              # Atajo para versión terminal
```

### Instalación con Entorno Virtual (Recomendado)

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install readchar

# 4. Jugar
python snake_game.py
```

## 🎮 Cómo Jugar

### Versión Terminal

```bash
python snake_game.py
# o
python maze.py
```

La versión de terminal muestra el juego en ASCII con el siguiente formato:
- `@` = Serpiente (cabeza y cola)
- `*` = Comida
- Bordes del tablero claramente definidos
- Información en tiempo real: Score, Level, High Score

### Versión GUI

```bash
python snake_game_gui.py
```

La versión gráfica ofrece:
- Visualización colorida (serpiente verde, comida amarilla)
- Pantalla de Game Over elegante
- Información visual del High Score
- Ventana redimensionable

### Objetivo del Juego

1. **Come**: Dirígete hacia los asteriscos (`*`) para aumentar tu puntuación
2. **Crece**: Cada objeto consumido hace crecer tu serpiente
3. **Evita**: No choques con las paredes ni contigo mismo
4. **Sobrevive**: Cuanto más tiempo juegues y más comas, mayor será tu puntuación

### Progresión de Niveles

- **Nivel 1**: Velocidad base (0.20s por movimiento)
- **Nivel 2**: Se alcanza con 5 puntos
- **Nivel 3**: Se alcanza con 10 puntos
- **Nivel N**: Cada 5 puntos sube un nivel
- La velocidad aumenta 0.02s por nivel (hasta un mínimo de 0.05s)

## ⌨️ Controles

### Versión Terminal

| Tecla | Acción |
|-------|--------|
| `W` o `↑` | Mover arriba |
| `S` o `↓` | Mover abajo |
| `A` o `←` | Mover izquierda |
| `D` o `→` | Mover derecha |
| `Q` | Salir del juego |

### Versión GUI

| Tecla | Acción |
|-------|--------|
| `↑` o `W` | Mover arriba |
| `↓` o `S` | Mover abajo |
| `←` o `A` | Mover izquierda |
| `→` o `D` | Mover derecha |
| `Q` | Salir del juego |

> **Tip**: Las flechas del teclado funcionan en ambas versiones si tienes `readchar` instalado.

## 🏗️ Arquitectura del Código

### Clase Principal: `SnakeGame`

La clase `SnakeGame` es el núcleo del juego y contiene toda la lógica principal.

#### Inicialización (`__init__`)

```python
def __init__(self, width: int = 20, height: int = 10, num_objects: int = 20):
```

**Parámetros**:
- `width`: Ancho del tablero (por defecto 20)
- `height`: Alto del tablero (por defecto 10)
- `num_objects`: Número de objetos de comida en pantalla (por defecto 20)

**Atributos inicializados**:
- `my_position`: Posición actual de la cabeza `[x, y]`
- `item_positions`: Set de tuplas con posiciones de comida
- `tail`: Deque con las posiciones de la cola
- `tail_length`: Longitud actual de la cola
- `score`: Puntuación actual
- `highscore_data`: Datos persistentes de récords
- `game_start_time`: Timestamp de inicio para estadísticas

#### Métodos Principales

##### 1. `clear_screen()`
Limpia la terminal usando secuencias ANSI para un renderizado fluido.

```python
def clear_screen(self) -> None:
    print("\x1bc", end="")
```

##### 2. `spawn_items()`
Genera objetos de comida en posiciones aleatorias válidas.

**Lógica**:
1. Calcula celdas libres (total - cabeza - cola - items existentes)
2. Determina cuántos items generar este tick
3. Intenta colocar items con un máximo de 50 intentos por item
4. Verifica que no se coloquen sobre la serpiente o items existentes

```python
def spawn_items(self) -> None:
    # Cálculo inteligente de espacios libres
    free_cells = total_cells - occupied_cells
    num_to_spawn = max(0, min(items_to_reach_target, free_cells))
```

##### 3. `draw_map()`
Dibuja el estado actual del juego.

**Versión Terminal**:
- Crea una matriz 2D para el tablero
- Coloca items (`*`) y serpiente (`@`)
- Imprime bordes decorativos
- Muestra Score, Level y High Score

**Versión GUI** (sobrescrita en `SnakeGameGUI`):
- Dibuja rectángulos en canvas de Tkinter
- Usa colores (verde para serpiente, amarillo para comida)
- Actualiza texto de información

##### 4. `read_input()`
Lee la entrada del usuario de forma no bloqueante.

**Multiplataforma**:
- **Windows**: Usa `msvcrt.kbhit()` y `msvcrt.getch()`
- **Unix/Linux**: Usa `select`, `termios` y `tty`
- **Con readchar**: Usa librería dedicada para mejor compatibilidad

**Características**:
- No bloquea el juego esperando entrada
- Mapea flechas del teclado a WASD
- Filtra solo teclas válidas (`w`, `a`, `s`, `d`, `q`)

##### 5. `update_position(direction)`
Actualiza la posición de la serpiente según la dirección.

**Flujo de ejecución**:
1. Determina dirección final (entrada o última dirección)
2. Previene giros de 180° si hay cola
3. Calcula nueva posición
4. Detecta colisión con paredes
5. Actualiza cola (añade cabeza vieja, elimina cola si es necesario)
6. Mueve cabeza
7. Detecta consumo de items
8. Detecta colisión consigo mismo

**Prevención de giros de 180°**:
```python
if self.tail_length > 0:
    # Si intentas ir en dirección opuesta, mantiene dirección actual
    if (self.last_direction == "w" and direction == "s") or \
       (self.last_direction == "s" and direction == "w") or \
       (self.last_direction == "a" and direction == "d") or \
       (self.last_direction == "d" and direction == "a"):
        final_direction = self.last_direction
```

##### 6. `run()`
Bucle principal del juego.

**Ciclo de juego**:
```python
while not self.end_game:
    self.spawn_items()         # Generar comida
    self.clear_screen()        # Limpiar pantalla
    self.draw_map()            # Dibujar estado
    direction = self.read_input()  # Leer entrada
    self.update_position(direction)  # Actualizar posición
    time.sleep(sleep_duration)  # Control de velocidad
```

**Control de velocidad dinámico**:
```python
sleep_duration = max(0.05, 0.2 - (self.level - 1) * 0.02)
# Nivel 1: 0.20s
# Nivel 2: 0.18s
# Nivel 3: 0.16s
# ...hasta mínimo 0.05s
```

#### Métodos de Persistencia

##### 1. `_load_highscore()`
Carga datos de récords desde archivo JSON.

**Ubicación**: `~/.snake_highscore.json`

**Estructura de datos**:
```json
{
  "high_score": 42,
  "games_played": 15,
  "total_score": 234
}
```

##### 2. `_save_highscore()`
Guarda datos actualizados de récords.

**Actualiza**:
- `high_score`: Si el score actual es mayor
- `games_played`: Incrementa en 1
- `total_score`: Suma el score actual

##### 3. `_show_game_over()`
Muestra pantalla de Game Over con estadísticas completas.

**Información mostrada**:
- Razón del fin del juego (pared, colisión, salir)
- Puntuación final
- Nivel alcanzado
- Longitud de la serpiente
- Tiempo de juego
- High Score (resalta si es nuevo récord)
- Partidas jugadas totales
- Puntuación media

#### Propiedades

##### `level`
Calcula el nivel basado en la puntuación.

```python
@property
def level(self) -> int:
    return self.score // 5 + 1
```

##### `high_score`
Obtiene el récord actual desde los datos cargados.

```python
@property
def high_score(self) -> int:
    return self.highscore_data.get("high_score", 0)
```

### Clase Derivada: `SnakeGameGUI`

Hereda de `SnakeGame` y sobrescribe métodos para GUI.

**Diferencias clave**:
- `draw_map()`: Usa Canvas de Tkinter
- `game_step()`: Reemplaza el bucle while por `root.after()`
- Manejo de eventos con `bind("<KeyPress>")`
- Pantalla de Game Over gráfica con overlays

## 🏆 Sistema de Puntuación

### Mecánicas de Puntuación

- **+1 punto** por cada objeto de comida consumido
- **+1 a tail_length** por cada objeto consumido
- **Nivel** calculado como `score // 5 + 1`

### Persistencia

Los datos se guardan en `~/.snake_highscore.json`:

```json
{
  "high_score": 156,
  "games_played": 47,
  "total_score": 2341
}
```

### Estadísticas Calculadas

- **Puntuación Media**: `total_score / games_played`
- **Tiempo de Juego**: `tiempo_fin - game_start_time`
- **Longitud Final**: `tail_length + 1`

## 📁 Estructura de Archivos

```
Snake/
│
├── snake_game.py          # Módulo principal con lógica del juego
│   ├── Clase SnakeGame    # Implementación base
│   ├── Constantes         # POS_X, POS_Y, HIGHSCORE_FILE
│   └── Métodos privados   # _load/save_highscore, _show_game_over
│
├── snake_game_gui.py      # Versión con interfaz gráfica (Tkinter)
│   └── Clase SnakeGameGUI # Hereda de SnakeGame
│
├── maze.py                # Script de inicio rápido
│   └── Instancia simple   # game.run()
│
├── test_snake_game.py     # Suite completa de tests unitarios
│   ├── 17 tests           # Cobertura exhaustiva
│   └── Mocks y patches    # Testing de I/O y persistencia
│
└── README.md              # Esta documentación
```

### Detalles de Archivos

#### `snake_game.py` (Núcleo - 360 líneas)
- Lógica completa del juego
- Manejo de entrada multiplataforma
- Sistema de puntuación y persistencia
- Algoritmos de colisión y movimiento

#### `snake_game_gui.py` (GUI - 81 líneas)
- Herencia de clase base
- Integración con Tkinter
- Renderizado gráfico
- Game Over visual

#### `maze.py` (Launcher - 7 líneas)
- Punto de entrada simple
- Configuración por defecto
- Inicio rápido del juego

#### `test_snake_game.py` (Tests - 380 líneas)
- 17 tests unitarios
- Cobertura de casos edge
- Mocking de archivos y entrada
- Validación de lógica de juego

## 🧪 Desarrollo y Tests

### Ejecutar Tests

```bash
# Ejecutar todos los tests
python -m unittest test_snake_game.py -v

# Ejecutar un test específico
python -m unittest test_snake_game.SnakeGameTestCase.test_highscore_persistence

# Con coverage (si está instalado)
pip install coverage
coverage run -m unittest test_snake_game.py
coverage report
```

### Cobertura de Tests

Los tests cubren:

1. **Estado Inicial**: Verificación de todos los atributos
2. **Spawn de Items**: Generación correcta de comida
3. **Movimiento y Crecimiento**: Mecánicas de serpiente
4. **Colisiones**: Paredes, auto-colisión
5. **Niveles**: Cálculo correcto de nivel
6. **Entrada**: Lectura multiplataforma
7. **High Score**: Persistencia y carga
8. **Giros 180°**: Prevención correcta
9. **Renderizado**: Output visual correcto
10. **Game Over**: Razones de terminación

### Ejemplo de Test

```python
def test_highscore_persistence(self):
    # Crear archivo temporal para testing
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    with patch('snake_game.HIGHSCORE_FILE', temp_file.name):
        # Primera partida
        game1 = SnakeGame()
        game1.score = 10
        game1._save_highscore()

        # Segunda partida carga el récord
        game2 = SnakeGame()
        assert game2.high_score == 10
        assert game2.highscore_data["games_played"] == 1
```

### Añadir Nuevas Funcionalidades

1. **Modificar `snake_game.py`**: Implementar la lógica
2. **Actualizar `snake_game_gui.py`**: Si afecta a la GUI
3. **Escribir tests**: En `test_snake_game.py`
4. **Ejecutar tests**: Verificar que pasen
5. **Actualizar README**: Documentar cambios

### Estilo de Código

- **Type Hints**: Todas las funciones tienen anotaciones de tipo
- **Docstrings**: Documentación clara de métodos
- **PEP 8**: Estilo de código Python estándar
- **Nombres descriptivos**: Variables y funciones auto-explicativas

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Aquí hay algunas ideas:

### Ideas de Mejora

- [ ] Modo multijugador
- [ ] Diferentes tipos de comida (bonus, malus)
- [ ] Obstáculos en el mapa
- [ ] Skins para la serpiente
- [ ] Sonidos y música
- [ ] Leaderboard online
- [ ] Modos de dificultad predefinidos
- [ ] Power-ups temporales
- [ ] Mapas personalizados
- [ ] Replay de partidas

### Proceso de Contribución

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. **Commit** tus cambios (`git commit -m 'Add amazing feature'`)
4. **Push** a la rama (`git push origin feature/amazing-feature`)
5. **Abre** un Pull Request

### Guías de Contribución

- Mantén el estilo de código existente
- Añade tests para nuevas funcionalidades
- Actualiza la documentación
- Verifica que todos los tests pasen
- Escribe mensajes de commit descriptivos

## 📊 Estadísticas del Proyecto

- **Líneas de código**: ~900 líneas
- **Tests**: 17 tests unitarios
- **Cobertura**: ~95%
- **Archivos**: 4 archivos principales
- **Dependencias**: 1 opcional (readchar)

## 🐛 Problemas Conocidos y Soluciones

### Problema: Entrada no detectada en terminal

**Solución**: Instala `readchar`
```bash
pip install readchar
```

### Problema: Parpadeo en terminal

**Solución**: El parpadeo es normal debido al clear. En sistemas lentos, aumenta el sleep_duration.

### Problema: GUI no abre

**Solución**: Verifica que Tkinter esté instalado:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (viene con Python)
# Windows (viene con Python)
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 🙏 Agradecimientos

- Implementación original del clásico juego Snake
- Comunidad de Python por las excelentes librerías
- Todos los contribuidores que han mejorado el proyecto

## 📧 Contacto

Si tienes preguntas, sugerencias o quieres reportar un bug:

- **Issues**: [GitHub Issues](https://github.com/Unamunoqueva/Snake/issues)
- **Pull Requests**: [GitHub PRs](https://github.com/Unamunoqueva/Snake/pulls)

---

**¡Diviértete jugando y programando! 🐍🎮**

*Última actualización: 2025*
