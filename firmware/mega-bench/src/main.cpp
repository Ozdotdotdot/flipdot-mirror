#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

constexpr uint8_t DATA_PIN = 6;
constexpr uint8_t DOT_COUNT = 35;
constexpr uint8_t WIRE_BYTES = 36;
constexpr uint8_t PSEUDO_PIXELS = WIRE_BYTES / 3;

Adafruit_NeoPixel signal(PSEUDO_PIXELS, DATA_PIN, NEO_GRB + NEO_KHZ800);
uint8_t dots[DOT_COUNT] = {0};
int selectedDot = -1;

void sendFrame() {
  uint8_t *wire = signal.getPixels();
  memset(wire, 0, WIRE_BYTES);
  memcpy(wire, dots, DOT_COUNT);
  signal.show();
}

void fillFrame(uint8_t value) {
  memset(dots, value, sizeof(dots));
  sendFrame();
}

void showOnly(int index) {
  memset(dots, 0, sizeof(dots));
  if (index >= 0 && index < DOT_COUNT) dots[index] = 0xFF;
  sendFrame();
  Serial.print(F("White dot byte: "));
  Serial.println(index + 1);
}

void testEveryDot() {
  for (int i = 0; i < DOT_COUNT; ++i) {
    showOnly(i);
    delay(300);
  }
  fillFrame(0x00);
}

void printHelp() {
  Serial.println(F("b black | w white | n next | p previous | t test | h help"));
}

void setup() {
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);
  Serial.begin(115200);
  signal.begin();
  fillFrame(0x00);
  printHelp();
  Serial.println(F("Startup frame sent: all black."));
}

void loop() {
  if (!Serial.available()) return;
  switch (tolower(Serial.read())) {
    case 'b': fillFrame(0x00); break;
    case 'w': fillFrame(0xFF); break;
    case 'n': selectedDot = (selectedDot + 1) % DOT_COUNT; showOnly(selectedDot); break;
    case 'p': selectedDot = (selectedDot + DOT_COUNT - 1) % DOT_COUNT; showOnly(selectedDot); break;
    case 't': testEveryDot(); break;
    case 'h': printHelp(); break;
  }
}
