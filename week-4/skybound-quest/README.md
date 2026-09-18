# Week 4 — Skybound Quest

A complete 2D game prototype built with **Python + Pygame**, designed around the Week 4 major-project requirements.

## Features

- **3 complete levels** with increasing enemy counts and level-specific scenery.
- **Enemies** that patrol back and forth.
- **Power-ups**
  - Shield: absorbs one enemy hit.
  - Speed: temporarily increases movement speed.
- **Lives system:** 3 lives; enemy contact or falling costs a life.
- **High-score saving:** best score is persisted locally in `highscore.json`.
- **Sound effects:** coin, power-up, hit, and finish sounds are synthesized at runtime, so no binary audio assets are required.
- **Polished UI:** level name, lives, score, high score, power status, instructions, win/game-over screens, and restart flow.
- **Progression:** reach the finish door to advance through all three levels.
- **No external art/audio dependencies.**

## Controls

| Action | Keys |
|---|---|
| Move | A/D or Left/Right |
| Jump | W / Up / Space |
| Restart | R after win/game over |

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

## APK / Play Store packaging

The repository includes an Android packaging configuration under `android/`. Because an APK must be compiled with a local Android SDK/NDK toolchain, this repository contains the reproducible build configuration rather than claiming a binary APK has been generated remotely.

Install the required Android tooling and run:

```bash
cd android
./gradlew assembleRelease
```

On Windows PowerShell:

```powershell
cd android
.\gradlew.bat assembleRelease
```

The resulting release APK will be under `android/app/build/outputs/apk/release/`.

For Play Store upload, use an Android App Bundle (`.aab`) and sign it with your release/upload key:

```bash
./gradlew bundleRelease
```

The build configuration targets a modern Android SDK and packages the Python/Pygame game using Chaquopy. Review and replace the placeholder release signing configuration before publishing.
