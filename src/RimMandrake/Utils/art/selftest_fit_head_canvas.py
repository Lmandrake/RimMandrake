#!/usr/bin/env python3
"""selftest_fit_head_canvas.py — the head envelope check and fit (fit_head_canvas.py + head_envelope.json).

Part 0, skull mass (owner 2026-10-20: centre on the skull, never on ears/horns/trunk tips): synthetic heads with
ears hanging BELOW the chin, horns rising above the crown, wide eye-stalks/wings and a trunk; the old alpha-bbox
reading is shown to miss the skull's crown/chin/centre and the skull-mass reading finds them, and fit seats the skull
(not the ear tips) on the vanilla chin. Part 1, synthetic heads: an in-envelope head passes; a wide side profile, a blank facing (UNMEASURED, never a
pass) and a trunk hanging below the chin are caught; fit clamps an over-wide head into the envelope with one
scale; --facing-scale / --squeeze-x bring a disagreeing side profile into line and a squeeze past SQUEEZE_MIN is
refused; the legacy argv form still runs. Part 2, a SANITY PROBE on real art: the PRE-FIT Mimbanese heads (read
from git at PREFIT_REV, since the shipped ones were refitted 2026-10-20) are flagged for the side profile the
owner called "far too wide", and the bbox-seated 6d77ea123 Ortolan is flagged for the skull chin riding high (the ears
were its chin), so the instrument can see the defects it was built for; the shipped heads now pass. Part 3, canvas
frame vs on screen: the Big and Small head-scale formula, species_render agreeing with it and with the live
measurement, and an on-screen target driving fit's height ratio, check's band and lineup --onscreen.
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_head_canvas as F  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FAILS = []
PREFIT_REV = "e9d81b61f"   # last commit holding the pre-envelope-fit species heads
BBOX_FIT_REV = "6d77ea123"  # the bbox-seated refit the owner rejected (Ortolan ears used as the chin)
SPECIES = ("Lasat", "Mimbanese", "Nelvaanian", "Ortolan")


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def head(path, w_frac, h_frac, cx=0.5, bottom=0.70, canvas=512):
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    if w_frac:
        w, h = w_frac * canvas, h_frac * canvas
        x0, y1 = cx * canvas - w / 2, bottom * canvas
        ImageDraw.Draw(im).ellipse((x0, y1 - h, x0 + w - 1, y1 - 1), fill=(200, 150, 120, 255))
    im.save(path)


def creature(path, appendages, w=0.36, h=0.39, cx=0.5, bottom=0.70, canvas=512):
    """An elliptical skull (w, h, cx, bottom in canvas fractions) plus appendage ellipses (x0, y0, x1, y1) that
    overlap it. Returns the true skull extents (t, b, cx) as fractions."""
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = lambda box: tuple(v * canvas for v in box)  # noqa: E731
    d.ellipse(c((cx - w / 2, bottom - h, cx + w / 2, bottom)), fill=(200, 150, 120, 255))
    for box in appendages:
        d.ellipse(c(box), fill=(120, 140, 220, 255))
    im.save(path)
    return bottom - h, bottom, cx


def rules(viol):
    return {(f, r) for f, r, _, _ in viol}


env = F.load_envelope()
van = env["vanilla"]
check(all(f in van and 0.3 < van[f]["w"] < 0.45 and 0.35 < van[f]["h"] < 0.45 for f in F.FACINGS),
      "envelope carries measured vanilla extents for all three facings", van)
check(all(f in env.get("vanilla_skull", {}) and abs(env["vanilla_skull"][f]["h"] - van[f]["h"]) < 0.02
          for f in F.FACINGS), "envelope carries the vanilla SKULL extents (== bbox on appendage-free vanilla heads)")

# ---- Part 0: skull mass vs alpha bbox ----
TOL = 0.012   # 6 px on 512: the skull reading must land on the true skull within this
with tempfile.TemporaryDirectory() as td:
    cases = {
        # Ortolan-like: long ears from the temples hanging well BELOW the chin, and a trunk
        "ears_below_chin": [(0.28, 0.40, 0.34, 0.86), (0.66, 0.40, 0.72, 0.86), (0.48, 0.60, 0.52, 0.86)],
        # Nelvaanian/Lasat-like: horns/ears rising far ABOVE the crown, asymmetric so the bbox centre moves too
        "horns_above_crown": [(0.30, 0.10, 0.36, 0.42), (0.58, 0.16, 0.64, 0.42)],
        # Rakata-like eye-stalks / wings: thin, much wider than the skull, one side longer
        "wide_stalks": [(0.06, 0.44, 0.40, 0.48), (0.60, 0.44, 0.97, 0.48)],
    }
    for name, apps in cases.items():
        p = os.path.join(td, f"{name}.png")
        t, b, cx = creature(p, apps)
        im = Image.open(p)
        bb = F.dims(F.bbox_frac(im))
        _, sk = F.skull_mass(im)
        old_ok = abs(bb["t"] - t) <= TOL and abs(bb["b"] - b) <= TOL and abs(bb["cx"] - cx) <= TOL
        new_err = max(abs(sk["t"] - t), abs(sk["b"] - b), abs(sk["cx"] - cx))
        check(not old_ok, f"{name}: the old alpha-bbox reading misses the skull (crown/chin/centre)",
              (bb["t"], bb["b"], bb["cx"], t, b, cx))
        check(new_err <= TOL, f"{name}: the skull-mass reading finds crown, chin and centre within {TOL}",
              (round(sk["t"], 3), round(sk["b"], 3), round(sk["cx"], 3), t, b, cx))
    # a plain vanilla-like head: skull == bbox (the detector costs nothing where there are no appendages)
    p = os.path.join(td, "plain.png")
    t, b, cx = creature(p, [])
    _, sk = F.skull_mass(Image.open(p))
    check(max(abs(sk["t"] - t), abs(sk["b"] - b), abs(sk["cx"] - cx)) <= TOL, "a head with no appendages: skull == bbox", sk)

    # fit seats the SKULL chin (not the ear tips) on the vanilla chin: source has short ears hanging below the chin
    src = []
    for f in F.FACINGS:
        p = os.path.join(td, f"eared_{f}.png")
        creature(p, [(0.28, 0.45, 0.33, 0.80), (0.67, 0.45, 0.72, 0.80)], w=0.40, h=0.42, bottom=0.72)
        src.append(p)
    out = os.path.join(td, "eared_fit")
    rc = F.main(["fit", "--stem", "E_Head", "--out", out] + src)
    _, ext = F.measure_dir(out)
    vsk = env["vanilla_skull"]
    chin_err = max(abs(ext[f]["skull"]["b"] - vsk[f]["b"]) for f in F.FACINGS)
    hang = min(ext[f]["bbox"]["b"] - ext[f]["skull"]["b"] for f in F.FACINGS)
    check(rc == 0 and chin_err <= TOL and hang > 0.03,
          "fit puts the skull chin on the vanilla chin and lets the ears hang below it", (rc, chin_err, hang))
    # and the bbox reading of that fitted head would have called the ear tips its chin
    check(max(abs(ext[f]["bbox"]["b"] - vsk[f]["b"]) for f in F.FACINGS) > 0.03,
          "the fitted head's alpha bbox bottom is the ear tips, not the chin (old method would have raised it)")
    ov = F.overlay_image(Image.open(os.path.join(out, "E_Head_south.png")), env, "south", 128)
    check(ov.size == (128, 128), "the skull-mass overlay renders")

with tempfile.TemporaryDirectory() as td:
    good = os.path.join(td, "Good")
    os.makedirs(good)
    for f in F.FACINGS:
        head(os.path.join(good, f"Good_Head_{f}.png"), van[f]["w"] * 1.05, van[f]["h"] * 1.05, bottom=van[f]["b"])
    _, ext = F.measure_dir(good)
    viol, _ = F.judge(ext, env, "Good")
    check(not viol, "a head 5% over vanilla on every facing passes", viol)

    wide = os.path.join(td, "Wide")
    os.makedirs(wide)
    for f in F.FACINGS:
        k = 1.5 if f == "east" else 1.0
        head(os.path.join(wide, f"Wide_Head_{f}.png"), van["south"]["w"] * k, van[f]["h"], bottom=van[f]["b"])
    # the mask a CutoutComplex head ships must not be taken for a facing
    Image.new("RGBA", (512, 512), (0, 0, 0, 255)).save(os.path.join(wide, "Wide_Head_eastm.png"))
    _, ext = F.measure_dir(wide)
    r = rules(F.judge(ext, env, "Wide")[0])
    check(("east", "side skull wider than front") in r and ("east", "too wide (with appendages)") in r,
          "a 1.5x-wide side profile is flagged (and the _eastm mask is skipped)", r)

    blank = os.path.join(td, "Blank")
    os.makedirs(blank)
    head(os.path.join(blank, "Blank_Head_south.png"), van["south"]["w"], van["south"]["h"], bottom=van["south"]["b"])
    head(os.path.join(blank, "Blank_Head_east.png"), 0, 0)
    _, ext = F.measure_dir(blank)
    r = rules(F.judge(ext, env, "Blank")[0])
    check(("east", "UNMEASURED") in r and ("north", "UNMEASURED") in r,
          "blank and missing facings are UNMEASURED, never passed", r)

    trunk = os.path.join(td, "Trunk")
    os.makedirs(trunk)
    for f in F.FACINGS:
        b = van[f]["b"] + (0.08 if f == "east" else 0)
        head(os.path.join(trunk, f"Trunk_Head_{f}.png"), van[f]["w"], van[f]["h"], bottom=b)
    _, ext = F.measure_dir(trunk)
    check(("east", "skull chin below vanilla chin") in rules(F.judge(ext, env, "Trunk")[0]),
          "a facing whose skull sits below the vanilla chin is flagged")

    src = os.path.join(td, "Src")
    os.makedirs(src)
    paths = []
    for f in F.FACINGS:
        p = os.path.join(src, f"big_{f}.png")
        head(p, 0.70, 0.60, bottom=0.95)       # a full-canvas render, much too wide
        paths.append(p)
    out = os.path.join(td, "out")
    rc = F.main(["fit", "--stem", "Big_Head", "--out", out] + paths)
    _, ext = F.measure_dir(out)
    viol, rows = F.judge(ext, env, "Big")
    check(rc == 0 and not viol, "fit clamps an over-wide render inside the envelope", (rc, viol))
    check(all(rows[f]["w_ratio"] <= env["limits"]["width_ratio_max"] + 0.01 for f in F.FACINGS),
          "fit honours width_ratio_max", rows)

    # a side profile 1.36x its front (the Mimbanese case): one scale cannot fix it, per-facing factors can
    side = os.path.join(td, "Side")
    os.makedirs(side)
    sp = []
    for f, (w, h) in {"south": (0.34, 0.47), "east": (0.46, 0.465), "north": (0.26, 0.34)}.items():
        p = os.path.join(side, f"side_{f}.png")
        head(p, w, h)
        sp.append(p)
    o3 = os.path.join(td, "side_plain")
    check(F.main(["fit", "--stem", "S_Head", "--out", o3] + sp) == 1, "one uniform scale leaves facing disagreement flagged")
    o4 = os.path.join(td, "side_fixed")
    rc = F.main(["fit", "--stem", "S_Head", "--out", o4, "--facing-scale", "north=1.30", "--facing-scale", "east=0.915",
                 "--squeeze-x", "east=0.955"] + sp)
    _, ext = F.measure_dir(o4)
    viol, rows = F.judge(ext, env, "S")
    check(rc == 0 and not viol, "--facing-scale + --squeeze-x bring the facings into agreement", (rc, viol))
    try:
        F.main(["fit", "--stem", "S_Head", "--out", o4, "--squeeze-x", f"east={F.SQUEEZE_MIN - 0.05:.2f}"] + sp)
        refused = False
    except SystemExit:
        refused = True
    check(refused, "a squeeze below SQUEEZE_MIN is refused (that is a repaint)")

    out2 = os.path.join(td, "legacy")
    rc = F.main(["--target-h", "240", "--stem", "L", "--out", out2] + paths)
    check(rc == 0 and len(os.listdir(out2)) == 3, "legacy argv (no subcommand) still fits", os.listdir(out2))

HEADS = "src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/Heads"
with tempfile.TemporaryDirectory() as td:
    pre = os.path.join(td, "Mimbanese")
    os.makedirs(pre)
    got = 0
    for f in F.FACINGS:
        rel = f"{HEADS}/Mimbanese/Mimbanese_Head_{f}.png"
        r = subprocess.run(["git", "-C", REPO, "show", f"{PREFIT_REV}:{rel}"], capture_output=True)
        if r.returncode == 0 and r.stdout:
            with open(os.path.join(pre, os.path.basename(rel)), "wb") as fh:
                fh.write(r.stdout)
            got += 1
    if got == 3:
        _, ext = F.measure_dir(pre)
        check(("east", "side skull wider than front") in rules(F.judge(ext, env, "Mimbanese")[0]),
              "SANITY: the pre-fit Mimbanese side profile is flagged too wide")
    else:
        print(f"UNMEASURED sanity probe: pre-fit Mimbanese heads not readable at {PREFIT_REV} ({got}/3)")
    pre = os.path.join(td, "Ortolan")
    os.makedirs(pre)
    got = 0
    for f in F.FACINGS:
        rel = f"{HEADS}/Ortolan/Ortolan_Head_{f}.png"
        r = subprocess.run(["git", "-C", REPO, "show", f"{BBOX_FIT_REV}:{rel}"], capture_output=True)
        if r.returncode == 0 and r.stdout:
            with open(os.path.join(pre, os.path.basename(rel)), "wb") as fh:
                fh.write(r.stdout)
            got += 1
    if got == 3:
        _, ext = F.measure_dir(pre)
        check(("south", "skull chin above vanilla chin") in rules(F.judge(ext, env, "Ortolan")[0]),
              "SANITY: the bbox-seated Ortolan (ears as chin) is flagged for a skull chin riding high")
    else:
        print(f"UNMEASURED sanity probe: bbox-fit Ortolan heads not readable at {BBOX_FIT_REV} ({got}/3)")
for sp_name in SPECIES:
    d = os.path.join(REPO, HEADS, sp_name)
    if os.path.isdir(d):
        _, ext = F.measure_dir(d)
        new, known, stale = F.split_known(F.judge(ext, env, sp_name)[0], env, sp_name)
        check(not new and not stale, f"shipped {sp_name} heads sit inside the envelope"
              + (f" (bar {len(known)} known, item-owned)" if known else ""), (new, stale))
    else:
        print(f"UNMEASURED: {sp_name} head dir absent")

# ---- Part 3: canvas frame vs on-screen (Big and Small scales the head with body size) ----
b, h = F.bs_render_size(0.75)
check(abs(b - 1.48) < 0.005 and abs(h - 1.369) < 0.002, "B&S formula: HalfJotun +0.75 -> body x1.48, head x1.369", (b, h))
check(F.bs_render_size(0.0) == (1.0, 1.0), "B&S formula: no size offset draws the head at x1.0")
check(F.bs_render_size(-0.35)[1] < 1, "B&S formula: a small frame shrinks the head")
sr = {k: v for k, v in env.get("species_render", {}).items() if not k.startswith("_")}
check(set(SPECIES) <= set(sr), "species_render covers the four painted species", sorted(sr))
for sp_name, r in sr.items():
    want = F.bs_render_size(r["size_offset"])[1]
    check(abs(r["engine_head_scale"] - want) < 0.002, f"{sp_name}: engine_head_scale is the B&S formula of its size offset",
          (r["engine_head_scale"], want))
    check(abs(r["measured_live"] - r["engine_head_scale"]) <= 0.03,
          f"{sp_name}: the live-measured head scale agrees with the formula within 0.03", r)
check(all(F.canvas_target(env, s) is None or sr[s]["onscreen_skull_target"] is not None for s in sr),
      "no canvas target without an owner on-screen target")
env2 = json.loads(json.dumps(env))
env2["species_render"]["Lasat"]["onscreen_skull_target"] = 1.0
ct = F.canvas_target(env2, "Lasat")
check(abs(ct - 1 / 1.369) < 0.002, "an on-screen target 1.0 on a x1.369 head asks the canvas for x0.730", ct)
lim2 = F.limits_for(env2, "Lasat")
check(abs(lim2["height_ratio_max"] - env["limits"]["height_ratio_max"] * ct) < 1e-9
      and F.limits_for(env, "Lasat")["height_ratio_max"] == env["limits"]["height_ratio_max"],
      "the size bands are centred on the canvas target only when a target is set")
_orig_load = F.load_envelope
F.load_envelope = lambda path=None: env2
try:
    with tempfile.TemporaryDirectory() as td:
        src = []
        for f in F.FACINGS:
            p = os.path.join(td, f"t_{f}.png")
            head(p, van[f]["w"], van[f]["h"], bottom=van[f]["b"])
            src.append(p)
        out = os.path.join(td, "Lasat")
        rc = F.main(["fit", "--species", "Lasat", "--stem", "Lasat_Head", "--out", out] + src)
        _, ext = F.measure_dir(out)
        hr = ext["south"]["skull"]["h"] / env["vanilla_skull"]["south"]["h"]
        check(rc == 0 and abs(hr - ct) < 0.02, "fit --species with a target sizes the skull to the canvas target", (rc, hr, ct))
        vd = os.path.join(td, "van")
        os.makedirs(vd)
        for f in F.FACINGS:
            head(os.path.join(vd, f"V_{f}.png"), van[f]["w"], van[f]["h"], bottom=van[f]["b"])
        sheet = os.path.join(td, "lineup.png")
        F.main(["lineup", out, "--vanilla-dir", vd, "--vanilla-stem", "V", "--out", sheet, "--cell", "100", "--onscreen"])
        check(Image.open(sheet).size[0] == 2 * round(100 * 1.369), "lineup --onscreen widens cells to the largest engine scale",
              Image.open(sheet).size)
finally:
    F.load_envelope = _orig_load

print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
