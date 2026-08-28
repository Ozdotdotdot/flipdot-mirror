#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#ifndef DISPLAY_WIDTH
#define DISPLAY_WIDTH 5
#endif

#ifndef DISPLAY_HEIGHT
#define DISPLAY_HEIGHT 7
#endif

#ifndef F30_DATA_PIN
#define F30_DATA_PIN 18
#endif

constexpr size_t MODULE_WIDTH = 5;
constexpr size_t MODULE_HEIGHT = 7;
constexpr size_t MODULE_BYTES = MODULE_WIDTH * MODULE_HEIGHT;
constexpr size_t MODULE_COLUMNS = DISPLAY_WIDTH / MODULE_WIDTH;
constexpr size_t MODULE_ROWS = DISPLAY_HEIGHT / MODULE_HEIGHT;
constexpr size_t DISPLAY_BYTES = DISPLAY_WIDTH * DISPLAY_HEIGHT;
constexpr size_t PADDED_BYTES = ((DISPLAY_BYTES + 2) / 3) * 3;
constexpr size_t PSEUDO_PIXELS = PADDED_BYTES / 3;
constexpr uint8_t MAGIC[] = {'F', 'D', 'M', '1'};

static_assert(DISPLAY_WIDTH % MODULE_WIDTH == 0, "display width must contain complete F30 modules");
static_assert(DISPLAY_HEIGHT % MODULE_HEIGHT == 0, "display height must contain complete F30 modules");

Adafruit_NeoPixel dotBus(PSEUDO_PIXELS, F30_DATA_PIN, NEO_GRB + NEO_KHZ800);
uint8_t framebuffer[DISPLAY_BYTES] = {0};

uint16_t crc16(const uint8_t *data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; ++i) {
    crc ^= static_cast<uint16_t>(data[i]) << 8;
    for (uint8_t bit = 0; bit < 8; ++bit) {
      crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
    }
  }
  return crc;
}

void sendFrame(const uint8_t *logicalFrame) {
  uint8_t *wire = dotBus.getPixels();
  memset(wire, 0, PADDED_BYTES);

  size_t chainModule = 0;
  for (size_t moduleY = 0; moduleY < MODULE_ROWS; ++moduleY) {
    for (size_t chainX = 0; chainX < MODULE_COLUMNS; ++chainX) {
      const size_t moduleX =
          moduleY % 2 ? MODULE_COLUMNS - 1 - chainX : chainX;
      const size_t moduleBase = chainModule++ * MODULE_BYTES;

      for (size_t localY = 0; localY < MODULE_HEIGHT; ++localY) {
        for (size_t localX = 0; localX < MODULE_WIDTH; ++localX) {
          const size_t logicalX = moduleX * MODULE_WIDTH + localX;
          const size_t logicalY = moduleY * MODULE_HEIGHT + localY;
          const size_t logicalIndex = logicalY * DISPLAY_WIDTH + logicalX;
          const size_t localWireIndex =
              MODULE_BYTES - 1 - localY * MODULE_WIDTH - localX;
          wire[moduleBase + localWireIndex] = logicalFrame[logicalIndex];
        }
      }
    }
  }
  dotBus.show();
}

void fillFrame(uint8_t value) {
  memset(framebuffer, value, sizeof(framebuffer));
  sendFrame(framebuffer);
}

void printStatus(const char *message) {
  Serial.print(F("STATUS "));
  Serial.println(message);
}

enum class RxState { Magic, LengthLow, LengthHigh, Payload, CrcLow, CrcHigh };
RxState rxState = RxState::Magic;
size_t magicIndex = 0;
uint16_t payloadLength = 0;
uint16_t payloadIndex = 0;
uint16_t receivedCrc = 0;
uint8_t incoming[DISPLAY_BYTES];

void resetReceiver() {
  rxState = RxState::Magic;
  magicIndex = 0;
  payloadLength = 0;
  payloadIndex = 0;
  receivedCrc = 0;
}

void receiveByte(uint8_t value) {
  switch (rxState) {
    case RxState::Magic:
      if (value == MAGIC[magicIndex]) {
        if (++magicIndex == sizeof(MAGIC)) rxState = RxState::LengthLow;
      } else {
        magicIndex = value == MAGIC[0] ? 1 : 0;
      }
      break;
    case RxState::LengthLow:
      payloadLength = value;
      rxState = RxState::LengthHigh;
      break;
    case RxState::LengthHigh:
      payloadLength |= static_cast<uint16_t>(value) << 8;
      if (payloadLength != DISPLAY_BYTES) {
        printStatus("bad-length");
        resetReceiver();
      } else {
        payloadIndex = 0;
        rxState = RxState::Payload;
      }
      break;
    case RxState::Payload:
      incoming[payloadIndex++] = value;
      if (payloadIndex == payloadLength) rxState = RxState::CrcLow;
      break;
    case RxState::CrcLow:
      receivedCrc = value;
      rxState = RxState::CrcHigh;
      break;
    case RxState::CrcHigh:
      receivedCrc |= static_cast<uint16_t>(value) << 8;
      if (receivedCrc == crc16(incoming, payloadLength)) {
        memcpy(framebuffer, incoming, DISPLAY_BYTES);
        sendFrame(framebuffer);
        printStatus("frame-ok");
      } else {
        printStatus("bad-crc");
      }
      resetReceiver();
      break;
  }
}

void setup() {
  pinMode(F30_DATA_PIN, OUTPUT);
  digitalWrite(F30_DATA_PIN, LOW);
  Serial.begin(921600);
  dotBus.begin();
  fillFrame(0x00);
  printStatus("ready");
}

void loop() {
  while (Serial.available()) receiveByte(static_cast<uint8_t>(Serial.read()));
}
