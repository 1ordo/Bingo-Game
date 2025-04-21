# Bally Bingo Simulation with a Real Playfield

## 🎉 Thanks and Acknowledgements

- **Joop Riem** – Bally Bingo simulation software ([Visit Site](http://www.bingo.joopriem.nl))
- **The Liphook team** – For help, parts, and advice
- **Ian** – For testing, feedback, and patience
- **Chris** – For the Playfield overlay
- **And everyone else**, especially my wife for all the cups of tea ☕️

---

## 🎯 1. Aim

Recreate the magic of original **BALLY BINGO** games without needing to maintain or repair the complex electro-mechanical systems.

---

## ⚙️ 1.1 How This Is Achieved

By using the **software simulation from Joop Riem** and attaching it to a **real Bally Bingo playfield**, we bring authentic gameplay to life. Please consider supporting:

- Joop’s website via donation
- The Arduino community

> The software provided is **open-source**—feel free to improve it!

---

## 📚 2. Background

Inspired by Joop Riem’s simulation and his documentation, this project integrates a real playfield into the virtual simulation. After trial and error, a solid software version was developed—emulating behavior close to the original (e.g., ball gates, shutters, and lift mechanics).

---

## 🛠️ 3. Skills Required

To build this project, you’ll need basic skills in:

- **Electronics** – Wiring and soldering
- **Software** – Installing and running programs
- **Arduino** – Uploading code and wiring to components
- **Mechanical Assembly** – For motor and cabinet fitting

---

## 🏗️ 4. Building the Simulation with Real Hardware

You’ll need:
- A **Bally Bingo playfield**
- Optional: a custom-built cabinet (requires ball lift mechanism, cover, and shooter)

---

## 🔌 4.1 Power & Wiring

- Use a **12V DC PSU** (safer than the original 50V)
- **Arduino powered via USB**
- **Motors require external 12V**
- **LEDs run on 5V from Arduino**

**Notes:**
- Use good-quality wiring and grounding.
- Old leaf switches may cause issues—replace where needed.
- Keep motor and control circuits separate to avoid interference.

---

## 💡 4.2 Helpful Hints

- Set up a **no-password login** on a dedicated PC for auto-launch
- Connect lights using a **5V distribution block**
- Use **new switches** for Ball Gate and Ball Return

---

## 🤖 5. Microprocessor Setup

This build uses the **Arduino MEGA 2560**. Get started:

1. Install the [Arduino IDE](https://www.arduino.cc/en/software)
2. Set board to **MEGA 2560**
3. Set the correct **COM port**
4. Load the custom **BALLY BINGO sketch**

---

### 🔧 Basic Test Setup (Parts)

- MEGA 2560
- USB cable
- Keyes MOSFET Modules (x2)
- LEDs
- 5V output from MEGA
- Relay modules (dual 5V)
- Arduino software
- Test Sketch

---

### 📌 Pin Assignments
```cpp
#define Yellowlamp 4
#define BallinLane A0
#define Shutteropen 50
#define Shutterclosed 51
#define LiftballRelay 52
#define ShutterRelay 53
