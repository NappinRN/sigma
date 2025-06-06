# Pinball Game

This repository contains a simple pinball game built with **Pygame**. The game is cross-platform and can be run on macOS with Python 3.

## How to Run on macOS

1. **Install Python 3**
   - If you use Homebrew:
     ```sh
     brew install python3
     ```
2. **Install dependencies**
   - Install Pygame via pip:
     ```sh
     pip3 install -r requirements.txt
     ```
3. **Run the game**
   ```sh
   python3 pinball.py
   ```
4. **Controls**
   - Left flipper: `A` key or Left Arrow
   - Right flipper: `D` key or Right Arrow

## Packaging as a macOS App

If you want to create a standalone macOS application you can use `py2app` or `PyInstaller`:

```sh
pip3 install py2app  # or pyinstaller
python3 setup.py py2app  # with a setup.py configuration
```

This will generate a `.app` bundle that you can open like any other macOS app.

