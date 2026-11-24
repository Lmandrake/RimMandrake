#!/usr/bin/env python3
"""The control store's kill drill (item RIMMANDRAKE_DRILL_KILL_ON_THROWAWAY_UNIT_ZERO_LIVE_KILLS; design
2026-11-18-review-growth-cycle/01-design.md 5.4 step 3): each control verb that kills, blocks or launches is run once,
for real, on throwaway `rm-probe-drill-<tag>-*` units in REAL user systemd, on a store of its own (RM_CONTROL_DB in a
temp dir), never the live one. It names its own units exactly and aims at nothing else.

Steps, each against a promise on design/specs/2026-11-18-pipeline-control-surface/boundary.md:
  launch   launch_unit runs a trap fixture (it and its child ignore SIGTERM)    launch-through-one-door
  end      a `true` unit ends by itself: its ExecStopPost records it ended       (life cycle: started -> ended)
  off      `pipe off family:probe`: the next launch is refused, never run      off-blocks-starts
  kill     `pipe stop <unit> --kill` on the trap fixture                        kill-verified-dead
  escalate `pipe stop <unit> --write-now --deadline 1s` on a deaf sleep        three-named-stops (write-now -> kill)
  locked   `pipe stop <unit> --kill` while another writer holds the store       kill-works-without-the-store
  live     the live store has no row naming this drill's units                 a-test-never-touches-the-live-store

Prints one line per step, then its verdict LAST: `DRILL PASS <unit> killed in <N> ms; N processes gone; run recorded
killed` (exit 0), `DRILL FAIL <cause>` (exit 1), or `DRILL UNMEASURED <cause>` (exit 3: user systemd cannot be
reached; not a pass)."""
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="rm-control-drill-")
DB = os.path.join(TMP, "control.db")
os.environ["RM_CONTROL_DB"] = DB        # before control is imported: every read and write of this run is the drill's
import control as C  # noqa: E402

PIPE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "pipe")
TAG = "rm-probe-drill-%d" % os.getpid()
TRAP = """#!/bin/bash
trap '' TERM
( trap '' TERM; exec -a rm-probe-drill-child sleep 1000 ) &
echo $! > "$1"
while true; do sleep 0.2; done
"""


class Fail(Exception):
    pass


def check(ok, what):
    if not ok:
        raise Fail(what)


def wait_for(fn, s):
    t = time.monotonic()
    while time.monotonic() - t < s:
        if fn():
            return True
        time.sleep(0.05)
    return bool(fn())


def state(unit):
    return (C.run_state(unit) or {}).get("state")


def pipe(*args):
    t = time.monotonic()
    r = subprocess.run([PIPE] + list(args), capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, RM_CONTROL_DB=DB))
    return r.returncode, r.stdout + r.stderr, int((time.monotonic() - t) * 1000)


def launch(name, payload):
    res = C.launch_unit(["--user", "--quiet", "--collect", "--"] + payload, {"family": "probe", "unit": name},
                        p=DB, capture_output=True, text=True, timeout=30)
    return res


def systemd_ok():
    try:
        r = subprocess.run(["systemctl", "--user", "is-system-running"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError) as e:
        return "systemctl could not run: %s" % e
    return None if r.stdout.strip() in ("running", "degraded") else "user systemd reads %r" % r.stdout.strip()


def drill(lines):
    C.init(DB)
    # launch: the trap fixture, through the one door
    u = TAG + "-kill"
    trap = os.path.join(TMP, "trap.sh")
    with open(trap, "w") as f:
        f.write(TRAP)
    os.chmod(trap, 0o755)
    pidf = os.path.join(TMP, "child.pid")
    res = launch(u, [trap, pidf])
    check(res.returncode == 0 and not res.refused, "launch: %s did not start (rc %s: %s)" % (
        u, res.returncode, res.why or (res.stderr or "")[:120]))  # cut-ok: test diagnostic display
    check(wait_for(lambda: os.path.exists(pidf) and open(pidf).read().strip(), 5) and state(u) == "started",
          "launch: %s reads %s, its child pid never appeared" % (u, state(u)))
    main = int(subprocess.run(["systemctl", "--user", "show", "-p", "MainPID", "--value", u], capture_output=True,
                              text=True, timeout=5).stdout.strip() or 0)
    child = int(open(pidf).read().strip())
    subprocess.run(["systemctl", "--user", "kill", "--signal=SIGTERM", "--kill-whom=all", u], timeout=10)
    time.sleep(0.3)
    check(main and C._alive(main) and C._alive(child), "launch: the fixture or its child did not ignore SIGTERM (the "
                                                       "kill would prove nothing)")
    pids, cg = C._cgroup_pids(u)    # the fixture, its child and its loop's current sleep
    check(pids.ok and {main, child} <= set(pids), "launch: %s's cgroup %s holds %s, not the fixture %d and its child %d" % (
        u, cg, pids, main, child))
    lines.append("launch   ok: %s started through launch_unit, %d processes in its cgroup, all ignore SIGTERM" % (
        u, len(pids)))
    # end: a run that ends by itself is recorded ended by its own receipt
    ue = TAG + "-end"
    res = launch(ue, ["/bin/true"])
    check(res.returncode == 0 and wait_for(lambda: state(ue) == "ended", 10), "end: %s reads %s, not ended" % (
        ue, state(ue)))
    lines.append("end      ok: %s ran /bin/true and its ExecStopPost recorded it ended" % ue)
    # off: a launch on an off scope is refused and never reaches systemd
    rc, out, _ms = pipe("off", "family:probe", "--why", "kill drill: off blocks starts")
    check(rc == 0, "off: pipe off family:probe failed (rc %d): %s" % (rc, out.strip()[:160]))  # cut-ok: test diagnostic display
    uo = TAG + "-off"
    res = launch(uo, ["/bin/sleep", "300"])
    loaded = subprocess.run(["systemctl", "--user", "show", "-p", "LoadState", "--value", uo + ".service"],
                            capture_output=True, text=True, timeout=5).stdout.strip()
    check(res.refused and res.returncode == C.LAUNCH_REFUSED_RC and loaded != "loaded",
          "off: %s launched past pipe off (refused %s, rc %s, LoadState %s)" % (uo, res.refused, res.returncode,
                                                                                loaded))
    rc, out, _ms = pipe("on", "family:probe", "--why", "kill drill: on again")
    check(rc == 0, "off: pipe on family:probe failed (rc %d): %s" % (rc, out.strip()[:160]))  # cut-ok: test diagnostic display
    lines.append("off      ok: %s refused (rc %d) and never reached systemd; pipe on again" % (uo, res.returncode))
    # kill: the trap fixture, by unit name
    rc, out, ms = pipe("stop", u, "--kill", "--why", "kill drill: SIGKILL the throwaway trap fixture")
    gone = wait_for(lambda: not any(C._alive(x) for x in pids), 2)
    check(rc == 0 and "dead in" in out, "kill: pipe stop %s --kill (rc %d): %s" % (u, rc, out.strip()[:200]))  # cut-ok: test diagnostic display
    check(gone, "kill: survivors after the kill: %s" % [x for x in pids if C._alive(x)])
    check(state(u) == "killed", "kill: %s's run reads %s, not killed" % (u, state(u)))
    kms = int(out.split("dead in", 1)[1].split()[0])
    lines.append("kill     ok: %s dead in %d ms (command %d ms), %d processes gone, run killed" % (u, kms, ms,
                                                                                                  len(pids)))
    # escalate: a write-now order past its deadline becomes a kill, through a real systemd timer
    ud = TAG + "-deaf"
    res = launch(ud, ["/bin/sleep", "300"])
    check(res.returncode == 0 and wait_for(lambda: state(ud) == "started", 5), "escalate: %s never started" % ud)
    rc, out, _ms = pipe("stop", ud, "--write-now", "--deadline", "1s", "--why", "kill drill: deaf run escalates")
    check(rc == 0 and "escalates to --kill" in out, "escalate: no escalation set (rc %d): %s" % (rc, out[:200]))  # cut-ok: test diagnostic display
    check(wait_for(lambda: state(ud) == "killed", 20), "escalate: %s reads %s 20 s after a 1 s deadline" % (
        ud, state(ud)))
    esc = C._q("SELECT * FROM acts WHERE kind='escalate' AND scope=?", ("unit:" + ud,), DB, one=True)
    check(esc is not None, "escalate: %s was killed but no escalate act says so" % ud)
    lines.append("escalate ok: %s write-now with a 1 s deadline was killed by its timer (act %s)" % (ud, esc["id"]))
    # locked: the kill does not wait on a store another writer holds
    ul = TAG + "-locked"
    res = launch(ul, ["/bin/sleep", "300"])
    check(res.returncode == 0 and wait_for(lambda: state(ul) == "started", 5), "locked: %s never started" % ul)
    held = threading.Event()

    def hold():
        c = sqlite3.connect(DB, isolation_level=None)
        c.execute("BEGIN EXCLUSIVE")
        held.set()
        time.sleep(1.0)
        c.execute("COMMIT")
        c.close()
    th = threading.Thread(target=hold)
    th.start()
    held.wait(5)
    rc, out, ms = pipe("stop", ul, "--kill", "--why", "kill drill: kill on a locked store")
    th.join()
    check(rc == 0 and "dead in" in out and "recorded after the kill" in out, "locked: pipe stop %s --kill did not "
          "kill first on a locked store (rc %d): %s" % (ul, rc, out.strip()[:200]))  # cut-ok: test diagnostic display
    check(state(ul) == "killed", "locked: %s reads %s after the store freed, not killed" % (ul, state(ul)))
    lines.append("locked   ok: %s killed while the store was held (%d ms), recorded killed once it freed" % (ul, ms))
    # live: the live store never heard of this drill
    if os.path.exists(C.DEFAULT_DB):
        lc = sqlite3.connect("file:%s?mode=ro" % C.DEFAULT_DB, uri=True, timeout=3)
        n = lc.execute("SELECT (SELECT COUNT(*) FROM runs WHERE unit LIKE ?) + (SELECT COUNT(*) FROM acts WHERE scope "
                       "LIKE ?)", (TAG + "%", "%" + TAG + "%")).fetchone()[0]
        lc.close()
        check(n == 0, "live: the live store holds %d row(s) naming %s" % (n, TAG))
        lines.append("live     ok: the live store holds 0 rows naming %s" % TAG)
    return "DRILL PASS %s killed in %d ms; %d processes gone; run recorded killed" % (u, kms, len(pids))


def cleanup():
    """Only this drill's own units, each by its exact name."""
    for s in ("kill", "end", "off", "deaf", "locked"):
        subprocess.run(["systemctl", "--user", "kill", "--signal=SIGKILL", "--kill-whom=all", "%s-%s.service" % (
            TAG, s)], capture_output=True, timeout=10)
        subprocess.run(["systemctl", "--user", "reset-failed", "%s-%s.service" % (TAG, s)], capture_output=True,
                       timeout=10)


def main():
    why = systemd_ok()
    if why:
        shutil.rmtree(TMP, ignore_errors=True)
        print("DRILL UNMEASURED %s" % why)
        return 3
    lines = []
    try:
        verdict, code = drill(lines), 0
    except Fail as e:
        verdict, code = "DRILL FAIL %s" % e, 1
    except Exception as e:      # noqa: BLE001  a crash is a failure named, never a pass
        verdict, code = "DRILL FAIL %s: %s" % (type(e).__name__, e), 1
    finally:
        cleanup()
    if code == 0:
        shutil.rmtree(TMP, ignore_errors=True)    # a failed drill keeps its store as evidence
    print("\n".join(lines + ([] if code == 0 else ["store kept: %s" % DB]) + [verdict]))
    return code


if __name__ == "__main__":
    sys.exit(main())
