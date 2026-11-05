#!/usr/bin/env python3
"""Selftest for owner_rulings.py, plus the item's re-probe bar (OWNER_RULINGS_HARDEN_DATES_ON_DISK).

1. A synthetic ledger with known answers: dated said/card rows print with their date, undated
   rows are refused, repeated words keep their FIRST date, filters work.
2. The real ledger: the instrument can see (a known 2026-11-02 card ruling is found, dated).
3. The committed re-probe record dates >= 80% of rulings while its summary alone does not.

    python3 src/RimMandrake/rimflow/selftest_owner_rulings.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import owner_rulings as orl  # noqa: E402

REPO = orl.REPO
FAIL = []


def check(cond, what):
    if not cond:
        FAIL.append(what)


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = orl.main(argv)
    return rc, buf.getvalue().splitlines()


with tempfile.TemporaryDirectory() as d:
    ev = [
        {"id": "KELP_X", "ownerSaid": "Kelp beds never spawn below minus five.", "ts": "2026-10-24T19:17:00Z"},
        {"id": "KELP_Y", "ownerSaid": "Kelp  beds never spawn below minus five.", "ts": "2026-10-28T09:00:00Z"},
        {"id": "CARD_Z", "byCard": "Night budget → four", "ts": "2026-10-25T11:30:00Z"},
        {"id": "UNDATED", "ownerSaid": "No date on this one.", "ts": ""},
        {"id": "PLAIN", "why": "agent words are not his", "ts": "2026-10-26T07:36:00Z"},
    ]
    with open(os.path.join(d, "A.jsonl"), "w") as f:
        for e in ev:
            f.write(json.dumps(e) + "\n")
        f.write("{torn line\n")
    rows = orl.rulings(d)
    check(len(rows) == 2, f"synthetic: expected 2 rulings, got {len(rows)}: {rows}")
    kelp = [r for r in rows if r["words"].startswith("Kelp")]
    check(len(kelp) == 1 and kelp[0]["ts"].startswith("2026-10-24") and kelp[0]["id"] == "KELP_X",
          f"synthetic: repeated words must keep the first date: {kelp}")
    check(not any(r["id"] == "UNDATED" for r in rows), "synthetic: undated ruling printed")
    rc, out = run(["--events", d, "--last", "0"])
    check(rc == 0 and out and out[0].startswith('2026-10-24 19:17Z  said  KELP_X  "Kelp'),
          f"synthetic: line shape wrong: {out}")
    rc, out = run(["--events", d, "--kind", "card", "--last", "0"])
    check(len(out) == 1 and "2026-10-25" in out[0] and "card" in out[0], f"synthetic: --kind card: {out}")
    rc, out = run(["--events", d, "--since", "2026-10-25", "--last", "0"])
    check(len(out) == 1 and "CARD_Z" in out[0], f"synthetic: --since: {out}")
    rc, out = run(["--events", d, "--grep", "KELP", "--last", "0"])
    check(len(out) == 1, f"synthetic: --grep over id: {out}")

# 2. the real ledger: sanity probe that the instrument sees a ruling we know exists
rc, out = run(["--grep", "What should happen to FOUNDRY.*Retire it", "--kind", "card", "--since", "2026-11-02", "--last", "0"])
check(rc == 0 and any(o.startswith("2026-11-0") for o in out),
      "real ledger: the FOUNDRY 'Retire it' card ruling (2026-11-02) was not found dated")
allrows = orl.rulings()
check(len(allrows) > 100, f"real ledger: only {len(allrows)} dated rulings seen; instrument blind?")

# 3. the re-probe bar
rec = json.load(open(os.path.join(REPO, "design", "RimMandrake", "compaction_retention_reprobe_2026-11-05.json")))
n = rec["rulings"]
qd = sum(v == "present" for k, v in rec["grade"]["quiz"].items() if k.startswith("ruling_date_"))
check(n == 5 and qd == rec["quiz_dates_present"], "re-probe: record counts disagree with its own grade")
check(qd / n >= 0.8, f"re-probe: only {qd}/{n} ruling dates recovered (bar 80%)")

if FAIL:
    print("FAIL selftest_owner_rulings")
    for x in FAIL:
        print("  -", x)
    sys.exit(1)
print(f"PASS selftest_owner_rulings ({len(allrows)} dated rulings on the ledger; re-probe {qd}/{n} dated)")
