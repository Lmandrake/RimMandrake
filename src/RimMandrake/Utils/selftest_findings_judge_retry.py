#!/usr/bin/env python3
"""ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS, the findings judge half: an account death retries ONCE after the reset
(findings_judge_retry.decide), and findings_judge.sh schedules exactly that one retry. The script runs for real in a
temp tree whose claude_bounded.sh, sync, pulse.py and systemd-run are fakes; nothing touches systemd or the clone."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import findings_judge_retry as FR  # noqa: E402

FAILS = []
NOW = 1_793_808_000.0     # 2026-11-04T14:40Z, inside the measured outage
OUTAGE = {"type": "result", "subtype": "success", "is_error": True, "terminal_reason": "api_error",
          "api_error_status": 429, "api_error": "usage_limit_reached", "total_cost_usd": 0,
          "result": "You've hit your weekly limit · resets 12pm (America/Los_Angeles)"}
GOOD = {"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 1.2,
        "result": "work\nJUDGED 4 findings"}


def check(name, ok):
    if not ok:
        FAILS.append(name)
    print(("ok   " if ok else "FAIL ") + name)


def test_decide():
    verdict = FR.decide(OUTAGE, NOW)
    reset = FR.RL.limit_reset_at(OUTAGE["result"], NOW)
    check("the outage result retries at its reset", verdict[0] == "RETRY" and reset is not None
          and verdict[1] == int(reset + FR.RETRY_MARGIN_S - NOW) and verdict[2] == "usage_limit_reached")
    check("12pm Los Angeles is 20:00Z that day", reset == 1_793_822_400.0)
    check("no reset named: RESUME_WAIT_S", FR.decide({"is_error": True, "api_error_status": 429}, NOW)
          == ("RETRY", FR.RL.RESUME_WAIT_S, "429"))
    check("a good run does not retry", FR.decide(GOOD, NOW)[0] == "NO")
    check("an auth death does not retry", FR.decide({"is_error": True, "terminal_reason": "api_error",
                                                     "result": "Failed to authenticate: OAuth session expired"}, NOW)[0] == "NO")


def tree(d, result, rc):
    u = os.path.join(d, "src", "RimMandrake", "Utils")
    os.makedirs(os.path.join(u, "pulse"))
    for f in ("findings_judge.sh", "findings_judge_retry.py", "findings_judge_prompt.md", "findings_judge_friday.md"):
        shutil.copy(os.path.join(HERE, f), u)
    for pkg in ("rimflow", "contracts"):     # role_launch (the classifier) and what it imports
        os.symlink(os.path.join(HERE, "..", pkg), os.path.join(d, "src", "RimMandrake", pkg))
    fake = {os.path.join(u, "claude_bounded.sh"): "#!/bin/sh\ncat <<'J'\n%s\nJ\nexit %d\n" % (json.dumps(result), rc),
            os.path.join(d, "sync"): "#!/bin/sh\nexit 0\n",
            os.path.join(d, "systemd-run"): "#!/bin/sh\necho \"$@\" >> \"%s/calls\"\n" % d}
    for p, body in fake.items():
        with open(p, "w") as f:
            f.write(body)
        os.chmod(p, 0o755)
    with open(os.path.join(u, "pulse", "pulse.py"), "w") as f:
        f.write("import sys\nopen(%r, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n" % os.path.join(d, "pulse"))


def run(result, rc, retry=False):
    d = tempfile.mkdtemp(prefix="fjr_")
    tree(d, result, rc)
    out = os.path.join(d, "out")
    env = dict(os.environ, FINDINGS_JUDGE_OUT=out, FINDINGS_JUDGE_SYSTEMD_RUN=os.path.join(d, "systemd-run"))
    env.pop("FINDINGS_JUDGE_RETRY", None)
    if retry:
        env["FINDINGS_JUDGE_RETRY"] = "1"
    p = subprocess.run(["bash", os.path.join(d, "src", "RimMandrake", "Utils", "findings_judge.sh")], env=env,
                       capture_output=True, text=True, timeout=120)
    calls = open(os.path.join(d, "calls")).read().splitlines() if os.path.exists(os.path.join(d, "calls")) else []
    retries = open(os.path.join(out, "retries.jsonl")).read().splitlines() \
        if os.path.exists(os.path.join(out, "retries.jsonl")) else []
    pulse = open(os.path.join(d, "pulse")).read() if os.path.exists(os.path.join(d, "pulse")) else ""
    last = json.load(open(os.path.join(out, "last.json")))
    shutil.rmtree(d)
    return p.returncode, calls, retries, pulse, last


def test_script():
    rc, calls, retries, pulse, last = run(OUTAGE, 1)
    check("an account death schedules exactly one retry", len(calls) == 1 and len(retries) == 1)
    c = calls[0] if calls else ""
    check("the retry is a user timer running the same script, marked as the retry",
          "--user" in c and "--on-active=" in c and "FINDINGS_JUDGE_RETRY=1" in c and c.endswith("findings_judge.sh"))
    check("one fixed unit name, so systemd refuses a second pending retry", "--unit rm-findings-judge-retry " in c)
    check("the elapsed timer unloads, so the next outage's retry is not refused", "RemainAfterElapse=no" in c)
    check("its wait is the decided one", calls and int(c.split("--on-active=")[1].split("s")[0]) > 60)
    check("the run still reads failed, the retry said", rc == 1 and not last["ok"] and "one retry" in pulse
          and "failed" in pulse)
    rc, calls, retries, _, _ = run(OUTAGE, 1, retry=True)
    check("the retry itself schedules none (one retry only)", rc == 1 and not calls and not retries)
    rc, calls, _, _, last = run(GOOD, 0)
    check("a good run schedules none", rc == 0 and not calls and last["ok"])
    rc, calls, _, _, _ = run({"is_error": True, "result": "some other failure"}, 1)
    check("a non-account failure schedules none", rc == 1 and not calls)


def main():
    test_decide()
    test_script()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
