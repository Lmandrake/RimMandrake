#!/usr/bin/env python3
"""Selftest of the run-end wake's result and state block (RIMMANDRAKE_CARRY_RESULT_IN_CONDUCTOR_WAKE_408_FILES_OPENED).
Each promise of design/specs/2026-11-23-wake-carries-result/boundary.md has a test of its name.

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_run_end_wake_result.py
"""
import io
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_run_end_wake_result_")
STATE = os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "cfg")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import run_end_wake as RW  # noqa: E402

RESULTS = []
N = [0]


def check(ok, what):
    RESULTS.append((bool(ok), what))


def rec(result="the answer", raw=None, missing=False, state="success (exited 0)", err=None, **extra):
    """A pending record with its result file; the file's spend fields are always there."""
    N[0] += 1
    unit = "u%d" % N[0]
    p = os.path.join(TMP, unit + ".out.json")
    res = {"type": "result", "result": result, "is_error": False, "session_id": "s", "num_turns": 3,
           "total_cost_usd": 12.34, "cap_usd": 98.76, "weighted_tokens": 7654321, "usage": {"output_tokens": 4455667},
           "modelUsage": {"m": {"costUSD": 55.44}}}
    res.update({k: v for k, v in extra.items() if k in ("is_error", "subtype", "result_index", "session_id", "stopped_by")})
    if not missing:
        with open(p, "w") as f:
            f.write(raw if raw is not None else json.dumps(res))
    if err is not None:
        with open(os.path.join(TMP, unit + ".err"), "w") as f:
            f.write(err)
    return {"unit": unit, "state": state, "result": p, "item": "ITEM_%d" % N[0], "at": 1795492604 + N[0],
            "owed": extra.get("owed", "")}


def transcript(sid, finals):
    d = os.path.join(TMP, "cfg", "projects", "-x")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sid + ".jsonl"), "w") as f:
        for t in finals:
            f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}}) + "\n")
            f.write(json.dumps({"type": "system", "subtype": "stop_hook_summary"}) + "\n")


def t_the_whole_last_message():
    parts = ["PART%05d %s" % (i, "z" * 90) for i in range(900)]
    got = RW.render([rec("\n".join(parts))])
    check(all(p in got for p in parts), "the-whole-last-message: every one of 900 lines stands (90,000 characters)")
    check(RW.report_of(rec("hello"))["text"] == "hello", "the-whole-last-message: a short message is as written")
    transcript("sess-late", ["THE REPORT", "late remark"])
    r = RW.report_of(rec("late remark", result_index=1, session_id="sess-late"))
    check(r["status"] == "value" and r["text"].startswith("THE REPORT") and "late remark" in r["text"],
          "the-whole-last-message: the report before a late remark is read (run_report's rule)")
    r = RW.report_of(rec("late remark", result_index=1, session_id="sess-none"))
    check("late remark" in r["text"] and "UNMEASURED" in r["text"],
          "the-whole-last-message: a report that cannot be read is named beside the last message")
    real = DH.run_report
    DH.run_report = lambda run, res=None: 1 / 0
    try:
        r = RW.report_of(rec("late remark", result_index=1))
        check(r["text"] == "late remark" and "COULD NOT" in r["why"] and "late remark" in RW.render([rec("late remark")]),
              "the-whole-last-message: a report reader that breaks leaves the last message, and says so")
    finally:
        DH.run_report = real


def t_could_not_look_is_said():
    st = lambda r: RW.report_of(r)["status"]  # noqa: E731
    for text in ("", "  \n"):
        check(st(rec(text)) == "empty" and "EMPTY" in RW.render([rec(text)]) and "COULD NOT LOOK" not in RW.render(
            [rec(text)]), "could-not-look-is-said: an empty last message (%r) reads empty" % text)
    for what, r in (("no file", rec(missing=True)), ("an empty file", rec(raw="")), ("half a file", rec(raw='{"result": "a')),
                    ("a list", rec(raw="[1]")), ("no result key", rec(raw='{"type": "result"}')),
                    ("a null result", rec(None))):
        got = RW.render([r])
        check(st(r) == "could_not_look" and r["result"] in got and "COULD NOT LOOK (" in got and "EMPTY" not in got,
              "could-not-look-is-said: %s reads could not look, with its path" % what)
    r = rec(raw="", state="killed: success (killed TERM)", err="signal: terminated by x")
    check("terminated by x" in RW.render([r]), "could-not-look-is-said: the stderr text is there when no result is")
    check("its stderr: none (no file" in RW.render([rec(raw="")]) and "its stderr: empty" in RW.render([rec(raw="", err="")]),
          "could-not-look-is-said: no stderr file and an empty stderr are two answers")
    r = rec(raw="")
    os.makedirs(r["result"][:-len(".out.json")] + ".err")
    check("its stderr: COULD NOT LOOK" in RW.render([r]), "could-not-look-is-said: a stderr that cannot be read says so")
    check(st(dict(rec(), result=None)) == "could_not_look", "could-not-look-is-said: no recorded path")
    for r in (rec("boom", is_error=True), rec("boom", subtype="error_max_turns")):
        check(st(r) == "failed" and "FAILED" in RW.render([r]) and "boom" in RW.render([r]),
              "could-not-look-is-said: an error result reads failed and keeps its text")
    r = rec(None, is_error=True, subtype="error_during_execution")
    check(st(r) == "failed" and "error_during_execution" in RW.render([r]),
          "could-not-look-is-said: an error with no text names Claude's end")


def t_the_decisive_run_stands_first():
    plain = lambda: rec("plain words")  # noqa: E731
    for what, r in (("a failed state", rec("ddd", state="exit-code (exited 1)")),
                    ("a claude error", rec("ddd", state="success/claude-error (exited 0)")),
                    ("LEFT OPEN:", rec("ddd LEFT OPEN: x")), ("Left open: in bold", rec("ddd\n**Left open:** the rest")),
                    ("OWED", rec("ddd the visit is OWED.")),
                    ("an owed record", rec("ddd", owed="item is still doing")), ("an empty one", rec("")),
                    ("an unreadable one", rec(missing=True)), ("an error result", rec("ddd", is_error=True))):
        got = RW.render([plain(), r, plain()])
        check(got.index("----- " + r["unit"] + " ended") < got.index("plain words") and got.count("plain words") == 2,
              "the-decisive-run-stands-first: %s" % what)
    r = rec("ddd", owed="item X is still doing")
    check("OWED: item X is still doing" in RW.render([r]), "the-decisive-run-stands-first: the owed line is in the wake")
    got = RW.render([rec("we FOLLOWED it"), rec("OWED is this")])
    check(got.index("OWED is this") < got.index("FOLLOWED"), "the-decisive-run-stands-first: OWED is a word, not FOLLOWED")
    check(not re.search(r"routine|all good|no action|nothing to do", RW.render([plain(), rec("shall I ask him?")]), re.I),
          "the-decisive-run-stands-first: no heading calls a result routine")
    seen = []

    def waker(*a):
        seen.append(a)
        return None
    DH.wake_conductor("u", "success (exited 0)", "/o", "I", "BENCH", waker, "owed text")
    check(seen and seen[0][4] == "owed text", "the-decisive-run-stands-first: finish's owed line reaches post")
    RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 1, "window_pid": 4242})
    p = RW.post("u-owed", "success (exited 0)", "/o", "I", "owed text", root=STATE, alive=lambda pid: True)
    check(json.load(open(p))["owed"] == "owed text", "the-decisive-run-stands-first: the pending file holds it")
    os.remove(p)


def t_no_spend_field_is_carried():
    got = RW.render([rec(), rec("x", is_error=True), rec("", state="timeout (killed KILL)")])
    check(not re.search(r"12\.34|98\.76|7654321|4455667|55\.44|cost|cap_usd|token", got),
          "no-spend-field-is-carried: no cost, cap or token field of the result file reaches the wake")
    for fig in ("$15", "≈7,500,000 weighted tokens"):
        r = rec("Stopped by spend_watchdog at its cap (%s); the session is resumable (--resume abc-1)." % fig, is_error=True,
                subtype="error_max_budget_usd", stopped_by="spend_watchdog")
        got = RW.render([r])
        check(fig not in got and "Stopped by spend_watchdog at its cap; the session is resumable (--resume abc-1)." in got,
              "no-spend-field-is-carried: a cap stop keeps its words and loses its figure (%s)" % fig)


def t_a_block_line_carries_its_time():
    b = RW.state_block({"locks": lambda: "one\ntwo\n\n", "pipe": lambda: 1 / 0, "accounts": lambda: ""}, now=1795492604)
    rows = b.splitlines()[1:]
    check(len(rows) == 4 and all(re.match(r"\[\d+:\d\d:\d\d [AP]M PST\] (locks|pipe|accounts): ", x) for x in rows),
          "a-block-line-carries-its-time: each of %d lines, a failure and an empty answer too" % len(rows))
    b = RW.state_block({"locks": lambda: "x"})
    check(RW._pacific(time.time())[:-10] in b, "a-block-line-carries-its-time: with no given time it is the reading's")


def t_a_reader_never_holds_the_wake():
    def ends():
        raise SystemExit(3)

    def boom():
        raise OSError("store\nunreadable")
    t0 = time.time()
    b = RW.state_block({"slow": lambda: time.sleep(8), "ends": ends, "boom": boom, "none": lambda: None,
                        "empty": lambda: "", "nolist": lambda: [], "ok": lambda: "fine"}, deadline_s=1)
    line = lambda n: [x for x in b.splitlines() if "] %s: " % n in x]  # noqa: E731
    check(time.time() - t0 < 5, "a-reader-never-holds-the-wake: a hung reader ends at the deadline")
    for n, why in (("slow", "no answer in 1 s"), ("ends", "SystemExit"), ("boom", "store unreadable"),
                   ("none", "no reading")):
        check(len(line(n)) == 1 and "COULD NOT LOOK" in line(n)[0] and why in line(n)[0],
              "a-reader-never-holds-the-wake: %s reads could not look with its cause" % n)
    for n in ("empty", "nolist"):
        check(len(line(n)) == 1 and line(n)[0].endswith("none (looked)"), "a-reader-never-holds-the-wake: %s" % n)
    check(line("ok")[0].endswith("fine"), "a-reader-never-holds-the-wake: the others answer")
    check(RW.READER_S < RW.STATE_DEADLINE_S, "a-reader-never-holds-the-wake: a child dies before the block's deadline")
    try:
        RW._tool("src/RimMandrake/rimflow/game_lock.py", "query", "no-such-game")
        bad = "no exception"
    except RuntimeError as e:
        bad = str(e)
    check(bad.startswith("exit "), "a-reader-never-holds-the-wake: a tool's failed exit is a failure (%s)" % bad[:60])


def t_the_pipe_answer_stays_short():
    text = "\n".join(["control rev 1: ALL ON", "ArchBig: HELD by BENCH", "item:A_B OFF: why", "item:C_D OFF: why",
                      "family:old OFF: x", "item:E_F ON until 5 PM", "Pyrelands in_game ON tick: live",
                      "stop order kill on u: pending", "runs in flight: []"])
    got = RW.short_pipe(text, ["ArchBig", "ArchSmall"])
    check("A_B" not in got and "ArchBig" not in got and "1 family, 2 item (./pipe show" in got,
          "the-pipe-answer-stays-short: OFF switches are counted, with the command that lists them")
    check(all(x in got.splitlines() for x in text.splitlines() if x.startswith(("control", "Pyre", "stop", "runs", "item:E"))),
          "the-pipe-answer-stays-short: every other line is whole")
    check(RW.short_pipe("runs in flight: []") == "runs in flight: []", "the-pipe-answer-stays-short: none off, no count line")


def arm_and_post(r, me=99):
    RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": me, "window_pid": 4242})
    return RW.post(r["unit"], r["state"], r["result"], r["item"], root=STATE, alive=lambda pid: True)


def pending():
    d = os.path.join(RW.wake_dir(STATE), "pending")
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def wait(**kw):
    kw.setdefault("state", lambda: "== STATE block")
    kw.setdefault("sleep", lambda s: None)
    return RW.wait("S", 4242, root=STATE, me=99, alive=lambda pid: True, max_wait=kw.pop("max_wait", 5), **kw)


def t_the_window_reads_it_whole():
    body = "BEGIN " + "q" * 60000 + " END"
    arm_and_post(rec(body))
    code, text = wait()
    check(code == 2 and body in text and text.endswith("== STATE block"),
          "the-window-reads-it-whole: the wait gives the whole text with the block at its end")
    import seat_restart as SR
    real = (RW.doorbell.claude_ancestor, SR.session_file, RW.MAX_WAIT_S, RW.POLL_S, RW.default_readers, sys.stderr)
    try:
        RW.doorbell.claude_ancestor = lambda pid=None: os.getpid()
        SR.session_file = lambda pid: {"name": "CONDUCTOR", "entrypoint": "cli"}
        RW.MAX_WAIT_S, RW.POLL_S = 5, 0.05
        RW.default_readers = lambda: {"locks": lambda: "all free"}
        arm_and_post(rec(body))
        sys.stderr = io.StringIO()
        code = RW.hook_main(stdin=io.StringIO(json.dumps({"session_id": "S"})), env={"AGENT_SEAT": "BENCH"})
        err = sys.stderr.getvalue()
    finally:
        (RW.doorbell.claude_ancestor, SR.session_file, RW.MAX_WAIT_S, RW.POLL_S, RW.default_readers, sys.stderr) = real
    check(code == 2 and body in err and "locks: all free" in err, "the-window-reads-it-whole: the hook writes it on stderr")


def t_a_wake_is_never_lost():
    r = rec("kept")
    arm_and_post(r)
    seen = []
    code, text = wait(state=lambda: seen.append(pending()) or "== STATE")
    check(code == 2 and seen == [[r["unit"] + ".json"]], "a-wake-is-never-lost: the block is read before the consume")
    arm_and_post(rec("kept2"))
    code, text = wait(state=lambda: 1 / 0)
    check(code == 2 and "kept2" in text and "COULD NOT LOOK" in text, "a-wake-is-never-lost: a block that breaks is said")
    arm_and_post(rec("kept3"))
    held = []
    clock = iter(range(0, 100)).__next__
    code, text = wait(state=lambda: held.append(1) or "b", hold=lambda: bool(held), clock=lambda: clock(), max_wait=4)
    check(code == 0 and len(pending()) == 1, "a-wake-is-never-lost: a hold that begins while the block is read keeps it")
    RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 99, "window_pid": 4242})
    code, text = wait(state=lambda: RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 5, "window_pid": 4242}))
    check(code == 0 and "superseded" in text and len(pending()) == 1,
          "a-wake-is-never-lost: a waiter superseded while the block is read consumes nothing")
    RW.doorbell._write_json_atomic(RW.armed_path(STATE), {"pid": 99, "window_pid": 4242})
    dead = []
    code, text = RW.wait("S", 4242, root=STATE, me=99, alive=lambda pid: not dead, max_wait=5, sleep=lambda s: None,
                         state=lambda: dead.append(1) or "b")
    check(code == 0 and "gone" in text and len(pending()) == 1,
          "a-wake-is-never-lost: a window that ends while the block is read loses nothing")
    d = os.path.join(RW.wake_dir(STATE), "pending")
    for n in pending():
        os.remove(os.path.join(d, n))
    with open(os.path.join(d, "torn.json"), "w") as f:
        f.write("{")
    reads = []
    clock2 = iter(range(0, 100)).__next__
    code, text = wait(state=lambda: reads.append(1) or "b", clock=lambda: clock2(), max_wait=6)
    check(code == 0 and reads == [] and pending() == ["torn.json"],
          "a-wake-is-never-lost: an unreadable pending file stays and starts no reader")
    os.remove(os.path.join(d, "torn.json"))
    real = RW.report_of
    RW.report_of = lambda r: 1 / 0
    try:
        got = RW.render([r])
    finally:
        RW.report_of = real
    check(r["unit"] in got and r["result"] in got and "ZeroDivisionError" in got,
          "a-wake-is-never-lost: a record that breaks the renderer is named with its path and cause")


def main():
    t_the_whole_last_message()
    t_could_not_look_is_said()
    t_the_decisive_run_stands_first()
    t_no_spend_field_is_carried()
    t_a_block_line_carries_its_time()
    t_a_reader_never_holds_the_wake()
    t_the_pipe_answer_stays_short()
    t_the_window_reads_it_whole()
    t_a_wake_is_never_lost()
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
