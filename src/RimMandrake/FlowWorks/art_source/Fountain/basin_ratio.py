"""Camera check for a round basin seen from the building camera: fit the silhouette's LOWER arc (the basin's bottom
rim) as an ellipse and report minor/major. validate_sprite.py --upright-cylinder fits the TOP arc, which on a fountain
is the jet/column, so it cannot judge this shape.  usage: basin_ratio.py <png>..."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../skills/generating-images/scripts"))
import pnglib  # noqa: E402

for p in sys.argv[1:]:
    w, h, rgba = pnglib.read_png(p)[:3]
    rows = []
    for y in range(h):
        xs = [x for x in range(w) if rgba[(y * w + x) * 4 + 3] >= 128]
        rows.append((xs[0], xs[-1]) if xs else None)
    widths = [(r[1] - r[0] + 1) if r else 0 for r in rows]
    full = max(widths)
    bottom = max(y for y in range(h) if widths[y])
    # the ellipse centre row: the lowest row within 2 px of the full width (99% sat ~15 rows low and read the 0.56 guide as 0.45)
    c = max(y for y in range(h) if widths[y] >= full - 2)
    a = full / 2.0
    # least-squares b over the arc rows: halfwidth = a*sqrt(1-((y-c)/b)^2)  ->  b = (y-c)/sqrt(1-(hw/a)^2)
    bs = []
    for y in range(c + 1, bottom + 1):
        hw = widths[y] / 2.0
        q = 1 - (hw / a) ** 2
        if 0.02 < q < 0.98:
            bs.append((y - c) / q ** 0.5)
    bs.sort()
    b = bs[len(bs) // 2] if bs else float("nan")
    print("%s  basin width %d px, bottom arc minor/major %.2f (target 0.56, band 0.48-0.64)" % (os.path.basename(p), full, b / a))
