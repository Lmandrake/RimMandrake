#!/usr/bin/env python3
"""selftest_nightly_catchup: NIGHTLY_SWEEP_HARDEN_DIED_AT_SIXTY. A sweep killed mid-run runs again on its own.

testdata below is the real log's section shape from 2026-11-02: the 03:21 PST sweep killed with nothing under its line, then
the hand restart at 09:07 that finished. Runs the real pass with a fake systemctl only; the unit files are read as shipped.
"""
import configparser
import json
import os
import sys
import tempfile
from pathlib import Path

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

print("selftest_nightly_catchup: %s" % ("FAIL: " + "; ".join(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
