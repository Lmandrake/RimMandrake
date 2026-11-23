#!/usr/bin/env python3
"""selftest_wrapup_restore_at_release.py — RIMMANDRAKE_WIRE_WRAPUP_RESTORE_ORPHANED_BY_RETIRED_TICK: since the Relentless
tick retired nothing ran `wrapup.py restore`, so a setting a run forced and still owed stayed forced. `rimflow bridge
release` now replays the owed settings while the releasing seat still holds the bridge (wrapup.restore_at_release).

  W1  a seat releasing its OWN hold with a planned setting debt owed: `python.exe wrapup.py restore` runs before the
      release (the ledger holds no `released` event as it starts), its tally is printed, and the bridge ends free
  W2  nothing owed: python.exe is never started
  W3  a crossed release (another seat frees the hold) never replays: the real holder may still be working
  W4  a restore that fails (exit 1) never stops the release
  W5  `release --mine` replays too
  W6  restore_at_release in-process: a void debt (owed to an exited game) is not owed; a runner that raises or times out
      answers (None, why), never raises; under RM_UNDER_SELFTEST the real runner is never used
  W7  a release on a throwaway ledger (RIMFLOW_LEDGER) never replays the real register (RM_WRAPUP_DIR unset): its hold
      is a fixture, the game it would write is real. RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT: on
      2026-11-23 ./publish's run of selftest_conductor_acts.py replayed live debts onto ArchBig this way

Runs the real cli on a throwaway ledger, wrap-up register and fake python.exe; touches nothing real."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIM = os.path.dirname(HERE)
CLI = os.path.join(HERE, "cli.py")
FAILS = []
TMP = tempfile.mkdtemp(prefix="st_wrapup_release_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "wrapup")
os.environ["RM_WRAPUP_PREV_LOG"] = ""           # the real game's relaunch never voids a test debt
sys.path[:0] = [HERE, os.path.join(RIM, "Utils")]
import wrapup  # noqa: E402


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


BIN = os.path.join(TMP, "bin")
MARK = os.path.join(TMP, "python_exe_calls.txt")


def fake_bin(rc=0):
    os.makedirs(BIN, exist_ok=True)
    with open(os.path.join(BIN, "python.exe"), "w") as f:
        # each call records its args and how many `released` events the ledger held as it started (0 = still held)
        f.write("#!/bin/sh\necho \"$@ released=$(cat \"$(dirname \"$RIMFLOW_LEDGER\")\"/events/*.jsonl | grep -c '\"released\"')\" >> %s\necho 'wrapup restore: 1 restored, 0 failed, 0 without a plan, 0 void; "
                "sweep 0 cleared, 0 open'\nexit %d\n" % (MARK, rc))
    with open(os.path.join(BIN, "wslpath"), "w") as f:
        f.write("#!/bin/sh\necho \"$2\"\n")
    for n in ("python.exe", "wslpath"):
        os.chmod(os.path.join(BIN, n), 0o755)


def calls():
    if not os.path.exists(MARK):
        return []
    with open(MARK) as f:
        return [x.strip() for x in f if x.strip()]


def owe_planned():
    D = wrapup._door()
    return wrapup.owe("setting", "selftest forced debug logRaidInfo=True", "set it back",
                      extra={"plan": [D.step("jawa/debug_settings", action="set", field="logRaidInfo", value=False)]})


def clear_register():
    shutil.rmtree(os.environ["RM_WRAPUP_DIR"], ignore_errors=True)
    if os.path.exists(MARK):
        os.remove(MARK)


class Rig:
    def __init__(self, name):
        self.tmp = os.path.join(TMP, name)
        os.makedirs(os.path.join(self.tmp, "items"))
        self.base = {k: v for k, v in os.environ.items() if k not in (
            "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY", "RM_DRIVER_PID",
            "RIMFLOW_BRIDGE_SEAT", "RELENTLESS_SUPERVISOR", "RM_HOST_GUARD_GEN", "RM_UNDER_SELFTEST")}
        self.base.update(RIMFLOW_LEDGER=os.path.join(self.tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(self.tmp, "items"),
                         RIMFLOW_PROBE="no-reading",
                         RIMFLOW_DISPATCH_LOCK=os.path.join(self.tmp, "dispatch.lock"),
                         RIMFLOW_BRIDGE_LOCK=os.path.join(self.tmp, "bridge.lock"),
                         RIMFLOW_OWNER_ACT_STAMP=os.path.join(self.tmp, "act.json"),
                         RIMFLOW_DRIVER_LOCK="", PATH=BIN + os.pathsep + os.environ.get("PATH", ""))

    def rf(self, seat, *a):
        r = subprocess.run([sys.executable, CLI, *a], env=dict(self.base, RIMFLOW_SEAT=seat), capture_output=True,
                           text=True, timeout=120, cwd=self.tmp)
        return r.returncode, r.stdout + r.stderr

    def holder(self):
        r = subprocess.run([sys.executable, "-c", "import os, sys; sys.path[:0] = [%r, %r]\nfrom rimflow import model as m; "
                            "m.EVENTS = os.environ['RIMFLOW_LEDGER']; print(m.replay(m.read()).bridge_holder)" % (RIM, HERE)],
                           env=self.base, capture_output=True, text=True, timeout=60, cwd=self.tmp)
        return (r.stdout + r.stderr).strip()


def release_rows():
    fake_bin(0)
    # W1: own hold, a planned debt owed
    clear_register()
    owe_planned()
    g = Rig("w1")
    rc, out = g.rf("BENCH", "bridge", "take", "--for", "selftest")
    check(rc == 0 and g.holder() == "BENCH", "W1 setup: BENCH takes the bridge (%s)" % out.strip()[-80:])
    rc, out = g.rf("BENCH", "bridge", "release")
    want = os.path.join(HERE, "wrapup.py") + " restore released=0"
    check(calls() == [want], "W1 python.exe <wrapup.py> restore ran once, before any release event: %s" % calls())
    check("wrapup restore before release: wrapup restore: 1 restored" in out, "W1 the tally is printed: %s" % out[:160])
    check(rc == 0 and g.holder() == "None", "W1 the bridge ends free (rc %d, holder %s)" % (rc, g.holder()))

    # W2: nothing owed
    clear_register()
    g = Rig("w2")
    g.rf("BENCH", "bridge", "take", "--for", "selftest")
    rc, out = g.rf("BENCH", "bridge", "release")
    check(calls() == [] and "wrapup restore" not in out, "W2 nothing owed: python.exe never started (%s)" % calls())
    check(rc == 0 and g.holder() == "None", "W2 the release still happens")

    # W3: crossed release
    clear_register()
    owe_planned()
    g = Rig("w3")
    g.rf("BENCH", "bridge", "take", "--for", "selftest")
    rc, out = g.rf("OWNER", "bridge", "release")
    check(calls() == [], "W3 a crossed release never replays: %s" % calls())
    check(g.holder() == "None", "W3 the crossed release itself still happens (rc %d: %s)" % (rc, out.strip()[-80:]))

    # W4: restore fails, release goes on
    fake_bin(1)
    clear_register()
    owe_planned()
    g = Rig("w4")
    g.rf("BENCH", "bridge", "take", "--for", "selftest")
    rc, out = g.rf("BENCH", "bridge", "release")
    check(len(calls()) == 1 and "(exit 1)" in out, "W4 the failed restore is named: %s" % out[:160])
    check(rc == 0 and g.holder() == "None", "W4 a failed restore never stops the release (rc %d)" % rc)

    # W5: release --mine
    fake_bin(0)
    clear_register()
    owe_planned()
    g = Rig("w5")
    g.rf("BENCH", "bridge", "take", "--for", "selftest")
    rc, out = g.rf("BENCH", "bridge", "release", "--mine")
    check(len(calls()) == 1 and rc == 0 and g.holder() == "None", "W5 release --mine replays and frees (rc %d, %s)"
          % (rc, calls()))


class World:
    def __init__(self, relaunched=None):
        self.t = relaunched

    def game_relaunched(self):
        return self.t


def unit_rows():
    clear_register()
    tok = owe_planned()
    check(wrapup.owed_plans(World()) == [tok], "W6 a planned debt is owed")
    import time
    check(wrapup.owed_plans(World(time.time() + 3600)) == [], "W6 a debt owed before the game relaunched is void")

    def boom(*a, **k):
        raise OSError("no such interpreter")

    def slow(*a, **k):
        raise subprocess.TimeoutExpired(a[0], 1)
    code, line = wrapup.restore_at_release(runner=boom, world=World(), env={})
    check(code is None and "could not run" in line, "W6 a runner that raises -> (None, why): %s" % line)
    code, line = wrapup.restore_at_release(runner=slow, world=World(), env={})
    check(code is None and "timed out" in line, "W6 a timeout -> (None, why): %s" % line)
    code, line = wrapup.restore_at_release(world=World(), env={"RM_UNDER_SELFTEST": "1"})
    check(code is None and "under a selftest" in line, "W6 under RM_UNDER_SELFTEST the real runner is never used")
    clear_register()
    code, line = wrapup.restore_at_release(runner=boom, world=World(), env={})
    check(code is None and "no planned setting debt" in line, "W6 nothing owed -> not run: %s" % line)
    clear_register()
    owe_planned()
    ran = []
    code, line = wrapup.restore_at_release(runner=lambda *a, **k: ran.append(a) or subprocess.CompletedProcess(a, 0, "", ""),
                                           world=World(), env={"RIMFLOW_LEDGER": os.path.join(TMP, "x.jsonl")})
    check(ran == [] and code is None and "throwaway ledger" in line,
          "W7 a throwaway ledger never replays the real register: %s (%d runs)" % (line, len(ran)))
    ran = []
    code, line = wrapup.restore_at_release(runner=lambda *a, **k: ran.append(a) or subprocess.CompletedProcess(a, 0, "", ""),
                                           world=World(), env={"RIMFLOW_LEDGER": os.path.join(TMP, "x.jsonl"),
                                                               "RM_WRAPUP_DIR": os.environ["RM_WRAPUP_DIR"]})
    check(len(ran) == 2, "W7 a throwaway ledger with its own register still replays it (wslpath + python.exe: %d)" % len(ran))


def main():
    try:
        unit_rows()
        release_rows()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_wrapup_restore_at_release: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
