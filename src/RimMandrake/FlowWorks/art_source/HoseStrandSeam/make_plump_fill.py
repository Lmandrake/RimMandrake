"""D1 (joints study 2026-10-22): the plump hose strand must FILL its strip, centred, like HoseMath.PlumpBand (62/64) says.

  python3 src/RimMandrake/FlowWorks/art_source/HoseStrandSeam/make_plump_fill.py [--dry-run]

Every installed Strand_Plump.png was opaque on only ~9-13 of its 64 rows (Modern's at rows 13-21, off the centreline), while
the ribbon is sized as if the strand filled rows 1-62: a flowing hose drew ~0.06 cell, THINNER than the empty flat one (owner
2026-10-22: "Hoses need to be twice as thick, too thin to see now."). Fix, keeping the look: crop each strand to its visible
rows (the half-opaque band), resample that band VERTICALLY (premultiplied, Lanczos) to 62 rows, place it at rows 1-62; columns are
untouched, so a seamless strand stays seamless. Installed through the art ledger (reason script:<this path>). Idempotent:
a strand already filling >= 54 rows within 2 rows of centre is left alone. The game draws it at ~0.23 cell, a handful of
screen pixels, so the source band's resolution is not what limits it.
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
TOP, ROWS = 1, 62


def band(a):
    """(first, last) rows that are at least half opaque across the strip (the measure validation_hose_offline uses)."""
    rows = np.where((a[:, :, 3] > 128).mean(1) > 0.5)[0]
    return (int(rows.min()), int(rows.max())) if len(rows) else (None, None)


def fills(a):
    r0, r1 = band(a)
    if r0 is None:
        return False
    h = a.shape[0]
    return (r1 - r0 + 1) >= 54 and abs((r0 + r1) / 2.0 - (h - 1) / 2.0) <= 2


def refill(a):
    h, w, _ = a.shape
    h0, h1 = band(a)
    r0, r1 = h0, h1   # the solid band (its soft rows, stretched 5x, would blur the edge into a halo)
    crop = a[r0:r1 + 1].astype(np.float32)
    pm = crop.copy()
    pm[:, :, :3] *= pm[:, :, 3:4] / 255.0
    chans = [np.asarray(Image.fromarray(pm[:, :, k]).resize((w, ROWS), Image.LANCZOS)) for k in range(4)]
    pm2 = np.stack(chans, axis=2).clip(0, 255)
    al = pm2[:, :, 3:4]
    rgb = np.where(al > 0.5, pm2[:, :, :3] * 255.0 / np.maximum(al, 1e-3), 0)
    out = np.zeros((h, w, 4), np.uint8)
    out[TOP:TOP + ROWS] = np.concatenate([rgb, al], axis=2).clip(0, 255).astype(np.uint8)
    return out, (r0, r1)


def main(argv=None):
    import artledger as L
    dry = "--dry-run" in (argv or sys.argv[1:])
    for root, _, files in sorted(os.walk(os.path.join(TEX, "Hose"))):
        for f in sorted(files):
            if f != "Strand_Plump.png":
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, TEX)
            a = np.asarray(Image.open(p).convert("RGBA"))
            if fills(a):
                print("ok      %s  band %s" % (rel, band(a)))
                continue
            out, src = refill(a)
            if not fills(out):
                print("FAILED  %s  band now %s" % (rel, band(out)))
                return 1
            b = io.BytesIO()
            Image.fromarray(out, "RGBA").save(b, "PNG")
            r = L.install_bytes(p, b.getvalue(), reason="script:" + REL_SCRIPT, dry_run=dry,
                                provenance={"fix": "plump strand fills its strip (D1)", "source_rows": list(src)})
            print("fixed   %s  band %s -> %s  %s" % (rel, band(a), band(out), r.get("status")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
