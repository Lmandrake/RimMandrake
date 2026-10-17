"""Terrain-tile checks validate_sprite.py does not have (it is a cutout-sprite gate: its two alpha REJECTs fire on
every opaque terrain tile, vanilla Mud included). Checks: canvas equals the reference, fully opaque, seamless
(wrap-edge step no larger than the tile's own interior step), mean level between two neighbour terrains.
    python3 check_terrain_tile.py <candidate.png> <reference.png> <neighbour_a.png> <neighbour_b.png>"""
import sys
import numpy as np
from PIL import Image
c, ref, na, nb = (np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) for p in sys.argv[1:5])
bad = []
if c.shape != ref.shape: bad.append(f"canvas {c.shape[:2]} != reference {ref.shape[:2]}")
if c[..., 3].min() < 255: bad.append("not fully opaque")
g = c[..., :3].mean(2)
inner = np.abs(np.diff(g, axis=1)).mean(), np.abs(np.diff(g, axis=0)).mean()
wrap = np.abs(g[:, 0] - g[:, -1]).mean(), np.abs(g[0] - g[-1]).mean()
for ax, w, i in zip("xy", wrap, inner):
    print(f"seam {ax}: wrap step {w:.2f} vs interior step {i:.2f}")
    if w > 1.5 * i: bad.append(f"seam on {ax}")
m = lambda a: a[..., :3].mean()
lo, hi = sorted((m(na), m(nb)))
print(f"mean level {m(c):.1f} between {lo:.1f} and {hi:.1f}")
if not lo <= m(c) <= hi: bad.append("level outside the neighbours")
print("FAIL: " + "; ".join(bad) if bad else "PASS")
sys.exit(1 if bad else 0)
