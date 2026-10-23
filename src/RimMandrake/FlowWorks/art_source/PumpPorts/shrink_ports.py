"""Shrink a 1-cell pump's four side-port assemblies (neck + flange) about the port axis, keeping the flange face at the
footprint edge, and bridge the gap to the body with the shrunken neck's own cross-section. Deterministic, same pixels."""
import sys, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
NECK = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15   # target neck width, cells
X0 = float(sys.argv[4]) if len(sys.argv) > 4 else 400/512    # body plate edge (fraction of canvas) -- erase from here out
XP = float(sys.argv[5]) if len(sys.argv) > 5 else 412/512    # port piece starts here (drops the neck's base ears)
HH = float(sys.argv[6]) if len(sys.argv) > 6 else 90/512     # half-height of the port window
im = np.array(Image.open(src).convert('RGBA')).astype(np.float32)
W = im.shape[1]
SIDES = {0: (400, 412), 1: (400, 404), 2: (400, 412), 3: (402, 405)}   # k -> (x0, xp) at 512 px; k0 E, k1 S, k2 W, k3 N
def do_east(a, k):
    H, W = a.shape[:2]; cy = H // 2
    x0, xp = (int(v * W / 512) for v in SIDES[k]); hh = int(HH * W)
    win = a[cy - hh:cy + hh, xp:, :].copy()
    alpha = win[:, :, 3] > 8
    cols = np.where(alpha.any(0))[0]; rows = np.where(alpha.any(1))[0]
    outer = xp + cols[-1]                       # outermost opaque column (flange face)
    # premultiply for clean resampling
    pm = win.copy(); pm[:, :, :3] *= pm[:, :, 3:4] / 255.0
    pim = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), 'RGBA')
    oc = np.where(alpha.any(0))[0]
    n0 = min(int((win[:, c, 3] > 128).sum()) for c in range(oc[0] + 1, oc[0] + (oc[-1] - oc[0]) // 2))
    S = NECK * W / n0
    print('side scale %.3f (neck %.3f -> %.3f cell)' % (S, n0 / W, NECK))
    nw, nh = max(1, round(win.shape[1] * S)), max(1, round(win.shape[0] * S))
    sm = np.array(pim.resize((nw, nh), Image.LANCZOS)).astype(np.float32)
    # un-premultiply
    al = sm[:, :, 3:4]; sm[:, :, :3] = np.where(al > 0, sm[:, :, :3] * 255.0 / np.maximum(al, 1), 0)
    # erase old port: everything x>=x0 inside window rows
    a[cy - hh:cy + hh, x0:, :] = 0
    # place scaled piece so its outer opaque column lands on `outer`
    so = np.where((sm[:, :, 3] > 8).any(0))[0][-1]
    left = outer - so
    top = cy - nh // 2
    # bridge: the scaled neck's cross-section a few px in from its inner end, tiled from x0-3 to left+3
    sc = np.where((sm[:, :, 3] > 8).any(0))[0][0]
    spans = [(int((sm[:, c, 3] > 128).sum()), c) for c in range(sc + 2, sc + (so - sc) // 2)]
    nc = min(spans)[1]; neck = sm[:, nc, :]
    mn = min(spans)[0]
    blk = [c for sp_, c in spans if sp_ <= mn + 2]          # the straight-neck columns of the scaled piece
    lo = hi = nc
    while lo - 1 in blk: lo -= 1
    while hi + 1 in blk: hi += 1
    block = sm[:, lo:hi + 1, :]                               # tiled (mirrored) so the bridge keeps the neck's surface texture
    seq = list(range(block.shape[1])) + list(range(block.shape[1] - 1, -1, -1))
    sc = nc - 4
    for i, x in enumerate(range(x0 - 3, left + sc + 5)):
        neck = block[:, seq[i % len(seq)], :] if block.shape[1] >= 3 else neck
        col = a[top:top + nh, x, :]
        # neck goes over the background, under nothing: composite neck OVER existing (body plate edge stays under)
        na = neck[:, 3:4] / 255.0
        col[:, :3] = neck[:, :3] * na + col[:, :3] * (1 - na)
        col[:, 3:4] = np.maximum(col[:, 3:4], neck[:, 3:4])
    sm[:, :nc, 3] = 0                       # drop anything inward of the neck column (body-plate scraps)
    reg = a[top:top + nh, left:left + nw, :]
    sa = sm[:, :, 3:4] / 255.0
    reg[:, :, :3] = sm[:, :, :3] * sa + reg[:, :, :3] * (1 - sa)
    reg[:, :, 3:4] = np.maximum(reg[:, :, 3:4], sm[:, :, 3:4])
    return a
out = im
for k in range(4):           # k=0 east; rotate so each side faces east in turn
    r = np.rot90(out, k).copy()
    r = do_east(r, k)
    out = np.rot90(r, -k).copy()
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA').save(dst)
