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

int numberOfNotes;
byte buffer[2];

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(127); // Set BRIGHTNESS to about 1/5 (max = 255)
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
