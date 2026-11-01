#!/usr/bin/env python3
"""Read-only census of the lane's INVALID results: the first look for an OPS_STEVE_DIAGNOSE_INVALID alarm.

  invalid_census.py [--since T] [--until T]     one line per INVALID/INTERRUPTED/REFUSED job, oldest first, then counts
  --require-all TEXT --min N                    exit 1 unless at least N jobs are INVALID and all of them carry TEXT
  --forbid TEXT                                 exit 1 if any INVALID job carries TEXT
  --selftest                                    prove the above on a made-up queue

Reads $TESTQ_QUEUE/done (the path ops_watch reads). Exit 2: a record is unreadable, or the window holds no job at all,
so the census saw nothing and may not vouch for anything. TEXT is matched against the cause, note and row details.
"""
import argparse
import collections
import glob
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

NOT_DONE = ("INVALID", "INTERRUPTED", "REFUSED")


def qhome():
    return Path(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"))


def when(s):
    """A timestamp, with or without seconds, -> aware UTC datetime. A bad one raises: a window must never be guessed."""
    s = s.strip().replace("Z", "+00:00")
    t = datetime.fromisoformat(s)
    return t.astimezone(timezone.utc) if t.tzinfo else t.replace(tzinfo=timezone.utc)


def read_done(since=None, until=None):
    """-> (jobs oldest first as (finished, record), unreadable file names). A record with no readable finish is unread."""
    jobs, bad = [], []
    for f in glob.glob(str(qhome() / "done" / "*.json")):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            fin = when(d.get("finished") or d["result"]["finished"])
            d["job"]["id"], d["result"]["outcome"]
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            bad.append(os.path.basename(f))
            continue
        if (since is None or fin >= since) and (until is None or fin <= until):
            jobs.append((fin, d))
    jobs.sort(key=lambda x: x[0])
    return jobs, bad


def text_of(d):
    r = d["result"]
    rows = r.get("rows") if isinstance(r.get("rows"), list) else []
    return "\n".join([str(r.get("cause")), str(r.get("note"))]
                     + [str(x.get("detail")) for x in rows if isinstance(x, dict)])


def run(a, out=sys.stdout):
    jobs, bad = read_done(when(a.since) if a.since else None, when(a.until) if a.until else None)
    for fin, d in jobs:
        r = d["result"]
        if r["outcome"] in NOT_DONE:
            note = " ".join(str(r.get("note")).split())[:110]
            print("%s %s %s/%s %s" % (fin.strftime("%Y-%m-%dT%H:%MZ"), d["job"]["id"], r["outcome"], r.get("cause"), note),
                  file=out)
    invalid = [d for _, d in jobs if d["result"]["outcome"] == "INVALID"]
    print("%d job(s): %s; INVALID causes: %s" % (
        len(jobs), dict(collections.Counter(d["result"]["outcome"] for _, d in jobs)),
        dict(collections.Counter(str(d["result"].get("cause")) for d in invalid))), file=out)
    if bad:
        print("UNREADABLE %d record(s): %s" % (len(bad), bad[:5]), file=out)
        return 2
    if not jobs:
        print("NO JOB in the window under %s: nothing seen, nothing vouched for" % (qhome() / "done"), file=out)
        return 2
    rc = 0
    if a.require_all is not None:
        have = [d for d in invalid if a.require_all in text_of(d)]
        if len(invalid) < a.min or len(have) != len(invalid):
            print("FAIL: %d of %d INVALID job(s) carry %r, wanted all of at least %d" % (
                len(have), len(invalid), a.require_all, a.min), file=out)
            rc = 1
    if a.forbid is not None:
        hit = [d["job"]["id"] for d in invalid if a.forbid in text_of(d)]
        if hit:
            print("FAIL: %d INVALID job(s) carry %r: %s" % (len(hit), a.forbid, hit[:10]), file=out)
            rc = 1
    return rc


def selftest():
    def job(i, fin, oc, cause=None, note=None, detail=None):
        return {"finished": fin, "job": {"id": i},
                "result": {"outcome": oc, "cause": cause, "note": note, "rows": [{"detail": detail}] if detail else []}}
    def rc(**kw):
        a = argparse.Namespace(since=None, until=None, require_all=None, min=1, forbid=None)
        vars(a).update(kw)
        with open(os.devnull, "w", encoding="utf-8") as sink:
            return run(a, sink)
    with tempfile.TemporaryDirectory() as t:
        os.environ["TESTQ_QUEUE"] = t
        done = Path(t) / "done"
        done.mkdir()
        recs = [job("a", "2026-01-01T10:00:00Z", "INVALID", "CANARY", detail="canary red: no live colonist"),
                job("b", "2026-01-01T11:00:00Z", "INVALID", "CANARY", note="no live colonist here"),
                job("c", "2026-01-02T10:00:00Z", "DONE"),
                job("d", "2026-01-03T10:00:00Z", "INVALID", "HARNESS", note="crash")]
        for r in recs:
            (done / (r["job"]["id"] + ".json")).write_text(json.dumps(r), encoding="utf-8")
        day1 = {"since": "2026-01-01T00:00Z", "until": "2026-01-01T23:59Z"}
        checks = [
            ("all carry it", rc(require_all="no live colonist", min=2, **day1), 0),
            ("too few", rc(require_all="no live colonist", min=3, **day1), 1),
            ("one job lacks it", rc(require_all="no live colonist", min=1), 1),
            ("forbidden text in the window", rc(forbid="no live colonist"), 1),
            ("forbidden text before the window", rc(forbid="no live colonist", since="2026-01-02T00:00Z"), 0),
            ("empty window vouches for nothing", rc(forbid="x", since="2027-01-01T00:00Z"), 2),
        ]
        (done / "broken.json").write_text("{", encoding="utf-8")
        checks.append(("unreadable record", rc(forbid="x"), 2))
    wrong = [(n, got, want) for n, got, want in checks if got != want]
    print("invalid_census selftest: %d of %d ok %s" % (len(checks) - len(wrong), len(checks), wrong or ""))
    return 1 if wrong else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--require-all")
    p.add_argument("--min", type=int, default=1)
    p.add_argument("--forbid")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    return selftest() if a.selftest else run(a)


if __name__ == "__main__":
    sys.exit(main())
