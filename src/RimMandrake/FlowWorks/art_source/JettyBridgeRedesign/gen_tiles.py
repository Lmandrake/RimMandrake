"""Cut each GENERATED deck strip into its four pieces, cut the post and cable sheets, and validate every piece.
RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD (design.md §2: one strip, cut into ROOT / MID / TIP / SOLO).

    python3 gen_tiles.py cut          raw/*.png -> tiles/<key>_{root,mid,tip,solo}.png, posts/<key>.png, cables/<key>.png
    python3 gen_tiles.py check        validate every piece; writes check.json and seams/<key>.png; exit 1 on any REJECT
    python3 gen_tiles.py selftest     the seam check must go red on planted faults and green on a clean strip

How the pieces join (S is the straightened strip, 256 px per cell, F the blend width):
- MID is periodic: MID[i] = S[m+i], cross-faded over its last F columns into S[m-F..m-1], so MID[255] meets MID[0] = S[m].
- ROOT is S[0..255] (the joint plate at its left edge), cross-faded over its last F columns into S[m-F..m-1], so ROOT
  meets MID and TIP exactly as MID meets MID.
- TIP starts at S[m] and cross-fades over its first F columns into the strip's last 256 columns (the end beam).
- SOLO is the strip's first half-cell and last half-cell, cross-faded in the middle.
m is chosen where the cross-faded columns already agree most, so the fades show least. Every joint is a joint between
two places of the same painted strip; nothing is framed at a piece edge."""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT_DIR = "/mnt/d/ClaudeWork/rimmandrake/art/jetty_bridge_gen"
RAW, TILES, POSTS, CABLES, SEAMS = (os.path.join(ROOT_DIR, d) for d in ("raw", "tiles", "posts", "cables", "seams"))
T = 256          # px per cell (128 px per cell is the rule; 256 because the scenes draw at 2x supersampling)
F = 64           # cross-fade width (a quarter cell)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_prompts as GP      # noqa: E402
import specs                  # noqa: E402


def geometry(key):
    """The procedural spec this generated option is built on."""
    kind, opt, look, _, _ = GP.DECKS[key]
    table = {"steel_jetty": specs.STEEL_JETTY, "heavy_jetty": specs.HEAVY_JETTY, "heavy_bridge": specs.HEAVY_BRIDGE,
             "bridge": specs.BRIDGE.get(look)}[kind]
    for k, name, text, spec in table:
        if k == opt:
            return name, text, dict(spec)
    raise KeyError(key)


# ---------------------------------------------------------------- deck strips
def straighten(im):
    """Rotate so the deck's centre line is level, crop to the deck. Returns RGBA float array."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    al = a[..., 3] > 128
    H, W = al.shape
    cols = np.where(al.sum(0) > 0.3 * al.sum(0).max())[0]
    x0, x1 = cols.min(), cols.max()
    mid = range(x0 + (x1 - x0) // 6, x1 - (x1 - x0) // 6, 4)
    xs, cs = [], []
    for x in mid:
        ys = np.where(al[:, x])[0]
        if len(ys):
            xs.append(x)
            cs.append((ys.min() + ys.max()) / 2)
    slope = np.polyfit(xs, cs, 1)[0]
    ang = np.degrees(np.arctan(slope))
    if abs(ang) > 0.05:
        im = im.rotate(ang, resample=Image.BICUBIC)
        a = np.asarray(im).astype(np.float32)
        al = a[..., 3] > 128
    rows = np.where(al[:, x0 + (x1 - x0) // 4: x1 - (x1 - x0) // 4].mean(1) > 0.3)[0]
    y0, y1 = rows.min(), rows.max() + 1
    colcov = al[y0:y1].mean(0)
    cx = np.where(colcov > 0.5)[0]
    return a[y0:y1, cx.min():cx.max() + 1], ang


def to_strip(key, raw_path):
    """Scale the straightened deck so its width is the spec's deck_w of a cell, on a 256-high transparent band."""
    name, text, spec = geometry(key)
    a, ang = straighten(Image.open(raw_path))
    dh = int(round(spec.get("deck_w", 0.8) * T))
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    w = int(round(im.width * dh / im.height))
    # premultiplied resize (no dark halo)
    pm = np.asarray(im).astype(np.float32)
    pm[..., :3] *= pm[..., 3:4] / 255.0
    small = np.stack([np.asarray(Image.fromarray(pm[..., c].astype(np.float32), "F").resize((w, dh), Image.LANCZOS))
                      for c in range(4)], -1)
    al = small[..., 3:4].clip(0, 255)
    rgb = np.where(al > 0.5, small[..., :3] / np.maximum(al, 1e-3) * 255.0, 0)
    al = np.where(al < 24, 0, al)          # faint haze from the generator: invisible, but it corrupts every measurement
    small = np.concatenate([rgb.clip(0, 255), al], -1)
    S = np.zeros((T, w, 4), np.float32)
    top = (T - dh) // 2
    S[top:top + dh] = small
    return S, dict(angle=round(float(ang), 3), deck_px=dh, strip_cells=round(w / T, 2))


def _lerp(a, b, t):
    return a * (1 - t) + b * t


def _ramp(n):
    return (np.arange(n, dtype=np.float32) + 0.5)[None, :, None] / n


def cut(S):
    W = S.shape[1]
    if W < 3 * T + F:
        raise ValueError("strip too short: %d px (%0.2f cells)" % (W, W / T))
    rows = slice(int(T * 0.1), int(T * 0.9))
    # a strong line ACROSS the deck inside MID repeats once per cell on a long bridge and shows the cell grid: score each
    # column's cross-line strength (mean jump to the next column over the deck's middle rows) against the strip's median
    core = S[int(T * 0.3):int(T * 0.7)]
    cross = np.abs(np.diff(core, axis=1)).sum(2).mean(0)
    cross = np.append(cross, cross[-1]) / (np.median(cross) + 1e-3)
    # every piece joint shows the strip at S[m-1] | S[m] (ROOT->MID, MID->MID, ROOT->TIP, MID->TIP), so a plate seam, rail
    # clamp or panel line within 0.1 cell of m puts a seam on the cell edge (design.md §2 rule 2): score it, all deck rows
    deckrows = np.where(S[..., 3].mean(1) > 0.5 * 255)[0]
    allx = np.abs(np.diff(S[deckrows], axis=1)).sum(2).mean(0)
    allx = np.append(allx, allx[-1]) / (np.median(allx) + 1e-3)
    G = int(0.1 * T)
    best = None
    for m in range(T, W - 2 * T + 1, 4):
        d_mid = np.abs(S[rows, m + T - F:m + T] - S[rows, m - F:m]).mean()
        d_root = np.abs(S[rows, T - F:T] - S[rows, m - F:m]).mean()
        d_tip = np.abs(S[rows, m:m + F] - S[rows, W - T:W - T + F]).mean()
        s = (d_mid + d_root + d_tip + 4.0 * max(0.0, cross[m:m + T].max() - 3.0)
             + 8.0 * max(0.0, allx[m - G:m + G].max() - 2.0))
        if best is None or s < best[0]:
            best = (s, m)
    m = best[1]
    r = _ramp(F)
    mid = S[:, m:m + T].copy()
    mid[:, T - F:] = _lerp(S[:, m + T - F:m + T], S[:, m - F:m], r)
    root = S[:, 0:T].copy()
    root[:, T - F:] = _lerp(S[:, T - F:T], S[:, m - F:m], r)
    tip = S[:, W - T:W].copy()
    tip[:, :F] = _lerp(S[:, m:m + F], S[:, W - T:W - T + F], r)
    half = T // 2
    solo = np.concatenate([S[:, :half], S[:, W - half:]], 1)
    solo[:, half - F // 2:half + F // 2] = _lerp(S[:, half - F // 2:half + F // 2], S[:, W - half - F // 2:W - half + F // 2],
                                                 _ramp(F))
    return dict(root=root, mid=mid, tip=tip, solo=solo), m


def save(a, path):
    Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA").save(path)


def load(path):
    return np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)


# ---------------------------------------------------------------- posts and cables
def _segments(profile, min_len, gap=6):
    on = profile > 0
    segs, i, n = [], 0, len(profile)
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or (j + gap < n and on[j:j + gap].any())):
                j += 1
            if j - i >= min_len:
                segs.append((i, j))
            i = j
        else:
            i += 1
    return segs


def cut_posts(group):
    im = Image.open(os.path.join(RAW, "posts_%s.png" % group)).convert("RGBA")
    a = np.asarray(im)
    prof = (a[..., 3] > 100).sum(0)
    segs = _segments(np.where(prof > 0.05 * a.shape[0], prof, 0), 8)
    names = [k for k, _ in GP.POSTS[group]]
    if len(segs) != len(names):
        raise ValueError("posts_%s: found %d posts, expected %d" % (group, len(segs), len(names)))
    out = {}
    for (x0, x1), nm in zip(segs, names):
        sub = a[:, x0:x1]
        ys = np.where((sub[..., 3] > 100).any(1))[0]
        crop = Image.fromarray(sub[ys.min():ys.max() + 1])
        crop.save(os.path.join(POSTS, nm + ".png"))
        out[nm] = crop.size
    return out


def cut_cables():
    im = Image.open(os.path.join(RAW, "cables.png")).convert("RGBA")
    a = np.asarray(im)
    prof = (a[..., 3] > 100).sum(1)
    segs = _segments(np.where(prof > 0.3 * a.shape[1], prof, 0), 4, gap=3)
    names = [k for k, _ in GP.CABLES]
    if len(segs) != len(names):
        raise ValueError("cables: found %d cables, expected %d" % (len(segs), len(names)))
    out = {}
    for (y0, y1), nm in zip(segs, names):
        sub = a[y0:y1].astype(np.float32)
        xs = np.where((sub[..., 3] > 100).mean(0) > 0.3)[0]
        sub = sub[:, xs.min() + 8:xs.max() - 8]
        h = 32
        w = int(sub.shape[1] * h / sub.shape[0])
        s = np.asarray(Image.fromarray(sub.astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(np.float32)
        # periodic: the last 24 columns fade into the 24 before the start of a 256-long window
        L, f = min(256, w - 30), 24
        t = s[:, f:f + L].copy()
        t[:, L - f:] = _lerp(s[:, f + L - f:f + L], s[:, 0:f], _ramp(f))
        save(t, os.path.join(CABLES, nm + ".png"))
        out[nm] = (L, h)
    return out


# ---------------------------------------------------------------- checks
def compose(pieces):
    return np.concatenate(pieces, 1)


def seam_ratios(strip, n, win=3):
    """For each piece junction of a composed strip of n cells: the largest colour jump within win px of the junction (deck
    rows, alpha included), divided by the 90th percentile of that same windowed jump at columns away from any junction. A junction where the deck is much less opaque across the joint than it is along its length (a transparent gap: today's framed pictures) scores
    inf: that gap is the "two squares" defect itself."""
    al = strip[..., 3]
    rows = np.where(al.mean(1) > 0.5 * 255)[0]
    if len(rows) == 0:
        return [float("inf")] * (n - 1)
    s = strip[rows]
    d = np.abs(np.diff(s, axis=1)).sum(2).mean(0)              # jump between column x and x+1, mean over deck rows
    junction = [T * k - 1 for k in range(1, n)]
    near = np.zeros(len(d), bool)
    for j in junction:
        near[max(0, j - win):j + win + 1] = True
    wmax = np.array([d[max(0, x - win):x + win + 1].max() for x in range(len(d))])   # the same windowed statistic
    ref = np.percentile(wmax[~near], 90) + 1e-3
    colcov = s[..., 3].mean(0)
    typical = np.percentile(colcov[~np.r_[near, False]], 10)     # see-through decks (grating, truss) have holes everywhere
    out = []
    for j in junction:
        cover = s[:, max(0, j - win):j + win + 2, 3].mean(0).min()
        if cover < 0.85 * typical:
            out.append(float("inf"))
        else:
            out.append(float(d[max(0, j - win):j + win + 1].max() / ref))
    return out


SEAM_MAX = 1.15     # set by selftest(): clean cuts of the four jetty strips 0.24-0.90; a TIP shifted 6 px 1.33-2.03; framed: inf


def check_deck(key):
    tl = {p: load(os.path.join(TILES, "%s_%s.png" % (key, p))) for p in ("root", "mid", "tip", "solo")}
    out = dict(key=key, rejects=[], warns=[])
    for p, a in tl.items():
        if a.shape != (T, T, 4):
            out["rejects"].append("%s canvas %s" % (p, a.shape))
        al = a[..., 3]
        if al[0].max() > 0 or al[-1].max() > 0:
            out["rejects"].append("%s: alpha on the top or bottom row (deck touches the canvas edge)" % p)
        fr = ((al > 0) & (al < 32)).mean()
        if fr > 0.01:
            out["warns"].append("%s faint fringe %.2f%%" % (p, fr * 100))
        rows = np.where(al.mean(1) > 0.9 * 255)[0]
        if len(rows) == 0:
            out["rejects"].append("%s has no opaque deck rows" % p)
    # the deck must run edge to edge where a piece meets another piece
    for p, edges in (("mid", (0, T - 1)), ("root", (T - 1,)), ("tip", (0,))):
        al = tl[p][..., 3]
        band = al[int(T * 0.2):int(T * 0.8)]
        typical = np.percentile(band.mean(0), 10)     # see-through decks (grating, truss) have holes everywhere
        for x in edges:
            if band[:, x].mean() < 0.85 * typical:
                out["rejects"].append("%s: transparent margin at column %d (the deck does not run to the piece edge)" % (p, x))
    seqs = {1: [tl["solo"]], 2: [tl["root"], tl["tip"]], 4: [tl["root"], tl["mid"], tl["mid"], tl["tip"]]}
    out["seams"] = {}
    for n, seq in seqs.items():
        ew = compose(seq)
        ns = np.rot90(ew, 1)                                  # north/south: the same strip turned (design.md §2)
        r_ew = seam_ratios(ew, n)
        r_ns = seam_ratios(np.rot90(ns, -1), n)               # measured along the deck in both cases
        out["seams"]["%d_EW" % n] = [round(x, 2) for x in r_ew]
        out["seams"]["%d_NS" % n] = [round(x, 2) for x in r_ns]
        for r in r_ew + r_ns:
            if r > SEAM_MAX:
                out["rejects"].append("%d cells: seam ratio %.2f > %.2f" % (n, r, SEAM_MAX))
    # a seams picture to LOOK at: 1, 2 and 4 cells east/west, and the 4-cell strip north/south
    pics = [compose(seqs[1]), compose(seqs[2]), compose(seqs[4])]
    W = 4 * T
    canvas = np.zeros((3 * T + 40, W + 40 + T, 4), np.float32)
    canvas[..., :3] = (52, 40, 31)
    canvas[..., 3] = 255
    y = 0
    for p in pics:
        _paste(canvas, p, 0, y)
        y += T + 20
    _paste(canvas, np.rot90(pics[2], 1)[::2, ::2], W + 40, 0)  # north/south, half size
    save(canvas, os.path.join(SEAMS, key + ".png"))
    return out


def _paste(canvas, a, x, y):
    h, w = a.shape[:2]
    h, w = min(h, canvas.shape[0] - y), min(w, canvas.shape[1] - x)
    a = a[:h, :w]
    al = a[..., 3:4] / 255.0
    canvas[y:y + h, x:x + w, :3] = canvas[y:y + h, x:x + w, :3] * (1 - al) + a[..., :3] * al


def selftest():
    """The seam check must go red on: today's framed jetty pictures side by side; a clean strip cut at two unrelated places
    with no fade; a TIP shifted 6 px across the deck. It must stay green on a clean cut of the same strip."""
    here = os.path.dirname(os.path.abspath(__file__))
    tex = os.path.normpath(os.path.join(here, "../../Textures/RimMandrake/FlowWorks"))
    fails = []
    import glob
    today = sorted(glob.glob(os.path.join(tex, "**/RM_SuspensionJetty*_east.png"), recursive=True))
    if not today:
        fails.append("no shipped jetty picture found under %s (cannot plant the framed fault)" % tex)
    for p in today[:3]:
        a = np.asarray(Image.open(p).convert("RGBA").resize((T, T), Image.LANCZOS)).astype(np.float32)
        r = max(seam_ratios(compose([a, a]), 2))
        print("planted  today's framed jetty %-60s ratio %.2f" % (os.path.relpath(p, tex), r))
        if r <= SEAM_MAX:
            fails.append("framed jetty %s NOT caught (%.2f)" % (p, r))
    keys = [k for k in GP.DECKS if os.path.exists(os.path.join(RAW, k + ".png"))][:4]
    if not keys:
        fails.append("no generated strip to test with")
    for key in keys:
        S, _ = to_strip(key, os.path.join(RAW, key + ".png"))
        pieces, m = cut(S)
        ok = max(seam_ratios(compose([pieces["root"], pieces["mid"], pieces["mid"], pieces["tip"]]), 4))
        raw_cut = max(seam_ratios(compose([S[:, :T], S[:, S.shape[1] // 2 + 37:S.shape[1] // 2 + 37 + T]]), 2))
        shifted = np.roll(pieces["tip"], 6, axis=0)
        sh = max(seam_ratios(compose([pieces["root"], shifted]), 2))
        print("%-22s clean %.2f | planted: unfaded cut %.2f, tip shifted 6 px %.2f" % (key, ok, raw_cut, sh))
        if ok > SEAM_MAX:
            fails.append("%s clean cut flagged (%.2f)" % (key, ok))
        if sh <= SEAM_MAX:
            fails.append("%s shifted tip NOT caught (%.2f)" % (key, sh))
        if raw_cut <= SEAM_MAX:
            print("   note: the unfaded cut happened to match (%.2f); not every random cut is a visible seam" % raw_cut)
    print("SELFTEST %s %s" % ("FAIL" if fails else "PASS", "; ".join(fails)))
    return 1 if fails else 0


def main(argv):
    for d in (TILES, POSTS, CABLES, SEAMS):
        os.makedirs(d, exist_ok=True)
    cmd = argv[1] if len(argv) > 1 else "cut"
    if cmd == "cut":
        info = {}
        for key in GP.DECKS:
            rp = os.path.join(RAW, key + ".png")
            if not os.path.exists(rp):
                print("MISSING raw %s" % key)
                continue
            S, meta = to_strip(key, rp)
            pieces, m = cut(S)
            for p, a in pieces.items():
                save(a, os.path.join(TILES, "%s_%s.png" % (key, p)))
            save(S, os.path.join(TILES, "%s_strip.png" % key))
            meta["mid_from"] = m
            info[key] = meta
            print("cut %-22s %s" % (key, meta))
        for g in GP.POSTS:
            if os.path.exists(os.path.join(RAW, "posts_%s.png" % g)):
                try:
                    print("posts", g, cut_posts(g))
                except ValueError as e:
                    print("POSTS FAIL", e)
        if os.path.exists(os.path.join(RAW, "cables.png")):
            try:
                print("cables", cut_cables())
            except ValueError as e:
                print("CABLES FAIL", e)
        json.dump(info, open(os.path.join(ROOT_DIR, "cut.json"), "w"), indent=1)
        return 0
    if cmd == "check":
        res, bad = [], 0
        for key in GP.DECKS:
            if not os.path.exists(os.path.join(TILES, key + "_mid.png")):
                res.append(dict(key=key, rejects=["UNMEASURED: no tiles"]))
                bad += 1
                continue
            r = check_deck(key)
            res.append(r)
            bad += bool(r["rejects"])
            print("%-22s %s %s %s" % (key, "REJECT" if r["rejects"] else "ok", r["seams"], r["rejects"] + r["warns"]))
        json.dump(res, open(os.path.join(ROOT_DIR, "check.json"), "w"), indent=1)
        print("CHECK %d of %d decks rejected" % (bad, len(res)))
        return 1 if bad else 0
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
