"""Connected components of a sprite's alpha (8-connected), pure numpy + a flood fill (no scipy here)."""
import numpy as np


def components(mask):
    """(labels, boxes): labels is an int array (0 = background, k = the k-th component in scan order) and boxes[k - 1] is
    that component's (x0, y0, x1, y1), inclusive."""
    H, W = mask.shape
    lab = np.zeros((H, W), np.int32)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        k = len(out) + 1
        lab[y0, x0] = k
        st = [(y0, x0)]
        b = [x0, y0, x0, y0]
        while st:
            y, x = st.pop()
            b = [min(b[0], x), min(b[1], y), max(b[2], x), max(b[3], y)]
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = k
                        st.append((yy, xx))
        out.append(tuple(int(v) for v in b))
    return lab, out


def boxes(mask):
    """[(x0, y0, x1, y1)] inclusive, one per 8-connected component of the boolean mask, in scan order."""
    return components(mask)[1]
