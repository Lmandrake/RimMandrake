#!/usr/bin/env python3
"""fit_head_canvas.py — measure, check and fit painted humanlike heads against the VANILLA head envelope.

The game draws every head texture stretched over the same 1.5 x 1.5 world-unit mesh (READ:
HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn; HeadTypeDef.GetGraphic passes Vector2.one), so a
head's drawn size is its alpha bbox as a FRACTION of its canvas, whatever the pixel size (vanilla 128,
ours 512). Head-slot apparel (helmets) uses that same head mesh (PawnRenderNode_Apparel.MeshSetFor,
useHeadMesh), so a hat covers the vanilla extent and anything painted beyond it shows around the hat.

The envelope (head_envelope.json, beside this file) holds the MEASURED vanilla extents per facing and the
allowed ratios/overhangs. Design + measurements: design/RimStarWars/head_envelope_2026-10-20.md.

usage:
  fit_head_canvas.py measure  PNG...                     bbox fractions per file
  fit_head_canvas.py vanilla  DIR [--write]              re-measure extracted vanilla heads into the envelope
  fit_head_canvas.py check    HEAD_DIR... [--report MD]  judge each species dir (Stem_south/east/north.png); exit 1 on a violation
  fit_head_canvas.py fit --stem S --out DIR south.png east.png north.png [--height-ratio 1.10] [--anchor chin|crown]
      scale ONE factor for all facings so the south height = vanilla x ratio, clamped so EVERY facing fits
      the envelope; centre x and chin line come from vanilla. Prints the check of the output.
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

from PIL import Image

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


def facing_files(head_dir):
    """{facing: path} for the head textures in a species dir (masks *_southm.png etc. skipped)."""
    out = {}
    for f in FACINGS:
        hits = sorted(p for p in glob.glob(os.path.join(head_dir, f"*_{f}.png")))
        if hits:
            out[f] = hits[0]
    return out


def judge(extents, env, species=None):
    """extents: {facing: dims dict}. Returns list of (facing, rule, value, limit) violations
    and the per-facing ratio rows. A facing with no extent is reported UNMEASURED, never passed."""
    lim = dict(env["limits"])
    lim.update(env.get("species_overrides", {}).get(species or "", {}))
    van = env["vanilla"]
    viol, rows = [], {}
    for f in FACINGS:
        e = extents.get(f)
        v = van[f]
        if e is None:
            viol.append((f, "UNMEASURED", None, None))
            continue
        r = {"w_ratio": e["w"] / v["w"], "h_ratio": e["h"] / v["h"],
             "top_over": (v["t"] - e["t"]) / v["h"], "below_chin": (e["b"] - v["b"]) / v["h"],
             "cx_off": e["cx"] - v["cx"]}
        rows[f] = r
        if r["w_ratio"] > lim["width_ratio_max"]:
            viol.append((f, "too wide", r["w_ratio"], lim["width_ratio_max"]))
        if r["w_ratio"] < lim["width_ratio_min"]:
            viol.append((f, "too narrow", r["w_ratio"], lim["width_ratio_min"]))
        if r["h_ratio"] > lim["height_ratio_max"]:
            viol.append((f, "too tall", r["h_ratio"], lim["height_ratio_max"]))
        if r["h_ratio"] < lim["height_ratio_min"]:
            viol.append((f, "too short", r["h_ratio"], lim["height_ratio_min"]))
        if r["top_over"] > lim["top_overhang_max"]:
            viol.append((f, "crest/ears above vanilla crown", r["top_over"], lim["top_overhang_max"]))
        if r["below_chin"] > lim["below_chin_max"]:
            viol.append((f, "hangs below vanilla chin", r["below_chin"], lim["below_chin_max"]))
        if r["below_chin"] < -lim["chin_rise_max"]:
            viol.append((f, "chin above vanilla chin", r["below_chin"], -lim["chin_rise_max"]))
        if abs(r["cx_off"]) > lim["center_x_tol"]:
            viol.append((f, "off-centre", r["cx_off"], lim["center_x_tol"]))
        m = lim["canvas_margin"]
        if e["l"] < m or e["t"] < m or e["r"] > 1 - m or e["b"] > 1 - m:
            viol.append((f, "touches canvas edge", min(e["l"], e["t"], 1 - e["r"], 1 - e["b"]), m))
    s = extents.get("south")
    if s:
        for f in ("east", "north"):
            e = extents.get(f)
            if e:
                hr = e["h"] / s["h"]
                if round(abs(hr - 1), 3) > lim["facing_height_tol"]:
                    viol.append((f, "height vs south", hr, 1 + (lim["facing_height_tol"] if hr > 1 else -lim["facing_height_tol"])))
        n = extents.get("north")
        if n:
            wr = n["w"] / s["w"]
            if round(abs(wr - 1), 3) > lim["north_width_tol"]:
                viol.append(("north", "width vs south", wr, 1 + (lim["north_width_tol"] if wr > 1 else -lim["north_width_tol"])))
        e = extents.get("east")
        if e and e["w"] / s["w"] > lim["east_width_vs_south_max"]:
            viol.append(("east", "side profile wider than front", e["w"] / s["w"], lim["east_width_vs_south_max"]))
    return viol, rows


def measure_dir(head_dir):
    files = facing_files(head_dir)
    ext = {}
    for f, p in files.items():
        fb = bbox_frac(Image.open(p))
        if fb:
            ext[f] = dims(fb)
    return files, ext


def cmd_measure(a):
    for p in a.pngs:
        im = Image.open(p)
        fb = bbox_frac(im)
        d = dims(fb) if fb else None
        print(f"{p}  canvas {im.size}  " + (
            "BLANK" if d is None else
            f"l {d['l']:.3f} t {d['t']:.3f} r {d['r']:.3f} b {d['b']:.3f}  w {d['w']:.3f} h {d['h']:.3f}"))


def vanilla_stats(vdir, groups):
    """Median bbox fractions per facing over the vanilla head textures whose names contain a group token."""
    out = {}
    for f in FACINGS:
        ds = []
        for p in sorted(glob.glob(os.path.join(vdir, f"*_{f}.png"))):
            if any(g in os.path.basename(p) for g in groups):
                fb = bbox_frac(Image.open(p))
                if fb:
                    ds.append(dims(fb))
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
    print(json.dumps({"vanilla": env["vanilla"], "vanilla_narrow": env["vanilla_narrow"]}, indent=1))
    if a.write:
        with open(ENVELOPE_PATH, "w") as f:
            json.dump(env, f, indent=1)
            f.write("\n")
        print(f"wrote {ENVELOPE_PATH}")


def fmt_row(rows, f):
    r = rows.get(f)
    if not r:
        return "UNMEASURED"
    return (f"w x{r['w_ratio']:.2f} h x{r['h_ratio']:.2f} above-crown {r['top_over']:+.2f} "
            f"below-chin {r['below_chin']:+.2f} cx {r['cx_off']:+.3f}")


def cmd_check(a):
    env = load_envelope()
    bad = 0
    lines = []
    for d in a.dirs:
        sp = os.path.basename(os.path.normpath(d))
        files, ext = measure_dir(d)
        viol, rows = judge(ext, env, sp)
        bad += bool(viol)
        print(f"{'FAIL' if viol else 'OK  '} {sp}")
        for f in FACINGS:
            print(f"     {f:5s} {fmt_row(rows, f)}")
        for f, rule, val, lim in viol:
            print(f"     ! {f} {rule}" + ("" if val is None else f": {val:.3f} (limit {lim:.3f})"))
        lines.append((sp, files, ext, rows, viol))
    if a.report:
        write_report(a.report, env, lines)
        print(f"report {a.report}")
    return 1 if bad else 0


def write_report(path, env, lines):
    van = env["vanilla"]
    px = lambda x: round(x * CANVAS)  # noqa: E731
    o = ["# Painted head envelope report — 2026-10-20", "",
         "Generated by `src/RimMandrake/Utils/art/fit_head_canvas.py check`, envelope "
         "`src/RimMandrake/Utils/art/head_envelope.json`, design `design/RimStarWars/head_envelope_2026-10-20.md`. "
         "No PNG was rewritten. Extents are alpha>20 bboxes as canvas fractions; px are on a 512 canvas.", "",
         "## Vanilla envelope (MEASURED, median of the Average head types)", "",
         "| facing | width | height | top | chin (bottom) | centre x |", "|---|---|---|---|---|---|"]
    for f in FACINGS:
        v = van[f]
        o.append(f"| {f} | {v['w']:.3f} ({px(v['w'])} px) | {v['h']:.3f} ({px(v['h'])} px) | {px(v['t'])} | {px(v['b'])} | {px(v['cx'])} |")
    o += ["", "Limits: " + ", ".join(f"`{k}` {v}" for k, v in env["limits"].items()), "",
          "## Per species (ratio to vanilla per facing)", "",
          "| species | facing | w px | h px | width x | height x | top overhang | below chin | centre off |",
          "|---|---|---|---|---|---|---|---|---|"]
    for sp, files, ext, rows, viol in lines:
        for f in FACINGS:
            e, r = ext.get(f), rows.get(f)
            if not r:
                o.append(f"| {sp} | {f} | UNMEASURED | | | | | | |")
                continue
            o.append(f"| {sp} | {f} | {px(e['w'])} | {px(e['h'])} | {r['w_ratio']:.2f} | {r['h_ratio']:.2f} | "
                     f"{r['top_over']:+.2f} | {r['below_chin']:+.2f} | {px(r['cx_off']):+d} px |")
    o += ["", "## Violations", ""]
    for sp, files, ext, rows, viol in lines:
        if not viol:
            o.append(f"- **{sp}**: none")
            continue
        o.append(f"- **{sp}**:")
        for f, rule, val, lim in viol:
            o.append(f"  - {f}: {rule}" + ("" if val is None else f" — {val:.3f} (limit {lim:.3f})"))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")


def fit_scale(crops_frac, env, height_ratio, species=None):
    """One uniform scale (canvas-fraction units) for all facings: south height = vanilla x ratio,
    then clamped so every facing's width/height ratio sits inside the envelope maxima."""
    lim = dict(env["limits"])
    lim.update(env.get("species_overrides", {}).get(species or "", {}))
    van = env["vanilla"]
    s = height_ratio * van["south"]["h"] / crops_frac["south"][1]
    for f, (w, h) in crops_frac.items():
        s = min(s, lim["width_ratio_max"] * van[f]["w"] / w, lim["height_ratio_max"] * van[f]["h"] / h)
    return s


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
    van = env["vanilla"]
    ims = {f: Image.open(p).convert("RGBA") for f, p in (("south", a.south), ("east", a.east), ("north", a.north))}
    crops, frac = {}, {}
    for f, im in ims.items():
        fb = bbox_frac(im)
        if not fb:
            raise SystemExit(f"{f} is blank")
        box = (round(fb[0] * im.width), round(fb[1] * im.height), round(fb[2] * im.width), round(fb[3] * im.height))
        crops[f] = (im.crop(box), im.width)
        frac[f] = ((fb[2] - fb[0]) * fscale[f] * squeeze[f], (fb[3] - fb[1]) * fscale[f])
    s = fit_scale(frac, env, a.height_ratio, a.species)
    os.makedirs(a.out, exist_ok=True)
    ext = {}
    for f, (crop, srcw) in crops.items():
        w = max(1, round(frac[f][0] * s * CANVAS))
        h = max(1, round(frac[f][1] * s * CANVAS))
        crop = crop.resize((w, h), Image.LANCZOS)
        out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        x = round(van[f]["cx"] * CANVAS) - w // 2
        if a.anchor == "crown" and f != "south":
            # same crown line as the fitted south: a trunk/snout hanging below the chin stays below it
            y = crown_y
        else:
            y = min(round(van[f]["b"] * CANVAS) - h, CANVAS - h)
        if f == "south":
            crown_y = y
        out.paste(crop, (max(0, x), max(0, y)), crop)
        p = os.path.join(a.out, f"{a.stem}_{f}.png")
        out.save(p)
        fb = bbox_frac(out)
        ext[f] = dims(fb) if fb else None
        print(f"{p}  scale x{s:.3f}" + (f" facing x{fscale[f]:.3f}" if fscale[f] != 1 else "")
              + (f" squeeze-x {squeeze[f]:.3f}" if squeeze[f] != 1 else "") + f"  bbox_px {tuple(round(v * CANVAS) for v in fb) if fb else None}")
    viol, rows = judge({k: v for k, v in ext.items() if v}, env, a.species)
    for f in FACINGS:
        print(f"  {f:5s} {fmt_row(rows, f)}")
    for f, rule, val, lim in viol:
        print(f"  ! {f} {rule}" + ("" if val is None else f": {val:.3f} (limit {lim:.3f})"))
    return 1 if viol else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("measure", "vanilla", "check", "fit", "-h", "--help"):
        argv = ["fit"] + argv   # legacy form
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure"); m.add_argument("pngs", nargs="+")
    v = sub.add_parser("vanilla"); v.add_argument("dir"); v.add_argument("--write", action="store_true")
    c = sub.add_parser("check"); c.add_argument("dirs", nargs="+"); c.add_argument("--report")
    f = sub.add_parser("fit")
    f.add_argument("--stem", required=True); f.add_argument("--out", required=True)
    f.add_argument("--species", help="key into species_overrides (defaults to none)")
    f.add_argument("--height-ratio", type=float, default=1.10, help="south height / vanilla south height")
    f.add_argument("--anchor", choices=("chin", "crown"), default="chin",
                   help="chin: every facing's bottom on the vanilla chin; crown: east/north share the south's top "
                        "(use when a facing hangs a trunk or snout below the chin — the Ortolan east case)")
    f.add_argument("--facing-scale", action="append", metavar="FACING=X",
                   help="per-facing uniform multiplier on top of the one scale (repeatable)")
    f.add_argument("--squeeze-x", action="append", metavar="FACING=X",
                   help=f"per-facing horizontal-only factor, {SQUEEZE_MIN}..1 (repeatable)")
    f.add_argument("--target-h", type=int, help="legacy, ignored: height now comes from --height-ratio")
    f.add_argument("south"); f.add_argument("east"); f.add_argument("north")
    a = ap.parse_args(argv)
    return {"measure": cmd_measure, "vanilla": cmd_vanilla, "check": cmd_check, "fit": cmd_fit}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
