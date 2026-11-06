#!/usr/bin/env python3
"""selftest_flight_reroll_route.py - an art-eval flight reroll never reaches artpipe as a whole creature
(ARTEVAL_FLIGHT_HARDEN_REROLLS_SKIP_BODY_LOCK).

  REFUSE   fill_queue refuses the committed shirrel_flight_w86 reroll row (arteval_RM_Shirrel__flight_cut4_r1, a
           whole-creature prompt on the body texPath) and a flight_cut2 id; a body reroll and a FleetFlier id pass
  LAYERED  runner.regen_jobs turns a flight REGEN with a wing design and an accepted master into 3x3 wing-layer rows:
           plan, derive_from, flyer_gate.wing_prompt prompt, flip-book acceptance named; each passes the gate and
           row_to_jobs files it
  HELD     the real Shirrel record (no wing design, no master) yields one row that keeps no plan and is refused
  ROUND    a round candidate (r2) of a flight record is held with a flight id; fauna_drive leaves such rows alone
  BODY     a static body REGEN of the same def is untouched (one row, no plan, no layer)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
import runner as RN  # noqa: E402
import fill_queue as F  # noqa: E402

RUN = REPO / "infrastructure/state/art_eval/runs/shirrel_flight_w86"
fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


def refused(row) -> bool:
    try:
        F._refuse_unlocked_frames(row)
        return False
    except ValueError as ex:
        return "wing layer" in str(ex) and "flyer_gate.py flipbook" in str(ex)


def main() -> int:
    check("runner and fill_queue share one flight pattern", RN.FLIGHT_TOKEN.pattern == F.FLIGHT_FRAME.pattern)
    old = json.loads((RUN / "regen_jobs.json").read_text())[0]
    check("REFUSE committed whole-creature flight reroll row", old["id"].endswith("__flight_cut4_r1") and refused(old))
    check("REFUSE flight_cut2 id", refused({"id": "arteval_RM_Shirrel__flight_cut2_r1", "target_texpath": "a/RM_Shirrel"}))
    check("REFUSE _Flying_ frames still", refused({"id": "x", "target_texpath": "a/X_Flying_2"}))
    for rid in ("arteval_RM_Shirrel_r2", "arteval_RUT_FleetFlier_r1", "arteval_RM_Shirrel__B_r1"):
        check(f"REFUSE body id {rid} passes", not refused({"id": rid, "target_texpath": "a/RM_Shirrel"}))

    rec = json.loads((RUN / "decisions.jsonl").read_text().splitlines()[0])
    check("record is a flight record", rec["decision"] == "REGEN" and RN.is_flight_record(rec))
    tp = lambda d: f"Things/Pawn/Animal/{d}/{d}"   # noqa: E731
    held = RN.regen_jobs([rec], "t", texpath_of=tp, neutralize=lambda p: (_ for _ in ()).throw(AssertionError("rewrite")))
    check("HELD one row, no plan", len(held) == 1 and not held[0].get("plan") and not held[0].get("derive_from"))
    check("HELD row refused at filing", refused(held[0]))
    check("HELD says what is owed", "no wing design" in held[0]["style_notes"] and "no accepted body master" in held[0]["style_notes"])

    strill = dict(rec, subject="RSW_Strill", candidate="flight_cut1", derive_from="arteval_RSW_Strill_master_east")
    rows = RN.regen_jobs([strill], "t", texpath_of=tp)
    check("LAYERED 9 rows", len(rows) == 9 and len({r["id"] for r in rows}) == 9)
    check("LAYERED plan + master", all(r["plan"] == "glider" and r["derive_from"] == "arteval_RSW_Strill_master_east" for r in rows))
    check("LAYERED wing prompts", all(r["prompt"].startswith("Attached: the accepted body master of the strill")
                                      and "Draw ONLY its wings" in r["prompt"] for r in rows))
    check("LAYERED one facing per row", sorted({tuple(r["facings"]) for r in rows}) == [("east",), ("north",), ("south",)])
    check("LAYERED flip-book acceptance named", all("flyer_gate.py flipbook" in r["style_notes"] for r in rows))
    check("LAYERED passes the flight gate", not any(refused(r) for r in rows))
    try:
        jobs = F.row_to_jobs(dict(rows[0], biome_neutral=True), derive_facings=False, no_subject="selftest fixture")
        check("LAYERED row_to_jobs files it", bool(jobs) and all(j.get("derive_from") == strill["derive_from"] for j in jobs))
    except (ValueError, SystemExit) as ex:
        check(f"LAYERED row_to_jobs files it ({ex})", False)
    nomaster = RN.regen_jobs([dict(strill, derive_from="")], "t", texpath_of=tp)
    check("HELD no master: refused", len(nomaster) == 1 and refused(nomaster[0]))

    # a ROUND candidate (r2) of a flight subject: its id has no flight word of its own, the held row must gain one
    rnd = RN.regen_jobs([dict(rec, candidate="r2", round=2)], "t", texpath_of=tp, rs={})
    check("HELD round candidate refused", len(rnd) == 1 and "flight" in rnd[0]["id"] and refused(rnd[0]))
    check("FAUNA_DRIVE keeps flight rows", all(RN.is_flight_row(r) for r in rows + held + rnd))

    body = {k: v for k, v in rec.items() if k not in ("candidate", "artpipe_job", "source_files")}
    b = RN.regen_jobs([dict(body, artpipe_job="RM_Shirrel_east")], "t", texpath_of=tp, neutralize=lambda p: (p, "noop"))
    check("BODY untouched", len(b) == 1 and not RN.is_flight_row(b[0]) and not b[0].get("plan") and not refused(b[0]) and "layered" not in b[0]["style_notes"])

    print(f"{'FAIL' if fails else 'PASS'} selftest_flight_reroll_route ({len(fails)} failed)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
