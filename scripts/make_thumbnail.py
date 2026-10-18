#!/usr/bin/env python3
"""Writes a 512x512 placeholder mod/thumbnail.png (stdlib only). Replace it with real art anytime."""
import math
import struct
import zlib
from pathlib import Path

SIZE = 512
BG = (16, 24, 20)
RING = (110, 210, 150)
GLOW = (200, 160, 80)
OUT = Path(__file__).resolve().parent.parent / "mod" / "thumbnail.png"


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def pixel(x, y):
    cx = cy = SIZE / 2
    r = math.hypot(x - cx, y - cy)
    color = mix(BG, GLOW, max(0.0, 1 - r / 260) * 0.35)
    for radius, width in ((170, 14), (120, 6)):  # two concentric rings
        d = abs(r - radius)
        if d < width:
            color = mix(color, RING, 1 - (d / width) ** 2)
    if r < 40:  # core
        color = mix(color, RING, 1 - r / 40)
    return color


def chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def main():
    raw = b"".join(
        b"\x00" + b"".join(bytes(pixel(x, y)) for x in range(SIZE)) for y in range(SIZE)
    )
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    OUT.write_bytes(png)
    print(f"Wrote {OUT} ({len(png)} bytes)")


if __name__ == "__main__":
    main()
