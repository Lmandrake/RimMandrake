#!/usr/bin/env python3
"""Seam check for the weir art: each body/overlay must tile along its wall axis. For a wall running along x, the jump
between the last and first column (the joint two sections make) must be no rougher than the roughest tenth of the image.s own
column-to-column changes (90th percentile x 1.5, floor 2). Prints one line per file; exit 1 on any seam."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

out = Path(__file__).resolve().parent / "out"
bad = 0
for f in sorted(out.glob("*/RM_BankWeir_*.png")) + sorted(out.glob("*/RM_BankWeirSpill_*.png")) + sorted(out.glob("RM_BankWeirWater_*.png")):
    a = np.array(Image.open(f).convert("RGBA")).astype(np.float32)
    a[..., :3] *= a[..., 3:4] / 255.0
    facing = f.stem.rsplit("_", 1)[-1]
    along_x = facing in ("east", "west")
    if not along_x:
        a = a.transpose(1, 0, 2)
    cols = a.transpose(1, 0, 2)
    jumps = np.abs(np.diff(cols, axis=0)).mean(axis=(1, 2))
    seam = np.abs(cols[-1] - cols[0]).mean()
    lim = max(np.percentile(jumps, 90) * 1.5, 2.0)   # a joint may be as rough as the roughest tenth of the interior
    ok = seam <= lim
    bad += not ok
    print(("ok   " if ok else "SEAM ") + f"{f.parent.name}/{f.name}: joint {seam:.2f} vs limit {lim:.2f}")
sys.exit(1 if bad else 0)
