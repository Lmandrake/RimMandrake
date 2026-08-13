#!/usr/bin/env python3
"""
pnglib.py — minimal pure-stdlib PNG read/write/measure for WreckedMachines.

WHY THIS EXISTS INSTEAD OF PILLOW
=================================
Pillow is not installed in the WSL environment this project's tooling runs in,
and `pip` is not available there either (`python3 -m pip` -> "No module named
pip"). `src/RimMandrake/Utils/animal_contact_sheet.py` sidesteps that by declaring itself
Windows-only; this toolchain cannot, because the art pipeline needs to run in
the same place as the deploy script and the def authoring.

So: decode, measure, composite and encode by hand, on stdlib `zlib` and
`struct` alone. That is ~150 lines and it removes an install step from every
future contributor's path. If Pillow ever becomes available, this module can be
swapped for a thin wrapper without touching its callers.

WHAT IT SUPPORTS
================
8-bit PNGs, colour types 0/2/3/4/6 (grey, RGB, palette, grey+alpha, RGBA),
including `tRNS` transparency on palette images, and **both** non-interlaced
and Adam7-interlaced data.

Adam7 is not optional here, and that was a surprise: **Vanilla Furniture
Expanded - Factory ships its machine textures interlaced.** The first run of
`grab_source_art.py` against the Automated Smelter rejected all four facings.
Any tool in this pipeline that assumes non-interlaced will fail on the very
first machine we care about, so it is handled properly rather than refused.

16-bit files are still refused loudly rather than returning quiet garbage.
"""

import struct
import zlib

__all__ = ["read_png", "write_png", "write_rgba", "resize_rgba", "measure", "scale", "checkerboard",
           "paste", "contact_sheet", "PngError"]


class PngError(Exception):
    pass


# --------------------------------------------------------------------- decode
def _unfilter(raw, pos, w, h, channels, path):
    """Undo PNG row filters for one image (or one Adam7 pass).

    Returns (pixel bytes, position in `raw` just past this image) so the caller
    can walk the seven interlace passes back to back out of a single stream.
    """
    stride = w * channels
    out = bytearray(h * stride)
    prev = bytearray(stride)
    for y in range(h):
        filt = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos + stride]); pos += stride
        if filt == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 255
        elif filt == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif filt == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif filt == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 255
        elif filt != 0:
            raise PngError("%s: unknown row filter %d" % (path, filt))
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out, pos


def read_png(path):
    """Return (width, height, bytearray of RGBA) for an 8-bit PNG."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\x1a"[:1] + b"PNG\r\n\x1a\n":
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise PngError("%s: not a PNG" % path)
    pos, idat, plte, trns = 8, b"", None, None
    w = h = bitdepth = colortype = interlace = None
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            w, h, bitdepth, colortype, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
        elif ctype == b"IDAT":
            idat += chunk
        elif ctype == b"PLTE":
            plte = chunk
        elif ctype == b"tRNS":
            trns = chunk
        elif ctype == b"IEND":
            break
        pos += 12 + length
    if bitdepth != 8:
        raise PngError("%s: %d-bit PNG; only 8-bit is supported" % (path, bitdepth))

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colortype]
    raw = zlib.decompress(idat)

    if not interlace:
        out = _unfilter(raw, 0, w, h, channels, path)[0]
    else:
        # Adam7: seven sub-images, each independently filtered, scattered back
        # onto the full grid. Pass geometry per the PNG spec.
        XSTART = (0, 4, 0, 2, 0, 1, 0)
        YSTART = (0, 0, 4, 0, 2, 0, 1)
        XSTEP = (8, 8, 4, 4, 2, 2, 1)
        YSTEP = (8, 8, 8, 4, 4, 2, 2)
        out = bytearray(w * h * channels)
        pos = 0
        for p_i in range(7):
            pw = (w - XSTART[p_i] + XSTEP[p_i] - 1) // XSTEP[p_i]
            ph = (h - YSTART[p_i] + YSTEP[p_i] - 1) // YSTEP[p_i]
            if pw <= 0 or ph <= 0:
                continue
            sub, pos = _unfilter(raw, pos, pw, ph, channels, path)
            for sy in range(ph):
                dy = YSTART[p_i] + sy * YSTEP[p_i]
                for sx in range(pw):
                    dx = XSTART[p_i] + sx * XSTEP[p_i]
                    s = (sy * pw + sx) * channels
                    d = (dy * w + dx) * channels
                    out[d:d + channels] = sub[s:s + channels]

    rgba = bytearray(w * h * 4)
    for i in range(w * h):
        px = out[i * channels:(i + 1) * channels]
        if colortype == 6:
            r, g, b, a = px
        elif colortype == 2:
            r, g, b = px; a = 255
        elif colortype == 0:
            r = g = b = px[0]; a = 255
        elif colortype == 4:
            r = g = b = px[0]; a = px[1]
        else:
            idx = px[0]
            r, g, b = plte[idx * 3:idx * 3 + 3]
            a = trns[idx] if (trns and idx < len(trns)) else 255
        rgba[i * 4:i * 4 + 4] = bytes((r, g, b, a))
    return w, h, rgba


# --------------------------------------------------------------------- encode
def write_png(path, w, h, rgb):
    """Write an opaque 8-bit RGB PNG (used for contact sheets only)."""
    raw = b"".join(b"\x00" + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))

    def chunk(tag, payload):
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)


def write_rgba(path, w, h, rgba):
    """Write an 8-bit RGBA PNG. This is the one that ships art to the game."""
    stride = w * 4
    raw = b"".join(b"\x00" + bytes(rgba[y * stride:(y + 1) * stride]) for y in range(h))

    def chunk(tag, payload):
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)


def resize_rgba(w, h, rgba, nw, nh):
    """Quality resize with premultiplied alpha.

    Two things matter here and nearest-neighbour gets both wrong:

    * **Area averaging on downscale.** Conforming generated art means shrinking
      ~1500px images to ~600px. Point-sampling that throws away 5 of every 6
      pixels and turns fine detail into aliased noise.
    * **Premultiplication.** Averaging straight RGBA across a soft edge blends
      the colour of fully-transparent pixels — usually black — into the visible
      fringe, which is where the classic dark halo around cut-out art comes
      from. Multiply by alpha first, average, then divide back out.
    """
    out = bytearray(nw * nh * 4)
    x_edges = [x * w // nw for x in range(nw + 1)]
    y_edges = [y * h // nh for y in range(nh + 1)]
    for oy in range(nh):
        y0, y1 = y_edges[oy], max(y_edges[oy + 1], y_edges[oy] + 1)
        for ox in range(nw):
            x0, x1 = x_edges[ox], max(x_edges[ox + 1], x_edges[ox] + 1)
            r = g = b = a = n = 0
            for sy in range(y0, y1):
                base = sy * w
                for sx in range(x0, x1):
                    i = (base + sx) * 4
                    pa = rgba[i + 3]
                    r += rgba[i] * pa
                    g += rgba[i + 1] * pa
                    b += rgba[i + 2] * pa
                    a += pa
                    n += 1
            o = (oy * nw + ox) * 4
            if a:
                out[o] = min(255, r // a)
                out[o + 1] = min(255, g // a)
                out[o + 2] = min(255, b // a)
                out[o + 3] = min(255, a // n)
    return out


# -------------------------------------------------------------------- measure
def measure(path):
    """Everything the validator and the art brief need to know about one file."""
    w, h, d = read_png(path)
    xs_min = ys_min = 10 ** 9
    xs_max = ys_max = -1
    opaque = semi = coloured = 0
    lum = [0] * 256
    for y in range(h):
        row = y * w
        for x in range(w):
            i = (row + x) * 4
            a = d[i + 3]
            if a == 0:
                continue
            if x < xs_min: xs_min = x
            if x > xs_max: xs_max = x
            if y < ys_min: ys_min = y
            if y > ys_max: ys_max = y
            if a == 255: opaque += 1
            else: semi += 1
            r, g, b = d[i], d[i + 1], d[i + 2]
            if max(r, g, b) - min(r, g, b) > 12:
                coloured += 1
            lum[(r * 299 + g * 587 + b * 114) // 1000] += 1
    total = opaque + semi
    if total == 0:
        raise PngError("%s: image is fully transparent" % path)
    return {
        "file": path,
        "width": w, "height": h,
        "bbox": [xs_min, ys_min, xs_max, ys_max],
        "bbox_wh": [xs_max - xs_min + 1, ys_max - ys_min + 1],
        "opaque_px": opaque, "semi_px": semi,
        "coverage_pct": round(100.0 * total / (w * h), 2),
        "coloured_px": coloured,
        "is_greyscale": coloured == 0,
        "has_real_alpha": total < w * h,
        "black_pct": round(100.0 * sum(lum[:10]) / total, 1),
        "light_pct": round(100.0 * sum(lum[224:]) / total, 1),
    }


# ------------------------------------------------------------------ compositing
def scale(w, h, rgba, nw, nh):
    """Nearest-neighbour resize. Good enough for review sheets."""
    out = bytearray(nw * nh * 4)
    for y in range(nh):
        sy = y * h // nh
        for x in range(nw):
            si = (sy * w + (x * w // nw)) * 4
            di = (y * nw + x) * 4
            out[di:di + 4] = rgba[si:si + 4]
    return out


def checkerboard(w, h, light=130, dark=90, cell=8):
    """Alpha PNGs are invisible on white. Every sheet gets a checkerboard."""
    c = bytearray(w * h * 3)
    for y in range(h):
        for x in range(w):
            v = dark if ((x // cell + y // cell) % 2) else light
            i = (y * w + x) * 3
            c[i:i + 3] = bytes((v, v, v))
    return c


def paste(canvas, cw, ox, oy, tw, th, rgba):
    """Alpha-over an RGBA tile onto an RGB canvas."""
    for y in range(th):
        for x in range(tw):
            s = (y * tw + x) * 4
            a = rgba[s + 3]
            if not a:
                continue
            d = ((oy + y) * cw + ox + x) * 3
            if a == 255:
                canvas[d:d + 3] = rgba[s:s + 3]
            else:
                for k in range(3):
                    canvas[d + k] = (rgba[s + k] * a + canvas[d + k] * (255 - a)) // 255


def contact_sheet(paths, out_path, cell=256, cols=4):
    """Tile images onto one reviewable sheet. Missing files render as an X."""
    rows = (len(paths) + cols - 1) // cols
    W, H = cols * cell, rows * cell
    canvas = checkerboard(W, H)
    for n, p in enumerate(paths):
        ox, oy = (n % cols) * cell, (n // cols) * cell
        try:
            w, h, d = read_png(p)
            paste(canvas, W, ox, oy, cell, cell, scale(w, h, d, cell, cell))
        except Exception:
            for t in range(cell):                       # a red X = missing/unreadable
                for dx, dy in ((t, t), (t, cell - 1 - t)):
                    i = ((oy + dy) * W + ox + dx) * 3
                    canvas[i:i + 3] = b"\xc0\x20\x20"
    write_png(out_path, W, H, canvas)
    return out_path
