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
               ["corpse", "corpse:0:Villager", "Villager", "Core", [10, 10], 1]],
}
HEIGHT = {"Bed": 0.8, "SculptureGrand": 3.0, "Steel": 0.3, "MinifiedThing": 0.75, "Corpse_Human": 0.3}
KIND = {"furn": "building", "item": "item", "mini": "minified", "corpse": "corpse"}


def toy_world(fault=None):
    """-> proof(x, z) for PLAN under a toy law (clarity 0.45 water, 0 tar; Seen = 1 - 0.5*(1 - c^(m + 0.35)))."""
    at = {}
    for key, x0, z0, f, fl, kind, dn, x, z in O.plan_rows(PLAN):
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
        shadow = 0.30 * seen(c, lv) if kind == "furn" else None
        if fault == "shadow_dry_alpha" and kind == "furn" and f > 0:
            shadow = 0.30
        label = (0.0 if seen(c, lv - h) < 0.05 else seen(c, lv - h)) if share > 0 else 1.0
        if fault == "label_bright" and share >= 1.0:
            label = 1.0
        return ("def=%s class=X kind=%s rot=0 depth=8 fill=%d level=%.2f share=%.3f clarity=%.3f seenLine=%.3f "
                "seenFoot=%.3f printedLevel=- setting=on height=%.2f shadow=%s label=%.3f liquid=- tint=0.05,0.05,0.05"
                % (dn, KIND[kind], f, f, share, c, sl, sf, h, "-" if shadow is None else "%.3f" % shadow, label))
    return proof


def families(rows, verdict):
    out = set()
    for name, v, _ in rows:
        if v == verdict:
            out.add(next(f for f in ("OL_buildings_covered", "OL_goods_covered", "OL_corpses_covered", "OL_opaque_hides",
                                     "OL_no_surface_shadow", "OL_labels_fade", "OL_one_law_over_fill") if name.startswith(f)))
    return out


def main():
    bad = 0

    def check(name, ok, got=""):
        nonlocal bad
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(got)[:300]))
        bad += not ok

    good = O.judge_scene(PLAN, toy_world())
    fails = [r for r in good if r[1] != "PASS"]
    check("fixed world: every scene row PASS (%d rows)" % len(good), not fails, fails[:4])
    want = {"OL_buildings_covered", "OL_goods_covered", "OL_corpses_covered", "OL_opaque_hides", "OL_no_surface_shadow",
            "OL_labels_fade", "OL_one_law_over_fill"}
    check("fixed world: every row family is exercised", families(good, "PASS") == want, families(good, "PASS"))
    # each planted fault reds its own family (and the build he saw reds the three he named)
    for fault, fam in (("old_build", {"OL_buildings_covered", "OL_goods_covered", "OL_corpses_covered"}),
                       ("corpse_refused", {"OL_corpses_covered"}), ("goods_dry", {"OL_goods_covered"}),
                       ("tar_seen", {"OL_opaque_hides"}), ("shadow_dry_alpha", {"OL_no_surface_shadow"}),
                       ("label_bright", {"OL_labels_fade"}), ("non_monotone", {"OL_one_law_over_fill"})):
        red = families(O.judge_scene(PLAN, toy_world(fault)), "FAIL")
        check("planted %s goes red in %s" % (fault, sorted(fam)), fam <= red, red)
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
    print("selftest_owner_look_regressions: %s (%d bad)" % ("PASS" if not bad else "FAIL", bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
