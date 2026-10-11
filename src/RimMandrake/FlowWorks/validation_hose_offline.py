"""validation_hose_offline.py -- the hose's offline art/source rows, moved from GimmeSomeSlack/validation.py at the hose port
(2026-10-11). Each row is the GSS row's hose half, unchanged in what it measures; the paths are FlowWorks'.

  HO5_hose_art_sane      (was O5's STAGED_HOSE half)   every hose PNG: RGBA, exact canvas, transparency, not magenta; strands tile
  HO6_hose_fittings      (was O6's B8 + B22 halves)    fitting bands match HoseMath.PieceBand; the binding wrap is wider than the
                                                       hose and every fitting; the open end draws the Mouth; the free end defaults Open
  HO7_hose_gpt_read_fixes (was O7's hose shapes)       the Verse-bound GPT source-read fixes (B1-B14) are present in the source
  HO8_no_visible_fire_hose (was O6's B20, hose files)  no player-visible 'fire hose' text in the moved hose files

    python3 src/RimMandrake/FlowWorks/validation_hose_offline.py      # prints the three rows; exit 1 on any FAIL
Each row carries its own can-fail (a planted magenta/seam strip; a planted missing fragment).
"""
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
    ("B4 port cache uses CacheFresh", "Hose/CompHoseReel.cs", "HoseLive.CacheFresh(now, portTick, 60)"),
    ("B1 tick lays hoses on every map", "Hose/RM_MapComponent_Hoses.cs", "% 250 == 0) EnsureLay(r);"),
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


OFFLINE_IDS = ["HO5_hose_art_sane", "HO6_hose_fittings", "HO7_hose_gpt_read_fixes", "HO8_no_visible_fire_hose"]


def run_offline():
    rows = []
    ho5_hose_art(rows)
    ho6_hose_fittings(rows)
    ho7_hose_gpt_read_fixes(rows)
    ho8_no_visible_fire_hose(rows)
    return rows


if __name__ == "__main__":
    sys.exit(0 if all(r["status"] == "PASS" for r in run_offline()) else 1)
