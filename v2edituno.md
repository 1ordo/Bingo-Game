Here's the markdown version of the content you provided, formatted appropriately:

# Bally Bingo Simulation with a Real Playfield

Thanks and acknowledgements to:
- Joop Reim – Bally Bingo simulation software
- The guys at Liphook - for help, parts, and advice
- Ian – for testing and feedback (and lots of patience)
- Chris for my Playfield overlay
- And anybody else including my wife for cups of tea

## 1. Aim

To recreate those wonderful BALLY BINGO games without having to fix/repair all that complex electro-mechanical stuff.

### 1.1 How to achieve my Aim

Use the software simulation by Joop Reim (see www.bingo.joopriem.nl) and add a real Bally Bingo playfield to provide the experience of a real Bally Bingo machine.  
Please help the Forum’s by making a small donation to Joop’s site and the ARDUINO’s site, the software I provide is open source so feel free to have a go at making it better.

## 2. Background

After seeing and downloading JR's excellent simulation of those great Bally Bingo machines, I decided to take it one stage further and add a real playfield. JR kindly has provided a manual (see above site) describing the interface to his simulations. So started the project, after a couple of false starts with my software, we finally ended with a usable software load, not behaving exactly like the real thing but close enough. We will keep updating it to get it perfect. (For those interested in what’s missing, it’s the ball-through gate logic which closes the shutter after delivering the first ball).

## 3. Building a Bally Bingo with JR simulation and a Real Playfield

The first thing you will need is a Bally Bingo playfield with the shutter and a cabinet, or you could build a cabinet yourself. If you do go down the build-a-cabinet route, you will need the following parts:
- Ball lift mechanism
- Ball lift cover
- Shooter

I found these quite hard to find, therefore I waited till I acquired a Bally Bumper from 1936 as my cabinet. Interestingly, the Bingo playfield fit perfectly. The first thing to do is to remove all the EM stuff as we will be using modern low-voltage motors for ball lift and shutter control. If the wiring to the playfield is okay, there’s no need to rewire.

### 3.1 Power & Wiring

The power for this conversion uses one 6V PSU and one 12V PSU. I chose this route rather than using the existing PSU and 50V AC because these are old machines and I didn’t fancy touching 50V AC. The ARDUINO would normally be powered from the computer USB; however, for the motor drive ARDUINO, you need an external 12V DC supply. For the lights, I again used a 6V DC supply, as I used LEDs so no need for high wattage. This also allowed me to use ARDUINO / RASPBERRY wires. If you plan to use original bulbs, make sure to check the power requirements and wire accordingly or use original wiring. Be sure all wiring is in good condition, as these microprocessors run on 5V and draw very little current, so any bad contacts may cause intermittent issues.

### 3.2 Microprocessors

As suggested by JR, this solution uses the ARDUINO micro (a great piece of kit). We will be using two: one for motor control and the other to handle switches and buttons. I used two because it proved to be an easy way forward. It should be noted for those not familiar with ARDUINOs, there are many sketches (programs) available at [Arduino Forum](https://forum.arduino.cc/) which you can try. It’s good fun!

## 4. Getting Started

See the list of parts below, but we will start with the ARDUINOs. If you are not familiar with ARDUINOs, go to the ARDUINO website for help and guidance; there’s some great stuff there.

### 4.1 Simple Stuff

A good starting point is to get used to loading and testing even if you have experience. This will check out the boards and switching. Load up the UNO with the test harness to check the Rollover lights and drivers.  
Parts needed: All of these are needed for the final build, so these aren’t wasted parts.
- UNO
- USB lead
- 2 x Keyes MOSFET Modules for Rollover Lights
- Optional light
- 6V DC PSU
- Power distribution block
- ARDUINO software environment
- `UNO_Rollover_test.ino`

The test here is very simple and will get you up and running. You will see how I configure pins, etc. The following code assigns A4 and A5 to the rollover lights. You need to connect the signal and earth from the MOSFET boards to earth and pins A4 and A5, as shown below. Test by using the monitor facility under ‘Tools’ and input 4 or 5 and 6 or 7 to switch on/off the lights.

```cpp
#define Yellowlamp A4
#define Redlamp A5
```

NOTE: I use a power distribution board to provide each MOSFET with power from a single 6V PSU. On the playfield, connect to the lights 6V rails.

### 4.2 Getting the System Up and Running

I suggest using the UNO + Adafruit shield and the 2 motors loaded with the UNO sketch. Make sure you have set up for an UNO (you will need to change the 'Board' when loading for MEGA).  
NOTE: You must have a 12V supply connected before you try out the motors and sketches, and have the VIN jumper installed. Use a USB lead to connect to your PC, as the motors take more current than the USB can supply.  
It should look like the screenshot below. Use the tools button to get the serial monitor window, and with the 'h', 'l', and 'i' commands, you should be able to drive the motors correctly before installing them.

### 4.3 Loading the MEGA

Next, load up the MEGA and disconnect the communication link between the MEGA and UNO for now (i.e., TX3 on MEGA and pin 0 on the UNO).  
Once the MEGA is loaded, the fun begins. Load one of JR’s simulations (I tend to use ShowTime). Start the game, ensuring the use remote interface is set with your serial communications port (see JR’s manual for help).  
If connected properly, the backglass will appear and be tilted, indicating a successful connection between JR’s simulation and the playfield system. You can actually test the system further by playing a game before installing it into your BALLY BINGO machine.  
Use a shorting lead from any ‘GND’ to pin A8 to start the game. The buttons are as follows:
- Red button A8
- Yellow button A9
- A button A10 to F button A15

Pins 22 to 47 are the BALLY HOLE numbers, shorting them will light the correct number on the backglass. Be very careful not to touch any 5V pins as this could damage the MEGA.

## 5. Ball Return Switch and Ball Lift Motor Switch

You will need a ball return switch for the system to operate correctly and a ball lift switch (as seen in Ian’s configurations). The motor stop switch is shown in the second photo at the bottom right; as the motor rotates, the arm opens and closes the switch. Adjust the position of the operating rod to suit the ball lifter's default position.

### 5.1 Mounting and Connecting ARDUINOs

There are two options for mounting the ARDUINOs: one is to use the lower region of the cabinet as per Ian’s configurations or mount them underneath the playfield (which is what I did, as I wanted to change playfields for my BALLY BUMPER).

Here is Ian’s configuration using existing wiring:

[Image: Ian's configuration]

Here is mine with ARDUINO mounted under the playfield and new wiring:

[Image: My configuration]

### 5.2 BALLY BINGO Buttons

There are several options for the button setup:
- Ian created a new button bar with simple switches and placed the Red, Yellow, White, and Green buttons on the front of the cabinet.
- I used an Xkeys programmable box, which is directly connected to JR’s simulation and doesn’t require changes to the cabinet.

Here is my Xkeys Box:

[Image: Xkeys box]

## Basic Kit of Parts

- ARDUINO MEGA 2560
- ARDUINO UNO
- Plywood board to mount ARDUINO and connections
- Adafruit motor shield v2.3
- UNO screw shield
- Adafruit 12V NEMA 17 stepper motor
- Adafruit NEMA 17 stepper motor bracket for shutter board
- Geared 12V DC hi-torque motor plus bracket (may need to make it)
- 1 ball return switch (leaf switch)
- 1 motor stop switch (can use the switch at the bottom of the ball lift)
- 2 Keyes MOSFET Modules for Rollover Lights
- Male to Male jumpers (approx 40)
- Male to Female jumpers (approx 6)
- Terminal blocks to connect playfield wiring to ARDUINOs
- Power distribution block
- 12V DC PSU to power motors (1A ideal)
- 6V PSU to power lights (wattage depends on bulb type)
- PC or laptop to host JR simulation
- Monitor to display backglass (16x9 or 5x4)

**Note**: The above should cost less than $100 (excluding the PC and monitor, assuming you already have them).

Not forgetting a BALLY BINGO donor cabinet, JR’s software, and my ARDUINO sketches for the UNO and MEGA.
