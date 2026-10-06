#!/usr/bin/env python3
"""selftest_placeholder_detect.py — placeholder_detect.py's guarantees (owner, 2026-10-05, Grey Sea sheet).

Part 1, synthetic: a flat ellipse / cube / wedge reads FLAT; a noisy painted blob reads real; a tiny sprite is not
judged; borrowed-texPath rule fires on a fish on Things/Plant/*, on a vanilla item path shared by subjects, and does
NOT fire on our own folder, a donor mod tree, a Juv life stage or a name-matching texPath.
Part 2, a SANITY PROBE on the real repo: the Grey Sea script-drawn creatures must classify PLACEHOLDER and real
artpipe renders + the installed Orruhmu set must classify REAL; the run fails if the probe cannot see either.
"""
from __future__ import annotations

import glob
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placeholder_detect as P  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:300]}]"))
    if not cond:
        FAILS.append(msg)


def run() -> int:
    import numpy as np
    from PIL import Image, ImageDraw
    d = Path(tempfile.mkdtemp())
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((20, 30, 108, 100), fill=(90, 100, 110, 255))
    im.save(d / "ell.png")
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(10, 100), (60, 20), (110, 100)], fill=(120, 60, 40, 255), outline=(30, 20, 10, 255))
    im.save(d / "wedge.png")
    rng = np.random.default_rng(3)
    a = np.zeros((128, 128, 4), np.uint8)
    yy, xx = np.mgrid[:128, :128]
    m = (xx - 64) ** 2 + (yy - 64) ** 2 < 50 ** 2
    a[m, :3] = (rng.integers(60, 200, (int(m.sum()), 3)) + (xx[m, None] // 2)).clip(0, 255)
    a[m, 3] = 255
    Image.fromarray(a).save(d / "painted.png")
    Image.new("RGBA", (8, 8), (9, 9, 9, 255)).save(d / "tiny.png")
    check(P.is_flat(P.pixel_metrics(d / "ell.png")), "flat ellipse is FLAT")
    check(P.is_flat(P.pixel_metrics(d / "wedge.png")), "outlined wedge is FLAT")
    check(not P.is_flat(P.pixel_metrics(d / "painted.png")), "noisy painted blob is not FLAT")
    check(not P.is_flat(P.pixel_metrics(d / "tiny.png")), "a tiny sprite is not judged")
    sh = {"Things/Item/Resource/MeatFoodRaw/Meat_Small": {"a", "b", "c"}, "Things/Plant/RM_Fam/RM_Fam": {"x", "y"},
          "swanimals/K/K": {"a", "b"}, "Things/Pawn/Animal/SeaBeasts/Faa/Faa": {"faa", "faa"}}
    b = P.borrowed_reason
    check(b("RM_HaarnCatch", "fish", "Things/Plant/Echeveria/EcheveriaA", sh), "fish on a plant texPath is BORROWED")
    check(b("RM_Duul", "fish", "Things/Item/Resource/MeatFoodRaw/Meat_Small", sh), "vanilla meat shared by 3 is BORROWED")
    check(not b("RM_X", "flora", "Things/Plant/RM_Fam/RM_Fam", sh), "own-folder family texture is not BORROWED")
    check(not b("RSW_V", "fauna", "swanimals/K/K", sh), "donor mod tree is not BORROWED")
    check(not b("RSW_FaaJuv", "fauna", "Things/Pawn/Animal/SeaBeasts/Faa/Faa", sh), "Juv life stage of the same subject is fine")
    check(not b("RM_Brinecomb", "flora", "Things/Plant/RM_Brinecomb/RM_Brinecomb_a", sh), "name-matching texPath is fine")
    check(not b("AA_Thing", "fauna", "Things/Pawn/Animal/Other/Other", sh), "a donor-prefixed def is not judged by name")
    # part 2: sanity probe on real files
    base = P.SRC / "RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal"
    flat = [base / f"RM_{n}/RM_{n}.png" for n in ("Corrik", "Grusk", "Haarn", "Karrud", "Nissik", "Oomal")]
    flat = [f for f in flat if f.is_file()]
    check(len(flat) >= 3, "probe can see the Grey Sea placeholder files", len(flat))
    check(all(P.is_flat(P.pixel_metrics(f)) for f in flat), "Grey Sea script-drawn shapes classify FLAT")
    real = sorted(glob.glob(str(base / "RM_Orruhmu/*.png")))
    check(len(real) >= 3, "probe can see the installed Orruhmu render", len(real))
    check(not any(P.is_flat(P.pixel_metrics(f)) for f in real), "installed Orruhmu render classifies REAL")
    arts = glob.glob("/mnt/d/Luke/dev/_artpipe/_artsrc/*/*.png")
    if arts:
        random.seed(7)
        pick = random.sample(arts, min(150, len(arts)))
        met = [(f, P.pixel_metrics(f)) for f in pick]
        bad = [f for f, m_ in met if P.is_flat(m_)]
        check(not bad, f"{len(pick)} real artpipe renders all classify REAL", bad[:3])
    else:
        check(False, "artpipe _artsrc unreachable: UNMEASURED, not a pass")
    print(f"{len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(run())
