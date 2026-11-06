#!/usr/bin/env python3
"""selftest for metronome_chores.py (OPS_METRONOME_MIGRATE_CLOCKS_FENCED): cadence, fence, refused starts and a torn
state file, on a fake systemctl and a temporary metronome directory. Touches no live unit.

    python3 src/RimMandrake/Utils/selftest_metronome_chores.py
"""
import contextlib
import io
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metronome  # noqa: E402
import metronome_chores as mc  # noqa: E402

fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


class Fake:
    def __init__(self, bad=(), raises=None):
        self.calls, self.bad, self.raises = [], set(bad), raises

    def __call__(self, argv, **kw):
        self.calls.append(argv)
        if self.raises:
            raise self.raises
        return subprocess.CompletedProcess(argv, 1 if argv[-1] in self.bad else 0, "", "nope")

    def units(self):
        return [a[-1] for a in self.calls]


def run(d, gen, chores, now, fake):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = mc.run_pass(d, gen, chores, now=now, runner=fake)
    return code, out.getvalue()


CH = [("a", 300), ("b", 900)]
with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    metronome.write_json(d / "state.json", dict(metronome.new_state(), generation=7))
    f = Fake()
    code, _ = run(d, 7, CH, 1000.0, f)
    ok(code == 0 and f.units() == ["a.service", "b.service"], "first pass starts every chore")
    ok(all(a[:4] == ["systemctl", "--user", "start", "--no-block"] for a in f.calls), "starts never wait for the unit")

    f = Fake()
    run(d, 7, CH, 1200.0, f)
    ok(f.calls == [], "nothing is due before its interval")

    f = Fake()
    run(d, 7, CH, 1000.0 + 300 - mc.SLACK_S, f)
    ok(f.units() == ["a.service"], "a beat inside the slack still runs a chore; the slower one waits")

    f = Fake()
    run(d, 7, CH, 1000.0 + 900, f)
    ok(f.units() == ["a.service", "b.service"], "both run at the longer interval")

    # the fence
    f = Fake()
    code, out = run(d, 6, CH, 9000.0, f)
    ok(code == mc.EXIT_FENCED and f.calls == [] and "fenced" in out, "a superseded generation starts nothing, exit 3")
    metronome.set_fence(d, "chores", 7)
    f = Fake()
    code, _ = run(d, 7, CH, 9000.0, f)
    ok(code == mc.EXIT_FENCED and f.calls == [], "a killed generation starts nothing, exit 3")

with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    metronome.write_json(d / "state.json", dict(metronome.new_state(), generation=1))
    # a refused start is not marked started, and does not stop the next chore
    f = Fake(bad={"a.service"})
    code, out = run(d, 1, CH, 1000.0, f)
    ok(code == 1 and f.units() == ["a.service", "b.service"] and "could not start a" in out,
       "a refused start exits 1 and the next chore still runs")
    f = Fake()
    code, _ = run(d, 1, CH, 1060.0, f)
    ok(code == 0 and f.units() == ["a.service"], "the refused chore is retried next beat; the started one is not")

    f = Fake(raises=subprocess.TimeoutExpired("systemctl", 3))
    code, _ = run(d, 1, [("c", 300)], 2000.0, f)
    ok(code == 1, "a hung systemctl is a failed start, not a crash")

    # the stamp is written at each start, so a kill mid-pass does not repeat a started chore
    (d / "chores_state.json").write_text("{torn", encoding="utf-8")
    f = Fake()
    code, _ = run(d, 1, CH, 3000.0, f)
    ok(code == 0 and len(f.calls) == 2, "a torn state file makes every chore due, it does not crash")
    f = Fake()
    run(d, 1, CH, 3000.0 + 1, f)
    ok(f.calls == [], "the state was rewritten after the torn file")

ok(not mc.due(300, 1000.0, 1100.0) and mc.due(300, 5000.0, 1000.0), "a stamp from the future does not stop a chore for good")
for bad in ("a", "a:", ":5", "a:0", "a:x", "a.service:5", "a.timer:5"):
    try:
        mc.parse_chore(bad)
        ok(False, "parse_chore refuses %r" % bad)
    except Exception:
        ok(True, "parse_chore refuses %r" % bad)
ok(mc.parse_chore("rm-account-usage:900") == ("rm-account-usage", 900), "parse_chore reads unit:seconds")

print("selftest_metronome_chores: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
