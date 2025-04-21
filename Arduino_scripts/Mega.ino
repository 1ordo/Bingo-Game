/*
  || @version 2.0
  ||
  || This program is only for use with BALLY Bingo simulation by Joop available on
  || http://www.bingo.joopriem.nl/
  || NOTE - Please check wiring is compliant with this build NOT compatable
  || with previous versions
  || 
  || Due to the current drawn(approx 2 amps) by motors;
  || a seperate 12 volt 30 watt must be used
  || fine tune motor speed by adjusting voltage - NOT above 12.5v
  || relays will chatter if to high
  || Simplfied Ball tho Gate logic
  || External Xkeys Keypad compliment orginal buttons on cabinet
*/
//
// Pin mapping
#define BTGpin  2                         // connect to gate switch
// Lamps
#define Yellowlamp 4 
#define Redlamp 5                
//Inputs
#define Whitebutton 6
#define Bluebutton 7
#define Greenbutton 8
#define Rbutton 9
#define Tilt 10
#define Rotateright 11
#define Rotateleft 12
#define LED 13
//
#define BallinLane A0
#define Ballreturn A1
#define Redrollover A2
#define Yellowrollover A3
#define Liftballbutton A4
//
#define Credits A7
#define Redbutton A8
#define Yellowbutton A9
#define Abutton A10
#define Bbutton A11
#define Cbutton A12
#define Dbutton A13
#define Ebutton A14
#define Fbutton A15
// 
#define Orangebutton 48
#define Shutteropen 50
#define Shutterclosed 51
#define LiftballRelay 52
#define ShutterRelay 53
//     
// Table containing numbered hole codes for Joop's simulation
char Ballcodes [26] =
{ ' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
  'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'
};
// These variables are for the Ball Thro Gate code      
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;       // last time was updated
const unsigned debounceTime = 500;      // leaf switch bounce time (milliseconds)
// End of BTG variables
char ch;                                // from Backglass simulation
int BallsinPocket [26];                 // slots 0 and 26 are not used
// NOTE - some of these variables are not used- they are for ODD/EVEN games due
// to be released next                      
int BIP;                         // Ball in pocketcount - # of balls in pockets
int currentball  = 0;            // number of ball that have passed thro gate
                                 // onto the playfield (-1 for every returned ball)
int returned = 0;                // returned balls                                                              
int YellRO = 0;                  // set to 1 if on
int RedRO  = 0;                  // set to 1 if on
// 
// 
void setup()
{
  Serial.begin  (9600);                  // <-> BALLY BINGO simulation
// set up Ball Thro Gate Interrupt
   pinMode(BTGpin,INPUT_PULLUP);         // Ball Thro Gate Switch
   attachInterrupt(digitalPinToInterrupt(BTGpin), BTG,RISING);
//
// Input Pins
  pinMode(Yellowrollover, INPUT_PULLUP); // YELLOW rollover
  pinMode(Redrollover, INPUT_PULLUP);    // RED rollover
  pinMode(Whitebutton, INPUT_PULLUP);    // White
  pinMode(Bluebutton, INPUT_PULLUP);     // Blue
  pinMode(Greenbutton, INPUT_PULLUP);    // Green
  pinMode(Rbutton, INPUT_PULLUP);        // R Button
  pinMode(Tilt, INPUT_PULLUP);           // tilt
  pinMode(Rotateright, INPUT_PULLUP);    // rotate >
  pinMode(Rotateleft, INPUT_PULLUP);     // rotate <
  pinMode(Orangebutton, INPUT_PULLUP);   // Small Orange Button
  pinMode(Ballreturn , INPUT_PULLUP);    // Ball return
  pinMode(Liftballbutton,INPUT_PULLUP);  // Lift Ball button
  pinMode(Credits, INPUT_PULLUP);        // 10 Credits awarded
  pinMode(Redbutton, INPUT_PULLUP);      // Red New Game Button
  pinMode(Yellowbutton, INPUT_PULLUP);   // Yellow Extra Ball Button
  pinMode(Abutton, INPUT_PULLUP);        // A Button
  pinMode(Bbutton, INPUT_PULLUP);        // B Button
  pinMode(Cbutton, INPUT_PULLUP);        // C Button
  pinMode(Dbutton, INPUT_PULLUP);        // D Button
  pinMode(Ebutton, INPUT_PULLUP);        // E Button
  pinMode(Fbutton, INPUT_PULLUP);        // F Button
  pinMode(BallinLane,INPUT_PULLUP);      // ball in shooter lane
// Shutter pin
  pinMode(Shutteropen ,INPUT_PULLUP); 
  pinMode(Shutterclosed,INPUT_PULLUP); 
//
// Output Pins 
  pinMode (LED,OUTPUT);
  pinMode(Yellowlamp,OUTPUT); 
  pinMode(Redlamp,OUTPUT);
  digitalWrite (LED,LOW); 
  digitalWrite(Yellowlamp, LOW);
  digitalWrite(Redlamp, LOW);
//
// Setup Relays
 pinMode (LiftballRelay, OUTPUT);
 pinMode (ShutterRelay, OUTPUT);
 digitalWrite(ShutterRelay, LOW);      // reset SHUTTER relay
 digitalWrite(LiftballRelay, LOW);     // reset LIFTBALL relay
//
BIP = 0;                               // Reset balls in pocket - countains the
                                       // number of balls currently in pockets
currentball = 0;                       // number times ball goes thro the gate 
returned = 0;                          // returned balls    
  
//          
YellRO = 0;                            // set to 1 if on
RedRO  = 0;                            // set to 1 if on                                       
// Setup numbers 1 to 25 on pins 22 to 47 inclusive;
  for (int i = 22; i <= 47; i++)
   {
     pinMode( i, INPUT_PULLUP);
   }
}
// end of setup
//

void waiton (char pin)
// this function is entered every time a button is held down  
// and exits when button is released.
// Easy way to stop switch bounce on old leaf switches.
{
  while (digitalRead(pin) == LOW )
  {
    delay (debounceTime);
  }
  Serial.println ('^');
}// end of waiton
//
void laneclear()
// Part of checks for a ball left in lane from 
// previous game. Will not close shutter until all balls 
// returned to ball chute, either via numbered hole or ball return.
// At present only caters for one ball in shooter lane, extra check 
// could use switch in ball chute as per real game !!
{
 int allballsreleased;
 if (digitalRead(BallinLane) == LOW)
 {
 // now wait until ball is thro a numbered hole 
 // or ball return   
  allballsreleased = false;  
  while (allballsreleased == false)
  {
  // check if ball has gone in numbered hole or Return
    for (int i = 22; i <= 47; i++)
     {
      if (digitalRead(i) == LOW)allballsreleased = true;
      if (digitalRead(Ballreturn) == LOW)allballsreleased = true;
     }
    }
    delay (500);                         //let balls drop 
   } 
  }
//
void reset ()
// This function is entered every time 
// the variables need resetting eg new game
{
   digitalWrite(Yellowlamp, LOW);
   digitalWrite(Redlamp, LOW); 
   digitalWrite (LED,LOW); 
// end of shutter positioning
// switch off relays
   digitalWrite(ShutterRelay, LOW); 
   digitalWrite(LiftballRelay, LOW);   
   currentMillis = 0;
   previousMillis = 0;                 // last time was update
   BIP = 0;                            // countains the number of balls
                                       // currently in pockets
   currentball = 0;                    // number times ball goes thro the gate 
   returned = 0;                       // returned balls    
//                                 
   YellRO = 0;                         // set to 1 if on
   RedRO  = 0;                         // set to 1 if on    
//
// clear numbers stored in pockets
   for ( int i = 1; i < 26; i++)
     {
      BallsinPocket [i] = 0;
     }
} // end of reset
//
void loop()
{  
// Process any inputs from Backglass
  if (Serial.available() > 0)
   {
    ch = Serial.read();
// does backglass want an identification
    if (ch == '?') 
     {
// tell backglass its a real playfield
      Serial.print("{BingoPlayfield}");
     }                       
// check for open shutter command
 if (ch == 'h')
 {   
// open shutter
   digitalWrite(ShutterRelay, HIGH);
// let motor run until shutter is open  
   while (digitalRead(Shutteropen) == HIGH)
    {
     delay(50);
    } 
   digitalWrite(ShutterRelay, LOW); 
// shutter now open     
// check to ensure all balls are in ball trough
// at start of game
   laneclear(); 
   delay (1000);                  // let balls drop
   reset();
 }  
// 
// close shutter command from backglass 
  if (ch == 'i') 
   {
     digitalWrite(ShutterRelay, HIGH);
// now stop motor in closed position
  while (digitalRead(Shutterclosed) == HIGH)
    {
     delay (50);
    }
     digitalWrite(ShutterRelay, LOW); 
   }                   
//
// backglass has sent a lift ball command
    if (ch == 'l')
    {  
      digitalWrite(LiftballRelay,HIGH);
      digitalWrite (LED,HIGH); 
    }
//
// Check backglass command
// for Yellow and Red lights ON or OFF
   if (ch == '4' )digitalWrite(Redlamp, LOW ); RedRO=LOW;
   if (ch == '5' )digitalWrite(Redlamp, HIGH ); RedRO=HIGH;
   if (ch == '6' )digitalWrite(Yellowlamp, LOW); YellRO=LOW;
   if (ch == '7' )digitalWrite(Yellowlamp, HIGH); YellRO=HIGH;
}// end of backglass controlled stuff
// 
//Check input from Playfield
//
  if (digitalRead(BallinLane) == LOW ) 
// Switch Ball Lift motor off
   {
     digitalWrite(LiftballRelay, LOW); // stop ball lift motor 
     digitalWrite (LED,LOW); 
   }  
// end of Lift ball Motor 
//
// check for ball over YELLOW rollover
  if ((digitalRead(Yellowrollover) == LOW) && (YellRO == HIGH ))
  {
    Serial.print ('8');
    waiton(Yellowrollover);         // wait for button release
  }
  // check for ball over RED rollover
  if ((digitalRead(Redrollover) == LOW)&& (RedRO == HIGH))
  {
    Serial.print ('9');
    waiton(Redrollover);             // wait for button release
  }
 // Check for small Orange button
    if (digitalRead(Orangebutton) == LOW)
     {
      Serial.print ('g');
      waiton (Orangebutton);         // wait for button release
     }
 // Check for Ball in Return Pocket
  if (digitalRead(Ballreturn) == LOW)
   {
     Serial.print ('Z');   
     waiton (Ballreturn); 
     ++returned;
   }
 // Lift Ball Button
 // Only valid if no ball is in the shooter lane
 // ie motor has failed to raise ball
  if ((digitalRead(Liftballbutton) == LOW)&&(digitalRead(BallinLane) == HIGH))
  {    
    if (BIP <5 )Serial.print ('.');
      waiton (Liftballbutton);
  }
 // check for white button
  if (digitalRead(Whitebutton) == LOW)
  {
    Serial.print ('w');
    waiton (Whitebutton);            // wait for button release
  }
 // check for blue button
  if (digitalRead (Bluebutton) == LOW)
  {
    Serial.print ('v');
    waiton (Bluebutton);            // wait for button release
  }
 // check for green button
  if (digitalRead(Greenbutton) == LOW)
  {
    Serial.print ('u');
    waiton (Greenbutton);           // wait for button release
  }
 // check for R button
  if (digitalRead(Rbutton) == LOW)
  {
    Serial.print ('r');             // wait for button release
    waiton(Rbutton);
  }
 // Check if machine tilted
  if (digitalRead(Tilt) == LOW)
  {
    Serial.print ('t');
    waiton(Tilt);                   // wait for button release
// close shutter as machine is tilted
// this copies a real Bally Bingo
     digitalWrite(ShutterRelay, HIGH);
// now stop motor in closed position
   while (digitalRead(Shutterclosed) == HIGH)
    {
       delay (50);
    }
     digitalWrite(ShutterRelay, LOW);  
  }
 // Rotate right
  if (digitalRead(Rotateright) == LOW)
  {
    Serial.print ('>');
    waiton (Rotateright);           // wait for button release
  }
 // Rotate left
  if (digitalRead(Rotateleft) == LOW)
  {
    Serial.print ('<');
    waiton (Rotateleft);            // wait for button release
  }
 // Check if 10 Credit button pressed
  if (digitalRead(Credits) == LOW)
    {
      Serial.print (')');
      waiton (Credits);             // wait for button release
    }
 // Check if Red Button pressed for new game
  if (digitalRead(Redbutton) == LOW)
  {
    Serial.print ('n');
    waiton (Redbutton);             // wait for button release
  }
 // Check if YELLOW button pressed for extra ball
  if (digitalRead(Yellowbutton) == LOW)
  {
    Serial.print ('x');
    waiton (Yellowbutton);          // wait for button release
  }
 // Check if A Button pressed
  if (digitalRead(Abutton) == LOW)
  {
    Serial.print ('a');
    waiton (Abutton);               // wait for button release
  }
 // Check if B Button pressed
  if (digitalRead(Bbutton) == LOW)
  {
    Serial.print ('b');
    waiton (Bbutton);                // wait for button release
  }
 // Check if C Button pressed
  if (digitalRead(Cbutton) == LOW)
  {
    Serial.print ('c');
    waiton (Cbutton);                // wait for button release
  }
 // Check if D Button pressed
  if (digitalRead(Dbutton) == LOW)
  {
    Serial.print ('d');
    waiton (Dbutton);                // wait for button release
  }
 // Check if E Button pressed
  if (digitalRead(Ebutton) == LOW)
  {
    Serial.print ('e');
    waiton (Ebutton);                 // wait for button release
  }
 // Check if F Button pressed
  if (digitalRead(Fbutton) == LOW)
  {
    Serial.print ('f');
    waiton (Fbutton);                 // wait for button release
  }
// check for ball in pocket
   for (int i = 22; i <= 47; i++)
    {
      if ((digitalRead(i)) == LOW && (BallsinPocket [i - 21]) == 0)
      { 
        BallsinPocket [i - 21] = 1;
        ++BIP;
        Serial.println (Ballcodes [i - 21]);  
      }
    }
}// end of main loop

//
void BTG ()
// Handles interrupts from Ball thro Gate switch
// keep code to a minimum
// NOTE - leaf switches can bounce an awful lot!
// especially the BTG switch
// test have shown this can be as much as 10 times over 0.25 second
// so interval timer between switch interrupts is set very long
// does not effect game as nothing else is happening till ball
// goes thro gate switch other than closing shutter after 1st ball
{
  currentMillis = millis();
  if (currentMillis - previousMillis > 2000)
  {          
    previousMillis = currentMillis;
    Serial.print('z');
    ++currentball;
  }  // end of interrupt handling
}
