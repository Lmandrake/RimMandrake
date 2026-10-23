#!/usr/bin/env python3
"""PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE: shrink a pipe adapter's two end connectors (west pipe flange + neck, east brass
hose coupling + neck) about the horizontal axis, keeping each outer face where it was, and bridge the gap to the valve body
with the shrunken neck's own textured run. Deterministic edit of the installed art, same pixels; the valve body, wheel and
(propane) gauge are untouched -- the gauge is lifted off first and laid back on top.

Owner 2026-10-23: "We should unfortunately regen the pumps and such to have connectors that match the more modern pipe and
hose sizes." Targets (cells): pipe flange ~0.22 (pipe 0.136), hose coupling ~0.22 (a plain hose coupling's widest part).

  python3 shrink_adapter.py <src.png> <dst.png> [--keep x0,y0,x1,y1]   (--keep: a box laid back on top, e.g. the gauge)
"""
import sys

import numpy as np
from PIL import Image

W = 256
WEST = dict(x0=0, x1=82, rows=(80, 236), target=0.22)    # flange + neck, up to the valve body's west plate
EAST = dict(x0=177, x1=256, rows=(86, 236), target=0.22)  # neck + brass coupling, from the body's east plate


def _premul(a):
    p = a.copy(); p[..., :3] *= p[..., 3:4] / 255.0
    return p


def _unpremul(p):
    al = p[..., 3:4]
    p[..., :3] = np.where(al > 0, p[..., :3] * 255.0 / np.maximum(al, 1), 0)
    return p


def _over(dst, src):
    sa = src[..., 3:4] / 255.0
    dst[..., :3] = src[..., :3] * sa + dst[..., :3] * (1 - sa)
    dst[..., 3:4] = np.maximum(dst[..., 3:4], src[..., 3:4])


def shrink_west(a, x0, x1, rows, target):
    """Shrink the west assembly in a[:, x0:x1] (rows = the window) so its tallest part is `target` cells; outer face kept."""
    r0, r1 = rows
    win = a[r0:r1, x0:x1].copy()
    op = win[..., 3] > 128
    cols = np.where(op.any(0))[0]
    tall = max(int(op[:, c].sum()) for c in cols)
    S = target * W / tall
    ys = np.where(op.any(1))[0]
    cy = r0 + (ys[0] + ys[-1]) / 2.0
    nw, nh = max(1, round(win.shape[1] * S)), max(1, round(win.shape[0] * S))
    sm = _unpremul(np.array(Image.fromarray(np.clip(_premul(win), 0, 255).astype(np.uint8), 'RGBA')
                            .resize((nw, nh), Image.LANCZOS)).astype(np.float32))
    smop = sm[..., 3] > 128
    scols = np.where(smop.any(0))[0]
    face = x0 + cols[0]
    left = face - scols[0]
    top = int(round(cy - ((ys[0] + ys[-1]) / 2.0) * S))
    # the neck: the narrowest opaque column in the inner half of the scaled piece
    inner = [c for c in scols if c > (scols[0] + scols[-1]) / 2]
    spans = [(int(smop[:, c].sum()), c) for c in inner]
    mn = min(spans)[0]
    blk = [c for s, c in spans if s <= mn + 2]
    # one clean cross-section (the most opaque straight-neck column), repeated: tiling a block repeats bolts and rings
    nc = max(blk, key=lambda c: float(sm[:, c, 3].sum()))
    block = sm[:, nc:nc + 1].copy()
    # only the column's main opaque run (the neck itself), never a stray scrap above or below it
    run = smop[:, nc]
    mid = int(np.argmax(np.convolve(run.astype(float), np.ones(5), 'same')))
    lo = hi = mid
    while lo > 0 and block[lo - 1, 0, 3] > 8: lo -= 1
    while hi + 1 < nh and block[hi + 1, 0, 3] > 8: hi += 1
    block[:lo] = 0; block[hi + 1:] = 0
    sm[:, nc + 1:, 3] = 0          # inward of the neck column: body-plate scraps the window caught (the bridge covers it)
    a[r0:r1, x0:x1] = 0
    reg = a[top:top + nh, left:left + nw]
    _over(reg, sm[:reg.shape[0], :reg.shape[1]])
    rng = np.random.default_rng(1023 + x0)            # deterministic wear, so the plain tube matches the weathered body
    for x in range(left + nc, x1 + 3):
        col = a[top:top + nh, x:x + 1]
        b = block[:col.shape[0]].copy()
        b[..., :3] *= (1.0 + rng.normal(0, 0.06, (b.shape[0], 1, 1)) * 0.6 + rng.normal(0, 0.03))
        _over(col, np.clip(b, 0, 255))
    print('west: tallest %.3f -> %.3f cell (x%.2f), neck %.3f cell' % (tall / W, target, S, mn / W))
    return a


def drop_specks(a, max_px=40):
    """Clear tiny islands of alpha > 8 (4-connected, <= max_px pixels): scraps the scaled windows left."""
    op = a[..., 3] > 8
    seen = np.zeros_like(op)
    H, Wd = op.shape
    for y0 in range(H):
        for x0 in range(Wd):
            if not op[y0, x0] or seen[y0, x0]:
                continue
            stack, comp = [(y0, x0)], []
            seen[y0, x0] = True
            while stack:
                y, x = stack.pop(); comp.append((y, x))
                for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= yy < H and 0 <= xx < Wd and op[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True; stack.append((yy, xx))
            if len(comp) <= max_px:
                for y, x in comp:
                    a[y, x] = 0
    return a


def main():
    src, dst = sys.argv[1], sys.argv[2]
    keep = None
    if '--keep' in sys.argv:
        keep = tuple(int(v) for v in sys.argv[sys.argv.index('--keep') + 1].split(','))
    a = np.array(Image.open(src).convert('RGBA')).astype(np.float32)
    assert a.shape[:2] == (W, W), a.shape
    kept = a[keep[1]:keep[3], keep[0]:keep[2]].copy() if keep else None
    if keep:
        a[keep[1]:keep[3], keep[0]:keep[2]] = 0      # lifted off, so it never feeds the shrunken neck
    a = shrink_west(a, **WEST)
    m = np.ascontiguousarray(a[:, ::-1])                       # the east side, mirrored to face west
    e = dict(EAST); e['x0'], e['x1'] = W - EAST['x1'], W - EAST['x0']
    m = shrink_west(m, **e)
    a = np.ascontiguousarray(m[:, ::-1])
    if kept is not None:
        _over(a[keep[1]:keep[3], keep[0]:keep[2]], kept)
        # the kept part's stem (its bottom row) runs on down until it meets the new neck
        x0, x1 = keep[0], keep[2]
        rows_op = np.where((kept[..., 3] > 200).any(1))[0]
        y = keep[1] + int(rows_op[-1])
        row = kept[rows_op[-1]:rows_op[-1] + 1].copy()
        row[..., 3] = np.where(row[..., 3] > 200, row[..., 3], 0)
        while y + 1 < W and not (a[y + 1, x0:x1, 3][row[0, :, 3] > 0] > 200).any():
            y += 1
            _over(a[y:y + 1, x0:x1], row)
    a = drop_specks(a)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA').save(dst)


if __name__ == '__main__':
    main()
