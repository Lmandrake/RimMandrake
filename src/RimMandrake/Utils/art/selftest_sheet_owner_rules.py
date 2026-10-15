#!/usr/bin/env python3
"""selftest_sheet_owner_rules.py — the owner's three art-sheet rules of 2026-10-12, consumer side (the page side is
selftest_sheet_slots.py):

  A retire AND replace in ONE pass: enact.retire_replaced plans a retired live picture out of the game in the same enact
    as the slot's pick, skips a file the pick's install overwrites, and plans nothing when no replacement is picked
    (that slot is a redraw: the picture stays until replaced); texpath_of maps a file back to the texPath a def names.
  B no "accept unchanged": `decisions_v2 --returned "<his words>"` stamps the return (refused on a file the sidecar never
    wrote, or without his words); ingest then records every slot he left alone as his keep of the IN GAME set, and never
    a slot he answered or a picture he retired.
  C "decided" is only his: a prefill seeded into a row (decision == prefill, no decidedAt) is not his decision —
    owner_view blanks it; his click, an override, a carried ruling and a pre-prefill saved letter are his.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decisions_v2 as DV  # noqa: E402
import enact as E  # noqa: E402
import ingest as I  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class FakeIdx:
    def __init__(self, live):
        self.live = {k: {"sha": v} for k, v in live.items()}

    def live_anywhere(self, sha):
        return [f"{m}/Textures/{r}" for (m, r), ev in self.live.items() if ev["sha"] == sha]


def part_a():
    M = "RimMandrake/TestMod"
    g = "Things/Lamp/Lamp"
    cols = {"A": {"south": "a1", "east": "a2"}, "B": {"south": "b1", "east": "b2", "north": "b3"}}
    idx = FakeIdx({(M, "Things/Lamp/Lamp_south.png"): "b1", (M, "Things/Lamp/Lamp_east.png"): "b2",
                   (M, "Things/Lamp/Lamp_north.png"): "b3", (M, "Things/OldLamp/Lamp_south.png"): "b1"})
    installs = [{"row": "RM_Lamp", "mod": M, "rel": "Things/Lamp/Lamp_south.png"},
                {"row": "RM_Lamp", "mod": M, "rel": "Things/Lamp/Lamp_east.png"}]
    v = {"retire": {g: ["B"]}}
    out = E.retire_replaced(idx, "RM_Lamp", v, cols, {g: "A"}, set(), installs)
    rels = sorted(x["rel"] for x in out)
    check(rels == ["Things/Lamp/Lamp_north.png", "Things/OldLamp/Lamp_south.png"]
          and all(x["replaced_by"] == "A" and x["retired"] == "B" for x in out),
          f"A retired B + pick A: files the pick overwrites need nothing; B's other live copies are planned out ({rels})")
    check(E.retire_replaced(idx, "RM_Lamp", v, cols, {}, set(), installs) == [],
          "A retired B with NO pick in the slot: nothing planned (a redraw; B stays until replaced)")
    check(E.retire_replaced(idx, "RM_Lamp", v, cols, {g: "A"}, {"b3"}, installs)[0]["rel"] == "Things/OldLamp/Lamp_south.png"
          and len(E.retire_replaced(idx, "RM_Lamp", v, cols, {g: "A"}, {"b3", "b1"}, installs)) == 0,
          "A a picture protected on this row (its own pick/variant) is never retired")
    check(E.texpath_of("Things/Lamp/Lamp_north.png") == "Things/Lamp/Lamp"
          and E.texpath_of("Things/Lamp/Lamp.png") == "Things/Lamp/Lamp"
          and E.texpath_of("Things/Pool/Pool_c.png") == "Things/Pool/Pool_c",
          "A texpath_of drops the facing suffix and extension (a folder member keeps its name; its folder is checked too)")


def part_b(tmp: Path):
    p = tmp / "x.decisions.json"
    p.write_text(json.dumps({"sheetId": "x", "decisions": {}}))
    check(not DV.mark_returned(p, "my sheet feedback is done", apply=True)["ok"] and "returned" not in json.loads(p.read_text()),
          "B a file the sidecar never wrote cannot be stamped returned (nothing of his landed)")
    p.write_text(json.dumps({"sheetId": "x", "savedBy": "review-sheet-sidecar", "writeCount": 2, "decisions": {}}))
    check(not DV.mark_returned(p, "ok", apply=True)["ok"], "B a return needs his words, not a bare 'ok'")
    r = DV.mark_returned(p, "My Gimme Some Slack sheet feedback is done.", apply=True, at="2026-10-12T08:26:00-0700")
    doc = json.loads(p.read_text())
    check(r["ok"] and DV.returned(doc) == {"at": "2026-10-12T08:26:00-0700", "said": "My Gimme Some Slack sheet feedback is done.",
                                           "by": "owner"} and doc["reviewStatus"]["state"] == "ruled",
          "B --returned stamps returned{at, said, by} and reviewStatus ruled")
    snap = {"rows": {
        "RM_Lamp": {"columns": {"A": {"south": "a1"}, "B": {"south": "b1"}}, "graphic_of": {"A": "L", "B": "L"},
                    "labels": {"A": "render lamp_v3", "B": "IN GAME — TestMod"}, "res": "L", "subject_key": "lamp"},
        "RM_Mast": {"columns": {"A": {"south": "m1"}}, "graphic_of": {"A": "M"}, "labels": {"A": "IN GAME — TestMod"},
                    "res": "M", "subject_key": "mast"},
        "RM_Pod": {"columns": {"A": {"single": "p1"}, "D": {"single": "y1"}, "G": {"single": "g1"}},
                   "graphic_of": {"A": "P", "D": "PY", "G": "PY"},
                   "labels": {"A": "IN GAME — x", "D": "IN GAME — young", "G": "render"}, "res": "P", "subject_key": "pod"},
        "RM_Gone": {"columns": {"A": {"south": "z1"}}, "graphic_of": {"A": "Z"}, "labels": {"A": "IN GAME — x"}, "res": "Z"}}}
    doc["decisions"] = {
        "RM_Lamp": {"decision": "A", "prefill": "B", "decidedAt": "T", "at": "T"},           # his pick: not touched
        "RM_Mast": {"decision": "A", "prefill": "A"},                                        # seeded prefill, left alone
        "RM_Pod": {"decision": "A", "prefill": "A", "at": "T", "note": "x",
                   "retire": {"PY": ["D"]}},                                                  # young D retired
    }
    evs = []
    out = {}
    I.returned_unchanged(doc, snap, "x.decisions.json", {"RM_Gone"}, lambda ev: evs.append(ev) or True, out)
    got = sorted((e["target"]["row"], e["target"]["column"]) for e in evs)
    check(got == [("RM_Mast", "A"), ("RM_Pod", "A")] and out["returned_unchanged"] == 2,
          f"B returned: the slots he left alone keep their IN GAME set; his pick, his retired D and skipped rows do not ({got})")
    check(all(e["verdict"] == "keep" and e["raw_verdict"] == "returned-unchanged" and e["by"] == "owner"
              and e["said"] == "My Gimme Some Slack sheet feedback is done." for e in evs),
          "B each is a keep ruling carrying his return words (raw_verdict returned-unchanged)")
    evs2 = []
    I.returned_unchanged({"decisions": doc["decisions"]}, snap, "x", set(), lambda ev: evs2.append(ev) or True, {})
    check(evs2 == [], "B a sheet that was never returned records nothing for the slots he left alone")


def part_c():
    seeded = {"decision": "A", "prefill": "A", "at": "T", "note": "a note"}
    check(not DV.decision_is_his(seeded) and DV.owner_view(seeded)["decision"] == ""
          and DV.owner_view(seeded)["prefillOnly"] == "A" and seeded["decision"] == "A",
          "C a seeded prefill saved with a note is NOT his decision (owner_view blanks it on a copy)")
    for v, why in (({"decision": "A", "prefill": "A", "decidedAt": "T"}, "his click"),
                   ({"decision": "B", "prefill": "A", "at": "T"}, "an override of the prefill"),
                   ({"decision": "A", "prefill": "A", "carriedRuledAt": "T"}, "a carried ruling"),
                   ({"decision": "redo", "at": "T"}, "a pre-prefill saved letter")):
        check(DV.decision_is_his(v) and DV.owner_view(v) is v, f"C {why} is his decision")
    check(not DV.decision_is_his({"decision": "A"}) and not DV.decision_is_his({"decision": "", "decidedAt": "T"}),
          "C an unsaved letter, or an empty decision, is nobody's decision")


def main():
    part_a()
    with tempfile.TemporaryDirectory(dir=str(Path.home() / "rm" / "scratch") if (Path.home() / "rm" / "scratch").is_dir() else None) as t:
        part_b(Path(t))
    part_c()
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
