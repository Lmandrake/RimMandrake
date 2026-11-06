#!/usr/bin/env python3
"""Selftest for hook_latency.py: the verdict arithmetic, and that the instrument can see what it claims to see.

Stub hooks in a throwaway repo prove: a slow hook shows in the wall reading; parallel and serial really differ; a
muted exit 2 allows and a raising hook fails open on both sides; a prototype that disagrees with the registered
command is caught by the replay; and the gate refuses a settings file that disagrees with the verdict.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_latency as H  # noqa: E402

fails = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


FACTS = {"heavy_share": 0.1, "median_step_s": 6.0, "bash_calls_per_day": 20000, "cores": 14}


def table(common_before, common_after, heavy_before=100.0, heavy_after=100.0, cpu_before=100.0, cpu_after=100.0):
    row = {"before_wall_ms": common_before, "after_wall_ms": common_after,
           "before_cpu_ms": cpu_before, "after_cpu_ms": cpu_after}
    heavy = dict(row, before_wall_ms=heavy_before, after_wall_ms=heavy_after)
    return {"bash_common": row, "bash_commit": heavy, "bash_push": heavy}


def test_verdict():
    v = H.verdict(table(120, 100), FACTS)
    check(v["verdict"] == "NOT_MATERIAL", "a 20 ms saving is not material")
    check(H.verdict(table(1000, 100, 1000, 100), FACTS)["verdict"] == "MATERIAL", "a 900 ms saving is material")
    v = H.verdict(table(400, 100, 400, 100), FACTS)
    check(v["verdict"] == "MATERIAL" and "step share" in v["reasons"][0], "300 of a 6000 ms step passes the share bar")
    v = H.verdict(table(100, 100, cpu_before=6000, cpu_after=100), FACTS)
    check(v["verdict"] == "MATERIAL" and "cpu share" in v["reasons"][0], "a machine-wide CPU saving passes the CPU bar")
    v = H.verdict(table(120, 100, 1300, 2300), FACTS)
    check(v["typical_saving_ms"] < 0, "serialising the heavy calls can make the typical call slower")


def stub_repo():
    d = tempfile.mkdtemp(prefix="hook_latency_selftest_")
    hooks = os.path.join(d, ".claude", "hooks")
    os.makedirs(hooks)
    stubs = {
        "slow_a": "import time,sys; sys.stdin.read(); time.sleep(0.25)\n",
        "slow_b": "import time,sys; sys.stdin.read(); time.sleep(0.25)\n",
        "deny_json": "import json,sys\nif 'NOPE' in sys.stdin.read():\n    print(json.dumps({'hookSpecificOutput':"
                     "{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':'no 12'}}))\n",
        "exit_two": "import sys\nif 'STOP' in sys.stdin.read():\n    sys.stderr.write('stopped'); sys.exit(2)\n",
        "raises": "raise RuntimeError('boom')\n",
        "two_faced": "import io,json,sys\nif 'FACE' in sys.stdin.read() and isinstance(sys.stdout, io.StringIO):\n"
                     "    print(json.dumps({'decision':'block','reason':'only in process'}))\n",
    }
    for name, body in stubs.items():
        with open(os.path.join(hooks, name + ".py"), "w") as f:
            f.write(body)
    return d


def write_settings(d, names, muted=()):
    def cmd(n):
        c = 'python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/%s.py"' % n
        return c + " 2>/dev/null || true" if n in muted else c
    path = os.path.join(d, "settings.json")
    with open(path, "w") as f:
        json.dump({"hooks": {"PreToolUse": [{"matcher": "Bash|Edit|Agent", "hooks": [
            {"type": "command", "command": cmd(n)} for n in names]}]}}, f)
    return path


def corpus(d, entries):
    path = os.path.join(d, "corpus.json")
    with open(path, "w") as f:
        json.dump({"entries": [{"tool": "Bash", "input": {"command": e}} for e in entries]}, f)
    return path


def test_instrument(d):
    s = write_settings(d, ["slow_a"])
    cmds = H.commands_for("Bash", s)
    pay = H.payload("Bash", {"command": "ls"}, d)
    wall = H.phase_parallel(cmds, pay, d)[0]
    check(wall >= 0.2, "a 250 ms hook reads at least 200 ms (read %.0f ms)" % (wall * 1000))
    s = write_settings(d, ["slow_a", "slow_b"])
    cmds = H.commands_for("Bash", s)
    par, ser = H.phase_parallel(cmds, pay, d)[0], H.phase_prototype(cmds, pay, d)[0]
    check(par < 0.45, "two 250 ms hooks run together read under 450 ms (read %.0f ms)" % (par * 1000))
    check(ser >= 0.45, "the same two in one process read at least 450 ms (read %.0f ms)" % (ser * 1000))


def test_outcomes(d):
    s = write_settings(d, ["deny_json", "exit_two", "raises"], muted=("exit_two",))
    cmds = H.commands_for("Bash", s)
    by = lambda res, n: next(v for c, v in res.items() if n in c)  # noqa: E731
    for label, fn in (("registered", H.phase_parallel), ("prototype", H.phase_prototype)):
        res = fn(cmds, H.payload("Bash", {"command": "STOP NOPE"}, d), d)[2]
        check(by(res, "deny_json")[0], label + ": a JSON deny refuses")
        check(not by(res, "exit_two")[0], label + ": a muted exit 2 allows, as `|| true` makes it")
        check(not by(res, "raises")[0], label + ": a raising hook fails open")
    s = write_settings(d, ["exit_two"])
    cmds = H.commands_for("Bash", s)
    for label, fn in (("registered", H.phase_parallel), ("prototype", H.phase_prototype)):
        res = fn(cmds, H.payload("Bash", {"command": "STOP"}, d), d)[2]
        check(by(res, "exit_two")[0], label + ": an unmuted exit 2 refuses")


def test_replay(d):
    s = write_settings(d, ["deny_json"])
    r = H.replay(corpus(d, ["ls", "NOPE"]), s, d)
    check(r["refused"] == 1 and r["allowed"] == 1 and not r["diffs"], "an honest replay sees both ways and no difference")
    s = write_settings(d, ["two_faced"])
    r = H.replay(corpus(d, ["ls", "FACE"]), s, d)
    check(len(r["diffs"]) == 1 and r["diffs"][0]["hook"] == "two_faced",
          "a hook that refuses only in-process is reported as a difference")


def test_gate(d):
    s = write_settings(d, ["deny_json"])
    entries = ["NOPE"] * 6 + ["ls"] * 20
    c = corpus(d, entries)
    facts = os.path.join(d, "facts.json")
    with open(facts, "w") as f:
        json.dump(FACTS, f)
    decision = os.path.join(d, "decision.md")
    with open(decision, "w") as f:
        f.write(H.FAILURE_HEADING + "\n")
    kw = dict(rounds=1, corpus=c, facts_path=facts, decision=decision, repo=d)
    check(H.gate(settings=s, **kw) == 1, "the gate refuses a corpus only one hook refuses in (floor of 3 hooks)")
    saved = H.replay
    H.replay = lambda *a, **k: {"entries": 26, "refused": 6, "allowed": 20, "refusing_hooks": ["a", "b", "c"], "diffs": []}
    try:
        check(H.gate(settings=s, **kw) == 0, "settings, verdict and record that agree pass")
        with open(decision, "w") as f:
            f.write("nothing here\n")
        check(H.gate(settings=s, **kw) == 1, "a record with no failure behaviour fails")
        with open(decision, "w") as f:
            f.write(H.FAILURE_HEADING + "\n")
        shutil.copy(os.path.join(d, ".claude", "hooks", "deny_json.py"),
                    os.path.join(d, ".claude", "hooks", "hook_dispatcher.py"))
        check(H.gate(settings=write_settings(d, ["hook_dispatcher"]), **kw) == 1,
              "a registered dispatcher with an immaterial cost fails")
        real = H.verdict
        H.verdict = lambda t, f: {"verdict": "MATERIAL", "reasons": ["forced"]}
        try:
            check(H.gate(settings=write_settings(d, ["deny_json"]), **kw) == 1, "a material cost with no dispatcher fails: the merge is owed")
        finally:
            H.verdict = real
    finally:
        H.replay = saved


def main():
    test_verdict()
    d = stub_repo()
    try:
        test_instrument(d)
        test_outcomes(d)
        test_replay(d)
        test_gate(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("selftest_hook_latency: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
