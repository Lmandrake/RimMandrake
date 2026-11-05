"""validation_hose_offline.py -- the hose's offline art/source rows, moved from GimmeSomeSlack/validation.py at the hose port
(2026-10-11). Each row is the GSS row's hose half, unchanged in what it measures; the paths are FlowWorks'.

  HO5_hose_art_sane      (was O5's STAGED_HOSE half)   every hose PNG: RGBA, exact canvas, transparency, not magenta; strands tile
  HO6_hose_fittings      (was O6's B8 + B22 halves)    fitting bands match HoseMath.PieceBand; the binding wrap is wider than the
                                                       hose and every fitting; the open end draws the Mouth; the free end defaults Open
  HO7_hose_gpt_read_fixes (was O7's hose shapes)       the Verse-bound GPT source-read fixes (B1-B14) are present in the source
  HO8_no_visible_fire_hose (was O6's B20, hose files)  no player-visible 'fire hose' text in the moved hose files
  HO9_drawn_fittings_meet_ports (2026-10-22)         the *_Bare pieces the draw code really uses, every look: coupling face at
                                                       JoinerFace, bands at PieceBand / CouplingMax / NozzleMax / EndCapMax
  HO10_reel_feed_off_pipe_is_pipe (2026-11-05)       HOSE_NET_DIAGNOSE_HALF_HOSE_HALF_PIPE: a reel's link off a PIPE draws in the
                                                       pipe's own straight tile, never hose cloth (C7 "one hose net, no pump" read
                                                       hose / pipe / hose); the C7 under-reel strip stays on the pipe cell + reel

    python3 src/RimMandrake/FlowWorks/validation_hose_offline.py      # prints the three rows; exit 1 on any FAIL
Each row carries its own can-fail (a planted magenta/seam strip; a planted missing fragment).
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks")
SRC = os.path.join(HERE, "Source")

STAGED_HOSE = ["Hose/" + n for n in ("Strand_Flat", "Strand_Plump", "Strand_Shadow", "Coupling_Brass", "Nozzle", "Reel_PumpHookup",
                                     "EndCap", "Binding", "Mouth", "Coupling_Bare", "EndCap_Bare", "Nozzle_Bare")]


def row(rows, rid, status, cls, detail):
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-28s %-9s %s" % (rid, status, str(detail)[:150]), flush=True)


def _canvas_for(rel):
    n = rel.split("/")[-1]
    if rel.startswith("Hose/Strand"):
        return (256, 64)
    if rel == "Hose/Binding":
        return (82, 40)            # the cloth wrap cropped from the accepted render (make_hose_binding.py, B22)
    if rel == "Hose/Mouth":
        return (64, 64)
    if rel == "Hose/Reel_PumpHookup":
        return (256, 256)          # the 2x2 reel's drum art is 256
    if n.startswith("Strand"):
        return (128, 32)
    return (128, 128)


def png_sanity(rel, root=TEX):
    """None if the PNG is sane, else why: RGBA, exact canvas, real transparency, not empty, not magenta; a strip must tile."""
    from PIL import Image
    import numpy as np
    p = os.path.join(root, rel + ".png")
    if not os.path.exists(p):
        return "missing"
    im = Image.open(p)
    if im.mode != "RGBA":
        return "mode %s" % im.mode
    want = _canvas_for(rel)
    if im.size != want:
        return "size %s != %s" % (im.size, want)
    a = np.asarray(im).astype(np.float32)
    al = a[:, :, 3]
    if (al > 8).mean() < 0.01:
        return "empty"
    if (al < 8).mean() < 0.02 and not rel.split("/")[-1].startswith("Strand"):
        return "no transparency"
    vis = a[al > 128][:, :3]
    if len(vis) and ((vis[:, 0] > 200) & (vis[:, 1] < 60) & (vis[:, 2] > 200)).mean() > 0.2:
        return "magenta"
    if rel.split("/")[-1].startswith("Strand"):
        return strand_seam(p)
    return None


def strand_band(path, need=54):
    """D1 (joints study 2026-10-22): a plump strand must fill its strip, centred (HoseMath.PlumpBand = 62/64 sizes the
    ribbon as if it did). None when >= need rows are half-opaque across the strip within 2 rows of centre, else why."""
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(path).convert("RGBA"))
    rows = np.where((a[:, :, 3] > 128).mean(1) > 0.5)[0]
    if not len(rows):
        return "band empty"
    r0, r1, h = int(rows.min()), int(rows.max()), a.shape[0]
    if r1 - r0 + 1 < need or abs((r0 + r1) / 2.0 - (h - 1) / 2.0) > 2:
        return "band rows %d-%d of %d (needs >= %d, centred): draws thinner than HoseMath.PlumpBand" % (r0, r1, h, need)
    return None


def strand_seam(path):
    """None when a strip tiles (its column 0 continues its last column), else 'seam E vs adjacent A' (premultiplied)."""
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    pm = np.concatenate([a[:, :, :3] * (a[:, :, 3:4] / 255.0), a[:, :, 3:4]], axis=2)
    edge = float(np.abs(pm[:, 0] - pm[:, -1]).mean())
    adj = float(np.abs(np.diff(pm, axis=1)).mean())
    if edge > max(1.5 * adj, adj + 4.0):
        return "seam %.1f vs adjacent %.1f" % (edge, adj)
    return None


def ho5_hose_art(rows):
    import tempfile
    import shutil
    from PIL import Image
    import numpy as np
    probs = ["%s: %s" % (rel, why) for rel in STAGED_HOSE for why in [png_sanity(rel)] if why]
    # 2026-10-22 night fixer: the per-look strands (Hose/Styles/<Look>/Strand_*) tile too; Modern/Strand_Plump had an 8-column
    # empty tail (a gap every tile) that this gate never read. Their canvas is the look's own, so only the seam is judged here.
    sdir = os.path.join(TEX, "Hose", "Styles")
    for look in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        for f in sorted(os.listdir(os.path.join(sdir, look))):
            if f.startswith("Strand") and f.endswith(".png"):
                why = strand_seam(os.path.join(sdir, look, f)) or (strand_band(os.path.join(sdir, look, f)) if "Plump" in f else None)
                if why:
                    probs.append("Hose/Styles/%s/%s: %s" % (look, f[:-4], why))
    why = strand_band(os.path.join(TEX, "Hose", "Strand_Plump.png"))
    if why:
        probs.append("Hose/Strand_Plump: " + why)
    plant = np.zeros((64, 256, 4), np.uint8)
    plant[8:56, :, :] = (255, 0, 255, 255)
    seam = np.zeros((64, 256, 4), np.uint8)
    seam[8:56, :128] = (20, 20, 20, 255)
    seam[8:56, 128:] = (220, 220, 220, 255)
    tdir = tempfile.mkdtemp(prefix="ho5probe_")
    try:
        os.makedirs(os.path.join(tdir, "Hose"))
        Image.fromarray(plant).save(os.path.join(tdir, "Hose", "Strand_magenta.png"))
        Image.fromarray(seam).save(os.path.join(tdir, "Hose", "Strand_seam.png"))
        can_fail = png_sanity("Hose/Strand_magenta", tdir) == "magenta" and (png_sanity("Hose/Strand_seam", tdir) or "").startswith("seam")
    finally:
        shutil.rmtree(tdir, ignore_errors=True)
    row(rows, "HO5_hose_art_sane", "PASS" if not probs and can_fail else "FAIL", "MOD",
        probs or "%d hose PNGs sane; planted magenta+seam refused=%s" % (len(STAGED_HOSE), can_fail))


def _band_px(path, xs=(10, 20)):
    from PIL import Image
    a = Image.open(path).convert("RGBA").getchannel("A")
    return max(sum(1 for y in range(a.size[1]) if a.getpixel((x, y)) > 128) for x in xs)


def ho6_hose_fittings(rows):
    from PIL import Image
    probs, info = [], []
    hs = "".join(open(os.path.join(SRC, "Hose", f), encoding="utf-8").read() for f in ("HoseMath.cs", "RM_MapComponent_Hoses.cs"))
    pb = float(re.search(r"PieceBand = ([0-9.]+)f?[,;]", hs).group(1))
    for n in ("Coupling_Brass", "EndCap"):
        px = _band_px(os.path.join(TEX, "Hose", n + ".png"))
        info.append("%s band %d px (code %.0f)" % (n, px, pb * 128))
        if abs(px - pb * 128) > 2:
            probs.append("B8 %s: hose band %d px, code sizes it as %.0f px" % (n, px, pb * 128))
    hm = open(os.path.join(SRC, "Hose", "HoseMath.cs"), encoding="utf-8").read()
    wk = float(re.search(r"WrapK = ([0-9.]+)", hm).group(1))
    fv, pe = [float(x) for x in re.search(r"FlatVisible = ([0-9.]+), PlumpExtra = ([0-9.]+)", hm).groups()]
    bind_code = float(re.search(r"BindBand = ([0-9.]+)f", hs).group(1))
    bim = Image.open(os.path.join(TEX, "Hose", "Binding.png")).convert("RGBA")
    ba = bim.getchannel("A")
    bind_px = max(sum(1 for y in range(bim.size[1]) if ba.getpixel((x, y)) > 128) for x in range(bim.size[0]))
    bind_frac = bind_px / float(bim.size[1])
    maxes = {n: float(re.search(r"\b%s = ([0-9.]+)f?[,;]" % c, hs).group(1))
             for n, c in (("Coupling_Brass", "CouplingMax"), ("Nozzle", "NozzleMax"), ("EndCap", "EndCapMax"))}
    worst = []
    for vis in (fv, fv + pe):
        wrap_drawn = wk * vis / bind_code * bind_frac
        if wrap_drawn < 1.3 * vis - 1e-6:
            probs.append("B22 wrap %.3f < 1.3 x hose %.3f" % (wrap_drawn, vis))
        for n, mx in maxes.items():
            im = Image.open(os.path.join(TEX, "Hose", n + ".png")).convert("RGBA").getchannel("A")
            mpx = max(sum(1 for y in range(128) if im.getpixel((x, y)) > 128) for x in range(128)) / 128.0
            if abs(mpx - mx) > 2 / 128.0:
                probs.append("B22 %s widest band %.3f, code says %.3f" % (n, mpx, mx))
            size = min(vis / pb, 0.95 * wk * vis / mx)
            fit_w = size * mpx
            worst.append(fit_w / wrap_drawn)
            if fit_w > wrap_drawn + 1e-6:
                probs.append("B22 %s on hose %.2f: fitting %.3f wider than wrap %.3f" % (n, vis, fit_w, wrap_drawn))
    if os.path.exists(os.path.join(TEX, "Hose", "OpenEnd.png")) or not ("HoseMaterials.Mouth" in hs or "PieceXZ(hm.Mouth" in hs) or "Wrap(" not in hs:
        probs.append("B22: open end still the OpenEnd stub, or no wrap drawn")
    info.append("B22 wrap band %d/%d px, wrap %.2f x hose, fitting/wrap max %.2f" % (bind_px, bim.size[1], wk * bind_frac / bind_code, max(worst)))
    if "public HoseEnd end = HoseEnd.Open;" not in open(os.path.join(SRC, "Hose", "CompHoseReel.cs"), encoding="utf-8").read():
        probs.append("B8: the free end does not default to Open")
    row(rows, "HO6_hose_fittings", "PASS" if not probs else "FAIL", "MOD", probs or "; ".join(info))


GPT_READ_FIX_SHAPES = [
    ("B4 port cache uses CacheFresh (phased: HoseLive.PhasedFresh is CacheFresh plus a per-reel phase, HOSELINKS_REFRESH_DIAGNOSE_MAP0_TICK_SPIKE)", "Hose/CompHoseReel.cs", "HoseLive.PhasedFresh(now, portTick, 60, parent.thingIDNumber)"),
    ("B1 tick lays hoses on every map", "Hose/RM_MapComponent_Hoses.cs", "% 250 == 0) TickRecheck(r, now);"),
    ("B5 no no-outlet fallback lay", "Hose/RM_MapComponent_Hoses.cs", "HoseMath.LeadOutBlocked"),
    ("B2 order need judged on shortest route", "Hose/CompHoseReel.cs", "new Cell(target.x, target.z), -1, false)"),
    ("B8 hose length in the shape fingerprint", "Hose/RM_HoseSettings.cs", '"|L" + maxLength'),
    ("B10 order loop check sees pending orders", "Hose/CompHoseReel.cs", "comp.Loops(this, relay, true)"),
    ("B11 resume rule for every dropped order", "Hose/Jobs/WorkGiver_HoseOrders.cs", "HoseOrderRules.MayResume("),
    ("B12 refused right-click restores the order", "Hose/Jobs/FloatMenuOptionProvider_Hose.cs", "r.pending = prevOrder;"),
    ("B13 pre-grab path failure clears the order", "Hose/Jobs/JobDriver_CarryHoseEnd.cs", "HoseOrderRules.KeepOrderAfterJob("),
    ("B14 port candidates in thing-id order", "Hose/HosePorts.cs", "ById(things, cands);"),
    ("B7 hose corridor hash has route cost", "Hose/RM_MapComponent_Hoses.cs", "CordSig.CellSig(w, c)"),
]


def gpt_read_fix_missing(shapes, src_dir=SRC):
    miss = []
    for name, rel, frag in shapes:
        path = os.path.join(src_dir, rel)
        body = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if frag not in body:
            miss.append(name)
    return miss


def ho7_hose_gpt_read_fixes(rows):
    miss = gpt_read_fix_missing(GPT_READ_FIX_SHAPES)
    if gpt_read_fix_missing([("planted", "Hose/HoseMath.cs", "this fragment is not in the source 7f3a")]) != ["planted"]:
        miss.append("probe: the shape check cannot see a missing fragment")
    row(rows, "HO7_hose_gpt_read_fixes", "PASS" if not miss else "FAIL", "MOD",
        miss or "%d fix shapes present; planted probe reported missing" % len(GPT_READ_FIX_SHAPES))


OWNER_WORDS = ("fire hoses they use", "firehose is shown as going OVER")   # the owner's words, quoted verbatim


def visible_fire_hose(paths):
    """Case-insensitive 'fire hose' / 'firehose' / 'fire-hose' hits in visible text (B20), identifiers excepted."""
    rx = re.compile(r"fire[\s_-]?hoses?", re.I)
    hits = []
    for p in paths:
        try:
            lines = open(p, encoding="utf-8").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, ln in enumerate(lines, 1):
            if any(q in ln for q in OWNER_WORDS):
                continue
            for m in rx.finditer(ln):
                pre, post = ln[m.start() - 1:m.start()], ln[m.end():m.end() + 1]
                if "_" in m.group(0) or (pre and (pre.isalnum() or pre == "_")) or (post and (post.isalnum() or post == "_")):
                    continue
                hits.append((os.path.relpath(p, HERE), i, ln.strip()[:120]))
    return hits


def ho8_no_visible_fire_hose(rows):
    import glob
    import tempfile
    paths = (glob.glob(os.path.join(SRC, "Hose", "**", "*.cs"), recursive=True) + glob.glob(os.path.join(HERE, "Defs", "Hose", "*.xml")) +
             [os.path.join(HERE, f) for f in ("validation_hose.py", "validation_style_hose.py")])
    hits = visible_fire_hose(paths)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("a Fire Hose here\nand fire_hose_id there\n")
    probe = visible_fire_hose([f.name])
    os.unlink(f.name)
    probs = (["visible 'fire hose' text: %s" % hits[:4]] if hits else []) + (["sweep cannot see a planted 'Fire Hose'"] if len(probe) != 1 else [])
    row(rows, "HO8_no_visible_fire_hose", "PASS" if not probs else "FAIL", "MOD", probs or "%d hose files swept, planted hit seen" % len(paths))


# ---------------------------------------------------------------- HO9 (HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES, 2026-10-22)
# The pieces DrawEnds/DrawFeed actually draw are the *_Bare ones (since 8ac23ee0f4, 2026-10-04), per look. HO6 measures
# Coupling_Brass/EndCap, which nothing draws, so when 2e22f30e3c (2026-10-17) installed small centred "gauge" couplings
# (opaque x 50-85 of 128 instead of 58-122) every coupling face landed 0.2-0.4 fitting-size short of its nozzle or port and
# HO6 stayed green. HO9 pins every drawn piece of every look to the constants the draw code places it with.
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
FACE_TOL, BAND_TOL_PX = 0.025, 5


def _look_png(tex, look, name):
    return os.path.join(tex, "Hose", name + ".png") if look == "Scrapper" else os.path.join(tex, "Hose", "Styles", look, name + ".png")


def piece_geometry(path):
    """(face, widest, entry) of a fitting PNG: face = rightmost opaque column as canvas units from the centre (the end that
    meets the nozzle/port), widest = tallest opaque column (px), entry = opaque px 3 columns in from the hose end."""
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    w, h = im.size
    cols = [sum(1 for y in range(h) if a.getpixel((x, y)) > 128) for x in range(w)]
    xs = [x for x in range(w) if cols[x]]
    if not xs:
        return None
    return ((xs[-1] + 1) / float(w) - 0.5, max(cols) * 128.0 / h, cols[min(w - 1, xs[0] + 3)] * 128.0 / h)


def drawn_fitting_problems(tex=TEX, src=SRC):
    hs = "".join(open(os.path.join(src, "Hose", f), encoding="utf-8").read() for f in ("HoseMath.cs", "RM_MapComponent_Hoses.cs"))
    face = float(re.search(r"JoinerFace = ([0-9.]+)", hs).group(1))
    pb = float(re.search(r"PieceBand = ([0-9.]+)f?[,;]", hs).group(1))
    maxes = {n: float(re.search(r"\b%s = ([0-9.]+)f?[,;]" % c, hs).group(1)) * 128
             for n, c in (("Coupling_Bare", "CouplingMax"), ("Nozzle_Bare", "NozzleMax"), ("EndCap_Bare", "EndCapMax"))}
    probs, seen = [], 0
    for look in LOOKS:
        for n, mx in maxes.items():
            g = piece_geometry(_look_png(tex, look, n))
            if g is None:
                probs.append("%s %s: empty or missing" % (look, n))
                continue
            seen += 1
            f, widest, entry = g
            if abs(widest - mx) > BAND_TOL_PX:
                probs.append("%s %s widest band %.0f px, the code sizes it as %.0f px" % (look, n, widest, mx))
            if n == "Coupling_Bare":
                # the coupling's face is what meets the reel nozzle / port / the other joiner half
                if abs(f - face) > FACE_TOL:
                    probs.append("%s Coupling_Bare face at %.3f canvas, the code puts the face at %.3f: drawn %.2f fitting-size short"
                                 % (look, f, face, face - f))
                if entry < pb * 128 * 0.75 or entry > pb * 128 * 1.5:
                    probs.append("%s Coupling_Bare hose entry %.0f px, the code sizes the hose band as %.0f px" % (look, entry, pb * 128))
    return probs, seen


def ho9_drawn_fittings(rows):
    import shutil
    import tempfile
    probs, seen = drawn_fitting_problems()
    # can-fail: the 2026-10-17 gauge coupling (small, centred) planted in a scratch texture tree must be refused
    tmp = tempfile.mkdtemp(prefix="ho9_")
    planted = False
    try:
        shutil.copytree(os.path.join(TEX, "Hose"), os.path.join(tmp, "Hose"))
        from PIL import Image
        im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        for x in range(50, 86):
            for y in range(60, 70):
                im.putpixel((x, y), (180, 120, 60, 255))
        im.save(os.path.join(tmp, "Hose", "Coupling_Bare.png"))
        pp, _ = drawn_fitting_problems(tex=tmp)
        planted = any("Scrapper Coupling_Bare face" in p for p in pp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not planted:
        probs.append("HARNESS: a planted short gauge coupling was not refused")
    row(rows, "HO9_drawn_fittings_meet_ports", "PASS" if not probs and seen == 12 else "FAIL", "MOD",
        probs or "%d drawn pieces (4 looks x coupling/nozzle/cap) match JoinerFace/PieceBand/*Max; planted gauge coupling refused" % seen)


# HOSE_NET_DIAGNOSE_HALF_HOSE_HALF_PIPE (owner's walk 2026-10-22, C7 station "one hose net, no pump": "half hose half pipe";
# Steam shot 20261022184620_1.jpg). RM_MapComponent_Hoses.DrawFeed laid hose CLOTH from the pipe cell's centre in under the
# reel for every port kind, so a pipe joining two reels read hose+coupling / pipe / hose. A reel is not a pipe partner, so the
# pipe draws no stub of its own: the feed must BE the pipe there. The C# twin (SelfTest HoseJointChecks.PipeFeeds) sweeps every
# look x facing x side; this row is the dotnet-free half: the draw's branch, read from the source, and the C7 strip.
BORE_HALF = 0.12   # LiquidJoinRule.BoreHalf, read below from the source


def _method_body(text, signature):
    """The text of one C# method from its signature to its closing brace at the same indent (8 spaces)."""
    i = text.find(signature)
    if i < 0:
        return ""
    j = text.find("\n        }\n", i)
    return text[i:j if j > 0 else len(text)]


def feed_branch_problems(draw_src, relay_src):
    probs = []
    body = _method_body(draw_src, "private void DrawFeed(CompHoseReel r, float y)")
    if not body:
        return ["DrawFeed not found in RM_MapComponent_Hoses.cs"]
    if not re.search(r"bool pipe = HoseJoints\.FeedIsPipe\(r\.portKind\);", body):
        probs.append("DrawFeed does not ask HoseJoints.FeedIsPipe(r.portKind)")
    if not re.search(r"Material m = pipe \? [^;]*StraightMat\(r\.Port\(\), true\) : hm\.Flat\(1f\);", body):
        probs.append("DrawFeed does not pick the pipe's straight tile for a pipe (cloth hm.Flat only in the non-pipe arm)")
    if len(re.findall(r"hm\.Flat\(", body)) != 1:
        probs.append("hose cloth (hm.Flat) is reachable outside the non-pipe arm")
    if not re.search(r"mesh = pipe \? PipeStrip\(path, fy\) : Ribbon\(", body):
        probs.append("DrawFeed does not build the pipe strip (PipeStrip) for a pipe")
    if not re.search(r"if \(pipe\) Graphics\.DrawMesh\(feed,", body):
        probs.append("the pipe strip is not drawn on its own (the hose depth pre-pass would print the atlas's wrong slice)")
    if not re.search(r"internal static bool FeedIsPipe\(HosePortKind kind\) => kind == HosePortKind\.Pipe;", relay_src):
        probs.append("HoseJoints.FeedIsPipe is not exactly 'a Pipe port'")
    return probs


def centre_stub(cx, cz, dx, dz, bx, bz, bw, bh):
    """LiquidJoinRule.CentreStub, ported: from the shared edge's midpoint in front of the end to the footprint's centre."""
    nx, nz = cx + dx, cz + dz
    if not (bx <= nx < bx + bw and bz <= nz < bz + bh):
        return None
    ex, ez = cx + 0.5 + dx * 0.5, cz + 0.5 + dz * 0.5
    mx, mz = bx + bw / 2.0, bz + bh / 2.0
    kx, kz = (mx if dx != 0 else ex), (mz if dz != 0 else ez)
    bend = abs(kx - mx) > 1e-9 or abs(kz - mz) > 1e-9
    return [(ex, ez), (kx, kz), (mx, mz)] if bend else [(ex, ez), (mx, mz)]


def strip_quads(path, half):
    """LiquidJoinRule.StripQuads for straight segments: one quad per stretch between whole-tile cuts, its corners and U span."""
    quads, s = [], 0.0
    for (ax, az), (bx, bz) in zip(path, path[1:]):
        ln = math.hypot(bx - ax, bz - az)
        if ln < 1e-9:
            continue
        tx, tz = (bx - ax) / ln, (bz - az) / ln
        fs = [0.0, 1.0]
        w = math.floor(s) + 1
        while w < s + ln - 1e-9:
            fs.append((w - s) / ln)
            w += 1
        fs.sort()
        for fa, fb in zip(fs, fs[1:]):
            if fb - fa < 1e-9:
                continue
            pa = (ax + (bx - ax) * fa, az + (bz - az) * fa)
            pb = (ax + (bx - ax) * fb, az + (bz - az) * fb)
            corners = [(pa[0] + tz * half, pa[1] - tx * half), (pa[0] - tz * half, pa[1] + tx * half),
                       (pb[0] - tz * half, pb[1] + tx * half), (pb[0] + tz * half, pb[1] - tx * half)]
            quads.append((corners, (fb - fa) * ln))
        s += ln
    return quads


def c7_strip_problems(feed=None):
    """The C7 bathhouse pair (northstar/scenarios/c07_bathhouse_tower.py): reels placed at (11,22) and (11,15) facing west
    (2x2 at x10-11), joined by RM_UniversalPipe on x=11. Each reel's link off its pipe neighbour, as the pipe strip draws it.
    feed: the link polyline builder (contact cell, side, rect) -> points; the default is DrawFeed's under-reel path."""
    probs, seen = [], 0
    reels = [((10, 22, 2, 2), (11, 21), (0, -1)), ((10, 15, 2, 2), (11, 17), (0, 1))]
    for rect, (cx, cz), (sx, sz) in reels:
        bx, bz, bw, bh = rect
        if feed is None:
            stub = centre_stub(cx, cz, -sx, -sz, bx, bz, bw, bh)
            path = [(cx + 0.5, cz + 0.5)] + (stub or [])
        else:
            path = feed((cx, cz), (sx, sz), rect)
        quads = strip_quads(path, BORE_HALF)
        ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
        if not quads:
            probs.append("reel %s: no strip" % (rect,))
            continue
        seen += 1
        if abs(sum(q[1] for q in quads) - ln) > 1e-6 or ln < 1.0:
            probs.append("reel %s: strip %.3f long, link %.3f (must run from the pipe's centre to the reel's)" % (rect, sum(q[1] for q in quads), ln))
        c0 = quads[0][0]
        mid = ((c0[0][0] + c0[1][0]) / 2, (c0[0][1] + c0[1][1]) / 2)
        if math.hypot(mid[0] - cx - 0.5, mid[1] - cz - 0.5) > 0.05:
            probs.append("reel %s: strip starts off the pipe's centre (%.2f, %.2f)" % (rect, mid[0], mid[1]))
        e = BORE_HALF + 1e-6
        for corners, _ in quads:
            for (x, z) in corners:
                in_reel = bx - e <= x <= bx + bw + e and bz - e <= z <= bz + bh + e
                in_pipe = cx - e <= x <= cx + 1 + e and cz - e <= z <= cz + 1 + e
                if not (in_reel or in_pipe):
                    probs.append("reel %s: strip corner (%.2f, %.2f) outside the pipe cell and the reel" % (rect, x, z))
    return probs, seen


def ho10_reel_feed_off_pipe(rows):
    draw = open(os.path.join(SRC, "Hose", "RM_MapComponent_Hoses.cs"), encoding="utf-8").read()
    relay = open(os.path.join(SRC, "Hose", "HoseRelay.cs"), encoding="utf-8").read()
    rule = open(os.path.join(SRC, "Machinery", "LiquidJoinRule.cs"), encoding="utf-8").read()
    probs = feed_branch_problems(draw, relay)
    m = re.search(r"public const double BoreHalf = ([0-9.]+);", rule)
    if not m or abs(float(m.group(1)) - BORE_HALF) > 1e-12:
        probs.append("LiquidJoinRule.BoreHalf is not %.2f (port out of date)" % BORE_HALF)
    gp, seen = c7_strip_problems()
    probs += gp
    # can-fails: the pre-fix DrawFeed (cloth for every port) and a strip cut to the old quarter-cell stub are both refused
    pre = re.sub(r"bool pipe = HoseJoints\.FeedIsPipe\(r\.portKind\);", "", draw)
    pre = re.sub(r"Material m = pipe \? [^;]*;", "Material m = hm.Flat(1f);", pre)
    if not feed_branch_problems(pre, relay):
        probs.append("HARNESS: the planted pre-fix DrawFeed (hose cloth for a pipe) was not refused")
    short, _ = c7_strip_problems(lambda c, s, r: [(c[0] + 0.5, c[1] + 0.5), (c[0] + 0.5, c[1] + 0.5 - s[1] * 0.25)])
    if not short:
        probs.append("HARNESS: a quarter-cell stub (the old cloth stub's reach) was not refused")
    row(rows, "HO10_reel_feed_off_pipe_is_pipe", "PASS" if not probs and seen == 2 else "FAIL", "MOD",
        probs or "DrawFeed draws a pipe port's link in the pipe's straight tile (cloth only off tanks/pumps/machines); "
                 "C7 pair: %d strips pipe-centre to reel-centre inside pipe cell + reel; planted pre-fix draw and short stub refused" % seen)


OFFLINE_IDS = ["HO5_hose_art_sane", "HO6_hose_fittings", "HO7_hose_gpt_read_fixes", "HO8_no_visible_fire_hose",
               "HO9_drawn_fittings_meet_ports", "HO10_reel_feed_off_pipe_is_pipe"]


def run_offline():
    rows = []
    ho5_hose_art(rows)
    ho6_hose_fittings(rows)
    ho7_hose_gpt_read_fixes(rows)
    ho8_no_visible_fire_hose(rows)
    ho9_drawn_fittings(rows)
    ho10_reel_feed_off_pipe(rows)
    return rows


if __name__ == "__main__":
    sys.exit(0 if all(r["status"] == "PASS" for r in run_offline()) else 1)
