#!/usr/bin/env python3
"""selftest_flyer_master_record.py - an ACCEPTED flyer body records its master, and a flight reroll derives from it
(ARTEVAL_WIRE_FLYER_MASTER_NOBODY_WRITES_IT).

  RECORD    runner.run (mock reviewers, --test) on a flyer static whose east picture is artpipe job <job>_east: ACCEPT
            writes master_job=<job>_east into decisions.jsonl; a non-flyer ACCEPT and a flyer ACCEPT drawn outside the
            pipeline (east not that job's render) record none
  WIRE      the same run also judges the flyer's flight cut (REGEN): regen_jobs.json holds 9 wing-layer rows with
            plan and derive_from=<job>_east, every one passing fill_queue's flight-frame gate
  HELD      a flight REGEN of a flyer whose body was not accepted in the run stays one held row, refused at filing
  HISTORY   accepted_masters reads production runs only, latest body verdict by `at`: a later REGEN withdraws the
            master, a later HOLD_ERROR does not, a --test run or one with no run.json never supplies one
  MERGE     this run's records over the history (run()'s call): an ACCEPT restores, an ESCALATE withdraws
  FINISHED  master_finished keeps a master only while the artpipe queue holds its ok manifest and render
  VETO      auto_judge.veto_record drops master_job from the REGEN that replaces a vetoed ACCEPT
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
import runner as RN  # noqa: E402
import policy as P  # noqa: E402
import fill_queue as F  # noqa: E402

fails = []
FLYER, OTHER, OUTSIDE, LONE = "RSW_Strill", "RM_DryWalker", "RSW_Sketto", "RM_FireHawk"


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


def refused(row) -> bool:
    try:
        F._refuse_unlocked_frames(row)
        return False
    except ValueError as ex:
        return "wing layer" in str(ex)


def sprite(p: Path, h: int) -> str:
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([60, 256 - h, 196, 250], fill=(120, 90, 60, 255))
    im.save(p)
    return str(p)


def specs(tmp: Path) -> list:
    def body(subj, job):
        d = tmp / subj
        d.mkdir(exist_ok=True)
        stem = (lambda f: f"{job}_{f}") if job else (lambda f: f"{subj}_{f}")
        imgs = {f: sprite(d / f"{stem(f)}.png", 150 + i) for i, f in enumerate(("south", "east", "north"))}
        imgs["scale"] = sprite(d / "scale.png", 100)
        s = {"subject": subj, "template": "creature", "module": "walker", "invented": True, "description": "a beast",
             "images": imgs, "owner_kept": False}
        return dict(s, artpipe_job=job) if job else s
    flight = []
    for subj in (FLYER, LONE):
        d = tmp / f"{subj}_flight"
        d.mkdir(exist_ok=True)
        imgs = {f: sprite(d / f"{subj}_flight_{f}.png", 140 + i) for i, f in enumerate(("south", "east", "north"))}
        imgs["scale"] = sprite(d / "scale.png", 100)
        flight.append({"subject": subj, "candidate": "flight_cut1", "template": "creature", "module": "walker",
                       "invented": True, "description": "a flyer in flight", "images": imgs, "owner_kept": False,
                       "target_texpath": f"Things/Pawn/Animal/{subj}/{subj}"})
    return [body(FLYER, f"arteval_{FLYER}_r1"), body(OTHER, f"arteval_{OTHER}_r1"), body(OUTSIDE, "")] + flight


class Mock(RN.Reviewers):
    def __init__(self):
        self.tpl = P.load_template("creature")

    def opus(self, prompt, card_dir):
        card = (card_dir / "card.md").read_text()
        subj = re.search(r"^# (\S+) —", card, re.M).group(1)
        flight = "flight" in card_dir.name
        items = self.tpl["checklist"]   # every item any card can carry (canon items on an RSW_ card)
        f = [{"code": "F_NORTH_FACE", "confidence": 0.95, "fix": "rear view"}] if flight else []
        return json.dumps({"schema": "rm-art-eval/opus@v1", "subject": subj, "observed": {},
                           "checklist": {i["id"]: {"status": "ok", "seen": "-"} for i in items},
                           "findings": f, "overall": "really_bad" if f else "good"}), {"models_reported": ["mock-opus"]}

    def gpt(self, prompt, images, work):
        raise AssertionError("no second look expected")

    def regen(self, prompt, work):
        return json.dumps({"schema": "rm-art-eval/regen@v1", "subject": "x", "edits": [], "invariants": [],
                           "reference": "keep", "prompt": "rear view, seen from behind"}), {"models_reported": ["mock"]}


def history(tmp: Path):
    runs = tmp / "hist"

    def put(run, test, recs):
        (runs / run).mkdir(parents=True)
        (runs / run / "run.json").write_text(json.dumps({"test": test}))
        (runs / run / "decisions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    acc = lambda s, at, m: {"subject": s, "decision": "ACCEPT", "at": at, "master_job": m}   # noqa: E731
    put("b_run", False, [acc("RSW_A", "2026-11-01T10:00:00-07:00", "arteval_RSW_A_r1_east"),
                         acc("RSW_B", "2026-11-01T10:00:00-07:00", "arteval_RSW_B_r1_east"),
                         acc("RSW_C", "2026-11-01T10:00:00-07:00", "arteval_RSW_C_r1_east")])
    # named 'a_' so dir order is not time order: these are LATER by `at`
    put("a_run", False, [{"subject": "RSW_A", "decision": "REGEN", "at": "2026-11-02T10:00:00-07:00"},
                         {"subject": "RSW_B", "decision": "HOLD_ERROR", "at": "2026-11-02T10:00:00-07:00"},
                         {"subject": "RSW_C", "candidate": "flight_cut1", "artpipe_job": "x_flight_cut1",
                          "decision": "REGEN", "at": "2026-11-02T10:00:00-07:00"}])
    put("t_run", True, [acc("RSW_D", "2026-11-03T10:00:00-07:00", "arteval_RSW_D_r1_east")])
    (runs / "n_run").mkdir()   # no run.json: unknown mode counts as --test (round_series.production_decisions)
    (runs / "n_run" / "decisions.jsonl").write_text(json.dumps(acc("RSW_E", "2026-11-03T10:00:00-07:00", "arteval_RSW_E_r1_east")) + "\n")
    m = RN.accepted_masters(runs, job_ok=None)
    check("HISTORY later body REGEN withdraws", "RSW_A" not in m)
    check("HISTORY later HOLD_ERROR keeps", m.get("RSW_B") == "arteval_RSW_B_r1_east")
    check("HISTORY a flight REGEN is not a body verdict", m.get("RSW_C") == "arteval_RSW_C_r1_east")
    check("HISTORY --test run supplies none", "RSW_D" not in m)
    check("HISTORY run with no run.json supplies none", "RSW_E" not in m)
    # MERGE: this run's records (extra) over the history, the way run() calls it
    now = [{"subject": "RSW_A", "decision": "ACCEPT", "at": "2026-11-04T10:00:00-07:00", "master_job": "arteval_RSW_A_r2_east"},
           {"subject": "RSW_B", "decision": "ESCALATE", "at": "2026-11-04T10:00:00-07:00"}]
    m = RN.accepted_masters(runs, now, job_ok=None)
    check("MERGE this run's ACCEPT restores a master", m.get("RSW_A") == "arteval_RSW_A_r2_east")
    check("MERGE this run's ESCALATE withdraws one", "RSW_B" not in m)
    # FINISHED: a master is kept only while artpipe holds its ok render
    q = tmp / "queue"
    for job, status, png in (("arteval_RSW_A_r2_east", "ok", True), ("arteval_RSW_C_r1_east", "failed", True)):
        (q / "done").mkdir(parents=True, exist_ok=True)
        (q / "done" / f"{job}.manifest.json").write_text(json.dumps({"status": status}))
        if png:
            (q / "_artsrc" / job).mkdir(parents=True, exist_ok=True)
            (q / "_artsrc" / job / f"{job}.png").write_bytes(b"png")
    m = RN.accepted_masters(runs, now, job_ok=lambda j: RN.master_finished(j, q))
    check("FINISHED ok render kept", m.get("RSW_A") == "arteval_RSW_A_r2_east")
    check("FINISHED failed / absent master dropped", "RSW_C" not in m and "RSW_B" not in m)


def main() -> int:
    flyers = RN.flyer_defs()
    check("fixture defs are flyers", {FLYER, OUTSIDE, LONE} <= flyers and OTHER not in flyers)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        sp = specs(tmp)
        # LONE's body is not in this run, so its flight cut has no master
        recs = RN.run(sp, "selftest_master", rev=Mock(), test=True, work_root=tmp / "work", state_root=tmp / "state")
        by = {(r["subject"], r.get("candidate")): r for r in recs}
        disk = [json.loads(x) for x in (tmp / "state/selftest_master/decisions.jsonl").read_text().splitlines() if x]
        body = next((r for r in disk if r["subject"] == FLYER and not RN.is_flight_record(r)), {})
        check("RECORD flyer body ACCEPT", body.get("decision") == "ACCEPT")
        check("RECORD master_job written to decisions.jsonl", body.get("master_job") == f"arteval_{FLYER}_r1_east")
        check("RECORD non-flyer records none", by.get((OTHER, None), {}).get("decision") == "ACCEPT"
              and "master_job" not in by[(OTHER, None)])
        check("RECORD outside-pipeline art records none", by.get((OUTSIDE, None), {}).get("decision") == "ACCEPT"
              and "master_job" not in by[(OUTSIDE, None)])
        fl = by.get((FLYER, "flight_cut1"), {})
        check("WIRE flight cut is a flight REGEN", fl.get("decision") == "REGEN" and RN.is_flight_record(fl))
        jobs = json.loads((tmp / "state/selftest_master/regen_jobs.json").read_text())
        layered = [j for j in jobs if j["target_def"] == FLYER]
        check("WIRE 9 wing-layer rows", len(layered) == 9)
        check("WIRE derive_from the recorded master",
              all(j.get("derive_from") == f"arteval_{FLYER}_r1_east" and j.get("plan") for j in layered))
        check("WIRE rows pass the flight-frame gate", layered and not any(refused(j) for j in layered))
        lone = [j for j in jobs if j["target_def"] == LONE]
        check("HELD no accepted body: one refused row", len(lone) == 1 and refused(lone[0])
              and "no accepted body master" in lone[0]["style_notes"])
        history(tmp)
    import auto_judge as AJ
    v = AJ.veto_record({"subject": FLYER, "decision": "ACCEPT", "master_job": "m_east", "reasons": []},
                       {"verdict": "worse", "reason": "drifted"}, "a strill", 0)
    check("VETO drops master_job", v["decision"] == "REGEN" and "master_job" not in v)
    print(f"{'FAIL' if fails else 'PASS'} selftest_flyer_master_record ({len(fails)} failed)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
