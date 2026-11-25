#!/usr/bin/env python3
"""Selftest for filing_refusal_before_stop.py, the filing gate's Stop hook (item
RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW; page design/specs/2026-11-24-filing-gate/boundary.md).
Each case runs the hook as Claude Code runs it (a subprocess, "{}" on stdin) on a scratch state folder and a scratch
block counter, never the real state. It also reads the hook's registration in .claude/settings.json."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).with_name("filing_refusal_before_stop.py")
REPO = HOOK.parents[2]
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "rimflow"))
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils"))
import filing_gate as FG  # noqa: E402
import time_budget  # noqa: E402

fails = 0
cases = 0


def check(ok, what, got=None):
    global fails, cases
    cases += 1
    fails += 0 if ok else 1
    print(("ok    " if ok else "FAIL  ") + what + ("" if ok or got is None else "  got: %r" % (got,)))


def hook(env):
    full = {k: v for k, v in os.environ.items() if not k.startswith(("RM_ROLE_UNIT", "RM_STOP_BLOCKS",
                                                                      "RM_DISPATCHER_STATE"))}
    full.update(env)
    p = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True, env=full,
                       timeout=time_budget.CALL_S)
    try:
        out = json.loads(p.stdout) if p.stdout.strip() else {}
    except ValueError:
        out = {"unparsed": p.stdout}
    return p.returncode, out, p.stderr


def refuse(state, unit, iid, title="some work left here"):
    return FG.at_door("file", iid, title, "bug", unit=unit, owner=False, program="", not_now=None, did_it=None,
                      not_worth_it=None, state_dir=state, facts_fn=lambda: ([], lambda m: False),
                      look_sha=lambda sha: {"looked": False, "why": "test"})


with tempfile.TemporaryDirectory() as tmp:
    state, blocks = os.path.join(tmp, "state"), os.path.join(tmp, "blocks")
    unit = "rm-detached-bench-hooktest-1"
    env = {"RM_ROLE_UNIT": unit, "RM_DISPATCHER_STATE": state, "RM_STOP_BLOCKS_DIR": blocks}

    # 1. no unit: a window. Silent, exit 0, whatever the state holds.
    refuse(state, unit, "RIMMANDRAKE_HOOK_TEST_ONE_LEFT")
    rc, out, err = hook({"RM_DISPATCHER_STATE": state, "RM_STOP_BLOCKS_DIR": blocks})
    check(rc == 0 and out == {} and not err.strip(), "no RM_ROLE_UNIT: silent, exit 0", (rc, out, err))

    # 2. a unit with no record: silent
    rc, out, err = hook(dict(env, RM_ROLE_UNIT="rm-detached-bench-hooktest-none"))
    check(rc == 0 and out == {}, "a unit with no refusal: silent, exit 0", (rc, out, err))

    # 3. a refusal not resolved: block JSON on stdout, exit 0, the id, the title and the three ways
    rc, out, err = hook(env)
    reason = out.get("reason", "")
    check(rc == 0 and out.get("decision") == "block", "a refusal not resolved: block, exit 0", (rc, out, err))
    check("RIMMANDRAKE_HOOK_TEST_ONE_LEFT: some work left here" in reason, "the block names the id and the title", reason)
    check(all(w in reason for w in ("--did-it", "--not-now", "--not-worth-it")), "the block names the three ways", reason)

    # 4. a second block, then the run may end (MAX_BLOCKS = 2), and stderr says so
    rc, out, err = hook(env)
    check(rc == 0 and out.get("decision") == "block" and "stop 2 of 2" in out.get("reason", ""), "the second stop: block 2 of 2",
          (rc, out))
    rc, out, err = hook(env)
    check(rc == 0 and out == {} and "letting the run end" in err, "the third stop: the run ends, stderr says so", (rc, out, err))

    # 5. resolved (did): silent, with a fresh counter
    unit2 = "rm-detached-bench-hooktest-2"
    env2 = dict(env, RM_ROLE_UNIT=unit2)
    refuse(state, unit2, "RIMMANDRAKE_HOOK_TEST_TWO_LEFT")
    rc, out, _ = hook(env2)
    check(out.get("decision") == "block", "unit 2 is blocked first", out)
    FG.at_door("file", "RIMMANDRAKE_HOOK_TEST_TWO_LEFT", "t", "bug", unit=unit2, owner=False, program="",
               not_now=None, did_it=None, not_worth_it="a cosmetic typo in a log line nobody reads", state_dir=state,
               facts_fn=lambda: ([], lambda m: False), look_sha=lambda sha: {"looked": False, "why": "test"})
    rc, out, err = hook(env2)
    check(rc == 0 and out == {}, "resolved: silent, exit 0", (rc, out, err))

    # 6. a record that cannot be read: no block, "could not look" on stderr
    unit3 = "rm-detached-bench-hooktest-3"
    with open(FG.refusals_path(unit3, state), "w", encoding="utf-8") as f:
        f.write("{not json\n")
    rc, out, err = hook(dict(env, RM_ROLE_UNIT=unit3))
    check(rc == 0 and out == {} and "could not look" in err, "an unreadable record: no block, could not look", (rc, out, err))

    # 7. a block counter that cannot be written: no block (an unbounded loop is worse), stderr says so
    unit4 = "rm-detached-bench-hooktest-4"
    refuse(state, unit4, "RIMMANDRAKE_HOOK_TEST_FOUR_LEFT")
    not_a_dir = os.path.join(tmp, "a_file")
    open(not_a_dir, "w").close()
    rc, out, err = hook(dict(env, RM_ROLE_UNIT=unit4, RM_STOP_BLOCKS_DIR=not_a_dir))
    check(rc == 0 and out == {} and "did not run" in err, "no counter: no block, stderr says so", (rc, out, err))

# 8. registered as a Stop hook in the project settings, before run_end_wake, with no "|| true"
settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
cmds = [h.get("command", "") for g in settings.get("hooks", {}).get("Stop", []) for h in g.get("hooks", [])]
mine = [i for i, c in enumerate(cmds) if "filing_refusal_before_stop.py" in c]
wake = [i for i, c in enumerate(cmds) if "run_end_wake" in c]
check(len(mine) == 1, "registered once as a Stop hook", cmds)
check(mine and wake and mine[0] < wake[0], "before run_end_wake", (mine, wake))
check(mine and "|| true" not in cmds[mine[0]], "no '|| true' (the hook exits 0 itself)", cmds[mine[0]] if mine else None)

print("%d of %d cases failed" % (fails, cases) if fails else "ALL PASS (%d cases)" % cases)
sys.exit(1 if fails else 0)
