#!/usr/bin/env python3
"""selftest_flyer_step_page.py - the flyer step page carries what the owner asked for (2026-11-07): true rate and quarter
speed, pause and frame step, the last frame held double, every facing full size and at true scale, west mirrored from
east. A missing frame is refused by name rather than drawn as a gap."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

TOOL = Path(__file__).resolve().parent / "flyer_step_page.py"
PREFIX = "Bird_Flying_"


def frames(folder: Path, n: int) -> None:
    folder.mkdir(parents=True)
    for facing in ("north", "east", "south"):
        for k in range(1, n + 1):
            im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.ellipse((40, 40, 70, 90), fill=(90, 80, 70, 255))
            d.rectangle((70, 50 + 4 * k, 120, 56 + 4 * k), fill=(200, 90, 20, 255))   # asymmetric, so a mirror shows
            im.save(folder / f"{PREFIX}{k}_{facing}.png")


def main() -> int:
    fails = []

    def expect(name, ok, detail=""):
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            fails.append(name)
            print(detail)

    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        frames(t / "src", 5)
        out = t / "page"
        r = subprocess.run([sys.executable, str(TOOL), "--out", str(out), "--title", "T",
                            "--cand", f"X|{t / 'src'}|{PREFIX}|5|2|1.35|what changed"], capture_output=True, text=True)
        expect("builds", r.returncode == 0, r.stdout + r.stderr)
        page = (out / "index.html").read_text() if (out / "index.html").exists() else ""
        for label in ("Play 1x", "Play 1/4x", "Pause", "< Frame", "Frame >", "ArrowRight", "ArrowLeft"):
            expect(f"page has control {label}", label in page)
        m = re.search(r"const DATA=(\[.*?\]);const TICK_MS", page, re.S)
        data = json.loads(m.group(1)) if m else []
        expect("last frame held double, the rest at ticksPerFrame", bool(data) and data[0]["ticks"] == [2, 2, 2, 2, 4], str(data[:1])[:300])
        expect("tick clock is 60 a second", "TICK_MS=1000/60" in page)
        views = data[0]["views"] if data else {}
        expect("four facings, five frames each, full and true scale",
               sorted(views) == ["east", "north", "south", "west"] and all(len(v) == 5 and len(v[0]) == 2 for v in views.values()), str(views)[:300])
        if views:
            e = np.asarray(Image.open(out / views["east"][0][0]))
            w = np.asarray(Image.open(out / views["west"][0][0]))
            expect("west is east mirrored", np.array_equal(w, e[:, ::-1]))
            expect("a 128 px frame is shown at 2x", e.shape[1] == 256, str(e.shape))
        expect("the change note is on the page", "what changed" in page)

        (t / "src" / f"{PREFIX}3_south.png").unlink()
        r = subprocess.run([sys.executable, str(TOOL), "--out", str(t / "page2"), "--title", "T",
                            "--cand", f"X|{t / 'src'}|{PREFIX}|5|2|1.35|n"], capture_output=True, text=True)
        expect("a missing frame is refused by name", r.returncode != 0 and "3_south" in (r.stdout + r.stderr), r.stdout + r.stderr)

    print(f"selftest_flyer_step_page: {'FAIL ' + ', '.join(fails) if fails else 'PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
