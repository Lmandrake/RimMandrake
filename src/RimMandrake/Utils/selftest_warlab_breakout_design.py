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


PLACEHOLDER = re.compile(r"\b(TBD|TODO|TBC|to be (decided|determined|written|confirmed)|placeholder|fill in)\b", re.I)


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
        if PLACEHOLDER.search(body):
            bad.append(f"§2.10 {name} block holds a placeholder")
    # Recovery: a table with an 'on the planet' column and one filled row per choice.
    if not re.search(r"^\| *choice recovered *\| *the lab afterwards *\| *on the planet *\|", rec, re.M):
        bad.append("recovery block has no 'choice recovered | the lab afterwards | on the planet' table")
    rows = {}
    for line in rec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in CHOICES:
            if cells[0] in rows:
                bad.append(f"recovery table has two rows for {cells[0]!r}")
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


def start_and_choices(sec):
    """What starts the breakout and what the choices are, by content, not headings (blind check, gen 7)."""
    bad = []
    trig = _block(sec, "**What starts the breakout", "**The choices.**")
    cho = _block(sec, "**The choices.**", "**The Specimen Casket.**")
    if not trig or not cho:
        return ["§2.10 trigger/choices blocks not found in order"]
    if PLACEHOLDER.search(trig) or PLACEHOLDER.search(cho):
        bad.append("§2.10 trigger or choices block holds a placeholder")
    items = {}
    cur = None
    for line in trig.splitlines():
        m = re.match(r"^(\d)\. (.*)", line)
        if m:
            cur = int(m.group(1))
            if cur in items:
                bad.append(f"trigger {cur} is listed twice")
            items[cur] = m.group(2)
        elif cur and line.startswith("   ") and line.strip():
            items[cur] += " " + line.strip()
        elif not line.strip():
            cur = None
    if sorted(items) != [1, 2, 3]:
        bad.append(f"trigger list is not three numbered triggers (found {sorted(items)})")
    t1, t2, t3 = (items.get(k, "") for k in (1, 2, 3))
    if "console" not in t1 or "choice" not in t1:
        bad.append("trigger 1 is not the choice finishing at the console")
    if "hyperdrive" not in t2 or "lifted" not in t2 or "Leave them" not in t2:
        bad.append("trigger 2 is not the hyperdrive lifted (as Leave them)")
    if "stasis decay runs out" not in t3 or "15-day clock" not in t3 or "Leave them" not in t3:
        bad.append("trigger 3 is not the 15-day stasis decay (as Leave them)")
    if "the first of three things" not in trig:
        bad.append("trigger block does not say the first of three starts it")
    flat = " ".join(cho.split())
    for want in ("One pick, made once at the console", "how bad the breakout is, never whether it comes"):
        if want not in flat:
            bad.append(f"choices block lacks {want!r}")
    if not re.search(r"^\| *choice *\| *what is done *\| *cells that fail *\| *seal window *\| *what it costs or pays *\|", cho, re.M):
        bad.append("choices block has no 'choice | what is done | cells that fail | seal window | what it costs or pays' table")
    rows = {}
    for line in cho.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[0].strip("*") in CHOICES:
            if cells[0].strip("*") in rows:
                bad.append(f"choices table has two rows for {cells[0]!r}")
            rows[cells[0].strip("*")] = cells
    for ch in CHOICES:
        r = rows.get(ch)
        if not r:
            bad.append(f"choices table has no row for {ch!r}")
            continue
        if PLACEHOLDER.search(" ".join(r)):
            bad.append(f"choice {ch!r} holds a placeholder")
        if len(r[1]) < 10 or len(r[4]) < 10:
            bad.append(f"choice {ch!r} has an empty 'what is done' or 'costs' cell")
        if not re.match(r"[1-4] of 4\b", r[2]):
            bad.append(f"choice {ch!r} sets no count of failing cells")
        if not re.match(r"\d+ days?$", r[3]):
            bad.append(f"choice {ch!r} sets no seal window")
    if "Leave them" in rows and "4 of 4" not in rows["Leave them"][2]:
        bad.append("Leave them (the default) does not fail every cell")
    if "every pick leaves it obtainable" not in flat:
        bad.append("choices block does not keep the hyperdrive obtainable on every pick")
    return bad


BREAKOUT = "**The breakout (start of the third act).**"
RECFAIL = "**Recover or fail: one check, at the seals.**"
LATCH = "Failure latches the moment"


def _bullet(sec, head):
    """The top-level '- **X:**' bullet starting with head, with its indented continuation and sub-bullets."""
    lines = sec.splitlines()
    i = next((n for n, l in enumerate(lines) if l.startswith(head)), None)
    if i is None:
        return ""
    out = [lines[i]]
    for l in lines[i + 1:]:
        if not l.strip() or not l.startswith(" "):
            break
        out.append(l)
    return "\n".join(out)


def breakout_recover_fail(sec):
    """The breakout and the recover-or-fail beat, by content (blind check, gen 9: deleting them stayed green)."""
    bad = []
    brk = _block(sec, BREAKOUT, RECFAIL)
    seals = _block(sec, RECFAIL, LATCH)
    if not brk or not seals:
        return ["§2.10 breakout / recover-or-fail blocks not found in order"]
    fb = " ".join(brk.split())
    for want in ("Failing cells release live originals into the core", "band by band", "outer gate", "attack them"):
        if want not in fb:
            bad.append(f"breakout paragraph lacks {want!r}")
    fs = " ".join(seals.split())
    for want in ("three bulkhead seals", "the last at the outer gate", "works from either side",
                 "Shutting takes one pawn 8 in-game hours", "A shut seal stops everything behind it",
                 "The pace is a schedule", "W/3", "passes the outer gate exactly as the window closes"):
        if want not in fs:
            bad.append(f"seals/pace block lacks {want!r}")
    if PLACEHOLDER.search(brk + seals):
        bad.append("breakout or recover-or-fail block holds a placeholder")
    rec = " ".join(_bullet(seals, "- **Recover:**").split())
    fail = " ".join(_bullet(seals, "- **Fail:**").split())
    if not rec:
        bad.append("no '- **Recover:**' bullet")
    else:
        if "every live specimen is dead or behind a shut seal" not in rec:
            bad.append("Recover bullet does not say every live specimen dead or behind a shut seal")
        if "settled by the choice" not in rec:
            bad.append("Recover bullet does not say the choice settles what is sealed in")
        m = re.search(r"Under Burn the cells, Leave them and Loose the experiments, the purge settles it(.*?)Recovery latches when the purge fires", rec)
        if not m or "every specimen there dies" not in m.group(1) or "calls the purge off" not in m.group(1):
            bad.append("Recover bullet lacks the purge settling Burn / Leave / Loose")
        m = re.search(r"Under Hold them and Take a specimen, recovery latches at once(.*?)not a live specimen, for this check", rec)
        if not m or "back in stasis" not in m.group(1) or "Imperial attempt" not in m.group(1) or "Shattered Lab" not in m.group(1):
            bad.append("Recover bullet lacks the stasis settling Hold / Take")
        if "Recovery latches in every case" not in rec:
            bad.append("Recover bullet does not say recovery latches in every case")
    if not fail:
        bad.append("no '- **Fail:**' bullet")
    else:
        for want in ("a specimen passes the outer gate", "leaves the map with one loose", "One specimen out is enough"):
            if want not in fail:
                bad.append(f"Fail bullet lacks {want!r}")
    if rec and fail and seals.find("- **Recover:**") > seals.find("- **Fail:**"):
        bad.append("Fail bullet comes before Recover bullet")
    if "nothing undoes it" not in " ".join(sec[sec.find(LATCH):sec.find(LATCH) + 400].split()):
        bad.append("failure does not latch for good")
    return bad


def breakout_mutants(sec):
    """The gen-9 checker's four deletions plus each half of Recover: every one must go red."""
    b, r, l = sec.index(BREAKOUT), sec.index(RECFAIL), sec.index(LATCH)
    rb, fb = sec.index("- **Recover:**"), sec.index("- **Fail:**")
    fend = sec.index("\n\n", fb)
    pu, ho = sec.index("  - Under Burn the cells"), sec.index("  - Under Hold them")
    ev = sec.index("  - Recovery latches in every case")
    gutted = {
        "seals, pace, Recover and Fail deleted": sec[:r] + sec[l:],
        "Fail bullet deleted": sec[:fb] + sec[fend:],
        "Recover bullet deleted": sec[:rb] + sec[fb:],
        "breakout paragraph deleted": sec[:b] + sec[r:],
        "purge sub-bullet deleted": sec[:pu] + sec[ho:],
        "stasis sub-bullet deleted": sec[:ho] + sec[ev:],
        "Fail loses the crew-leaves case": sec.replace("leaves the map with one loose", "leaves"),
    }
    bad = [f"mutant {k!r} changed nothing" for k, s in gutted.items() if s == sec]
    return bad + [f"breakout/recover-fail checks stay green on mutant {k!r}" for k, s in gutted.items() if not breakout_recover_fail(s)]


def start_mutants(sec):
    """The checker's two mutants (trigger list deleted; choices paragraph+table+drive paragraph deleted) and a blanked cell."""
    w, c, k = sec.index("**What starts the breakout"), sec.index("**The choices.**"), sec.index("**The Specimen Casket.**")
    trig = sec[w:c].splitlines()
    t = next((i for i, l in enumerate(trig) if re.match(r"^\d\. ", l)), len(trig))
    e = next((i for i in range(t, len(trig)) if not trig[i].strip()), len(trig))
    blank = "\n".join("| Hold them |  |  |  |  |"
                      if l.strip().strip("|").split("|")[0].strip().strip("*") == "Hold them" else l
                      for l in sec[c:k].splitlines())
    gutted = {
        "trigger list deleted": sec[:w] + "\n".join(trig[:t] + trig[e:]) + "\n" + sec[c:],
        "choices paragraph, table and drive paragraph deleted": sec[:c] + sec[k:],
        "Hold them row blanked": sec[:c] + blank + "\n" + sec[k:],
        "trigger 3 lost its clock": sec.replace("15-day clock", "clock"),
    }
    bad = [f"mutant {name!r} changed nothing" for name, s in gutted.items() if s == sec]
    return bad + [f"start/choice checks stay green on mutant {name!r}" for name, s in gutted.items() if not start_and_choices(s)]


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
    sec = re.search(r"^### 2\.10 .*?(?=^#{1,3} |\Z)", spec, re.S | re.M)
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
    bad += start_and_choices(sec)
    bad += breakout_recover_fail(sec)
    if "### 2.9 " not in spec:
        bad.append("no §2.9 in dungeons_arc_spec.md")
    if not bad:
        bad += mutants(sec)
        bad += start_mutants(sec)
        bad += breakout_mutants(sec)
    q = spec[spec.index("### 2.9 "):spec.index("### 2.10 ")] if "### 2.9 " in spec else ""
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
    order = sorted(rounds, key=lambda k: (not re.fullmatch(r"[0-9]{1,3}", k), int(k) if re.fullmatch(r"[0-9]{1,3}", k) else 0, k))
    placeholder = False
    if v["item"] != ITEM or not rounds:
        bad.append("judge record is not on this item")
        placeholder = True
        order = ["0"]
        rounds = {"0": {"verdict": "", "models": []}}
    if v.get("scope") != "whole §2.10, strike paragraph included":
        bad.append("the judge did not have the whole section in scope")
    if order != [str(i) for i in range(1, len(order) + 1)] and not placeholder:
        bad.append(f"judge rounds are not numbered 1..n in a row ({order})")
    # delegation_policy §4.5: three opus REDOs go to him flagged; rounds past three only on his word.
    first3 = [rounds[k] for k in order[:3]]
    if not all(any(isinstance(m, str) and re.search(r"\bopus\b", m) for m in r["models"]) for r in first3):
        bad.append("one of the first three rounds was not opus (Agent_Policy)")
    if len(order) > 3:
        if not all(r["verdict"].startswith("VERDICT: REDO") for r in first3) or v.get("flagged") != "WARLAB_DIVE_DECIDE_JUDGES_STUCK_AT_THREE" or v["flagged"] not in sec:
            bad.append("rounds past three without three REDOs flagged to him in §2.10")
        if "Keep shape, fix, 4th judge" not in v.get("owner_authorized_past_three", ""):
            bad.append("rounds past three carry no owner authorization (delegation_policy §4.5)")
    last = rounds[order[-1]]
    if not last["verdict"].startswith("VERDICT: KEEP") or v.get("verdict") != "KEEP":
        bad.append("the last judge round is not a KEEP")
    if not any(isinstance(m, str) and re.search(r"\bopus\b", m) for m in last["models"]):
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
