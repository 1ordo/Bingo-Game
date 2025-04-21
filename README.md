# Belgian Bingo Game

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![Arduino](https://img.shields.io/badge/Arduino-Compatible-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

A digital bingo game that interfaces with Arduino hardware for a physical/digital hybrid bingo experience. This project combines software and hardware to create an engaging bingo game system with physical ball manipulation and digital tracking.

![Belgian Bingo Game](assets/images/logo.png)

## Features

- 5x5 Belgian bingo card layout with dynamic generation
- Ball drawing system that works with physical Arduino components
- Sound effects and background music
- Score tracking and win detection
- Multiple winning patterns
- Interactive UI optimized for vertical display
- Fallback simulation mode when hardware is not available

## Project Structure

```
├── main.py                  # Main game file
├── settings.json            # Game configuration
├── requirements.txt         # Python dependencies
├── Arduino_scripts/         # Arduino code
│   ├── Mega.ino             # Code for Arduino Mega (physical components)
│   └── uno.ino              # Code for Arduino Uno (bridge)
└── assets/                  # Game assets
    ├── fonts/               # Game fonts 
    ├── images/              # Game images and sprites
    └── sounds/              # Game audio files
```

## Requirements

- Python 3.6 or higher
- Pygame
- PySerial
- Arduino Uno (connected to computer)
- Arduino Mega (connected to physical bingo components)

## Hardware Setup

1. Connect the Arduino Uno to your computer via USB
   - This Uno acts as the bridge between your computer and the Mega
   - If the Uno is not connected, the game will run in simulation mode

2. Connect the Arduino Mega to the physical bingo components as described in the documentation
   - The Mega controls all the physical elements (ball lift, shutter, etc.)

3. Connect the Arduino Uno and Mega together:
   - Uno RX (pin 10) → Mega TX
   - Uno TX (pin 11) → Mega RX
   - Connect GND between both Arduinos (common ground)

### Communication Protocol

The game communicates with the Arduino hardware using simple commands:

- **N**: Start a new game
- **E**: End the current game
- **D**: Draw a new ball

This simple protocol allows for reliable communication between the software and hardware components.

### Connection Diagram

```
Computer <--USB--> Arduino Uno <--Serial--> Arduino Mega <---> Physical Components
```

## Software Setup

1. Clone this repository:
   ```
   git clone https://github.com/1ordo/bingo-game.git
   cd bingo-game
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Upload the Arduino code:
   - Upload the `Arduino_scripts/uno.ino` script to the Arduino Uno
   - Upload the `Arduino_scripts/Mega.ino` script to the Arduino Mega

5. Configure the `settings.json` file with the correct serial port for your Arduino Uno or enable auto-detection

## Running the Game

Start the game by running:
```
python main.py
```

### Finding Your Arduino Serial Port

- On macOS: `/dev/tty.usbmodem*` or `/dev/tty.usbserial*`
- On Windows: `COM*` (ex: COM3, COM4)
- On Linux: `/dev/ttyACM*` or `/dev/ttyUSB*`

## Fallback Mode

If the Arduino hardware is not properly connected, the game will automatically switch to fallback (simulation) mode:

- You'll see "SIMULATION MODE (No Hardware)" in the top-right corner of the screen
- Ball drawing will be simulated by the game itself
- All game features will work without the physical components

## Game Controls

- **Space**: Draw a new ball (manual mode)
- **ESC**: Return to main menu
- **Arrow Keys**: Navigate menus
- **Enter**: Select menu option

## Settings

The game can be configured through the Settings menu:

- **Serial Settings**: Configure Arduino connection settings including auto-detection
- **Display Settings**: Adjust screen resolution and fullscreen settings
- **Audio Settings**: Control music and sound effects volume
- **Game Settings**: Set ball draw delay and winning pattern

## How to Play

1. Launch the game
2. Select "New Game" from the main menu
3. A new bingo card will be generated
4. Balls will be automatically drawn at regular intervals
5. Match the numbers on your card with the drawn balls
6. Get 5 in a row (horizontally, vertically, or diagonally) to win!

## Development and Contributing

This project is under active development with plans for enhanced animations and UI improvements. See the [CHANGELOG](CHANGELOG.md) for version history and planned features.

Contributions are welcome! Please check our [Contributing Guide](CONTRIBUTING.md) for guidelines on how to make contributions.

For bug reports and feature requests, please use the issue templates provided in the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Bally Bingo simulation software inspiration: Joop Riem
- Playfield hardware assistance: Liphook team
- Sound effects: Various creative commons sources