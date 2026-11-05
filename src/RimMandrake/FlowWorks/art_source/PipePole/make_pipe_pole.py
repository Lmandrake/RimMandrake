"""PIPE_POLE_REDRAW_NOT_A_POWER_POLE: each pipe-pole look gets its own pipe-clamp support, never the GSS power mast.

  python3 src/RimMandrake/FlowWorks/art_source/PipePole/make_pipe_pole.py [--dry-run]

Sources: raw/<Look>_PipePole_raw.png, 1024x1536 RGB on a magenta (#ff00ff) key, exactly as Codex returned them. Each is a Codex image edit (2026-11-05) of that look's own
GSS AerialMast (3x, centred on a 1024x1536 magenta canvas) with the look's ground pipe tile as image 2: crossarm, braces
and insulators removed, a saddle clamp gripping a short stub of the look's pipe put at the head. Keyed HERE (key_out): chroma_key.py's despill
turned the Scrapper wood green and its no-despill mode left magenta fringes on the thin wires, so this script un-mixes the
key from each edge pixel instead (C = a*F + (1-a)*K solved for F), which leaves opaque colours untouched.

This script crops the 768-wide pole column, downsamples to 256x512 (premultiplied, so no dark fringe), then REGISTERS the
pipe stub's centre row to SEAT_ROW: the rows between the stub and the canvas bottom are resampled linearly so the base stays
on the bottom row. SEAT_ROW is RM_PipePole's attachZ (RM_PipePoles.xml, 2.66 cells): drawSize (2,4) at drawOffset z 1.5
puts the texture over z -0.5..3.5 at 128 px a cell, so the span seat sits (3.5 - 2.66) * 128 = 107.5 rows from the top.
GSS has no PoleGeometryTable row for RM_PipePole, so the def's attachZ is the seat for every look.
Installed through the art ledger at RimMandrake/FlowWorks/PipePole/<Look>/PipePole.png (reason script:<this path>).
"""
import io
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
TEX = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Textures", "RimMandrake", "FlowWorks")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
REL_SCRIPT = os.path.relpath(os.path.abspath(__file__), REPO).replace(os.sep, "/")
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
OUT = (256, 512)
ATTACH_Z = 2.66
SEAT_ROW = (3.5 - ATTACH_Z) * 128.0     # 107.5


def stub_centre(alpha, limit):
    """The pipe stub's centre row and diameter, read at the stub's two ends (the widest opaque columns above `limit`)."""
    cols = np.where(alpha[:limit].max(0) > 128)[0]
    out = []
    for c in (cols.min() + 4, cols.max() - 4):
        r = np.where(alpha[:limit, c] > 128)[0]
        out.append(((r.min() + r.max()) / 2.0, r.max() - r.min() + 1))
    return sum(o[0] for o in out) / 2.0, max(o[1] for o in out)


KEY = np.array([255.0, 0.0, 255.0])
M_OPAQUE, M_CLEAR = 0.12, 0.62          # magenta-ness min(R,B)-G (0..1): below opaque, above fully key


def key_out(rgb):
    """RGB on the magenta key -> RGBA: alpha from magenta-ness, edge colours un-mixed from the key."""
    c = rgb[:, :, :3].astype(np.float32)
    m = (np.minimum(c[:, :, 0], c[:, :, 2]) - c[:, :, 1]) / 255.0
    a = np.clip((M_CLEAR - m) / (M_CLEAR - M_OPAQUE), 0.0, 1.0)
    f = (c - (1.0 - a[:, :, None]) * KEY) / np.maximum(a[:, :, None], 1e-3)
    f = np.where(a[:, :, None] > 1e-3, np.clip(f, 0, 255), 0)
    return np.concatenate([f, a[:, :, None] * 255.0], axis=2).astype(np.uint8)


def premul_resize(a, size):
    f = a.astype(np.float32) / 255.0
    pm = np.concatenate([f[:, :, :3] * f[:, :, 3:4], f[:, :, 3:4]], axis=2)
    chans = [np.asarray(Image.fromarray(pm[:, :, i]).resize(size, Image.LANCZOS)) for i in range(4)]
    return np.clip(np.stack(chans, axis=2), 0.0, 1.0)


def vremap(pm, src_seat, dst_seat):
    """Rows 0..dst_seat take 0..src_seat; dst_seat..H-1 take src_seat..H-1 (linear, premultiplied)."""
    h = pm.shape[0]
    y = np.arange(h, dtype=np.float32) + 0.5
    src = np.where(y <= dst_seat, y * src_seat / dst_seat,
                   src_seat + (y - dst_seat) * (h - src_seat) / (h - dst_seat)) - 0.5
    y0 = np.clip(np.floor(src).astype(int), 0, h - 1)
    y1 = np.clip(y0 + 1, 0, h - 1)
    t = (src - np.floor(src))[:, None, None]
    return pm[y0] * (1 - t) + pm[y1] * t


def unpremul(pm):
    a = pm[:, :, 3:4]
    rgb = np.where(a > 1e-4, pm[:, :, :3] / np.maximum(a, 1e-4), 0.0)
    return (np.clip(np.concatenate([rgb, a], axis=2), 0, 1) * 255.0 + 0.5).astype(np.uint8)


def pole(look):
    raw = np.asarray(Image.open(os.path.join(HERE, "raw", "%s_PipePole_raw.png" % look)).convert("RGB"))
    raw = key_out(raw)[:, 128:896]                                          # the 768-wide column the 3x mast was placed in
    pm = premul_resize(raw, OUT)
    seat = stub_centre((pm[:, :, 3] * 255).astype(int), OUT[1] // 2)[0] + 0.5   # pixel index -> distance from the top
    src = seat
    for _ in range(3):                    # the resampled edge moves the measured centre a little: correct and redo
        out = unpremul(vremap(pm, src, SEAT_ROW))
        got, diam = stub_centre(out[:, :, 3].astype(int), OUT[1] // 2)
        got += 0.5
        if abs(got - SEAT_ROW) <= 0.5:
            break
        src += (got - SEAT_ROW) * src / SEAT_ROW
    return out, {"seat_row_raw": round(float(seat), 2), "seat_row": round(float(got), 2), "stub_px": int(diam),
                 "attachZ": ATTACH_Z, "source": "art_source/PipePole/raw/%s_PipePole_raw.png" % look}


def main(argv=None):
    import artledger as L
    dry = "--dry-run" in (argv or sys.argv[1:])
    for look in LOOKS:
        out, prov = pole(look)
        if abs(prov["seat_row"] - SEAT_ROW) > 1.5:
            print("FAILED  %s  seat row %.1f, want %.1f" % (look, prov["seat_row"], SEAT_ROW))
            return 1
        dest = os.path.join(TEX, "PipePole", look, "PipePole.png")
        b = io.BytesIO()
        Image.fromarray(out, "RGBA").save(b, "PNG", optimize=True)
        r = L.install_bytes(dest, b.getvalue(), reason="script:" + REL_SCRIPT, dry_run=dry, provenance=prov)
        print("%-10s %s  %s" % (look, prov, r.get("status")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
