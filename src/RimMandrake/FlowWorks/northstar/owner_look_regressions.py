"""RIMMANDRAKE_PIN_OWNER_LOOK_DEFECTS_AS_NAMED_TESTS: the owner's 2026-11-12 pit looks, kept fixed by STATE READ.

    python.exe owner_look_regressions.py <OUT dir> [--plan <scene_plan.json>] [--acts [x,z]]
    exit 0 PASS, 1 FAIL, 2 UNMEASURED or BLOCKED.

Owner, 2026-11-12 ~9:20 PM PST: "So are we recording each of these defects for future testing to keep them fixed? I believe
these sessions were supposed to generate test cases in the future, especially if they can be made offline or very fast
ingame validations, yes?"  The table of every defect and its test: D:\\ClaudeWork\\rimmandrake\\conductor\\
underliquid_20261112_evening\\regressions\\DEFECT_TESTS.md.

Runs on the keeper scene UNDER_LIQUID_LAW_BIGPIT_20261112b (big_pit_scene.py's series: BP0 dry .. BP5 brim water, BP6 tar),
read from its scene_plan.json (`--plan`; default <OUT>\\scene_plan.json). Read only, unless --acts (then it pours on the
spare dry test pit, default 140,100, and drains it again; never on the series, never saves). Minimal list, about a minute.

What a row can and cannot see: RM_SubmergeDraw.ProofSubmerge reports what the ONE under-liquid law decides for the first
thing at a cell (share under, seenLine, seenFoot, shadow, label alpha). It reads the law each drawer is handed, not the
pixels: a drawer that ignores the law (overlays, ropes, flames, the corpse cover's rotation) is invisible to it. Those rows
are BLOCKED ON HOOK (item RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS), never faked.

Rows (one family per owner sentence; the pure judges below are selftested by selftest_owner_look_regressions.py):
  OL_buildings_covered      18:15 "It's easy to see which items are not going under water" -> every installed building in
                            a wet copy reports kind=building and share > 0 (the build he saw drew none of them under).
  OL_goods_covered          16:2x "Items (raw steel, minified furniture) never become covered" -> items, minified: share > 0.
  OL_corpses_covered        18:15 corpses drawn whole; 20:55 "ignore bodies" -> kind=corpse, share > 0.
  OL_opaque_hides           20:55 "deep tar seems to ignore bodies, torches ..." -> in tar every drowned part seenLine 0.
  OL_no_surface_shadow      18:15 "Strange shadows are being cast by some items and not others" -> a building in a pit has
                            ONE floor shadow, seen through by the law (tar: 0); never the dry-ground alpha.
  OL_labels_fade            18:15 labels at full brightness over faded items -> label < 1 when wholly under clear liquid,
                            0 under tar.
  OL_one_law_over_fill      16:2x "It's as though each case is independently set" -> per thing, BP0..BP5: share never
                            falls and seenFoot never rises as the water rises.
  OL_pour_never_no_room     20:49 "it always responded "No Room." It shouldn't do that. It should go ahead and overflow."
                            (--acts only) -> a pour into a brim-full pit replies OK and never "no room".
  OL_screenshot_mode_off    18:15 "The game is no longer allowing me to select objects at all..." (cause: screenshot mode
                            left on) -> at the end of the run screenshot mode is off, and it was not left on before.
  OL_label_text_true_depth  17:57 "It's supposed to show the precise depth no matter what" -> BLOCKED ON HOOK
                            (RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE); the expected text is offline in
                            PitLabelChecks.
  OL_overlays_hidden        20:30/20:55 connector over the battery, wires over furniture, battery bar, cooler arrow, torch
                            flame, power icon -> BLOCKED ON HOOK (RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS).
UNTESTED LIVE as committed (2026-11-12): the judges are selftested offline against a fake bridge; the bridge replies are
the shapes pit_fittings_matrix.py and the 20:11 live run read (ProofSubmerge text, list_things rows, screenshot_mode).
"""
import json
import os
import sys

SUB = "RimMandrake.FlowWorks.RM_SubmergeDraw"
GL = "RimMandrake.FlowWorks.RM_GodLiquid"
PW = 16
SPARE = (140, 100, 6, 8)        # the spare dry test pit of the keeper save: SW corner, side, depth notches
THING_SHADOW_ALPHA = 0.30       # RM_UnderLiquid.DefaultThingShadowAlpha (kept equal by selftest_flowworks_underliquid_parity)
EPS = 1e-6
OVERLAY_HOOK = "RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS"
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


def judge_shadow(kv, wet):
    """A building in a pit casts one floor shadow, seen through the liquid by the law: wet clear < the dry alpha, tar 0."""
    s, cl = num(kv, "shadow"), num(kv, "clarity", 0.0)
    if s is None:
        return "UNMEASURED", "shadow=%s (not a building in a pit?)" % kv.get("shadow")
    if not wet:      # dry: the plain shadow (the setting pitThingShadowAlpha; default THING_SHADOW_ALPHA)
        return ("PASS", "dry shadow %s" % s) if s > EPS else ("FAIL", "no shadow at all in a dry pit")
    if cl == 0.0:
        return ("PASS", "tar: no shadow") if s <= EPS else ("FAIL", "shadow %s seen through tar" % s)
    return ("PASS", "floor shadow %s seen through water" % s) if 0.0 <= s < THING_SHADOW_ALPHA - EPS else \
        ("FAIL", "shadow %s is the dry alpha: not seen through the water" % s)


def judge_label(kv):
    """A label over a thing wholly under liquid fades (clear) or is hidden (opaque)."""
    lab, share, cl = num(kv, "label"), num(kv, "share"), num(kv, "clarity", 0.0)
    if lab is None or share is None:
        return "UNMEASURED", "no label/share field"
    if share < 1.0 - EPS:
        return "PASS", "partly above (share %s): label %s" % (kv.get("share"), lab)
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


def judge_scene(plan, proof):
    """plan: scene_plan.json; proof(x, z) -> ProofSubmerge text. -> list of (row, verdict, got). Pure but for proof()."""
    rows, mono = [], {}
    for key, _x0, _z0, f, fl, kind, dn, x, z in plan_rows(plan):
        kv = kv_of(proof(x, z))
        wet = f > 0
        want_def = "MinifiedThing" if kind == "mini" else None if kind == "corpse" else dn
        fam = {"furn": "OL_buildings_covered", "corpse": "OL_corpses_covered"}.get(kind, "OL_goods_covered")
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
            rows.append(("OL_no_surface_shadow_%s_%s" % (key, dn),) + judge_shadow(kv, True))
        rows.append(("OL_labels_fade_%s_%s_%s" % (key, kind, dn),) + judge_label(kv))
    for (kind, dn), seq in sorted(mono.items()):
        if len(seq) > 1:
            rows.append(("OL_one_law_over_fill_%s_%s" % (kind, dn),) + judge_monotone(seq))
    return rows


def blocked_rows():
    return [("OL_label_text_true_depth", "BLOCKED", "no reader for the on-screen pit label (" + LABEL_HOOK + "); "
             "expected text is pinned offline by PitLabelChecks"),
            ("OL_overlays_hidden", "BLOCKED", "overlay drawers (power icon, battery bar, cooler arrow, torch flame, GSS "
             "rope and connector) do not report to the law (" + OVERLAY_HOOK + ")")]


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
    out.append(("OL_pour_never_no_room",) + judge_pour(static(GL, "Pour", c + "|RM_Fluid_Water|1000")))
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
    spare = None
    rest = argv[2:]
    while rest:
        a = rest.pop(0)
        if a == "--plan":
            plan_path = rest.pop(0)
        elif a == "--acts":
            spare = SPARE
            if rest and "," in rest[0]:
                x, z = (int(v) for v in rest.pop(0).split(","))
                spare = (x, z) + SPARE[2:]
    os.makedirs(out, exist_ok=True)
    with open(plan_path) as fh:
        plan = json.load(fh)
    sm0 = call("jawa/screenshot_mode")
    rows = judge_scene(plan, lambda x, z: static(SUB, "ProofSubmerge", "%d,%d" % (x, z)))
    if spare:
        rows += acts(spare)
    else:
        rows.append(("OL_pour_never_no_room", "UNMEASURED", "acts off (pass --acts to pour on the spare pit)"))
    rows += blocked_rows()
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
