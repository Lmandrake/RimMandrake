#!/usr/bin/env python3
"""selftest_sheet_look_lanes.py — every LOOK of a def is its own lane, and all looks can be accepted together.

Owner, 2026-10-21, on the line_joins_redraw sheet: *"You had it so that I had to choose between "use this" for each art
style... when actually all four art styles could be chosen together. Bad sheet design, but just accept and move on."*
The sheet had put the four looks' renders (Tank/<Look>/RM_LiquidTank) in ONE lane, the def's base texPath: one pick per
row, and enact would have installed every look onto the Scrapper file.

  builder   art_sheet.look_lane_target: a render filed (artpipe target_texpath) for a sibling look's LIVE texPath leaves
            this lane for its own; its own texPath, a dead path, or a job with a `slot` stay put
  record    decisions_v2.accept_looks: one pick per lane in every row; a lane with two renders needs --prefer; an old
            one-lane `assign` is superseded, not kept as a live choice; his words are required
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as AS  # noqa: E402
import decisions_v2 as DV  # noqa: E402

FAILS: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


T = "RimMandrake/FlowWorks/Tank/{}/RM_LiquidTank"


def builder() -> None:
    AS._FAM_SLOTS = {"tank_slotted": T.format("Scrapper")}
    AS._FAM_TEX = {"tank_lj_futuristic": T.format("Futuristic"), "tank_lj_scrapper": T.format("Scrapper"),
                   "tank_lj_dead": T.format("Gone"), "tank_slotted": T.format("Modern")}
    live = {T.format(x) for x in ("Scrapper", "Futuristic", "Modern")}
    base = {T.format("Scrapper")}
    check(AS.look_lane_target("Tank_lj_Futuristic", base, live) == T.format("Futuristic"),
          "a sibling look's render leaves the base lane for its own")
    check(AS.look_lane_target("tank_lj_scrapper", base, live) is None, "a render of THIS lane's texPath stays")
    check(AS.look_lane_target("tank_lj_dead", base, live) is None, "a texPath no mod ships opens no lane")
    check(AS.look_lane_target("tank_slotted", base, live) is None, "a job filed for a sheet slot keeps the slot route")
    check(AS.look_lane_target("unknown_job", base, live) is None, "a job with no target_texpath stays")
    AS._FAM_SLOTS = AS._FAM_TEX = None


def record() -> None:
    lanes = {x: T.format(x) for x in ("Scrapper", "Futuristic")}
    snap = {"snapshotId": "s1", "rows": {
        "RM_LiquidTank": {"res": lanes["Scrapper"],
                          "columns": {L: {"single": L * 64} for L in "ABCDE"},
                          "graphic_of": {"A": lanes["Scrapper"], "B": lanes["Futuristic"], "C": lanes["Scrapper"],
                                         "D": lanes["Futuristic"], "E": lanes["Scrapper"]},
                          "labels": {"A": "IN GAME — FlowWorks", "B": "render tank_lj_futuristic",
                                     "C": "render tank_lj_scrapper", "D": "IN GAME — FlowWorks",
                                     "E": "render tank_lj2_scrapper"}}}}
    doc = {"snapshotId": "s1", "snapshot": "x", "decisions": {
        "RM_LiquidTank": {"decision": "C", "assign": {"B": lanes["Scrapper"]}, "prefill": "A"}}}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "d.json"
        p.write_text(json.dumps(doc))
        r = DV.accept_looks(p, "short", snapshot=snap)
        check(not r["ok"] and "his words" in r["error"], "refuses without his words")
        said = "Just accept the art and go on."
        r = DV.accept_looks(p, said, snapshot=snap, apply=True)
        check(not r["ok"] and lanes["Scrapper"] in r["unresolved"].get("RM_LiquidTank", {}),
              "a lane with two renders and no --prefer is reported, not guessed")
        check(json.loads(p.read_text()) == doc, "an unresolved row is left unchanged on disk")
        r = DV.accept_looks(p, said, prefer={"RM_LiquidTank": ["E"]}, snapshot=snap, apply=True)
        v = json.loads(p.read_text())["decisions"]["RM_LiquidTank"]
        picks = {g: s["pick"] for g, s in v["slots"].items() if s["state"] == "pick"}
        check(r["ok"] and picks == {lanes["Scrapper"]: "E", lanes["Futuristic"]: "B"},
              "every look lane gets its render, together (prefer settles the two-render lane)")
        check(DV.slot_picks(v) == picks, "enact's reader (slot_picks) sees the same per-look picks")
        check(v["assign"] == {} and v["assignSuperseded"] == {"B": lanes["Scrapper"]},
              "the old one-lane assign is superseded, kept for audit")
        check(v["acceptedLooks"]["said"] == said and v["decision"] == "E" and DV.decision_is_his(v),
              "his words are on the record; the row decision is the base lane's pick and reads as his")
        r = DV.accept_looks(p, said, snapshot={**snap, "snapshotId": "s2"})
        check(not r["ok"] and "remap" in r["error"], "refuses against a different snapshot (remap first)")


if __name__ == "__main__":
    builder()
    record()
    print(f"{'FAIL' if FAILS else 'PASS'} selftest_sheet_look_lanes: {len(FAILS)} failure(s)")
    sys.exit(1 if FAILS else 0)
