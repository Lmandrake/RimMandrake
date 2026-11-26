#!/usr/bin/env python3
"""The account plan's way to another machine: read which account it is on, write its notice, take its mark off, count
its live helper runs, and switch its account (RIMMANDRAKE_AUTOMATE_STEVEDESKTOP_ACCOUNT_SWITCH_PLAN_SAYS_NEVER).

Page: design/specs/2026-11-24-account-plan-one-file/boundary.md (the promises of the machines). account_plan.py decides
(machine_notice, push_machines) and starts no process; this file is the ssh transport, and decides nothing. A machine
that got a notice from here is a following machine: its launch gate (account_plan.launch_gate) reads that notice, and
refuses new runs with COULD NOT LOOK when the notice is missing or older than account_plan.NOTICE_FRESH_S.
"""
import json
import shlex
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rimflow"))
import fulltext  # noqa: E402

REMOTE_DIR = "/mnt/d/ClaudeWork/rimmandrake/switching_plan"     # switching_plan.LIVE_OUT on each machine
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
# budget: danger=an ssh that hangs holds the timed pass, and the next pass waits on its lock; evidence=a push that is
# budget: cut is could not look (that machine's notice ages and its own gate refuses new runs); longest=0.6s (three
# budget: pushes to stevedesktop-wsl, measured 2026-11-24)
SSH_DEADLINE_S = 120
# budget: danger=the same hang, on the read of that machine's account; evidence=a read that is cut is could not look,
# budget: and that machine then gets a notice that refuses new runs; longest=16.8s (four reads of the switcher's status
# budget: on stevedesktop-wsl over ssh took 4.0, 4.4, 6.7 and 16.8 s, measured 2026-11-24 with 8 Claude processes there)
ACCOUNT_DEADLINE_S = 180

def machine_account(alias):
    """-> (the live account of the machine behind `alias`, None) or (None, why)."""
    import account_live as AL
    ans = AL.read(target=alias, timeout=ACCOUNT_DEADLINE_S)
    return AL.name_of(ans), AL.why_of(ans)


def send_notice(alias, n):
    """Write n as the notice of the machine behind `alias`, and the mark that it follows this one. -> (ok, why)."""
    mark = json.dumps({"of": n.get("follows"), "at": n.get("at")})
    cmd = ("mkdir -p {d} && cat > {d}/notice.json.new && mv {d}/notice.json.new {d}/notice.json && "
           "printf %s {m} > {d}/follows.json").format(d=REMOTE_DIR, m=shlex.quote(mark))
    try:
        r = subprocess.run(SSH + [alias, cmd], input=json.dumps(n), capture_output=True, text=True, timeout=SSH_DEADLINE_S)
    except (OSError, subprocess.SubprocessError) as e:
        return False, "%s: %s" % (type(e).__name__, e)
    return r.returncode == 0, (r.stderr or r.stdout).strip() or "exit %d" % r.returncode


def forget_machine(alias):
    """Take the follower mark and the notice off the machine behind `alias`: it is no machine of the plan any more."""
    try:
        r = subprocess.run(SSH + [alias, "rm -f %s/follows.json %s/notice.json" % (REMOTE_DIR, REMOTE_DIR)],
                           capture_output=True, text=True, timeout=SSH_DEADLINE_S)
    except (OSError, subprocess.SubprocessError) as e:
        return False, "%s: %s" % (type(e).__name__, e)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


RUNS_CMD = "cd ~/rm/bench && PATH=$HOME/.local/bin:$PATH python3 src/RimMandrake/rimflow/detached_helper.py status"


def machine_runs(alias):
    """-> (the number of helper runs the machine behind `alias` lists as running, None) or (None, why). A line whose
    second field is `running` counts, whatever systemd says, so a doubt keeps the machine from a switch."""
    try:
        r = subprocess.run(SSH + [alias, RUNS_CMD], capture_output=True, text=True, timeout=ACCOUNT_DEADLINE_S)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    if r.returncode != 0:
        return None, fulltext.fit((r.stderr or r.stdout).strip(), 200, tail=True) or "exit %d" % r.returncode
    return sum(1 for ln in r.stdout.splitlines() if len(ln.split()) > 1 and ln.split()[1] == "running"), None


def switch_machine(alias, name, account):
    """Switch the machine behind `alias` (machine name `name`) to `account`: the switcher's own non-interactive verb,
    which closes every Claude window there and relaunches its Fleet. -> (ok, its words)."""
    cmd = "PATH=$HOME/.local/bin:$PATH claude-account use %s --confirm %s" % (shlex.quote(account), shlex.quote(name))
    try:
        r = subprocess.run(SSH + [alias, cmd], capture_output=True, text=True, timeout=1800)  # budget: class=call
    except (OSError, subprocess.SubprocessError) as e:
        return False, "%s: %s" % (type(e).__name__, e)
    return r.returncode == 0, (fulltext.fit((r.stdout + r.stderr).strip(), 300, tail=True) or "exit %d" % r.returncode)
