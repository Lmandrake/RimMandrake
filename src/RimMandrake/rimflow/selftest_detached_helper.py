#!/usr/bin/env python3
"""selftest_detached_helper.py — the detached launcher (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

All in a temp state dir with a faked runner: no systemd unit, no claude, no clone, no rimflow write, no real log.
  refuse     an unknown item, a blind ledger read, a bad model, an empty brief, an out-of-range bound: nothing starts
  argv       role_launch's shape: systemd-run --user, claude_bounded.sh -p, the model, RuntimeMaxSec and the scope
             bound, --max-budget-usd, ExecStopPost=finish, RM_DISPATCHER_STATE for the finish step, the brief footer
  record     a launch records the run; a systemd-run refusal marks it launch_failed
  finish     a note on the item, the shard published from the clone, one Conductor log line, tokens read; once only
  killed     a run killed at its bound (no result JSON) still finishes, with the stderr tail
  guard      the real Conductor log is refused from a test process
  hook       the spawn hook's drain refusal points at this launcher
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_detached_helper_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

FAILS = []
T0 = 1_800_000_000.0
KNOWN = {"SOME_ITEM_TO_BUILD"}
CLONE = os.path.join(TMP, "clone")


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


class R:
    def __init__(self, rc=0, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def recorder(rc=0, out=""):
    calls = []

    def run(argv, **kw):
        calls.append((argv, kw))
        return R(rc, out)
    return calls, run


def test_refuse():
    calls, run = recorder()
    for args, word in (((("BENCH", "NOT_AN_ITEM", "b", "sonnet", 600, 5)), "not a ledger item"),
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "b", "gpt", 600, 5)), "model"),
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "  ", "sonnet", 600, 5)), "empty brief"),
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 99999, 5)), "--max-s"),
                       ((("NOPE", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5)), "seat")):
        rc, text = DH.launch(*args, now=T0, runner=run, known=KNOWN, clone=CLONE)
        check(rc == 2 and word in text, "refuse: %s (%s)" % (word, text[:60]))
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0, runner=run, known=set(),
                         clone=CLONE)
    check(rc == 2 and "blind" in text, "refuse: a ledger read of 0 items is blind, not a pass")
    check(calls == [], "refuse: nothing was started")


def test_launch_and_finish():
    calls, run = recorder()
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build the thing.", "opus", 1800, 12, now=T0, runner=run,
                         known=KNOWN, clone=CLONE)
    check(rc == 0 and "DETACHED rm-detached-bench-some-item-to-build-" in text, "launch: ok (%s)" % text[:70])
    argv = calls[0][0]
    j = " ".join(argv)
    check(argv[:3] == ["systemd-run", "--user", "--quiet"] and "claude_bounded.sh" in j, "argv: systemd-run + claude_bounded")
    check(argv[argv.index("--model") + 1] == "opus" and "-p" in argv[argv.index("--"):], "argv: the model, -p")
    check("RuntimeMaxSec=%d" % (1800 + DH.GRACE_S) in argv and "CLAUDE_SCOPE_RUNTIME_MAX=%d" % (1800 + DH.GRACE_S) in argv,
          "argv: wall time bounded twice (unit and scope)")
    check(argv[argv.index("--max-budget-usd") + 1] == "12", "argv: spend bounded by --max-budget-usd")
    check(any(a.startswith("ExecStopPost=/usr/bin/python3 ") and a.endswith("finish --unit " + argv[argv.index("--unit") + 1])
              for a in argv), "argv: ExecStopPost runs finish for this unit")
    check("RM_DISPATCHER_STATE=" + os.environ["RM_DISPATCHER_STATE"] in argv, "argv: the finish step finds the record")
    msg = argv[argv.index("-p", argv.index("--")) + 1]
    check(msg.startswith("Build the thing.") and "cli.py note SOME_ITEM_TO_BUILD" in msg and "./publish" in msg,
          "argv: the brief carries the note-and-publish footer")
    unit = argv[argv.index("--unit") + 1]
    rec = DH.read_record(unit)
    check(rec and rec["status"] == "running" and rec["clone"] == CLONE, "record: the run is recorded running")
    with open(rec["out"], "w") as f:
        json.dump({"result": "Built it; sha abc123.", "usage": {"input_tokens": 10, "output_tokens": 5,
                   "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}, f)
    fcalls, frun = recorder(out="PUBLISHED abcdef1234567")
    rc, text = DH.finish(unit, now=T0 + 600, env={"SERVICE_RESULT": "success", "EXIT_CODE": "exited",
                                                  "EXIT_STATUS": "0"}, runner=frun)
    note = fcalls[0][0]
    check(note[2:4] == ["note", "SOME_ITEM_TO_BUILD"] and "--text" in note and fcalls[0][1].get("cwd") == CLONE,
          "finish: a note on the item, from the clone")
    nt = note[note.index("--text") + 1]
    check("success" in nt and "Built it" in nt and "600 s" in nt, "finish: the note says how it ended (%s)" % nt[:80])
    check(fcalls[1][0][0] == "./publish" and fcalls[1][0][-1] == "infrastructure/state/ledger/events/BENCH.jsonl",
          "finish: the seat shard is published")
    with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
        log = f.read()
    check(log.count("DETACHED RUN ENDED") == 1 and "SOME_ITEM_TO_BUILD" in log, "finish: one Conductor log line")
    rec = DH.read_record(unit)
    check(rec["status"] == "finished" and isinstance(rec["tokens"], int) and "publish abcdef1234" in text,
          "finish: recorded finished with tokens and the publish sha (%s)" % text[-60:])
    rc, text = DH.finish(unit, now=T0 + 700, env={}, runner=frun)
    check(rc == 0 and "already" in text and len(fcalls) == 2, "finish: a second call changes nothing")


def test_killed_and_failed_launch():
    calls, run = recorder()
    DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 1, runner=run, known=KNOWN, clone=CLONE)
    unit = calls[0][0][calls[0][0].index("--unit") + 1]
    rec = DH.read_record(unit)
    with open(rec["err"], "w") as f:
        f.write("Terminated\n")
    fcalls, frun = recorder()
    rc, text = DH.finish(unit, now=T0 + 800, env={"SERVICE_RESULT": "timeout", "EXIT_CODE": "killed",
                                                  "EXIT_STATUS": "TERM"}, runner=frun)
    nt = fcalls[0][0][fcalls[0][0].index("--text") + 1]
    check(rc == 0 and "timeout" in nt and "UNMEASURED" in nt and "Terminated" in nt,
          "killed: a run killed at its bound still ends with a note (%s)" % nt[:90])
    calls, run = recorder(rc=1, out="Failed to start transient service unit")
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 2, runner=run, known=KNOWN,
                         clone=CLONE)
    unit = calls[0][0][calls[0][0].index("--unit") + 1]
    check(rc == 1 and DH.read_record(unit)["status"] == "launch_failed", "record: a refused systemd-run is launch_failed")


def test_guard():
    try:
        DH.conductor_line("x", T0, path=DH.REAL_LOG)
        ok = False
    except RuntimeError:
        ok = True
    check(ok, "guard: the real Conductor log is refused from a test process")


def test_hook_points_here():
    hook = os.path.join(HERE, "..", "..", "..", ".claude", "hooks", "block_agent_over_slots.py")
    with open(hook, encoding="utf-8") as f:
        src = f.read()
    check("detached_helper.py launch" in src, "hook: the drain refusal names detached_helper.py launch")


def main():
    test_refuse()
    test_launch_and_finish()
    test_killed_and_failed_launch()
    test_guard()
    test_hook_points_here()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
