#!/usr/bin/env python3
"""Realign the four elbow blocks (masks 3, 6, 9, 12) of the Modern, Industrial and Futuristic pipe
atlases so every seam matches its straight/tee neighbours (PT17), as the Scrapper atlas already does.

The elbows were drawn 3 px (in the 132 px visible tile) off-centre on each arm; each whole 176 px block
is translated by the integer offset (searched) that best centres both arms on the 57-74 bore. Nothing is regenerated.
Output goes through the art ledger (art.py put + install --reason script:<this file>).

    fix_pipe_elbow_seams.py [--apply]     (default: write to a work dir and report only)
"""
import subprocess, sys, shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
TEX = ROOT / "src/RimMandrake/FlowWorks/Textures"
ART = ROOT / "src/RimMandrake/Utils/art/art.py"
WORK = ROOT / "_pipe_elbow_fix_work"
LOOKS = ("Modern", "Industrial", "Futuristic")
SHIFT = {3: (-3, 2), 6: (-3, -2), 9: (2, 2), 12: (2, -3)}     # mask -> (dx, dy) in atlas px (y down); searched so each arm best matches the straight bore (arms are slightly slanted, so not a plain 3 px)


def fixed(look):
    src = TEX / ("RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas.png" % look)
    a = Image.open(src).convert("RGBA")
    out = a.copy()
    t = a.width // 4
    for m, (dx, dy) in SHIFT.items():
        x, y = m % 4, m // 4
        box = (x * t, (3 - y) * t, (x + 1) * t, (4 - y) * t)
        block = a.crop(box)
        moved = Image.new("RGBA", block.size, (0, 0, 0, 0))
        moved.paste(block, (dx, dy))
        out.paste(moved, box[:2])
    return out


def main():
    apply = "--apply" in sys.argv
    WORK.mkdir(exist_ok=True)
    try:
        for look in LOOKS:
            p = WORK / (look + ".png")
            fixed(look).save(p)
            if not apply:
                print("wrote", p)
                continue
            rel = "RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas.png" % look
            r = subprocess.run([sys.executable, str(ART), "install", "FlowWorks", rel, "--file", str(p),
                                "--reason", "script:src/RimMandrake/FlowWorks/Tools/fix_pipe_elbow_seams.py"],
                               capture_output=True, text=True)
            print(look, r.returncode, (r.stdout + r.stderr).strip()[-300:])
    finally:
        if apply:
            shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    main()
