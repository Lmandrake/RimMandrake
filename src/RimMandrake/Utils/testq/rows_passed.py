#!/usr/bin/env python3
"""testq/rows_passed.py -- did a finished test-lane run pass these rows? An outcome check for a live ticket.

  python3 src/RimMandrake/Utils/testq/rows_passed.py MOD SINCE SEL [SEL ...] [--reports DIR]

SEL is `chain` (every row of that chain, at least one) or `chain/row`. SINCE is an ISO stamp (`YYYY-MM-DDTHH:MM:SSZ`):
only jobs submitted at or after it count, so a check written before its run cannot be met by an older run.
Two sources: the testq done queue (a lane job), and modcheck reports `<MOD>_<stamp>.json` in DIR (default the repo's
Transient/modcheck/, where a pinned report of a run by hand on an Archmagi game travels with git).
Exit 0: one DONE job or report of MOD since SINCE carries every selected row, each PASS (prints `PASS <job>`).
Exit 1: none does (prints the nearest job and what it lacked, or that no job ran).
Exit 2: could not look (no done queue and no report folder on this host). Never a FAIL and never a PASS.
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


def iso(stamp):
    """modcheck's `20261114T131233Z` -> testq's `2026-11-14T13:12:33Z`; anything else unchanged."""
    t = str(stamp or "")
    if len(t) == 16 and t[8] == "T" and t.endswith("Z"):
        return "%s-%s-%sT%s:%s:%sZ" % (t[0:4], t[4:6], t[6:8], t[9:11], t[11:13], t[13:15])
    return t


def load_reports(rep_dir, mod):
    """modcheck reports of MOD in REP_DIR, shaped as done records (outcome DONE: a report is a finished run)."""
    recs = []
    for f in glob.glob(os.path.join(rep_dir, glob.escape(mod) + "_*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        chains = ((d or {}).get("summary") or {}).get("chains") or []
        rows = [{"chain": c.get("name"), "row": x.get("name"), "verdict": x.get("verdict")}
                for c in chains for x in c.get("components") or []]
        recs.append({"job": {"id": os.path.splitext(os.path.basename(f))[0], "mod": d.get("mod") or mod,
                             "submitted": iso(d.get("stamp"))},
                     "result": {"outcome": "DONE", "rows": rows}})
    return recs


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rep_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))),
                           "Transient", "modcheck")
    if "--reports" in argv:
        i = argv.index("--reports")
        rep_dir = argv[i + 1] if i + 1 < len(argv) else ""
        del argv[i:i + 2]
    if len(argv) < 3:
        print(__doc__)
        return 2
    mod, since, sels = argv[0], argv[1], argv[2:]
    done = os.environ.get("TESTQ_DONE_DIR")
    if not done:
        sys.path.insert(0, HERE)
        import testq as T
        done = os.path.join(T.QHOME, "done")
    if not os.path.isdir(done) and not os.path.isdir(rep_dir):
        print("UNMEASURED: no done queue at %s and no report folder at %s on this host" % (done, rep_dir))
        return 2
    recs = (load(done) if os.path.isdir(done) else []) + (load_reports(rep_dir, mod) if os.path.isdir(rep_dir) else [])
    jid, why = check(recs, mod, since, sels)
    print(("PASS %s: " % jid if jid else "FAIL: ") + why)
    return 0 if jid else 1


if __name__ == "__main__":
    sys.exit(main())
