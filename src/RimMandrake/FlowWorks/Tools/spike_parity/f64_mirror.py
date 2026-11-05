"""The PRE-FIX double-precision mirror of RM_SpikeDrawMath.Layout (fw_scenes_spikes.layout before
SPIKES_PARITY_FIX_FLOAT32_MIRROR), kept only as the can-fail of selftest_spike_float32_parity.py and as the search
gen_golden.py runs for rects where doubles and float32 take different sides of a threshold. Never used to draw."""
import math


def layout_f64(variant, seed, x0, z0, x1, z1, lib, MARGIN, hash32):
    lib, (ppx, ppz) = lib
    n = len(lib)
    if n == 0:
        return []
    wmax, hmax = max(s[0] for s in lib), max(s[1] for s in lib)
    fw, fh = x1 - x0 - 2 * MARGIN, z1 - z0 - 2 * MARGIN
    if n == 0 or fw <= 0 or fh <= 0:
        return []
    sc = min(1.0, fh / hmax, fw / wmax)
    lo, hi, bot, top = x0 + MARGIN, x1 - MARGIN, z0 + MARGIN, z1 - MARGIN
    clamp = lambda v, a, b: a if v < a else (b if v > b else v)
    span = max(0.0, 1.0 - hmax * 0.5)   # base rows run 0..1-hmax/2: the tallest stakes of the top rows are pulled down to the cell top
    cell_top = top >= 1.0 - MARGIN - 1e-4
    nrow, ncol = max(1, int(math.floor(span / ppz)) + 1), max(1, int(math.floor(1.0 / ppx + 0.5)))
    rpz, rpx = (span / (nrow - 1) if nrow > 1 else 0.0), 1.0 / ncol
    # PIT_SPIKES_TUNE_NORTH_ROW_TOO_SPARSE: a rect the north face shortens keeps every row the cell top would keep: a
    # base up to half a stake under the rect top, plus half a row pitch, is pulled down inside (as the cell top pulls in
    # its top row) instead of being dropped, so the north cell keeps a middle cell's density on its shorter floor.
    cap = top - hmax * sc * 0.5 + 0.5 * rpz
    out = []
    for pas in range(2):
        if out:
            break
        for r in range(nrow):
            odd = r & 1
            for col in range(ncol + 1 if odd else ncol):
                k = r * (ncol + 1) + col
                h = hash32(seed, k)
                st = lib[h % n]
                w, ht = st[0] * sc, st[1] * sc
                xc = (col if odd else col + 0.5) * rpx
                jx = (((h >> 8) & 0xFF) / 255 - 0.5) * 0.5 * rpx
                jz = (((h >> 16) & 0xFF) / 255 - 0.5) * 0.5 * rpz
                if xc + w * 0.5 <= lo or xc - w * 0.5 >= hi:
                    continue
                zb = r * rpz + jz
                if (((zb > cap and not cell_top) or (r > 0 and zb < bot)) if pas == 0 else r != 0):
                    continue
                out.append((clamp(xc + jx - w * 0.5, lo, hi - w), clamp(zb, bot, top - ht), w, ht) + tuple(st[2:]) + (k,))
    out.sort(key=lambda q: (-q[1], q[8]))
    return [q[:8] for q in out]


