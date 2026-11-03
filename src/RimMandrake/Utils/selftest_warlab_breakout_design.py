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


CHOICES = ("Burn the cells", "Hold them", "Loose the experiments", "Take a specimen", "Leave them")
LABS = ("the Shattered Lab", "the Held Lab", "the Feeding Lab", "the Emptied Lab")


def _block(sec, start, end):
    i = sec.find(start)
    j = sec.find(end, i + 1) if i >= 0 else -1
    return sec[i:j] if i >= 0 and j > i else ""


def planet_content(sec):
    """What recover and fail each LEAVE ON THE PLANET, not just the headings (blind check, gen 5)."""
    bad = []
    rec = _block(sec, "**What a recovery leaves.**", "**What a failure leaves")
    fail = _block(sec, "**What a failure leaves", "**The strike branch")
    if not rec or not fail:
        return ["§2.10 recovery/failure blocks not found in order"]
    for name, body in (("recovery", rec), ("failure", fail)):
        if re.search(r"\bTBD\b|\bTODO\b", body):
            bad.append(f"§2.10 {name} block holds a placeholder")
    # Recovery: a table with an 'on the planet' column and one filled row per choice.
    if not re.search(r"^\| *choice recovered *\| *the lab afterwards *\| *on the planet *\|", rec, re.M):
        bad.append("recovery block has no 'choice recovered | the lab afterwards | on the planet' table")
    rows = {}
    for line in rec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in CHOICES:
            rows[cells[0]] = cells
    for ch in CHOICES:
        r = rows.get(ch)
        if not r:
            bad.append(f"recovery table has no row for {ch!r}")
            continue
        if not (any(lab in r[1] for lab in LABS) or r[1].startswith("as the Held Lab")):
            bad.append(f"recovery row {ch!r} names no lab state")
        if len(r[2]) < 15:
            bad.append(f"recovery row {ch!r} says nothing about the planet")
    for lab in LABS:
        if lab not in rec:
            bad.append(f"recovery block lacks {lab!r}")
    if "spreads nothing" not in rec:
        bad.append("recovery block does not say a recovery spreads nothing")
    if not any(ch in rows and "over for good" in rows[ch][2] for ch in ("Burn the cells", "Leave them")):
        bad.append("recovery table does not say the threat is over for good")
    if "Hold them" in rows and "Imperial attempt" not in rows["Hold them"][2]:
        bad.append("Held Lab row lacks its Imperial attempt on the planet")
    # Failure: his ruling and the planet consequences.
    flat = " ".join(fail.split())
    for want in ("failure = reinfection spreads from the lake across the world over seasons, game continues harder",
                 "reinfection node", "world site", "each season", "hand-authored list", "never rewrites a tile",
                 "sends raids", "never ends the game", "can be pushed back", "threat points", "capped at +40%",
                 "never lowers"):
        if want not in flat:
            bad.append(f"failure block lacks {want!r}")
    return bad


def mutants(sec):
    """The planet checks must see: each gutting of the blocks has to go red (blind checker's mutant included)."""
    a, b, c = sec.index("**What a recovery leaves.**"), sec.index("**What a failure leaves"), sec.index("**The strike branch")
    gutted = {
        "checker: both bodies TBD, lab names kept": sec[:a] + "**What a recovery leaves.** TBD (" + ", ".join(LABS)
        + ").\n\n**What a failure leaves (ruled; the detail delegated).** TBD.\n\n" + sec[c:],
        "recovery planet column blanked": sec[:a] + "\n".join(
            "|".join(x if i != 3 else " - " for i, x in enumerate(l.split("|")))
            if len(l.split("|")) == 5 and l.split("|")[1].strip() in CHOICES else l
            for l in sec[a:b].splitlines()) + "\n" + sec[b:],
        "failure keeps only his ruling": sec[:b] + "**What a failure leaves (ruled; the detail delegated).** His ruling: "
        "*\"failure = reinfection spreads from the lake across the world over seasons, game continues harder.\"*\n\n" + sec[c:],
    }
    return [f"planet checks stay green on mutant {k!r}" for k, s in gutted.items() if not planet_content(s)]


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
    bad += planet_content(sec)
    if not bad:
        bad += mutants(sec)
    q = spec[spec.index("### 2.9 "):spec.index("### 2.10 ")]
    for gone in ("What are the specimen choices", "What does a successful recovery leave"):
        if gone in q:
            bad.append(f"§2.9 still asks {gone!r}")
    # §2.9 Q2 (strike cutoff) and Q5 (strike breakout) closed by his cards, not by this design.
    for ruled in ("Up to what point can the player still call the Cradle strike? → At the wake, gate 4",
                  "Does the Cradle strike skip the breakout? → Strike ends it, no breakout"):
        if ruled not in " ".join(q.split()) or ruled not in " ".join(sec.split()):
            bad.append(f"§2.9 and §2.10 do not both carry his ruling {ruled!r}")
    for stale in ("Not judge-kept", "No fifth round", "Nothing spreads, on any recovery", "unanswered here"):
        if stale in sec:
            bad.append(f"§2.10 still says {stale!r}")
    if "On the dive it always starts" not in sec:
        bad.append("'always starts' is not scoped to the dive")
    arc = yaml.safe_load((ROOT / "infrastructure/state/canon.yml").read_text(encoding="utf-8"))["assailant_reveal_arc"]
    src = arc.get("breakout_design_src", "")
    if not src.startswith(f"delegated:design ({ITEM}"):
        bad.append("canon breakout_design_src is not marked delegated:design")
    if "KEEP" not in src or "not judge-kept" in src:
        bad.append("canon breakout_design_src does not record the judge KEEP")
    if "Still open" in arc.get("breakout_src", ""):
        bad.append("canon breakout_src still says Still open")
    if not (arc.get("strike_breakout_ruled") and arc.get("strike_cutoff_ruled")):
        bad.append("canon does not carry both strike rulings")
    v = json.loads((ROOT / "infrastructure/state/delegated/2026-11-01/warlab_specimens_breakout.json").read_text(encoding="utf-8"))
    rounds = v["rounds"]
    order = sorted(rounds, key=int)
    if v["item"] != ITEM or not rounds:
        bad.append("judge record is not on this item")
    if v.get("scope") != "whole §2.10, strike paragraph included":
        bad.append("the judge did not have the whole section in scope")
    # delegation_policy §4.5: three opus REDOs go to him flagged; rounds past three only on his word.
    first3 = [rounds[k] for k in order[:3]]
    if not all(any("opus" in m for m in r["models"]) for r in first3):
        bad.append("one of the first three rounds was not opus (Agent_Policy)")
    if len(order) > 3:
        if not all(r["verdict"].startswith("VERDICT: REDO") for r in first3) or not v.get("flagged", "") or v["flagged"] not in sec:
            bad.append("rounds past three without three REDOs flagged to him in §2.10")
        if "Keep shape, fix, 4th judge" not in v.get("owner_authorized_past_three", ""):
            bad.append("rounds past three carry no owner authorization (delegation_policy §4.5)")
    last = rounds[order[-1]]
    if not last["verdict"].startswith("VERDICT: KEEP") or v.get("verdict") != "KEEP":
        bad.append("the last judge round is not a KEEP")
    if not any("opus" in m for m in last["models"]):
        bad.append("the KEEP round was not a fresh opus (Agent_Policy)")
    if "WARLAB_STRIKE_DECIDE_JUDGES_SPLIT_TWO_ONE" not in q:
        bad.append("§2.9 does not name WARLAB_STRIKE_DECIDE_JUDGES_SPLIT_TWO_ONE")
    for other in ("WARLAB_DIVE_DECIDE_JUDGES_STUCK_AT_THREE", "WARLAB_BREAKOUT_BUILD_SEALS_HOLD_THE_LINE"):
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
