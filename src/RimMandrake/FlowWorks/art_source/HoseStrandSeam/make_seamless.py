"""Make the hose strand textures tile seamlessly (HO5_hose_art_sane: 'Hose/Strand_Plump: seam 10.4 vs adjacent 2.4').

  python3 src/RimMandrake/FlowWorks/art_source/HoseStrandSeam/make_seamless.py [--dry-run]

A strand is drawn repeated along the hose, so its column 0 must continue its last column. Two defects, same fix:
  Hose/Strand_Plump                 column 0 at half alpha (a faint cut line every tile)
  Hose/Styles/Modern/Strand_Plump   last 8 columns empty, one half-alpha column each end (a visible gap every tile)
Fix, keeping the look: drop the soft/empty end columns, cross-fade the head over the tail (N columns, premultiplied) so the
strip is periodic, then resample horizontally back to 256 (a 3-8 % stretch of a uniform weave). Rows are untouched.
Installed through the art ledger (artledger.install_bytes, reason script:<this path>). Idempotent: a strand that already
passes validation_hose_offline.png_sanity's seam test is left alone.
"""
import io
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
FW = os.path.join(REPO, "src", "RimMandrake", "FlowWorks")
TEX = os.path.join(FW, "Textures", "RimMandrake", "FlowWorks")
sys.path.insert(0, FW)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
REL_SCRIPT = os.path.relpath(os.path.abspath(__file__), REPO).replace(os.sep, "/")
FADE = 8


def seam(a):
    """validation_hose_offline's own metric: (edge, adjacent) on premultiplied RGBA."""
    a = a.astype(np.float32)
    pm = np.concatenate([a[:, :, :3] * (a[:, :, 3:4] / 255.0), a[:, :, 3:4]], axis=2)
    return float(np.abs(pm[:, 0] - pm[:, -1]).mean()), float(np.abs(np.diff(pm, axis=1)).mean())


def is_seamed(a):
    edge, adj = seam(a)
    return edge > max(1.5 * adj, adj + 4.0)


def make_periodic(a):
    """Trim end columns whose alpha mass is under 90 % of the median column, cross-fade, resample to the old width."""
    h, w, _ = a.shape
    mass = a[:, :, 3].astype(np.float32).sum(0)
    full = 0.9 * float(np.median(mass))
    lo, hi = 0, w
    while lo < w and mass[lo] < full:
        lo += 1
    while hi > lo and mass[hi - 1] < full:
        hi -= 1
    core = a[:, lo:hi].astype(np.float32)
    n = min(FADE, core.shape[1] // 4)
    pm = core.copy()
    pm[:, :, :3] *= pm[:, :, 3:4] / 255.0
    body = pm[:, : core.shape[1] - n].copy()
    tail = pm[:, core.shape[1] - n:]
    for x in range(n):
        t = (x + 0.5) / n                      # 0 -> the tail continues; 1 -> the head as it was
        body[:, x] = (1 - t) * tail[:, x] + t * pm[:, x]
    al = body[:, :, 3:4]
    rgb = np.where(al > 0, body[:, :, :3] * 255.0 / np.maximum(al, 1e-3), 0)
    out = np.concatenate([rgb, al], axis=2).clip(0, 255).astype(np.uint8)
    # horizontal resample, wrap-aware: pad one period each side, resize, crop the middle
    tiled = np.concatenate([out, out, out], axis=1)
    big = Image.fromarray(tiled, "RGBA").resize((w * 3, h), Image.LANCZOS)
    return np.asarray(big)[:, w: 2 * w].copy(), (lo, hi, n)


def main(argv=None):
    import artledger as L
    dry = "--dry-run" in (argv or sys.argv[1:])
    rels = []
    for root, _, files in os.walk(os.path.join(TEX, "Hose")):
        rels += [os.path.join(root, f) for f in files if f.startswith("Strand") and f.endswith(".png")]
    for p in sorted(rels):
        a = np.asarray(Image.open(p).convert("RGBA"))
        rel = os.path.relpath(p, TEX)
        if not is_seamed(a):
            print("ok      %s  edge %.1f adj %.1f" % ((rel,) + seam(a)))
            continue
        out, (lo, hi, n) = make_periodic(a)
        e, d = seam(out)
        if is_seamed(out):
            print("FAILED  %s  still edge %.1f adj %.1f" % (rel, e, d))
            return 1
        b = io.BytesIO()
        Image.fromarray(out, "RGBA").save(b, "PNG")
        r = L.install_bytes(p, b.getvalue(), reason="script:" + REL_SCRIPT, dry_run=dry,
                            provenance={"fix": "seamless tiling", "kept_cols": [lo, hi], "fade": n})
        print("fixed   %s  %s  edge %.1f -> %.1f (adj %.1f)  cols %d..%d fade %d  %s" % (
            rel, "x".join(map(str, out.shape[1::-1])), seam(a)[0], e, d, lo, hi, n, r.get("status")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
