#!/usr/bin/env python3
"""selftest.py — prove validate_sprite actually catches the defects it claims.

Each case synthesises a known-bad sprite from a known-good one and asserts the
validator rejects it for the right reason. A checker nobody has tested is a
checker that reports OK on broken work, which is worse than no checker: the
undersizing bug this suite exists for passed every automated check at the time.

    python selftest.py --reference <a real sprite.png>
    python selftest.py --reference <ref.png> --keep /tmp/fixtures

Exit codes: 0 all cases behaved, 1 one or more did not.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "generating-images" / "scripts"))
import pnglib  # noqa: E402

VALIDATOR = HERE / "validate_sprite.py"


# --- fixture builders --------------------------------------------------------

def rescale_subject(w, h, px, factor):
    """Shrink or grow the subject on the same canvas, centred where it was."""
    nw, nh = max(1, round(w * factor)), max(1, round(h * factor))
    small = pnglib.resize_rgba(w, h, px, nw, nh)
    out = bytearray(w * h * 4)
    ox, oy = (w - nw) // 2, (h - nh) // 2
    for y in range(nh):
        ty = y + oy
        if not (0 <= ty < h):
            continue
        for x in range(nw):
            tx = x + ox
            if 0 <= tx < w:
                s, d = (y * nw + x) * 4, (ty * w + tx) * 4
                out[d:d + 4] = small[s:s + 4]
    return out


def add_fringe(w, h, px, alpha=20):
    """Scatter near-invisible pixels near the frame edge - the real bug.

    Sized to the defect this defends against: the sprite that came out 20%
    undersized carried fringe over ~0.12% of its pixels. A first attempt used
    100 pixels (0.03%), which the validator correctly ignored as noise - the
    fixture was a smaller defect than the real one, not a validator failure.
    """
    out = bytearray(px)
    target = max(1, int(w * h * 0.0015))
    per_cluster = target // 4
    half = max(2, int(per_cluster ** 0.5) // 2)
    # Kept off the exact corners so this exercises the fringe check rather
    # than the corner check.
    margin = half + 3
    for (cx, cy) in ((margin, margin), (w - 1 - margin, margin),
                     (margin, h - 1 - margin), (w - 1 - margin, h - 1 - margin)):
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < w and 0 <= y < h:
                    i = (y * w + x) * 4
                    out[i:i + 3] = bytes((90, 90, 90))
                    out[i + 3] = alpha
    return out


def make_translucent(w, h, px, alpha=170):
    """Push solid pixels into the mid-alpha band - a too-wide key ramp."""
    out = bytearray(px)
    for i in range(3, len(out), 4):
        if out[i] == 255:
            out[i] = alpha
    return out


def shift_subject(w, h, px, dx, dy):
    out = bytearray(w * h * 4)
    for y in range(h):
        ty = y + dy
        if not (0 <= ty < h):
            continue
        for x in range(w):
            tx = x + dx
            if 0 <= tx < w:
                s, d = (y * w + x) * 4, (ty * w + tx) * 4
                out[d:d + 4] = px[s:s + 4]
    return out


def squash(w, h, px):
    """Same area, wrong aspect."""
    return rescale_subject(w, h, px, 1.0) if False else _squash(w, h, px)


def _squash(w, h, px):
    nw, nh = max(1, round(w * 0.78)), h
    small = pnglib.resize_rgba(w, h, px, nw, nh)
    out = bytearray(w * h * 4)
    ox = (w - nw) // 2
    for y in range(nh):
        for x in range(nw):
            tx = x + ox
            if 0 <= tx < w:
                s, d = (y * nw + x) * 4, (y * w + tx) * 4
                out[d:d + 4] = small[s:s + 4]
    return out


def strip_alpha(w, h, px):
    out = bytearray(px)
    for i in range(3, len(out), 4):
        out[i] = 255
    return out


CASES = [
    ("undersized-20pct", lambda w, h, p: rescale_subject(w, h, p, 0.80),
     "subject width", True),
    ("oversized-15pct", lambda w, h, p: rescale_subject(w, h, p, 1.15),
     "exceeds the reference", True),
    ("faint-fringe", lambda w, h, p: add_fringe(w, h, p),
     "alpha 1-31", True),
    ("semi-transparent", lambda w, h, p: make_translucent(w, h, p),
     "semi-transparent", True),
    ("shifted", lambda w, h, p: shift_subject(w, h, p, 40, 0),
     "origin", True),
    ("squashed", lambda w, h, p: _squash(w, h, p),
     "aspect", True),
    ("no-alpha", lambda w, h, p: strip_alpha(w, h, p),
     "alpha channel", True),
    ("identical", lambda w, h, p: bytearray(p),
     "byte-identical", True),
]


def run_validator(ref: Path, cand: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--reference", str(ref),
         "--candidate", str(cand)],
        capture_output=True, text=True, timeout=600)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--keep", help="write fixtures here instead of a temp dir")
    args = ap.parse_args()

    ref = Path(args.reference)
    if not ref.is_file():
        print(f"ERROR no such reference: {ref}", file=sys.stderr)
        return 1

    w, h, px = pnglib.read_png(str(ref))
    workdir = Path(args.keep) if args.keep else Path(tempfile.mkdtemp())
    workdir.mkdir(parents=True, exist_ok=True)

    # A sanity case first: the reference lightly edited must still PASS, or
    # every rejection below is meaningless.
    control = bytearray(px)
    for i in range(0, len(control), 4):
        if control[i + 3] == 255:
            control[i] = min(255, control[i] + 12)   # tint, geometry untouched
    control_path = workdir / "control-tinted.png"
    pnglib.write_rgba(str(control_path), w, h, control)

    failures = 0
    code, out = run_validator(ref, control_path)
    if code == 0:
        print(f"  ok    control-tinted            PASS as expected")
    else:
        print(f"  FAIL  control-tinted            expected PASS, got reject")
        print("        " + "\n        ".join(out.strip().splitlines()[-3:]))
        failures += 1

    for name, build, expect_text, expect_reject in CASES:
        path = workdir / f"{name}.png"
        pnglib.write_rgba(str(path), w, h, build(w, h, px))
        code, out = run_validator(ref, path)
        rejected = code != 0
        matched = expect_text.lower() in out.lower()
        if rejected == expect_reject and matched:
            print(f"  ok    {name:<24} rejected on {expect_text!r}")
        else:
            failures += 1
            why = ("was not rejected" if not rejected
                   else f"rejected but never mentioned {expect_text!r}")
            print(f"  FAIL  {name:<24} {why}")

    print()
    if failures:
        print(f"{failures} case(s) misbehaved. Fixtures kept in {workdir}",
              file=sys.stderr)
        return 1
    print(f"all {len(CASES) + 1} cases behaved as specified")
    if not args.keep:
        for p in workdir.glob("*.png"):
            p.unlink()
        workdir.rmdir()
    return 0


if __name__ == "__main__":
    sys.exit(main())
