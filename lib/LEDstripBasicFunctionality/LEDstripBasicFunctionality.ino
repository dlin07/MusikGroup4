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

#define whiteKeyWidth 22 // mm
#define ledWidth 8 // mm



// setup() function -- runs once at startup --------------------------------

int numberOfNotes = 0;
int keyboardWidth = 0;

byte buffer[2];


void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(127); // Set BRIGHTNESS to about 1/5 (max = 255)

  // waiting graphic for key range input
  bool mode = 1;

  while(Serial.available() < 2) {
    for(int i = 0; i < strip.numPixels(); i++) {  
      if(Serial.available() >= 2) {
        break;
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
  Serial.readBytes(buffer, 2);
  
  numberOfNotes = buffer[1] - buffer[0];
  keyboardWidth = midi_notes_to_white_keys(buffer[0], buffer[1]) * whiteKeyWidth;
  Serial.print("keyboardWidth");
  Serial.print(keyboardWidth);

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

void loop() {

  
  if(Serial.available() >= 2) {
    Serial.readBytes(buffer, 2);

    // read pedal
    if(buffer[0] == 189) {
      pedal = buffer[1];

      if(pedal == false) {
        strip.clear();
        strip.show();
      }
      
      // clear buffer
      buffer[0] = 0x00;
      buffer[1] = 0x00;
    }

    // read notes
    if(buffer[0] >= 12 && buffer[0] <= 119) {
      if(buffer[1] != 64) {
        strip.setPixelColor(buffer[0], strip.Color(2*buffer[1], 2*buffer[1], 2*buffer[1], 2*buffer[1]));
      } else {
        if(!pedal) {
          strip.setPixelColor(buffer[0], strip.Color(0x0, 0x0, 0x0, 0x0));
        } else {
          strip.setPixelColor(buffer[0], strip.getPixelColor(buffer[0]) & 0x0F0F0F0F);
        }

      }
      strip.show(); // Update LED strip with new info
        
      // clear buffer
      buffer[0] = 0x00;
      buffer[1] = 0x00;
    }
    // Serial.print(buffer[0]);
    // Serial.print(" ");
    // Serial.println(buffer[1]);

    }

}

// function definitions


int midi_notes_to_white_keys(int note1, int note2) {
    int pitch_class_note1 = note1 % 12;
    int pitch_class_note2 = note2 % 12;
    
    int absolute_difference = abs(pitch_class_note2 - pitch_class_note1);
    
    int complete_octaves = abs(note2 - note1) / 12;
    int white_keys_in_complete_octaves = complete_octaves * 7;
    
    int remaining_keys = absolute_difference % 12;
    
    // Count the number of white keys in the remaining range
    int white_keys = 0;
    for (int i = 0; i <= remaining_keys; ++i) {
        if (i % 12 == 0 || i % 12 == 2 || i % 12 == 4 || i % 12 == 5 || i % 12 == 7 || i % 12 == 9 || i % 12 == 11) {
            white_keys++;
        }
    }
    
    int total_white_keys = white_keys_in_complete_octaves + white_keys;
    
    return total_white_keys;
}
