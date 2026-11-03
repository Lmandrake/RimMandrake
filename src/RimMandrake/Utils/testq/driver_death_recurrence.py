#!/usr/bin/env python3
"""driver_death_recurrence.py - did a live driver die mid bridge call again after a given failure?

MODCHECK_DIAGNOSE_DRIVER_DIES_MID_SETFOG: testq J20261026T182927Z-c2508c's drawbridge_proof died <1 s after sending
jawa/set_fog (no timeout; the game answered the next client in 17 ms), stranding an UNKNOWN-outcome marker that made
modcheck crash with no sheet. Its done-condition: the cause named from the driver tail, or no recurrence in 3 runs.

Reads every finished job under TESTQ_QUEUE/done (default /mnt/d/ClaudeWork/rimmandrake/testq/done) and, for jobs that
started after --since:
  CLEAN    the driver ran to a result: a row of --chain whose detail cites a '<--result-stem>_<ts>.json'
  RECUR    a job whose selector names --chain, and whose note or any row names an UNKNOWN-outcome mutating call
           or 'client interrupted'. The same class in a job that did not run --chain is listed (OTHER DRIVERS), not
           counted: the job record does not say which script stranded the call.
Exit 0 when CLEAN >= --need and RECUR == 0; 1 otherwise; 2 when the queue cannot be read (never a silent 0).

  python3 src/RimMandrake/Utils/testq/driver_death_recurrence.py [--since 2026-10-26T18:34:00Z] [--need 3]
"""
import argparse
import glob
import json
import os
import re
import sys

QHOME = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
RECUR_RE = re.compile(r"earlier mutating call\(s\) have an UNKNOWN outcome|client interrupted")


def scan(done_dir, since, chain, stem):
    clean, recur, elsewhere, other, unreadable, seen = [], [], [], [], [], 0
    for p in sorted(glob.glob(os.path.join(done_dir, "*.json"))):
        try:
            with open(p, encoding="utf-8") as fh:
                rec = json.load(fh)
        except (OSError, ValueError, RecursionError) as ex:
            unreadable.append("%s: %s" % (os.path.basename(p), type(ex).__name__))
            continue
        res = rec.get("result") if isinstance(rec, dict) else None
        if not isinstance(res, dict):
            continue
        seen += 1
        if str(res.get("started") or "") <= since:
            continue
        jid = res.get("job") or os.path.basename(p)[:-5]
        rows = [r for r in (res.get("rows") or []) if isinstance(r, dict)]
        text = " ".join([str(res.get("note") or "")] + [str(r.get("detail") or "") for r in rows])
        job = rec.get("job") if isinstance(rec.get("job"), dict) else {}
        sel = job.get("selector") if isinstance(job.get("selector"), dict) else {}
        ran_chain = chain in (sel.get("chains") or []) or any(r.get("chain") == chain for r in rows)
        if RECUR_RE.search(text):
            (recur if ran_chain else elsewhere).append(jid)
            continue
        if any(r.get("chain") == chain and (stem + "_") in str(r.get("detail") or "") for r in rows):
            clean.append(jid)
        elif any(r.get("chain") == chain for r in rows):
            other.append(jid)
    return seen, clean, recur, elsewhere, other, unreadable


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", default="2026-10-26T18:34:00Z", help="ISO UTC; jobs started after it count")
    ap.add_argument("--need", type=int, default=3)
    ap.add_argument("--chain", default="drawbridges")
    ap.add_argument("--result-stem", default="drawbridge_result")
    ap.add_argument("--done-dir", default=os.path.join(QHOME, "done"))
    a = ap.parse_args(argv)
    if not os.path.isdir(a.done_dir):
        print("UNMEASURED: no done dir at %s" % a.done_dir)
        return 2
    seen, clean, recur, elsewhere, other, unreadable = scan(a.done_dir, a.since, a.chain, a.result_stem)
    if not seen:      # sanity probe: an instrument that read nothing must not report "no recurrence"
        print("UNMEASURED: %s holds no readable job result" % a.done_dir)
        return 2
    print("read %d job results (%d unreadable) in %s; after %s:" % (seen, len(unreadable), a.done_dir, a.since))
    print("  CLEAN %d (the %s driver ran to a %s_*.json row): %s" % (len(clean), a.chain, a.result_stem,
                                                                    ", ".join(clean)))
    print("  RECUR %d (UNKNOWN-outcome mutating call or 'client interrupted'): %s" % (len(recur), ", ".join(recur)))
    print("  OTHER DRIVERS %d (same class in jobs that did not run %s; not counted): %s"
          % (len(elsewhere), a.chain, ", ".join(elsewhere)))
    print("  chain ran without a driver-result row (not this failure; see the job): %s" % ", ".join(other))
    ok = len(clean) >= a.need and not recur
    print("%s: %d clean of %d needed, %d recurrence(s)" % ("PASS" if ok else "FAIL", len(clean), a.need, len(recur)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
