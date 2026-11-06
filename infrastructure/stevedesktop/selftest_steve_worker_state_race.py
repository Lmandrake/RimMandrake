#!/usr/bin/env python3
"""selftest_steve_worker_state_race.py - two threads write an attempt's state.json and neither may lose
(HARNESS_REPAIR_CAUSE_B338C64C).

The main thread beats at each phase change and the heartbeat thread every HEARTBEAT_S. Both named one temp file (per pid),
so a phase change landing on a heartbeat tick crashed the attempt with no verdict: `FileNotFoundError in phase load`,
job J20261106T134317Z-55ba0d, a phase switch exactly 90 s (tick six) after the heartbeat started. No retry: the writers must
not meet. Runs on any filesystem; the two-path ENOENT reproduces on ext4 within a second, drvfs adds the one-path form.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
HOME = tempfile.mkdtemp(prefix="testq_state_race_home_")
os.environ["TESTQ_HOME"] = HOME     # never the real queue, even when the caller's environment names one
import worker as W  # noqa: E402
S = W.S

SECONDS = 3.0
FAILS = []


def check(ok, msg):
    print("%s %s" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def hammer(writer, threads=2):
    """-> the errors `writer` raised, from N threads running together for SECONDS."""
    errors, end = [], time.time() + SECONDS

    def run():
        while time.time() < end:
            try:
                writer()
            except Exception as e:      # noqa: BLE001 - any writer failure is the finding
                errors.append("%s: %s" % (type(e).__name__, e))
    ts = [threading.Thread(target=run) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return errors


def attempt(d):
    a = W.Attempt.__new__(W.Attempt)
    a.d, a.phase = d, "deploy"
    a.res = {"runner_sha": "x", "retries": 0, "phase_s": {}}
    a.state_lock = threading.Lock()     # as Attempt.__init__: the rest of __init__ reads a real job
    return a


def main():
    d = tempfile.mkdtemp(prefix="testq_state_race_")
    try:
        path = os.path.join(d, "x.json")
        errors = hammer(lambda: S.dump({"a": 1}, path))
        check(not errors, "S.dump from two threads on one path: %d errors %s" % (len(errors), errors[:1]))

        path = os.path.join(d, "x.txt")
        errors = hammer(lambda: W.write_text(path, "a"))
        check(not errors, "write_text from two threads on one path: %d errors %s" % (len(errors), errors[:1]))

        a = attempt(d)
        errors = hammer(a.beat)
        check(not errors, "beat from two threads: %d errors %s" % (len(errors), errors[:1]))

        # The real shape: the heartbeat runs while the main thread walks phases, adding phase_s rows as timed() does.
        # A beat that returned must have left its own phase: a heartbeat holding an older one may not land after it.
        stop, stale, hb_errors = threading.Event(), [], []

        def heartbeat():
            while not stop.is_set():
                try:
                    a.beat()
                except Exception as e:  # noqa: BLE001 - heartbeat_loop only survives OSError; anything else kills it
                    hb_errors.append("%s: %s" % (type(e).__name__, e))
        t = threading.Thread(target=heartbeat)
        t.start()
        end, n, main_errors = time.time() + SECONDS, 0, []
        state = os.path.join(d, "state.json")
        while time.time() < end:
            n += 1
            a.phase = "phase%d" % n
            a.res["phase_s"]["p%d" % n] = n
            try:
                a.beat()
                got = json.load(open(state, encoding="utf-8"))["phase"]
                if got != a.phase:
                    stale.append((a.phase, got))
            except (OSError, ValueError) as e:
                main_errors.append("%s: %s" % (type(e).__name__, e))
        stop.set()
        t.join()
        check(n > 10, "the walk really ran (%d phase changes)" % n)
        check(not main_errors, "a phase change meeting the heartbeat: %d errors %s" % (len(main_errors), main_errors[:1]))
        check(not hb_errors, "the heartbeat survives phase_s growing under it: %d errors %s" % (len(hb_errors), hb_errors[:1]))
        check(not stale, "state.json holds the phase just beaten: %d stale %s" % (len(stale), stale[:1]))
        left = [f for f in os.listdir(d) if ".tmp." in f]
        check(not left, "no temp file left behind: %s" % left[:3])
    finally:
        shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree(HOME, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "selftest_steve_worker_state_race: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
