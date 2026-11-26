#!/usr/bin/env python3
"""The account plan's way to another machine: read which account it is on, write its notice, take its mark off, list
its live helper runs, order them to save, stop a run that does not end, carry on the runs that waited, and switch its
account (RIMMANDRAKE_AUTOMATE_STEVEDESKTOP_ACCOUNT_SWITCH_PLAN_SAYS_NEVER,
RIMMANDRAKE_SWITCH_STEVEDESKTOP_PAST_A_RUN_THAT_ONLY_WAITS).

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
    """-> (the units of the helper runs that the machine behind `alias` lists as running, None) or (None, why). A line
    whose second field is `running` counts, whatever systemd says, so a doubt keeps the machine from a switch."""
    try:
        r = subprocess.run(SSH + [alias, RUNS_CMD], capture_output=True, text=True, timeout=ACCOUNT_DEADLINE_S)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    if r.returncode != 0:
        return None, fulltext.fit((r.stderr or r.stdout).strip(), 200, tail=True) or "exit %d" % r.returncode
    return [ln.split()[0] for ln in r.stdout.splitlines() if len(ln.split()) > 1 and ln.split()[1] == "running"], None


# The acts on that machine's own control store and run records, run there by its own code (~/rm/bench) with functions
# that every clone since 2026-11-24 holds: the same orders, stops and carry-on as on this machine, never a second kind.
REMOTE_PY = "cd ~/rm/bench && PATH=$HOME/.local/bin:$PATH python3 - %s"
REMOTE_STEP = r"""
import json, sys
sys.path[:0] = ["src/RimMandrake/rimflow", "src/RimMandrake/Utils"]
a = json.loads(sys.argv[1])
out = {}
if a["do"] == "order":          # account_end's save order at the line: no void, no kill (control.order_runs)
    import account_end as AE, control as C
    units = sorted(set(AE.Orders().store_runs()) | set(a.get("units") or []))
    out = {"ok": True, "units": units, "act": C.order_runs(units, "at_easy_spot", a["text"])["id"] if units else None}
elif a["do"] == "stop":         # pipe stop UNIT --write-now: the trial voided, the order, the kill at its deadline
    import control as C
    rows = []
    for u in a["units"]:
        r = C.stop(u, "write_now", a["why"], per_ruling=a.get("per_ruling"))
        rows += [{"unit": x.get("unit"), "ok": x.get("ok", True), "said": x.get("said")} for x in r.get("units", [])]
    out = {"ok": bool(rows) and all(x["ok"] for x in rows), "units": rows}
elif a["do"] == "probe":        # read only: the code there holds each function that the acts above call
    import account_end as AE, control as C, left_open_continue as LOC
    has = {k: callable(getattr(mod, f, None)) for k, mod, f in (("order_runs", C, "order_runs"), ("stop", C, "stop"),
           ("kick_waiting", LOC, "kick_waiting"), ("store_runs", AE.Orders, "store_runs"))}
    out = {"ok": all(has.values()), "has": has, "echo": a.get("echo")}
elif a["do"] == "kick":         # the continuations that waited for the switch (left_open_continue.kick_waiting)
    import left_open_continue as LOC
    out = {"ok": True, "said": LOC.kick_waiting(plan_dir=a["plan_dir"])}
print("REMOTE_STEP " + json.dumps(out))
"""


def remote_step(alias, args, timeout):
    """One act of REMOTE_STEP on the machine behind `alias`. -> (ok, its answer dict or the cause as text). Its answer
    is the one line that starts REMOTE_STEP: a run that printed none did not answer (could not look)."""
    try:
        r = subprocess.run(SSH + [alias, REMOTE_PY % shlex.quote(json.dumps(args))], input=REMOTE_STEP,
                           capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return False, "%s: %s" % (type(e).__name__, e)
    got = [ln[len("REMOTE_STEP "):] for ln in r.stdout.splitlines() if ln.startswith("REMOTE_STEP ")]
    if r.returncode != 0 or not got:
        return False, fulltext.fit((r.stderr or r.stdout).strip(), 300, tail=True) or "exit %d, no answer" % r.returncode
    try:
        ans = json.loads(got[-1])
    except ValueError as e:
        return False, "its answer is no JSON (%s)" % e
    return bool(ans.get("ok")), ans


def probe_machine(alias, echo=""):
    """Read only: does the machine behind `alias` hold the functions of REMOTE_STEP, and does `echo` come back whole?"""
    return remote_step(alias, {"do": "probe", "echo": echo}, SSH_DEADLINE_S)


def order_machine(alias, units, text):
    """The save order at the line to each live run of the machine behind `alias` (its store's runs and `units`)."""
    ok, ans = remote_step(alias, {"do": "order", "units": list(units or []), "text": text}, SSH_DEADLINE_S)
    return ok, (("act %s to %s" % (ans.get("act"), ", ".join(ans.get("units") or []) or "no run")) if ok else
                ans if isinstance(ans, str) else json.dumps(ans))


def stop_machine_runs(alias, units, why, per_ruling=None):
    """`pipe stop U --write-now` on the machine behind `alias`, for each of `units`: its trial voided, the order said
    by its hook, the kill at that machine's own write-now deadline (control.WRITE_NOW_DEADLINE_S); a run that saved a
    LEFT OPEN note is carried on (control.carry_stop)."""
    ok, ans = remote_step(alias, {"do": "stop", "units": list(units or []), "why": why, "per_ruling": per_ruling},
                          SSH_DEADLINE_S)
    if isinstance(ans, str):
        return False, ans
    return ok, "; ".join("%s: %s" % (x.get("unit"), x.get("said")) for x in ans.get("units") or []) or "no unit"


def kick_machine(alias):
    """left_open_continue.kick_waiting on the machine behind `alias`, which reads its own notice for headroom."""
    ok, ans = remote_step(alias, {"do": "kick", "plan_dir": REMOTE_DIR}, SSH_DEADLINE_S)
    return ok, (ans.get("said") if isinstance(ans, dict) else ans)


def switch_machine(alias, name, account):
    """Switch the machine behind `alias` (machine name `name`) to `account`: the switcher's own non-interactive verb,
    which closes every Claude window there and relaunches its Fleet. -> (ok, its words)."""
    cmd = "PATH=$HOME/.local/bin:$PATH claude-account use %s --confirm %s" % (shlex.quote(account), shlex.quote(name))
    try:
        r = subprocess.run(SSH + [alias, cmd], capture_output=True, text=True, timeout=1800)  # budget: class=call
    except (OSError, subprocess.SubprocessError) as e:
        return False, "%s: %s" % (type(e).__name__, e)
    return r.returncode == 0, (fulltext.fit((r.stdout + r.stderr).strip(), 300, tail=True) or "exit %d" % r.returncode)
