#!/usr/bin/env python3
"""driver_death_recurrence.py - did a live driver die mid bridge call again after a given failure?

MODCHECK_DIAGNOSE_DRIVER_DIES_MID_SETFOG: testq J20261026T182927Z-c2508c's drawbridge_proof died <1 s after sending
jawa/set_fog (no timeout; the game answered the next client in 17 ms), stranding an UNKNOWN-outcome marker that made
modcheck crash with no sheet. Its done-condition: the cause named from the driver tail, or no recurrence in 3 runs.

Reads every finished job under TESTQ_QUEUE/done (default /mnt/d/ClaudeWork/rimmandrake/testq/done) and, for jobs that
started after --since:
  CLEAN    the driver ran to a result: a row of --chain whose detail opens with '<--result-stem>_<YYYYMMDDTHHMMSS>.json:'
           (the shape drawbridge_proof's result rows carry; 'no drawbridge_result_*.json' does not match)
  RECUR    a job whose selector names --chain, and whose note or any row names an UNKNOWN-outcome mutating call
           or 'client interrupted'. The same class in a job that did not run --chain is listed (OTHER DRIVERS), not
           counted: the job record does not say which script stranded the call.
Exit 0 when CLEAN >= --need and RECUR == 0 and every record was readable; 1 when the counts fail; 2 when nothing can
be read, or a would-be PASS rests on unreadable records (one of them could be the recurrence; never a silent 0).

The live queue is on the Windows data root, which a checker in another sandbox cannot reach. When the done dir is
absent the committed SNAPSHOT is read instead, and the output says so: a distillation of every done record started
after SNAPSHOT_SINCE (the fields scan() reads, plus each source file's sha256). Refresh it with --snapshot.
Sanity probe on either source: the seed failure (--seed) must itself be seen as a recurrence when it is in the data,
or the instrument is blind and the verdict is UNMEASURED.

  python3 src/RimMandrake/Utils/testq/driver_death_recurrence.py [--since 2026-10-26T18:34:00Z] [--need 3]
  python3 src/RimMandrake/Utils/testq/driver_death_recurrence.py --snapshot   # rewrite the committed snapshot
"""
import argparse
import datetime
import glob
import gzip
import hashlib
import json
import os
import re
import sys
import zlib

QHOME = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures",
                        "driver_death_recurrence_snapshot.jsonl.gz")
SNAPSHOT_SINCE = "2026-10-26T18:00:00Z"
SEED = "J20261026T182927Z-c2508c"
RECUR_RE = re.compile(r"earlier mutating call\(s\) have an UNKNOWN outcome|client interrupted")


def parse_ts(s):
    """An ISO UTC timestamp as an aware datetime, or None. Compared as times, never as strings ('...:00.5Z' sorts
    before '...:00Z' as text)."""
    try:
        t = datetime.datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else None


def read_dir(done_dir):
    """(records, unreadable): records are (basename, record, sha256) for every *.json in done_dir."""
    recs, unreadable = [], []
    for p in sorted(glob.glob(os.path.join(done_dir, "*.json"))):
        try:
            with open(p, "rb") as fh:
                raw = fh.read()
            rec = json.loads(raw.decode("utf-8"))
        except (OSError, ValueError, RecursionError) as ex:
            unreadable.append("%s: %s" % (os.path.basename(p), type(ex).__name__))
            continue
        recs.append((os.path.basename(p), rec, hashlib.sha256(raw).hexdigest()))
    return recs, unreadable


def problem(rec):
    """Why a parsed record cannot be assessed, or None. Every shape scan() relies on is checked here, so a record
    it would otherwise skip or misfile (no result, no selector to attribute a recurrence, a row that is not an
    object) is reported unreadable instead. A selector with no 'chains' (650 of 661 records carry a list, MEASURED
    2026-11-02; the rest select by something else) is a real shape, not a problem."""
    if not isinstance(rec, dict):
        return "record is not an object"
    res, job = rec.get("result"), rec.get("job")
    if not isinstance(res, dict):
        return "no result object"
    if not isinstance(job, dict) or not isinstance(job.get("selector"), dict):
        return "no job selector"
    if not isinstance(job["selector"].get("chains"), (list, type(None))):
        return "selector chains is not a list"
    rows = res.get("rows")
    if not isinstance(rows, (list, type(None))) or not all(isinstance(r, dict) for r in rows or []):
        return "rows is not a list of objects"
    return None


def distill(rec):
    """The fields scan() reads, nothing else; the record must have passed problem()."""
    res, sel = rec["result"], rec["job"]["selector"]
    rows = [{"chain": r.get("chain"), "detail": r.get("detail")} for r in (res.get("rows") or [])]
    return {"job": {"selector": {"chains": list(sel.get("chains") or [])}},
            "result": {"job": res.get("job"), "started": res.get("started"), "note": res.get("note"), "rows": rows}}


def write_snapshot(done_dir, out, since=SNAPSHOT_SINCE, taken=None):
    recs, unreadable = read_dir(done_dir)
    cut, body = parse_ts(since), []
    for name, rec, sha in recs:
        why = problem(rec)
        if why:                                         # unassessable: it stays on record, never silently dropped
            unreadable.append("%s: %s" % (name, why))
            continue
        d = distill(rec)
        t = parse_ts(d["result"].get("started")) if d is not None else None
        if t is None or t > cut:   # an undatable record is kept: the reader must flag it
            d["file"], d["sha256"] = name, sha
            body.append(d)
    if not body:
        raise SystemExit("refused: %s holds no job started after %s; snapshot not written" % (done_dir, since))
    head = {"snapshot": "driver_death_recurrence", "source": done_dir, "since": since, "records": len(body),
            "unreadable": unreadable,
            "taken": taken or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:   # mtime 0: stable bytes
        for line in [head] + body:
            gz.write((json.dumps(line, sort_keys=True) + "\n").encode("utf-8"))
    return head


def read_snapshot(path):
    """(head, records): records are (file, distilled record, sha256 of the source file)."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        lines = [json.loads(ln) for ln in fh if ln.strip()]
    if not lines or not isinstance(lines[0], dict) or lines[0].get("snapshot") != "driver_death_recurrence":
        raise ValueError("%s is not a driver_death_recurrence snapshot" % path)
    head, body = lines[0], lines[1:]
    if parse_ts(head.get("since")) is None:
        raise ValueError("%s header has no parseable since: %r" % (path, head.get("since")))
    if not isinstance(head.get("unreadable", []), list):
        raise ValueError("%s header's unreadable is not a list" % path)
    if head.get("records") != len(body):
        raise ValueError("%s header says %s records, body holds %d" % (path, head.get("records"), len(body)))
    bad = [i for i, r in enumerate(body) if not isinstance(r, dict)]
    if bad:
        raise ValueError("%s body lines %s are not objects" % (path, bad[:5]))
    return head, [(r.get("file"), r, r.get("sha256")) for r in body]


def scan(records, since, chain, stem):
    """since: an aware datetime, or None for every record. A result with no parseable 'started' cannot be placed
    against since, and a record failing problem() cannot be assessed at all: both are returned as undated (the
    caller treats them as unreadable), never silently skipped."""
    clean, recur, elsewhere, other, undated, seen = [], [], [], [], [], 0
    result_re = re.compile(r"\s*%s_\d{8}T\d{6}\.json:" % re.escape(stem))
    for name, rec, _sha in records:
        why = problem(rec)
        if why:
            undated.append("%s: %s" % (name, why))
            continue
        res = rec["result"]
        seen += 1
        jid = res.get("job") or str(name)[:-5]
        started = parse_ts(res.get("started"))
        if started is None:
            undated.append("%s: no parseable started %r" % (jid, res.get("started")))
            continue
        if since is not None and started <= since:
            continue
        rows = res.get("rows") or []
        text = " ".join([str(res.get("note") or "")] + [str(r.get("detail") or "") for r in rows])
        job = rec.get("job") if isinstance(rec.get("job"), dict) else {}
        sel = job.get("selector") if isinstance(job.get("selector"), dict) else {}
        ran_chain = chain in (sel.get("chains") or []) or any(r.get("chain") == chain for r in rows)
        if RECUR_RE.search(text):
            (recur if ran_chain else elsewhere).append(jid)
            continue
        if any(r.get("chain") == chain and result_re.match(str(r.get("detail") or "")) for r in rows):
            clean.append(jid)
        elif any(r.get("chain") == chain for r in rows):
            other.append(jid)
    return seen, clean, recur, elsewhere, other, undated


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", default="2026-10-26T18:34:00Z", help="ISO UTC; jobs started after it count")
    ap.add_argument("--need", type=int, default=3)
    ap.add_argument("--chain", default="drawbridges")
    ap.add_argument("--result-stem", default="drawbridge_result")
    ap.add_argument("--seed", default=SEED, help="the failure the probe must see as a recurrence ('' skips)")
    ap.add_argument("--done-dir", default=os.path.join(QHOME, "done"))
    ap.add_argument("--fixture", default=None, help="read this snapshot instead of the done dir")
    ap.add_argument("--snapshot", nargs="?", const=SNAPSHOT, default=None, metavar="OUT",
                    help="write a snapshot of --done-dir (default: the committed one) and exit")
    a = ap.parse_args(argv)
    since = parse_ts(a.since)
    if since is None:
        ap.error("--since %r is not an ISO UTC timestamp (e.g. 2026-10-26T18:34:00Z)" % a.since)
    if a.snapshot:
        if not os.path.isdir(a.done_dir):
            print("UNMEASURED: no done dir at %s; snapshot not written" % a.done_dir)
            return 2
        head = write_snapshot(a.done_dir, a.snapshot)
        print("wrote %s: %d records started after %s (%d unreadable)"
              % (a.snapshot, head["records"], head["since"], len(head["unreadable"])))
        return 0
    fixture = a.fixture
    if fixture is None and not os.path.isdir(a.done_dir):
        print("live queue unreachable (no done dir at %s); reading the committed snapshot" % a.done_dir)
        fixture = SNAPSHOT
    if fixture:
        try:
            head, records = read_snapshot(fixture)
        except (OSError, ValueError, EOFError, zlib.error) as ex:
            print("UNMEASURED: snapshot %s unreadable: %s" % (fixture, ex))
            return 2
        if since < parse_ts(head["since"]):
            print("UNMEASURED: snapshot %s covers jobs after %s only; --since %s is earlier"
                  % (fixture, head["since"], a.since))
            return 2
        unreadable = list(head.get("unreadable") or [])
        src = "snapshot %s (taken %s from %s)" % (fixture, head.get("taken"), head.get("source"))
    else:
        records, unreadable = read_dir(a.done_dir)
        src = a.done_dir
    seen, clean, recur, elsewhere, other, undated = scan(records, since, a.chain, a.result_stem)
    unreadable += undated
    if not seen:      # sanity probe: an instrument that read nothing must not report "no recurrence"
        print("UNMEASURED: %s holds no readable job result" % src)
        return 2
    if a.seed:        # sanity probe: the failure this check exists for must read as a recurrence
        _s, _c, seed_recur, _e, _o, _u = scan([r for r in records if isinstance(r[1], dict)
                                           and isinstance(r[1].get("result"), dict)
                                           and r[1]["result"].get("job") == a.seed],
                                          None, a.chain, a.result_stem)
        if not _s:
            print("sanity: seed %s not in %s (probe skipped)" % (a.seed, src))
        elif a.seed not in seed_recur:
            print("UNMEASURED: the seed failure %s does not read as a recurrence; the instrument is blind" % a.seed)
            return 2
        else:
            print("sanity: seed %s reads as a recurrence" % a.seed)
    print("read %d job results (%d unreadable) in %s; after %s:" % (seen, len(unreadable), src, a.since))
    print("  CLEAN %d (the %s driver ran to a %s_*.json row): %s" % (len(clean), a.chain, a.result_stem,
                                                                    ", ".join(clean)))
    print("  RECUR %d (UNKNOWN-outcome mutating call or 'client interrupted'): %s" % (len(recur), ", ".join(recur)))
    print("  OTHER DRIVERS %d (same class in jobs that did not run %s; not counted): %s"
          % (len(elsewhere), a.chain, ", ".join(elsewhere)))
    print("  chain ran without a driver-result row (not this failure; see the job): %s" % ", ".join(other))
    ok = len(clean) >= a.need and not recur
    if ok and unreadable:
        print("UNMEASURED: the counts pass but %d record(s) were unreadable, and any could be a recurrence: %s"
              % (len(unreadable), ", ".join(unreadable)))
        return 2
    print("%s: %d clean of %d needed, %d recurrence(s)" % ("PASS" if ok else "FAIL", len(clean), a.need, len(recur)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
