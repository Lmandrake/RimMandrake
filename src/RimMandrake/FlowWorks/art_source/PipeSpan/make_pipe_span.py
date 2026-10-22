"""D5 (joints study 2026-10-22): a pipe pole's span draws the LOOK'S OWN PIPE, not GSS's dark aerial wire.

  python3 src/RimMandrake/FlowWorks/art_source/PipeSpan/make_pipe_span.py [--dry-run]

Writes RimMandrake/FlowWorks/PipePole/<Look>/PipeSpan.png, the art-contract path RM_PipePoles.xml's spanTexPath names and
GSS's AerialMaterials.PipeMats looks up silently (until now it was never installed, so every pipe span drew the look's
power wire: "the span reads as an electric line"). Derived, not drawn: a window of the look's own ground pipe (the E-W
straight tile of Pipe/<Look>/UniversalPipe_Atlas.png, rows of its opaque band), so no new design is introduced.
GSS maps a span strip 4:1 (u advances length / (4 x mesh width)), so the window is 4 x the band height long, chosen where
its two ends match (a plain stretch), which makes it tile. Resampled to 128 x 32 like GSS's own SpanWire.png.
Installed through the art ledger (reason script:<this path>).
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
TILE = 176          # the atlas is 4 x 4 tiles of 176 px
EW = (2, 1)         # Graphic_Linked index 10 (E + W): column 2, row 1 from the top
OUT = (128, 32)


def band_of(tile):
    rows = np.where(tile[:, :, 3].max(1) > 8)[0]
    return int(rows.min()), int(rows.max())


def seam(a):
    a = a.astype(np.float32)
    pm = np.concatenate([a[:, :, :3] * (a[:, :, 3:4] / 255.0), a[:, :, 3:4]], axis=2)
    return float(np.abs(pm[:, 0] - pm[:, -1]).mean()), float(np.abs(np.diff(pm, axis=1)).mean())


def span_strip(atlas):
    cx, cy = EW
    tile = atlas[cy * TILE:(cy + 1) * TILE, cx * TILE:(cx + 1) * TILE]
    r0, r1 = band_of(tile)
    band = tile[r0:r1 + 1]
    h = band.shape[0]
    n = 4 * h
    twice = np.concatenate([band, band], axis=1).astype(np.float32)
    best = None
    for x0 in range(TILE):
        d = float(np.abs(twice[:, x0] - twice[:, x0 + n]).mean())
        if best is None or d < best[0]:
            best = (d, x0)
    x0 = best[1]
    win = np.concatenate([band, band], axis=1)[:, x0:x0 + n]
    img = Image.fromarray(win, "RGBA").resize(OUT, Image.LANCZOS)
    return np.asarray(img), {"band_rows": [r0, r1], "window": [x0, n], "girth_cells": round(h / float(TILE), 4)}


def main(argv=None):
    import artledger as L
    dry = "--dry-run" in (argv or sys.argv[1:])
    for look in LOOKS:
        atlas = np.asarray(Image.open(os.path.join(TEX, "Pipe", look, "UniversalPipe_Atlas.png")).convert("RGBA"))
        out, prov = span_strip(atlas)
        e, d = seam(out)
        if e > max(1.5 * d, d + 4.0):
            print("FAILED  %s  seam %.1f vs %.1f" % (look, e, d))
            return 1
        dest = os.path.join(TEX, "PipePole", look, "PipeSpan.png")
        b = io.BytesIO()
        Image.fromarray(out, "RGBA").save(b, "PNG")
        r = L.install_bytes(dest, b.getvalue(), reason="script:" + REL_SCRIPT, dry_run=dry, provenance=dict(prov, source="Pipe/%s/UniversalPipe_Atlas.png" % look))
        print("%-10s %s  seam %.1f (adj %.1f)  %s  %s" % (look, "x".join(map(str, OUT)), e, d, prov, r.get("status")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
