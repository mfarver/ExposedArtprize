#include <Adafruit_NeoPixel.h>

// Parameter 1 = number of pixels in strip
// Parameter 2 = Arduino pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(500/*ish*/, 6, NEO_RGB + NEO_KHZ400);
bool show = false;

void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
}

void loop() {
  if (show) {
    strip.show();
    show = false;
  }
  // TODO: Do no-change refreshes if necessary
}

enum PARSE_STATE {
  R_LOW,
  R_HIGH,
  G_LOW,
  G_HIGH,
  B_LOW,
  B_HIGH,
};

void serialevent() {
  static PARSE_STATE state = R_HIGH;
  static uint32_t color = 0;
  static size_t i = 0;
  while (Serial.available()) {
    char in = Serial.read();
    if (in == '\n') { // End of frame, display
      show = true;
      i = 0;
      state = R_HIGH;
  } else {
    uint8_t val = 0;
    if ('0' <= in && in <= '9') {
      val = in - '0';
    else if ('A' <= in && in <= 'F') {
      val = in - 'A' + 0xA;
    } else {
      continue; // Skip unknown characters
    }
    // 00RRGGBB
    switch(state) {
      case R_HIGH:
        color |= val << 20;
        state = R_LOW;
        break;
      case R_LOW:
        color |= val << 16;
        state = G_HIGH;
        break;
      case G_HIGH:
        color |= val << 12;
        state = G_LOW;
        break;
      case G_LOW:
        color |= val << 8;
        state = B_HIGH;
        break;
      case B_HIGH:
        color |= val << 4;
        state = B_LOW;
        break;
      case B_LOW:
        color |= val;
        state = R_HIGH;
        // Last item of group of three; send to neopixel
        strip.setPixelColor(i++, color);
        color = 0;
        break;
      default:
        state = R_HIGH;
    }
  }
}


