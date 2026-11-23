"""HELD MATERIAL, built early, awaiting ingest (owner, 2026-11-12 ~9:35 PM PST: "store these items until our validation ladder is
fully defined and regenerated. Then we will ingest them properly"). Wired into NO ladder stage, gate, nightly list or close
check; do not add it to one. Index: design/RimMandrake/validation_holding/README.md. Its selftest is found by the nightly
sweep's selftest*.py discovery, only so it does not rot.

RIMMANDRAKE_PIN_OWNER_LOOK_DEFECTS_AS_NAMED_TESTS: the owner's 2026-11-12 pit looks, kept fixed by STATE READ.

    python.exe owner_look_regressions.py <OUT dir> [--plan <scene_plan.json>] [--acts [x,z]]
    exit 0 PASS, 1 FAIL, 2 UNMEASURED or BLOCKED.

Owner, 2026-11-12 ~9:20 PM PST: "So are we recording each of these defects for future testing to keep them fixed? I believe
these sessions were supposed to generate test cases in the future, especially if they can be made offline or very fast
ingame validations, yes?"  The table of every defect: design/RimMandrake/validation_holding/owner_look_defects_2026-11-12.md.

Runs on the keeper scene UNDER_LIQUID_LAW_BIGPIT_20261112b (big_pit_scene.py's series: BP0 dry .. BP5 brim water, BP6 tar),
read from its scene_plan.json (`--plan`; default <OUT>\\scene_plan.json). Read only, unless --acts (then it pours on the
spare dry test pit the plan names, its "spare" [x, z, side, depth], and drains it again; never on the series, never saves;
`--acts x,z` names a spare by hand, e.g. 140,100 on the 11-12 keeper save, whose plan predates "spare"). Minimal list, about
a minute.

What a row can and cannot see: RM_SubmergeDraw.ProofSubmerge reports what the ONE under-liquid law decides for the first
thing at a cell (share under, seenLine, seenFoot, shadow, label alpha). It reads the law each drawer is handed, not the
pixels. The overlays, flames and ropes are read by their own reader, RM_SubmergeDraw.ProofOverlays (676c5cd131), and the
pit label by RM_Patch_MouseoverDepth.ProofPitLabel; a build without a reader reads that row BLOCKED, never faked.

Rows (one family per owner sentence; the pure judges below are selftested by selftest_owner_look_regressions.py):
  OL_buildings_covered      18:15 "It's easy to see which items are not going under water" -> every installed building in
                            a wet copy reports kind=building and share > 0 (the build he saw drew none of them under).
  OL_goods_covered          16:2x "Items (raw steel, minified furniture) never become covered" -> items, minified: share > 0.
  OL_corpses_covered        18:15 corpses drawn whole; 20:55 "ignore bodies" -> kind=corpse, share > 0.
  OL_opaque_hides           20:55 "deep tar seems to ignore bodies, torches ..." -> in tar every drowned part seenLine 0.
  OL_no_surface_shadow      18:15 "Strange shadows are being cast by some items and not others"; 11-13 01:26Z "it should
                            simply be transparent to them as usual" -> a building in a pit has ONE floor shadow at its own
                            (dry) alpha in clear liquid, drawn UNDER the liquid's sheet so the sheet hides it by the law
                            (RM_UnderLiquid.ThingShadow, RM_FaceMaterial.UnderSheetQueue); 0 under tar; 0 or a faded alpha
                            in clear liquid is FAIL. The draw order (shadowQueue) is judged per thing if ProofSubmerge ever
                            reports it; it does not, so the order is his walk's to see (polish.md).
  OL_labels_fade            18:15 labels at full brightness over faded items -> a label fades with its thing's TOP
                            (RM_UnderLiquid.LabelAlpha): label < 1 once the line is over the top in clear liquid, 0 under
                            tar; a top at the line is seen whole.
  OL_one_law_over_fill      16:2x "It's as though each case is independently set" -> per thing, BP0..BP5: share never
                            falls and seenFoot never rises as the water rises.
  OL_pour_never_no_room     20:49 "it always responded "No Room." It shouldn't do that. It should go ahead and overflow."
                            (--acts only) -> a pour into a brim-full pit replies OK and never "no room".
  OL_screenshot_mode_off    18:15 "The game is no longer allowing me to select objects at all..." (cause: screenshot mode
                            left on) -> at the end of the run screenshot mode is off, and it was not left on before.
  OL_label_text_true_depth  17:57 "It's supposed to show the precise depth no matter what" -> per copy, 16 cells (every
                            LABEL_STRIDE): ProofPitLabel's line starts with the text RM_Volume.PitLabel gives the true grid
                            (jawa/flowworks_excavation_rect d, dl, fluid): "Pit, 8.0 m deep" / "Pit, 2.5 m water in 8.0 m".
                            Left out: what LineAt appends after it (floor, walk speed, readout, sunk geyser).
  OL_overlays_hidden        20:30/20:55 connector over the battery, wires over furniture, battery bar, cooler arrow, torch
                            flame, power icon -> per planned building, item, minified good: ProofOverlays carries the alpha
                            RM_UnderLiquid.OverlayAlpha is due (1 middle dry, 0 once 0.5 m over the top, else seen; an icon
                            drawn whole where it is due less is FAIL), the realtime verdict, a flame out under the line, and
                            cords seen as the floor. Left out: corpses (two readers, two heights), pawns (none planned).
UNTESTED LIVE as committed (2026-11-12): the judges are selftested offline against a fake bridge; the bridge replies are
the shapes pit_fittings_matrix.py and the 20:11 live run read (ProofSubmerge text, list_things rows, screenshot_mode).
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

SUB = "RimMandrake.FlowWorks.RM_SubmergeDraw"
GL = "RimMandrake.FlowWorks.RM_GodLiquid"
PW = 16
SPARE_SIDE_DEPTH = (6, 8)       # a spare named by hand (--acts x,z) with no plan spare: the 11-12 keeper's side and notches
THING_SHADOW_ALPHA = 0.30       # RM_UnderLiquid.DefaultThingShadowAlpha (kept equal by selftest_flowworks_underliquid_parity)
SHEET_QUEUE = 2449              # RM_FaceMaterial.SheetQueue: a floor shadow must draw before it (UnderSheetQueue 2448)
NOTCH_M = 0.5                   # RM_Volume.MetresPerNotch: ProofSubmerge's level= is in notches
LINE_TOL = 0.006                # level= and height= are printed F2
EPS = 1e-6
OVERLAY_HOOK = "RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS"
LABEL_T = "RimMandrake.FlowWorks.RM_Patch_MouseoverDepth"   # ProofPitLabel lives here (RM_MouseoverDepth.cs)
FLUID_LABEL = {"RM_Fluid_Water": "water", "RM_Fluid_Tar": "tar"}   # FluidDef labels, Defs/Canals/FluidDefs/FlowWorks_Fluids.xml
UNITS_PER_LEVEL = 10000         # RM_Volume.UnitsPerLevel (dl per notch): PitLabel prints dl * 0.5 / 10000 m
LABEL_STRIDE = 5                # label cells read per copy: i, j in 0, 5, 10, 15 (16 of 256: walls' feet and middle)
LABEL_TAILS = (" (", " \u2014 ", " \u00b7 ")   # what LineAt appends: walk speed, depth readout, floor phrase or sunk geyser
OV_TOL = 0.002                  # overlay=, share=, cords= (ProofOverlays) and seenFoot=, share= (ProofSubmerge) are F3: 2 x 0.0005, doubled
OV_EDGE = 0.008                 # a band edge cannot be placed closer: level= F2 in notches (x 0.5 m: 0.0025) + height= F2 (0.005)
SEEN_EDGE = 0.001               # LABEL_HIDDEN against a seenFoot printed F3 (0.0005, doubled)
LABEL_HIDDEN = 0.05             # RM_UnderLiquid.LabelHidden
OVERLAY_HIDE_M = 0.5            # RM_UnderLiquid.OverlayHideMetres
LABEL_HOOK = "RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE"
ROWS = []
B = None


# ---------- pure half: no bridge ----------

def kv_of(text):
    """'def=Bed kind=building share=0.500 ...' -> dict; a REFUSED reply -> {}."""
    if not text or str(text).startswith("REFUSED"):
        return {}
    out = {}
    for tok in str(text).split(" "):
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def vacuous(text, kv):
    """-> why the read cannot judge anything (no map, no engine, no pit cell), or None. A REFUSED "nothing drawn" over a
    dug cell is not vacuous: when a presence read finds the planned thing there (judge_absent), it is drawn whole over
    the liquid (judge_covered's FAIL)."""
    t = str(text or "")
    if t.startswith("REFUSED"):
        if "nothing drawn" not in t or "(depth=0 " in t:
            return "vacuous read: " + t[:120]
        return None
    if kv and num(kv, "depth") == 0:
        return "the thing is not in a pit cell (depth=0)"
    return None


def num(kv, k, dflt=None):
    try:
        return float(kv.get(k))
    except (TypeError, ValueError):
        return dflt


def judge_covered(kv, want_kind, wet, want_def=None):
    """A thing in a copy: wet -> it reports the kind it is and some of it is under (share > 0); dry -> share 0.
    -> (verdict, why)."""
    if not kv:
        return "FAIL", "the law reports nothing for it (ProofSubmerge refused): it is drawn whole over the liquid"
    if want_def and kv.get("def") != want_def:
        return "UNMEASURED", "first thing at the cell is %s, not %s" % (kv.get("def"), want_def)
    share = num(kv, "share")
    if share is None:
        return "UNMEASURED", "no share field"
    if want_kind and kv.get("kind") != want_kind:
        return "FAIL", "kind=%s, want %s" % (kv.get("kind"), want_kind)
    if wet and share <= 0.0:
        return "FAIL", "share=%s in liquid" % kv.get("share")
    if not wet and share != 0.0:
        return "FAIL", "share=%s when dry" % kv.get("share")
    return "PASS", "kind=%s share=%s" % (kv.get("kind"), kv.get("share"))


def judge_opaque(kv):
    """Under an opaque liquid (clarity 0) the drowned part is not seen at all."""
    share, line, foot, cl = num(kv, "share"), num(kv, "seenLine"), num(kv, "seenFoot"), num(kv, "clarity")
    if None in (share, line, foot, cl):
        return "UNMEASURED", "fields missing: %s" % sorted(kv)
    if cl != 0.0:
        return "FAIL", "tar clarity=%s, want 0" % kv.get("clarity")
    if share <= 0.0:
        return "FAIL", "share=0 under tar"
    if line > EPS or foot > EPS:
        return "FAIL", "seen through tar: seenLine=%s seenFoot=%s" % (kv.get("seenLine"), kv.get("seenFoot"))
    return "PASS", "hidden (share=%s)" % kv.get("share")


def judge_shadow(kv, wet, dry=None):
    """A building in a pit casts one floor shadow (RM_UnderLiquid.ThingShadow): dry its alpha (the setting
    pitThingShadowAlpha); in clear liquid the SAME alpha, drawn under the sheet, which hides it by the law; tar 0.
    dry: the alpha the same def read in the dry copy, when known. A shadowQueue at or after the sheet is FAIL."""
    s, cl, q = num(kv, "shadow"), num(kv, "clarity", 0.0), num(kv, "shadowQueue")
    if s is None:
        return "UNMEASURED", "shadow=%s (not a building in a pit?)" % kv.get("shadow")
    if not wet:
        return ("PASS", "dry shadow %s" % s) if s > EPS else ("FAIL", "no shadow at all in a dry pit")
    if cl == 0.0:
        return ("PASS", "tar: no shadow") if s <= EPS else ("FAIL", "shadow %s seen through tar" % s)
    if s <= EPS:
        return "FAIL", "no shadow under clear liquid: it should be transparent to it (owner 11-13), not hide it"
    if q is not None and q >= SHEET_QUEUE:
        return "FAIL", "shadow %s drawn OVER the liquid sheet (queue %d >= %d)" % (s, q, SHEET_QUEUE)
    if dry is not None and abs(s - dry) > EPS:
        return "FAIL", "shadow %s in clear liquid, %s dry: the drawer fades it itself (the old over-the-sheet shadow)" % (s, dry)
    return "PASS", "own alpha %s under clear liquid%s" % (s, "" if q is None else ", queue %d under the sheet" % q)


def judge_label(kv):
    """A label over a thing wholly under liquid fades (clear) or is hidden (opaque)."""
    lab, share, cl = num(kv, "label"), num(kv, "share"), num(kv, "clarity", 0.0)
    lv, h = num(kv, "level"), num(kv, "height")
    if lab is None or share is None:
        return "UNMEASURED", "no label/share field"
    if share < 1.0 - EPS:
        return "PASS", "partly above (share %s): label %s" % (kv.get("share"), lab)
    if lv is not None and h is not None and lv * NOTCH_M - h <= LINE_TOL:     # LabelAlpha fades with the TOP
        return "PASS", "top at the line (level %s m, height %s m): label %s" % (lv * NOTCH_M, h, lab)
    if cl == 0.0:
        return ("PASS", "hidden under tar") if lab <= EPS else ("FAIL", "label %s over a thing hidden in tar" % lab)
    return ("PASS", "label %s" % lab) if lab < 1.0 - EPS else ("FAIL", "label at full brightness over a drowned thing")


def judge_monotone(seq):
    """seq: [(fill, share, seenFoot)] of one thing across the water copies. One law: as the fill rises share never falls
    and seenFoot never rises."""
    seq = sorted(seq)
    bad = [(a, b) for a, b in zip(seq, seq[1:]) if b[1] < a[1] - EPS or b[2] > a[2] + EPS]
    return ("PASS" if not bad else "FAIL"), " ".join("%d,%.3f,%.3f" % t for t in seq)


def judge_pour(reply):
    """A pour into a brim-full pit overflows: OK, and never 'no room'."""
    r = str(reply or "")
    if not r.startswith("OK"):
        return "FAIL", r[:200]
    if "no room" in r.lower():
        return "FAIL", "replied OK but kept a remainder for room: " + r[:200]
    return "PASS", r[:200]


def judge_screenshot(before, after):
    """before/after: jawa/screenshot_mode replies. Off at the end, and nothing left it on before this run."""
    def active(r):
        if not isinstance(r, dict):
            return None
        for k in ("activeAfter", "active", "activeBefore"):
            if isinstance(r.get(k), bool):
                return r[k]
        return None
    a0, a1 = active(before), active(after)
    if a1 is None or a0 is None:
        return "UNMEASURED", "screenshot_mode unreadable: %s / %s" % (str(before)[:80], str(after)[:80])
    if a1:
        return "FAIL", "screenshot mode still ON at the end: every map click is eaten"
    if a0:
        return "FAIL", "screenshot mode was left ON before this run (turned off now): the 18:15 dead-selection defect"
    return "PASS", "off before and after"


def plan_rows(plan):
    """-> [(copy key, x0, z0, fill notches, fluid, kind, def, world x, world z)] for every planned thing in every copy.
    plan: big_pit_scene.py's scene_plan.json (copies [key, x0, z0, fill, fluid]; things [kind, k2, def, src, [i, j], n])."""
    out = []
    for key, x0, z0, f, fl in plan["copies"]:
        for kind, _k2, dn, _src, (i, j), _n in plan["things"]:
            out.append((key, x0, z0, f, fl, kind, dn, x0 + i, z0 + j))
    return out


WANT_KIND = {"furn": "building", "item": "item", "mini": "minified", "corpse": "corpse"}


def present_at(things, kind, dn, x, z):
    """things: list_things rows of the copy (def, x, z), or None when unread. -> True/False, or None when unread.
    A minified good reads def MinifiedThing, a corpse Corpse_<race> (a Villager's is Corpse_Human), the rest its own def."""
    if things is None:
        return None
    for t in things:
        if (t.get("x"), t.get("z")) != (x, z):
            continue
        d = str(t.get("def"))
        if (d == "MinifiedThing" if kind == "mini" else d.startswith("Corpse_") if kind == "corpse" else d == dn):
            return True
    return False


def judge_absent(text, kv, here, x0, z0, kind, dn, x, z):
    """ProofSubmerge says 'nothing drawn under liquid' both for a thing drawn whole over the liquid and for no thing at
    the cell (visit 2: the minified goods were absent after a staging miss, and 9 rows read FAIL). -> None when the read
    may be judged (the thing is there), else why it is UNMEASURED. here(x0, z0) -> the copy's list_things rows or None."""
    if kv or not str(text or "").startswith("REFUSED"):
        return None
    if here is None:
        return "no presence read: 'nothing drawn' cannot tell a thing drawn whole from no thing at %d,%d" % (x, z)
    p = present_at(here(x0, z0), kind, dn, x, z)
    if p is None:
        return "presence unreadable (list_things failed): 'nothing drawn' at %d,%d cannot be judged" % (x, z)
    return None if p else "the planned %s %s is not at %d,%d (a staging miss, not a look): nothing to judge" % (kind, dn, x, z)


def judge_scene(plan, proof, here=None):
    """plan: scene_plan.json; proof(x, z) -> ProofSubmerge text; here(x0, z0) -> the copy's list_things rows (def, x, z) or
    None when unreadable. -> list of (row, verdict, got). Pure but for proof() and here()."""
    rows, mono, dry = [], {}, {}
    pr = plan_rows(plan)
    if not pr:
        return [("OL_scene", "UNMEASURED", "the plan has no things in its copies: nothing to read")]
    reads = [(r, proof(r[7], r[8])) for r in pr]
    for (_key, _x0, _z0, f, _fl, kind, dn, _x, _z), text in reads:
        kv = kv_of(text)
        if kind == "furn" and f == 0 and num(kv, "shadow") is not None and not vacuous(text, kv):
            dry[dn] = num(kv, "shadow")
    for (key, x0, z0, f, fl, kind, dn, x, z), text in reads:
        kv = kv_of(text)
        wet = f > 0
        want_def = "MinifiedThing" if kind == "mini" else None if kind == "corpse" else dn
        fam = {"furn": "OL_buildings_covered", "corpse": "OL_corpses_covered"}.get(kind, "OL_goods_covered")
        vac = vacuous(text, kv) or judge_absent(text, kv, here, x0, z0, kind, dn, x, z)
        if vac:
            rows.append(("%s_%s_%s_%s" % (fam, key, kind, dn), "UNMEASURED", vac))
            continue
        v, why = judge_covered(kv, WANT_KIND[kind], wet, want_def)
        rows.append(("%s_%s_%s_%s" % (fam, key, kind, dn), v, why))
        if v != "PASS" or not wet:
            if v == "PASS" and kind == "furn":
                rows.append(("OL_no_surface_shadow_%s_%s" % (key, dn),) + judge_shadow(kv, False))
            continue
        if fl:
            rows.append(("OL_opaque_hides_%s_%s_%s" % (key, kind, dn),) + judge_opaque(kv))
        else:
            mono.setdefault((kind, dn), []).append((f, num(kv, "share", 0.0), num(kv, "seenFoot", 1.0)))
        if kind == "furn":
            rows.append(("OL_no_surface_shadow_%s_%s" % (key, dn),) + judge_shadow(kv, True, dry.get(dn)))
        rows.append(("OL_labels_fade_%s_%s_%s" % (key, kind, dn),) + judge_label(kv))
    for (kind, dn), seq in sorted(mono.items()):
        if len(seq) > 1:
            rows.append(("OL_one_law_over_fill_%s_%s" % (kind, dn),) + judge_monotone(seq))
    return rows


def spare_of(plan, at=None):
    """The spare pit --acts pours on: (x, z, side, depth notches). at (x, z) by hand wins and keeps the plan spare's side and
    depth (else SPARE_SIDE_DEPTH); else the plan's "spare"; None when neither (never another save's pit, guessed)."""
    sp = plan.get("spare")
    if at:
        return tuple(at) + (tuple(sp[2:]) if sp else SPARE_SIDE_DEPTH)
    return tuple(sp) if sp else None


def hook_missing(reply):
    """The bridge's static_call answer when the build has no such reader (JawaBenchCompanionProbeTools: "Type not found: ..."
    or "No public static <method> with N params.")."""
    t = str(reply or "")
    return "No public static" in t or "Type not found" in t


def exact_metres(m):
    """RM_Volume.FormatExactMetres: "0.00" under 0.05 m (above 0), else "0.0", then " m". Mono formats a double to 15
    significant digits and rounds the pattern half away from zero (0.15 -> "0.2"; Python's "%.1f" gives "0.1")."""
    m = max(0.0, float(m))
    q = Decimal("0.01") if 0.0 < m < 0.05 else Decimal("0.1")
    return str(Decimal("%.15g" % m).quantize(q, rounding=ROUND_HALF_UP)) + " m"


def pit_label_want(d, dl, fluid, plan_fluid):
    """RM_Volume.PitLabel from the true grid (RM_MapComponent_Excavation.PitLabelAt): d notches dug, dl decilitres standing,
    fluid the recorded FluidDef (null when unrecorded: the label then names the active fluid, which this script cannot
    read, so the plan's poured fluid stands in; None in the plan = water). -> the expected text, or None when the cell is
    not dug or its fluid has no label known here."""
    if d is None or d <= 0:
        return None
    hole = exact_metres(d * NOTCH_M)
    if not dl or dl <= 0:
        return "Pit, %s deep" % hole
    word = FLUID_LABEL.get(fluid or plan_fluid or "RM_Fluid_Water")
    if word is None:
        return None
    return "Pit, %s %s in %s" % (exact_metres(dl * NOTCH_M / UNITS_PER_LEVEL), word, hole)


def judge_pit_label(reply, want):
    """reply: ProofPitLabel's answer ("line=<the mouseover line>" | "line=vanilla" | "fogged" | "REFUSED: ..."). The line
    starts with the true-depth label; what LineAt puts after it (a floor " · ", the walk speed " (", the depth readout
    " — ", a sunk geyser " · ") is not judged here."""
    t = str(reply or "")
    if not t.startswith("line="):
        return "UNMEASURED", "label unread: " + t[:100]
    line = t[5:]
    if line == "vanilla":
        return "FAIL", "a dug square shows vanilla's line, not %r" % want
    if line == want or any(line.startswith(want + tail) for tail in LABEL_TAILS):
        return "PASS", line[:120]
    return "FAIL", "shows %r, want %r" % (line[:120], want)


def judge_labels(plan, label_read, rect_read):
    """OL_label_text_true_depth, one row per copy: LABEL_STRIDE-spaced cells (16 of 256) read by ProofPitLabel against the
    label the true grid names (jawa/flowworks_excavation_rect d, dl, fluid). Any wrong cell FAILs the copy; a cell that
    cannot be judged (fogged, refused, not dug, unread) makes it UNMEASURED; a reader missing from the build is BLOCKED.
    label_read(x, z) -> reply; rect_read(x0, z0) -> the copy's rows or None."""
    rows = []
    for key, x0, z0, _f, fl in plan.get("copies") or []:
        name = "OL_label_text_true_depth_" + key
        cells = rect_read(x0, z0)
        if cells is None:
            rows.append((name, "UNMEASURED", "excavation_rect unreadable: no true depth to hold the label to"))
            continue
        at = {(c.get("x"), c.get("z")): c for c in cells}
        n, bad, unj, last = 0, [], [], ""
        for i in range(0, PW, LABEL_STRIDE):
            for j in range(0, PW, LABEL_STRIDE):
                x, z = x0 + i, z0 + j
                c = at.get((x, z))
                try:
                    d, dl = int(c.get("d")), float(c.get("dl") or 0)
                except (AttributeError, TypeError, ValueError):
                    unj.append("%d,%d: no excavation row" % (x, z))
                    continue
                want = pit_label_want(d, dl, c.get("fluid"), fl)
                if want is None:
                    unj.append("%d,%d: d=%d fluid=%s (not dug, or a fluid with no known label)" % (x, z, d, c.get("fluid")))
                    continue
                reply = label_read(x, z)
                if hook_missing(reply):
                    return [blocked_rows()[0]]
                v, why = judge_pit_label(reply, want)
                if v == "UNMEASURED":
                    unj.append("%d,%d: %s" % (x, z, why))
                    continue
                n += 1
                last = why
                if v == "FAIL":
                    bad.append("%d,%d: %s" % (x, z, why))
        if bad:
            rows.append((name, "FAIL", "%d of %d cells wrong (limit 0); first %s" % (len(bad), n, bad[0])))
        elif unj or not n:
            rows.append((name, "UNMEASURED", "%d cells read, %d unjudged; first %s" % (n, len(unj), unj[0] if unj else "-")))
        else:
            rows.append((name, "PASS", "%d cells read, 0 wrong (limit 0); last %r" % (n, last[:80])))
    return rows or [("OL_label_text_true_depth", "UNMEASURED", "the plan has no copies")]


def overlay_lines(text):
    """ProofOverlays text -> ([kv of each thing line], cords float or None)."""
    things, cords = [], None
    for ln in str(text or "").split("\n"):
        ln = ln.strip()
        if ln.startswith("cords="):
            cords = num({"c": ln[6:]}, "c")
        elif ln.startswith("def="):
            things.append(kv_of(ln))
    return things, cords


def overlay_wants(lv, h, seen):
    """RM_UnderLiquid.OverlayAlpha(clarity, lv, h) with Seen(clarity, lv) = seen: 1 while the middle is above the line, 0
    once OVERLAY_HIDE_M stands over the top, else seen (0 under LABEL_HIDDEN). Within OV_EDGE of a band edge (or SEEN_EDGE
    of LABEL_HIDDEN) both neighbours are due: the printed values cannot place it. -> (set of due alphas, at an edge)."""
    if lv <= 0:
        return {1.0}, False
    mids = {lv >= h * 0.5} | ({True, False} if abs(lv - h * 0.5) <= OV_EDGE else set())
    hides = {lv - h >= OVERLAY_HIDE_M - 1e-4} | ({True, False} if abs(lv - h - OVERLAY_HIDE_M) <= OV_EDGE else set())
    fades = {0.0 if seen < LABEL_HIDDEN else seen} | ({0.0, seen} if abs(seen - LABEL_HIDDEN) <= SEEN_EDGE else set())
    out = set()
    for m in mids:
        for hd in hides:
            out |= {1.0} if not m else {0.0} if hd else fades
    return out, len(out) > 1


def judge_overlay(kv, ov_text, want_def):
    """kv: ProofSubmerge's read of the thing (level notches, height, share, seenFoot, label = the law); ov_text: ProofOverlays
    at its cell. The thing's line must carry the overlay alpha the law is due (an icon drawn whole where the law hides or
    fades it is FAIL), the realtime verdict (whole dry, hidden once its label is gone, else split at the same share), a flame
    out once its top is under the line, and cords (a rope on the floor) seen as the floor is (seenFoot wet, 1 dry)."""
    t = str(ov_text or "")
    if not t.strip() or t.startswith("REFUSED") or "cords=" not in t:
        return "UNMEASURED", "overlay read unusable: " + t[:100]
    things, cords = overlay_lines(t)
    mine = [k for k in things if k.get("def") == want_def]
    if not mine:
        return "UNMEASURED", "ProofOverlays lists no %s at the cell (%s)" % (want_def, [k.get("def") for k in things][:4])
    o = mine[0]
    a, osh, flame, rt = num(o, "overlay"), num(o, "share"), o.get("flame"), o.get("realtime")
    if None in (a, osh, cords) or flame not in ("none", "shows", "out") or rt not in ("whole", "hidden", "bodycover", "split"):
        return "UNMEASURED", "overlay line garbled: %s cords=%s" % (sorted(o.items())[:6], cords)
    lvn, h, sh, foot, lab = (num(kv, k) for k in ("level", "height", "share", "seenFoot", "label"))
    if None in (lvn, h, sh, foot, lab):
        return "UNMEASURED", "the law's read lacks level/height/share/seenFoot/label: %s" % sorted(kv)[:8]
    lv = lvn * NOTCH_M
    wants, edge = overlay_wants(lv, h, foot)
    wet = lv > 0 and sh > 0
    top_edge = abs(lv - h) <= OV_EDGE
    fails = []
    if not any(abs(a - w) <= OV_TOL for w in wants):
        fails.append("overlay %s, law %s%s" % (o.get("overlay"), "/".join("%.3f" % w for w in sorted(wants)),
                                               " (drawn whole)" if a >= 1 - EPS else " (hidden)" if a <= EPS else ""))
    rts = {"whole"} if not wet else ({"hidden"} if lab <= EPS else {"split"}) | ({"hidden", "split"} if top_edge else set())
    if rt not in rts:
        fails.append("realtime=%s, law %s" % (rt, "/".join(sorted(rts))))
    elif rt == "split" and abs(osh - sh) > OV_TOL:
        fails.append("realtime share %s, law share %s" % (o.get("share"), kv.get("share")))
    if flame != "none":
        outs = {False} if not wet else {True, False} if top_edge else {lab <= EPS or sh >= 1 - EPS}
        if (flame == "out") not in outs:
            fails.append("flame %s with its top %s the line" % (flame, "under" if True in outs else "above"))
    cw = foot if lv > 0 else 1.0
    if abs(cords - cw) > OV_TOL:
        fails.append("cords %.3f, the floor seen %.3f" % (cords, cw))
    got = "overlay %s (law %s%s) realtime %s flame %s cords %.3f" % (
        o.get("overlay"), "/".join("%.3f" % w for w in sorted(wants)), ", band edge" if edge else "", rt, flame, cords)
    return ("FAIL", "; ".join(fails) + " | " + got) if fails else ("PASS", got)


def judge_overlays(plan, proof, overlays_read):
    """OL_overlays_hidden, one row per planned building, item and minified good in every copy: judge_overlay of
    ProofOverlays(x, z) against ProofSubmerge(x, z). Left out: corpses (OverlayAlpha stands a corpse at the item height,
    ProofSubmerge at its pawn's: one read cannot give the other's law) and pawns (none planned). A reader missing from
    the build is one BLOCKED row. proof(x, z) / overlays_read(x, z) -> reply text."""
    rows = []
    for key, x0, z0, f, fl, kind, dn, x, z in plan_rows(plan):
        if kind == "corpse":
            continue
        name = "OL_overlays_hidden_%s_%s_%s" % (key, kind, dn)
        ov = overlays_read(x, z)
        if hook_missing(ov):
            return [blocked_rows()[1]]
        text = proof(x, z)
        kv = kv_of(text)
        vac = vacuous(text, kv)
        want_def = "MinifiedThing" if kind == "mini" else dn
        if vac or not kv:
            rows.append((name, "UNMEASURED", vac or "the law's read refused (%s): the overlay's due alpha is unknown" % text[:80]))
        elif kv.get("def") != want_def:
            rows.append((name, "UNMEASURED", "first thing at the cell is %s, not %s" % (kv.get("def"), want_def)))
        else:
            rows.append((name,) + judge_overlay(kv, ov, want_def))
    return rows or [("OL_overlays_hidden", "UNMEASURED", "the plan has no building, item or minified good")]


def blocked_rows():
    """The two reader rows when the build lacks the reader (the bridge says the method or type is missing): BLOCKED, so the
    run never reads PASS over a reader that is not there."""
    return [("OL_label_text_true_depth", "BLOCKED", "the build has no pit label reader (" + LABEL_T + ".ProofPitLabel, "
             "676c5cd131; " + LABEL_HOOK + ")"),
            ("OL_overlays_hidden", "BLOCKED", "the build has no overlay reader (" + SUB + ".ProofOverlays, 676c5cd131; "
             + OVERLAY_HOOK + "): power icon, cooler arrow, torch flame and GSS cords cannot be read")]


def exit_code(rows):
    vs = {r[1] for r in rows}
    return 1 if "FAIL" in vs else 2 if vs & {"UNMEASURED", "BLOCKED"} else 0


# ---------- live half: the bridge ----------

def bridge():
    global B
    if B is None:
        sys.path.insert(0, os.path.join(os.environ.get("RM_REPO", r"D:\Luke\dev\RimMandrake"), "src", "RimMandrake", "Utils"))
        import validation_core as V
        B = V.Bridge()
    return B


def call(tool, **kw):
    try:
        return bridge().call(tool, **kw) or {}
    except Exception as ex:  # noqa: BLE001
        return {"success": False, "error": str(ex)}


def static(type_, method, arg):
    r = call("jawa/static_call", type=type_, method=method, args=arg)
    return str(r.get("result") or r.get("error") or r.get("message") or r)


def acts(spare):
    """--acts: on the spare dry pit only. Fill to the brim, pour 1000 L more, then drain all (and the overflow)."""
    x0, z0, w, d = spare
    c = "%d,%d" % (x0 + w // 2, z0 + w // 2)
    out = []
    r0 = static(GL, "SetLevel", c + "|RM_Fluid_Water|%.1f" % (d * 0.5))
    if not r0.startswith("OK"):
        return [("OL_pour_never_no_room", "UNMEASURED", "could not brim the spare pit: " + r0[:160])]
    # PourOverflow is what the dev menu's "Pour liquid..." runs; Pour keeps to the overflow switches and refuses a brim pit
    # by design (live 2026-11-12 night: "REFUSED ... had no room (the dev action overflows it)")
    out.append(("OL_pour_never_no_room",) + judge_pour(static(GL, "PourOverflow", c + "|RM_Fluid_Water|1000")))
    static(GL, "DrainAll", c)
    for dx, dz in ((-1, 0), (w, 0), (0, -1), (0, w)):          # the overflow, if it reached the ground
        static(GL, "DrainAll", "%d,%d" % (x0 + dx, z0 + dz))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = argv[1]
    plan_path = os.path.join(out, "scene_plan.json")
    act, at = False, None
    rest = argv[2:]
    while rest:
        a = rest.pop(0)
        if a == "--plan":
            plan_path = rest.pop(0)
        elif a == "--acts":
            act = True
            if rest and "," in rest[0]:
                at = tuple(int(v) for v in rest.pop(0).split(","))
    os.makedirs(out, exist_ok=True)
    with open(plan_path) as fh:
        plan = json.load(fh)
    spare = spare_of(plan, at) if act else None
    sm0 = call("jawa/screenshot_mode")
    seen = {}

    def here(x0, z0):
        """One list_things per copy, read once; None when the bridge cannot list it."""
        if (x0, z0) not in seen:
            r = call("jawa/list_things", rect="%d,%d,%d,%d" % (x0, z0, PW, PW), limit=2000)
            seen[(x0, z0)] = r.get("things") if r.get("success") is not False and isinstance(r.get("things"), list) else None
        return seen[(x0, z0)]
    proofs = {}

    def sub(x, z):
        """ProofSubmerge, read once a cell: judge_scene and judge_overlays share it."""
        if (x, z) not in proofs:
            proofs[(x, z)] = static(SUB, "ProofSubmerge", "%d,%d" % (x, z))
        return proofs[(x, z)]

    def rect(x0, z0):
        """The copy's true depth grid (one excavation_rect read), or None when unreadable."""
        r = call("jawa/flowworks_excavation_rect", x=x0, z=z0, w=PW, h=PW, includeTerrain=False)
        return r.get("rows") if r.get("success") is not False and isinstance(r.get("rows"), list) else None
    rows = judge_scene(plan, sub, here)
    rows += judge_overlays(plan, sub, lambda x, z: static(SUB, "ProofOverlays", "%d,%d" % (x, z)))
    rows += judge_labels(plan, lambda x, z: static(LABEL_T, "ProofPitLabel", "%d,%d" % (x, z)), rect)
    if spare:
        rows += acts(spare)
    else:
        rows.append(("OL_pour_never_no_room", "UNMEASURED", "acts off (pass --acts to pour on the spare pit)" if not act else
                     "the plan names no spare pit (a scene_plan.json older than big_pit_scene's spare): re-run big_pit_scene.py "
                     "plan and stage, or pass --acts x,z for a save whose spare is known"))
    call("jawa/screenshot_mode", enabled=False)
    rows.append(("OL_screenshot_mode_off",) + judge_screenshot(sm0, call("jawa/screenshot_mode")))
    for r in rows:
        if r[1] != "PASS":
            print(r[1], r[0], str(r[2])[:200])
    tally = {v: sum(1 for r in rows if r[1] == v) for v in ("PASS", "FAIL", "UNMEASURED", "BLOCKED")}
    print("owner_look_regressions", json.dumps(tally))
    with open(os.path.join(out, "owner_look_regressions.json"), "w") as fh:
        json.dump([{"row": r[0], "verdict": r[1], "got": r[2]} for r in rows], fh, indent=0)
    return exit_code(rows)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
