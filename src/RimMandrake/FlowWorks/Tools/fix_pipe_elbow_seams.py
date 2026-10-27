#!/usr/bin/env python3
"""Realign the four elbow blocks (masks 3, 6, 9, 12) of the Modern, Industrial and Futuristic pipe
atlases so every seam matches its straight/tee neighbours (PT17), as the Scrapper atlas already does.

The elbows were drawn 3 px (in the 132 px visible tile) off-centre on each arm; each whole 176 px block
is translated by the integer offset (searched) that best centres both arms on the 57-74 bore. Nothing is regenerated.
Output goes through the art ledger (art.py put + install --reason script:<this file>).

    fix_pipe_elbow_seams.py [--apply [--by-card "q -> option"]]   (default: write to a work dir and report only)

The atlases are owner-kept, so --apply needs the authority: --by-card is passed to art.py install.
The shift is fixed, not re-measured, so a second run would push already-aligned elbows 3 px the other way: a look whose
installed atlas already passes PT17 is skipped, and a result that does not pass PT17 is never installed.
"""
import subprocess, sys, shutil
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selftest_player_truths_art as pta  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
TEX = ROOT / "src/RimMandrake/FlowWorks/Textures"
ART = ROOT / "src/RimMandrake/Utils/art/art.py"
WORK = ROOT / "Transient" / "pipe_elbow_fix_work"     # inside the clone: art.py put refuses files outside it
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


def seam_violations(atlas, look):
    """PT17 violations of one atlas image (the player-truth check the fix exists to satisfy)."""
    tiles = {m: pta.alpha(pta.fc.atlas_tile(atlas, m)) for m in range(16)}
    return [b for b in pta.pipe_truths(tiles, look) if b.startswith("PT17")]


def main():
    apply = "--apply" in sys.argv
    auth = ["--reason", "script:src/RimMandrake/FlowWorks/Tools/fix_pipe_elbow_seams.py"]
    if "--by-card" in sys.argv:
        auth = ["--by-card", sys.argv[sys.argv.index("--by-card") + 1]]
    WORK.mkdir(parents=True, exist_ok=True)
    try:
        rc = 0
        for look in LOOKS:
            rel = "RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas.png" % look
            if not seam_violations(Image.open(TEX / rel), look):
                print(look, "already passes PT17: skipped (a second shift would misalign it)")
                continue
            out = fixed(look)
            left = seam_violations(out, look)
            if left:
                print(look, "still %d PT17 violations after the shift: not written" % len(left))
                rc = 1
                continue
            p = WORK / (look + ".png")
            out.save(p)
            if not apply:
                print("wrote", p)
                continue
            r = subprocess.run([sys.executable, str(ART), "install", "FlowWorks", rel, "--file", str(p)] + auth,
                               capture_output=True, text=True)
            print(look, r.returncode, (r.stdout + r.stderr).strip()[-300:])
            rc = rc or r.returncode
        return rc
    finally:
        if apply:
            shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
