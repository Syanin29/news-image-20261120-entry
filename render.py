#!/usr/bin/env python3
"""Render the front page for Friday 20 November 2026 — 35 verified stories.

Deterministic 1024x1024 PNG (fixed seed, no timestamps, no metadata):
running twice produces byte-identical output, <= 1 MiB.

Usage:
  python3 render.py            # v1 light front page -> entry.png
  python3 render.py v2         # -> variants/v2-entry.png, etc.

Six variants, two palettes (light/dark) and four layouts (front page,
map-led, photo-led, broadsheet, stat-led). All share stories.py data and
the same band primitives; only arrangement and palette differ.
"""

import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import stories as S

HERE = Path(__file__).parent
W, H = 1024, 1024
SEED = 20261120
MAX_BYTES = 1024 * 1024
MARGIN = 28

LIGHT = dict(
    paper=(247, 243, 234), ink=(24, 22, 20), muted=(96, 90, 80),
    accent=(178, 34, 34), navy=(23, 42, 74), card=(255, 253, 248),
    line=(196, 188, 172), chip=(23, 42, 74), chip_text=(255, 255, 255),
    ticker_bg=(24, 22, 20), ticker_text=(247, 243, 234),
    map_dot=(120, 130, 145), marker=(178, 34, 34),
)
DARK = dict(
    paper=(16, 19, 26), ink=(238, 236, 230), muted=(160, 165, 178),
    accent=(240, 120, 90), navy=(120, 170, 240), card=(26, 31, 42),
    line=(58, 66, 82), chip=(240, 120, 90), chip_text=(16, 19, 26),
    ticker_bg=(238, 236, 230), ticker_text=(16, 19, 26),
    map_dot=(110, 130, 160), marker=(240, 120, 90),
)

VARIANTS = {
    # palette, hero_h, map_h, list_cols, photo_mode, stat_strip
    "v1": (LIGHT, 240, 215, 2, "side", False),
    "v2": (DARK, 240, 215, 2, "side", False),
    "v3": (LIGHT, 170, 300, 2, "side", False),
    "v4": (LIGHT, 300, 170, 2, "wide", False),
    "v5": (LIGHT, 200, 200, 3, "none", False),
    "v6": (LIGHT, 215, 200, 2, "side", True),
}


def font(name, size):
    return ImageFont.truetype(str(HERE / "fonts" / name), size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt, max_w):
    """Truncate with ellipsis so text never overprints its neighbour."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "…", font=fnt) > max_w:
        text = text[:-1]
    return text + "…"


def shadow_card(img, box, fill, radius=8):
    """Card with a soft drop shadow — depth instead of flat blocks."""
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([x0 + 3, y0 + 5, x1 + 3, y1 + 5], radius,
                         fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius, fill=fill)
    return d


# ---------------------------------------------------------------------------
# Dotted world map from Natural Earth coastline data (public domain)
# ---------------------------------------------------------------------------

def load_land():
    data = json.loads((HERE / "ne_110m_land.geojson").read_text())
    polys = []
    for feat in data["features"]:
        geom = feat["geometry"]
        rings = []
        if geom["type"] == "Polygon":
            rings = [geom["coordinates"][0]]
        elif geom["type"] == "MultiPolygon":
            rings = [poly[0] for poly in geom["coordinates"]]
        for ring in rings:
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            polys.append((ring, min(xs), max(xs), min(ys), max(ys)))
    return polys


def in_land(polys, lon, lat):
    for ring, x0, x1, y0, y1 in polys:
        if not (x0 <= lon <= x1 and y0 <= lat <= y1):
            continue
        inside = False
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > lat) != (yj > lat) and \
                    lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        if inside:
            return True
    return False


def draw_map(draw, box, pal, polys, title=True):
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    # equirectangular: lon -180..180, lat 78..-58 (crop poles)
    lat_top, lat_bot = 78.0, -58.0

    def px(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (lat_top - lat) / (lat_top - lat_bot) * mh)

    step = 7
    for gy in range(int(y0) + 3, int(y1) - 2, step):
        lat = lat_top - (gy - y0) / mh * (lat_top - lat_bot)
        for gx in range(int(x0) + 3, int(x1) - 2, step):
            lon = (gx - x0) / mw * 360.0 - 180.0
            if in_land(polys, lon, lat):
                draw.ellipse([gx - 1.6, gy - 1.6, gx + 1.6, gy + 1.6],
                             fill=pal["map_dot"])
    f_num = font("Archivo.ttf", 13)
    for num, (lon, lat, dx, dy) in S.MARKERS.items():
        cx, cy = px(lon, lat)
        # clamp the label disc inside the map box so edge markers (Fiji,
        # Wellington) never clip
        lx = min(max(cx + dx, x0 + 12), x1 - 12)
        ly = min(max(cy + dy, y0 + 12), y1 - 12)
        draw.line([cx, cy, lx, ly], fill=pal["marker"], width=1)
        r = 10
        draw.ellipse([lx - r, ly - r, lx + r, ly + r], fill=pal["marker"],
                     outline=(255, 255, 255), width=2)
        label = str(num)
        tw = draw.textlength(label, font=f_num)
        draw.text((lx - tw / 2, ly - 7), label, font=f_num,
                  fill=(255, 255, 255))
    if title:
        f_t = font("Archivo.ttf", 15)
        label = f"WHERE IT HAPPENED — {len(S.MARKERS)} PLACES"
        tw = draw.textlength(label, font=f_t)
        # paper patch behind the title so dots/markers never strike through it
        draw.rectangle([x0 + 2, y0 + 2, x0 + tw + 12, y0 + 24],
                       fill=pal["paper"])
        draw.text((x0 + 6, y0 + 4), label, font=f_t, fill=pal["ink"])


# ---------------------------------------------------------------------------
# Bands
# ---------------------------------------------------------------------------

def grain(img, pal, rng):
    """Paper grain + soft vignette glow — surface texture, no flat fill."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    dark = pal is DARK
    for _ in range(2600):
        gx, gy = rng.randrange(W), rng.randrange(H)
        a = rng.randrange(6, 22)
        od.point((gx, gy), fill=(255, 255, 255, a) if dark else (60, 50, 30, a))
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-220, -320, 1244, 420], fill=42 if dark else 26)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    base = img.convert("RGBA")
    warm = Image.new("RGBA", (W, H), (255, 214, 150, 255))
    base = Image.composite(warm, base, glow) if dark else base
    return Image.alpha_composite(base, overlay).convert("RGB")


def masthead(draw, pal, y):
    f_big = font("PlayfairDisplay.ttf", 54)
    title = "THE WORLD TODAY"
    tw = draw.textlength(title, font=f_big)
    draw.text(((W - tw) / 2, y), title, font=f_big, fill=pal["ink"])
    y += 62
    f_sub = font("Archivo.ttf", 16)
    sub = f"{S.DATE_LINE}  •  {S.STORY_COUNT} STORIES  •  {S.CONTINENT_LINE}"
    sw = draw.textlength(sub, font=f_sub)
    draw.text(((W - sw) / 2, y), sub, font=f_sub, fill=pal["accent"])
    y += 24
    draw.line([MARGIN, y, W - MARGIN, y], fill=pal["ink"], width=3)
    draw.line([MARGIN, y + 5, W - MARGIN, y + 5], fill=pal["ink"], width=1)
    return y + 12


def hero_band(img, draw, pal, y, height, photo_mode):
    head, expl, stat, _marker, photo = S.HERO
    x0, x1 = MARGIN, W - MARGIN
    if photo_mode == "wide":
        ph_h = height - 92
        pic = Image.open(HERE / "assets" / photo).convert("RGB")
        pic = pic.resize((x1 - x0, ph_h))
        img.paste(pic, (x0, y))
        draw.rectangle([x0, y, x1, y + ph_h], outline=pal["ink"], width=2)
        cap_y = y + ph_h + 4
        draw.text((x0, cap_y), "Cyclone Akvan from space — generic image",
                  font=font("Inter.ttf", 10), fill=pal["muted"])
        ty = cap_y + 16
        draw.text((x0, ty), "TOP STORY", font=font("Archivo.ttf", 13),
                  fill=pal["accent"])
        f_h = font("PlayfairDisplay.ttf", 30)
        draw.text((x0, ty + 16), fit_text(draw, head, f_h, x1 - x0 - 230),
                  font=f_h, fill=pal["ink"])
        f_stat = font("Archivo.ttf", 22)
        sw = draw.textlength(stat, font=f_stat)
        draw.text((x1 - sw, ty + 20), stat, font=f_stat, fill=pal["accent"])
        return y + height
    # side / none: photo left (or text full width), words right
    text_x = x0
    if photo_mode == "side":
        pw = 430
        pic = Image.open(HERE / "assets" / photo).convert("RGB")
        # centre-crop to the band's aspect, then resize
        target_ratio = pw / (height - 18)
        w0, h0 = pic.size
        if w0 / h0 > target_ratio:
            nw = int(h0 * target_ratio)
            pic = pic.crop(((w0 - nw) // 2, 0, (w0 + nw) // 2, h0))
        else:
            nh = int(w0 / target_ratio)
            pic = pic.crop((0, (h0 - nh) // 2, w0, (h0 + nh) // 2))
        pic = pic.resize((pw, height - 18))
        img.paste(pic, (x0, y))
        draw.rectangle([x0, y, x0 + pw, y + height - 18],
                       outline=pal["ink"], width=2)
        draw.text((x0, y + height - 14),
                  "Cyclone Akvan from space — generic image",
                  font=font("Inter.ttf", 10), fill=pal["muted"])
        text_x = x0 + pw + 18
    tw = x1 - text_x
    draw.text((text_x, y), "TOP STORY", font=font("Archivo.ttf", 14),
              fill=pal["accent"])
    f_h = font("PlayfairDisplay.ttf", 31)
    hy = y + 20
    for line in wrap(draw, head, f_h, tw)[:3]:
        draw.text((text_x, hy), line, font=f_h, fill=pal["ink"])
        hy += 36
    f_e = font("Inter.ttf", 14)
    for line in wrap(draw, expl, f_e, tw)[:3]:
        draw.text((text_x, hy + 2), line, font=f_e, fill=pal["muted"])
        hy += 19
    f_stat = font("Archivo.ttf", 26)
    draw.text((text_x, hy + 8), stat, font=f_stat, fill=pal["accent"])
    draw.text((text_x, hy + 40), "to 1,224 shelters • landfall noon today",
              font=font("Inter.ttf", 12), fill=pal["muted"])
    return y + height


def stat_strip(img, draw, pal, y):
    """v6 only: four big numbers under the masthead."""
    stats = [("105,304", "EVACUATED IN ODISHA"), ("$1.84BN", "GTA VI DAY ONE"),
             ("+17%", "ANTHROPIC DEBUT"), ("317-6", "NZ AT LUNCH")]
    x0, x1 = MARGIN, W - MARGIN
    cw = (x1 - x0) // 4
    f_big = font("Archivo.ttf", 30)
    f_lab = font("Inter.ttf", 10)
    for i, (big, lab) in enumerate(stats):
        cx = x0 + i * cw
        draw = shadow_card(img, [cx + 3, y, cx + cw - 3, y + 58], pal["card"])
        bw = draw.textlength(big, font=f_big)
        draw.text((cx + (cw - bw) / 2, y + 6), big, font=f_big,
                  fill=pal["accent"])
        lw = draw.textlength(lab, font=f_lab)
        draw.text((cx + (cw - lw) / 2, y + 40), lab, font=f_lab,
                  fill=pal["muted"])
    return y + 68, draw


def feature_row(img, draw, pal, y, height):
    x0, x1 = MARGIN, W - MARGIN
    gap = 10
    cw = (x1 - x0 - gap * 3) // 4
    f_h = font("Archivo.ttf", 15)
    f_e = font("Inter.ttf", 10.5)
    f_s = font("Archivo.ttf", 13)
    for i, (head, expl, stat, marker, _p) in enumerate(S.FEATURES):
        cx = x0 + i * (cw + gap)
        draw = shadow_card(img, [cx, y, cx + cw, y + height], pal["card"])
        draw.rectangle([cx, y, cx + cw, y + 4], fill=pal["accent"])
        ty = y + 10
        for line in wrap(draw, head, f_h, cw - 16)[:2]:
            draw.text((cx + 8, ty), line, font=f_h, fill=pal["ink"])
            ty += 18
        for line in wrap(draw, expl, f_e, cw - 16)[:3]:
            draw.text((cx + 8, ty + 2), line, font=f_e, fill=pal["muted"])
            ty += 14
        if marker:
            draw.text((cx + 8, ty + 4), f"— map {marker}",
                      font=font("Inter.ttf", 10), fill=pal["accent"])
        # stat chip pinned to the card foot — never overprints the explainer
        chip_w = draw.textlength(stat, font=f_s) + 16
        cy = y + height - 26
        draw.rounded_rectangle([cx + 8, cy, cx + 8 + chip_w, cy + 20], 6,
                               fill=pal["chip"])
        draw.text((cx + 16, cy + 3), stat, font=f_s, fill=pal["chip_text"])
    return y + height, draw


def list_band(draw, pal, y, height, cols):
    x0, x1 = MARGIN, W - MARGIN
    rows = (len(S.LIST_STORIES) + cols - 1) // cols
    rh = height / rows
    cw = (x1 - x0) // cols
    f_h = font("Archivo.ttf", 12.5 if cols == 2 else 11)
    f_s = font("Archivo.ttf", 11.5 if cols == 2 else 10)
    f_n = font("Archivo.ttf", 11)
    for idx, (head, stat, _m) in enumerate(S.LIST_STORIES):
        col, row = divmod(idx, rows)
        cx = x0 + col * cw
        cy = y + row * rh
        num = f"{idx + 6:02d}"
        draw.text((cx, cy + 2), num, font=f_n, fill=pal["accent"])
        sw = draw.textlength(stat, font=f_s)
        max_hw = cw - 30 - sw - 10
        draw.text((cx + 28, cy + 1), fit_text(draw, head, f_h, max_hw),
                  font=f_h, fill=pal["ink"])
        draw.text((cx + cw - sw - 6, cy + 2), stat, font=f_s,
                  fill=pal["navy"])
        if row < rows - 1:
            draw.line([cx, cy + rh - 2, cx + cw - 8, cy + rh - 2],
                      fill=pal["line"], width=1)
    return y + height


def ticker_band(draw, pal, y, height):
    x0, x1 = MARGIN, W - MARGIN
    draw.rectangle([x0, y, x1, y + height], fill=pal["ticker_bg"])
    f_h = font("Archivo.ttf", 12)
    f_e = font("Inter.ttf", 10)
    draw.text((x0 + 10, y + 6), "ALSO TODAY", font=font("Archivo.ttf", 12),
              fill=pal["accent"] if pal is LIGHT else pal["ticker_text"])
    cw = (x1 - x0 - 20) // 4
    for i, (head, expl) in enumerate(S.TICKER):
        cx = x0 + 10 + i * cw
        draw.text((cx, y + 24), fit_text(draw, head, f_h, cw - 8),
                  font=f_h, fill=pal["ticker_text"])
        draw.text((cx, y + 40), fit_text(draw, expl, f_e, cw - 8),
                  font=f_e, fill=pal["ticker_text"])
    return y + height


def render(variant):
    pal, hero_h, map_h, cols, photo_mode, strip = VARIANTS[variant]
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H), pal["paper"])
    img = grain(img, pal, rng)
    draw = ImageDraw.Draw(img)
    polys = load_land()

    y = masthead(draw, pal, 16)
    if strip:
        y, draw = stat_strip(img, draw, pal, y + 2)
    y = hero_band(img, draw, pal, y + 4, hero_h, photo_mode) + 10
    y, draw = feature_row(img, draw, pal, y, 118)
    y += 10
    map_box = [MARGIN, y, W - MARGIN, y + map_h]
    draw.rectangle(map_box, outline=pal["line"], width=1)
    draw_map(draw, map_box, pal, polys)
    y += map_h + 10
    # list takes whatever vertical space remains above the ticker
    ticker_h = 58
    list_h = H - 26 - ticker_h - 8 - y
    y = list_band(draw, pal, y, list_h, cols) + 8
    y = ticker_band(draw, pal, y, ticker_h)
    draw.text((MARGIN, y + 6),
              "Sources: Reuters, AP, BBC, IMD, Sensor Tower — see NEWS-SOURCES.md",
              font=font("Inter.ttf", 10), fill=pal["muted"])
    return img


def save(img, path):
    img.save(path, "PNG", optimize=True)
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"{path} is {size} bytes, over the 1 MiB cap")
    print(f"wrote {path} ({size} bytes, {img.size[0]}x{img.size[1]})")


def main(argv):
    if len(argv) > 1:
        name = argv[1]
        if name not in VARIANTS:
            raise SystemExit(f"unknown variant {name}; choose {sorted(VARIANTS)}")
        out = HERE / "variants" / f"{name}-entry.png"
        out.parent.mkdir(exist_ok=True)
        save(render(name), out)
    else:
        save(render("v1"), HERE / "entry.png")


if __name__ == "__main__":
    main(sys.argv)
