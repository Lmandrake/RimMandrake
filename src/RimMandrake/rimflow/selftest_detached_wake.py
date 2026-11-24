#!/usr/bin/env python3
"""Acceptance selftest for RIMMANDRAKE_WAKE_CONDUCTOR_ON_RUN_END_LOG_ONLY_TODAY: a finished detached run of the
Conductor's seat reaches the live Conductor window (run_end_wake.py), and with no live window nothing is pending and the
Conductor log line stands.

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_detached_wake.py

LIVE HALF, UNRUN (the ticket: never run by the building run): in the Conductor window, launch a 30-second detached run
(`python3 src/RimMandrake/rimflow/detached_helper.py launch --seat BENCH --item <ID> --brief "Say done." --max-s 60 --budget-usd 1`)
and stay quiet: within a minute of its end the window wakes with "[RimFlow] 1 detached run(s) ended …" naming the run,
its state and its result path.
"""
import functools
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_detached_wake_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import run_end_wake as RW  # noqa: E402

RESULTS = []
T0 = 1_800_000_000.0
STATE = os.environ["RM_DISPATCHER_STATE"]
CLONE = os.path.join(TMP, "clone")
os.makedirs(CLONE)


def check(ok, what):
    RESULTS.append((bool(ok), what))


class R:
    def __init__(self, rc=0, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def runner(argv, **kw):
    return R(0, "PUBLISHED abcdef1234567" if argv[:1] == ["./publish"] else "")


def ended_run(unit, seat="BENCH"):
    out = os.path.join(TMP, unit + ".out.json")
    with open(out, "w") as f:
        json.dump({"result": "Built it; sha abc123.", "usage": {"input_tokens": 10, "output_tokens": 5}}, f)
    DH.write_record({"unit": unit, "item": "SOME_ITEM_TO_BUILD", "seat": seat, "model": "opus", "clone": CLONE,
                     "out": out, "err": out[:-len(".out.json")] + ".err", "at": T0, "status": "running"})
    return out


def pending():
    d = os.path.join(RW.wake_dir(STATE), "pending")
    return [json.load(open(os.path.join(d, n))) for n in sorted(os.listdir(d))] if os.path.isdir(d) else []


def log_lines():
    p = os.environ["RM_CONDUCTOR_LOG"]
    return open(p).read().count("DETACHED RUN ENDED") if os.path.exists(p) else 0


def main():
    ok_env = {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"}
    item = lambda clone, iid: {"state": "done", "notes": []}  # noqa: E731
    # 1. a live Conductor window: exactly one pending wake line, with the run id, terminal state and full result path
    RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 1, "window_pid": 4242, "session_id": "S"})
    live = functools.partial(RW.post, root=STATE, alive=lambda pid: pid == 4242)
    out = ended_run("rm-detached-bench-wake-a-1800000000")
    rc, text = DH.finish("rm-detached-bench-wake-a-1800000000", now=T0 + 600, env=ok_env, runner=runner,
                         item_reader=item, waker=live)
    p = pending()
    check(rc == 0 and len(p) == 1, "a live window: exactly one pending wake line (%d)" % len(p))
    check(p and p[0]["unit"] == "rm-detached-bench-wake-a-1800000000" and p[0]["state"].startswith("success")
          and p[0]["result"] == out, "the line carries the run id, its terminal state and the full result path")
    check(log_lines() == 1, "the Conductor log line is written too")
    # 2. no live window (its pid gone): nothing pending, the log line stands
    for n in os.listdir(os.path.join(RW.wake_dir(STATE), "pending")):
        os.remove(os.path.join(RW.wake_dir(STATE), "pending", n))
    gone = functools.partial(RW.post, root=STATE, alive=lambda pid: False)
    ended_run("rm-detached-bench-wake-b-1800000001")
    rc, text = DH.finish("rm-detached-bench-wake-b-1800000001", now=T0 + 700, env={"SERVICE_RESULT": "timeout",
                         "EXIT_CODE": "killed"}, runner=runner, item_reader=item, waker=gone)
    check(rc == 0 and pending() == [] and log_lines() == 2 and "no live Conductor window" in text,
          "no live window: nothing pending, the log line stands")
    # 3. another seat's run never wakes the Conductor; a finish under a selftest never posts to the real one
    ended_run("rm-detached-foundry-wake-c-1800000002", seat="FOUNDRY")
    rc, text = DH.finish("rm-detached-foundry-wake-c-1800000002", now=T0 + 800, env=ok_env, runner=runner,
                         item_reader=item, waker=live)
    check(pending() == [] and "not the Conductor's seat" in text, "another seat's run wakes nobody")
    check("skipped under a selftest" in DH.wake_conductor("u", "success", "/o", "I", "BENCH"),
          "no waker under a selftest: the real window is never posted to")
    # 4. the hook's wait: a pending line wakes it (exit 2, the text names the run), consumed once
    live("rm-detached-bench-wake-d-1800000003", "failure (exit 1)", "/tmp/d.out.json", "SOME_ITEM_TO_BUILD")
    code, txt = RW.wait("S", 4242, root=STATE, me=99, alive=lambda pid: True, sleep=lambda s: None, max_wait=5)
    check(code == 2 and "rm-detached-bench-wake-d-1800000003" in txt and "/tmp/d.out.json" in txt and pending() == [],
          "the Stop hook's wait wakes the window with the line, consumed once")
    # 5. a hold (handoff or restart drain) keeps the line for the next window; a superseded waiter never consumes
    live("rm-detached-bench-wake-e-1800000004", "success", "/tmp/e.out.json")
    clock = iter(range(0, 100)).__next__
    code, txt = RW.wait("S", 4242, root=STATE, me=99, alive=lambda pid: True, hold=lambda: True,
                        sleep=lambda s: None, clock=lambda: clock(), max_wait=5)
    check(code == 0 and len(pending()) == 1, "a hold keeps the line for the next window")
    RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 123, "window_pid": 4242, "session_id": "S2"})
    check(RW.deliver(99, root=STATE) is None and len(pending()) == 1,
          "a waiter that is no longer the armed one consumes nothing, checked under the lock")
    code, txt = RW.wait("S", 4242, root=STATE, me=99, alive=lambda pid: True, hold=lambda: True,
                        sleep=lambda s: RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 123,
                                                                       "window_pid": 4242}), max_wait=10)
    check(code == 0 and "superseded" in txt and len(pending()) == 1, "a newer Stop's waiter supersedes the older one")
    # 6. giving up or outliving the window disarms: nothing is posted to a window nobody waits in
    clock = iter(range(0, 100)).__next__
    code, txt = RW.wait("S", 4242, root=STATE, me=77, alive=lambda pid: True, hold=lambda: True,
                        sleep=lambda s: None, clock=lambda: clock(), max_wait=3)
    check(code == 0 and "gave up" in txt and not os.path.exists(RW.armed_path(STATE))
          and RW.post("u2", "success", "/o", root=STATE, alive=lambda pid: True) is None,
          "a waiter that gives up disarms, so a later run end posts nothing")
    code, txt = RW.wait("S", 4242, root=STATE, me=78, alive=lambda pid: False, sleep=lambda s: None, max_wait=5)
    check(code == 0 and "gone" in txt and not os.path.exists(RW.armed_path(STATE)) and len(pending()) == 1,
          "a gone window ends the wait, disarms and delivers nothing")
    # 7. hook_main admits only the interactive Conductor window, and holds on a HANDOFF READY turn
    import seat_restart as SR
    import io
    sfs = {"conductor": {"name": "CONDUCTOR", "entrypoint": "cli"},
           "print": {"name": "CONDUCTOR", "entrypoint": "sdk-cli"},
           "detached": {"name": "DETACHED BENCH X", "entrypoint": "sdk-cli"}}
    real = (RW.doorbell.claude_ancestor, SR.session_file, RW.MAX_WAIT_S, RW.POLL_S, RW.default_readers)
    try:
        RW.default_readers = lambda: {}     # the real readers are selftest_run_end_wake_result's and the live wake's
        RW.doorbell.claude_ancestor = lambda pid=None: os.getpid()
        RW.MAX_WAIT_S, RW.POLL_S = 2, 0.05
        for kind, want in (("conductor", 2), ("print", 0), ("detached", 0)):
            SR.session_file = lambda pid, k=kind: sfs[k]
            code = RW.hook_main(stdin=io.StringIO(json.dumps({"session_id": "S"})), env={"AGENT_SEAT": "BENCH"})
            check(code == want, "hook_main on a %s window: exit %d (%d)" % (kind, want, code))
            if kind == "conductor":
                check(len(pending()) == 0, "the interactive Conductor window took the waiting line")
                RW.post("rm-detached-bench-wake-f-1800000005", "success", "/tmp/f.out.json", root=STATE,
                        alive=lambda pid: True)
        SR.session_file = lambda pid: sfs["conductor"]
        code = RW.hook_main(stdin=io.StringIO(json.dumps({"session_id": "S", "last_assistant_message":
                                                          "All landed.\n\nHANDOFF READY 3:05 PM PST"})),
                            env={"AGENT_SEAT": "BENCH"})
        check(code == 0 and len(pending()) == 1, "a HANDOFF READY turn delivers nothing (exit %d, %d pending)" % (
            code, len(pending())))
        check(RW.hook_main(stdin=io.StringIO("{}"), env={"AGENT_SEAT": "FOUNDRY"}) == 0, "another seat exits 0 at once")
    finally:
        RW.doorbell.claude_ancestor, SR.session_file, RW.MAX_WAIT_S, RW.POLL_S, RW.default_readers = real
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
