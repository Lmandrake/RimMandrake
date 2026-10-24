"""Connected-component boxes of a sprite's alpha (8-connected), pure numpy + a flood fill (no scipy here)."""
import numpy as np


def boxes(mask):
    """[(x0, y0, x1, y1)] inclusive, one per 8-connected component of the boolean mask, in scan order."""
    H, W = mask.shape
    lab = np.zeros((H, W), bool)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        lab[y0, x0] = True
        st = [(y0, x0)]
        b = [x0, y0, x0, y0]
        while st:
            y, x = st.pop()
            b = [min(b[0], x), min(b[1], y), max(b[2], x), max(b[3], y)]
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = True
                        st.append((yy, xx))
        out.append(tuple(int(v) for v in b))
    return out
