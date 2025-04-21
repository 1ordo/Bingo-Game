/*
 * Bingo Game - Arduino Uno Bridge
 * This script serves as a bridge between the Arduino Mega (physical board) 
 * and the Python/Pygame game interface
 */

// Constants
#define BAUD_RATE 9600
#define MEGA_RX 10
#define MEGA_TX 11

#include <SoftwareSerial.h>

// Setup software serial for communication with Mega
SoftwareSerial megaSerial(MEGA_RX, MEGA_TX); // RX, TX

// Variables to track game state
char lastBall = ' ';
bool gameActive = false;
unsigned long lastCommandTime = 0;
const unsigned long COMMAND_DEBOUNCE_TIME = 500; // 500ms debounce for commands

void setup() {
  // Initialize serial communications
  Serial.begin(BAUD_RATE);     // USB connection to computer
  megaSerial.begin(BAUD_RATE); // Connection to Arduino Mega
  
  // Startup message
  Serial.println("BINGO_BRIDGE_READY");
}

void loop() {
  // Check for messages from the computer
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Pass commands to the Mega
    megaSerial.write(command);
    
    // Process specific commands locally if needed
    unsigned long currentTime = millis();
    if (currentTime - lastCommandTime >= COMMAND_DEBOUNCE_TIME) {
      lastCommandTime = currentTime;
      
      switch(command) {
        case 'N': // New game
          gameActive = true;
          Serial.println("GAME_STARTED");
          break;
        case 'E': // End game
          gameActive = false;
          Serial.println("GAME_ENDED");
          break;
        case 'D': // Draw ball - send lift ball command to Mega
          if (gameActive) {
            // Send lift ball command to Mega
            megaSerial.write('l');
            Serial.println("BALL_REQUESTED");
          } else {
            Serial.println("GAME_NOT_ACTIVE");
          }
          break;
      }
    }
  }
  
  // Check for messages from the Mega
  if (megaSerial.available() > 0) {
    char message = megaSerial.read();
    
    // Forward to computer
    Serial.write(message);
    
    // Process specific messages if needed
    if (message >= 'A' && message <= 'Y') {
      lastBall = message;
      // Send formatted ball data to the computer
      Serial.print("BALL:");
      Serial.println(message);
    }
    
    // Ball through gate message
    if (message == 'z') {
      Serial.println("BALL_RELEASED");
    }
    
    // Ball returned message
    if (message == 'Z') {
      Serial.println("BALL_RETURNED");
    }
  }
  
  // Add a small delay to prevent overwhelming the serial buffers
  delay(10);
}

// Helper function to send formatted messages to the computer
void sendMessage(const char* type, const char* value) {
  Serial.print(type);
  Serial.print(":");
  Serial.println(value);
}