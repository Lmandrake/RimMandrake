#!/usr/bin/env python3
"""WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE: the delegated specimen design is written, closes its questions and stays delegated."""
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
ITEM = "WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE"
LEDGER = ROOT / "infrastructure/state/ledger/events"


def main():
    bad = []
    spec = (ROOT / "design/Jawa/worldbuilding/dungeons_arc_spec.md").read_text(encoding="utf-8")
    sec = re.search(r"^### 2\.10 .*?(?=^## 3\. )", spec, re.S | re.M)
    if not sec:
        print("FAIL: no §2.10 in dungeons_arc_spec.md")
        return 1
    sec = sec.group(0)
    for want in ("Burn the cells", "Hold them", "Loose the experiments", "Take a specimen", "Leave them",
                 "What starts the breakout", "What a recovery leaves", "What a failure leaves",
                 "Failure latches", "The strike branch", "PROVISIONAL", "the Shattered Lab", "the Held Lab",
                 "the Feeding Lab", "the Emptied Lab"):
        if want not in sec:
            bad.append(f"§2.10 lacks {want!r}")
    q = spec[spec.index("### 2.9 "):spec.index("### 2.10 ")]
    for gone in ("What are the specimen choices", "What does a successful recovery leave"):
        if gone in q:
            bad.append(f"§2.9 still asks {gone!r}")
    # The strike stays his: open in §2.9 until WARLAB_STRIKE_DECIDE_JUDGES_SPLIT_TWO_ONE is ruled.
    if "Does the breakout happen on the strike branch" not in q or "WARLAB_STRIKE_DECIDE_JUDGES_SPLIT_TWO_ONE" not in q:
        bad.append("§2.9 no longer holds the strike question open")
    arc = yaml.safe_load((ROOT / "infrastructure/state/canon.yml").read_text(encoding="utf-8"))["assailant_reveal_arc"]
    src = arc.get("breakout_design_src", "")
    if not src.startswith(f"delegated:design ({ITEM}"):
        bad.append("canon breakout_design_src is not marked delegated:design")
    if "Still open" in arc.get("breakout_src", ""):
        bad.append("canon breakout_src still says Still open")
    v = json.loads((ROOT / "infrastructure/state/delegated/2026-11-01/warlab_specimens_breakout.json").read_text(encoding="utf-8"))
    rounds = v["rounds"]
    if v["item"] != ITEM or not rounds or len(rounds) > 3:
        bad.append("judge record is not one to three rounds on this item (delegation_policy §4.5)")
    if not all(any("opus" in m for m in r["models"]) for r in rounds.values()):
        bad.append("a judge round was not opus (Agent_Policy)")
    if v.get("scope") != "whole §2.10, strike paragraph included":
        bad.append("the judge did not have the whole section in scope")
    last = rounds[max(rounds, key=int)]["verdict"]
    if not last.startswith("VERDICT: KEEP") and not (v.get("verdict") == "STUCK" and len(rounds) == 3 and v.get("flagged", "") in sec and v.get("flagged")):
        bad.append("no final KEEP, and not flagged stuck after three rounds")
    for other in ("WARLAB_STRIKE_DECIDE_JUDGES_SPLIT_TWO_ONE", "WARLAB_BREAKOUT_BUILD_SEALS_HOLD_THE_LINE"):
        if other not in sec:
            bad.append(f"§2.10 does not name {other}")
    notes = [json.loads(l) for p in LEDGER.glob("*.jsonl") for l in p.read_text(encoding="utf-8").splitlines() if ITEM in l]
    if not any(e.get("id") == ITEM and e.get("event") == "note" and str(e.get("why", "")).startswith("delegated: design") for e in notes):
        bad.append("no ledger note with why delegated: design")
    for b in bad:
        print("FAIL:", b)
    print("OK" if not bad else f"{len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
