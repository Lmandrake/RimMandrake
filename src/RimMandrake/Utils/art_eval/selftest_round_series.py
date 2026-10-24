#!/usr/bin/env python3
"""Selftest for round_series.py: fresh round series and owner-written prompts (pure, temp dirs only)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import round_series as RS  # noqa: E402

FAILS = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        FAILS.append(name)


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        rp = td / "round_resets.jsonl"
        recs = [("fauna_x_00", {"subject": "D", "decision": "REGEN", "at": "2026-10-23T10:00:00-07:00"}),
                ("fauna_x_r1_00", {"subject": "D", "decision": "REGEN", "at": "2026-10-23T17:00:00-07:00"}),
                ("fauna_x_r2_00", {"subject": "D", "decision": "REGEN", "at": "2026-10-24T01:00:00-07:00"}),
                ("fauna_x_r3_00", {"subject": "D", "decision": "ESCALATE", "at": "2026-10-24T03:00:00-07:00"}),
                ("fauna_x_00", {"subject": "E", "decision": "REGEN", "at": "2026-10-23T10:00:00-07:00"})]
        check("no reset: count is REGENs", RS.regen_counts(recs, {}) == {"D": 3, "E": 1})
        check("no reset: tag rN", RS.tag("D", 2, {}) == "r2")
        try:
            RS.add_reset("D", "fauna_x_00", {"why": "mine"}, path=rp)
            check("reset without owner provenance refused", False)
        except ValueError:
            check("reset without owner provenance refused", True)
        RS.add_reset("D", "fauna_x_00", {"by_card": "q → a"}, path=rp, now="2026-10-24T07:00:00-07:00")
        rs = RS.resets(rp)
        check("reset is series 1", rs["D"]["series"] == 1)
        check("tag carries series", RS.tag("D", 1, rs) == "s1r1" and RS.tag("E", 1, rs) == "r1")
        check("after reset: round 1 filed", RS.regen_counts(recs, rs)["D"] == 1)
        later = recs + [("fauna_s1_r1_00", {"subject": "D", "decision": "REGEN", "at": "2026-10-24T09:00:00-07:00"})]
        check("after reset: REGEN after it counts", RS.regen_counts(later, rs)["D"] == 2)
        rounds = RS.apply_to_rounds({"D": 3, "E": 1}, later, rs)
        check("runner rounds use the series", rounds == {"D": 2, "E": 1})
        RS.add_reset("D", "fauna_x_00", {"by_card": "q → a"}, path=rp, now="2026-10-25T07:00:00-07:00")
        check("second reset is series 2", RS.tag("D", 1, RS.resets(rp)) == "s2r1")
        RS.add_stop("D", {"why": "he kept the live art"}, path=rp, now="2026-10-25T08:00:00-07:00")
        rs2 = RS.resets(rp)
        check("stop marks the series stopped, series kept", RS.stopped("D", rs2) and RS.tag("D", 1, rs2) == "s2r1"
              and not RS.stopped("E", rs2))
        check("stop does not move the reset time", RS.regen_counts(later, rs2)["D"] == 1)
        RS.add_reset("D", "fauna_x_00", {"by_card": "q → a"}, path=rp, now="2026-10-26T07:00:00-07:00")
        check("a newer reset clears the stop", not RS.stopped("D", RS.resets(rp)) and RS.tag("D", 1, RS.resets(rp)) == "s3r1")

        # install gate: the 2026-10-23 kept-art card covers keeps the REALLY_BAD judgement saw, never a keep he made
        # AFTER it (he looked again and kept it); a keep with no time is treated as newer (refuse, never overwrite)
        judged = "2026-10-23T10:00:00-07:00"
        old_k = {"id": "k1", "ts": "2026-10-20T10:00:00Z"}
        new_k = {"id": "k2", "ts": "2026-10-24T01:00:00Z"}
        check("keep older than the judgement: card applies", RS.keeps_after([old_k], judged) == [])
        check("keep newer than the judgement: refused", [k["id"] for k in RS.keeps_after([old_k, new_k], judged)] == ["k2"])
        check("keep with no time: refused", [k["id"] for k in RS.keeps_after([{"id": "k3"}], judged)] == ["k3"])
        check("no judgement time: every keep refuses", len(RS.keeps_after([old_k], None)) == 1)

        # owner prompts: sheet note and jsonl, newest wins; prefill (empty) notes ignored
        root = td / "repo"
        sd = root / "Transient/biome_ffar"
        sd.mkdir(parents=True)
        (sd / "owner_escalations_x_sheet_2026-10-24.decisions.json").write_text(json.dumps({
            "reviewStatus": {"state": "saved", "at": "2026-10-24T08:00:00-07:00"},
            "decisions": {"D": {"decision": "A", "note": "a squat grey beetle, six legs"},
                          "E": {"decision": "A", "note": ""}}}))
        op = td / "owner_prompts.jsonl"
        found = RS.owner_prompts(root, op)
        check("sheet note found, empty note ignored", set(found) == {"D"} and found["D"]["text"].startswith("a squat"))
        op.write_text(json.dumps({"at": "2026-10-24T09:00:00-07:00", "def": "D", "text": "newer words",
                                  "owner_said": "newer words"}) + "\n")
        check("newest owner text wins", RS.owner_prompts(root, op)["D"]["text"] == "newer words")
        p = RS.compose_owner_prompt("dust beetle", "His text, kept exactly; Unusual Case!")
        check("owner text verbatim inside template", "His text, kept exactly; Unusual Case!" in p
              and p.startswith("A single RimWorld creature sprite of the dust beetle") and "transparent" in p)
    print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
