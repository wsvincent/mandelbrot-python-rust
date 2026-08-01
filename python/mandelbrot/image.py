"""Minimal PNG writer.

Standard library only -- Pillow would work fine here, but keeping the whole
demo dependency-free means `python -m mandelbrot` runs straight out of a
fresh checkout with nothing installed.
"""

import struct
import zlib


def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path, width, height, raw):
    """Write 8-bit truecolour RGB scanlines (`raw`) out as a PNG."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_chunk(b"IHDR", ihdr))
        f.write(_chunk(b"IDAT", zlib.compress(raw, 6)))
        f.write(_chunk(b"IEND", b""))
