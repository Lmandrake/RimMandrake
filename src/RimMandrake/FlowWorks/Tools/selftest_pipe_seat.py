#!/usr/bin/env python3
"""selftest_pipe_seat.py -- SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE: a fitting set on a pipe sits on the DRAWN centreline.

Owner 2026-10-23: "Sprinkler on a curved pipe segment is no longer on pipe." The head (and the pipe faucet) are printed
at RM_PipeSeatMath.Seat(mask, look) from the cell centre. This test reads that table out of the C# source and measures
every shipped universal-pipe atlas (Textures/.../Pipe/<Look>/UniversalPipe_Atlas.png, vanilla 4x4 Graphic_Linked layout:
704 px atlas, 176 px tile, 22 px padding, 132 px shown cell, mask bits N=1 E=2 S=4 W=8, row 0 at the bottom):
  1. elbows (masks 3, 6, 9, 12): the seat lies within 1 px of the midpoint of the pipe's alpha run along the cell
     diagonal toward the bend (the drawn centreline); the old cell-centre seat does NOT (can-fail: the bug);
  2. the lone stub (mask 0): the seat is the drawn flange's centre within 1 px (centred since Scrapper v3; v2's sat 4 px SE);
     every other mask: the seat is (0,0), the pipe covers it, and each arm's cross-section is centred within 1 px;
  3. can-fail: a seat moved 2 px along the diagonal fails check 1.
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
SRC = MOD / "Source" / "Sprinklers" / "RM_PipeSeatMath.cs"
TEX = MOD / "Textures" / "RimMandrake" / "FlowWorks" / "Pipe"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
T, P, C = 176, 22, 132
PX = 1.0 / C
N, E, S, W = 1, 2, 4, 8
fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def num(tok):
    """A C# float literal or quotient of two ("0.5f", "2f / 3f")."""
    parts = [float(t.strip().rstrip("f")) for t in tok.split("/")]
    return parts[0] / parts[1] if len(parts) == 2 else parts[0]


def arcs_from_source():
    """{look: (k, r)} parsed from RM_PipeSeatMath.ElbowArc's switch (case labels fall through to one k/r line)."""
    body = SRC.read_text(encoding="utf-8")
    body = body[body.index("public static bool ElbowArc"):body.index("public static bool IsElbow")]
    out, pending = {}, []
    for line in body.splitlines():
        m = re.search(r'case "(\w+)":', line)
        if m:
            pending.append(m.group(1))
        m = re.search(r"k = ([^;]+); r = ([^;]+); return true;", line)
        if m:
            for look in pending:
                out[look] = (num(m.group(1)), num(m.group(2)))
            pending = []
    return out


def is_elbow(mask):
    return mask in (N | E, E | S, S | W, W | N)


def stub_px_from_source():
    m = re.search(r"LoneStubScrapperPx = ([\d.]+)f;", SRC.read_text(encoding="utf-8"))
    return float(m.group(1)) if m else None


STUB = {"Scrapper": stub_px_from_source() or 0.0}


def seat(mask, look, arcs):
    if mask == 0:
        d = STUB.get(look, 0.0) / C
        return d, -d
    if not is_elbow(mask) or look not in arcs:
        return 0.0, 0.0
    k, r = arcs[look]
    d = k - r / math.sqrt(2)
    return d * (1 if mask & E else -1), d * (1 if mask & N else -1)


def cell_alpha(look, mask):
    im = Image.open(TEX / look / "UniversalPipe_Atlas.png").convert("RGBA")
    if im.size != (4 * T, 4 * T):            # a look authored at another size (Scrapper v3: 1408 px) is judged in 704 px units
        assert im.size[0] == im.size[1] and im.size[0] % (4 * T) == 0, im.size
        im = im.resize((4 * T, 4 * T), Image.BOX)
    a = np.asarray(im).astype(float)[..., 3] / 255
    col, row = mask % 4, 3 - mask // 4
    return a[row * T + P:row * T + P + C, col * T + P:col * T + P + C]


def alpha_at(cell, x, z):
    """Alpha at cell-relative (x east, z north) from the centre, cells."""
    px, py = (0.5 + x) * C, (0.5 - z) * C
    xi, yi = min(C - 1, max(0, int(px))), min(C - 1, max(0, int(py)))
    return cell[yi, xi]


def diag_mid(cell, sx, sz):
    """Midpoint (distance from centre, cells) of the opaque run along the diagonal toward (sx, sz)."""
    ts = np.linspace(0, math.sqrt(2) / 2, 2000)
    on = [t for t in ts if alpha_at(cell, sx * t / math.sqrt(2), sz * t / math.sqrt(2)) > 0.5]
    return (min(on) + max(on)) / 2 if on else None


def run_mid(vals):
    idx = np.where(vals > 0.5)[0]
    return (idx.min() + idx.max() + 1) / 2 if len(idx) else None


def main():
    arcs = arcs_from_source()
    check(set(arcs) == set(LOOKS), "ElbowArc knows exactly the four pipe looks: %s" % sorted(arcs))
    for look in LOOKS:
        if look not in arcs:
            continue
        for mask in range(16):
            cell = cell_alpha(look, mask)
            x, z = seat(mask, look, arcs)
            if is_elbow(mask):
                sx, sz = (1 if mask & E else -1), (1 if mask & N else -1)
                m = diag_mid(cell, sx, sz)
                got = math.hypot(x, z)
                check(m is not None and abs(got - m) <= PX,
                      "%s mask %2d elbow: seat %.4f vs drawn centreline %.4f along the diagonal (|d| %.2f px)"
                      % (look, mask, got, m or -1, abs(got - (m or 0)) * C))
                check(m is not None and m > 2 * PX, "%s mask %2d: can-fail, the cell centre is off the bend" % (look, mask))
                check(m is not None and abs(got + 2 * PX - m) > PX, "%s mask %2d: can-fail, a seat 2 px out fails" % (look, mask))
                check(alpha_at(cell, x, z) > 0.5, "%s mask %2d: the pipe is drawn under the seat" % (look, mask))
            elif mask == 0:
                ys, xs = np.where(cell > 0.5)
                bx, bz = ((xs.min() + xs.max() + 1) / 2 - C / 2) / C, (C / 2 - (ys.min() + ys.max() + 1) / 2) / C
                check(abs(x - bx) <= PX and abs(z - bz) <= PX,
                      "%s mask  0 lone flange: seat (%.4f,%.4f) vs drawn centre (%.4f,%.4f)" % (look, x, z, bx, bz))
            else:
                check((x, z) == (0.0, 0.0), "%s mask %2d: no bend, seat (0,0)" % (look, mask))
                band = cell[C // 2 - 1:C // 2 + 1, C // 2 - 1:C // 2 + 1].max()
                check(band > 0.5, "%s mask %2d: the pipe covers the cell centre" % (look, mask))
                # each arm's cross-section, 30 px out from the centre (clear of any other arm), is centred within 1 px
                for bit, name in ((N, "N"), (E, "E"), (S, "S"), (W, "W")):
                    if not mask & bit:
                        continue
                    if bit in (N, S):
                        row = C // 2 - 30 if bit == N else C // 2 + 30
                        mid = run_mid(cell[row - 1:row + 1, :].max(0))
                    else:
                        colx = C // 2 + 30 if bit == E else C // 2 - 30
                        mid = run_mid(cell[:, colx - 1:colx + 1].max(1))
                    check(mid is not None and abs(mid - C / 2) <= 1,
                          "%s mask %2d: %s arm centred on the cell axis (%.1f of %d px)" % (look, mask, name, mid or -1, C))
    print("%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
