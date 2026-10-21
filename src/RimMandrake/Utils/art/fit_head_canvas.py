#!/usr/bin/env python3
"""fit_head_canvas.py — measure, check and fit painted humanlike heads against the VANILLA head envelope.

The game draws every head texture stretched over the same 1.5 x 1.5 world-unit mesh (READ:
HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn; HeadTypeDef.GetGraphic passes Vector2.one), so a
head's drawn size is its alpha bbox as a FRACTION of its canvas, whatever the pixel size (vanilla 128,
ours 512). Head-slot apparel (helmets) uses that same head mesh (PawnRenderNode_Apparel.MeshSetFor,
useHeadMesh), so a hat covers the vanilla extent and anything painted beyond it shows around the hat.

SKULL MASS (owner 2026-10-20): "center the head regardless of additional appendages such as horns, ears, or anything
else. The bulk of the head must be searched for detectable chins (or bottom of skull mass) vs top of head ignoring
these extensions." So every placement and size is read from skull_mass() (opening + largest central mass + chin/crown
tip walk), never from the alpha bounding box, which only bounds the appendages.

The envelope (head_envelope.json, beside this file) holds the MEASURED vanilla extents per facing (bbox and skull)
and the allowed ratios/overhangs. Design + measurements: design/RimStarWars/head_envelope_2026-10-20.md.

usage:
  fit_head_canvas.py vanilla  DIR [--write]              re-measure extracted vanilla heads into the envelope
  fit_head_canvas.py check    HEAD_DIR... [--report MD]  judge each species dir (Stem_south/east/north.png); exit 1 on a violation
  fit_head_canvas.py measure  PNG...                     bbox and SKULL-MASS extents per file
  fit_head_canvas.py overlay  HEAD_DIR... --out PNG       skull mass tinted per facing, to LOOK at what was picked
  fit_head_canvas.py lineup   HEAD_DIR... --vanilla-dir D --out PNG   beside a vanilla head at true scale, vanilla box red
  fit_head_canvas.py fit --stem S --out DIR south.png east.png north.png [--height-ratio 1.0] [--anchor chin|crown|north-crown]
      scale ONE factor for all facings so the south SKULL height = vanilla skull x ratio, clamped so EVERY facing
      fits the envelope; the skull centroid goes on the vanilla centre and the skull chin on the vanilla chin
      (ears, horns, crests and trunks hang free). Prints the check of the output.
      [--facing-scale east=0.92 ...]  a per-facing UNIFORM multiplier on top of the one scale (aspect kept), for
      facings that disagree with the south (one uniform scale cannot fix a ratio between facings).
      [--squeeze-x east=0.96 ...]     a per-facing HORIZONTAL-only factor, refused below SQUEEZE_MIN (a visible
      distortion is a repaint, not a fit).
  (legacy) fit_head_canvas.py --stem S --out DIR south east north  ==  fit
"""
import argparse
import glob
import json
import os
import statistics
import sys
from collections import deque

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flier_guard as FG  # noqa: E402
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENVELOPE_PATH = os.path.join(HERE, "head_envelope.json")
FACINGS = ("south", "east", "north")
ALPHA = 20
CANVAS = 512
SQUEEZE_MIN = 0.93   # below this a horizontal squeeze reads as distortion: repaint instead


def load_envelope(path=ENVELOPE_PATH):
    with open(path) as f:
        return json.load(f)


def bbox_frac(im):
    """Alpha>ALPHA bbox as canvas fractions (l, t, r, b), or None if blank."""
    im = im.convert("RGBA")
    b = im.getchannel("A").point(lambda a: 255 if a > ALPHA else 0).getbbox()
    if not b:
        return None
    w, h = im.size
    return (b[0] / w, b[1] / h, b[2] / w, b[3] / h)


def dims(fb):
    l, t, r, b = fb
    return {"l": l, "t": t, "r": r, "b": b, "w": r - l, "h": b - t, "cx": (l + r) / 2}


# --- skull mass (owner 2026-10-20: centre and seat on the bulk of the head, never on ears/horns/trunk tips) ---
SKULL_OPEN_FRAC = 0.55    # opening radius / largest inscribed radius: anything thinner than this is an appendage
SKULL_TIP_FRAC = 0.06     # a walked run narrower than this x the core width is the END of a tip (chin point, dome)
SKULL_WORK = 512          # small canvases (vanilla 128) are measured upsampled to this, so radii are comparable


def _shift_and(m, square):
    p = np.pad(m, 1, constant_values=False)
    o = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    if square:
        o &= p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:]
    return o


def _shift_or(m, square):
    p = np.pad(m, 1, constant_values=False)
    o = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    if square:
        o |= p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
    return o


def _dilate(m, n):
    for i in range(n):   # alternating cross/square steps approximate a disk (octagon)
        m = _shift_or(m, i % 2 == 1)
    return m


def _largest_component(m):
    """Largest 4-connected component (ties: nearest the canvas centre) as a bool array."""
    lab = Image.fromarray((m * 255).astype(np.uint8)).copy()   # copy: fromarray shares the buffer, floodfill misses it
    h, w = m.shape
    best, best_key, v = None, None, 1
    rest = m.copy()
    while rest.any() and v < 255:
        ys, xs = np.nonzero(rest)
        ImageDraw.floodfill(lab, (int(xs[0]), int(ys[0])), v, thresh=0)
        comp = np.asarray(lab) == v
        rest &= ~comp
        cy, cx = np.nonzero(comp)
        key = (comp.sum(), -((cx.mean() - w / 2) ** 2 + (cy.mean() - h / 2) ** 2))
        if best_key is None or key > best_key:
            best, best_key = comp, key
        v += 1
    return best


SKULL_WALK_SLACK = 2       # px per row the walked span may widen (a chin/dome tapers; an ear base splaying out does not)


def _walk(m, core, steps, tip_w, down):
    """Row-width walk off the core's lowest (down) or highest row: each next row keeps the widest alpha run
    overlapping the current span (clipped to the span +-SKULL_WALK_SLACK). Returns (rows as (y, l, r), ended):
    ended is True when the run gave out (gap, or narrower than tip_w) within `steps` rows. The opening can only
    have rounded away a convex tip shorter than its radius, so a run that ENDS within it is the skull's own chin or
    crown and is given back; one still going after it is a trunk, horn or stalk and is not."""
    ys, xs = np.nonzero(core)
    y = ys.max() if down else ys.min()
    cols = xs[ys == y]
    l, r = int(cols.min()), int(cols.max()) + 1
    out, step, H, W = [], 1 if down else -1, m.shape[0], m.shape[1]
    for _ in range(steps):
        y += step
        if not 0 <= y < H:
            return out, True
        L, R = max(0, l - SKULL_WALK_SLACK), min(W, r + SKULL_WALK_SLACK)
        seg = np.concatenate(([False], m[y, L:R], [False]))
        edges = np.flatnonzero(seg[1:] != seg[:-1])
        best = None
        for s0, s1 in zip(edges[::2] + L, edges[1::2] + L):
            if s1 > l and s0 < r and (best is None or s1 - s0 > best[1] - best[0]):
                best = (s0, s1)
        if best is None or best[1] - best[0] < tip_w:
            return out, True
        l, r = int(best[0]), int(best[1])
        out.append((y, l, r))
    return out, False


def skull_mass(im):
    """The rigid head mass of a head texture: (mask at SKULL_WORK px, dims as canvas fractions) or (None, None).

    1. alpha mask; 2. the largest inscribed radius R (erosion depth); 3. morphological OPENING with radius
    SKULL_OPEN_FRAC x R removes every part thinner than that (ears, horns, crests, eye-stalks, trunks, hair strands);
    4. keep the largest central connected mass (the core); 5. ROW-WIDTH WALK (_walk): from the core's top and
    bottom rows, follow the alpha run under the current span outward; if it ENDS within the opening radius it is the
    chin point or dome edge the opening rounded off and is given back (the crown walk reaches half as far), if it is still going it is a trunk, horn or
    stalk and is left out; 6. crown = top and chin = bottom of that mass; width = its
    horizontal extent; cx = its mass centroid."""
    im = im.convert("RGBA")
    a = im.getchannel("A")
    if a.size != (SKULL_WORK, SKULL_WORK):
        a = a.resize((SKULL_WORK, SKULL_WORK), Image.BILINEAR)
    m = np.asarray(a) > ALPHA
    if not m.any():
        return None, None
    erosions = [m]
    while erosions[-1].any():
        erosions.append(_shift_and(erosions[-1], len(erosions) % 2 == 0))
    rmax = len(erosions) - 2
    r = max(1, int(round(SKULL_OPEN_FRAC * rmax)))
    core = _largest_component(_dilate(erosions[r], r) & m)
    if core is None:
        return None, None
    cys, cxs = np.nonzero(core)
    cw = cxs.max() - cxs.min() + 1
    skull = core.copy()
    for down in (False, True):
        # a crown is a blunt dome (the opening loses little of it); a chin can be a long muzzle point. Half the reach
        # upward keeps a short ear or horn tip (Lasat east) from passing for the dome top.
        rows, ended = _walk(m, core, r if down else r // 2, SKULL_TIP_FRAC * cw, down)
        for y, l, rr in rows if ended else ():
            skull[y, l:rr] = True
    ys, xs = np.nonzero(skull)
    n = float(SKULL_WORK)
    d = dims((xs.min() / n, ys.min() / n, (xs.max() + 1) / n, (ys.max() + 1) / n))
    d["cx"] = (xs.mean() + 0.5) / n
    d["r_open"] = r / n
    return skull, d


def measure_image(im):
    """{"bbox": dims, "skull": dims} as canvas fractions, or None when blank."""
    fb = bbox_frac(im)
    if not fb:
        return None
    _, sk = skull_mass(im)
    return {"bbox": dims(fb), "skull": sk}


def facing_files(head_dir):
    """{facing: path} for the head textures in a species dir (masks *_southm.png etc. skipped)."""
    out = {}
    for f in FACINGS:
        hits = sorted(p for p in glob.glob(os.path.join(head_dir, f"*_{f}.png")))
        if hits:
            out[f] = hits[0]
    return out


def limits_for(env, species=None):
    lim = dict(env["limits"])
    lim.update(env.get("species_overrides", {}).get(species or "", {}))
    return lim


def judge(extents, env, species=None):
    """extents: {facing: {"bbox": dims, "skull": dims}} (measure_image). Returns (violations, rows).

    The SKULL mass carries the head: its height against the vanilla skull height, its chin on the vanilla chin, its
    centroid on the vanilla centre, and the facing agreement. The alpha BBOX carries the appendages (ears, horns,
    crests, trunks) inside their own allowance: width, rise above the vanilla crown, hang below the vanilla chin,
    canvas margin. A facing with no extent is reported UNMEASURED, never passed."""
    lim = limits_for(env, species)
    van, vsk = env["vanilla"], env.get("vanilla_skull")
    if not vsk:
        raise SystemExit(f"{ENVELOPE_PATH} has no vanilla_skull block: run `vanilla DIR --write`")
    viol, rows = [], {}
    for f in FACINGS:
        e = extents.get(f)
        if e is None or e.get("skull") is None:
            viol.append((f, "UNMEASURED", None, None))
            continue
        bb, k, v, vs = e["bbox"], e["skull"], van[f], vsk[f]
        r = {"w_ratio": bb["w"] / v["w"], "skull_w_ratio": k["w"] / vs["w"], "h_ratio": k["h"] / vs["h"],
             "crown": (vs["t"] - k["t"]) / vs["h"], "chin": (k["b"] - vs["b"]) / vs["h"],
             "top_over": (v["t"] - bb["t"]) / v["h"], "below_chin": (bb["b"] - vs["b"]) / vs["h"],
             "cx_off": k["cx"] - vs["cx"]}
        rows[f] = r
        if r["w_ratio"] > lim["width_ratio_max"]:
            viol.append((f, "too wide (with appendages)", r["w_ratio"], lim["width_ratio_max"]))
        if r["w_ratio"] < lim["width_ratio_min"]:
            viol.append((f, "too narrow", r["w_ratio"], lim["width_ratio_min"]))
        if r["h_ratio"] > lim["height_ratio_max"]:
            viol.append((f, "skull too tall", r["h_ratio"], lim["height_ratio_max"]))
        if r["h_ratio"] < lim["height_ratio_min"]:
            viol.append((f, "skull too short", r["h_ratio"], lim["height_ratio_min"]))
        if r["chin"] > lim["below_chin_max"]:
            viol.append((f, "skull chin below vanilla chin", r["chin"], lim["below_chin_max"]))
        if r["chin"] < -lim["chin_rise_max"]:
            viol.append((f, "skull chin above vanilla chin", r["chin"], -lim["chin_rise_max"]))
        if r["top_over"] > lim["top_overhang_max"]:
            viol.append((f, "appendages above vanilla crown", r["top_over"], lim["top_overhang_max"]))
        if r["below_chin"] > lim["appendage_below_chin_max"]:
            viol.append((f, "appendages hang below vanilla chin", r["below_chin"], lim["appendage_below_chin_max"]))
        if abs(r["cx_off"]) > lim["center_x_tol"]:
            viol.append((f, "skull off-centre", r["cx_off"], lim["center_x_tol"]))
        m = lim["canvas_margin"]
        if bb["l"] < m or bb["t"] < m or bb["r"] > 1 - m or bb["b"] > 1 - m:
            viol.append((f, "touches canvas edge", min(bb["l"], bb["t"], 1 - bb["r"], 1 - bb["b"]), m))
    sk = {f: e["skull"] for f, e in extents.items() if e and e.get("skull")}
    s = sk.get("south")
    if s:
        for f in ("east", "north"):
            if f in sk:
                hr = sk[f]["h"] / s["h"]
                if round(abs(hr - 1), 3) > lim["facing_height_tol"]:
                    viol.append((f, "skull height vs south", hr, 1 + (lim["facing_height_tol"] if hr > 1 else -lim["facing_height_tol"])))
        if "north" in sk:
            wr = sk["north"]["w"] / s["w"]
            if round(abs(wr - 1), 3) > lim["north_width_tol"]:
                viol.append(("north", "skull width vs south", wr, 1 + (lim["north_width_tol"] if wr > 1 else -lim["north_width_tol"])))
        if "east" in sk and sk["east"]["w"] / s["w"] > lim["east_width_vs_south_max"]:
            viol.append(("east", "side skull wider than front", sk["east"]["w"] / s["w"], lim["east_width_vs_south_max"]))
    return viol, rows


def split_known(viol, env, species):
    """(new violations, {(facing, rule): why} known and present, [(facing, rule)] known but no longer present)."""
    listed = {(f, r): why for f, r, why in env.get("known_violations", {}).get(species or "", [])}
    seen = {(f, r) for f, r, _, _ in viol}
    new = [v for v in viol if (v[0], v[1]) not in listed]
    return new, {k: w for k, w in listed.items() if k in seen}, [k for k in listed if k not in seen]


def measure_dir(head_dir):
    files = facing_files(head_dir)
    ext = {}
    for f, p in files.items():
        m = measure_image(Image.open(p))
        if m:
            ext[f] = m
    return files, ext


def _rect(d, box, colour, width=2, n=SKULL_WORK):
    d.rectangle((box["l"] * n, box["t"] * n, box["r"] * n - 1, box["b"] * n - 1), outline=colour, width=width)


def overlay_image(im, env=None, facing=None, cell=SKULL_WORK):
    """The head on grey with its skull mass tinted green, skull box yellow (crown/chin lines across), alpha bbox
    cyan, and (given env + facing) the vanilla head box in red. For LOOKING at what the instrument picked."""
    im = im.convert("RGBA").resize((SKULL_WORK, SKULL_WORK), Image.LANCZOS)
    out = Image.new("RGBA", im.size, (96, 96, 96, 255))
    out.alpha_composite(im)
    mask, sk = skull_mass(im)
    if mask is not None:
        tint = np.zeros((SKULL_WORK, SKULL_WORK, 4), np.uint8)
        tint[mask] = (40, 220, 60, 90)
        out.alpha_composite(Image.fromarray(tint))
        d = ImageDraw.Draw(out)
        _rect(d, dims(bbox_frac(im)), (0, 220, 255, 255), 1)
        _rect(d, sk, (255, 230, 0, 255), 2)
        for y in (sk["t"], sk["b"]):
            d.line((0, y * SKULL_WORK, SKULL_WORK, y * SKULL_WORK), fill=(255, 230, 0, 160), width=1)
        d.line((sk["cx"] * SKULL_WORK, 0, sk["cx"] * SKULL_WORK, SKULL_WORK), fill=(255, 230, 0, 160), width=1)
    if env and facing:
        _rect(ImageDraw.Draw(out), env["vanilla"][facing], (230, 30, 30, 255), 2)
    return out.resize((cell, cell), Image.LANCZOS) if cell != SKULL_WORK else out


def cmd_overlay(a):
    """One row per species dir: south/east/north overlays (see overlay_image)."""
    env = load_envelope()
    rows = [(os.path.basename(os.path.normpath(d)), facing_files(d)) for d in a.dirs]
    c = a.cell
    sheet = Image.new("RGBA", (c * 3, c * len(rows)), (60, 60, 60, 255))
    d = ImageDraw.Draw(sheet)
    for i, (sp, files) in enumerate(rows):
        for j, f in enumerate(FACINGS):
            if f in files:
                sheet.alpha_composite(overlay_image(Image.open(files[f]), env, f, c), (j * c, i * c))
            d.text((j * c + 4, i * c + 4), f"{sp} {f}", fill=(255, 255, 255, 255))
    d.text((4, c * len(rows) - 14), "green skull mass, yellow skull box, cyan alpha bbox, red vanilla head box",
           fill=(255, 255, 255, 255))
    sheet.convert("RGB").save(a.out)
    print(f"overlay {a.out}")


def cmd_lineup(a):
    """Vanilla head beside each species at TRUE scale (every head canvas draws on the same 1.5-cell mesh), one row
    per facing, vanilla head box outlined red in every cell."""
    env = load_envelope()
    cols = [("vanilla", {f: os.path.join(a.vanilla_dir, f"{a.vanilla_stem}_{f}.png") for f in FACINGS})]
    cols += [(os.path.basename(os.path.normpath(d)), facing_files(d)) for d in a.dirs]
    c, top = a.cell, 22
    sheet = Image.new("RGBA", (c * len(cols), c * 3 + top), (96, 96, 96, 255))
    d = ImageDraw.Draw(sheet)
    if a.title:
        d.text((4, 4), a.title, fill=(255, 255, 255, 255))
    for i, (name, files) in enumerate(cols):
        for j, f in enumerate(FACINGS):
            x, y = i * c, top + j * c
            if f in files and os.path.exists(files[f]):
                sheet.alpha_composite(Image.open(files[f]).convert("RGBA").resize((c, c), Image.LANCZOS), (x, y))
            v = env["vanilla"][f]
            d.rectangle((x + v["l"] * c, y + v["t"] * c, x + v["r"] * c - 1, y + v["b"] * c - 1),
                        outline=(230, 30, 30, 255), width=2)
            d.text((x + 4, y + 4), f"{name} {f}", fill=(255, 255, 255, 255))
    sheet.convert("RGB").save(a.out)
    print(f"lineup {a.out}")


def cmd_measure(a):
    for p in a.pngs:
        im = Image.open(p)
        m = measure_image(im)
        if m is None:
            print(f"{p}  canvas {im.size}  BLANK")
            continue
        d, k = m["bbox"], m["skull"]
        print(f"{p}  canvas {im.size}  bbox l {d['l']:.3f} t {d['t']:.3f} r {d['r']:.3f} b {d['b']:.3f} "
              f"w {d['w']:.3f} h {d['h']:.3f} | skull crown {k['t']:.3f} chin {k['b']:.3f} w {k['w']:.3f} "
              f"h {k['h']:.3f} cx {k['cx']:.3f}")


def vanilla_stats(vdir, groups, kind="bbox"):
    """Median fractions per facing (kind bbox or skull) over the vanilla head textures whose names contain a group
    token. Vanilla is measured by the SAME skull-mass detector as our art, so the two compare like for like."""
    out = {}
    for f in FACINGS:
        ds = []
        for p in sorted(glob.glob(os.path.join(vdir, f"*_{f}.png"))):
            if any(g in os.path.basename(p) for g in groups):
                m = measure_image(Image.open(p))
                if m and m[kind]:
                    ds.append(m[kind])
        if not ds:
            raise SystemExit(f"no vanilla {f} heads matching {groups} in {vdir}")
        out[f] = {k: round(statistics.median(d[k] for d in ds), 4) for k in ("l", "t", "r", "b", "w", "h", "cx")}
        out[f]["n"] = len(ds)
        out[f]["w_range"] = [round(min(d["w"] for d in ds), 4), round(max(d["w"] for d in ds), 4)]
        out[f]["h_range"] = [round(min(d["h"] for d in ds), 4), round(max(d["h"] for d in ds), 4)]
    return out


def cmd_vanilla(a):
    env = load_envelope()
    env["vanilla"] = vanilla_stats(a.dir, env["vanilla_groups"]["average"])
    env["vanilla_narrow"] = vanilla_stats(a.dir, env["vanilla_groups"]["narrow"])
    env["vanilla_skull"] = vanilla_stats(a.dir, env["vanilla_groups"]["average"], "skull")
    print(json.dumps({k: env[k] for k in ("vanilla", "vanilla_narrow", "vanilla_skull")}, indent=1))
    if a.write:
        with open(ENVELOPE_PATH, "w") as f:
            json.dump(env, f, indent=1)
            f.write("\n")
        print(f"wrote {ENVELOPE_PATH}")


def fmt_row(rows, f):
    r = rows.get(f)
    if not r:
        return "UNMEASURED"
    return (f"skull h x{r['h_ratio']:.2f} w x{r['skull_w_ratio']:.2f} crown {r['crown']:+.2f} chin {r['chin']:+.2f} "
            f"cx {r['cx_off']:+.3f} | bbox w x{r['w_ratio']:.2f} above-crown {r['top_over']:+.2f} "
            f"below-chin {r['below_chin']:+.2f}")


def cmd_check(a):
    env = load_envelope()
    bad = 0
    lines = []
    for d in a.dirs:
        sp = os.path.basename(os.path.normpath(d))
        files, ext = measure_dir(d)
        viol, rows = judge(ext, env, sp)
        new, known, stale = split_known(viol, env, sp)
        bad += bool(new or stale)
        print(f"{'FAIL' if new or stale else 'OK  '} {sp}" + (f" ({len(known)} known)" if known else ""))
        for f in FACINGS:
            print(f"     {f:5s} {fmt_row(rows, f)}")
        for f, rule, val, lim in viol:
            tag = "KNOWN" if (f, rule) in known else "!"
            print(f"     {tag} {f} {rule}" + ("" if val is None else f": {val:.3f} (limit {lim:.3f})")
                  + (f" — {known[(f, rule)][:90]}" if tag == "KNOWN" else ""))
        for f, rule in stale:
            print(f"     ! STALE known violation {f} {rule}: it no longer occurs, delete it from known_violations")
        lines.append((sp, files, ext, rows, viol))
    if a.report:
        write_report(a.report, env, lines)
        print(f"report {a.report}")
    return 1 if bad else 0


def write_report(path, env, lines):
    van, vsk = env["vanilla"], env["vanilla_skull"]
    px = lambda x: round(x * CANVAS)  # noqa: E731
    o = ["# Painted head envelope report (skull mass)", "",
         "Generated by `src/RimMandrake/Utils/art/fit_head_canvas.py check`, envelope "
         "`src/RimMandrake/Utils/art/head_envelope.json`, design `design/RimStarWars/head_envelope_2026-10-20.md`. "
         "No PNG was rewritten. The SKULL is the bulk head mass with ears/horns/crests/trunks removed (owner "
         "2026-10-20); the BBOX is the alpha>20 box including them. Fractions of the canvas; px on a 512 canvas.", "",
         "## Vanilla (MEASURED, median of the Average head types, same detector)", "",
         "| facing | skull w | skull h | crown | chin | centre x | bbox w | bbox h |", "|---|---|---|---|---|---|---|---|"]
    for f in FACINGS:
        v, k = van[f], vsk[f]
        o.append(f"| {f} | {px(k['w'])} | {px(k['h'])} | {px(k['t'])} | {px(k['b'])} | {px(k['cx'])} | {px(v['w'])} | {px(v['h'])} |")
    o += ["", "Limits: " + ", ".join(f"`{k}` {v}" for k, v in env["limits"].items()), "",
          "## Per species (skull ratios to the vanilla skull; crown/chin in vanilla head heights, + = higher crown / lower chin)", "",
          "| species | facing | skull h x | skull w x | crown | chin | centre off | bbox w x | above crown | below chin |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for sp, files, ext, rows, viol in lines:
        for f in FACINGS:
            r = rows.get(f)
            if not r:
                o.append(f"| {sp} | {f} | UNMEASURED | | | | | | | |")
                continue
            o.append(f"| {sp} | {f} | {r['h_ratio']:.2f} | {r['skull_w_ratio']:.2f} | {r['crown']:+.2f} | {r['chin']:+.2f} | "
                     f"{px(r['cx_off']):+d} px | {r['w_ratio']:.2f} | {r['top_over']:+.2f} | {r['below_chin']:+.2f} |")
    o += ["", "## Violations", ""]
    for sp, files, ext, rows, viol in lines:
        if not viol:
            o.append(f"- **{sp}**: none")
            continue
        o.append(f"- **{sp}**:")
        known = split_known(viol, env, sp)[1]
        for f, rule, val, lim in viol:
            o.append(f"  - {f}: {rule}" + ("" if val is None else f" — {val:.3f} (limit {lim:.3f})")
                     + (f" — KNOWN: {known[(f, rule)]}" if (f, rule) in known else ""))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")


def fit_scale(meas, fscale, squeeze, env, height_ratio, species=None):
    """ONE scale s for all facings (facing f drawn at s x fscale[f], x-squeezed by squeeze[f]): the south SKULL height
    = vanilla skull height x ratio, then clamped so on every facing the skull stays under height_ratio_max, the
    appendage-inclusive bbox under width_ratio_max, and the seated head (skull chin on the vanilla chin, skull
    centroid on the vanilla centre) clear of the canvas margin. Returns (s, the binding limit)."""
    lim = limits_for(env, species)
    van, vsk = env["vanilla"], env["vanilla_skull"]
    m = lim["canvas_margin"] + 2.0 / CANVAS   # 2 px spare: resampling and the re-seat may move the edge a pixel
    s = height_ratio * vsk["south"]["h"] / (meas["south"]["skull"]["h"] * fscale["south"])
    why = f"south skull height x{height_ratio}"
    for f, e in meas.items():
        bb, k, vs = e["bbox"], e["skull"], vsk[f]
        fs, sq = fscale[f], fscale[f] * squeeze[f]
        caps = {"skull height_ratio_max": lim["height_ratio_max"] * vs["h"] / (k["h"] * fs),
                "bbox width_ratio_max": lim["width_ratio_max"] * van[f]["w"] / (bb["w"] * sq),
                "canvas top": (vs["b"] - m) / max(1e-6, (k["b"] - bb["t"]) * fs),
                "canvas left": (vs["cx"] - m) / max(1e-6, (k["cx"] - bb["l"]) * sq),
                "canvas right": (1 - m - vs["cx"]) / max(1e-6, (bb["r"] - k["cx"]) * sq)}
        if bb["b"] > k["b"]:
            caps["canvas bottom"] = (1 - m - vs["b"]) / ((bb["b"] - k["b"]) * fs)
        for name, cap in caps.items():
            if cap < s:
                s, why = cap, f"{f} {name}"
    return s, why


def _place(src, bb_px, k, kx, x, y):
    crop = src.crop(bb_px)
    crop = crop.resize((max(1, round(crop.width * kx)), max(1, round(crop.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(crop, (round(x), round(y)), crop)
    return out


def parse_facing_map(items, name, lo=None):
    out = {f: 1.0 for f in FACINGS}
    for it in items or ():
        k, _, v = it.partition("=")
        if k not in FACINGS or not v:
            raise SystemExit(f"--{name} wants FACING=FACTOR with FACING in {FACINGS}, got {it!r}")
        out[k] = float(v)
        if out[k] <= 0 or (lo is not None and not lo <= out[k] <= 1.0):
            raise SystemExit(f"--{name} {it}: factor outside [{lo or 0}, 1]")
    return out


def cmd_fit(a):
    env = load_envelope()
    fscale = parse_facing_map(a.facing_scale, "facing-scale")
    squeeze = parse_facing_map(a.squeeze_x, "squeeze-x", SQUEEZE_MIN)
    vsk = env["vanilla_skull"]
    ims = {f: Image.open(p).convert("RGBA") for f, p in (("south", a.south), ("east", a.east), ("north", a.north))}
    meas = {}
    for f, im in ims.items():
        meas[f] = measure_image(im)
        if not meas[f] or not meas[f]["skull"]:
            raise SystemExit(f"{f} is blank")
    s, why = fit_scale(meas, fscale, squeeze, env, a.height_ratio, a.species)
    os.makedirs(a.out, exist_ok=True)
    ext, crown_y = {}, None
    for f in FACINGS:
        im, bb, k = ims[f], meas[f]["bbox"], meas[f]["skull"]
        W = im.width
        ky, kx = s * fscale[f] * CANVAS / W, s * fscale[f] * squeeze[f] * CANVAS / W   # source px -> output px
        bb_px = (round(bb["l"] * W), round(bb["t"] * W), round(bb["r"] * W), round(bb["b"] * W))
        # target: skull centroid on the vanilla centre; skull chin on the vanilla chin (or, --anchor crown, the
        # east/north skull crown on the fitted south's crown line)
        tx = vsk[f]["cx"] * CANVAS
        if crown_y is not None and (a.anchor == "crown" and f != "south" or a.anchor == "north-crown" and f == "north"):
            ty, ref = crown_y, "t"
        else:
            ty, ref = vsk[f]["b"] * CANVAS, "b"
        x = tx - (k["cx"] * W - bb_px[0]) * kx
        y = ty - (k[ref] * W - bb_px[1]) * ky
        out = _place(im, bb_px, ky, kx, x, y)
        # one translation-only correction: re-measure the skull on the output (detection is near scale-invariant)
        got = measure_image(out)["skull"]
        x += tx - got["cx"] * CANVAS
        y += ty - got[ref] * CANVAS
        out = _place(im, bb_px, ky, kx, x, y)
        p = os.path.join(a.out, f"{a.stem}_{f}.png")
        out.save(p)
        ext[f] = measure_image(out)
        if f == "south":
            crown_y = ext[f]["skull"]["t"] * CANVAS
        print(f"{p}  scale x{s:.3f} ({why})" + (f" facing x{fscale[f]:.3f}" if fscale[f] != 1 else "")
              + (f" squeeze-x {squeeze[f]:.3f}" if squeeze[f] != 1 else ""))
    viol, rows = judge({k: v for k, v in ext.items() if v}, env, a.species)
    for f in FACINGS:
        print(f"  {f:5s} {fmt_row(rows, f)}")
    for f, rule, val, lim in viol:
        print(f"  ! {f} {rule}" + ("" if val is None else f": {val:.3f} (limit {lim:.3f})"))
    return 1 if viol else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("measure", "vanilla", "check", "fit", "overlay", "lineup", "-h", "--help"):
        argv = ["fit"] + argv   # legacy form
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure"); m.add_argument("pngs", nargs="+")
    v = sub.add_parser("vanilla"); v.add_argument("dir"); v.add_argument("--write", action="store_true")
    c = sub.add_parser("check"); c.add_argument("dirs", nargs="+"); c.add_argument("--report")
    f = sub.add_parser("fit")
    f.add_argument("--stem", required=True); f.add_argument("--out", required=True)
    f.add_argument("--species", help="key into species_overrides (defaults to none)")
    f.add_argument("--height-ratio", type=float, default=1.0, help="south SKULL height / vanilla south skull height")
    f.add_argument("--anchor", choices=("chin", "crown", "north-crown"), default="chin",
                   help="chin: every facing's skull chin on the vanilla chin; crown: east/north skull crown on the "
                        "south's skull crown line; north-crown: only the north on the south's crown (a back view whose "
                        "nape runs below the front's chin line, the Ortolan case)")
    f.add_argument("--facing-scale", action="append", metavar="FACING=X",
                   help="per-facing uniform multiplier on top of the one scale (repeatable)")
    f.add_argument("--squeeze-x", action="append", metavar="FACING=X",
                   help=f"per-facing horizontal-only factor, {SQUEEZE_MIN}..1 (repeatable)")
    f.add_argument("--target-h", type=int, help="legacy, ignored: height now comes from --height-ratio")
    f.add_argument("south"); f.add_argument("east"); f.add_argument("north")
    o = sub.add_parser("overlay", help="skull-mass overlay sheet, one row per species dir")
    o.add_argument("dirs", nargs="+"); o.add_argument("--out", required=True); o.add_argument("--cell", type=int, default=256)
    ln = sub.add_parser("lineup", help="species heads beside a vanilla head at true scale, vanilla box in red")
    ln.add_argument("dirs", nargs="+"); ln.add_argument("--out", required=True); ln.add_argument("--cell", type=int, default=256)
    ln.add_argument("--vanilla-dir", required=True, help="extracted Core head PNGs (<stem>_<facing>.png)")
    ln.add_argument("--vanilla-stem", default="Male_Average_Normal"); ln.add_argument("--title")
    a = ap.parse_args(argv)
    if a.cmd == "fit":
        FG.refuse_fliers('fit_head_canvas.py fit', a.stem, a.out, a.south, a.east, a.north)
    return {"measure": cmd_measure, "vanilla": cmd_vanilla, "check": cmd_check, "fit": cmd_fit,
            "overlay": cmd_overlay, "lineup": cmd_lineup}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
