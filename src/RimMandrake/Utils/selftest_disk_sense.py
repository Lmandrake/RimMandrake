#!/usr/bin/env python3
"""selftest_disk_sense.py -- the disk sense reads only; the seat tidy lands in its own unit
(design/specs/2026-11-22-disk-sense-reads-only/boundary.md). Hermetic: a temp seat clone with its bare origin, empty
role, pool and scratch roots, and ops_watch's store in a temp dir. `run` and every filer are stubbed: nothing is filed,
fetched from the network or landed on a real remote."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TMP = Path(tempfile.mkdtemp(prefix="selftest_disk_sense_"))
SEAT = TMP / "seat"
ORIGIN = TMP / "origin.git"
ROLES = TMP / "roles"
os.environ.update({
    "RM_SEAT_CLONE": str(SEAT), "RM_ROLE_CLONE_ROOT": str(ROLES),
    "RM_OPS_WATCH_DIR": str(TMP / "ops"), "RM_OPS_DISKS": "root=%s" % TMP,
    "RM_SCRATCH_REAP_RUNS": str(TMP / "reap.jsonl"), "RM_POOL_ROOT": str(TMP / "pool"),
    "RM_OBJSTORE_STATE": str(TMP / "objstate"), "RM_SCRATCH_ROOT": str(TMP / "scr"),
    "RM_SESSION_GLOB": str(TMP / "nosession*"), "SCRATCH_REAP_MIRRORS": str(ORIGIN),
    "RM_DATA_ROOT": str(TMP / "data"), "RM_TESTING_METRICS_DIR": str(TMP / "no_testing_metrics"),
    "METRONOME_DIR": str(TMP / "metronome"),
    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
})
sys.path.insert(0, str(HERE))
import seat_dirt  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sh(*a, cwd=None):
    subprocess.run(list(a), cwd=cwd, check=True, capture_output=True)


def write(rel, text, age_s=0):
    p = SEAT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    if age_s:
        t = time.time() - age_s
        os.utime(p, (t, t))


def seat_with_landable_dirt():
    """The seat clone of 11:02 PST 2026-11-22: a conversation record, settled, that the tidy would land."""
    if not SEAT.exists():
        ROLES.mkdir(parents=True)
        sh("git", "init", "-q", "--bare", "-b", "main", str(ORIGIN))
        sh("git", "init", "-q", "-b", "main", str(SEAT))
        sh("git", "-C", str(SEAT), "remote", "add", "origin", str(ORIGIN))
        write("tracked.txt", "one\n")
        sh("git", "-C", str(SEAT), "add", "-A")
        sh("git", "-C", str(SEAT), "commit", "-q", "-m", "base")
        sh("git", "-C", str(SEAT), "push", "-q", "origin", "main")
    write("conversations/2026-11-22-1102-x.md", "record\n", age_s=(seat_dirt.SETTLE_MIN + 5) * 60)


class Spy:
    """Records every git fetch, land.sh and tidy the code under test starts, and lets none of them run."""

    def __init__(self):
        self.acts = []

    def __enter__(self):
        self.git, self.tidy, self.srun = seat_dirt.git, seat_dirt.tidy, seat_dirt.subprocess.run

        def git(clone, *a, **kw):
            if a and a[0] in ("fetch", "push", "pull"):
                self.acts.append("git " + a[0])
                return ""
            return self.git(clone, *a, **kw)

        def tidy(clone=None, *a, **kw):
            self.acts.append("tidy %s" % clone)
            return "nothing to land"

        def run(argv, *a, **kw):
            if any(str(x).endswith("land.sh") for x in argv) or argv[:3] == ["git", "-C", str(SEAT)] and "fetch" in argv:
                self.acts.append("run " + " ".join(map(str, argv[:3])))
                return subprocess.CompletedProcess(argv, 0, "", "")
            return self.srun(argv, *a, **kw)
        seat_dirt.git, seat_dirt.tidy, seat_dirt.subprocess.run = git, tidy, run
        return self

    def __exit__(self, *e):
        seat_dirt.git, seat_dirt.tidy, seat_dirt.subprocess.run = self.git, self.tidy, self.srun


def t_the_disk_sense_starts_no_fetch_and_no_landing():
    """The beat's own argv (metronome_phases.json sense: run --compose --file-alarms --metronome-gen N --family disk)
    with landable dirt in the seat clone: the disk collector reads the dirt and starts no fetch, land.sh or tidy."""
    seat_with_landable_dirt()
    import metronome
    real_run, real_may = OW.run, metronome.may_act
    got = {}

    def run(filer=None, families=None, compose=False, still_owner=None):
        got.update(OW.c_disk(time.time(), OW.load_rules(), {}))
        return {"headline": "stub"}
    OW.run, metronome.may_act = run, (lambda *a, **kw: (True, ""))
    try:
        with Spy() as spy:
            rc = OW.main(["run", "--compose", "--file-alarms", "--metronome-gen", "7", "--family", "disk"])
    finally:
        OW.run, metronome.may_act = real_run, real_may
    sd = got.get("disk.seat_dirt") or {}
    check(rc == 0 and sd.get("m") == "MEASURED" and sd.get("v") == 0,
          "the-disk-sense-starts-no-fetch-and-no-landing: the reading is measured (rc %s, %s)" % (rc, sd))
    check(spy.acts == [], "the-disk-sense-starts-no-fetch-and-no-landing: no fetch, land or tidy (%s)" % spy.acts)


def t_the_seat_tidy_runs_in_its_own_unit():
    """`seat_dirt.py tidy --all --apply` tidies every clone; rm-seat-tidy.service runs it from the deploy, its timer
    exists, and ops_clocks.json names the timer as a clock."""
    seat_with_landable_dirt()
    (ROLES / "Designer" / ".git").mkdir(parents=True, exist_ok=True)
    seen, real = [], seat_dirt.tidy

    def tidy(clone=None, *a, **kw):
        seen.append(clone)
        if clone == str(SEAT):
            raise RuntimeError("land.sh exited 1: planted refusal")
        return "nothing to land"
    seat_dirt.tidy = tidy
    try:
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = seat_dirt.main(["tidy", "--all", "--apply"])
    finally:
        seat_dirt.tidy = real
    check(seen == [str(SEAT), str(ROLES / "Designer")],
          "the-seat-tidy-runs-in-its-own-unit: --all tidies every clone, past one that fails (%s)" % seen)
    check(rc != 0 and "planted refusal" in out.getvalue(),
          "the-seat-tidy-runs-in-its-own-unit: a failed clone exits non-zero and is named (rc %s)" % rc)
    sysd = HERE / "systemd"
    svc = (sysd / "rm-seat-tidy.service").read_text() if (sysd / "rm-seat-tidy.service").exists() else ""
    conf = json.loads((sysd / "ops_clocks.json").read_text())
    check("ExecStart=/usr/bin/python3 %s/src/RimMandrake/Utils/seat_dirt.py tidy --all --apply" % conf["deploy"] in svc
          and (sysd / "rm-seat-tidy.timer").exists() and conf["clocks"].get("rm-seat-tidy") == "rm-seat-tidy.timer",
          "the-seat-tidy-runs-in-its-own-unit: the unit runs it from the deploy and is a clock")


def t_a_safe_path_the_tidy_left_counts_as_dirt():
    """A landable path older than TIDY_LATE_MIN counts in the reading's stale (a dead tidy unit alarms through
    disk.seat_dirt); a landable path younger than it does not."""
    seat_with_landable_dirt()
    late = getattr(seat_dirt, "TIDY_LATE_MIN", None)
    if late is None:
        check(False, "a-safe-path-the-tidy-left-counts-as-dirt: seat_dirt has no TIDY_LATE_MIN")
        return
    write("conversations/2026-11-22-1102-x.md", "record\n", age_s=(late + 5) * 60)
    r = seat_dirt.reading(str(SEAT))
    check(r["stale"] == 1 and r["landable"] == 1, "a-safe-path-the-tidy-left-counts-as-dirt: late -> stale (%s)" % r)
    write("conversations/2026-11-22-1102-x.md", "record\n", age_s=(seat_dirt.SETTLE_MIN + 5) * 60)
    r = seat_dirt.reading(str(SEAT))
    check(r["stale"] == 0 and r["landable"] == 1, "a-safe-path-the-tidy-left-counts-as-dirt: settled, not late (%s)" % r)


def main():
    for t in (t_the_disk_sense_starts_no_fetch_and_no_landing, t_the_seat_tidy_runs_in_its_own_unit,
              t_a_safe_path_the_tidy_left_counts_as_dirt):
        try:
            t()
        except (Exception, SystemExit) as e:  # noqa: BLE001  a test that raises (argparse exits) is a red, named
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_disk_sense: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
