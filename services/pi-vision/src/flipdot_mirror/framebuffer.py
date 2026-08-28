class FrameBuffer:
    """Logical binary framebuffer whose dimensions are multiples of an F30."""

    MODULE_WIDTH = 5
    MODULE_HEIGHT = 7

    def __init__(self, width: int = 35, height: int = 21):
        if width % self.MODULE_WIDTH or height % self.MODULE_HEIGHT:
            raise ValueError("frame dimensions must be multiples of 5x7")
        self.width = width
        self.height = height
        self.bits = bytearray(width * height)

    def set(self, x: int, y: int, active: bool = True) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError((x, y))
        self.bits[y * self.width + x] = 1 if active else 0

    def clear(self) -> None:
        self.bits[:] = bytes(len(self.bits))

    def to_f30_stream(self, serpentine: bool = True) -> bytes:
        """Map top-left logical pixels to module-chain bytes.

        Modules are assumed to start at top-left. Odd module rows reverse when
        serpentine cabling is enabled. Each module uses the verified local order
        35..31 at the top and 5..1 at the bottom.
        """
        module_cols = self.width // self.MODULE_WIDTH
        module_rows = self.height // self.MODULE_HEIGHT
        stream = bytearray()

        for module_y in range(module_rows):
            columns = list(range(module_cols))
            if serpentine and module_y % 2:
                columns.reverse()
            for module_x in columns:
                module = bytearray(35)
                for local_y in range(self.MODULE_HEIGHT):
                    for local_x in range(self.MODULE_WIDTH):
                        global_x = module_x * self.MODULE_WIDTH + local_x
                        global_y = module_y * self.MODULE_HEIGHT + local_y
                        wire_index = 34 - local_y * self.MODULE_WIDTH - local_x
                        module[wire_index] = (
                            0xFF if self.bits[global_y * self.width + global_x] else 0x00
                        )
                stream.extend(module)
        return bytes(stream)
