#!/usr/bin/env python3
"""spend_watchdog.py — the hard per-run spend stop, enforced from OUTSIDE the agent.

    spend_watchdog.py --cap-usd X [--poll-s 30] [--grace-s 30] [--projects DIR] -- <claude argv...>

Why: `claude --max-budget-usd` makes the harness inject `USD budget: $used/$cap; $left remaining` into the agent on
EVERY turn (attachment type `budget_usd`; 143 in one 11-16 builder run). The owner, 2026-11-16: "I don't like how
you're telling the agent how much it's spent. This has been shown to reduce their creativity and obsess on cost
savings..." · "You're telling it constantly". Claude 2.1.311 has no switch that keeps the cap and drops the reminder
(the attachment fires whenever maxBudgetUsd is set; CLAUDE_CODE_DISABLE_ATTACHMENTS drops every attachment, hooks and
file edits included), so the flag is gone and this wrapper keeps the stop (owner 2026-11-12: "Don't let any burn go
to 90M this time ok?"). Item RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN.

How: it pins the session (`--session-id <uuid4>` unless the argv resumes one), runs claude as a child with stdout
captured, and every poll reads the session's transcripts (role_launch.transcript_usage: the session and its
subagents; a resume counts only turns from its launch on) into weighted_v2 tokens (role_launch.run_tokens, each
message at its own model's list prices) and those into ≈ list dollars (USD_PER_M). At the cap it stops the child's process group (TERM, KILL after grace) and writes the
result claude itself writes at --max-budget-usd: subtype `error_max_budget_usd`, is_error, session_id, usage, with
`stopped_by: spend_watchdog` and the estimate, so every reader of that result (finish, maturation_now, the Dispatcher)
handles it as before and the session stays resumable. An unreadable, empty or malformed transcript measures nothing and
never stops a run. Under cap, the child's stdout is passed through whole and its exit code returned. It spends no
tokens.

USD_PER_M: list USD per million weighted_v2 tokens, one rate for every model, because weighted_v2 is already list
price / the reference input price (role_launch.MODEL_PRICES; RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT). It
replaced per-model ≈rates over weighted_v1 measured 2026-11-16 from 580 transcripts (opus 5.5 median 2.94 $/M v1;
x the Opus v1->v2 median 0.713 that is 4.12, against 4.00 here). A transcript message of a model not in the table
stops the run, naming the model: it is weighed as no other model, and an unmeasured run is never left uncapped.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

USD_PER_M = RL.MODEL_PRICES[RL.REF_MODEL]["input_tokens"]   # list $/MTok of the reference input: 1 v2 token's price
POLL_S = 30
# budget: danger=a run that ignores SIGTERM goes on spending past its stop (the per-run spend stop he ordered); SIGKILL follows;
# budget: its reach leaves no record; no record of its run
GRACE_S = 30


def rate(model=None):
    """-> list USD per million weighted_v2 tokens: the same for every model (the weights already carry its prices)."""
    return float(USD_PER_M)


def wrap(argv, cap_usd, python=None):
    """-> argv run under the watchdog with its cap. Every capped launcher calls this instead of --max-budget-usd."""
    return [python or sys.executable, os.path.join(HERE, "spend_watchdog.py"), "--cap-usd", "%g" % float(cap_usd),
            "--"] + list(argv)


def wrap_shell(cmd, cap_usd, python="python3"):
    """-> a shell command string run under the watchdog (for a launcher that builds a `sh -c` line)."""
    import shlex
    return "%s %s --cap-usd %s -- %s" % (python, shlex.quote(os.path.join(HERE, "spend_watchdog.py")),
                                         shlex.quote("%g" % float(cap_usd)), cmd)


def _opt(argv, name):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def pin_session(argv):
    """-> (argv, session id, resumed). A resume (`--resume ID`, which reuses the id) is watched as that id; otherwise
    an existing `--session-id` is kept, or a fresh uuid4 is added."""
    argv = list(argv)
    for flag in ("--resume", "-r"):
        sid = _opt(argv, flag)
        if sid and not sid.startswith("-"):
            return argv, sid, True
    sid = _opt(argv, "--session-id")
    if sid:
        return argv, sid, False
    sid = str(uuid.uuid4())
    at = argv.index("--") if "--" in argv else len(argv)
    return argv[:at] + ["--session-id", sid] + argv[at:], sid, False


def measure(sid, since=None, projects=RL.PROJECTS):
    """-> (weighted_v2 tokens, usage) of the session since `since` (epoch; None = all of it), or (None, None). Raises
    role_launch.UnknownModel when a message's model is not in MODEL_PRICES."""
    try:
        u = RL.transcript_usage({"session": sid, "at": since, "resume_of": "watchdog" if since else None}, projects)
    except Exception:  # noqa: BLE001 - an unreadable transcript measures nothing; it never stops a run
        return None, None
    tok = RL.run_tokens(RL.transcript_result(u)) if u else None
    return tok, (u if tok is not None else None)


def over_cap(sid, cap_usd, model, projects=RL.PROJECTS, since=None):
    """-> (over: bool, ≈ list usd or None, weighted tokens or None, usage or None). A model not in the table is over
    (the stop names it in usage["unknown_model"]): never a fallback weight, never an uncapped run."""
    try:
        tok, u = measure(sid, since, projects)
    except RL.UnknownModel as e:
        return True, None, None, {"unknown_model": str(e)}
    if tok is None:
        return False, None, None, None
    usd = tok * rate(model) / 1e6
    return usd >= cap_usd, usd, tok, u


def _stop(proc, grace_s):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except (ProcessLookupError, PermissionError):
            return
        try:
            proc.wait(timeout=grace_s)
            return
        except subprocess.TimeoutExpired:
            continue


def run(argv, cap_usd, poll_s=POLL_S, grace_s=GRACE_S, projects=RL.PROJECTS, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    argv, sid, resumed = pin_session(argv)
    model = _opt(argv, "--model") or ""
    since = time.time() if resumed else None
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, start_new_session=True)
    buf = []

    def drain():                # chunk by chunk: a grandchild holding the pipe open never loses what was printed
        fd = proc.stdout.fileno()
        while True:
            b = os.read(fd, 65536)
            if not b:
                return
            buf.append(b)
    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    hit = None
    while proc.poll() is None:
        try:
            proc.wait(timeout=poll_s)
            break
        except subprocess.TimeoutExpired:
            pass
        over, usd, tok, u = over_cap(sid, cap_usd, model, projects, since)
        if over:
            hit = (usd, tok, u)
            _stop(proc, grace_s)
            break
    reader.join(timeout=min(grace_s, 5))
    child_out = b"".join(buf)
    if hit is None:
        out.buffer.write(child_out) if hasattr(out, "buffer") else out.write(child_out.decode("utf-8", "replace"))
        out.flush()
        return proc.returncode if proc.returncode is not None else 1
    usd, tok, u = hit
    if child_out.strip():       # what the stopped child printed goes to stderr: out stays one whole result JSON
        err.write("spend_watchdog: the stopped child's stdout: %s\n" % child_out.decode("utf-8", "replace")[-4000:])
    # what a person reads says weighted tokens (owner 2026-11-16); cap_usd stays a field for the tools that need it.
    # No resumed or continued run reads this text: finish keeps it out of the item note (detached_helper.cap_stopped)
    cap_tok = cap_usd * 1e6 / rate(model)
    res = {"type": "result", "subtype": "error_max_budget_usd", "is_error": True, "session_id": sid,
           "stopped_by": "spend_watchdog", "cap_usd": cap_usd, "cap_weighted_tokens": int(round(cap_tok)),
           "result": "Stopped by spend_watchdog at its cap (≈{:,} weighted tokens); the session is resumable "
                     "(--resume {}).".format(int(round(cap_tok)), sid)}
    if tok is None:             # a model not in MODEL_PRICES: stopped by name, its spend unmeasured
        res.update(result="Stopped by spend_watchdog: %s; the session is resumable (--resume %s)." % (
            u["unknown_model"], sid), unknown_model=u["unknown_model"])
        err.write("spend_watchdog: stopped session %s: %s\n" % (sid, u["unknown_model"]))
    else:
        res.update(total_cost_usd=round(usd, 6), weighted_tokens=tok, token_unit=RL.TOKEN_UNIT,
                   cost_basis="spend_watchdog estimate: %d weighted_v2 tokens x %g list USD/M (%s)" % (
                       tok, rate(model), model or "?"),
                   usage={k: v for k, v in u.items() if k != "model_usage"}, modelUsage=u.get("model_usage") or {})
        err.write("spend_watchdog: stopped session {} at {:,} weighted tokens, its cap ≈{:,}\n".format(
            sid, tok, int(round(cap_tok))))
    out.write(json.dumps(res) + "\n")
    out.flush()
    return 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        print("usage: spend_watchdog.py --cap-usd X [--poll-s S] [--grace-s S] [--projects DIR] -- <claude argv>",
              file=sys.stderr)
        return 2
    i = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap-usd", type=float, required=True)
    ap.add_argument("--poll-s", type=float, default=POLL_S)
    ap.add_argument("--grace-s", type=float, default=GRACE_S)
    ap.add_argument("--projects", default=RL.PROJECTS)
    a = ap.parse_args(argv[:i])
    if not a.cap_usd > 0:
        print("spend_watchdog: --cap-usd must be > 0", file=sys.stderr)
        return 2
    return run(argv[i + 1:], a.cap_usd, a.poll_s, a.grace_s, a.projects)


if __name__ == "__main__":
    sys.exit(main())
