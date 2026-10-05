"""validation_style.py -- Gimme Some Slack per-build style, STAGES 1-2 (poles; conduit runs): functional script beside validation_aerial.py.

Design: design/RimMandrake/messyconduit_style_per_build_design.md (architecture B, section 5 stage 1, owner decisions
2026-10-04). The look is stored on each building in the engine's own style field (CompStyleable, ThingStyleDefs in
Defs/Aerial/RM_AerialStyles.xml); StylePicker.cs adds the build-button menu, the designator style getter, the copy
carry-over, the legacy read (unstyled -> default look, never written) and a Frame guard.

    python3 validation_style.py --offline                    # S0: style defs, art on disk, no ideo category lists them
    python.exe validation_style.py --live [--save NAME]      # S1-S8: THE one behaviour check of stage 1 (needs colonists),
                                                             # then S9 + S10: stage 2's two behaviour checks (conduit runs)

STAGE 2 (design 5 stage 2, owner decisions 2026-10-04; ConduitStyles.cs / ConduitStylePicker.cs / RM_MapComponent_ConduitRuns.cs).
The probe verbs are on the AerialProbe channel (ConduitStyleProbe): cstyles / cplace / cline / cfinishbuild / crestyle /
cdeconstruct / cprocess.
  S9  two runs in two styles (Industrial 6 cells, Modern orange 3 cells + a Modern switch), a Futuristic cell bridging them
      (the 6-cell run wins: all Industrial, the switch too, a message naming Modern and Industrial), a split by
      deconstruction (both halves stay Industrial), a "Restyle this run" of one half to Modern random mix (the other half
      untouched), a build-mode Futuristic line (blueprint -> frame -> building keeps the style); then every cell's stored
      style and every cord piece's printed material are read (a piece prints its run's look; the section meshes hold it);
      with --save, the same read after save/load must be identical.
  S10 an unstyled (legacy) conduit line built outside the menu: nothing is stored, nothing is written when it is
      processed, and every piece chooses the SAME Material objects the pre-stage-2 default-look set chose (an older
      save looks unchanged -- the materials-identity proof standing in for a screenshot hash).

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
    s0b_offline(rows)


COLOURS = ["Orange", "Green", "Brown", "Yellow", "Blue"]
CONDUITS = ["PowerConduit", "WaterproofConduit"]


def stage2_style_names():
    names = []
    for d in CONDUITS:
        for l in LOOKS:
            names.append("%s_%s" % (d, l))
            if l == "Modern":
                names += ["%s_Modern_%s" % (d, c) for c in COLOURS + ["Mix"]]
    return names + ["PowerSwitch_%s" % l for l in LOOKS] + ["StandingLamp_%s" % l for l in LOOKS]


def s0b_offline(rows):
    """Stage 2 offline: the 24 style defs (conduit markers carry NO graphic; switch styles point at art on disk), the guarded
    CompProperties_Styleable patch, and the per-look art the cord layer and the switch now pick."""
    probs, info = [], {}
    root = ET.parse(os.path.join(HERE, "Defs", "Aerial", "RM_ConduitStyles.xml")).getroot()
    styles = {e.findtext("defName"): e for e in root.findall("ThingStyleDef")}
    want = set(stage2_style_names())
    if set(styles) != want:
        probs.append("stage-2 style defs: missing %s extra %s" % (sorted(want - set(styles)), sorted(set(styles) - want)))
    for n, e in styles.items():
        has_g = e.find("graphicData") is not None
        if n.startswith("PowerSwitch_") or n.startswith("StandingLamp_"):
            tp = e.findtext("graphicData/texPath") or ""
            if not os.path.exists(os.path.join(TEX, tp + ".png")):
                probs.append("%s: art missing %s" % (n, tp))
            if n.startswith("StandingLamp_") and tp != "RimMandrake/GimmeSomeSlack/Styles/%s/StandingLamp" % n.split("_", 1)[1]:
                probs.append("%s: lamp must draw its own look's art, got %s" % (n, tp))
        elif has_g:
            probs.append("%s: a conduit style must be a marker (a graphic would make the conduit visible)" % n)
    pt = os.path.join(HERE, "Patches", "RM_ConduitStyleable.xml")
    patch = open(pt, encoding="utf-8").read() if os.path.exists(pt) else ""
    for d in ("PowerConduit", "PowerSwitch", "StandingLamp"):
        if 'defName="%s"]/comps/li[@Class="CompProperties_Styleable"]' % d not in patch or "PatchOperationConditional" not in patch:
            probs.append("patch: %s lacks the guarded CompProperties_Styleable add" % d)
    if 'defName="WaterproofConduit"' in patch:
        probs.append("patch: WaterproofConduit inherits PowerConduit's comps; patching it too lists the comp twice")
    # every look's switch on/off frames, live frayed ends, and Modern's dark strip (art stage 2026-10-04)
    need = ["PowerSwitch.png", "PowerSwitch_Off.png"] + ["Styles/%s/PowerSwitch%s.png" % (l, s) for l in LOOKS[1:] for s in ("", "_Off")]
    need += ["Styles/%s/EndFrayed_Live.png" % f for f in ("StarWars", "ExtCord", "Cybertek")] + ["Styles/ExtCord/PowerStrip_Off.png"]
    need += ["Styles/ExtCord/Strand_%s.png" % c for c in COLOURS] + ["Styles/StarWars/Strand_%s.png" % k for k in ("BlackRubber", "CorrugatedSteel", "CoiledBlack")]
    need += ["Styles/Cybertek/Strand.png", "Strand_Jawa.png"]
    # art round 5: the floor lamp per look, the power-tap clamp per look (Scrapper = root Aerial/TapClamp)
    need += ["Styles/%s/StandingLamp.png" % l for l in LOOKS] + ["Aerial/TapClamp.png"] + ["Aerial/Styles/%s/TapClamp.png" % l for l in LOOKS[1:]]
    miss = [f for f in need if not os.path.exists(os.path.join(TEX, "RimMandrake", "GimmeSomeSlack", f))]
    info["artChecked"] = len(need)
    if miss:
        probs.append("art missing: %s" % miss)
    hits = 0
    for dp, _, fs in os.walk(os.path.join(V.REPO, "src")):
        for f in fs:
            if f.endswith(".xml") and "Defs" in dp:
                t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                if re.search(r"<StyleCategoryDef[\s>]", t) and re.search(r"(PowerConduit|WaterproofConduit|PowerSwitch|StandingLamp)_(Scrapper|Industrial|Modern|Futuristic)", t):
                    hits += 1
    if hits:
        probs.append("%d StyleCategoryDef files list stage-2 styles" % hits)
    info["styleDefsSeen"] = len(styles)
    if len(styles) < 20:
        probs.append("sanity: parser saw only %d stage-2 style defs" % len(styles))
    V.row(rows, "S0b_stage2_defs_offline", "FAIL" if probs else "PASS", "MOD", {"problems": probs, **info})


# ============================================================================ live
def prepare_site(B, rect, rows, rid):
    """Make a site's cells independent of the quicktest map's random terrain (roofed ruins, rock, plants, non-soil floor).
    Clear everything, Soil, unfog, remove roof, then READ BACK: any roof or any thing still standing in the rect is an
    environmental block and is recorded UNMEASURED (never a mod FAIL). Returns True when the site is ready."""
    r = "%d,%d,%d,%d" % tuple(rect)
    why = []
    for tool, kw in (("jawa/destroy_batch", {"rects": r, "categories": "All"}),
                     ("jawa/set_terrain_batch", {"ops": "Soil:" + r}),
                     ("jawa/set_fog", {"action": "unfog", "rect": r}),
                     ("jawa/set_roof_batch", {"ops": "None:" + r})):
        res = B.call(tool, **kw)
        if isinstance(res, dict) and res.get("success") is False:
            why.append("%s refused: %s" % (tool, str(res)[:160]))
    B.ticks(2)
    roof = B.call("jawa/get_roof_batch", rects=r) or {}
    roofs = [x for x in (roof.get("roofs") or []) if x not in (None, "None")]
    if roofs:
        why.append("roof still present over the site: %s" % roofs)
    elif roof.get("success") is False:
        why.append("get_roof_batch unreadable: %s" % str(roof)[:160])
    lt = B.call("jawa/list_things", rect=r, limit=20) or {}
    # only terrain-type blockers count (a quicktest colonist may stand on the site; list_things' pawn/category fields are unproven)
    left = [d for d in ((t.get("defName") or t.get("def") or t.get("label") or "") for t in (lt.get("things") or []))
            if re.search(r"Granite|Sandstone|Limestone|Marble|Slate|Rock|Chunk|Plant_|Tree|Bush|Grass|Ruin", str(d))]
    if left:
        why.append("rock/plants/ruins still standing in the site: %s" % left[:8])
    if why:
        V.row(rows, rid, "UNMEASURED", "SITE", {"rect": list(rect), "blocked": why,
              "meaning": "the quicktest terrain still blocks the site after clearing; this is environmental, not a mod result"})
        return False
    return True


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
    if not (prepare_site(B, SITE, rows, "S_site_ready") & prepare_site(B, SITE2, rows, "S9_site_ready")):
        res["aborted"] = "site not ready (terrain)"
        return res
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
    # stage 2 (design 2.3): auto-link only links a pole to a run of the SAME look, so no mixed span forms here any more;
    # a span's look is its run's (ConduitStyles.SpanLook: larger run wins, tie older) -- "expect" above is that tie case
    V.row(rows, "S6_spans_in_pole_look", "PASS" if spans >= 1 and same >= 1 and mixed == 0 and not bad else "FAIL", "MOD",
          {"spans": spans, "sameLook": same, "mixedLook": mixed, "bad": bad[:8], "lookSpans": st.get("lookSpans"),
           "meaning": "PASS = a same-look span draws that look's cable, and auto-link strung no span between two looks (stage 2)"})
    res["styles_before"] = st

    # ---------------------------------------------------------------- stage 2: S9 runs, S10 legacy
    s9 = s9_runs(B, rows, res)
    s10 = s10_legacy(B, rows, res)

    # ---------------------------------------------------------------- S7: save / load (stage 1 masts, then S9's read)
    if args.save:
        # LEARNED live 2026-10-04: S9's site clear destroys anchors that stood in SITE2 (e.g. at 63,154 and 79,154), so
        # comparing against the stage-1 read taken BEFORE S9 reported them as "changed by the load". Read again just
        # before saving: the comparison is then load-only.
        res["save"] = _save_load(B, rows, args.save, B.ap("styles"))
        s9_after_load(B, rows, s9, s10)
    elif not V.SHARED:               # SHARED: S7 + S9e are proof_all's SL3 over the session's one save (doc section 2)
        V.row(rows, "S7_save_load_styles", "UNMEASURED", "HARNESS", "run with --save NAME to include save/load")
        V.row(rows, "S9e_runs_save_load", "UNMEASURED", "HARNESS", "run with --save NAME to include save/load")
    return res


# ============================================================================ stage 2 (conduit runs)
SITE2 = (X0, Z0 + 26, 30, 12)                       # clear of stage 1's site (z up to Z0+21)
ZR = Z0 + 29                                         # the two-runs row
RUN_A = [(X0 + 2 + i, ZR) for i in range(6)]         # Industrial, 6 conduit cells
BRIDGE = (X0 + 8, ZR)                                # the gap; a Futuristic cell placed here joins A and B
RUN_B = [(X0 + 9 + i, ZR) for i in range(3)]         # Modern orange, 3 conduit cells
SWITCH = (X0 + 12, ZR)                               # a Modern switch at the end of run B
SPLIT = (X0 + 5, ZR)                                 # deconstructed: halves X0+2..4 and X0+6..12
ZF = Z0 + 32
LINE_F = [(X0 + 2 + i, ZF) for i in range(4)]        # a build-mode Futuristic line (blueprint -> frame -> building)
MIX_SPUR = [(X0 + 9, ZR + 1 + i) for i in range(3)]  # S9d round 5: a 3-cell Modern mix spur off the right half -> a T node,
                                                     # so the mix run has >= 3 node-to-node pieces (a 2-cell spur is pruned)
ZL = Z0 + 35
LEGACY = [(X0 + 2 + i, ZL) for i in range(8)]       # S10: unstyled, built outside the menu


def _members(st):
    return {(m["x"], m["z"]): m for m in st.get("members") or []}


def _cst(B):
    B.ap("cprocess")
    B.ticks(2)
    return B.ap("cstyles:%d,%d,%d,%d" % SITE2)


def _piece_look_bad(st):
    """Every cord piece owned on a styled cell must print its cell's run look; returns the offenders and the count checked."""
    mem = _members(st)
    bad, n = [], 0
    for p in st.get("pieces") or []:
        m = mem.get(tuple(p["owner"]))
        if not m or not m.get("look") or not p.get("strands"):
            continue
        n += 1
        if p.get("look") != m["look"] or p.get("legacy") or p.get("strandTex") not in ((st.get("lookStrands") or {}).get(m["look"]) or []):
            bad.append((p["owner"], m["look"], p.get("look"), p.get("strandTex")))
    return bad, n


def s9_runs(B, rows, res):
    B.ap("cclearpicks")
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE2, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE2)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE2)
    B.call("rimworld/frame_cell_rect", x=SITE2[0], z=SITE2[1], width=SITE2[2], height=SITE2[3], paddingCells=1)
    B.ticks(2)
    out = {}
    # ---- S9a: two runs in two styles
    a = B.ap("cline:PowerConduit:Industrial:%d,%d:%d,%d:god" % (RUN_A[0] + RUN_A[-1]))
    b = B.ap("cline:PowerConduit:Modern_Orange:%d,%d:%d,%d:god" % (RUN_B[0] + RUN_B[-1]))
    sw = B.ap("cplace:PowerSwitch:Modern:%d,%d:god" % SWITCH)
    st = _cst(B)
    mem = _members(st)
    ok_a = all((mem.get(c) or {}).get("rawStyle") == "PowerConduit_Industrial" for c in RUN_A)
    ok_b = all((mem.get(c) or {}).get("rawStyle") == "PowerConduit_Modern_Orange" for c in RUN_B) and (mem.get(SWITCH) or {}).get("rawStyle") == "PowerSwitch_Modern"
    runs = {(mem.get(c) or {}).get("run") for c in RUN_A} | {(mem.get(c) or {}).get("run") for c in RUN_B}
    pb, pn = _piece_look_bad(st)
    V.row(rows, "S9a_two_runs_two_styles", "PASS" if a.get("success") and b.get("success") and sw.get("success") and ok_a and ok_b and len(runs) == 2 and pn >= 2 and not pb else "FAIL", "MOD",
          {"runs": len(runs), "piecesChecked": pn, "pieceBad": pb[:6], "switchDrawn": (mem.get(SWITCH) or {}).get("drawnTex"),
           "errors": [x.get("error") for x in (a, b, sw) if not x.get("success")],
           "meaning": "PASS = each run stores its picked style on every cell (the switch adopts its Modern run) and its cords print that look"})
    # ---- S9b: a Futuristic cell bridging them -> the 6-cell Industrial run wins, the 3-cell run + switch are repainted
    br = B.ap("cplace:PowerConduit:Futuristic:%d,%d:god" % BRIDGE)
    st = _cst(B)
    mem = _members(st)
    allc = RUN_A + [BRIDGE] + RUN_B
    wrong = [(c, (mem.get(c) or {}).get("rawStyle")) for c in allc if (mem.get(c) or {}).get("rawStyle") != "PowerConduit_Industrial"]
    swr = (mem.get(SWITCH) or {}).get("rawStyle")
    msg = st.get("lastMessage") or ""
    pb, pn = _piece_look_bad(st)
    V.row(rows, "S9b_bridge_largest_wins", "PASS" if br.get("success") and not wrong and swr == "PowerSwitch_Industrial" and "Modern" in msg and "Industrial" in msg
          and len({(mem.get(c) or {}).get("run") for c in allc}) == 1 and not pb else "FAIL", "MOD",
          {"wrong": wrong, "switch": swr, "switchDrawn": (mem.get(SWITCH) or {}).get("drawnTex"), "message": msg, "counters": st.get("counters"), "pieceBad": pb[:6],
           "meaning": "PASS = bridging Industrial(6) and Modern(3) with a Futuristic cell: one run, all Industrial incl. the switch, a message naming both"})
    # ---- S9c: split by deconstruction -> both halves keep Industrial
    dc = B.ap("cdeconstruct:%d,%d" % SPLIT)
    st = _cst(B)
    mem = _members(st)
    left = [c for c in allc if c[0] < SPLIT[0]]
    right = [c for c in allc if c[0] > SPLIT[0]] + [SWITCH]
    kept = all((mem.get(c) or {}).get("look") == "Industrial" for c in left + right) and SPLIT not in mem
    two = len({(mem.get(c) or {}).get("run") for c in left}) == 1 and len({(mem.get(c) or {}).get("run") for c in right}) == 1 and \
        (mem.get(left[0]) or {}).get("run") != (mem.get(right[0]) or {}).get("run")
    V.row(rows, "S9c_split_keeps_styles", "PASS" if dc.get("success") and kept and two else "FAIL", "MOD",
          {"deconstruct": dc, "left": [(mem.get(c) or {}).get("rawStyle") for c in left], "right": [(mem.get(c) or {}).get("rawStyle") for c in right],
           "meaning": "PASS = deconstructing the middle leaves two runs, each still Industrial"})
    # ---- S9d: restyle the right half to Modern random mix; the left half is untouched; a build-mode Futuristic line
    rs = B.ap("crestyle:%d,%d:Modern_Mix" % right[1])
    sp = B.ap("cline:PowerConduit:Modern_Mix:%d,%d:%d,%d:god" % (MIX_SPUR[0] + MIX_SPUR[-1]))
    fl = B.ap("cline:PowerConduit:Futuristic:%d,%d:%d,%d:build" % (LINE_F[0] + LINE_F[-1]))
    fb = B.ap("cfinishbuild")
    B.ticks(3)
    st = _cst(B)
    mem = _members(st)
    r_ok = all((mem.get(c) or {}).get("rawStyle") == ("PowerSwitch_Modern" if c == SWITCH else "PowerConduit_Modern_Mix") for c in right)
    l_ok = all((mem.get(c) or {}).get("rawStyle") == "PowerConduit_Industrial" for c in left)
    f_ok = all((mem.get(c) or {}).get("rawStyle") == "PowerConduit_Futuristic" for c in LINE_F)
    pb, pn = _piece_look_bad(st)
    # owner round 5 (2026-10-04, station 5): "Each run from one node to another stays a single color, but it varies through
    # the whole nodal array" -- REVERTS round 4's colour change along a cord. Each mix piece prints ONE strand colour; the
    # pieces of the mix run (with the spur: >= 3 pieces around a T node) show >= 2 colours between them
    mix_cells = set(right) | set(MIX_SPUR)
    right_pieces = [p for p in st.get("pieces") or [] if tuple(p["owner"]) in mix_cells and p.get("strands")]
    piece_tex = [p.get("strandTex") for p in right_pieces if p.get("mix")]
    right_tex = set(t for t in piece_tex if t)
    uniform = all(len(p.get("mixTex") or []) == 1 and p["mixTex"][0] == p.get("strandTex") for p in right_pieces if p.get("mix"))
    mix_flag = all(p.get("mix") for p in right_pieces if (mem.get(tuple(p["owner"])) or {}).get("def") != "PowerSwitch")
    sp_ok = all((mem.get(c) or {}).get("rawStyle") == "PowerConduit_Modern_Mix" for c in MIX_SPUR)
    printed = st.get("printedTex") or {}
    unprinted = sorted({p.get("strandTex") for p in st.get("pieces") or [] if p.get("strands")} - set(printed))
    # LEARNED live 2026-10-04: a straight run is ONE cord piece; this scene has the left Industrial half, the mix pieces and
    # the Futuristic line
    mixed_ok = len(piece_tex) >= 3 and len([t for t in right_tex if t.startswith("Strand_")]) >= 2 and uniform and mix_flag and sp_ok and \
        all(t in printed for t in right_tex)
    # far zoom: every mix piece colour also has its LOD mesh (the LOD strand is the piece's own single colour)
    lod_on = any(k.endswith("(lod)") for k in printed)
    lod_missing = sorted(t for t in right_tex if (t + "(lod)") not in printed) if lod_on else []
    mixed_ok = mixed_ok and not lod_missing
    V.row(rows, "S9d_restyle_and_materials", "PASS" if rs.get("success") and r_ok and l_ok and f_ok and pn >= 3 and not pb and not unprinted and mixed_ok else "FAIL", "MOD",
          {"restyle": rs, "build": {"line": fl.get("success"), "finish": fb}, "rightColours": sorted(x for x in right_tex if x), "pieceBad": pb[:6],
           "unprintedStrands": unprinted, "printedTex": printed, "switchDrawn": (mem.get(SWITCH) or {}).get("drawnTex"),
           "mixPieceTex": piece_tex, "spur": sp.get("success"),
           "conds": {"restyle": bool(rs.get("success")), "right": r_ok, "left": l_ok, "futuristic": f_ok, "piecesChecked": pn, "mixPieces": len(piece_tex),
                     "eachPieceOneColour": uniform, "spurMix": sp_ok, "mixed": mixed_ok, "lodMissing": lod_missing},
           "meaning": "PASS = Restyle repaints only its own run (Mix; switch Modern); each mix piece node to node is ONE colour and the run's >= 3 pieces show >= 2 colours (round 5), build mode keeps Futuristic, every piece prints its run's look and the section meshes hold every piece's strand"})
    out["st"] = st
    res["stage2_before"] = st
    return out


def s10_legacy(B, rows, res):
    before = _cst(B)
    mat0 = (before.get("counters") or {}).get("materialised")
    bb = B.call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d" % c for c in LEGACY), faction="player", wipeExisting=False)
    B.ticks(3)
    st = _cst(B)
    mem = _members(st)
    raw = [(mem.get(c) or {}).get("rawStyle") for c in LEGACY]
    leg = [p for p in st.get("pieces") or [] if p["owner"][1] == ZL]
    same = [p for p in leg if p.get("legacy") and p.get("legacySameMaterials")]
    dl = st.get("defaultLook")
    in_default = all(p.get("strandTex") in ((st.get("lookStrands") or {}).get(dl) or []) for p in leg if p.get("strands"))
    V.row(rows, "S10_legacy_default_materials", "PASS" if len(mem.keys() & set(LEGACY)) == len(LEGACY) and all(r is None for r in raw) and leg and len(same) == len(leg)
          and in_default and (st.get("counters") or {}).get("materialised") == mat0 else "FAIL", "MOD",
          {"build": bb.get("success"), "rawStyles": raw, "pieces": len(leg), "sameMaterials": len(same), "defaultLook": dl, "defaultKey": st.get("defaultKey"),
           "materialisedBefore": mat0, "materialisedAfter": (st.get("counters") or {}).get("materialised"),
           "meaning": "PASS = an unstyled line stores nothing, processing writes nothing, and every piece chooses the SAME Material objects as the pre-stage-2 default-look set (older saves look unchanged)"})
    return {"st": st}


def _s9_snap(st):
    return (sorted((m["x"], m["z"], m["def"], m.get("rawStyle")) for m in st.get("members") or []),
            sorted((tuple(p["owner"]), p.get("key"), p.get("g"), p.get("strandTex"), p.get("legacy")) for p in st.get("pieces") or []))


def s9_after_load(B, rows, s9, s10):
    before = s10.get("st") or s9.get("st") or {}
    st = {}
    t0 = time.time()
    while time.time() - t0 < 12.0:
        st = _cst(B)
        if len(st.get("members") or []) >= len(before.get("members") or []):
            break
        B.ticks(10)
        time.sleep(1.0)
    a, b = _s9_snap(before), _s9_snap(st)
    V.row(rows, "S9e_runs_save_load", "PASS" if a == b and a[0] else "FAIL", "MOD",
          {"members": len(a[0]), "pieces": len(a[1]), "membersDiffer": [x for x in a[0] if x not in b[0]][:6], "piecesDiffer": [x for x in a[1] if x not in b[1]][:6],
           "meaning": "PASS = after save/load every cell's stored style and every piece's material index and strand texture are identical (legacy cells still store nothing)"})


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
