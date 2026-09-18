# Week 1 — Catch the Falling Objects

A simple 2D game built with **Python + Pygame** for the Week 1 mini project.

## Objective

Catch objects falling from the top of the screen by moving the player left and right. Each successful catch increases the score. Missing 5 objects ends the game.

## Features

- Player movement with **Left/Right arrow keys** or **A/D**
- Random falling objects with different colors and speeds
- Collision detection between the player and falling objects
- On-screen score counter
- Miss counter and game-over state
- Press **R** to restart after game over
- Difficulty gradually increases as the score grows
- No external art assets required

## Run locally

### 1. Create and activate a virtual environment

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the game

```bash
python main.py
```

## Controls

| Action | Key |
|---|---|
| Move left | Left Arrow / A |
| Move right | Right Arrow / D |
| Restart | R |

## Project structure

```text
catch-the-falling-objects/
├── main.py
├── requirements.txt
└── README.md
```
