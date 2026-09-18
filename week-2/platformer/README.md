# Week 2 — Platformer Level

A simple 2D platformer prototype built with **Python + Pygame**.

## Objective

Navigate the level, use moving platforms, collect every coin, and avoid the patrolling enemy. Contact with the enemy costs one life.

## Features

- Left/right player movement
- Jumping and gravity
- Static and horizontally moving platforms
- 7 collectible coins
- Enemy patrols back and forth
- Player starts with 3 lives
- Enemy contact costs one life and respawns the player
- Falling off the level also costs one life
- Level completion after collecting all coins
- Restart with **R**
- No external art assets required

## Run

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Controls

| Action | Key |
|---|---|
| Move | A/D or Left/Right |
| Jump | W / Up / Space |
| Restart after win/game over | R |

## Structure

```text
week-2/platformer/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```
