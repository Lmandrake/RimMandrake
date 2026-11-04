"""What a Relentless run cost, measured for every run (RELENTLESS_USAGE_MEASURE_NO_FLAT_GUESSES).

`claude -p --output-format json` prints ONE result object when it ends cleanly. A run that is killed, times out
(run_max_s), runs out of context or dies leaves an empty .json: usage was then charged as the flat run_reserve
(23% of 2026-11-01 spend, 42 runs). Claude Code writes every assistant message with its `usage` to the session
transcript as it goes, so the cost of a killed run is still on disk. Order of trust: the result object (basis
"result"), else the run's transcripts (basis "transcript"), else the flat reserve, labelled "estimated"."""
import json
import os
import calendar
import re
import time

SIDECAR = ".clone"
KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def sidecar_path(run):
    return (run.get("out") or "") + SIDECAR


def note_clone(run, clone):
    """At launch, before the unit exists: the working directory of the run, so its transcripts can be found later."""
    p = sidecar_path(run)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(clone or "")


def clone_of(run):
    try:
        with open(sidecar_path(run), encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def project_dir(clone):
    return os.path.expanduser("~/.claude/projects/" + re.sub(r"[^A-Za-z0-9]", "-", clone or ""))


def _ts(s):
    try:
        return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def _files(d, since, subagents_only=False):
    for root, _dirs, names in os.walk(d):        # session files and their subagents/ files
        if subagents_only and os.path.basename(root) != "subagents":
            continue
        for n in names:
            if n.endswith(".jsonl"):
                p = os.path.join(root, n)
                try:
                    if os.stat(p).st_mtime >= since:
                        yield p
                except OSError:
                    pass


def transcript_result(clone, since, until=None, session=None, subagents_only=False):
    """-> a result-shaped {"usage": ...} summed over the assistant messages written in `clone`'s transcripts at or
    after `since` (one message counted once by its id, at its largest output), or None when there are none.
    subagents_only: only the subagents/ transcripts, of `session` when it is known, else of every session there."""
    if not clone:
        return None
    best = {}
    d = project_dir(clone)
    if subagents_only and session:
        d = os.path.join(d, re.sub(r"[^A-Za-z0-9-]", "", str(session)) or "-")
    for p in _files(d, since, subagents_only):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"usage"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue
                    m = d.get("message") if isinstance(d, dict) else None
                    u = m.get("usage") if isinstance(m, dict) else None
                    if d.get("type") != "assistant" or not isinstance(u, dict):
                        continue
                    t = _ts(d.get("timestamp"))
                    if t is None or t < since or (until and t > until):
                        continue
                    key = m.get("id") or "%s:%s" % (p, d.get("uuid"))
                    if key not in best or (u.get("output_tokens") or 0) >= (best[key].get("output_tokens") or 0):
                        best[key] = u
        except OSError:
            continue
    if not best:
        return None
    tot = dict.fromkeys(KEYS, 0)
    w5 = w1 = 0
    for u in best.values():
        for k in KEYS:
            v = u.get(k)
            tot[k] += v if type(v) is int and v >= 0 else 0
        cw = u.get("cache_creation_input_tokens")
        cc = u.get("cache_creation")
        a, b = (cc.get("ephemeral_5m_input_tokens"), cc.get("ephemeral_1h_input_tokens")) if isinstance(cc, dict) else (None, None)
        if type(a) is int and type(b) is int and a + b == cw:
            w5, w1 = w5 + a, w1 + b
        else:
            w1 += cw if type(cw) is int else 0         # an unsplit write is weighed at the dearer rate
    tot["cache_creation"] = {"ephemeral_5m_input_tokens": w5, "ephemeral_1h_input_tokens": w1}
    return {"usage": tot}


def subagent_tokens(RL, run, res):
    """RELENTLESS_SUBAGENT_DECIDE_THREE_PER_BUILDER: the result object's usage is the main session's; a worker's
    subagents spend in their own transcripts (<project>/<session>/subagents/*.jsonl). -> their weighted tokens, 0 when
    there are none. Without a session id every subagents/ transcript written in the clone since the run began counts:
    a charge errs dear, never cheap."""
    sid = res.get("session_id") if isinstance(res, dict) else None
    tr = transcript_result(clone_of(run), run.get("at") or 0, session=sid, subagents_only=True)
    return int(RL.run_tokens(tr) or 0) if tr else 0


def measure(RL, run):
    """-> (weighted tokens or 0, basis). 0 means unmeasurable: the caller charges the reserve and the basis says
    "estimated"."""
    res = RL.read_result({"out": run.get("out"), "err": run.get("err")})
    tok = RL.run_tokens(res) if res else None
    if tok:
        sub = subagent_tokens(RL, run, res)
        return (int(tok) + sub, "result+subagents") if sub else (int(tok), "result")
    tr = transcript_result(clone_of(run), run.get("at") or 0)
    tok = RL.run_tokens(tr) if tr else None
    if tok:
        return int(tok), "transcript"
    return 0, "estimated"


# ---------------------------------------------------------------- which OOM kills are Relentless's

OOM_SCOPE_MARK = "rm-relentless"


def own_oom_kills(kernel_lines):
    """Pure. Kernel `oom-kill:constraint=...` lines -> how many killed something inside a Relentless run's cgroup
    (its unit is named rm-relentless-*). /proc/vmstat's oom_kill counts the whole host: on 2026-11-01 all five
    step-downs were other cgroups' kills (44 intended rm-harness selftest caps, 21 BENCH tool caps, none Relentless's),
    each of which stepped staffing down for nothing."""
    return sum(1 for ln in kernel_lines if "oom-kill:constraint" in ln and OOM_SCOPE_MARK in ln)
