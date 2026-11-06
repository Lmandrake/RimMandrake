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
  DRIVE    fauna_drive.cmd_rows run for real on a runs file holding the layered, held and round flight rows plus a body
           row, with a spec and an owner prompt present: the body row is re-id'd and owner-prompted (the drive ran),
           every flight row keeps its _flight id, wing prompt, plan and derive_from, and the held rows are still
           refused by fill_queue.row_to_jobs
  BODY     a static body REGEN of the same def is untouched (one row, no plan, no layer)
"""
from __future__ import annotations

import argparse
import copy
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
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


def drive_fauna(layered, held_rows):
    """Run fauna_drive.cmd_rows (not a stand-in) on a temp runs file; only its ledger/state readers are stubbed."""
    import fauna_drive as FD
    import round_series as RS
    body_row = {"id": "arteval_RM_Shirrel_bodyprobe", "target_def": "RM_Shirrel", "prompt": "a shirrel, whole body",
                "target_texpath": "Things/Pawn/Animal/RM_Shirrel/RM_Shirrel", "style_notes": "", "facings": ["east"]}
    src = copy.deepcopy(layered + held_rows) + [body_row]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        run = td / "infrastructure/state/art_eval/runs/flightprobe"
        run.mkdir(parents=True)
        (run / "regen_jobs.json").write_text(json.dumps(src))
        specs = td / "specs"
        specs.mkdir()
        for d in ("RM_Shirrel", "RSW_Strill"):
            (specs / f"{d}.spec.json").write_text(json.dumps({"subject": d, "label": d[4:].lower(),
                                                               "size": {"drawSize": [1.4, 1.4]}}))
        owner = {d: {"text": "OWNERPROBE a plain sandy creature standing", "source": "selftest"}
                 for d in ("RM_Shirrel", "RSW_Strill")}
        saved = (FD.ROOT, RS.resets, RS.regen_counts, RS.owner_prompts, FD.production, FD.bind_texpath)
        FD.ROOT = td
        RS.resets = lambda *a, **k: {}
        RS.regen_counts = lambda *a, **k: {}
        RS.owner_prompts = lambda *a, **k: owner
        FD.production = lambda: []
        FD.bind_texpath = lambda r, texpath_of=None: r
        out = td / "rows.json"
        try:
            with redirect_stdout(io.StringIO()):
                FD.cmd_rows(argparse.Namespace(runs=["flightprobe"], specs=str(specs), out=str(out), file=False,
                                               only=None))
        finally:
            FD.ROOT, RS.resets, RS.regen_counts, RS.owner_prompts, FD.production, FD.bind_texpath = saved
        got = json.loads(out.read_text())
    probe = [r for r in got if r.get("target_texpath") == body_row["target_texpath"] and "OWNERPROBE" in r.get("prompt", "")
             and "plan" not in r]
    check("DRIVE sanity: body row re-id'd and owner-prompted by cmd_rows",
          len(probe) == 1 and probe[0]["id"] != body_row["id"] and probe[0]["id"].startswith("arteval_RM_Shirrel_"))
    flight = [r for r in got if r is not None and r not in probe]
    want = layered + held_rows
    check("DRIVE every flight row written", len(flight) == len(want))
    check("DRIVE flight ids keep _flight_ and stay distinct",
          [r["id"] for r in flight] == [r["id"] for r in want] and len({r["id"] for r in flight}) == len(want)
          and all("flight" in r["id"] for r in flight))
    check("DRIVE wing prompts not overwritten by owner/neutral prompt",
          [r["prompt"] for r in flight] == [r["prompt"] for r in want] and not any("OWNERPROBE" in r["prompt"] for r in flight))
    check("DRIVE plan and derive_from kept",
          [(r.get("plan"), r.get("derive_from")) for r in flight] == [(r.get("plan"), r.get("derive_from")) for r in want])
    n_held = 0
    for r in flight[len(layered):]:
        try:
            F.row_to_jobs(dict(r, biome_neutral=True), derive_facings=False, no_subject="selftest fixture")
        except ValueError as ex:
            n_held += "wing layer" in str(ex)
    check("DRIVE held rows still refused by row_to_jobs", n_held == len(held_rows))


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

    drive_fauna(rows, held + nomaster + rnd)

    body = {k: v for k, v in rec.items() if k not in ("candidate", "artpipe_job", "source_files")}
    b = RN.regen_jobs([dict(body, artpipe_job="RM_Shirrel_east")], "t", texpath_of=tp, neutralize=lambda p: (p, "noop"))
    check("BODY untouched", len(b) == 1 and not RN.is_flight_row(b[0]) and not b[0].get("plan") and not refused(b[0]) and "layered" not in b[0]["style_notes"])

    print(f"{'FAIL' if fails else 'PASS'} selftest_flight_reroll_route ({len(fails)} failed)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
