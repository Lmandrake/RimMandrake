#!/usr/bin/env python3
"""selftest_scratch_reap_sanity.py -- the cleaner speaks at both ends of a run, and the Dispatcher's watch hears it.

No dispatcher runs here: the alarm is collected from signal_watch.step, so nothing can reach the real Conductor log."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import scratch_reap as R  # noqa: E402
import signal_watch as SW  # noqa: E402
R.CTIME_COUNTS = False   # utime ages a fixture's mtime only; the content reading is what the counter now shares with the reaper

FAILS = []
OLD = 3 * 86400


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


POOL = {"pool_clones": 1, "pool_clones_cap": 10, "pool_gb": 1.0, "pool_gb_cap": 40.0}
LOOSE = dict.fromkeys(("rm_scratch_clones", "rm_scratch_gb", "selftest_stale", "session_dirs", "refused", "refused_gb",
                       "oldest_h", "root_disk_pct"), 1e9)


def limits(path: Path, **start):
    path.write_text(json.dumps({"_why": "test", "start": {**LOOSE, **start}, "end": {**LOOSE, **start}}))


def stale_fixture(root: Path, name="selftest_a"):
    d = root / "S" / name
    d.mkdir(parents=True)
    os.utime(d, (time.time() - OLD, time.time() - OLD))


def heard(sd: Path):
    """What the Dispatcher's watch raises from what is on disk now."""
    acts = []
    obs = {"paused": None, "signals": {"units": lambda: ([], []), "alarms": lambda: {},
                                       "flags": lambda: {"flags": [], "at": "9"},
                                       "sanity": lambda: SW.read_sanity({"sanity_file": str(sd / "sanity.json")})}}
    SW.step({"signal_watch": {"enabled": True, "ops_dir": "/nonexistent"}}, {}, obs, 9.0, lambda **a: acts.append(a),
            str, lambda s: float(s))
    return sorted(a["kind"] for a in acts)


def borrower_retry():
    """drvfs answers ENOMEM under load: a retry that reads clears the hold, one that does not keeps it."""
    real_walk, real_sleep, real_roots = R.Borrows._walk, R.time.sleep, R.scan_roots
    bad = "find: \u2018/x/Defs\u2019: Cannot allocate memory"
    try:
        R.time.sleep = lambda s: None
        R.scan_roots = lambda: [Path("/")]
        seen = []
        def once(tops):
            seen.append(tops)
            return (1, b"", [bad]) if len(seen) == 1 else (0, b"", [])
        R.Borrows._walk = staticmethod(once)
        check(R.Borrows().hold == [] and seen[1] == ["/x/Defs"], "a directory that reads on retry holds nothing")
        R.Borrows._walk = staticmethod(lambda tops: (1, b"", [bad]))
        check(R.Borrows().hold == [bad], "a directory that never reads still holds every deletion")
    finally:
        R.Borrows._walk, R.time.sleep, R.scan_roots = staticmethod(real_walk), real_sleep, real_roots


def main():
    borrower_retry()
    td = Path(tempfile.mkdtemp(prefix="selftest_sanity_"))
    root, sd, lim = td / ".seat-tmp", td / "state", td / "limits.json"
    root.mkdir()
    sd.mkdir()
    os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_STATE=str(sd), SCRATCH_REAP_SANITY=str(lim),
                      SCRATCH_REAP_RM_SCRATCH=str(td / "rm_scratch"), SCRATCH_REAP_CORPUS=str(td / "corpus"),
                      SCRATCH_REAP_TRANSCRIPTS=str(td / "transcripts"), LEFTOVERS_ARCHIVE_ROOT=str(td / "archive"),
                      SCRATCH_REAP_PROTECTED=str(td / "held"))
    (td / "archive").mkdir()
    R.pool_measures = lambda: dict(POOL)
    R.free_gb = lambda path="/": 500.0
    real_start, real_end, real_ctx = R.sanity_start, R.sanity_end, R.Ctx

    # dirty start, and the run then dies: the alarm is on disk already
    stale_fixture(root)
    limits(lim, selftest_stale=0)

    def dies(now):
        raise RuntimeError("killed after the reading")
    R.Ctx = dies
    try:
        R.main(["--apply"])
        check(False, "the dying run raises")
    except RuntimeError:
        pass
    R.Ctx = real_ctx
    rec = json.loads((sd / "sanity.json").read_text())
    check("selftest_stale 1 over 0" in rec["start"]["problems"], "dirty start: the problem is recorded before any work")
    check(any("the run died" in p for p in rec["end"]["problems"]), "a run that dies says so at its end")
    check(heard(sd) == ["scratch:sanity:end", "scratch:sanity:start"], "the Dispatcher's watch hears a dead run's start")

    # a full run, dirty at both ends (the line of 0 refusals, with a refused row): the two mutants must go quiet
    real_apply = R.apply_rows
    refused = {"verdict": "REFUSE", "bytes": 5 * 10 ** 9, "age_h": 40.0, "why": ["/x/y: a rebase-merge is in progress"],
               "kind": "clone", "path": "/x/y"}
    real_judge = R.judge_all
    R.judge_all = lambda ctx: [dict(refused)]
    R.apply_rows = lambda rows, ctx, max_s, failures, started: (0, 0)
    limits(lim, refused=0)
    (sd / "last_run.json").write_text(json.dumps({"counts": {"REFUSE": 3}, "refused_bytes": 0}))

    def run_heard():
        (sd / "sanity.json").unlink(missing_ok=True)
        (sd / "last_run.json").write_text(json.dumps({"counts": {"REFUSE": 3}, "refused_bytes": 0}))
        check(R.main(["--apply"]) == 0, "a run with only refusals exits 0")
        return heard(sd)

    check(run_heard() == ["scratch:sanity:end", "scratch:sanity:start"], "dirty at both ends: two alarms")
    end = json.loads((sd / "sanity.json").read_text())["end"]["problems"]
    check("refused 1 over 0" in end and any(p.startswith("1 refused, ") and "rebase-merge" in p for p in end),
          "residual end: the dirt is raised with its reason")
    R.sanity_start = lambda sd, now: {}
    check(run_heard() == ["scratch:sanity:end"], "mutant: no start reading, no start alarm (this check is the red)")
    R.sanity_start, R.sanity_end = real_start, lambda sd, now, rows, rec: None
    check(run_heard() == ["scratch:sanity:start"], "mutant: no end reading, no end alarm (this check is the red)")
    R.sanity_end = real_end

    # clean at both ends: silent
    R.judge_all = lambda ctx: []
    limits(lim)
    check(run_heard() == [], "a clean state is silent at both ends")
    check(json.loads((sd / "last_run.json").read_text()).get("oldest_h") is not None, "the record carries its oldest item")

    # no reading is a problem, never a pass
    R.pool_measures = lambda: dict(POOL, pool_clones=None)
    check("pool_clones: no reading" in R.judge_sanity("start", R.measure(time.time(), [], {})), "no pool reading is a problem")
    R.pool_measures = lambda: dict(POOL, pool_clones=11)
    check(any("over the pool cap" in p for p in R.judge_sanity("start", R.measure(time.time(), [], {}))), "over the pool cap")
    R.pool_measures = lambda: dict(POOL)
    (td / "rm_scratch" / "BENCH" / "c" / ".git" / "objects").mkdir(parents=True)
    limits(lim, rm_scratch_clones=0)
    check("rm_scratch_clones 1 over 0" in R.judge_sanity("start", R.measure(time.time(), [], {})),
          "rm/scratch is counted, which the pool cap cannot see")
    lim.write_text("not json")
    R.sanity_start(sd, time.time())
    check(any("blind" in p for p in json.loads((sd / "sanity.json").read_text())["start"]["problems"]),
          "a bad limits file is said aloud, and the run goes on")
    R.judge_all = real_judge
    R.apply_rows = real_apply

    shipped = json.loads((HERE / "scratch_reap_sanity.json").read_text())
    check(shipped.get("_why") and set(shipped["start"]) <= set(LOOSE) and set(shipped["end"]) <= set(LOOSE),
          "the shipped limits say why and name only real readings")
    # the counter reads what the reaper reads: an epoch-stamped dir holding a fresh file is young, not 498211 h old
    fx = td / "epoch_fx"
    fx.mkdir()
    (fx / "f").write_text("fresh")
    os.utime(fx, (0, 0))
    check((R.fixture_age_h(fx, time.time()) or 1e9) < 1, "a fixture dir with fresh contents is young by content, not by dir mtime")
    import shutil
    shutil.rmtree(td)
    print(f"selftest_scratch_reap_sanity: {'FAIL' if FAILS else 'PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
