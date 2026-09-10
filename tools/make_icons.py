"""Generate the Rome Trip PWA icons (pure stdlib, no Pillow needed).

Draws a simple terracotta Colosseum facade in cream and writes:
  icons/icon-180.png  (iOS apple-touch-icon)
  icons/icon-192.png  (manifest)
  icons/icon-512.png  (manifest / maskable)

Run:  py tools/make_icons.py
"""
import os
import struct
import zlib

CREAM = (250, 243, 232)   # --cream
TERRA = (193, 68, 14)     # --terracotta  #c1440e
DARK = (150, 48, 6)       # subtle cornice shadow


def render(S):
    """Render the icon at S x S (RGB bytes), background = terracotta."""
    buf = bytearray(bytes(TERRA) * (S * S))

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, int(y0)), min(S, int(y1))):
            base = y * S
            for x in range(max(0, int(x0)), min(S, int(x1))):
                i = (base + x) * 3
                buf[i], buf[i + 1], buf[i + 2] = c

    def disc(cx, cy, r, c):
        r2 = r * r
        for y in range(max(0, int(cy - r)), min(S, int(cy + r) + 1)):
            dy2 = (y - cy) ** 2
            for x in range(max(0, int(cx - r)), min(S, int(cx + r) + 1)):
                if (x - cx) ** 2 + dy2 <= r2:
                    i = (y * S + x) * 3
                    buf[i], buf[i + 1], buf[i + 2] = c

    def arch(x0, x1, ytop, ybot, c):
        r = (x1 - x0) / 2
        cx = (x0 + x1) / 2
        disc(cx, ytop + r, r, c)
        rect(x0, ytop + r, x1, ybot, c)

    # facade body (content kept inside the maskable safe zone, ~0.1..0.9).
    # Top edge steps down twice on the right for a weathered "ruin" look.
    bx0, bx1 = 0.15 * S, 0.85 * S
    rect(bx0, 0.300 * S, 0.60 * S, 0.74 * S, CREAM)
    rect(0.60 * S, 0.360 * S, 0.74 * S, 0.74 * S, CREAM)
    rect(0.74 * S, 0.420 * S, bx1, 0.74 * S, CREAM)
    rect(0.12 * S, 0.74 * S, 0.88 * S, 0.80 * S, CREAM)   # ground base
    rect(bx0, 0.470 * S, bx1, 0.486 * S, DARK)            # cornice line

    gap = 0.018 * S
    n = 4
    aw = ((bx1 - bx0) - gap * (n + 1)) / n
    for k in range(n):
        ax0 = bx0 + gap + k * (aw + gap)
        arch(ax0, ax0 + aw, 0.505 * S, 0.735 * S, TERRA)   # lower tier (full row)
    for k in range(3):
        ax0 = bx0 + gap + k * (aw + gap)
        arch(ax0, ax0 + aw, 0.340 * S, 0.450 * S, TERRA)   # upper tier (stops at the break)
    return buf


def downsample(buf, S, ss):
    O = S // ss
    out = bytearray(O * O * 3)
    n = ss * ss
    for oy in range(O):
        for ox in range(O):
            r = g = b = 0
            for dy in range(ss):
                row = (oy * ss + dy) * S
                for dx in range(ss):
                    i = (row + ox * ss + dx) * 3
                    r += buf[i]
                    g += buf[i + 1]
                    b += buf[i + 2]
            j = (oy * O + ox) * 3
            out[j], out[j + 1], out[j + 2] = r // n, g // n, b // n
    return out, O


def write_png(path, w, h, rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)                       # filter: none
        raw.extend(rgb[y * stride:(y + 1) * stride])

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))  # 8-bit RGB
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(here, "icons")
    os.makedirs(out_dir, exist_ok=True)
    for size, ss in [(180, 4), (192, 4), (512, 2)]:
        big = render(size * ss)
        small, o = downsample(big, size * ss, ss)
        path = os.path.join(out_dir, f"icon-{size}.png")
        write_png(path, o, o, small)
        print("wrote", path, f"({o}x{o})")


if __name__ == "__main__":
    main()
