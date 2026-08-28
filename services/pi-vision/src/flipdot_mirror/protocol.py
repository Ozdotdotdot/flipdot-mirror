import struct

MAGIC = b"FDM1"


def crc16(payload: bytes) -> int:
    crc = 0xFFFF
    for value in payload:
        crc ^= value << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode_packet(payload: bytes) -> bytes:
    if len(payload) > 0xFFFF:
        raise ValueError("payload too large")
    return MAGIC + struct.pack("<H", len(payload)) + payload + struct.pack("<H", crc16(payload))
