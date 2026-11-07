#!/usr/bin/env python3
"""selftest_flyer_eye_checks.py - flyer_eye_checks can fail where it must. Planted on synthetic frames in a temp dir:
a clean set is green; a head shift, a frozen wing, an erased wing, a missing frame and a squash pose each go red by name;
no head box and no config read UNMEASURED, not green; a mid-stroke hold is advice and does not fail; parts writes a sheet."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOL = HERE / "flyer_eye_checks.py"
PREFIX = "Bird_Flying_"
N = 5
SIZE = 128
HEAD = "48,20,80,50"
LIFT = [34, 16, 0, 16, 26]


def frame(k: int, head_dy=0, left=True, right=True, left_k=None, right_k=None) -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if left:
        y = 50 + LIFT[k if left_k is None else left_k]
        d.polygon([(54, 60), (6, y), (8, y + 14), (54, 72)], fill=(200, 90, 20, 255))
    if right:
        y = 50 + LIFT[k if right_k is None else right_k]
        d.polygon([(74, 60), (122, y), (120, y + 14), (74, 72)], fill=(200, 90, 20, 255))
    d.ellipse((52, 44, 76, 110), fill=(90, 80, 70, 255))
    d.ellipse((54, 24 + head_dy, 74, 44 + head_dy), fill=(150, 140, 120, 255))
    d.point((60, 32 + head_dy), fill=(10, 10, 10, 255))
    d.point((68, 32 + head_dy), fill=(10, 10, 10, 255))
    d.line((58, 38 + head_dy, 70, 38 + head_dy), fill=(30, 20, 10, 255))
    return im


def write_set(folder: Path, make) -> Path:
    folder.mkdir(parents=True)
    for facing in ("north", "east", "south"):
        for k in range(N):
            make(facing, k).save(folder / f"{PREFIX}{k + 1}_{facing}.png")
    return folder


def run(folder: Path, *extra) -> tuple[int, str]:
    heads = [f"--head={f}={HEAD}" for f in ("north", "east", "south")]
    r = subprocess.run([sys.executable, str(TOOL), "audit", str(folder), "--prefix", PREFIX, "--n", str(N), *heads, *extra],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    fails = []

    def expect(name, ok, out=""):
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            fails.append(name)
            print(out)

    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        clean = write_set(t / "clean", lambda f, k: frame(k))
        rc, out = run(clean)
        expect("clean set exits 0", rc == 0 and ": RED" not in out and "SQUASH  RED" not in out, out)
        expect("clean set: no config reads UNMEASURED", "SQUASH  UNMEASURED" in out, out)
        expect("held frame part way through the stroke is advice, not a failure", "mid-stroke" in out and rc == 0, out)

        r = subprocess.run([sys.executable, str(TOOL), "audit", str(clean), "--prefix", PREFIX, "--n", str(N)],
                           capture_output=True, text=True)
        expect("no head box is UNMEASURED, not GREEN", "HEAD    north: UNMEASURED" in r.stdout and "HEAD    north: GREEN" not in r.stdout,
               r.stdout)

        bob = [0, 3, 1, -2, -3]
        rc, out = run(write_set(t / "bob", lambda f, k: frame(k, head_dy=bob[k])))
        expect("head bob goes red at HEAD", rc == 1 and "HEAD    east: RED" in out, out)

        rc, out = run(write_set(t / "frozen", lambda f, k: frame(k, right_k=4)))
        expect("one wing frozen goes red at SIDES", rc == 1 and "SIDES   north: RED" in out, out)

        rc, out = run(write_set(t / "erased", lambda f, k: frame(k, left=False)))
        expect("one wing erased goes red at SIDES", rc == 1 and "SIDES   south: RED" in out, out)

        gone = write_set(t / "gone", lambda f, k: frame(k))
        (gone / f"{PREFIX}3_north.png").unlink()
        rc, out = run(gone)
        expect("a missing frame goes red at FRAMES", rc == 1 and "FRAMES  north: RED" in out, out)

        config = {"set": "Bird", "prefix": PREFIX, "facings": {"east": {"master": 2, "protect": [[[48, 20], [80, 20], [80, 50], [48, 50]]],
                  "wings": [{"poly": [[0, 40], [54, 40], [54, 100], [0, 100]], "hinge": [54, 60], "sign": 1,
                             "poses": [[0, 1, 1.0], [0, 1, 0.55], [3, 1, -0.1], [5, 1, -0.4], [0, 1, 0.6]]}]}}}
        cfg = t / "bird.json"
        cfg.write_text(json.dumps(config))
        rc, out = run(clean, "--config", str(cfg))
        expect("a squash pose goes red at SQUASH and names its frames", rc == 1 and "frame 3 sy -0.1" in out and "frame 4 sy -0.4" in out, out)

        plate = t / "plate.png"
        rc, out = run(clean, "--plate-out", str(plate))
        expect("plate view is written", plate.exists(), out)

        sheet = t / "parts.png"
        r = subprocess.run([sys.executable, str(TOOL), "parts", str(cfg), "--src", str(clean), "--out", str(sheet)],
                           capture_output=True, text=True)
        expect("parts writes a sheet", r.returncode == 0 and sheet.exists(), r.stdout + r.stderr)

    print(f"selftest_flyer_eye_checks: {'FAIL ' + ', '.join(fails) if fails else 'PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
