#!/usr/bin/env python3
"""news-image-20261120 entrypoint.

Writes the pre-rendered front page (entry.png, 1024x1024, 35 verified
stories from Friday 20 November 2026) into the output directory.

Stdlib only — the sandbox installs nothing, so no Pillow is needed here.
The image was rendered at build time by render.py (PIL) from the verified
facts in stories.py / NEWS-SOURCES.md, the photos in assets/, and Natural
Earth coastline data (ne_110m_land.geojson). Running render.py again
reproduces entry.png byte-for-byte (deterministic: fixed seed, no
timestamps).

Before writing, the PNG is validated: magic signature, IHDR dimensions
(1024x1024), size within the 1 MiB cap, and a trailing IEND chunk, so a
corrupt or truncated file fails loudly instead of shipping a broken image.
"""

import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024  # 1 MiB cap


def load_png(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        raise SystemExit(
            f"entry.png is {len(data)} bytes, over the 1 MiB cap"
        )
    if not data.startswith(PNG_MAGIC):
        raise SystemExit("entry.png: bad PNG signature")
    # IHDR: 8 magic + 4 length + 4 type + 13 data (width, height, ...).
    if len(data) < 33 or data[12:16] != b"IHDR":
        raise SystemExit("entry.png: missing IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise SystemExit(
            f"entry.png is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    # The last 8 bytes must hold the IEND chunk type plus its CRC.
    tail = data.rstrip(b"\x00")
    if len(tail) < 8 or tail[-8:-4] != b"IEND":
        raise SystemExit("entry.png: missing IEND chunk")
    return data


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    data = load_png(os.path.join(here, "entry.png"))
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    print(
        f"wrote {target} ({len(data)} bytes, "
        f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT})"
    )


if __name__ == "__main__":
    sys.exit(main())
