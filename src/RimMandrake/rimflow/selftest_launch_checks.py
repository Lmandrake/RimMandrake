#!/usr/bin/env python3
"""selftest_launch_checks.py: GATE_FIRST's checker (launch_checks.py) and its filers' blocks, offline in a temp dir.

  parse     only the `## launch-checks` section is read; a must-pass in prose or in another section is not a check
  run       must-pass 0 / must-fail non-zero pass; the other way refuses with evidence, would_pass, smallest_fix;
            exit 126/127, a timeout, an unknown line: did not run, never a refusal; a fake runner gets the contract's call
  block     block_for("advance") names maturation.py gate; ops_watch.red_launch_checks writes must-fail: <the rerun>
            for a red group and nothing for an alarm without tests
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import launch_checks as LC  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    text = "## spec\nmust-pass: false\n\n## launch-checks\nmust-pass: true\n\nmust-fail: false\n### sub\n## verify\nmust-pass: false\n"
    ck = LC.parse(text)
    check([c["kind"] for c in ck] == ["must-pass", "must-fail", "unknown"], "parse: the block's lines only (%s)" % ck)
    with tempfile.TemporaryDirectory() as tmp:
        r = LC.run(LC.parse("## launch-checks\nmust-pass: true\nmust-fail: false\n"), tmp, timeout_s=5)
        check(r["ok"] and not r["refusals"] and not r["did_not_run"], "run: good checks pass")
        r = LC.run(LC.parse("## launch-checks\nmust-pass: echo gate shut; false\nmust-fail: echo green; true\n"), tmp,
                   timeout_s=5)
        check(not r["ok"] and len(r["refusals"]) == 2 and "gate shut" in r["refusals"][0]["evidence"]
              and "already passes" in r["refusals"][1]["evidence"]
              and all(x[k] for x in r["refusals"] for k in ("check", "kind", "evidence", "would_pass", "smallest_fix")),
              "run: both wrong ways refuse, each with its path to pass")
        r = LC.run(LC.parse("## launch-checks\nmust-fail: sh -c 'exit 126'\nmust-pass: sleep 5\nwhat: x\n"), tmp, timeout_s=1)
        check(r["ok"] and len(r["did_not_run"]) == 3 and not r["refusals"], "run: 126, a timeout, an unknown line: did not run")
    seen = []

    def fake(cmd, **kw):
        seen.append((cmd, kw))
        raise OSError("no shell")
    r = LC.run(LC.parse("## launch-checks\nmust-pass: x\n"), "/c", timeout_s=7, runner=fake)
    check(seen == [("x", {"shell": True, "cwd": "/c", "capture_output": True, "text": True, "timeout": 7})]
          and r["ok"] and len(r["did_not_run"]) == 1, "run: the runner gets the contract's call; an OSError did not run")
    check(LC.block_for("advance", mod="M", to="preflight").endswith("maturation.py gate M --to preflight\n"),
          "block: advance names the gate verb")
    import ops_watch
    b = ops_watch.red_launch_checks({"x": {"tests": ["src/RimMandrake/rimflow/selftest_x.py"]}})
    check(b == "## launch-checks\nmust-fail: python3 src/RimMandrake/Utils/run_selftests.py --only "
              "src/RimMandrake/rimflow/selftest_x.py\n" and ops_watch.red_launch_checks({"x": {}}) is None,
          "block: a red group's fixer gets must-fail on its rerun; an alarm without tests gets none")
    r = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "gate", "--help"], capture_output=True,
                       text=True, timeout=60)
    check(r.returncode == 0 and "--to" in r.stdout, "block: the gate verb the advance line names exists")
    print("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
