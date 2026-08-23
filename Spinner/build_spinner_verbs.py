#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the project's one spinner-verb pool from the four per-seat lists.

    python3 Spinner/build_spinner_verbs.py            # rewrite the md AND the setting
    python3 Spinner/build_spinner_verbs.py --check     # verify only, exit 1 if stale

🔑 WHY ONE POOL. `.claude/settings.json` is scoped to the PROJECT, not the window, and
Claude Code has no per-seat settings file — so four lists cannot be applied four ways.
Owner, 2026-08-23: *"please concat all the spinner verbs together into a
RimMandrake_spinner_verbs.md file, and then set that to the project."*

🔴 THE EXCEPTION TABLE IS THE POINT. English doubling has no rule a script can apply:
a stressed final consonant-vowel-consonant doubles (`Trap` -> `Trapping`) and an
unstressed one does not (`Rivet` -> `Riveting`), and nothing in the spelling says which.
The table below is hand-checked. An audit pass caught SEVEN wrong forms that a naive
`+ing` had been emitting as real spinner words — Traping, Admiting, Defering, Forbiding,
Retconing, Retrofiting, Snapshoting. ⚠️ Add a stem here rather than "fixing" the rule.

⛔ Do not hand-edit RimMandrake_spinner_verbs.md or the `spinnerVerbs` block; both are
generated, and a hand edit is lost at the next run. Edit the four seat files.
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "RimMandrake_spinner_verbs.md")
SETTINGS = os.path.join(ROOT, ".claude", "settings.json")
ORDER = ["BUILD", "CHECK", "DECIDE", "REP"]
SRC = {s: os.path.join(HERE, "agent_%s_spinner_verbs.md" % s.lower()) for s in ORDER}

# Stems whose gerund a rule gets wrong. Hand-checked; extend rather than generalise.
DOUBLE = {
    "Log": "Logging", "Plan": "Planning", "Prod": "Prodding", "Spin": "Spinning",
    "Signal": "Signalling", "Corral": "Corralling", "Fit": "Fitting", "Cut": "Cutting",
    "Set": "Setting", "Run": "Running", "Ship": "Shipping", "Map": "Mapping",
    "Trim": "Trimming", "Wrap": "Wrapping", "Strip": "Stripping", "Swap": "Swapping",
    "Drop": "Dropping", "Stop": "Stopping", "Flag": "Flagging", "Tag": "Tagging",
    "Pin": "Pinning", "Scan": "Scanning", "Split": "Splitting", "Grep": "Grepping",
    "Debug": "Debugging", "Commit": "Committing", "Submit": "Submitting",
    "Permit": "Permitting", "Rig": "Rigging", "Trap": "Trapping", "Admit": "Admitting",
    "Defer": "Deferring", "Forbid": "Forbidding", "Retcon": "Retconning",
    "Plot": "Plotting", "Equip": "Equipping", "Retrofit": "Retrofitting",
    "Snapshot": "Snapshotting",
}


def gerund(v):
    if v in DOUBLE:
        return DOUBLE[v]
    if v.endswith("e") and not v.endswith(("ee", "ye", "oe")):
        return v[:-1] + "ing"
    return v + "ing"


def read_seat(path):
    t = io.open(path, encoding="utf-8").read()
    verbs = [re.sub(r"\*\*", "", m.group(1)).strip()
             for m in re.finditer(r"^\d+\.\s+(.+)$", t, re.M)]
    blurb = next((l for l in t.split("\n") if l.startswith("A ")), "")
    return verbs, blurb


def build():
    seat_verbs, blurb = {}, {}
    for s in ORDER:
        seat_verbs[s], blurb[s] = read_seat(SRC[s])
    seen, combined, owner = set(), [], {}
    for s in ORDER:
        for v in seat_verbs[s]:
            g = gerund(v)
            if g in seen:
                continue
            seen.add(g)
            combined.append(g)
            owner[g] = s
    return seat_verbs, blurb, combined, owner


def audit(combined):
    """-> gerunds that look like a missed doubling. Advisory: it over-reports drop-e
    forms (Coding, Framing), so read it, do not gate on it."""
    return [g for g in combined
            if re.search(r"[^aeiou][aeiou][bcdfglmnprtv]ing$", g)
            and not re.search(r"([bcdfglmnprtv])\1ing$", g)
            and len(g) <= 11]


HEAD = """# RimMandrake — the project's spinner verbs

**One pool, {n} verbs, shared by every seat.** Set as `spinnerVerbs` in
`.claude/settings.json`, so it is what the thinking spinner says in BUILD, CHECK, DECIDE
and REP windows alike.

🔑 **WHY ONE FILE AND NOT FOUR.** The per-seat lists in this folder are the source, but
`.claude/settings.json` is scoped to the **project**, not to the window — there is no
per-seat settings file in Claude Code. Four lists could not be applied four ways, so the
owner ruled 2026-08-23: *"please concat all the spinner verbs together into a
RimMandrake_spinner_verbs.md file, and then set that to the project."*

⚠️ **Verbs are stored here as PRESENT PARTICIPLES**, because that is the shape the
built-ins take (`Cogitating`, `Pondering`) and the setting substitutes the word directly.
The per-seat files hold the bare stems; this file holds what is actually displayed.

⛔ **{d} duplicates were dropped**, on first appearance in seat order. A repeat is not an
error — it only re-weights the random pick toward words several seats share.

🔴 **REGENERATE, DO NOT HAND-EDIT.** `Spinner/build_spinner_verbs.py` reads the four seat
files, converts, dedupes, audits and rewrites both this file and the setting. It carries a
hand-checked exception table because no rule gets English doubling right — the audit
caught **Traping, Admiting, Defering, Forbiding, Retconing, Retrofiting and Snapshoting**
being emitted as real spinner words.

## The seats these came from

{seats}

---

{body}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 if stale")
    args = ap.parse_args()
    seat_verbs, blurb, combined, owner = build()
    total = sum(len(v) for v in seat_verbs.values())
    md = HEAD.format(
        n=len(combined), d=total - len(combined),
        seats="\n".join("- **%s** — %s" % (s, blurb[s].rstrip(".") + ".") for s in ORDER),
        body="\n".join("%d. **%s**  <sub>%s</sub>" % (i + 1, g, owner[g])
                       for i, g in enumerate(combined)))
    settings = json.load(io.open(SETTINGS, encoding="utf-8"))
    want = {"mode": "replace", "verbs": combined}
    if args.check:
        stale = (io.open(OUT, encoding="utf-8").read() != md
                 or settings.get("spinnerVerbs") != want)
        print("STALE — run without --check" if stale else
              "current: %d verbs in both the md and the setting" % len(combined))
        return 1 if stale else 0
    io.open(OUT, "w", encoding="utf-8").write(md)
    settings["spinnerVerbs"] = want
    io.open(SETTINGS, "w", encoding="utf-8").write(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
    sus = audit(combined)
    print("%d verbs from %d (%d duplicates dropped) -> %s and spinnerVerbs"
          % (len(combined), total, total - len(combined), os.path.relpath(OUT, ROOT)))
    if sus:
        print("audit, advisory only — eyeball for a missed doubling: %s"
              % ", ".join(sus[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
