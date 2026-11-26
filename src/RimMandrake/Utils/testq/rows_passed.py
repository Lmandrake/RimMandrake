#!/usr/bin/env python3
"""testq/rows_passed.py -- did a finished test-lane run pass these rows? An outcome check for a live ticket.

  python3 src/RimMandrake/Utils/testq/rows_passed.py MOD SINCE SEL [SEL ...]

SEL is `chain` (every row of that chain, at least one) or `chain/row`. SINCE is an ISO stamp (`YYYY-MM-DDTHH:MM:SSZ`):
only jobs submitted at or after it count, so a check written before its run cannot be met by an older run.
Exit 0: one DONE job of MOD since SINCE carries every selected row, each PASS (prints `PASS <job>`).
Exit 1: none does (prints the nearest job and what it lacked, or that no job ran).
Exit 2: could not look (no done queue on this host). A missing queue is never a FAIL and never a PASS.
Written for ASTEROID_DESERT_ORES_1 (work bundle WB-game-ship-20261126-164518), whose live rows run on SteveDesktop."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def judge(rec, sels):
    """-> (ok, why) for one done record against the selectors."""
    res = (rec or {}).get("result") or {}
    if res.get("outcome") != "DONE":
        return False, "outcome %s" % res.get("outcome")
    rows = res.get("rows") or []
    for sel in sels:
        chain, _, row = sel.partition("/")
        hit = [r for r in rows if r.get("chain") == chain and (not row or r.get("row") == row)]
        if not hit:
            return False, "no row %s" % sel
        bad = [(r.get("row"), r.get("verdict")) for r in hit if r.get("verdict") != "PASS"]
        if bad:
            return False, "%s: %s" % (sel, ", ".join("%s %s" % b for b in bad))
    return True, "%d selector(s) all PASS" % len(sels)


def check(recs, mod, since, sels):
    """-> (job id or None, why)."""
    nearest = None
    for rec in sorted(recs, key=lambda r: str(((r or {}).get("job") or {}).get("submitted") or "")):
        job = (rec or {}).get("job") or {}
        if job.get("mod") != mod or str(job.get("submitted") or "") < since:
            continue
        ok, why = judge(rec, sels)
        if ok:
            return job.get("id"), why
        nearest = "%s: %s" % (job.get("id"), why)
    return None, nearest or "no done %s job submitted since %s" % (mod, since)


def load(done_dir):
    recs = []
    for f in glob.glob(os.path.join(done_dir, "*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                recs.append(json.load(fh))
        except (OSError, ValueError):
            continue        # a record mid-write: the next check reads it
    return recs


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 3:
        print(__doc__)
        return 2
    mod, since, sels = argv[0], argv[1], argv[2:]
    done = os.environ.get("TESTQ_DONE_DIR")
    if not done:
        sys.path.insert(0, HERE)
        import testq as T
        done = os.path.join(T.QHOME, "done")
    if not os.path.isdir(done):
        print("UNMEASURED: no done queue at %s on this host" % done)
        return 2
    jid, why = check(load(done), mod, since, sels)
    print(("PASS %s: " % jid if jid else "FAIL: ") + why)
    return 0 if jid else 1


if __name__ == "__main__":
    sys.exit(main())
