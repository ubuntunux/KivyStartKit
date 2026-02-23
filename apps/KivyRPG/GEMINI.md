# KivyRPG

This is a Kivy-powered RPG game.

## Project Overview

The project is a 2D RPG game built with the Kivy framework in Python. It features a tile-based map, a variety of characters (player, NPCs, enemies), and a simple combat system. The game also includes a day/night cycle, a basic inventory system, and a trade system.

### Architecture

The game follows a simple entity-component-system (ECS) like architecture. The main components are:

*   **`main.py`**: The entry point of the application. It initializes the Kivy app and the game managers.
*   **`game/game_manager.py`**: The core of the game logic. It manages the game state, the main game loop, and actor spawning.
*   **`game/level.py`**: Manages the game level, including the tile map, character and effect layers, and the day/night cycle.
*   **`game/actor.py`**: Manages all actors in the game, including the player, NPCs, and enemies. It handles actor creation, removal, and updates.
*   **`game/game_controller.py`**: Manages the game's UI and handles user interactions.
*   **`game/game_resource.py`**: Manages loading and storing all game data, including character, tile, weapon, and level data.

### Data Files

The game uses `.data` files to store game data. These files are simple Python dictionaries that are read using `eval()`.

*   `data/characters/`: Contains data for different character types.
*   `data/levels/`: Contains data for game levels.
*   `data/tiles/`: Contains data for tile sets.
*   `data/weapons/`: Contains data for weapons.

## Building and Running

To run the game, you need to have Python and Kivy installed.

```bash
pip install kivy==2.2.1
python main.py
```

## Development Conventions

The code follows a simple object-oriented programming style. Most of the core game logic is encapsulated in manager classes that are implemented as singletons.

### TODO

*   The `README.md` is very brief. It would be beneficial to add more information about the project, including a more detailed description of the gameplay and features.
*   The use of `eval()` to read data files is a security risk. It would be better to use a safer data serialization format like JSON or YAML.
*   The project could benefit from more comments and documentation to make it easier for new developers to understand the code.
