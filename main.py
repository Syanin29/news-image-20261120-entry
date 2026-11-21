#!/usr/bin/env python3
"""Entrypoint for the news-image-20261120 entry.

The front page image (entry.png, 1024x1024) is rendered ahead of time by
render.py from the verified story data in stories.py. This script is the
piece the competition harness runs: it checks the PNG is intact and copies
it into the output directory. Standard library only, so it runs anywhere
python3 does.

Checks before copying:
  - file size within the 1 MiB cap
  - PNG magic signature at the start
  - IHDR chunk reporting exactly 1024x1024
  - IEND chunk at the end (no truncation)
Any failure aborts with a message instead of shipping a broken image.
"""

import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WANT_W = 1024
WANT_H = 1024
SIZE_CAP = 1024 * 1024


def read_checked_png(path):
    with open(path, "rb") as fh:
        blob = fh.read()
    if len(blob) > SIZE_CAP:
        raise SystemExit(f"entry.png is {len(blob)} bytes, cap is {SIZE_CAP}")
    if blob[:8] != PNG_MAGIC:
        raise SystemExit("entry.png does not start with the PNG signature")
    if len(blob) < 33 or blob[12:16] != b"IHDR":
        raise SystemExit("entry.png is missing its IHDR chunk")
    width, height = struct.unpack(">II", blob[16:24])
    if (width, height) != (WANT_W, WANT_H):
        raise SystemExit(f"entry.png is {width}x{height}, want {WANT_W}x{WANT_H}")
    if blob.rstrip(b"\x00")[-8:-4] != b"IEND":
        raise SystemExit("entry.png has no IEND chunk (truncated?)")
    return blob


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    png = read_checked_png(os.path.join(base, "entry.png"))
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as fh:
        fh.write(png)
    print(f"wrote {dest} ({len(png)} bytes, {WANT_W}x{WANT_H}, checks passed)")


if __name__ == "__main__":
    sys.exit(main())
