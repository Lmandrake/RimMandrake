#!/usr/bin/env python3
"""Class guard for NIGHTLY_COP_FIX_RED_JQURAF_DQRD: a snapshot selftest over the test queue's records stays green when
the queue moves a done record into quarantined/ (testq/fault_monitor.py rewrites it as it moves it), and stays red when
a record truly vanishes or is changed in place.

The instance: selftest_ns_capture_down_rows.py read done/ only, so on 2026-11-04 a quarantined record made it report
"snapshot differs from the records in done on: files_scanned, jobs, record_sha256, sanity_probe".

Builds a synthetic queue in a temp dir (no real records, no game, no ledger) and drives the target's own derive() and
main() against it. `--instance <git-rev>` loads the target as it was at that revision (the guard shown red on
dcd4b1873f^, the version before the fix); with no argument it checks the working tree's target.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TARGET = "src/RimMandrake/Utils/modcheck/selftest_ns_capture_down_rows.py"


def load(rev, tmp):
    path = os.path.join(REPO, TARGET)
    if rev:
        path = os.path.join(tmp, "target_at_rev.py")
        with open(path, "wb") as fh:
            fh.write(subprocess.check_output(["git", "-C", REPO, "show", "%s:%s" % (rev, TARGET)]))
    spec = importlib.util.spec_from_file_location("nscd_target", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record(mod, job, pit_rows, probe=False):
    rows = [{"chain": mod.CHAIN, "row": r, "verdict": "PASS", "detail": "ok"} for r in pit_rows]
    if probe:
        rows.append({"chain": "other_chain", "row": "arrives", "verdict": "PASS", "detail": "%s: Pirate" % mod.MARK})
    return {"id": job, "result": {"host": "synthetic", "rows": rows}}


def build(mod, q):
    done = os.path.join(q, "done")
    os.makedirs(done)
    os.makedirs(os.path.join(q, "quarantined"))
    filler = ["filler_%02d" % i for i in range(16)]
    recs = {j: record(mod, j, list(mod.NAMED_ROWS) + filler) for j in mod.NAMED_JOBS}
    recs["J20261101T000000Z-probe1"] = record(mod, "J20261101T000000Z-probe1", [], probe=True)
    # the one the queue will quarantine: pit rows AND a probe row, so leaving done/ moves every derived field
    recs["J20261027T000000Z-movee1"] = record(mod, "J20261027T000000Z-movee1", ["capture_down_off", "extra"], probe=True)
    recs["J20261024T000000Z-before"] = record(mod, "J20261024T000000Z-before", ["outside_window"])
    for j, r in recs.items():
        with open(os.path.join(done, j + ".json"), "w") as fh:
            json.dump(r, fh)
    return done


def run_main(mod, q, snapshot):
    mod.QUEUE, mod.SNAPSHOT = q, snapshot
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.main([])
    return rc, buf.getvalue()


def quarantine(q, job):
    """As testq/fault_monitor.py does: move done -> quarantined, rewriting the record with a `quarantined` key."""
    src = os.path.join(q, "done", job + ".json")
    with open(src) as fh:
        rec = json.load(fh)
    rec["quarantined"] = {"window": "synthetic", "at": "2026-11-04T00:00:00Z"}
    with open(os.path.join(q, "quarantined", job + ".json"), "w") as fh:
        json.dump(rec, fh)
    os.remove(src)


def case(mod, tmp, name, act):
    q = os.path.join(tmp, name)
    done = build(mod, q)
    snapshot = os.path.join(q, "snapshot.json")
    with open(snapshot, "w") as fh:
        json.dump(mod.derive(done), fh)
    act(q)
    return run_main(mod, q, snapshot)


def main(argv):
    rev = argv[0] if argv else None
    tmp = tempfile.mkdtemp(prefix="nscd_guard_")
    fails = []
    try:
        mod = load(rev, tmp)
        movee = "J20261027T000000Z-movee1"

        rc, out = case(mod, tmp, "untouched", lambda q: None)
        if rc != 0:
            fails.append("untouched queue is red (the synthetic fixture is wrong): " + out.strip()[-300:])

        rc, out = case(mod, tmp, "quarantined", lambda q: quarantine(q, movee))
        if rc != 0:
            fails.append("a record moved done/ -> quarantined/ turned the snapshot test red (the instance): "
                         + " | ".join(l for l in out.splitlines() if l.startswith("FAIL")))

        rc, out = case(mod, tmp, "vanished", lambda q: os.remove(os.path.join(q, "done", movee + ".json")))
        if rc == 0:
            fails.append("a record that vanished from the queue stayed green: the guard against a stale snapshot is gone")

        def tamper(q):
            p = os.path.join(q, "done", mod.NAMED_JOBS[0] + ".json")
            with open(p) as fh:
                rec = json.load(fh)
            rec["result"]["rows"][0]["verdict"] = "FAIL"
            with open(p, "w") as fh:
                json.dump(rec, fh)
        rc, out = case(mod, tmp, "tampered", tamper)
        if rc == 0:
            fails.append("a record changed in place in done/ stayed green")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("target: %s%s" % (TARGET, " at %s" % rev if rev else " (working tree)"))
    for f in fails:
        print("FAIL " + f)
    print("RESULT: %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
