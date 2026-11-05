#!/usr/bin/env python3
"""selftest_weir_spill_animated.py -- WEIR_SPILL_REDRAW_ANIMATED_NOT_PAINTED. Owner 2026-10-24, on the weir looks: "The
white water I'm hoping is merely an indicator of the design intention, not actual graphics. We will want to animate a
much better design of water going over the weir."

Offline, on the INSTALLED textures (Textures/RimMandrake/FlowWorks/Weir) and the committed sources; no git, no game:
  no_painted_water  no look paints water into its wall: every body has < 1 % "water" pixels (opaque, lum 150..255, blue
                    over red by 12..60: the old Modern curtain 176,204,216..238,246,250 and Futuristic bays 184,204,216..)
  no_static_sheet   no RM_BankWeirSpill_<facing>.png is installed (or staged in art_source/Weir/out_photo) for any look
  frames            every look and facing has RM_BankWeirSpill_<facing>_00..11 at 128x128 and nothing past _11
  moves             consecutive frames differ (mean premultiplied change over the sheet's footprint >= 3 of 255), no two
                    frames are the same
  seamless_loop     the step 11 -> 00 is an ordinary step (0.5x..2x the median of the other steps), not a jump
  falls_downstream  on every falling facing (east falls down-screen, north right, south left) the best-matching shift of
                    the sheet's shading between consecutive frames, inside it, points downstream in >= 9 of the 12 steps
  foam_from_the_foot the white water starts under the wall (RM_WeirArt.FoamStart per look, read from RM_Weir.cs): the
                    body covers >= 90 % from that row to its foot in every facing and no foot lies > 4 px upstream of it
                    (no strip of still water); the sheet's toe sits on the foot in every frame
  csharp            RM_Weir.cs: Print prints no Spill; DrawAt draws DrawSpill and DrawWhiteWater on one frame clock;
                    DrawSpill draws RM_WeirArt.SpillPath(<look>, facing, frame) = "<base>Spill_<facing>_NN"; the setting
                    off draws frame 0 (still) and no foam; DrawWhiteWater's plane runs from FoamStart(look) to the lane's
                    reach; the offline scene uses the same table; FoamFrames == frames on disk == whitewater_frames.FRAMES
  dll_current       Assemblies/RimMandrakeFlowWorks.dll.srchash: every listed source's sha256 and the DLL's own match
  can-fail          each must FAIL: Modern east body with the old curtain sheet painted back; a static sheet re-added;
                    a look's frame 05 copied over 06 (a frozen step); a set whose frames run upstream (order reversed);
                    a sheet cut short of its foot; Futuristic's foam from the centre line; Modern's from 0.1 (a strip);
                    the Print spill line put back
"""
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_scenes_weir as W  # noqa: E402  (art(): a 2x look read on its 1x canvas)

FW = HERE.parent
INSTALLED = FW / "Textures/RimMandrake/FlowWorks/Weir"
OUT_PHOTO = FW / "art_source/Weir/out_photo"
WEIR_CS = FW / "Source/Rivers/RM_Weir.cs"
DLL = FW / "Assemblies/RimMandrakeFlowWorks.dll"
SRCHASH = FW / "Assemblies/RimMandrakeFlowWorks.dll.srchash"
WW_SRC = FW / "art_source/Weir/whitewater_frames.py"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
FACINGS = ("east", "west", "north", "south")
BODIES = ("RM_BankWeir_east", "RM_BankWeir_west", "RM_BankWeir_north", "RM_BankWeir_south")
N = 12
FALL = {"east": (0, 1), "north": (1, 1), "south": (1, -1)}   # (axis, sign) of downstream in the image
fails = []


def check(name, ok, detail=""):
    print("%-4s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def px(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)


def lum(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


# ---- the art ---------------------------------------------------------------------------------------------------------
def water_frac(a):
    """Share of the opaque body that is pale blue-white water colour; a light's anti-aliased halo (white metal blended
    with the cyan lights, within 2 px of a light pixel) is not water."""
    light = (a[..., 2] > 170) & (a[..., 1] > 150) & (a[..., 0] < 140)
    near = light.copy()
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            near |= np.roll(np.roll(light, dy, 0), dx, 1)
    m = (a[..., 3] >= 128)
    rgb = a[..., :3]
    l, br = lum(rgb), rgb[..., 2] - rgb[..., 0]
    water = m & ~near & (l >= 150) & (br >= 12) & (br <= 60)
    return float(water.sum() / max(1, m.sum()))


def no_painted_water(d):
    worst = {}
    for look in LOOKS:
        for b in BODIES:
            worst["%s/%s" % (look, b)] = water_frac(px(Path(d) / look / (b + ".png")))
    bad = {k: round(v, 3) for k, v in worst.items() if v >= 0.01}
    return not bad, "bodies over 1 %% water px: %s" % bad if bad else "max water px %.4f (< 0.01) over %d bodies" % (
        max(worst.values()), len(worst))


def no_static_sheet(*dirs):
    found = [str(p) for d in dirs for look in LOOKS for f in FACINGS
             for p in [Path(d) / look / ("RM_BankWeirSpill_%s.png" % f)] if p.exists()]
    return not found, "static sheets: %s" % found if found else "no RM_BankWeirSpill_<facing>.png in %d dirs" % len(dirs)


def frames_of(d, look, f):
    return [Path(d) / look / ("RM_BankWeirSpill_%s_%02d.png" % (f, k)) for k in range(N)]


def frame_set(d):
    bad = []
    for look in LOOKS:
        for f in FACINGS:
            for p in frames_of(d, look, f):
                if not p.is_file() or Image.open(p).size != (128, 128):
                    bad.append(p.name if not p.is_file() else "%s size %s" % (p.name, Image.open(p).size))
            extra = Path(d) / look / ("RM_BankWeirSpill_%s_%02d.png" % (f, N))
            if extra.exists():
                bad.append(extra.name)
    return not bad, "missing/wrong: %s" % bad[:6] if bad else "%d looks x %d facings x %d frames, 128x128" % (
        len(LOOKS), len(FACINGS), N)


def pre(a):
    return np.dstack([a[..., :3] * a[..., 3:4] / 255.0, a[..., 3]])


def steps(fr):
    """Mean premultiplied change of each step k -> k+1 (the last is 11 -> 00) over the sheet's footprint (every pixel
    some frame draws): a lip-only sheet (west) is small, and the empty canvas is not motion."""
    foot = np.any([f[..., 3] > 0 for f in fr], 0)
    return [float(np.abs(pre(fr[(k + 1) % N]) - pre(fr[k]))[foot].mean()) if foot.any() else 0.0 for k in range(N)]


def shade(a):
    """Premultiplied luminance: what the eye sees of the sheet over the water."""
    return lum(a[..., :3]) * a[..., 3] / 255.0


def interior(fr, axis, margin=6):
    """Pixels every frame draws, at least `margin` px inside the sheet along the fall: the static lip, foot and canvas
    edges would otherwise vote for a shift of 0."""
    m = np.all([f[..., 3] > 0 for f in fr], 0)
    out = m.copy()
    for k in range(1, margin + 1):
        out &= np.roll(m, k, axis) & np.roll(m, -k, axis)
    return out


def best_shift(a, b, axis, mask, span=8):
    """The integer shift s (|s| <= span) along `axis` that best maps frame a's shading onto frame b's inside `mask`."""
    sa, sb = shade(a), shade(b)
    errs = {s: float(np.abs(np.roll(sa, s, axis) - sb)[mask].mean()) for s in range(-span, span + 1)}
    return min(errs, key=lambda s: (errs[s], abs(s)))


def motion(d):
    """(moves_ok, loop_ok, falls_ok, details)."""
    m_bad, l_bad, f_bad = [], [], []
    for look in LOOKS:
        for f in FACINGS:
            fr = [px(p) for p in frames_of(d, look, f)]
            st = steps(fr)
            same = [(i, j) for i in range(N) for j in range(i + 1, N) if (fr[i] == fr[j]).all()]
            if min(st) < 3.0 or same:
                m_bad.append("%s %s min step %.2f same %s" % (look, f, min(st), same[:2]))
            med = float(np.median(st[:-1]))
            if not (0.5 * med <= st[-1] <= 2.0 * med):
                l_bad.append("%s %s 11->00 %.2f vs median %.2f" % (look, f, st[-1], med))
            if f in FALL:
                axis, sign = FALL[f]
                inner = interior(fr, axis)
                down = sum(1 for k in range(N) if inner.any() and best_shift(fr[k], fr[(k + 1) % N], axis, inner) * sign > 0)
                if down < 9:
                    f_bad.append("%s %s %d/12 downstream" % (look, f, down))
    return m_bad, l_bad, f_bad


def fall_alpha(d, look, f):
    """The body's opaque mask at 1x with rows along the fall, row 0 upstream (east falls down-screen, west up, north
    right, south left)."""
    a = np.asarray(W.art(d, look, "RM_BankWeir_" + f))[..., 3] >= 128
    return {"east": a, "west": a[::-1], "north": a.T, "south": a.T[::-1]}[f]


def foam_from_the_foot(d, starts):
    """The white water starts `starts[look]` cells upstream of the wet cell's downstream edge, under the wall: for every
    look and facing, the body hides it from there to its foot (>= 90 % opaque between the start row and each column's
    foot) and the foot is never more than 4 px upstream of the start (the toe's reach: no strip of still water); and the
    sheet's toe is on the foot (alpha >= 60 within 6 px of the foot in >= 90 % of columns, every frame, falling facings)."""
    bad, worst_cov, worst_strip = [], 1.0, 0
    for look in LOOKS:
        r0 = int(round(128 * (1 - starts[look])))
        for f in FACINGS:
            a = fall_alpha(d, look, f)
            foot = np.where(a, np.arange(a.shape[0])[:, None], -1).max(0)
            seg = np.concatenate([a[r0:max(r0, foot[c] + 1), c] for c in range(a.shape[1])])
            cov = float(seg.mean()) if seg.size else 1.0
            strip = int(max(0, r0 - foot.min()))
            worst_cov, worst_strip = min(worst_cov, cov), max(worst_strip, strip)
            if cov < 0.9 or strip > 4:
                bad.append("%s %s start row %d cover %.2f strip %d" % (look, f, r0, cov, strip))
            if f == "west":
                continue
            ft = np.minimum(foot[:128], foot[128:256]) if len(foot) >= 256 else foot   # the higher toe of the two cells
            for k, p in enumerate(frames_of(INSTALLED if d is None else d, look, f)):
                sh = px(p)
                q = {"east": sh, "north": sh.transpose(1, 0, 2), "south": sh.transpose(1, 0, 2)[::-1]}[f][..., 3]
                hit = np.mean([q[max(0, ft[c] - 6):ft[c] + 7, c].max() >= 60 for c in range(128)])
                if hit < 0.9:
                    bad.append("%s %s %02d toe on the foot in %.2f of columns" % (look, f, k, hit))
                    break
    return not bad, str(bad[:4]) if bad else ("start rows %s; body cover >= %.2f, strip <= %d px; toe on the foot in "
                                               "every frame" % ({k: int(round(128 * (1 - v))) for k, v in starts.items()},
                                                                worst_cov, worst_strip))


def cs_starts(src):
    """{look: FoamStart} from RM_WeirArt.FoamStartDefault / FoamStartByLook."""
    dm = re.search(r"public const float FoamStartDefault = ([0-9.]+)f;", src)
    tbl = re.search(r"FoamStartByLook = new Dictionary<string, float> \{(.*?)\};", src)
    if not dm or not tbl:
        return None
    by = {k: float(v) for k, v in re.findall(r'\{ "(\w+)", ([0-9.]+)f \}', tbl.group(1))}
    return {look: by.get(look, float(dm.group(1))) for look in LOOKS}


# ---- the code --------------------------------------------------------------------------------------------------------
def method(src, sig):
    i = src.find(sig)
    if i < 0:
        return None
    j = src.find("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
    return None


def csharp(src, frames_on_disk):
    pr = method(src, "public override void Print(SectionLayer layer)")
    da = method(src, "protected override void DrawAt(Vector3 drawLoc, bool flip = false)")
    ds = method(src, "private void DrawSpill(Map map, int frame)")
    sp = re.search(r'SpillPath\(string basePath, Rot4 r, int frame\) => basePath \+ "Spill_" \+ FacingName\(r\) \+ "_" \+ '
                   r'frame\.ToString\("00"\)', src)
    ff = re.search(r"private const int FoamFrames = (\d+);", src)
    ww = re.search(r"^FRAMES = (\d+)", WW_SRC.read_text(), re.M)
    out = []
    out.append(("Print draws no spill", pr is not None and "Spill" not in pr))
    out.append(("DrawAt draws the sheet and the white water on one clock", da is not None and da.count("WeirFoamFrame(") == 1
                and "DrawSpill(map, animate ? frame : 0)" in da and "DrawWhiteWater(map, comp, dx, dz, surge, frame)" in da
                and re.search(r"if \(animate\)\s*\{\s*DrawWhiteWater", da) is not None))
    out.append(("DrawSpill draws SpillPath(base, rot, frame) per wet cell", ds is not None
                and "RM_WeirArt.SpillPath(basePath, rot, frame)" in ds and "IsWaterCell" in ds and "Graphics.DrawMesh" in ds))
    out.append(("SpillPath spells <base>Spill_<facing>_NN", sp is not None))
    da2 = method(src, "private void DrawWhiteWater(")
    out.append(("DrawWhiteWater starts the foam plane at FoamStart(look) under the wall", da2 is not None
                and "float start = RM_WeirArt.FoamStart(LookBase);" in da2 and "float reach = start + look.length;" in da2
                and "(0.5f + look.length - reach * 0.5f)" in da2 and "new Vector3(1f, 1f, reach)" in da2))
    st = cs_starts(src)
    out.append(("the offline scene's FOAM_START is the C# table", st is not None and all(
        abs(st[k] - W.FOAM_START.get(k, W.FOAM_START_DEFAULT)) < 1e-6 for k in LOOKS)))
    out.append(("FoamFrames == frames on disk == whitewater_frames.FRAMES", ff is not None and ww is not None
                and int(ff.group(1)) == frames_on_disk == int(ww.group(1))))
    return out


def dll_current():
    lines = SRCHASH.read_text().splitlines()
    want_dll = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("# dll:")), None)
    proj = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("# project:")), "")
    src_dir = (FW.parents[1] / proj).parent if proj else FW / "Source"
    bad, n = [], 0
    for ln in lines:
        if ln.startswith("#") or not ln.strip():
            continue
        h, rel = ln.split(" ", 1)
        p = (src_dir / rel).resolve()
        n += 1
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append(rel)
    got_dll = hashlib.sha256(DLL.read_bytes()).hexdigest()
    ok = not bad and want_dll == got_dll and n > 0
    return ok, ("stale: %s; dll %s" % (bad[:5], "ok" if want_dll == got_dll else "MISMATCH")) if not ok else \
        "%d sources and the DLL's own bytes match its stamp" % n


# ---- run -------------------------------------------------------------------------------------------------------------
def art_checks(d, tag=""):
    """[(name, ok, detail)] for an installed-shaped set."""
    rows = [("no_painted_water",) + no_painted_water(d), ("no_static_sheet",) + no_static_sheet(d),
            ("frames",) + frame_set(d)]
    if not rows[-1][1]:
        return rows
    m_bad, l_bad, f_bad = motion(d)
    rows += [("moves", not m_bad, str(m_bad[:3]) if m_bad else "every step changes, no repeated frame"),
             ("seamless_loop", not l_bad, str(l_bad[:3]) if l_bad else "11 -> 00 within 0.5x..2x the other steps"),
             ("falls_downstream", not f_bad, str(f_bad[:3]) if f_bad else ">= 9/12 steps downstream, every falling facing"),
             ("foam_from_the_foot",) + foam_from_the_foot(d, cs_starts(WEIR_CS.read_text(encoding="utf-8")))]
    return rows


def main():
    for name, ok, det in art_checks(INSTALLED):
        check(name, ok, det)
    ok, det = no_static_sheet(OUT_PHOTO)
    check("no_static_sheet staged (out_photo)", ok, det)
    src = WEIR_CS.read_text(encoding="utf-8")
    for name, ok in csharp(src, N):
        check("csharp: " + name, ok)
    ok, det = dll_current()
    check("dll_current", ok, det)

    with tempfile.TemporaryDirectory() as tmp:
        def copy(tag):
            d = Path(tmp) / tag
            shutil.copytree(INSTALLED, d)
            return d

        def row(rows, name):
            return next((r for r in rows if r[0] == name), (name, False, "not reached"))

        d = copy("painted")
        p = d / "Modern/RM_BankWeir_east.png"
        a = px(p)
        band = slice(int(a.shape[0] * 0.45), int(a.shape[0] * 0.7))
        streak = (np.sin(np.arange(a.shape[1]) * 0.7) * 0.5 + 0.5)[None, :, None]
        a[band, :, :3] = np.array([176, 204, 216]) * (1 - streak) + np.array([238, 246, 250]) * streak
        a[band, :, 3] = 255
        Image.fromarray(a.astype(np.uint8), "RGBA").save(p)
        ok, det = no_painted_water(d)
        check("can-fail no_painted_water (Modern curtain sheet painted back)", not ok, det)

        d = copy("static")
        shutil.copy(d / "Industrial/RM_BankWeirSpill_east_00.png", d / "Industrial/RM_BankWeirSpill_east.png")
        ok, det = no_static_sheet(d)
        check("can-fail no_static_sheet (a static sheet re-added)", not ok, det)

        d = copy("frozen")
        shutil.copy(d / "Scrapper/RM_BankWeirSpill_east_05.png", d / "Scrapper/RM_BankWeirSpill_east_06.png")
        r = row(art_checks(d), "moves")
        check("can-fail moves (Scrapper east 05 copied over 06)", not r[1], r[2])

        d = copy("upstream")
        for f in ("east", "north"):
            src_fr = [Image.open(p).copy() for p in frames_of(INSTALLED, "Modern", f)]
            for k, p in enumerate(frames_of(d, "Modern", f)):
                src_fr[N - 1 - k].save(p)
        r = row(art_checks(d), "falls_downstream")
        check("can-fail falls_downstream (Modern frames played backwards)", not r[1], r[2])

        d = copy("cut")
        p = frames_of(d, "Industrial", "east")[4]
        a = px(p)
        a[60:, :, 3] = 0
        Image.fromarray(a.astype(np.uint8), "RGBA").save(p)
        st = cs_starts(src)
        ok, det = foam_from_the_foot(d, st)
        check("can-fail foam_from_the_foot (Industrial east 04 cut short of its foot)", not ok, det)
        ok, det = foam_from_the_foot(INSTALLED, dict(st, Futuristic=0.5))
        check("can-fail foam_from_the_foot (Futuristic foam from the centre line: shows in the open notches)", not ok, det)
        ok, det = foam_from_the_foot(INSTALLED, dict(st, Modern=0.1))
        check("can-fail foam_from_the_foot (Modern foam from 0.1: a strip of still water under the foot)", not ok, det)

    bad_src = src.replace("Printer_Plane.PrintPlane(layer, center, size, g.MatAt(rot, this), 0f, flip);",
                          "Printer_Plane.PrintPlane(layer, center, size, g.MatAt(rot, this), 0f, flip);\n"
                          "\t\t\tPrinter_Plane.PrintPlane(layer, center, Vector2.one, RM_WeirArt.Mat(LookBase + \"Spill_east\", "
                          "ShaderDatabase.Transparent));", 1)
    r = dict(csharp(bad_src, N))
    check("can-fail csharp (the static Print spill put back)", bad_src != src and not r["Print draws no spill"])

    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
