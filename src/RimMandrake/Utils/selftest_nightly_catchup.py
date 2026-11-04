#!/usr/bin/env python3
"""selftest_nightly_catchup: NIGHTLY_SWEEP_HARDEN_DIED_AT_SIXTY. A sweep killed mid-run runs again on its own.

testdata below is the real log's section shape from 2026-11-02: the 03:21 PST sweep killed with nothing under its line, then
the hand restart at 09:07 that finished. Runs the real pass with a fake systemctl, the script as the shipped ExecStart runs it,
and a real kill of a throwaway stand-in unit under the user's systemd (no bus is a FAIL, not a skip); the unit files are read
as shipped.
"""
import configparser
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

os.environ["TZ"] = "America/Los_Angeles"
import time  # noqa: E402
time.tzset()

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_nightly_catchup_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
import known_reds as KR  # noqa: E402
import nightly_catchup as NC  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


FINISHED_NOV1 = "=== 2026-11-01T11:00:00Z nightly\nPASS 900/925\nRESULT: RED (green = FAIL 0 and CRASH 0)\nexit 1\n"
KILLED_NOV2 = "\n=== 2026-11-02T11:21:47Z nightly\n"
RERUN_NOV2 = "\n=== 2026-11-02T17:07:20Z nightly\nPASS 900/925\nRESULT: RED (green = FAIL 0 and CRASH 0)\nexit 1\n"
AT = KR.epoch
HOUR, CAP = 3, 3


def decide(now, text, state="inactive", enabled=True, started=0, **k):
    return NC.decide(AT(now), text, state, enabled, started, HOUR, CAP, **k)


# ---- the night itself, replayed: boot at about 09:05 PST, sweep killed at 03:22, Nov 1 finished the night before
night = decide("2026-11-02T17:05:00Z", FINISHED_NOV1 + KILLED_NOV2)
check("the killed 2026-11-02 sweep re-runs at the first pass after boot", night[:2] == (True, "start"), night)
check("the sweep that did finish clears the night", decide("2026-11-02T18:00:00Z", FINISHED_NOV1 + KILLED_NOV2 + RERUN_NOV2)[1] == "done")
check("yesterday's RESULT does not count for tonight", decide("2026-11-02T11:30:00Z", FINISHED_NOV1)[0] is True)
check("a timer that never fired at all is caught too", decide("2026-11-02T17:05:00Z", FINISHED_NOV1)[0] is True)
check("before 03:00 the night is still yesterday's", decide("2026-11-02T10:30:00Z", FINISHED_NOV1)[1] == "done")
check("a machine with no log yet starts", decide("2026-11-02T17:05:00Z", "")[0] is True)

# ---- what must stop it
for st in sorted(NC.UP):
    check("a sweep that is %s is left alone" % st, decide("2026-11-02T17:05:00Z", KILLED_NOV2, state=st)[:2] == (False, "running"))
check("'failed', what a kill leaves, does not read as running", decide("2026-11-02T17:05:00Z", KILLED_NOV2, state="failed")[0] is True)
check("a disabled nightly timer is not brought back", decide("2026-11-02T17:05:00Z", KILLED_NOV2, enabled=False)[:2] == (False, "disabled"))
check("the next fire close by does the work", decide("2026-11-03T10:30:00Z", KILLED_NOV2)[:2] == (False, "quiet"))
check("two hours off the next fire still starts", decide("2026-11-03T09:00:00Z", KILLED_NOV2)[0] is True)

many = "".join("\n=== 2026-11-02T%02d:00:00Z nightly\n" % h for h in (12, 13, 14))
check("three killed sections and it gives up", decide("2026-11-02T17:05:00Z", many)[:2] == (False, "gave_up"))
check("two killed sections still try", decide("2026-11-02T17:05:00Z", "\n=== 2026-11-02T12:00:00Z nightly\n\n=== 2026-11-02T13:00:00Z nightly\n")[0] is True)
check("starts that left no section count to the cap", decide("2026-11-02T17:05:00Z", "", started=3)[:2] == (False, "gave_up"))
check("the next night starts over", decide("2026-11-03T12:00:00Z", many)[0] is True)
check("a finish after two kills is done, not gave_up", decide("2026-11-02T18:00:00Z", many + RERUN_NOV2)[1] == "done")

# ---- the DST night: 2026-11-01 02:00 PDT falls back, so that day is 25 hours long
s, n = NC.night_start(AT("2026-11-01T11:00:00Z"), HOUR)
check("03:00 PST on the fall-back day is 11:00Z", KR.stamp(s) == "2026-11-01T11:00:00Z", KR.stamp(s))
s, n = NC.night_start(AT("2026-10-31T11:00:00Z"), HOUR)
check("the night's length follows the calendar over DST", n - s == 25 * 3600, (n - s) / 3600)


# ---- the real pass, on real files, with systemd faked: the only thing faked
class Ctl:
    def __init__(self, state="inactive", on="enabled", starts=True):
        self.state, self.on, self.starts, self.calls = state, on, starts, []

    def __call__(self, *a):
        self.calls.append(a)
        if a[0] == "is-active":
            return self.state
        if a[0] == "is-enabled":
            return self.on
        if a[0] == "start" and self.starts:
            self.state = "activating"
        return None


LOG = TMP / "bench" / "Transient" / "selftests_nightly.log"
LOG.parent.mkdir(parents=True)
LOG.write_text(FINISHED_NOV1 + KILLED_NOV2)
OUT = TMP / "ops" / "nightly_catchup.json"
BOOT = AT("2026-11-02T17:05:00Z")

c = Ctl()
r = NC.one_pass(BOOT, True, ctl=c, log=LOG, out=OUT)
check("the pass starts the sweep's own unit, without waiting on it",
      ("start", "--no-block", "rm-selftests-nightly.service") in c.calls and r["state"] == "start", (c.calls, r))
check("the reading records the start", json.loads(OUT.read_text())["started"] == 1, OUT.read_text())
c2 = Ctl(state="activating")
r = NC.one_pass(BOOT + 3600, True, ctl=c2, log=LOG, out=OUT)
check("the next pass sees it running and does not start again", r["state"] == "running" and not any(x[0] == "start" for x in c2.calls), r)
check("the count survives a pass that started nothing", json.loads(OUT.read_text())["started"] == 1)

c3 = Ctl()
before = OUT.read_text()
r = NC.one_pass(BOOT, False, ctl=c3, log=LOG, out=OUT)
check("status starts nothing and writes nothing", r["state"] == "start" and not any(x[0] == "start" for x in c3.calls) and OUT.read_text() == before)



class EndsNowCtl(Ctl):
    """The sweep writes its RESULT and exits just as the pass asks whether it is up."""
    def __call__(self, *a):
        if a[0] == "is-active" and self.log is not None:
            self.log.write_text(FINISHED_NOV1 + KILLED_NOV2 + RERUN_NOV2)
            self.log = None
        return super().__call__(*a)


LOG5 = TMP / "bench5" / "Transient" / "selftests_nightly.log"
LOG5.parent.mkdir(parents=True)
LOG5.write_text(FINISHED_NOV1 + KILLED_NOV2)
c5 = EndsNowCtl()
c5.log = LOG5
r = NC.one_pass(AT("2026-11-02T18:00:00Z"), True, ctl=c5, log=LOG5, out=TMP / "ops5" / "nightly_catchup.json")
check("a sweep ending during the pass is not run twice", r["state"] == "done" and not any(x[0] == "start" for x in c5.calls), r)
NC.SETTLE_S = 0


class LateCtl(Ctl):
    """The queued start job shows only on the third read after --no-block returned."""
    def __init__(self):
        super().__init__(starts=False)
        self.reads = 0

    def __call__(self, *a):
        if a[0] == "start":
            self.go = True
        if a[0] == "is-active" and getattr(self, "go", False):
            self.reads += 1
            if self.reads >= 3:
                self.state = "activating"
        return super().__call__(*a)


r = NC.one_pass(BOOT, True, ctl=LateCtl(), log=LOG, out=TMP / "ops4" / "nightly_catchup.json")
check("a start slow to show is not a failed start", r["state"] == "start", r)
OUT2 = TMP / "ops2" / "nightly_catchup.json"
c4 = Ctl(starts=False)
r = NC.one_pass(BOOT, True, ctl=c4, log=LOG, out=OUT2)
check("a start that did not take reads start_failed and still counts", r["state"] == "start_failed" and r["started"] == 1, r)

for label, ctl, log in (("systemd silent", Ctl(state=None), LOG), ("is-enabled silent", Ctl(on=None), LOG),
                        ("the clone missing", Ctl(), TMP / "gone" / "Transient" / "selftests_nightly.log")):
    r = NC.one_pass(BOOT, True, ctl=ctl, log=log, out=TMP / "ops3" / "nightly_catchup.json")
    check("%s is blind: no start" % label, r["state"] == "blind" and not any(x[0] == "start" for x in ctl.calls), r)
LOG2 = TMP / "bench2" / "Transient" / "selftests_nightly.log"
LOG2.parent.mkdir(parents=True)
check("a clone with no log file yet is a night with no sweep, not blindness",
      NC.one_pass(BOOT, False, ctl=Ctl(), log=LOG2, out=OUT2)["state"] == "start")
OUT2.write_text("not json")
check("a torn reading costs the count, not the pass", NC.read_started(OUT2, "x") == 0)
check("a reading of another night counts nothing", NC.read_started(OUT, "2026-01-01T11:00:00Z") == 0)

# ---- the real systemctl wrapper against a stub on PATH: `is-active` exits 3 on the healthy answer `inactive`
BIN = TMP / "bin"
BIN.mkdir()
STUB = BIN / "systemctl"
STUB.write_text("#!/bin/sh\necho inactive\nexit 3\n")
STUB.chmod(0o755)
PATH0 = os.environ["PATH"]
os.environ["PATH"] = str(BIN) + os.pathsep + PATH0
check("the answer is stdout's, whatever the exit code", NC.systemctl("is-active", NC.SERVICE) == "inactive")
STUB.write_text("#!/bin/sh\necho 'Failed to connect to bus' >&2\nexit 1\n")
check("no bus reads as no answer", NC.systemctl("is-active", NC.SERVICE) is None)
os.environ["PATH"] = PATH0

# ---- the alarm: a real rule through the real reader, set off by the real reading
rules = json.loads((HERE / "ops_watch_rules.json").read_text())
flat = json.dumps(rules)
check("the give-up alarm is a rule", '"testing.nightly_gave_up"' in flat and '"OPS_NIGHTLY_SWEEP_DIAGNOSE"' in flat)
for st, want in (("gave_up", 1), ("start_failed", 1), ("done", 0), ("running", 0), ("start", 0), ("blind", 0)):
    OUT.write_text(json.dumps({"state": st, "why": "w"}))
    got = OW.nightly_catchup_reading()["testing.nightly_gave_up"]
    check("state %s reads %d" % (st, want), got["v"] == want and got["m"] == "MEASURED", got)
OUT.write_text("not json")
check("a torn reading holds the alarm", OW.nightly_catchup_reading()["testing.nightly_gave_up"]["m"] == "UNMEASURED")
OUT.unlink()
check("no reading holds the alarm", OW.nightly_catchup_reading()["testing.nightly_gave_up"]["m"] == "UNMEASURED")

# ---- the units as shipped
cp = configparser.ConfigParser(strict=False, interpolation=None)
cp.optionxform = str
cp.read(HERE / "systemd" / "rm-selftests-nightly-catchup.timer")
check("it fires after a boot and keeps firing", cp["Timer"].get("OnBootSec") and cp["Timer"].get("OnUnitInactiveSec"))
cp = configparser.ConfigParser(strict=False, interpolation=None)
cp.optionxform = str
cp.read(HERE / "systemd" / "rm-selftests-nightly-catchup.service")
check("the service runs this tool", "nightly_catchup.py run" in cp["Service"]["ExecStart"])
check("the promise is on the baseline", any(ln.startswith("unit=rm-selftests-nightly-catchup.timer reading=") for ln in
                                            (HERE.parent / "rimflow" / "live_baseline.txt").read_text().splitlines()))
check("the sweep's section line is the one this reads", '=== %%s nightly' in (HERE / "systemd" / "rm-selftests-nightly.service").read_text())


def unit(name):
    p = configparser.ConfigParser(strict=False, interpolation=None)
    p.optionxform = str
    p.read(HERE / "systemd" / name)
    return p


# ---- the install: a timer with no [Install] target cannot be enabled, so a fresh install would run no pass at any boot
ct, cs = unit("rm-selftests-nightly-catchup.timer"), unit("rm-selftests-nightly-catchup.service")
check("the catch-up timer installs into timers.target", ct.has_section("Install") and ct["Install"].get("WantedBy") == "timers.target")
check("the catch-up timer fires its own service", ct["Timer"].get("Unit", "rm-selftests-nightly-catchup.service") == "rm-selftests-nightly-catchup.service")
check("the service is a one-shot pass", cs["Service"].get("Type") == "oneshot")
check("the pass's own names are shipped units", (HERE / "systemd" / NC.SERVICE).is_file() and (HERE / "systemd" / NC.TIMER).is_file(), (NC.SERVICE, NC.TIMER))
import testing_policy as TP  # noqa: E402
cal = unit(NC.TIMER)["Timer"].get("OnCalendar", "")
check("the night this reads starts when the nightly timer fires", cal.endswith(" %02d:00:00" % int(TP.param("selftest.nightly_full_hour_local"))), cal)
check("the sweep prints the line 'finished' is read from, last of all",
      'print("RESULT: "' in (HERE / "run_selftests.py").read_text(encoding="utf-8") and "tail -40" in unit(NC.SERVICE)["Service"]["ExecStart"])

# ---- the production defaults, with nothing in the environment: where the sweep writes and where the promise reads
saved = {k: os.environ.pop(k, None) for k in ("RM_STREAMS_BENCH", "RM_OPS_WATCH_DIR")}
sweep = unit(NC.SERVICE)["Service"]
check("the pass reads the log the sweep writes", KR.log_path() == Path(sweep["WorkingDirectory"]) / "Transient" / "selftests_nightly.log"
      and "LOG=Transient/selftests_nightly.log" in sweep["ExecStart"], KR.log_path())
promise = [ln for ln in (HERE.parent / "rimflow" / "live_baseline.txt").read_text().splitlines() if ln.startswith("unit=rm-selftests-nightly-catchup.timer ")]
check("the pass writes the reading the promise holds", promise and "reading=%s " % NC.reading_path() in promise[0], (NC.reading_path(), promise))
for k, v in saved.items():
    if v is not None:
        os.environ[k] = v

# ---- the entry point the timer uses: the shipped ExecStart line, through __main__, default log and reading, a stub systemctl.
# Only the clock is pinned, so 02:00 to 03:00 (`quiet`) cannot change the answer; every test above hands one_pass its paths.
argv = cs["Service"]["ExecStart"].split()
ROOT = HERE.parents[2]
check("ExecStart names this tool by its path in the clone it runs in", argv[1].startswith(cs["Service"]["WorkingDirectory"] + "/")
      and (ROOT / os.path.relpath(argv[1], cs["Service"]["WorkingDirectory"])).resolve() == Path(NC.__file__).resolve(), argv)
CLOCK = "import runpy,sys,time;t=float(sys.argv[1]);time.time=lambda:t;sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')"
STUB2 = """#!/bin/sh
echo "$*" >>"$STUB_DIR/calls"
case "$2" in
is-active) if [ -f "$STUB_DIR/up" ]; then echo activating; else echo inactive; exit 3; fi;;
is-enabled) echo enabled;;
start) : >"$STUB_DIR/up";;
esac
"""


def cli(tag, verb, log_text, now=BOOT, up=False, clone=True):
    """The script as the service runs it -> (exit, stdout, stub's calls, reading or None, the log's path)."""
    d = TMP / "cli" / tag
    (d / "bin").mkdir(parents=True)
    (d / "bin" / "systemctl").write_text(STUB2)
    (d / "bin" / "systemctl").chmod(0o755)
    if up:
        (d / "up").write_text("")
    log = d / "bench" / "Transient" / "selftests_nightly.log"
    if clone:
        log.parent.mkdir(parents=True)
        log.write_text(log_text)
    env = dict(os.environ, PATH=str(d / "bin") + os.pathsep + os.environ["PATH"], STUB_DIR=str(d),
               RM_STREAMS_BENCH=str(d / "bench"), RM_OPS_WATCH_DIR=str(d / "ops"), PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-c", CLOCK, str(now), str(NC.__file__), verb], env=env, capture_output=True, text=True, timeout=120)
    calls = (d / "calls").read_text().splitlines() if (d / "calls").exists() else []
    rd = d / "ops" / "nightly_catchup.json"
    return p.returncode, p.stdout + p.stderr, calls, (json.loads(rd.read_text()) if rd.exists() else None), log


START = "--user start --no-block rm-selftests-nightly.service"
VERB = argv[2]
check("the service's verb is run", argv[2:] == ["run"], argv)
rc, so, calls, rd, lg = cli("killed", VERB, FINISHED_NOV1 + KILLED_NOV2)
check("the service's own line re-runs the killed sweep", rc == 0 and START in calls, (rc, so, calls))
check("that pass read the sweep's log from the default path", rd and rd["log"] == str(lg) and rd["state"] == "start" and rd["started"] == 1, rd)
check("and says so on stdout, which is the journal", so.startswith("start: "), so)
rc, so, calls, rd, _ = cli("done", VERB, FINISHED_NOV1 + KILLED_NOV2 + RERUN_NOV2, now=AT("2026-11-02T18:00:00Z"))
check("the default path's content decides: a finished night starts nothing", rc == 0 and START not in calls and rd["state"] == "done", (rc, so, calls, rd))
rc, so, calls, rd, _ = cli("up", VERB, FINISHED_NOV1 + KILLED_NOV2, up=True)
check("the service's line leaves a running sweep alone", rc == 0 and START not in calls and rd["state"] == "running", (rc, so, calls, rd))
rc, so, calls, rd, _ = cli("blind", VERB, "", clone=False)
check("the service's line, no clone: blind, exit 1, no start", rc == 1 and START not in calls and rd["state"] == "blind", (rc, so, calls, rd))
rc, so, calls, rd, _ = cli("status", "status", FINISHED_NOV1 + KILLED_NOV2)
check("the status verb decides but starts and writes nothing", rc == 0 and so.startswith("start: ") and START not in calls and rd is None, (rc, so, calls, rd))

# ---- the promise itself, read by the check the supervisor and rm-deadman run: a pass in ANY state renews the reading (a healthy
# `done` night is most of them), the shipped cadence renews it inside max_age, and an old or predating reading goes red.
import live_line  # noqa: E402
PROMISE = live_line.parse(promise[0])
UNITS = {"s": 1, "sec": 1, "min": 60, "h": 3600}


def span(text):
    """A systemd time span as the shipped units spell it -> seconds; None for anything else, which fails the bound below."""
    m = re.fullmatch(r"(\d+)(s|sec|min|h)", (text or "").strip())
    return int(m.group(1)) * UNITS[m.group(2)] if m else None


def bound(key, value):
    n = span(value)
    check("%s=%s leaves a reading inside max_age" % (key, value), n is not None and n + 3600 <= PROMISE["max_age_s"], (n, PROMISE))


bound("OnBootSec", ct["Timer"].get("OnBootSec"))
bound("OnUnitInactiveSec", ct["Timer"].get("OnUnitInactiveSec"))
bound("TimeoutStartSec", cs["Service"].get("TimeoutStartSec"))
check("the promise names this timer and holds the reading's age", PROMISE["unit"] == "rm-selftests-nightly-catchup.timer" and PROMISE["max_age_s"])


def pass_ctl(state, on="enabled", rises=True):
    """A systemctl for one pass: `start` raises the state only when `rises`."""
    now = {"s": state}

    def ctl(*a):
        if a[0] == "start" and rises:
            now["s"] = "activating"
        return on if a[0] == "is-enabled" else now["s"] if a[0] == "is-active" else None
    return ctl


def sysd(cmd, **k):
    return SimpleNamespace(stdout="enabled\n" if "is-enabled" in cmd else "active\n", returncode=0)


NOV2_13Z, NOV3_0230 = AT("2026-11-02T13:00:00Z"), AT("2026-11-03T10:30:00Z")
LOGS = TMP / "promise"
LOGS.mkdir()
(LOGS / "done.log").write_text(FINISHED_NOV1 + KILLED_NOV2 + RERUN_NOV2)
(LOGS / "killed.log").write_text(FINISHED_NOV1 + KILLED_NOV2)
(LOGS / "thrice.log").write_text(KILLED_NOV2.replace("11:21", "11:22") * 3)
BLIND_LOG = TMP / "no" / "such" / "clone" / "Transient" / "selftests_nightly.log"
CASES = (("done", "done.log", NOV2_13Z, {"state": "inactive"}), ("running", "killed.log", NOV2_13Z, {"state": "active"}),
         ("disabled", "killed.log", NOV2_13Z, {"state": "inactive", "on": "disabled"}), ("gave_up", "thrice.log", NOV2_13Z, {"state": "failed"}),
         ("quiet", "killed.log", NOV3_0230, {"state": "inactive"}), ("blind", None, NOV2_13Z, {"state": "inactive"}),
         ("start", "killed.log", NOV2_13Z, {"state": "inactive"}), ("start_failed", "killed.log", NOV2_13Z, {"state": "inactive", "rises": False}))
settle1 = NC.SETTLE_S
NC.SETTLE_S = 0
for want, name, when, how in CASES:
    out = LOGS / want / "nightly_catchup.json"
    log = LOGS / name if name else BLIND_LOG
    line = "unit=%s reading=%s max_age=%ds" % (PROMISE["unit"], out, PROMISE["max_age_s"])
    check("%s: a reading that was never written reads red" % want, "absent" in (live_line.check(line, runner=sysd) or ""))
    first = NC.one_pass(when, True, ctl=pass_ctl(**how), log=log, out=out)
    stale = time.time() - PROMISE["max_age_s"] - 600
    os.utime(out, (stale, stale))
    check("%s: an aged reading reads red" % want, "old" in (live_line.check(line, runner=sysd) or ""), live_line.check(line, runner=sysd))
    NC.one_pass(when, False, ctl=pass_ctl(**how), log=log, out=out)
    check("%s: a status look does not freshen it" % want, abs(out.stat().st_mtime - stale) < 2, out.stat().st_mtime)
    before = time.time() - 1
    second = NC.one_pass(when, True, ctl=pass_ctl(**how), log=log, out=out)
    check("%s: both passes reach the state under test" % want, first["state"] == want == second["state"], (first, second))
    check("%s: the same state again still renews the reading" % want, out.stat().st_mtime >= before, out.stat().st_mtime)
    check("%s: the promise holds on a commit older than the pass" % want, live_line.check(line, not_before=before, runner=sysd) is None,
          live_line.check(line, not_before=before, runner=sysd))
    check("%s: and not on a commit newer than it" % want, "predates" in (live_line.check(line, not_before=time.time() + 60, runner=sysd) or ""))
NC.SETTLE_S = settle1

# ---- a real kill under real systemd: the states a SIGKILL and a shutdown's SIGTERM leave, the restart, the finish. The unit is
# a throwaway stand-in for the sweep, with the sweep's section line and RESULT, so no 50-minute sweep is spent.
REAL = TMP / "real" / "Transient" / "selftests_nightly.log"
REAL.parent.mkdir(parents=True)
BODY = ("printf '\\n=== 2026-11-02T17:04:00Z nightly\\n' >>\"$L\"; if [ -e \"$F\" ]; then sleep 3; echo 'RESULT: GREEN' >>\"$L\"; "
        "else : >\"$F\"; sleep 300; echo 'RESULT: GREEN' >>\"$L\"; fi")


def real_ctl(*a):
    return "enabled" if a[0] == "is-enabled" else NC.systemctl(*a)


def wait_state(u, want, tries=60):
    for _ in range(tries):
        s = NC.systemctl("is-active", u)
        if s in want:
            return s
        time.sleep(0.25)
    return s


check("systemd answers: the rest of this block is real", NC.systemctl("is-system-running") is not None)
service0, settle0 = NC.SERVICE, NC.SETTLE_S
for sig, left in (("SIGKILL", {"failed"}), ("SIGTERM", NC.DOWN)):
    u = "rm-selftest-nc-%d-%s.service" % (os.getpid(), sig.lower())
    REAL.write_text(FINISHED_NOV1)
    flag = TMP / ("real_flag_" + sig)
    ok = subprocess.run(["systemd-run", "--user", "--unit=" + u, "--no-block", "--property=Type=oneshot", "--setenv=L=%s" % REAL,
                         "--setenv=F=%s" % flag, "/bin/sh", "-c", BODY], capture_output=True, timeout=60).returncode == 0
    check("%s: the stand-in starts" % sig, ok and wait_state(u, NC.UP) in NC.UP)
    try:
        for _ in range(40):
            if flag.exists():
                break
            time.sleep(0.25)
        subprocess.run(["systemctl", "--user", "kill", "--signal=" + sig, u], capture_output=True, timeout=60)
        s = wait_state(u, left)
        check("%s leaves %s, a section and no RESULT" % (sig, s), s in left and "RESULT" not in REAL.read_text().split("17:04:00Z")[-1], (s, REAL.read_text()))
        NC.SERVICE, NC.SETTLE_S = u, 1
        o = TMP / ("real_" + sig) / "nightly_catchup.json"
        r = NC.one_pass(BOOT, True, ctl=real_ctl, log=REAL, out=o)
        check("%s: the pass restarts it, try 2 of 3" % sig, r["state"] == "start" and "try 2 of 3" in r["why"] and r["started"] == 1, r)
        r = NC.one_pass(BOOT, True, ctl=real_ctl, log=REAL, out=o)
        check("%s: the next pass sees it running" % sig, r["state"] == "running" and r["started"] == 1, r)
        wait_state(u, NC.DOWN)
        r = NC.one_pass(BOOT, True, ctl=real_ctl, log=REAL, out=o)
        check("%s: and once it finishes, done, one start" % sig, r["state"] == "done" and r["started"] == 1, r)
    finally:
        NC.SERVICE, NC.SETTLE_S = service0, settle0
        subprocess.run(["systemctl", "--user", "stop", u], capture_output=True, timeout=60)
        subprocess.run(["systemctl", "--user", "reset-failed", u], capture_output=True, timeout=60)

print("selftest_nightly_catchup: %s" % ("FAIL: " + "; ".join(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
