> ⚠️ **Work in Progress**  
> This project is currently under active development. Features, structure and documentation may change frequently.

# 2D Grid Game  

This repository contains the **initial plan** for a 2D board game project.  
The goal is to build a modular, testable, and documented game using Python with asynchronous, multithreaded, and multiprocessing features.  

---

## 📝 Project Overview  

The project will be a simple **2D board game** running on a grid.  
It will feature:  

- **Player movement** on a board.  
- **Random item spawning** and collection.  
- **Opponents** moving independently using:
  - asyncio (asynchronous)
  - multithreading
  - multiprocessing  
- **Collision detection** between player, items, and opponents.  

---

## 🏗 Planned Architecture  

The game will be split into multiple modules inside the `game` folder:  

- `core/` – main game logic (player, opponents, utils, game loop).  
- `tests/` – unit and integration tests written with pytest.  
- `docs/` – auto-generated documentation using pdoc.  
- `requirements.txt` – dependencies list.  

---

## 🔄 Continuous Integration / Linting  

This project will include a simple GitHub Actions workflow to automatically run code linters and style checks on every push and pull request.  
The goal is to maintain consistent code quality and catch issues early before merging changes.

---

## ✅ Planned Features  

- Player moves using keyboard input.  
- Items spawn randomly and increase player life when collected.  
- Opponents move independently based on selected concurrency mode.  
- Reset, cleanup, and mode switching logic.  
- Fully tested with `pytest`.  
- Automatically generated HTML docs with `pdoc`.  

---

## 🖼 Screenshots  

*(I’ll add screenshots here once the UI is ready.)*  

