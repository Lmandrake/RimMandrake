#!/usr/bin/env python3
"""Head truth: the deterministic gate a `head` template card passes before any model is asked.

Code measures two things a reviewer must not re-estimate (template `head`, skill `rimworld-art-evaluation`):

  envelope   module `head` only: the skull mass and its appendages fit the painted-head envelope
             (`src/RimMandrake/Utils/art/head_envelope.json`, judged by `fit_head_canvas.judge`, known violations
             excepted by `split_known`). A head outside it sits wrong under hats and beside a vanilla head.
  greyscale  when the card says `skin_tint` (the head type or gene draws with the skin shader, RimWorld's default):
             the mean and 95th-percentile chroma (max(R,G,B) - min(R,G,B), opaque pixels) under the template's
             limits. The skin shader MULTIPLIES the texture by the pawn's skin colour, so a painted colour shifts every
             skin tone and the head disagrees with the body (SPECIES_HEADS_AUDIT_PROVENANCE_BEFORE_REDRAW: Togruta).

truth(spec) -> None (not a head card) | {"verdict": "PASS"|"FLAG"|"UNMEASURED", "flags": [...],
"measured": {...}, "fix": "<one positive sentence per flag>"}. A facing that cannot be read is UNMEASURED, never PASS.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "art"))
import fit_head_canvas as F  # noqa: E402
import policy as P  # noqa: E402

FACINGS = ("south", "east", "north")


def chroma(im: Image.Image) -> tuple[float, float] | None:
    """(mean, p95) chroma of the opaque pixels (alpha > 0.5) as 0..1, or None for a blank picture."""
    a = np.asarray(im.convert("RGBA")).astype(float) / 255
    m = a[..., 3] > 0.5
    if not m.any():
        return None
    rgb = a[..., :3][m]
    c = rgb.max(1) - rgb.min(1)
    return round(float(c.mean()), 4), round(float(np.percentile(c, 95)), 4)


def truth(spec: dict, limits: dict | None = None) -> dict | None:
    """limits: the head template's `gate` block (read from the template when not given)."""
    if spec.get("template") != "head":
        return None
    limits = limits or P.load_template("head")["gate"]
    imgs = spec.get("images") or {}
    files = {f: imgs[f] for f in FACINGS if imgs.get(f)}
    if not files:
        return {"verdict": "UNMEASURED", "flags": [], "measured": {}, "why": "no south/east/north picture"}
    flags, measured, unread = [], {"chroma": {}}, []
    pics = {f: Image.open(p) for f, p in files.items()}

    if spec.get("skin_tint", True):
        g = limits["greyscale"]
        for f, im in pics.items():
            c = chroma(im)
            measured["chroma"][f] = c
            if c is None:
                unread.append(f"{f} blank")
            elif c[0] > g["mean_chroma_max"] or c[1] > g["p95_chroma_max"]:
                flags.append({"code": "SKIN_NOT_GREY", "facing": f,
                              "seen": f"chroma mean {c[0]:.3f} / p95 {c[1]:.3f} over {g['mean_chroma_max']} / {g['p95_chroma_max']}"})

    if spec.get("module", "head") == "head":
        env = F.load_envelope()
        ext = {}
        for f, im in pics.items():
            m = F.measure_image(im)
            if m:
                ext[f] = m
        viol, rows = F.judge(ext, env, spec.get("species"))
        new, _known, _stale = F.split_known(viol, env, spec.get("species"))
        measured["envelope"] = {f: {k: round(v, 3) for k, v in r.items()} for f, r in rows.items()}
        for f, rule, val, lim in new:
            if rule == "UNMEASURED":
                unread.append(f"{f} envelope unmeasured")
                continue
            flags.append({"code": "HEAD_ENVELOPE", "facing": f,
                          "seen": f"{rule}: {val:.3f} (limit {lim:.3f})" if val is not None else rule})

    if flags:
        verdict = "FLAG"
    elif unread:
        verdict = "UNMEASURED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "flags": flags, "measured": measured, "unread": unread, "fix": fix_text(flags)}


def fix_text(flags: list) -> str:
    out = []
    if any(f["code"] == "SKIN_NOT_GREY" for f in flags):
        out.append("Paint the head in neutral greyscale values only (light skin as near-white, shading as grey), with no "
                   "hue: the game tints it with the pawn's skin colour.")
    env = sorted({f"{f['facing']} {f['seen'].split(':')[0]}" for f in flags if f["code"] == "HEAD_ENVELOPE"})
    if env:
        out.append("Seat the skull on the vanilla head box: same height, chin on the vanilla chin, centred, every "
                   "facing the same size; keep horns, ears and lekku inside the canvas (measured: " + "; ".join(env) + ").")
    return " ".join(out)
