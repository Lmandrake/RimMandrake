#!/usr/bin/env python3
"""Offline test of owner_look_regressions.py's judges: no bridge, no game.

A fake ProofSubmerge answers for a small big-pit series from a toy law. The fixed world must read all PASS; each planted
fault, one per owner defect of 2026-11-12, must turn its own row family FAIL (a judge that cannot go red proves nothing).
The first fault is the build he saw at 18:15: buildings, corpses and goods reported nothing to the law (drawn whole)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import owner_look_regressions as O  # noqa: E402

PLAN = {
    "copies": [["BP0_dry", 0, 0, 0, None], ["BP1", 20, 0, 1, None], ["BP3", 40, 0, 4, None],
               ["BP5_brim", 60, 0, 8, None], ["BP6_tar", 80, 0, 3, "RM_Fluid_Tar"]],
    "things": [["furn", "furn:Bed", "Bed", "Core", [3, 3], 1], ["furn", "furn:SculptureGrand", "SculptureGrand", "Core", [8, 8], 1],
               ["item", "item:0:Steel", "Steel", "Core", [5, 5], 75], ["mini", "mini:0:Armchair", "Armchair", "Core", [6, 6], 1],
               ["corpse", "corpse:0:Villager", "Villager", "Core", [10, 10], 1],
               ["furn", "furn:TableButcher", "TableButcher", "Core", [12, 12], 1]],
}
# TableButcher stands 2.0 m: in BP3 (2 m of water) its top is AT the line, as fill-0.5 things were at BP2_1m live 2026-11-15
HEIGHT = {"Bed": 0.8, "SculptureGrand": 3.0, "Steel": 0.3, "MinifiedThing": 0.75, "Corpse_Human": 0.3, "TableButcher": 2.0}
KIND = {"furn": "building", "item": "item", "mini": "minified", "corpse": "corpse"}


def toy_here(absent=(), plan=PLAN):
    """-> here(x0, z0) for PLAN: list_things rows of every planned thing at its cell (the toy world's things stand there),
    less the (kind, def) pairs in absent."""
    rows = {}
    for key, x0, z0, f, fl, kind, dn, x, z in O.plan_rows(plan):
        if (kind, dn) in absent:
            continue
        rows.setdefault((x0, z0), []).append({"def": "MinifiedThing" if kind == "mini" else "Corpse_Human" if kind == "corpse"
                                              else dn, "x": x, "z": z})
    return lambda x0, z0: rows.get((x0, z0), [])


def toy_world(fault=None, queue=2448, plan=PLAN):
    """-> proof(x, z) for PLAN under a toy law (clarity 0.45 water, 0 tar; Seen = 1 - 0.5*(1 - c^(m + 0.35))).
    The floor shadow is the 11-12 design (RM_UnderLiquid.ThingShadow): its own alpha, drawn UNDER the liquid sheet
    (shadowQueue < RM_FaceMaterial.SheetQueue 2449), none under tar. queue=None: the reply carries no shadowQueue (the
    ProofSubmerge of 2026-11-15 does not report it)."""
    at = {}
    for key, x0, z0, f, fl, kind, dn, x, z in O.plan_rows(plan):
        at[(x, z)] = (key, f, fl, kind, "MinifiedThing" if kind == "mini" else "Corpse_Human" if kind == "corpse" else dn)

    def seen(c, m):
        if m <= 0:
            return 1.0
        return 0.0 if c == 0 else 1 - 0.5 * (1 - c ** (m + 0.35))

    def proof(x, z):
        key, f, fl, kind, dn = at[(x, z)]
        if fault == "old_build" and kind in ("furn", "corpse", "item", "mini") or fault == "corpse_refused" and kind == "corpse":
            return "REFUSED: nothing drawn under liquid at %d,%d (depth=8 fill=%d)" % (x, z, f)
        lv = f * 0.5
        c = 0.0 if fl else 0.45
        h = HEIGHT[dn]
        share = 0.0 if f == 0 else min(1.0, lv / h)
        if fault == "goods_dry" and kind in ("item", "mini"):
            share = 0.0
        if fault == "non_monotone" and dn == "Bed" and key == "BP5_brim":
            share = 0.2
        line = max(0.0, lv - share * h)
        sl, sf = (seen(c, line if line > 0 else 1e-4), seen(c, lv)) if share > 0 else (1.0, 1.0)
        if fault == "tar_seen" and fl:
            sl = sf = 0.3
        shadow = (0.0 if fl else 0.30) if kind == "furn" else None
        if fault == "shadow_faded" and kind == "furn" and f > 0 and not fl:
            shadow = 0.30 * seen(c, lv)      # the drawer fading it itself: the old shadow drawn OVER the sheet
        if fault == "shadow_lost" and kind == "furn" and f > 0 and not fl:
            shadow = 0.0                     # a full pit hiding shadows (owner 11-13: "transparent to them as usual")
        q = 2450 if fault == "shadow_over_sheet" else queue
        label = (0.0 if seen(c, lv - h) < 0.05 else seen(c, lv - h)) if share > 0 else 1.0
        if fault == "label_bright" and share >= 1.0:
            label = 1.0
        sq = "" if shadow is None or q is None else " shadowQueue=%d" % q
        return ("def=%s class=X kind=%s rot=0 depth=8 fill=%d level=%.2f share=%.3f clarity=%.3f seenLine=%.3f "
                "seenFoot=%.3f printedLevel=- setting=on height=%.2f shadow=%s%s label=%.3f liquid=- tint=0.05,0.05,0.05"
                % (dn, KIND[kind], f, f, share, c, sl, sf, h, "-" if shadow is None else "%.3f" % shadow, sq, label))
    return proof


def families(rows, verdict):
    out = set()
    for name, v, _ in rows:
        if v == verdict:
            out.add(next(f for f in ("OL_buildings_covered", "OL_goods_covered", "OL_corpses_covered", "OL_opaque_hides",
                                     "OL_no_surface_shadow", "OL_labels_fade", "OL_one_law_over_fill") if name.startswith(f)))
    return out


# ---------- the two readers of 676c5cd131: RM_Patch_MouseoverDepth.ProofPitLabel (the on-screen pit label line) and
# RM_SubmergeDraw.ProofOverlays (every overlay drawer's share of the law), driven through O.main on a fake bridge ----------
# The toy plan adds a flame (the owner's 20:55 "torches"): 1.2 m toy height, so its middle (0.6 m) is above BP1's 0.5 m and
# its top is 0.8 m under BP3's 2 m (the overlay hide band, OverlayHideMetres 0.5).
HEIGHT["TorchLamp"] = 1.2
PLAN_OL = {"copies": PLAN["copies"], "things": PLAN["things"] + [["furn", "furn:TorchLamp", "TorchLamp", "Core", [14, 3], 1]]}
FLAMES = {"TorchLamp"}
WORD = {"RM_Fluid_Water": "water", "RM_Fluid_Tar": "tar"}     # Defs/Canals/FluidDefs/FlowWorks_Fluids.xml labels


def toy_seen(c, m):
    """toy_world's Seen."""
    if m <= 0:
        return 1.0
    return 0.0 if c == 0 else 1 - 0.5 * (1 - c ** (m + 0.35))


def law_overlay(c, lv, h):
    """RM_UnderLiquid.OverlayAlpha over the toy Seen (lv, h in metres)."""
    if lv <= 0 or lv < h * 0.5:
        return 1.0
    if lv - h >= 0.5 - 1e-4:
        return 0.0
    a = toy_seen(c, lv)
    return 0.0 if a < 0.05 else a


def oracle_label(d, dl, word):
    """RM_Volume.PitLabel in integers (independent of the script's mirror): metres = dl / 20000 (0.5 m per 10,000 dl),
    "0.00" under 0.05 m else "0.0", ties away from zero (Mono's double.ToString)."""
    hole = "%d.%d m" % (d // 2, 5 * (d % 2))
    if dl <= 0:
        return "Pit, %s deep" % hole
    if dl < 1000:
        m = "0.%02d m" % ((dl + 100) // 200)
    else:
        n = (dl + 1000) // 2000
        m = "%d.%d m" % (n // 10, n % 10)
    return "Pit, %s %s in %s" % (m, word, hole)


def toy_rect(plan, fault=None):
    """-> rect(x0, z0) -> excavation_rect rows of a copy: 8 notches dug, the fill minus 0..1875 dl by cell (so the copy
    holds fractional depths and x.x5 ties), fluid the plan's (water when None), null when dry."""
    fills = {(x0, z0): (f, fl) for _k, x0, z0, f, fl in plan["copies"]}

    def rect(x0, z0):
        if fault == "rect_unread":
            return None
        f, fl = fills[(x0, z0)]
        return [{"x": x0 + i, "z": z0 + j, "d": 8, "dl": max(0, f * 10000 - ((i * 7 + j * 3) % 16) * 125) if f else 0,
                 "fluid": (fl or "RM_Fluid_Water") if f else None} for i in range(O.PW) for j in range(O.PW)]
    return rect


def toy_label(plan, fault=None):
    """-> ProofPitLabel(x, z) over toy_rect, with a planted fault."""
    rect = toy_rect(plan)
    cells = {}
    for _k, x0, z0, _f, fl in plan["copies"]:
        for c in rect(x0, z0):
            cells[(c["x"], c["z"])] = c
    if fault == "no_method":
        return lambda x, z: "No public static ProofPitLabel with 1 params."
    if fault == "type_missing":
        return lambda x, z: "Type not found: RimMandrake.FlowWorks.RM_Patch_MouseoverDepth"

    def label(x, z):
        c = cells.get((x, z))
        if c is None:
            return "line=vanilla"
        d, dl, word = c["d"], c["dl"], WORD.get(c["fluid"], "water")
        if fault == "fogged":
            return "fogged"
        if fault == "refused":
            return 'REFUSED: need a current map and "x,z"'
        if fault == "vanilla":
            return "line=vanilla"
        if fault == "band":
            return "line=Pit (2 m or more) (Walk speed 100%)"
        if fault == "off_notch":
            d -= 1
        if fault == "wrong_kind" and word == "tar":
            word = "water"
        text = oracle_label(d, dl, word)
        if fault == "rounded_even" and dl >= 1000:
            text = "Pit, %.1f m %s in %d.%d m" % (dl * 0.5 / 10000, word, d // 2, 5 * (d % 2))
        tail = {"floor_tail": " · Wood floor (Walk speed 100%)", "suffix_tail": " (Walk speed 100%) — Hole 4 m · Water"}
        return "line=" + text + tail.get(fault, " (Walk speed 100%)")
    return label


def toy_overlays(plan, fault=None):
    """-> ProofOverlays(x, z) under the toy law, with a planted fault."""
    at = {}
    for key, x0, z0, f, fl, kind, dn, x, z in O.plan_rows(plan):
        at[(x, z)] = (f, fl, kind, "MinifiedThing" if kind == "mini" else "Corpse_Human" if kind == "corpse" else dn)
    if fault == "no_method":
        return lambda x, z: "No public static ProofOverlays with 1 params."
    if fault == "type_missing":
        return lambda x, z: "Type not found: RimMandrake.FlowWorks.RM_SubmergeDraw"

    def ov(x, z):
        if fault == "refused":
            return "REFUSED: cell off the map"
        if (x, z) not in at:
            return "cords=1.000"
        f, fl, kind, dn = at[(x, z)]
        lv, c, h = f * 0.5, (0.0 if fl else 0.45), HEIGHT[dn]
        if f == 0:
            rt, share = "whole", 0.0
        elif toy_seen(c, lv - h) < 0.05:
            rt, share = "hidden", 0.0
        elif kind == "corpse":
            rt, share = "bodycover", 0.0
        else:
            rt, share = "split", min(1.0, lv / h)
        flame = "none" if dn not in FLAMES else "out" if rt == "hidden" or rt == "split" and share >= 1 else "shows"
        a = law_overlay(c, lv, h) if kind != "corpse" else 1.0
        if fault == "icon_whole":
            a = 1.0
        if fault == "faded_not_hidden" and f and lv - h >= 0.5 - 1e-4:
            a = toy_seen(c, lv)
        if fault == "hidden_dry" and f == 0 or fault == "hidden_high" and f and lv < h * 0.5:
            a = 0.0
        if fault == "flame_shows" and flame != "none":
            flame = "shows"
        if fault == "flame_out_dry" and flame != "none" and f == 0:
            flame = "out"
        cords = toy_seen(c, lv) if f else 1.0
        if fault == "cords_dry":
            cords = 1.0
        if fault == "missing_def":
            return "cords=%.3f" % cords
        if fault == "garbled":
            return "def=%s id=7\ncords=%.3f" % (dn, cords)
        return "def=%s id=%d realtime=%s share=%.3f flame=%s overlay=%.3f\ncords=%.3f" % (
            dn, 1000 + x * 100 + z, rt, share, flame, a, cords)
    return ov


def run_main(plan=PLAN_OL, label_fault=None, ov_fault=None, world_fault=None, rect_fault=None):
    """O.main on a fake bridge (no game): -> (exit code, [(row, verdict, got)])."""
    import json
    import tempfile
    here = toy_here(plan=plan)
    world, lab, ovs, rect = (toy_world(world_fault, plan=plan), toy_label(plan, label_fault), toy_overlays(plan, ov_fault),
                             toy_rect(plan, rect_fault))

    def fake(tool, **kw):
        if tool == "jawa/screenshot_mode":
            return {"success": True, "activeBefore": False, "activeAfter": False}
        if tool == "jawa/list_things":
            x0, z0 = (int(v) for v in kw["rect"].split(",")[:2])
            return {"success": True, "things": here(x0, z0)}
        if tool == "jawa/flowworks_excavation_rect":
            rows = rect(kw["x"], kw["z"])
            return {"success": False, "error": "no map"} if rows is None else {"success": True, "rows": rows}
        if tool == "jawa/static_call":
            x, z = (int(v) for v in str(kw["args"]).split(",")[:2])
            fn = {"ProofSubmerge": world, "ProofPitLabel": lab, "ProofOverlays": ovs}.get(kw["method"])
            if fn is None:
                return {"success": False, "error": "No public static %s with 1 params." % kw["method"]}
            r = fn(x, z)
            return {"success": False, "error": r} if r.startswith(("No public static", "Type not found")) else {"result": r}
        return {"success": False, "error": "fake bridge: no tool " + tool}
    keep = O.call
    O.call = fake
    try:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "scene_plan.json")
            with open(p, "w") as fh:
                json.dump(plan, fh)
            with open(os.devnull, "w") as null:
                so, sys.stdout = sys.stdout, null
                try:
                    rc = O.main(["owner_look_regressions.py", d, "--plan", p])
                finally:
                    sys.stdout = so
            with open(os.path.join(d, "owner_look_regressions.json")) as fh:
                rows = [(r["row"], r["verdict"], r["got"]) for r in json.load(fh)]
    finally:
        O.call = keep
    return rc, rows


def fam_rows(rows, fam):
    return [r for r in rows if r[0].startswith(fam)]


def tally(rows):
    out = {}
    for r in rows:
        out[r[1]] = out.get(r[1], 0) + 1
    return out


def reader_checks(check):
    LB, OV = "OL_label_text_true_depth", "OL_overlays_hidden"
    ncopies = len(PLAN_OL["copies"])
    nov = ncopies * sum(1 for t in PLAN_OL["things"] if t[0] != "corpse")
    rc, good = run_main()
    lb, ov = fam_rows(good, LB), fam_rows(good, OV)
    check("readers, fixed world: %d label rows (want %d, one per copy) and %d overlay rows (want %d, corpses left out) all "
          "PASS; got %s / %s" % (len(lb), ncopies, len(ov), nov, tally(lb), tally(ov)),
          len(lb) == ncopies and len(ov) == nov and all(r[1] == "PASS" for r in lb + ov), [r for r in lb + ov if r[1] != "PASS"][:3])
    cells = sum(int(str(r[2]).split(" cells")[0].split()[-1]) for r in lb if " cells" in str(r[2]))
    check("readers, fixed world: label cells read %d (want %d = 16 a copy)" % (cells, 16 * ncopies), cells == 16 * ncopies,
          [r[2] for r in lb][:2])
    check("readers, fixed world: no BLOCKED row but none (got %s)" % sorted(r[0] for r in good if r[1] == "BLOCKED"),
          not [r for r in good if r[1] == "BLOCKED"])
    check("readers, fixed world: the exit is 2 only for the acts-off pour row (rc %d)" % rc,
          rc == 2 and [r[0] for r in good if r[1] != "PASS"] == ["OL_pour_never_no_room"], [r for r in good if r[1] != "PASS"][:3])
    # label faults: (fault, verdicts the label rows may read, copies that must FAIL)
    for fault, allowed, must_fail in (
            ("band", {"FAIL"}, None), ("off_notch", {"FAIL"}, None), ("vanilla", {"FAIL"}, None),
            # Python's "%.1f" (half-even on the binary value) misreads 39,000 dl (1.95 m) and 29,000 dl at sampled cells
            ("wrong_kind", {"PASS", "FAIL"}, {"BP6_tar"}), ("rounded_even", {"PASS", "FAIL"}, {"BP3", "BP6_tar"}),
            ("fogged", {"UNMEASURED"}, set()), ("refused", {"UNMEASURED"}, set()),
            ("floor_tail", {"PASS"}, set()), ("suffix_tail", {"PASS"}, set())):
        _rc, rows = run_main(label_fault=fault)
        r = fam_rows(rows, LB)
        failed = {x[0][len(LB) + 1:] for x in r if x[1] == "FAIL"}
        ok = len(r) == ncopies and {x[1] for x in r} <= allowed and (must_fail is None and len(failed) == ncopies
                                                                     or must_fail is not None and failed == must_fail)
        check("label fault %s: %d rows %s, FAIL copies %s (want %s)" % (fault, len(r), tally(r), sorted(failed),
              "all" if must_fail is None else sorted(must_fail)), ok, r[:2])
    _rc, rows = run_main(rect_fault="rect_unread")
    r = fam_rows(rows, LB)
    check("label: excavation_rect unreadable -> every label row UNMEASURED, never PASS (%s)" % tally(r),
          r and all(x[1] == "UNMEASURED" for x in r), r[:2])
    for fault in ("no_method", "type_missing"):
        _rc, rows = run_main(label_fault=fault)
        r = fam_rows(rows, LB)
        check("label reader missing (%s) -> one row %s BLOCKED, never PASS (%s)" % (fault, LB, [(x[0], x[1]) for x in r]),
              [(x[0], x[1]) for x in r] == [(LB, "BLOCKED")], r[:2])
    # overlay faults: (fault, verdicts allowed, (copy, def) rows that must FAIL; None = some FAIL in every wet copy)
    wet_keys = {k for k, _x, _z, f, _fl in PLAN_OL["copies"] if f}
    for fault, allowed, must in (
            ("icon_whole", {"PASS", "FAIL"}, {("BP3", "TorchLamp"), ("BP3", "Steel"), ("BP5_brim", "Bed"), ("BP6_tar", "Steel"),
                                              ("BP1", "Steel")}),
            ("faded_not_hidden", {"PASS", "FAIL"}, {("BP3", "TorchLamp"), ("BP5_brim", "Bed"), ("BP5_brim", "TableButcher")}),
            ("hidden_dry", {"PASS", "FAIL"}, {("BP0_dry", "Bed"), ("BP0_dry", "TorchLamp")}),
            ("hidden_high", {"PASS", "FAIL"}, {("BP1", "SculptureGrand"), ("BP1", "TorchLamp"), ("BP1", "TableButcher")}),
            ("flame_shows", {"PASS", "FAIL"}, {("BP3", "TorchLamp"), ("BP5_brim", "TorchLamp"), ("BP6_tar", "TorchLamp")}),
            ("flame_out_dry", {"PASS", "FAIL"}, {("BP0_dry", "TorchLamp")}),
            ("cords_dry", {"PASS", "FAIL"}, {(k, "Bed") for k in wet_keys - {"BP6_tar"}})):
        _rc, rows = run_main(ov_fault=fault)
        r = fam_rows(rows, OV)
        failed = {(x[0][len(OV) + 1:].split("_" + kd + "_")[0], x[0].split("_" + kd + "_")[1])
                  for x in r if x[1] == "FAIL" for kd in ("furn", "item", "mini") if "_" + kd + "_" in x[0]}
        check("overlay fault %s: %d rows %s; must-FAIL rows missed %s" % (fault, len(r), tally(r), sorted(must - failed)),
              len(r) == nov and {x[1] for x in r} <= allowed and must <= failed, [x for x in r if x[1] == "FAIL"][:2])
    for fault in ("refused", "missing_def", "garbled"):
        _rc, rows = run_main(ov_fault=fault)
        r = fam_rows(rows, OV)
        check("overlay read unusable (%s) -> every overlay row UNMEASURED, never PASS (%d rows %s)" % (fault, len(r), tally(r)),
              len(r) == nov and all(x[1] == "UNMEASURED" for x in r), r[:2])
    _rc, rows = run_main(world_fault="old_build")
    r = fam_rows(rows, OV)
    check("overlays with ProofSubmerge refusing (the law unread) -> no overlay row PASS in a wet copy (%s)" % tally(r),
          r and all(x[1] != "PASS" for x in r if "_BP0_" not in x[0]), [x for x in r if x[1] == "PASS"][:2])
    for fault in ("no_method", "type_missing"):
        _rc, rows = run_main(ov_fault=fault)
        r = fam_rows(rows, OV)
        check("overlay reader missing (%s) -> one row %s BLOCKED, never PASS (%s)" % (fault, OV, [(x[0], x[1]) for x in r]),
              [(x[0], x[1]) for x in r] == [(OV, "BLOCKED")], r[:2])
    label_sweep(check)
    overlay_sweep(check)


def label_sweep(check):
    """Every label the law can print for a dug cell: hole 1..40 notches (0.5..20 m) x water 0..brim in 125 dl steps (so
    every x.x5 tie and every 0.05 m step) plus the thin films 1, 99, 100, 101, 999, 1000 dl, water and tar. The script's
    expected text must equal the integer oracle; the true line (with each tail) must PASS; the line a notch or 0.1 m off,
    or with the other liquid, must FAIL. Left out: d > 40 (no pit stage digs past 8; the format is the same) and an
    unrecorded fluid (judge_labels falls back to the plan's)."""
    want_of, judge = getattr(O, "pit_label_want", None), getattr(O, "judge_pit_label", None)
    if want_of is None or judge is None:
        check("label sweep: the script has pit_label_want and judge_pit_label", False, "missing")
        return
    n = wrong_text = pass_bad = fail_bad = 0
    first = []
    for d in range(1, 41):
        dls = sorted(set(range(0, d * 10000 + 1, 125)) | {1, 99, 100, 101, 999, 1000})
        for dl in dls:
            for fl in ("RM_Fluid_Water", "RM_Fluid_Tar"):
                n += 1
                word = WORD[fl]
                o = oracle_label(d, dl, word)
                w = want_of(d, dl, fl if dl > 0 else None, None)
                if w != o:
                    wrong_text += 1
                    first.append(("text", d, dl, fl, w, o))
                    continue
                for tail in (" (Walk speed 100%)", " · Wood floor (Walk speed 100%)", " — Hole", ""):
                    if judge("line=" + o + tail, w)[0] != "PASS":
                        pass_bad += 1
                        first.append(("pass", d, dl, o + tail))
                bads = [oracle_label(d + 1, dl, word), oracle_label(d - 1, dl, word) if d > 1 else None,
                        oracle_label(d, dl + 2000, word), oracle_label(d, dl - 2000, word) if dl >= 2000 else None,
                        oracle_label(d, dl, "water" if word == "tar" else "tar") if dl > 0 else None, "vanilla"]
                for b in bads:
                    if b is not None and b != o and judge("line=" + b + " (Walk speed 100%)", w)[0] != "FAIL":
                        fail_bad += 1
                        first.append(("fail", d, dl, b))
    check("label sweep: %d cases; wrong expected text %d, true line not PASS %d, wrong line not FAIL %d (worst %d, limit 0)"
          % (n, wrong_text, pass_bad, fail_bad, max(wrong_text, pass_bad, fail_bad)),
          n > 100000 and not (wrong_text or pass_bad or fail_bad), first[:3])
    for reply, v in (("fogged", "UNMEASURED"), ('REFUSED: need a current map and "x,z"', "UNMEASURED"), ("", "UNMEASURED"),
                     ("{'success': False, 'error': 'timeout'}", "UNMEASURED")):
        check("label judge: reply %r -> %s" % (reply[:30], v), judge(reply, "Pit, 4.0 m deep")[0] == v, judge(reply, "Pit, 4.0 m deep"))


def overlay_sweep(check):
    """The overlay law over its regimes: height 0.3..3 m (the planned goods to the grand sculpture) x level 0..8 m in
    0.5 m notches and at 0.01 m either side of each band edge x clarity 0 (tar), 0.2, 0.45, 0.9, 1. The law's value must
    PASS; an icon drawn whole where the law draws it at under 1, or hidden where the law shows it, must FAIL, except
    within OV_EDGE of a band edge (both neighbours accepted: the printed F2 level and height cannot place it). Left out:
    corpses and pawns (their two readers use different heights) and multi-thing cells (one planned thing per cell)."""
    judge = getattr(O, "judge_overlay", None)
    if judge is None:
        check("overlay sweep: the script has judge_overlay", False, "missing")
        return
    edge = getattr(O, "OV_EDGE", 0.0)
    n = pass_bad = fail_bad = at_edge = 0
    first = []
    for h in (0.3, 0.75, 0.8, 1.0, 1.2, 2.0, 3.0):
        levels = {k * 0.5 for k in range(17)}
        for e in (h * 0.5, h + 0.5):
            levels |= {round(e - 0.01, 4), round(e + 0.01, 4), e}
        for lv in sorted(levels):
            for c in (0.0, 0.2, 0.45, 0.9, 1.0):
                n += 1
                share = 0.0 if lv <= 0 else min(1.0, lv / h)
                lab = (0.0 if toy_seen(c, lv - h) < 0.05 else toy_seen(c, lv - h)) if share > 0 else 1.0
                kv = O.kv_of("def=Bed kind=building depth=16 level=%.2f share=%.3f clarity=%.3f seenFoot=%.3f height=%.2f "
                             "label=%.3f" % (lv / 0.5, share, c, toy_seen(c, lv) if share > 0 else 1.0, h, lab))
                rt = "whole" if share <= 0 else "hidden" if lab <= 0 else "split"
                a = law_overlay(c, lv, h)
                cords = toy_seen(c, lv) if lv > 0 else 1.0

                def text(alpha):
                    return "def=Bed id=1 realtime=%s share=%.3f flame=none overlay=%.3f\ncords=%.3f" % (
                        rt, 0.0 if rt == "hidden" else share, alpha, cords)
                if judge(kv, text(a), "Bed")[0] != "PASS":
                    pass_bad += 1
                    first.append(("pass", h, lv, c, a, judge(kv, text(a), "Bed")))
                near = lv > 0 and (abs(lv - h * 0.5) <= edge or abs(lv - h - 0.5) <= edge)
                for wrong in ((1.0,) if a < 0.95 else ()) + ((0.0,) if a > 0.06 else ()):
                    if near:
                        at_edge += 1
                    elif judge(kv, text(wrong), "Bed")[0] != "FAIL":
                        fail_bad += 1
                        first.append(("fail", h, lv, c, a, wrong))
    check("overlay sweep: %d cases; law value not PASS %d, wrong icon not FAIL %d (worst %d, limit 0); %d wrong icons at "
          "a band edge within OV_EDGE %.3f m accepted (limit OV_EDGE < 0.01, the probes' offset)" % (
              n, pass_bad, fail_bad, max(pass_bad, fail_bad), at_edge, edge),
          # the excuse must stay inside the sweep's own probes: at 0.01 m from an edge a wrong icon must already FAIL
          n > 500 and not pass_bad and not fail_bad and 0 < edge < 0.01, first[:3])
    # flame and cords
    kvu = O.kv_of("def=TorchLamp kind=building depth=16 level=4.00 share=1.000 clarity=0.450 seenFoot=0.600 height=1.20 label=0.700")
    check("flame: top 0.8 m under and the flame shows -> FAIL",
          judge(kvu, "def=TorchLamp id=1 realtime=split share=1.000 flame=shows overlay=0.000\ncords=0.600", "TorchLamp")[0] == "FAIL")
    check("flame: top 0.8 m under and the flame out -> PASS",
          judge(kvu, "def=TorchLamp id=1 realtime=split share=1.000 flame=out overlay=0.000\ncords=0.600", "TorchLamp")[0] == "PASS")
    check("cords: a wet cell's cords at 1 (rope drawn whole over the water) -> FAIL",
          judge(kvu, "def=TorchLamp id=1 realtime=split share=1.000 flame=out overlay=0.000\ncords=1.000", "TorchLamp")[0] == "FAIL")
    check("realtime: whole for a thing half under -> FAIL",
          judge(kvu, "def=TorchLamp id=1 realtime=whole share=0.000 flame=out overlay=0.000\ncords=0.600", "TorchLamp")[0] == "FAIL")
    check("overlay read of another def only -> UNMEASURED",
          judge(kvu, "def=Steel id=1 realtime=split share=1.000 flame=none overlay=0.000\ncords=0.600", "TorchLamp")[0] == "UNMEASURED")


def main():
    bad = 0

    def check(name, ok, got=""):
        nonlocal bad
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(got)[:300]))
        bad += not ok

    good = O.judge_scene(PLAN, toy_world(), toy_here())
    fails = [r for r in good if r[1] != "PASS"]
    check("fixed world: every scene row PASS (%d rows)" % len(good), not fails, fails[:4])
    want = {"OL_buildings_covered", "OL_goods_covered", "OL_corpses_covered", "OL_opaque_hides", "OL_no_surface_shadow",
            "OL_labels_fade", "OL_one_law_over_fill"}
    check("fixed world: every row family is exercised", families(good, "PASS") == want, families(good, "PASS"))
    # each planted fault reds its own family (and the build he saw reds the three he named)
    for fault, fam in (("old_build", {"OL_buildings_covered", "OL_goods_covered", "OL_corpses_covered"}),
                       ("corpse_refused", {"OL_corpses_covered"}), ("goods_dry", {"OL_goods_covered"}),
                       ("tar_seen", {"OL_opaque_hides"}), ("shadow_faded", {"OL_no_surface_shadow"}),
                       ("shadow_lost", {"OL_no_surface_shadow"}), ("shadow_over_sheet", {"OL_no_surface_shadow"}),
                       ("label_bright", {"OL_labels_fade"}), ("non_monotone", {"OL_one_law_over_fill"})):
        red = families(O.judge_scene(PLAN, toy_world(fault), toy_here()), "FAIL")
        check("planted %s goes red in %s" % (fault, sorted(fam)), fam <= red, red)
    # "nothing drawn" is FAIL only for a thing the presence read finds at its cell (visit 2: absent goods read FAIL)
    minis = [(k, d) for k, _k2, d, _s, _ij, _n in PLAN["things"] if k == "mini"]
    ab = O.judge_scene(PLAN, toy_world("old_build"), toy_here(absent=set(minis)))
    gm = [r for r in ab if r[0].startswith("OL_goods_covered_") and "_mini_" in r[0] and "_BP0_" not in r[0]]
    check("planted old_build with the minified goods absent: their rows UNMEASURED, never FAIL (%d rows)" % len(gm),
          gm and all(r[1] == "UNMEASURED" and "not at" in r[2] for r in gm), gm[:3])
    check("planted old_build with the minified goods absent: the present things still FAIL",
          {"OL_buildings_covered", "OL_corpses_covered"} <= families(ab, "FAIL"), families(ab, "FAIL"))
    for why, here in (("no presence reader", None), ("presence unreadable", lambda x0, z0: None)):
        nr = O.judge_scene(PLAN, toy_world("old_build"), here)
        cov = [r for r in nr if "_covered_" in r[0] and "_BP0_" not in r[0]]
        check("planted old_build, %s: no covered row FAIL or PASS (%d rows)" % (why, len(cov)),
              cov and all(r[1] == "UNMEASURED" for r in cov), sorted({r[1] for r in cov}))
    pa = O.present_at
    check("presence: a minified good reads MinifiedThing, a corpse Corpse_*, a building its own def",
          pa([{"def": "MinifiedThing", "x": 3, "z": 4}], "mini", "Armchair", 3, 4) is True
          and pa([{"def": "Corpse_Human", "x": 3, "z": 4}], "corpse", "Villager", 3, 4) is True
          and pa([{"def": "Bed", "x": 3, "z": 4}], "furn", "Bed", 3, 4) is True)
    check("presence: another def at the cell, or the def one cell over, is absent; unread is None",
          pa([{"def": "Steel", "x": 3, "z": 4}], "furn", "Bed", 3, 4) is False
          and pa([{"def": "Bed", "x": 4, "z": 4}], "furn", "Bed", 3, 4) is False
          and pa([], "mini", "Armchair", 3, 4) is False and pa(None, "furn", "Bed", 3, 4) is None)
    # sweep: 4 read classes x 5 presence states x 4 kinds (80 cases). Only a "nothing drawn" read over a dug cell with the
    # planned thing present may FAIL; a real reply is never re-classed by presence; every other pair is UNMEASURED.
    # Left out: multi-thing cells (the stage plans one thing per cell) and partial list_things pages (limit 2000 > 256 cells).
    reads = {"drawn": "def=Bed kind=building share=0.500", "nothing": "REFUSED: nothing drawn under liquid at 3,4 (depth=8 waterM=1)",
             "no_pit": "REFUSED: nothing drawn under liquid at 3,4 (depth=0 waterM=0)", "no_map": "REFUSED: need a current map"}
    sweep_bad, n = [], 0
    for kind, dn, fake in (("furn", "Bed", "Bed"), ("item", "Steel", "Steel"), ("mini", "Armchair", "MinifiedThing"),
                           ("corpse", "Villager", "Corpse_Human")):
        for pres, here in (("present", lambda a, b, d=fake: [{"def": d, "x": 3, "z": 4}]), ("absent", lambda a, b: []),
                           ("other", lambda a, b: [{"def": "Plant_Grass", "x": 3, "z": 4}]), ("unread", lambda a, b: None),
                           ("noreader", None)):
            for rc, text in reads.items():
                n += 1
                kv = O.kv_of(text)
                vac = O.vacuous(text, kv) or O.judge_absent(text, kv, here, 0, 0, kind, dn, 3, 4)
                want_judged = rc == "drawn" or (rc == "nothing" and pres == "present")
                if bool(vac) == want_judged:
                    sweep_bad.append((kind, pres, rc, vac))
    check("sweep: judged only when drawn, or 'nothing drawn' with the thing present (%d cases, %d wrong)" % (n, len(sweep_bad)),
          n == 80 and not sweep_bad, sweep_bad[:4])
    # the floor shadow (11-12 design: its own alpha UNDER the sheet, owner 11-13 "transparent to them as usual")
    sh = [r for r in good if r[0].startswith("OL_no_surface_shadow_BP3_")]
    check("shadow under the sheet in clear water at the dry alpha -> PASS", sh and all(r[1] == "PASS" for r in sh), sh[:3])
    over = [r for r in O.judge_scene(PLAN, toy_world("shadow_over_sheet"), toy_here()) if r[0].startswith("OL_no_surface_shadow")]
    check("planted shadow over the sheet -> its per-thing rows FAIL",
          any(r[0].startswith("OL_no_surface_shadow_BP3_") and r[1] == "FAIL" for r in over), over[:3])
    noq = O.judge_scene(PLAN, toy_world(queue=None), toy_here())
    check("no shadowQueue in the reply (the shipped reader's): no row waits on it, every row PASS",
          noq and not [r for r in noq if r[1] != "PASS"], [r for r in noq if r[1] != "PASS"][:3])
    check("tar: a shadow seen through it -> FAIL",
          O.judge_shadow(O.kv_of("def=Bed kind=building share=1 clarity=0.000 shadow=0.300"), True)[0] == "FAIL")
    # labels (RM_UnderLiquid.LabelAlpha: a label fades with its TOP; a top at the line is seen whole)
    jl = O.judge_label
    check("label: top exactly at the line, label 1 -> PASS",
          jl(O.kv_of("share=1.000 clarity=0.450 level=2.00 height=1.00 label=1.000"))[0] == "PASS")
    tb = [r for r in good if r[0] == "OL_labels_fade_BP3_furn_TableButcher"]
    check("scene: TableButcher's top at the BP3 line reads PASS", tb and tb[0][1] == "PASS", tb)
    check("label: 1 m over the top in clear water at full brightness -> FAIL",
          jl(O.kv_of("share=1.000 clarity=0.450 level=4.00 height=1.00 label=1.000"))[0] == "FAIL")
    check("label: under tar over the top but still shown -> FAIL",
          jl(O.kv_of("share=1.000 clarity=0.000 level=4.00 height=1.00 label=0.300"))[0] == "FAIL")
    # vacuous reads are UNMEASURED, never FAIL or PASS
    for why, reply in (("no map", 'REFUSED: need a current map and "x,z"'),
                       ("no engine", "REFUSED: cell off the map or no excavation engine"),
                       ("no pit cell", "REFUSED: nothing drawn under liquid at 3,3 (depth=0 waterM=0.0000)"),
                       ("thing not in a pit", "def=Bed class=X kind=building rot=0 depth=0 level=0.00 share=0.000 "
                                              "clarity=0.000 seenLine=1 seenFoot=1 height=0.80 shadow=- label=1.000")):
        rv = O.judge_scene(PLAN, lambda x, z, reply=reply: reply, toy_here())
        check("vacuous read (%s) -> every row UNMEASURED" % why, rv and all(r[1] == "UNMEASURED" for r in rv),
              sorted({r[1] for r in rv}))
    rv = O.judge_scene({"copies": [], "things": []}, lambda x, z: "")
    check("empty plan -> one UNMEASURED row, not an empty PASS", [r[1] for r in rv] == ["UNMEASURED"], rv)
    # the dry copy never reds a covered row on share 0
    dry = [r for r in good if "_BP0_dry_" in r[0]]
    check("dry copy: covered rows PASS on share 0", dry and all(r[1] == "PASS" for r in dry), dry[:3])
    # pour (owner 20:49: "No Room" ... "It should go ahead and overflow")
    check("pour: OK with overflow is PASS", O.judge_pour("OK poured 1,000 L into a pit of 36 squares; 1,000 L overflowed onto the ground")[0] == "PASS")
    check("pour: a refusal for room is FAIL", O.judge_pour("REFUSED: No room")[0] == "FAIL")
    check("pour: OK that kept a remainder for room is FAIL",
          O.judge_pour("OK poured 0 L into a pit of 36 squares; 1,000 L had no room")[0] == "FAIL")
    # screenshot mode (owner 18:15: "no longer allowing me to select objects at all")
    js = O.judge_screenshot
    check("screenshot: off before and after PASS", js({"activeBefore": False}, {"activeBefore": False})[0] == "PASS")
    check("screenshot: left on before the run FAIL", js({"activeBefore": True}, {"activeBefore": False})[0] == "FAIL")
    check("screenshot: still on at the end FAIL", js({"activeBefore": False}, {"activeAfter": True})[0] == "FAIL")
    check("screenshot: unreadable is UNMEASURED, never PASS", js({"success": False}, {})[0] == "UNMEASURED")
    # a refused read is FAIL for a planned thing (drawn whole), a wrong first thing is UNMEASURED, never PASS
    check("refused read -> FAIL", O.judge_covered(O.kv_of("REFUSED: nothing drawn"), "building", True, "Bed")[0] == "FAIL")
    check("other thing first at the cell -> UNMEASURED",
          O.judge_covered(O.kv_of("def=Steel kind=item share=1.000"), "building", True, "Bed")[0] == "UNMEASURED")
    # BLOCKED rows keep the run from reading PASS
    rows = good + O.blocked_rows()
    check("blocked hooks make the exit 2, not 0", O.exit_code(rows) == 2 and O.exit_code(good) == 0)
    check("a FAIL makes the exit 1", O.exit_code(rows + [("x", "FAIL", "")]) == 1)
    reader_checks(check)
    print("selftest_owner_look_regressions: %s (%d bad)" % ("PASS" if not bad else "FAIL", bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
