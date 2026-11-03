#!/usr/bin/env python3
"""selftest_unproven_legs_triage.py -- the proof of UNPROVEN_LIVE_LEGS_TRIAGE_1 (offline half).

A1: each of the four triaged items carries a ledger note from the triage giving every scoped leg a verdict from the
    triage's vocabulary and a NEXT.
A2: every item named in a NEXT exists (a `file` event and its items/<ID>.md); the legs found bridge-measurable now are
    bound to live proofs in infrastructure/state/live_proofs/UNPROVEN_LIVE_LEGS_TRIAGE_1.txt whose bars exist (each
    live-proof line rerun with --mock, which exits 0 only when every named bar is present in a mock suite run).
Planted breaks (a note missing a leg, a verdict word, a NEXT; a NEXT naming an unfiled item) must redden, so a
blind parser cannot pass. Exit 0 green, 1 red.
"""
import glob
import json
import os
import re
import shlex
import subprocess
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ITEM = "UNPROVEN_LIVE_LEGS_TRIAGE_1"
SCOPE = {   # the item's spec: which owed legs of which item this triage covers
    "CAULDRON_ENRICHMENT_LIVE_PROOF_1": ["A4"],
    "FEVERWOOD_BROOD_RANSOM_1": ["A3", "A4"],
    "RUSTCATHEDRAL_BASE_FINISH_BUILD_1": ["A5", "A6", "A7", "A8", "A9"],
    "FORGE_ENRICHMENT_QUICKTEST_1": ["A3", "A4"],
}
VERDICTS = ("BRIDGE-MEASURABLE NOW", "NEEDS A TOOL", "NEEDS A GENERATED MAP", "OWNER")
LEG = re.compile(r"\bA(\d+)(?:-A(\d+))?\b")
NEXT_IDS = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")


def events():
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "infrastructure/state/ledger/events/*.jsonl"))):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def leg_segments(text):
    """-> {leg: text from its mention up to the next leg mention}. 'A5-A9' covers A5..A9."""
    marks = list(LEG.finditer(text))
    seg = {}
    for i, m in enumerate(marks):
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
        body = text[m.start(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        for n in range(lo, hi + 1):
            seg.setdefault("A%d" % n, "")
            seg["A%d" % n] += " " + body
    return seg


def note_problems(item, legs, text):
    bad = []
    if "NEXT:" not in text:
        bad.append("%s: triage note has no NEXT" % item)
    seg = leg_segments(text)
    for leg in legs:
        if leg not in seg:
            bad.append("%s: leg %s has no verdict in the triage note" % (item, leg))
        elif not any(v in seg[leg] for v in VERDICTS):
            bad.append("%s: leg %s is mentioned without a verdict word %s" % (item, leg, VERDICTS))
    return bad


def next_ids(text):
    return [i for i in NEXT_IDS.findall(text.split("NEXT:", 1)[-1]) if i != ITEM]


def check(evs, filed):
    bad = []
    for item, legs in SCOPE.items():
        notes = [e.get("text", "") for e in evs if e.get("event") == "note" and e.get("id") == item
                 and (e.get("text") or "").startswith(ITEM + " triage")]
        if not notes:
            bad.append("%s: no triage note" % item)
            continue
        text = notes[-1]
        bad += note_problems(item, legs, text)
        for nid in next_ids(text):
            if nid not in filed:
                bad.append("%s: NEXT names %s, which has no file event" % (item, nid))
            elif not os.path.exists(os.path.join(REPO, "infrastructure/state/items", nid + ".md")):
                bad.append("%s: NEXT names %s, which has no items/%s.md" % (item, nid, nid))
    return bad


def live_lines():
    p = os.path.join(REPO, "infrastructure/state/live_proofs", ITEM + ".txt")
    with open(p) as f:
        return [l.split(":", 1)[1].strip() for l in f if l.startswith("live-proof ")]


def mock_bars(cmd):
    argv = shlex.split(cmd.split("<", 1)[0])
    rc = subprocess.run(argv + ["--mock"], cwd=REPO, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, timeout=500).returncode
    return rc


def planted(evs, filed):
    """Each break must redden; returns the breaks that did NOT."""
    good = "%s triage. A3 = NEEDS A TOOL x. A4 = BRIDGE-MEASURABLE NOW y. NEXT: do it." % ITEM
    missed = []
    cases = {
        "missing leg": note_problems("X", ["A3", "A4", "A5"], good),
        "no verdict": note_problems("X", ["A3"], "%s triage. A3 is hard. NEXT: z." % ITEM),
        "no NEXT": note_problems("X", ["A3", "A4"], good.replace("NEXT:", "then")),
        "range gap": note_problems("X", ["A9"], "%s triage. A5-A8 = NEEDS A TOOL. NEXT: z." % ITEM),
    }
    for name, probs in cases.items():
        if not probs:
            missed.append(name)
    if note_problems("X", ["A5", "A7", "A9"], "%s triage. A5-A9 = NEEDS A TOOL. NEXT: z." % ITEM):
        missed.append("range A5-A9 not expanded (false red)")
    fake = [dict(e) for e in evs]
    for e in fake:
        if e.get("event") == "note" and e.get("id") in SCOPE and (e.get("text") or "").startswith(ITEM + " triage"):
            e["text"] = e["text"].replace("NEXT:", "NEXT: build NO_SUCH_ITEM_FILED_EVER, and")
    if not any("NO_SUCH_ITEM_FILED_EVER" in b for b in check(fake, filed)):
        missed.append("unfiled NEXT id")
    return missed


def main():
    evs = events()
    filed = {e.get("id") for e in evs if e.get("event") == "file"}
    bad = check(evs, filed)
    missed = planted(evs, filed)
    bad += ["planted break did not redden: %s" % m for m in missed]
    lines = live_lines()
    if len(lines) < 2:
        bad.append("live_proofs file binds %d live-proof lines, expected the Cauldron and Forge lines" % len(lines))
    if "--fast" not in sys.argv:
        for cmd in lines:
            if mock_bars(cmd) != 0:
                bad.append("live-proof bars absent in a mock run: %s" % cmd)
    for b in bad:
        print("RED  " + b)
    print("%s: %s (%d items, %d live lines)" % (ITEM, "GREEN" if not bad else "RED", len(SCOPE), len(lines)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
