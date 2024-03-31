// NEOPIXEL BEST PRACTICES for most reliable operation:
// GND to white
// Data to green


// - Add 1000 uF CAPACITOR between NeoPixel strip's + and - connections.
// - MINIMIZE WIRING LENGTH between microcontroller board and first pixel.
// - NeoPixel strip's DATA-IN should pass through a 300-500 OHM RESISTOR.
// - AVOID connecting NeoPixels on a LIVE CIRCUIT. If you must, ALWAYS
//   connect GROUND (-) first, then +, then data.
// - When using a 3.3V microcontroller with a 5V-powered NeoPixel strip,
//   a LOGIC-LEVEL CONVERTER on the data line is STRONGLY RECOMMENDED.
// (Skipping these may work OK on your workbench but can fail in the field)

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif


// Which pin on the Arduino is connected to the NeoPixels?
#define LED_PIN    6

// How many NeoPixels are attached to the Arduino?
#define LED_COUNT 177

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
// Argument 1 = Number of pixels in NeoPixel strip
// Argument 2 = Arduino pin number (most are valid)
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)



// setup() function -- runs once at startup --------------------------------

float whiteKeyWidth = 330.0/14; // mm, measured over 2 octaves
float blackKeyWidth = 13.0; // mm, close enough approximation
float ledWidth = 1000.0/144; // mm, 144 leds/1000 mm 

int numberOfNotes = 0;
// int keyboardWidth = 0;
int startKey = 0;

byte buffer[2];


void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(32); // Set BRIGHTNESS to about 1/5 (max = 255)

  // waiting graphic for key range input
  bool mode = 1;

  bool waitForInput = true;

  while(waitForInput) {
    for(int i = 0; i < strip.numPixels(); i++) {  
      if(Serial.available() >= 2) {
        Serial.readBytes(buffer, 2);
        if(buffer[0] >= 12 && buffer[0] <= 119) {
          waitForInput = false;
          break;
        }
      }

      if(mode) {
        strip.setPixelColor(i, strip.Color(8,8,8,8));
      
      } else {
        strip.setPixelColor(i, strip.Color(0, 0, 0, 0));
      }      
      strip.show();
      delay(20);
    }

    mode = mode ^ 1; 
  }

  strip.fill(strip.Color(0, 8, 0, 8)); // green
  strip.show();
  
  // numberOfNotes = buffer[1] - buffer[0];
  // keyboardWidth = midi_notes_to_white_keys(buffer[0], buffer[1]) * whiteKeyWidth;
  startKey = buffer[0];

  // clear buffer
  buffer[0] = 0x00;
  buffer[1] = 0x00;
  delay(1000);
  strip.clear();
  strip.show();
}

// loop() function -- runs repeatedly as long as board is on ---------------

// pedal toggle
bool pedal = false;
// RGB
byte mood[3] = {0x00, 0xFF, 0x00};


void loop() {
  
  if(Serial.available() >= 2) {
    Serial.readBytes(buffer, 2);

    // read notes
    if(buffer[0] >= 12 && buffer[0] <= 119) {
      // chatgpt byte fractions, takes the velocity/127th fraction of each mood color
      noteToLed(buffer[0], strip.Color(
        static_cast<int>(static_cast<unsigned char>(buffer[1] * (static_cast<double>(mood[0]) / 127.0))), 
        static_cast<int>(static_cast<unsigned char>(buffer[1] * (static_cast<double>(mood[1]) / 127.0))), 
        static_cast<int>(static_cast<unsigned char>(buffer[1] * (static_cast<double>(mood[2]) / 127.0))), 
        0xFF), buffer[1]);

      strip.show(); // Update LED strip with new info
    }
    
    switch(buffer[0]) {
      // RGB
      case 1:
        mood[0] = buffer[1];
        break; 
      case 2:
        mood[1] = buffer[1];
        break;
      case 3:
        mood[2] = buffer[1];
        Serial.println("Mood response: ");

        Serial.println(mood[0]);
        Serial.println(mood[1]);
        Serial.println(mood[2]);

        break;

      // read pedal
      case 189:
        pedal = buffer[1];

        if(pedal == false) {
          strip.clear();
          strip.show();
        }
        break;
    }

    // clear buffer
    buffer[0] = 0x00;
    buffer[1] = 0x00;   
    }

}

// function definitions


int whiteKeysToLeft(int note) {
    // Count the number of white keys in the remaining range
    int whiteKeys = 0;
    for (int i = startKey; i < note; i++) {
        // C's are divisible by 12
        if (i % 12 == 0 || i % 12 == 2 || i % 12 == 4 || i % 12 == 5 || i % 12 == 7 || i % 12 == 9 || i % 12 == 11) {
            whiteKeys++;
        }
    }
        
    return whiteKeys;
}

void noteToLed(int noteNumber, uint32_t color, int action) {
  float leftBound = whiteKeysToLeft(noteNumber) * whiteKeyWidth;
  int blackKeyOffset = noteNumber % 12;
  
  if(blackKeyOffset == 1 || blackKeyOffset == 8) {
    // C# and F#
    leftBound -= 7;
  } else if (blackKeyOffset == 6 || blackKeyOffset == 10) {
    // A# and D#
    leftBound -= 5;
  } else if (blackKeyOffset == 3) {
    //
    leftBound -= 8;
  }

  float rightBound = leftBound;
  if (noteNumber % 12 == 0 || noteNumber % 12 == 2 || noteNumber % 12 == 4 || noteNumber % 12 == 5 || noteNumber % 12 == 7 || noteNumber % 12 == 9 || noteNumber % 12 == 11) {
    rightBound += whiteKeyWidth;
  } else {
    rightBound += blackKeyWidth;
  }

  // int rightBound = midi_notes_to_white_keys(startKey, noteNumber) * whiteKeyWidth;
  // Serial.print("leftbound: ");
  // Serial.println(leftBound);
  // Serial.print("right: ");
  // Serial.println(rightBound);

  boundariesToLed(leftBound, rightBound, color, action);
}

void boundariesToLed(float startDist, float endDist, uint32_t color, int action) {
  float lowerPixelNum = startDist / ledWidth;
  float upperPixelNum = endDist / ledWidth;


  for(int i = ceil(lowerPixelNum); i <= floor(upperPixelNum); i++) {

    if(action != 64) {
      strip.setPixelColor(i, color);
    } else {
      if(!pedal) {
        strip.setPixelColor(i, strip.Color(0x0, 0x0, 0x0, 0x0));
      } else {
        // Serial.print(strip.getPixelColor(i), HEX);
        strip.setPixelColor(i, strip.Color(mood[0] & 0xA, mood[1] & 0xA, mood[2] & 0xA, 0));
      
      }

    }
    
  
  }

  // aliasing
  // float percentLowerPixelNum = lowerPixelNum - floor(lowerPixelNum);
  // strip.setPixelColor(floor(lowerPixelNum), color);
}
