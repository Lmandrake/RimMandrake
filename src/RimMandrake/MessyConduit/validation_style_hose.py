"""validation_style_hose.py -- Messy Conduit per-build style, STAGE 3 (hose reels and hoses): functional script.

Design: design/RimMandrake/messyconduit_style_per_build_design.md (architecture B, section 5 stage 3, section 2.3 "the
hose takes the reel's style"). The reel's look is stored on it in the engine's own style field (CompStyleable,
ThingStyleDefs RM_HoseReel_<Look> in Defs/Hose/RM_HoseReelStyles.xml), picked on the build button by StylePicker (the
reel registers through Hose/HoseStyles.StyledDefs). Graphic_HoseReel swaps each look's stored art for the Reel_Deployed
(empty drum, hose inlet) in the SAME folder while laid; the hose's materials come from HoseMaterials.For(reel).

    python3 validation_style_hose.py --offline                    # R0: style defs, art on disk, comp, no ideo category
    python.exe validation_style_hose.py --live [--save NAME]      # R1-R7: THE one behaviour check of stage 3 (needs colonists)

The ONE live scene (design 5, stage 3): four reels, one per look, placed through the REAL Architect designator
(AerialProbe "place:", the menu's own StylePicker.Pick; Scrapper + Industrial in build mode -> blueprint -> frame ->
building with a real colonist, Modern + Futuristic in god mode); each laid out, saved and loaded while laid out (with
--save), then reeled in; the Industrial reel packed up and reinstalled, then laid again; one legacy reel built by
jawa/build_batch (no designator, no style). Every value is read through HoseProbe "census" (look, rawStyle, style,
reelState, reelTex, hoseTex) and AerialProbe "place"/"reinstall", never from screenshots.

LEARNED (each line is a check below):
  * RimWorld names a loose-PNG texture by its FILE name only, so every look's strand is "Strand_Flat": a check on
    mainTexture.name cannot tell looks apart. The probe reports the PATH each look's material set loaded (hoseTex)
    and the reel's printing path (reelTex), and the rows compare paths.
  * hoseTex is the material set the draw code selects for the reel (HoseMaterials.For(reel), every frame), not a
    read-back of the GPU; whether it LOOKS right is the review map's job (row 3), not this script's.
  * The coil overlay of design section 4 is NOT built: each look swaps its own stored/laid pair (art report section 4),
    so "coil/drum state" is read as reelState stored|deployed plus the path printing.
"""
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
PIECES = ["Strand_Flat", "Strand_Plump", "Binding", "Coupling_Bare", "Nozzle_Bare", "EndCap_Bare", "Mouth"]
TEX = os.path.join(HERE, "Textures")
ROOT = "RimMandrake/MessyConduit/Hose/"
X0, Z0 = 110, 120                                   # scene origin (east of validation_style's mast rows at 60..100,120..140)
SITE = (X0 - 2, Z0 - 2, 34, 24)
REELS = [(X0 + 7 * i, Z0) for i in range(4)]        # one per look, 2x2 each, 7 cells apart
MODE = ["build", "build", "god", "god"]
LAY_TO = [(x + 1, Z0 + 12) for x, _ in REELS]       # straight north, ~11 cells: well inside the default hose length
REINSTALL_AT = (X0 + 3, Z0 + 16)                    # the Industrial reel moves here (reeled in first)
RELAY_TO = (X0 + 14, Z0 + 20)
LEGACY_AT = (X0 + 24, Z0 + 16)                      # built by jawa/build_batch: no designator, no style
LEGACY_LAY = (X0 + 30, Z0 + 20)


def folder(look):
    return ROOT if look == "Scrapper" else ROOT + "Styles/%s/" % look


# ============================================================================ offline
def r0_offline(rows):
    probs, info = [], {}
    root = ET.parse(os.path.join(HERE, "Defs", "Hose", "RM_HoseReelStyles.xml")).getroot()
    styles = {e.findtext("defName"): e for e in root.findall("ThingStyleDef")}
    want = {"RM_HoseReel_%s" % l for l in LOOKS}
    if set(styles) != want:
        probs.append("style defs: missing %s extra %s" % (sorted(want - set(styles)), sorted(set(styles) - want)))
    reel = ET.parse(os.path.join(HERE, "Defs", "Hose", "RM_Hoses.xml")).getroot().find("ThingDef[defName='RM_HoseReel']")
    info["reelDefSeen"] = reel is not None                       # sanity probe: the parser sees the def it must see
    if reel is None:
        probs.append("sanity: RM_HoseReel not found in RM_Hoses.xml")
    else:
        if not any(li.get("Class") == "CompProperties_Styleable" for li in reel.findall("comps/li")):
            probs.append("RM_HoseReel lacks CompProperties_Styleable")
        ds = reel.findtext("graphicData/drawSize")
        for n, e in styles.items():
            if e.findtext("graphicData/drawSize") != ds:
                probs.append("%s: drawSize %s differs from the reel's %s" % (n, e.findtext("graphicData/drawSize"), ds))
    for n, e in styles.items():
        look = n.rsplit("_", 1)[-1]
        tp = e.findtext("graphicData/texPath") or ""
        if tp != folder(look) + "Reel_PumpHookup":
            probs.append("%s: texPath %s is not its look's stored reel" % (n, tp))
        if (e.findtext("graphicData/graphicClass") or "") != "RimMandrake.MessyConduit.Hose.Graphic_HoseReel":
            probs.append("%s: graphicClass is not Graphic_HoseReel (the laid swap would be lost)" % n)
    missing, seen = [], 0
    for l in LOOKS:
        for p in PIECES + ["Reel_PumpHookup", "Reel_Deployed"]:
            f = os.path.join(TEX, folder(l) + p + ".png")
            if os.path.exists(f):
                seen += 1
            else:
                missing.append(folder(l) + p)
    if not os.path.exists(os.path.join(TEX, ROOT + "Strand_Shadow.png")):
        missing.append(ROOT + "Strand_Shadow")
    info["artFilesFound"] = seen
    if missing:
        probs.append("art missing: %s" % missing)
    # the C# path rule must agree with this script's folder() (one source of truth would be nicer; this pins them)
    cs = open(os.path.join(HERE, "Source", "Hose", "HoseStyles.cs"), encoding="utf-8").read()
    if 'Root + "Styles/" + look + "/"' not in cs or 'Root = "RimMandrake/MessyConduit/Hose/"' not in cs:
        probs.append("HoseStyles.Folder no longer matches this script's folder() rule")
    hits, swept = [], 0
    for dp, _, fs in os.walk(os.path.join(V.REPO, "src")):
        if "Defs" not in dp:
            continue
        for f in fs:
            if not f.endswith(".xml"):
                continue
            swept += 1
            try:
                t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if re.search(r"<StyleCategoryDef[\s>]", t) and "RM_HoseReel_" in t:
                hits.append(os.path.relpath(os.path.join(dp, f), V.REPO))
    info["defsXmlSwept"] = swept
    if hits:
        probs.append("a StyleCategoryDef lists the reel styles: %s" % hits)
    V.row(rows, "R0_reel_styles_offline", "FAIL" if probs else "PASS", "MOD", {"problems": probs, **info, "styleDefs": len(styles)})


# ============================================================================ live
def _bridges():
    import validation_aerial as VA
    import validation_hose as VH
    return VA.A(), VH.H()


def _reels(c):
    return {tuple(h["reel"]): h for h in c.get("hoses") or []}


def _find(c, cell):
    """The reel whose 2x2 footprint holds cell (Position of a 2x2 is one of its cells, not necessarily the placed one)."""
    for h in c.get("hoses") or []:
        x0, z0, w, hh = h.get("footprint") or [0, 0, 0, 0]
        if x0 <= cell[0] < x0 + w and z0 <= cell[1] < z0 + hh:
            return h
    return {}


def _art_ok(h, look, laid):
    """Reel printing path + every hose piece path in the look's folder; '' when right, else what is wrong."""
    want_reel = folder(look) + ("Reel_Deployed" if laid else "Reel_PumpHookup")
    errs = []
    if h.get("look") != look:
        errs.append("look %s" % h.get("look"))
    if h.get("reelTex") != want_reel:
        errs.append("reelTex %s" % h.get("reelTex"))
    if h.get("reelState") != ("deployed" if laid else "stored"):
        errs.append("reelState %s" % h.get("reelState"))
    ht = h.get("hoseTex") or {}
    bad = [p for p in PIECES if ht.get(p) != folder(look) + p]
    if bad:
        errs.append("hoseTex wrong for %s" % bad)
    return "; ".join(errs)


def run_live(args):
    A, H = _bridges()
    rows = []
    res = {"mod": V.MOD, "mode": "live", "script": "validation_style_hose.py", "tier": V.TIER, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    if not A.ap("defaults").get("success") or not H.hp("defaults").get("success"):
        V.row(rows, "R_probe_channels", "FAIL", "HARNESS", "aerial or hose probe dead")
        res["aborted"] = "probe dead"
        return res
    A.ap("clearpicks")
    import validation_style as VS
    if not VS.prepare_site(A, SITE, rows, "R_site_ready"):
        res["aborted"] = "site not ready (terrain)"
        return res
    A.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    A.ticks(2)

    # ---------------------------------------------------------------- R1: menu pick -> designator -> blueprint / god building
    placed = [(l, c, m, A.ap("place:RM_HoseReel:%s:%d,%d:%s" % (l, c[0], c[1], m))) for l, c, m in zip(LOOKS, REELS, MODE)]
    bad = [(l, m, r.get("designatorStyle"), (r.get("made") or {}).get("kind"), (r.get("made") or {}).get("rawStyle"), r.get("error"))
           for l, c, m, r in placed if not r.get("success") or r.get("designatorStyle") != "RM_HoseReel_" + l
           or (r.get("made") or {}).get("kind") != ("blueprint" if m == "build" else "building")
           or (r.get("made") or {}).get("rawStyle") != "RM_HoseReel_" + l]
    fb = A.ap("finishbuild")
    A.ticks(3)
    V.row(rows, "R1_pick_reaches_reel", "FAIL" if bad or not fb.get("success") else "PASS", "MOD",
          {"bad": bad, "finishbuild": fb, "meaning": "PASS = each picked look is the designator's style and lands on the blueprint (build) or building (god)"})

    # ---------------------------------------------------------------- R2: built reels store + draw their look, reeled in
    c = H.hp("census")
    bad = []
    for l, cell in zip(LOOKS, REELS):
        h = _find(c, cell)
        e = "no reel" if not h else ("rawStyle %s" % h.get("rawStyle") if h.get("rawStyle") != "RM_HoseReel_" + l else _art_ok(h, l, False))
        if e:
            bad.append((l, cell, e))
    V.row(rows, "R2_built_reels_stored_art", "FAIL" if bad else "PASS", "MOD",
          {"bad": bad, "defaultLook": c.get("defaultLook"), "styleArtMissing": c.get("styleArtMissing"),
           "meaning": "PASS = blueprint -> frame -> building kept each look; each reel prints its look's STORED art and selects its look's hose set"})

    # ---------------------------------------------------------------- R3: lay each out: deployed drum + the reel's hose look
    lays = []
    for l, cell, to in zip(LOOKS, REELS, LAY_TO):
        lays.append((l, H.hp("lay:%d,%d,%d,%d" % (cell[0], cell[1], to[0], to[1]))))
    A.ticks(5)
    c = H.hp("census")
    bad = [(l, r.get("reason")) for l, r in lays if not r.get("success")]
    off_default = 0
    for l, cell in zip(LOOKS, REELS):
        h = _find(c, cell)
        e = "not laid" if not h.get("laid") or not h.get("layOk") else _art_ok(h, l, True)
        if e:
            bad.append((l, e))
        elif l != c.get("defaultLook"):
            off_default += 1
    V.row(rows, "R3_laid_out_per_look", "PASS" if not bad and off_default >= 3 else "FAIL", "MOD",
          {"bad": bad, "reelsNotInDefaultLook": off_default, "defaultLook": c.get("defaultLook"),
           "meaning": "PASS = each laid reel prints its look's EMPTY DRUM and its hose draws that look's pieces, including >= 3 reels whose look is not the global default"})
    res["census_laid"] = c

    # ---------------------------------------------------------------- R4: save / load while laid out
    if args.save:
        _save_load(A, H, rows, args.save, c)
    else:
        V.row(rows, "R4_save_load_laid", "UNMEASURED", "HARNESS", "run with --save NAME to include save/load")

    # ---------------------------------------------------------------- R5: reel each back in: stored art again, look kept
    for cell in REELS:
        H.hp("reelin:%d,%d" % cell)
    A.ticks(5)
    c = H.hp("census")
    bad = []
    for l, cell in zip(LOOKS, REELS):
        h = _find(c, cell)
        e = "still laid" if h.get("laid") else ("rawStyle %s" % h.get("rawStyle") if h.get("rawStyle") != "RM_HoseReel_" + l else _art_ok(h, l, False))
        if e:
            bad.append((l, e))
    V.row(rows, "R5_reeled_in_per_look", "FAIL" if bad else "PASS", "MOD",
          {"bad": bad, "meaning": "PASS = reeling in restores each look's STORED art and keeps the stored style"})

    # ---------------------------------------------------------------- R6: pack up + reinstall keeps the look, then lay again
    ind = _find(c, REELS[1])
    ri = A.ap("reinstall:%s:%d,%d" % (ind.get("id"), REINSTALL_AT[0], REINSTALL_AT[1])) if ind else {"success": False, "error": "no Industrial reel"}
    A.ap("finishbuild")
    A.ticks(3)
    c = H.hp("census")
    moved = _find(c, REINSTALL_AT)
    lay2 = H.hp("lay:%d,%d,%d,%d" % (REINSTALL_AT[0], REINSTALL_AT[1], RELAY_TO[0], RELAY_TO[1])) if moved else {}
    A.ticks(5)
    c = H.hp("census")
    moved = _find(c, REINSTALL_AT)
    e = _art_ok(moved, "Industrial", True) if moved.get("laid") else "not laid after reinstall: %s" % lay2.get("reason")
    ok = (ri.get("success") and ri.get("minifiedStyle") == "RM_HoseReel_Industrial" and moved.get("id") == ind.get("id")
          and moved.get("rawStyle") == "RM_HoseReel_Industrial" and not e)
    V.row(rows, "R6_reinstall_keeps_look", "PASS" if ok else "FAIL", "MOD",
          {"reinstall": ri, "after": {k: moved.get(k) for k in ("id", "rawStyle", "look", "reelTex", "laid")}, "art": e})

    # ---------------------------------------------------------------- R7: legacy reel (no style stored) draws the default look
    bb = A.call("jawa/build_batch", ops="RM_HoseReel:%d,%d" % LEGACY_AT, faction="player", wipeExisting=False)
    A.ticks(3)
    H.hp("lay:%d,%d,%d,%d" % (LEGACY_AT[0], LEGACY_AT[1], LEGACY_LAY[0], LEGACY_LAY[1]))
    A.ticks(5)
    c = H.hp("census")
    lg = _find(c, LEGACY_AT)
    dl = c.get("defaultLook")
    e = _art_ok(lg, dl, bool(lg.get("laid"))) if lg else "no legacy reel"
    V.row(rows, "R7_legacy_reel_default_look", "PASS" if lg and lg.get("rawStyle") is None and lg.get("style") == "RM_HoseReel_%s" % dl and not e else "FAIL", "MOD",
          {"build": bb.get("success"), "legacy": {k: lg.get(k) for k in ("rawStyle", "style", "look", "reelTex", "laid")}, "defaultLook": dl, "art": e,
           "meaning": "PASS = an unstyled reel stores NO style (an older save is unchanged) yet draws, and lays its hose in, the default look"})
    res["census_end"] = c
    return res


def _snapshot(c):
    return sorted((tuple(h["reel"]), h.get("rawStyle"), h.get("look"), h.get("laid"), h.get("reelState"), h.get("reelTex"),
                   tuple(sorted((h.get("hoseTex") or {}).items())), h.get("geometryHash")) for h in c.get("hoses") or [])


def _save_load(A, H, rows, name, before_c):
    before = V._saves_stat()
    if name + ".rws" in before:
        V.row(rows, "R4_save_load_laid", "FAIL", "HARNESS", "%s.rws exists" % name)
        return
    A.call("rimworld/save_game", saveName=name)
    time.sleep(3.0)
    after = V._saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    if new != [name + ".rws"] or changed:
        V.row(rows, "R4_save_load_laid", "FAIL", "HARNESS", {"new": new, "changed": changed})
        return
    with open(os.path.join(V.SAVES, name + ".rws"), "rb") as f:
        blob = f.read()
    saved_styles = {l: blob.count(("RM_HoseReel_%s" % l).encode()) for l in LOOKS}
    A.call("rimworld/load_game", saveName=name)
    ok, waited = V._wait_playing(A)
    if not ok:
        V.row(rows, "R4_save_load_laid", "FAIL", "SITE", {"state": waited})
        return
    A.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    c, t0 = {}, time.time()
    while time.time() - t0 < 12.0:          # comps register a little after load
        A.ticks(10)
        time.sleep(1.0)
        c = H.hp("census")
        if len(c.get("hoses") or []) >= len(before_c.get("hoses") or []):
            break
    a, b = _snapshot(before_c), _snapshot(c)
    V.row(rows, "R4_save_load_laid", "PASS" if a == b and len(a) >= 4 and all(v >= 1 for v in saved_styles.values()) else "FAIL", "MOD",
          {"reels": len(a), "styleNamesInSave": saved_styles, "differs": [x for x in a if x not in b][:4], "loadSeconds": waited,
           "meaning": "PASS = after save/load every laid reel keeps its stored style, deployed drum, hose look and hose geometry"})


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--save", default=None, metavar="NAME", help="also save and reload as NAME (a NEW save file) while laid out")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.offline:
        rows = []
        r0_offline(rows)
        return 0 if all(r["status"] == "PASS" for r in rows) else 1
    if not a.live:
        ap.print_help()
        return 2
    res = run_live(a)
    os.makedirs(os.path.join(HERE, "northstar"), exist_ok=True)
    out = a.out or os.path.join(HERE, "northstar", "validation_style_hose_%s_%s.json" % (res["mode"], time.strftime("%Y%m%dT%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    t = {}
    for r in res["rows"]:
        t[r["status"]] = t.get(r["status"], 0) + 1
    print("style-hose %s: %s -> %s" % (res["mode"], t, out))
    return 0 if not res.get("aborted") and not t.get("FAIL") else 1


if __name__ == "__main__":
    sys.exit(main())
