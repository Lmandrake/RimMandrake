"""validation_style.py -- Messy Conduit per-build style, STAGE 1 (poles alone): functional script beside validation_aerial.py.

Design: design/RimMandrake/messyconduit_style_per_build_design.md (architecture B, section 5 stage 1, owner decisions
2026-10-04). The look is stored on each building in the engine's own style field (CompStyleable, ThingStyleDefs in
Defs/Aerial/RM_AerialStyles.xml); StylePicker.cs adds the build-button menu, the designator style getter, the copy
carry-over, the legacy read (unstyled -> default look, never written) and a Frame guard.

    python3 validation_style.py --offline                    # S0: style defs, art on disk, no ideo category lists them
    python.exe validation_style.py --live [--save NAME]      # S1-S8: THE one behaviour check of stage 1 (needs colonists)

The ONE live scene (design 5, stage 1): the four mast looks placed through the REAL Architect designator twice -- build
mode (blueprint -> frame -> building, completed by the engine's own Blueprint.TryReplaceWithSolidThing and
Frame.CompleteConstruction with a real colonist) and god mode -- plus a Copy of one mast, a pack-up + reinstall of one,
one legacy (unstyled) mast; then save/load (with --save). Each mast's stored StyleDef, the graphic it draws and every
span's look/texture/width are read through AerialProbe "styles", never from screenshots. The look is picked by
StylePicker.Pick -- the same call the menu option makes -- so only the mouse click itself is not exercised.

LEARNED (each line is a check below):
  * Frame.CompleteConstruction (decompiled 1.6) copies the frame's style ONLY when the worker has an ideoligion
    (GetIdeoForStyle). S2 reports workerHasIdeo and frameStyleRestored: if the worker had no ideo and the style still
    arrived, the Frame guard did it.
  * Industrial and Modern spans fall back to the SAME cable texture (Strand_BlackRubber) and differ only by width, so
    S6 compares look AND width, never the texture name alone.
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
ANCHORS = ["RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket"]
TEX = os.path.join(HERE, "Textures")
X0, Z0 = 60, 120                         # scene origin (left of validation_aerial's site at 90,180)
SITE = (X0 - 2, Z0 - 2, 40, 22)
ROW_B = [(X0 + 4 * i, Z0) for i in range(4)]          # build mode: 4-cell spans, autolinked in a row
ROW_G = [(X0 + 4 * i, Z0 + 8) for i in range(4)]      # god mode
COPY_AT = (X0 + 20, Z0 + 8)                           # copy of the god-mode Industrial mast
REINSTALL_AT = (X0 + 20, Z0)                          # the build-mode Futuristic mast moves here
LEGACY_AT = (X0 + 4, Z0 + 14)                         # built by jawa/build_batch: no designator, no style
TWIN_AT = (X0 + 8, Z0 + 11)                           # a second Modern god mast 3 cells from the first: a same-look span


# ============================================================================ offline
def s0_offline(rows):
    probs, info = [], {}
    p = os.path.join(HERE, "Defs", "Aerial", "RM_AerialStyles.xml")
    root = ET.parse(p).getroot()
    styles = {e.findtext("defName"): e for e in root.findall("ThingStyleDef")}
    want = {"%s_%s" % (a, l) for a in ANCHORS for l in LOOKS}
    if set(styles) != want:
        probs.append("style defs: missing %s extra %s" % (sorted(want - set(styles)), sorted(set(styles) - want)))
    for n, e in styles.items():
        tp = e.findtext("graphicData/texPath") or ""
        cls = e.findtext("graphicData/graphicClass") or ""
        look = n.rsplit("_", 1)[-1]
        if "/Styles/%s/" % look not in tp:
            probs.append("%s: texPath %s is not its own look's folder" % (n, tp))
        files = [tp + s + ".png" for s in (("_north", "_east", "_south") if cls == "Graphic_Multi" else ("",))]
        for f in files:
            if not os.path.exists(os.path.join(TEX, f)):
                probs.append("%s: art missing %s" % (n, f))
    anchors = open(os.path.join(HERE, "Defs", "Aerial", "RM_AerialAnchors.xml"), encoding="utf-8").read()
    base = anchors[anchors.index('Name="RM_AerialAnchorBase"'):anchors.index("</ThingDef>")]
    if "CompProperties_Styleable" not in base:
        probs.append("RM_AerialAnchorBase lacks CompProperties_Styleable")
    # sanity probe: the parser sees the anchor defs it must see
    info["anchorDefsSeen"] = sum(1 for a in ANCHORS if "<defName>%s</defName>" % a in anchors)
    if info["anchorDefsSeen"] != 3:
        probs.append("sanity: anchor defs not found in RM_AerialAnchors.xml (%d/3)" % info["anchorDefsSeen"])
    # design 6: no StyleCategoryDef may list our styles (an ideoligion would then hand them out); sweep every Defs xml
    hits, seen = [], 0
    for dp, _, fs in os.walk(os.path.join(V.REPO, "src")):
        for f in fs:
            if not f.endswith(".xml") or "Defs" not in dp:
                continue
            seen += 1
            try:
                t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if re.search(r"<StyleCategoryDef[\s>]", t) and re.search(r"RM_Aerial(Mast|LampMast|WallBracket)_", t):
                hits.append(os.path.relpath(os.path.join(dp, f), V.REPO))
    info["defsXmlSwept"] = seen
    if hits:
        probs.append("a StyleCategoryDef lists our styles: %s" % hits)
    # stage 1 removed the shared-def edit: nothing in AerialMaterials writes a ThingDef's graphic any more
    am = open(os.path.join(HERE, "Source", "Aerial", "AerialMaterials.cs"), encoding="utf-8").read()
    if re.search(r"\bd\.graphicData\s*=|\bd\.graphic\s*=|ext\.attachZ\s*=", am):
        probs.append("AerialMaterials still edits a shared ThingDef / extension")
    V.row(rows, "S0_style_defs_offline", "FAIL" if probs else "PASS", "MOD", {"problems": probs, **info, "styleDefs": len(styles)})


# ============================================================================ live
def _A():
    import validation_aerial as VA
    return VA.A()


def _by_pos(st):
    return {(a["x"], a["z"]): a for a in st.get("anchors") or []}


def _look_of(style):
    return style.rsplit("_", 1)[-1] if style else None


def run_live(args):
    B = _A()
    rows = []
    res = {"mod": V.MOD, "mode": "live", "script": "validation_style.py", "tier": V.TIER, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    d = B.ap("defaults")
    if not d.get("success"):
        V.row(rows, "S_probe_channel", "FAIL", "HARNESS", d)
        res["aborted"] = "aerial probe dead"
        return res
    B.ap("clearpicks")
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    B.ticks(2)

    # ---------------------------------------------------------------- S1: menu pick -> designator -> blueprint (build mode)
    placed = []
    for look, c in zip(LOOKS, ROW_B):
        placed.append((look, c, B.ap("place:RM_AerialMast:%s:%d,%d:build" % (look, c[0], c[1]))))
    bad = [(l, r.get("designatorStyle"), (r.get("made") or {}).get("kind"), (r.get("made") or {}).get("rawStyle"), r.get("error"))
           for l, c, r in placed if not r.get("success") or r.get("designatorStyle") != "RM_AerialMast_" + l
           or (r.get("made") or {}).get("kind") != "blueprint" or (r.get("made") or {}).get("rawStyle") != "RM_AerialMast_" + l]
    V.row(rows, "S1_pick_reaches_blueprint", "FAIL" if bad else "PASS", "MOD",
          {"bad": bad, "meaning": "PASS = each picked look is the designator's style (getter patch, any game mode) and is stored on the blueprint"})

    # ---------------------------------------------------------------- S2: blueprint -> frame -> building
    fb = B.ap("finishbuild")
    B.ticks(3)
    st = B.ap("styles")
    bp = _by_pos(st)
    bad = []
    for look, c in zip(LOOKS, ROW_B):
        a = bp.get(c)
        if not a or a.get("rawStyle") != "RM_AerialMast_" + look or "/Styles/%s/" % look not in (a.get("graphicPath") or ""):
            bad.append((look, c, a and a.get("rawStyle"), a and a.get("graphicPath")))
    V.row(rows, "S2_blueprint_frame_building", "FAIL" if bad or not fb.get("success") else "PASS", "MOD",
          {"bad": bad, "finishbuild": fb, "frameStyleRestored": st.get("frameStyleRestored"),
           "meaning": "PASS = the engine carried each look blueprint -> frame -> building, and each mast DRAWS its look's art"})

    # ---------------------------------------------------------------- S3: god mode
    gres = [(look, c, B.ap("place:RM_AerialMast:%s:%d,%d:god" % (look, c[0], c[1]))) for look, c in zip(LOOKS, ROW_G)]
    B.ticks(3)
    st = B.ap("styles")
    bp = _by_pos(st)
    bad = [(l, c, r.get("error"), (bp.get(c) or {}).get("rawStyle"), (bp.get(c) or {}).get("graphicPath")) for l, c, r in gres
           if not r.get("success") or (r.get("made") or {}).get("kind") != "building" or (bp.get(c) or {}).get("rawStyle") != "RM_AerialMast_" + l
           or "/Styles/%s/" % l not in ((bp.get(c) or {}).get("graphicPath") or "")]
    V.row(rows, "S3_god_mode", "FAIL" if bad else "PASS", "MOD", {"bad": bad, "meaning": "PASS = god mode writes the picked look straight onto the building"})
    twin = B.ap("place:RM_AerialMast:Modern:%d,%d:god" % TWIN_AT)        # for S6's same-look span
    if not twin.get("success"):
        res["twin"] = twin

    # ---------------------------------------------------------------- S4: Copy carries the look (picks last set Futuristic)
    ind = bp.get(ROW_G[1]) or {}
    cp = B.ap("copy:%s:%d,%d" % (ind.get("id"), COPY_AT[0], COPY_AT[1])) if ind else {"success": False, "error": "no Industrial god mast"}
    B.ap("finishbuild")
    B.ticks(3)
    st = B.ap("styles")
    bp = _by_pos(st)
    got = (bp.get(COPY_AT) or {}).get("rawStyle")
    V.row(rows, "S4_copy_carries_look", "PASS" if cp.get("success") and got == "RM_AerialMast_Industrial" else "FAIL", "MOD",
          {"copy": cp, "built": got, "lastPicked": st.get("lastPicked"),
           "meaning": "PASS = copying an Industrial mast builds Industrial although the button's last pick is Futuristic"})

    # ---------------------------------------------------------------- S5: pack up + reinstall keeps the look
    fut = bp.get(ROW_B[3]) or {}
    ri = B.ap("reinstall:%s:%d,%d" % (fut.get("id"), REINSTALL_AT[0], REINSTALL_AT[1])) if fut else {"success": False}
    B.ap("finishbuild")
    B.ticks(3)
    st = B.ap("styles")
    bp = _by_pos(st)
    moved = bp.get(REINSTALL_AT) or {}
    V.row(rows, "S5_reinstall_keeps_look", "PASS" if ri.get("success") and ri.get("minifiedStyle") == "RM_AerialMast_Futuristic"
          and moved.get("id") == fut.get("id") and moved.get("rawStyle") == "RM_AerialMast_Futuristic" else "FAIL", "MOD",
          {"reinstall": ri, "after": {k: moved.get(k) for k in ("id", "rawStyle", "graphicPath")}})

    # ---------------------------------------------------------------- S8 (scene part): a legacy mast, no designator, no style
    V_build = B.call("jawa/build_batch", ops="RM_AerialMast:%d,%d" % LEGACY_AT, faction="player", wipeExisting=False)
    B.ticks(3)
    st = B.ap("styles")
    bp = _by_pos(st)
    lg = bp.get(LEGACY_AT) or {}
    dl = st.get("defaultLook")
    V.row(rows, "S8_legacy_unstyled_draws_default", "PASS" if lg and lg.get("rawStyle") is None and lg.get("style") == "RM_AerialMast_%s" % dl
          and "/Styles/%s/" % dl in (lg.get("graphicPath") or "") else "FAIL", "MOD",
          {"build": V_build.get("success"), "legacy": {k: lg.get(k) for k in ("rawStyle", "style", "graphicPath")}, "defaultLook": dl,
           "meaning": "PASS = an unstyled mast stores NO style (an older save is unchanged) yet draws the default look"})

    # ---------------------------------------------------------------- S6: spans draw in their poles' look
    bad, mixed, same = [], 0, 0
    for a in st.get("anchors") or []:
        for s in a.get("spans") or []:
            o = next((b for b in st["anchors"] if b["id"] == s["other"]), {})
            la, lb = _look_of(a.get("style")), _look_of(o.get("style"))
            expect = la if la == lb else (la if a["id"] <= o["id"] else lb)
            if la == lb:
                same += 1
            else:
                mixed += 1
            if s.get("look") != expect:
                bad.append((a["id"], o.get("id"), la, lb, s.get("look")))
        for s in a.get("spans") or []:
            ls = (st.get("lookSpans") or {}).get(s.get("look")) or {}
            if s.get("spanTex") != ls.get("tex") or abs((s.get("width") or 0) - (ls.get("width") or 0)) > 1e-3:
                bad.append(("tex/width", a["id"], s))
    spans = same + mixed
    V.row(rows, "S6_spans_in_pole_look", "PASS" if spans >= 4 and same >= 1 and mixed >= 1 and not bad else "FAIL", "MOD",
          {"spans": spans, "sameLook": same, "mixedLook": mixed, "bad": bad[:8], "lookSpans": st.get("lookSpans"),
           "meaning": "PASS = a same-look span draws that look's cable; a mixed span draws the OLDER pole's (stage 1 stand-in)"})
    res["styles_before"] = st

    # ---------------------------------------------------------------- S7: save / load
    if args.save:
        res["save"] = _save_load(B, rows, args.save, st)
    else:
        V.row(rows, "S7_save_load_styles", "UNMEASURED", "HARNESS", "run with --save NAME to include save/load")
    return res


def _snapshot(st):
    return sorted((a["x"], a["z"], a.get("rawStyle"), a.get("graphicPath"), tuple(sorted((s.get("look"), s.get("spanTex"), s.get("width")) for s in a.get("spans") or [])))
                  for a in st.get("anchors") or [])


def _save_load(B, rows, name, before_st):
    before = V._saves_stat()
    if name + ".rws" in before:
        V.row(rows, "S7_save_load_styles", "FAIL", "HARNESS", "%s.rws exists" % name)
        return {}
    B.call("rimworld/save_game", saveName=name)
    time.sleep(3.0)
    after = V._saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    if new != [name + ".rws"] or changed:
        V.row(rows, "S7_save_load_styles", "FAIL", "HARNESS", {"new": new, "changed": changed})
        return {}
    B.call("rimworld/load_game", saveName=name)
    ok, waited = V._wait_playing(B)
    if not ok:
        V.row(rows, "S7_save_load_styles", "FAIL", "SITE", {"state": waited})
        return {}
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    st, t0 = {}, time.time()
    while time.time() - t0 < 12.0:          # anchors register a little after load (validation_aerial LEARNED)
        B.ticks(10)
        time.sleep(1.0)
        st = B.ap("styles")
        if len(st.get("anchors") or []) >= len(before_st.get("anchors") or []):
            break
    a, b = _snapshot(before_st), _snapshot(st)
    V.row(rows, "S7_save_load_styles", "PASS" if a == b and a else "FAIL", "MOD",
          {"anchors": len(a), "differs": [x for x in a if x not in b][:4], "loadSeconds": waited})
    return st


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--save", default=None, metavar="NAME", help="also save and reload as NAME (a NEW save file)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.offline:
        rows = []
        s0_offline(rows)
        return 0 if all(r["status"] == "PASS" for r in rows) else 1
    if not a.live:
        ap.print_help()
        return 2
    res = run_live(a)
    os.makedirs(os.path.join(HERE, "northstar"), exist_ok=True)
    out = a.out or os.path.join(HERE, "northstar", "validation_style_%s_%s.json" % (res["mode"], time.strftime("%Y%m%dT%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    t = {}
    for r in res["rows"]:
        t[r["status"]] = t.get(r["status"], 0) + 1
    print("style %s: %s -> %s" % (res["mode"], t, out))
    return 0 if not res.get("aborted") and not t.get("FAIL") else 1


if __name__ == "__main__":
    sys.exit(main())
