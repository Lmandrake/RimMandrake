#!/usr/bin/env python3
"""PIPE_CAP_FIX_NORTH_END_FLOATS_FREE (live round 4, 2026-10-26): on the Industrial, Modern and Futuristic atlases the end cap
of a pipe that ends going north (tile S-only, index 4) or south (tile N-only, index 1) floats 7-10 px (0.05-0.08 of the shown
cell) clear of the pipe and is clipped to the pipe's own 18 px width. East/west ends are fine; Scrapper is fine.

Cause: the 2026-10-22 composer (Transient/pile_2026-10-22/pipefit/compose.py, rot()) turned the tall, narrow EndCap piece a
quarter turn with PIL `rotate(expand=False)`. That keeps the w x h canvas, so the turned cap is cropped to w wide, and the
paste offset used the unturned height, so it lands (h - w) / 2 px away from the pipe end. Not a draw offset: the ground pipe is
vanilla Graphic_Linked (no C# offset per link).

Fix, per affected look, on the shipped atlas (so the Modern recolour d95104ac0c and every other tile stay byte-identical):
  tile S-only (cap north) := the W-only tile (cap east) turned a quarter CCW;
  tile N-only (cap south) := the E-only tile (cap west) turned a quarter CCW.
A CCW quarter turn is exactly what the composer meant for those two tiles (its arm and cap angles both come out equal), and it
is the same turn the composer gave the north-south straight, so the pipe's shading matches its neighbours.

The three atlases are owner-KEPT pictures, so a mechanical install is refused (delegation_policy section 3); the fix
goes live only on his ruling:

    python3 fix_ns_end_caps.py                       # dry run: the gap before and after, per look
    python3 fix_ns_end_caps.py --out DIR             # write the fixed atlases to DIR for review
    python3 fix_ns_end_caps.py --install (--owner-said "..." | --by-card "q -> option" | --per-ruling ID)
                                                     # install all three through the art ledger on his ruling

Idempotent: the source tiles (W-only, E-only) are never rewritten, so a second run reproduces the same pixels.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, "..", "..", "..", "Utils", "art"))
WHY = "script:src/RimMandrake/FlowWorks/art_source/pipe/fix_ns_end_caps.py"
PIPE = os.path.normpath(os.path.join(HERE, "..", "..", "Textures", "RimMandrake", "FlowWorks", "Pipe"))
LOOKS = ("Industrial", "Modern", "Futuristic")   # Scrapper's atlas was built another way and has no gap
N, E, S, W = 1, 2, 4, 8


def box(T, i):
    """(y0, x0) of sub-material i in image rows from the top (vanilla Basic: row 0 of the 4x4 grid is the image bottom)."""
    return (3 - i // 4) * T, (i % 4) * T


def get(px, T, i):
    y, x = box(T, i)
    return px[y:y + T, x:x + T]


def gap_rows(px, T, i):
    """Empty rows (alpha <= 128) inside the occupied span of tile i: the cap's float gap."""
    a = get(px, T, i)[..., 3] > 128
    rows = a.sum(1)
    ys = np.nonzero(rows)[0]
    return int(sum(1 for y in range(ys.min(), ys.max() + 1) if rows[y] == 0))


def fixed(px):
    T = px.shape[0] // 4
    out = px.copy()
    for dst, src in ((S, W), (N, E)):
        y, x = box(T, dst)
        out[y:y + T, x:x + T] = np.rot90(get(px, T, src), 1)
    return out


def flag(argv, name):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def main(argv):
    out = flag(argv, "--out")
    owner = {k: flag(argv, "--" + k.replace("_", "-")) for k in ("owner_said", "by_card", "per_ruling")}
    install = "--install" in argv
    if install and not any(owner.values()):
        print("REFUSED: the atlases are owner-KEPT; --install needs his --owner-said, --by-card or --per-ruling")
        return 2
    if out:
        os.makedirs(out, exist_ok=True)
    for look in LOOKS:
        p = os.path.join(PIPE, look, "UniversalPipe_Atlas.png")
        px = np.asarray(Image.open(p).convert("RGBA"))
        T = px.shape[0] // 4
        new = fixed(px)
        print("%s: gap rows S-only %d -> %d, N-only %d -> %d" % (
            look, gap_rows(px, T, S), gap_rows(new, T, S), gap_rows(px, T, N), gap_rows(new, T, N)))
        img = Image.fromarray(new, "RGBA")
        if out:
            img.save(os.path.join(out, "%s_UniversalPipe_Atlas.png" % look))
        if install:
            sys.path.insert(0, ART)
            import io
            import artledger as L
            b = io.BytesIO()
            img.save(b, "PNG")
            mod, rel = L.locate(p)
            print("  ", L.install(mod, rel, L.store_put_bytes(b.getvalue()), reason=WHY,
                                  provenance={"kind": "derived", "job": "PIPE_CAP_FIX_NORTH_END_FLOATS_FREE"}, **owner))
    if not (out or install):
        print("dry run; --out DIR writes candidates, --install installs on his ruling")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
