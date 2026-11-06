#!/usr/bin/env python3
"""selftest_flyer_wing_designs.py - every flyer whose static draws no wing (G3) has a wing design (THOZZIK_REDRAW_WINGS_FLIES_WITHOUT_THEM).

  DESIGNS  each flyer_gate.NO_WINGS_DRAWN def has a complete design in design/RimMandrake/flyer_wing_designs.json;
           a planted design missing its folded clause, a pose or a facing is caught by name, and a G3 def with no
           design at all is caught
  PROMPTS  `wingprompt` renders a study 3.3 master (folded clause, roots, flat light) and a 3.4 layer (pose, wings
           only, transparent) for every facing and pose; an undesigned def refuses
  QUEENS   RM_ThozzikQueen / RM_ThozzikColonyQueen are not G3-failed, in the gate or in the committed plan (their
           static draws wings), while the worker Thozzik still is
  STRILL   the Strill design is the owner's (2026-10-17): six legs, gliding membranes between them, four ears, whip tail
"""
from __future__ import annotations

import copy
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_gate as FG  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def main() -> int:
    designs = FG.wing_designs()
    check(not FG.wing_design_gaps(), f"DESIGNS every G3 def designed: {FG.wing_design_gaps() or 'none missing'}")
    check(set(FG.NO_WINGS_DRAWN) <= set(designs), "DESIGNS cover NO_WINGS_DRAWN")
    # sanity: the validator can see a hole
    for field, sub in (("folded", None), ("poses", "down"), ("facings", "north")):
        d = copy.deepcopy(designs)
        x = d["RM_Thozzik"] = copy.deepcopy(d["RM_Thozzik"])
        if sub:
            x[field].pop(sub)
        else:
            x.pop(field)
        gaps = FG.wing_design_gaps(d)
        check(any(g.startswith("RM_Thozzik") and (sub or field) in g for g in gaps), f"DESIGNS planted hole {field}/{sub} caught: {gaps}")
    check(FG.wing_design_gaps({}, ["RM_Planted"]) == ["RM_Planted: G3 and no wing design"], "DESIGNS undesigned G3 def caught")

    for name in FG.NO_WINGS_DRAWN:
        for f in FG.FACINGS:
            m = FG.wing_prompt(name, f, "master")
            check(designs[name]["folded"] in m and "Wing roots clearly visible" in m and "no cast shadow" in m
                  and designs[name]["facings"][f] in m, f"PROMPTS {name} {f} master")
            for w in FG.WING_POSES:
                lp = FG.wing_prompt(name, f, w)
                check(designs[name]["poses"][w] in lp and "ONLY its wings" in lp and "fully transparent" in lp,
                      f"PROMPTS {name} {f} {w}")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = FG.main(["wingprompt", "RSW_Strill", "east", "level"])
    check(rc == 0 and "membranes taut" in buf.getvalue(), "PROMPTS cli wingprompt prints the layer prompt")
    try:
        FG.wing_prompt("RM_NotAFlyer", "east", "master")
        check(False, "PROMPTS undesigned def refuses")
    except SystemExit as e:
        check("no wing design" in str(e), "PROMPTS undesigned def refuses")

    plan = FG.plan_rows()
    for q in ("RM_ThozzikQueen", "RM_ThozzikColonyQueen"):
        check(q not in FG.NO_WINGS_DRAWN, f"QUEENS {q} not G3 in the gate")
        check(not any(x.startswith("G3") for x in plan[q]["static_fails"]), f"QUEENS {q} not G3 in the plan")
    check("G3 no wings drawn" in plan["RM_Thozzik"]["static_fails"] and "RM_Thozzik" in FG.NO_WINGS_DRAWN,
          "QUEENS the worker Thozzik is still G3 (instrument can see)")

    s = designs["RSW_Strill"]
    text = " ".join([s["look"], s["wings"], s["folded"], s["why_wings"]]).lower()
    check(all(k in text for k in ("six", "four ears", "whip", "glide")) and "Six legs.  Gliding flyers." in s["why_wings"],
          "STRILL six legs, four ears, whip tail, glide membranes, owner words carried")
    print(f"{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
