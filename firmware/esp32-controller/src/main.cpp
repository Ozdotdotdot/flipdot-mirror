#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#ifndef DISPLAY_BYTES
#define DISPLAY_BYTES 35
#endif

#ifndef F30_DATA_PIN
#define F30_DATA_PIN 18
#endif

constexpr size_t PADDED_BYTES = ((DISPLAY_BYTES + 2) / 3) * 3;
constexpr size_t PSEUDO_PIXELS = PADDED_BYTES / 3;
constexpr uint8_t MAGIC[] = {'F', 'D', 'M', '1'};

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

void sendFrame(const uint8_t *frame) {
  uint8_t *wire = dotBus.getPixels();
  memset(wire, 0, PADDED_BYTES);
  memcpy(wire, frame, DISPLAY_BYTES);
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
