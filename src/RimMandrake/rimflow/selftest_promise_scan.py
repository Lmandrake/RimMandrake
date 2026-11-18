#!/usr/bin/env python3
"""Regression checks for promise_scan.py and its two readers (RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL):
the per-prompt notice in .claude/hooks/conductor_goodbye.py and seat_restart.queue_untracked_promises at a backstop kill.
The contract itself is acceptance/owed_promise_scan_accept.py.

    python3 src/RimMandrake/rimflow/selftest_promise_scan.py      # exit 0 and "PASS n/n"
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import promise_scan as PS  # noqa: E402
import seat_restart as SR  # noqa: E402

RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


def tx(tmp, text):
    p = os.path.join(tmp, "tx.jsonl")
    with open(p, "w") as f:
        f.write(json.dumps({"type": "user", "message": {"content": "status?"}}) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}) + "\n")
    return p


def scanner():
    check(PS.scan("I’ll send it after lunch.") == ["I’ll send it after lunch."], "a curly apostrophe is a promise")
    check(PS.scan("Done.\n\n```\nI will run this\n```\n\nNothing else.") == [], "a code block is not the reply's words")
    check(PS.scan("- I will file it.\n- I filed the other.") == ["I will file it."], "bullets are sentences of their own")
    check(PS.scan("Is it done? Yes, it landed at 3 PM.") == [], "a question answered in the reply is not a closing ask")
    check(PS.scan("") == [] and PS.scan(None) == [], "an empty reply has no promise")
    check(PS.scan("I will write it. meanwhile, RIMMANDRAKE_OTHER_OWED waits.", ["RIMMANDRAKE_OTHER_OWED"])
          == ["I will write it."], "another sentence's owed id never tracks a promise")
    check(PS.scan("I will ask Dr. Smith to finish RIMMANDRAKE_OTHER_OWED.", ["RIMMANDRAKE_OTHER_OWED"]) == [],
          "an abbreviation's period does not end the sentence")
    check(PS.scan("I will check whether it is yes or no. RIMMANDRAKE_OTHER_OWED waits.", ["RIMMANDRAKE_OTHER_OWED"])
          == ["I will check whether it is yes or no."], "a sentence ending in 'no.' still ends there")
    check(PS.scan("Run:\n~~~\nI will run it.\n~~~\nDone.") == [], "a ~~~ fence is code")
    check(PS.scan("Ex:\n````\n```\nI will run it.\n```\n````\nDone.") == [], "a longer fence holds a shorter one")


def hook():
    tmp = tempfile.mkdtemp(prefix="promise_hook_")
    p = tx(tmp, "Published `abc1234`.\n\nWhen the slot frees I will launch the FlowWorks realignment.")
    data = json.dumps({"prompt": "how is it going", "session_id": "x", "transcript_path": p})
    env = dict(os.environ, AGENT_SEAT="BENCH")
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")], input=data,
                       cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
    check(r.returncode == 0 and "UNTRACKED in your last reply (1)" in r.stdout and "I will launch" in r.stdout,
          "the per-prompt notice names the last reply's untracked promise (rc %d)" % r.returncode)
    data = json.dumps({"prompt": "how is it going", "session_id": "x", "transcript_path": os.path.join(tmp, "none")})
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")], input=data,
                       cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
    check(r.returncode == 0 and "UNTRACKED" not in r.stdout, "no readable reply prints no promise line, exit 0")


def kill_queue():
    tmp = tempfile.mkdtemp(prefix="promise_kill_")
    state = os.path.join(tmp, "state")
    os.makedirs(state)
    p = tx(tmp, "The summary was never written. Should I write it now?")
    out = SR.queue_untracked_promises("BENCH", {"tx_path": p, "session_id": "s1"}, root=state)
    q = os.path.join(state, "untracked_promises.jsonl")
    lines = [json.loads(l) for l in open(q)] if os.path.exists(q) else []
    check(out.startswith("queued 2") and len(lines) == 2 and all(l["title"].startswith("UNTRACKED promise: ")
                                                                 for l in lines), "a backstop kill queues each promise")
    out = SR.queue_untracked_promises("BENCH", {"tx_path": os.path.join(tmp, "gone.jsonl")}, root=state)
    check(out.startswith("UNMEASURED"), "an unreadable transcript is UNMEASURED, never 'no promise' (%s)" % out[:40])
    out = SR.queue_untracked_promises("BENCH", {"tx_path": p}, root=os.path.join(tmp, "no", "such", "dir"))
    check(out.startswith("promise queue FAILED"), "a queue it cannot write says FAILED and never raises")


def kill_gate():
    sch = {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor"}, "FOUNDRY": {"kind": "doorbell"}}}}
    calls = []
    fx = {"promises": lambda seat, rs: calls.append(seat) or "queued 1"}
    for src, seat, want in (("backstop", "BENCH", 1), ("backstop_hard", "BENCH", 1), ("goodbye", "BENCH", 0),
                            ("handoff", "BENCH", 0), ("backstop", "FOUNDRY", 0)):
        calls.clear()
        rs = {"source": src}
        SR.promises_after_kill(seat, sch, rs, fx)
        check(len(calls) == want and (rs.get("promises") == "queued 1") == bool(want),
              "a %s kill of %s queues promises: %s" % (src, seat, bool(want)))
    calls.clear()
    SR.promises_after_kill("BENCH", sch, {"source": "backstop"}, {"kill": lambda *a: None})
    check(calls == [], "a test's fx without `promises` never runs the real queue")


def kill_through_execute():
    """The real kill path, SR.execute on a restart_kill, queues promises on a backstop and not on a goodbye: removing
    the call in _do_kill turns this red (Codex's second look)."""
    sch = {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor", "backstop": True}}}}
    for src, want in (("backstop", 1), ("goodbye", 0)):
        calls = []
        st = {"seat_restart": {"BENCH": {"state": "claimed", "source": src, "start": 77, "ts": 1.0, "tx_path": "/x"}}}
        a = {"do": "restart_kill", "seat": "BENCH", "pid": 4242, "session_id": "S", "session_name": "CONDUCTOR",
             "argv": ["claude"]}
        fx = {"session_file": lambda pid: {"sessionId": "S", "name": "CONDUCTOR", "status": "idle"},
              "recheck": lambda *x: [], "start": lambda pid: 77, "write_killed": lambda *x: None,
              "final": lambda *x: [], "kill": lambda pid, start=None: "SIGTERM, exited",
              "promises": lambda seat, rs: calls.append(seat) or "queued 1"}
        try:
            res = SR.execute(a, sch, st, True, 100.0, fx)
        except Exception as e:  # noqa: BLE001 - a fixture this test does not know: said in the check
            res = "raised %s: %s" % (type(e).__name__, e)
        check(len(calls) == want and str(res).startswith("killed"),
              "execute(restart_kill) from a %s kill queues promises: %s (%s)" % (src, bool(want), str(res)[:80]))


def downstream():
    """queue -> owed.py sync-sources (one a pass) files each once; a sentence citing an owed id (closed too) never."""
    tmp = tempfile.mkdtemp(prefix="promise_down_")
    state, items = os.path.join(tmp, "state"), os.path.join(tmp, "items")
    os.makedirs(os.path.join(state, "detached"))
    os.makedirs(items)
    env = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
               RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")
    done = "RIMMANDRAKE_CONFIRM_SANDBOX_DEBT_PAID_ALREADY"
    cli = [sys.executable, os.path.join(HERE, "cli.py")]
    subprocess.run(cli + ["file", done, "--for", "BENCH", "--kind", "owed", "--title", "t", "--why", "sandbox"],
                   cwd=REPO, env=env, capture_output=True, timeout=120)
    subprocess.run(cli + ["close", done, "--no-code", "told him at 3:00 PM PST", "--why", "sandbox"], cwd=REPO,
                   env=env, capture_output=True, timeout=120)
    long_act = "When the slot frees, " + "after the water pass and the census, " * 8 + "I will launch the realignment."
    p = tx(tmp, "The summary was never written.\n\nI will confirm `%s` with him.\n\n%s" % (done, long_act))
    SR.queue_untracked_promises("BENCH", {"tx_path": p, "session_id": "s1"}, root=state)
    mj = os.path.join(tmp, "m.json")
    open(mj, "w").write("[]")
    argv = [sys.executable, os.path.join(HERE, "owed.py"), "sync-sources", "--maturation-json", mj, "--detached-dir",
            os.path.join(state, "detached"), "--max-file", "1"]
    outs = [subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=300) for _ in range(3)]
    filed = [o.stdout.count("FILED ") for o in outs]
    check(filed == [1, 1, 0] and all(o.returncode == 0 for o in outs),
          "two untracked promises file one a pass, then nothing; the one citing a closed owed id never (%s)" % filed)
    ev = ""
    for f in os.listdir(os.path.join(tmp, "events")):
        ev += open(os.path.join(tmp, "events", f)).read()
    check("I will launch the realignment" in ev, "a long promise's act survives whole in its owed title")


def main():
    scanner()
    hook()
    kill_queue()
    kill_gate()
    kill_through_execute()
    downstream()
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
