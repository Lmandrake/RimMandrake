#!/usr/bin/env python3
"""selftest for timers_guard.py (TIMERS_DIAGNOSE_SILENT_MASS_STOP). Fixtures plus ONE throwaway user timer; no live rm-* timer touched.

    python3 src/RimMandrake/Utils/selftest_timers_guard.py
"""
import os
import subprocess as SP
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_timers_guard_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
import timers_guard as TG  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


NOW = 1_800_000_000.0


def main():
    # judge: pure
    units = {"rm-a.timer": "active", "rm-b.timer": "inactive", "testq-c.timer": "inactive", "rm-d.timer": "failed"}
    bad = TG.judge(units, covered=False)
    check(sorted(bad) == ["rm-b.timer", "testq-c.timer"], "inactive enabled timers are the fault (failed is ops_watch's)")
    check(TG.judge({"rm-a.timer": "active"}, False) == {}, "all active: nothing")
    check(TG.judge(units, {"rm-b.timer", "testq-c.timer"}) == {}, "timers covered by a pending restart are tolerated")
    check(sorted(TG.judge(units, {"rm-b.timer"})) == ["testq-c.timer"],
          "a pause of A does NOT hide an unrelated stopped B (the mass-stop hole)")
    mass = TG.judge({"rm-%d.timer" % i: "inactive" for i in range(5)}, False)
    check(len(mass) == 5, "a mass stop (every rm timer inactive, deadman included) is seen")

    # listing parse
    out = "rm-a.timer enabled enabled\nrm-b.timer disabled enabled\ntestq-c.timer enabled enabled\nfoo.timer enabled enabled\n"
    check(TG.enabled_from_listing(out) == ["rm-a.timer", "testq-c.timer"], "only enabled rm-/testq- timers are watched")

    check(TG.enabled_from_listing("rm-r.timer enabled-runtime enabled\n") == ["rm-r.timer"], "enabled-runtime timers are watched too")

    # read_states with a fake systemctl
    def fake(listing, active, pending):
        def run(argv, **kw):
            sub = argv[2]
            if sub == "list-unit-files":
                return SP.CompletedProcess(argv, 0, listing, "")
            if sub == "is-active":
                return SP.CompletedProcess(argv, 3, active.get(argv[3], ""), "")
            return SP.CompletedProcess(argv, 0, pending, "")
        return run
    lst = "rm-a.timer enabled enabled\nrm-b.timer enabled enabled\n"
    TG.pauses_file().parent.mkdir(parents=True, exist_ok=True)
    TG.pauses_file().write_text('{"timer-resume-1.timer": ["rm-a.timer"]}')
    sts, cov = TG.read_states(fake(lst, {"rm-a.timer": "inactive\n", "rm-b.timer": "inactive\n"},
                                   "Wed 2026 1h timer-resume-1.timer timer-resume-1.service\n"))
    check(cov == {"rm-a.timer"} and sorted(TG.judge(sts, cov)) == ["rm-b.timer"], "pending resume covers only its recorded timers")
    sts, cov = TG.read_states(fake(lst, {"rm-a.timer": "inactive", "rm-b.timer": "active"}, ""))
    check(cov == set(), "no pending resume: nothing covered")
    try:
        TG.read_states(fake(lst, {"rm-a.timer": "active"}, ""))
        check(False, "an unanswered is-active must not read as healthy")
    except RuntimeError:
        check(True, "an unanswered is-active raises instead of reading as healthy")

    # guard unit is outside the glob it watches
    check(not TG.WATCH_RE.match(TG.GUARD_NAME + ".timer"), "the guard's own name is outside rm-*/testq-*")
    check(not TG.WATCH_RE.match(TG.RESUME_PREFIX + "x.timer"), "resume timers are outside the watched glob")

    # edge-triggered alarm
    filed = []

    def filer(todo, conf):
        filed.extend(a["name"] for a in todo)
        return {a["name"]: None for a in todo}
    ids = set()
    st = TG.check(NOW, filer, ids, {"rm-b.timer": "inactive", "rm-a.timer": "active"}, False)
    check(len(filed) == 1 and st.get("state") == "OPEN", "stopped timer files exactly one alarm")
    TG.check(NOW + 600, filer, ids, {"rm-b.timer": "inactive"}, False)
    check(len(filed) == 1, "edge-triggered: no second alarm while open")
    TG.check(NOW + 1200, filer, ids, {"rm-b.timer": "active"}, False)
    check(not TG.check(NOW + 1300, None, ids, {"rm-b.timer": "active"}, False), "cleared when timers are active again")

    # a tolerated pause is neither recovery nor a new alarm: the open episode survives it
    f2 = []
    ids2 = set()
    TG.check(NOW + 2000, lambda t, c: (f2.extend(x["name"] for x in t), {x["name"]: None for x in t})[1], ids2, {"rm-b.timer": "inactive"}, set())
    st = TG.check(NOW + 2100, lambda t, c: (f2.append("N"), {})[1], ids2, {"rm-b.timer": "inactive"}, {"rm-b.timer"})
    check(st.get("state") == "OPEN" and f2.count("N") == 0, "pause covering the fault keeps the episode (no 'active again' note)")
    TG.check(NOW + 2200, None, ids2, {"rm-b.timer": "active"}, set())

    # pause helper: arms restart BEFORE stopping, against a throwaway timer
    cmds = []
    TG.pause(["rm-x.timer", "testq-y.timer"], 2, runner=lambda argv, **kw: (cmds.append(argv), SP.CompletedProcess(argv, 0, "", ""))[1])
    kinds = ["run" if a[0] == "systemd-run" else a[2] for a in cmds]
    check(kinds[0] == "run" and "stop" in kinds and kinds.index("stop") > 0, "restart armed before the stop")
    run = cmds[0]
    check(any(x.startswith("--on-active=") for x in run) and "start" in run and "rm-x.timer" in run, "restart covers the list")
    for bad_h in (0, -1, float("nan"), float("inf")):
        try:
            TG.pause(["rm-x.timer"], bad_h, runner=lambda *a, **k: SP.CompletedProcess(a, 0, "", ""))
            check(False, "hours %r refused" % bad_h)
        except ValueError:
            check(True, "hours %r refused" % bad_h)
    check(any("rm-x.timer" in v for v in TG.load_pauses().values()), "pause records which timers its restart covers")
    try:
        TG.pause(["foo.service"], 1, runner=lambda *a, **k: SP.CompletedProcess(a, 0, "", ""))
        check(False, "non-timer name refused")
    except ValueError:
        check(True, "non-timer name refused")

    name = "testq-selftestthrow-%d" % os.getpid()
    d = Path.home() / ".config/systemd/user"
    (d / (name + ".service")).write_text("[Service]\nType=oneshot\nExecStart=/bin/true\n")
    (d / (name + ".timer")).write_text("[Timer]\nOnActiveSec=1d\n")
    try:
        SP.run(["systemctl", "--user", "daemon-reload"], timeout=60)
        SP.run(["systemctl", "--user", "start", name + ".timer"], timeout=60)
        r = TG.pause([name + ".timer"], 0.02)   # 72 s
        st1 = SP.run(["systemctl", "--user", "is-active", name + ".timer"], capture_output=True, text=True).stdout.strip()
        armed = SP.run(["systemctl", "--user", "list-timers", "--all", "--no-legend", TG.RESUME_PREFIX + "*"],
                       capture_output=True, text=True).stdout
        check(st1 == "inactive", "throwaway timer stopped (is %s)" % st1)
        check(r["unit"] in armed, "restart timer %s is pending" % r["unit"])
        t0 = time.time()
        st2 = "inactive"
        while time.time() - t0 < 110 and st2 != "active":
            time.sleep(3)
            st2 = SP.run(["systemctl", "--user", "is-active", name + ".timer"], capture_output=True, text=True).stdout.strip()
        check(st2 == "active", "throwaway timer restarted by its own armed resume")
    finally:
        SP.run(["systemctl", "--user", "stop", name + ".timer"], timeout=60)
        for s in (".timer", ".service"):
            (d / (name + s)).unlink(missing_ok=True)
        SP.run(["systemctl", "--user", "daemon-reload"], timeout=60)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
