#!/usr/bin/env python3
"""Codex transport for role workers, through Dispatch's Codex door (door_agent). Task acceptance belongs to the caller.

The door starts Codex in the clone, keeps answered, failed, no answer in time and could not start apart, and streams
the events. This file keeps RimMandrake's own part: the weekly meter gate, the agent definition, the spend envelope.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dispatch_door  # noqa: E402


class Refused(RuntimeError):
    pass


PROBE_TIMEOUT_S = 150   # a one-word gpt_consult answered in well under a minute on 2026-11-18; 150 s is 2x+ margin


def codex_probe():
    """The cheapest call that makes Codex write a fresh rate-limit reading: the one-word gpt_consult the
    owner ran by hand on 2026-11-18 (it turned a 9.9 h stale ESTIMATE into MEASURED). Raises on any failure."""
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("gpt_consult.py")),
                        "Reply with the single word: ok"], capture_output=True, text=True,
                       timeout=PROBE_TIMEOUT_S, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError("exit %s: %s" % (r.returncode, (r.stderr or r.stdout or "").strip()[-300:]))  # cut-ok: exception message


def _read_meter():
    import ops_watch
    return ops_watch.c_codex(time.time(), ops_watch.load_rules(), {})


def _bad_key(points):
    for key in ("codex.week_used_pct", "codex.hours_to_reset"):
        p = points.get(key, {})
        v = p.get("v")
        if (p.get("m") != "MEASURED" or type(v) not in (int, float)
                or not math.isfinite(v) or v < 0):
            return key, p
    return None


def _stale(points):
    """Only a readable-but-not-MEASURED weekly percentage (ESTIMATE: stale, a floor, or window reset since) is
    something a fresh Codex reading can cure. Missing/negative/NaN/UNMEASURED-everything is not."""
    p = points.get("codex.week_used_pct", {})
    v = p.get("v")
    return p.get("m") == "ESTIMATE" and type(v) in (int, float) and math.isfinite(v) and v >= 0


def quota_gate(points=None, probe=None, reader=None):
    """probe/reader are injectable. The default probe fires only when the gate read the meter itself (points None)
    or the caller passed a probe; a caller-supplied snapshot is otherwise judged as given. At most one probe."""
    reader = reader or _read_meter
    from_meter = points is None
    if from_meter:
        try:
            points = reader()
        except Exception as e:
            raise Refused("Codex weekly meter unreadable: %s" % e) from e
    if _bad_key(points) and _stale(points) and (probe or from_meter):
        try:
            (probe or codex_probe)()
        except Exception as e:
            raise Refused("Codex meter stale and the refresh probe failed: %s: %s" % (type(e).__name__, e)) from e
        try:
            points = reader()
        except Exception as e:
            raise Refused("Codex meter stale; probe ran but the re-read failed: %s" % e) from e
        if _bad_key(points):
            raise Refused("Codex meter stale; probe ran but the reading is still not MEASURED: %s" % (_bad_key(points),))
    bad = _bad_key(points)
    if bad:
        raise Refused("Codex weekly meter unreadable: %s %s" % bad)
    if points["codex.hours_to_reset"]["v"] <= 0:
        raise Refused("Codex weekly reset unreadable")
    if points["codex.week_used_pct"]["v"] > 90:
        raise Refused("Codex weekly quota exceeds 90%")
    return points


def event_usage(stream):
    """Sum completed turns. A malformed/missing usage is unknown, never zero."""
    total = {"input_tokens": 0, "output_tokens": 0}
    seen = False
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get("type") != "turn.completed":
            continue
        u = event.get("usage")
        if not isinstance(u, dict) or not all(type(u.get(k)) is int and u[k] >= 0 for k in total):
            return "UNMEASURED"
        seen = True
        for k in total:
            total[k] += u[k]
    return total if seen else "UNMEASURED"


def rollout_usage(stream, home=None):
    """The running token total of the Codex thread a stream started: `codex exec` is ONE turn, so its turn.completed
    usage comes only at the very end, and a run killed before then has none in its events. Codex's own session
    rollout (<home>/sessions/**/rollout-*-<thread_id>.jsonl) writes a token_count after every model call; its last
    total_token_usage is the run's spend so far. -> dict, or "UNMEASURED"."""
    tid = None
    for line in stream.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict) and e.get("type") == "thread.started":
            tid = e.get("thread_id")
            break
    if not tid or not re.fullmatch(r"[0-9a-f-]{8,64}", str(tid)):
        return "UNMEASURED"
    try:
        root = Path(home) if home else dispatch_door.load().default_home("linux")
        files = sorted((root / "sessions").glob("*/*/*/rollout-*-%s.jsonl" % tid))
        text = files[-1].read_text(encoding="utf-8", errors="replace") if files else ""
    except (OSError, IndexError, AttributeError):
        return "UNMEASURED"
    last = None
    for line in text.splitlines():
        if '"token_count"' not in line:
            continue
        try:
            t = ((json.loads(line).get("payload") or {}).get("info") or {}).get("total_token_usage")
        except (ValueError, AttributeError):
            continue
        if isinstance(t, dict) and all(type(t.get(k)) is int and t[k] >= 0 for k in ("input_tokens", "output_tokens")):
            last = t
    if last is None:
        return "UNMEASURED"
    return dict({k: last[k] for k in ("input_tokens", "output_tokens")},
                **({"cached_input_tokens": last["cached_input_tokens"]} if type(last.get("cached_input_tokens")) is int
                   else {}), usage_from="codex rollout %s (running total; the run never completed its turn)" % tid)


def usage_of_files(spend, events, home=None):
    """A run's measured usage from what it left on disk: the spend envelope, else the events streamed so far (a run
    killed before it wrote the envelope), else Codex's session rollout for the thread those events started. None
    readable -> UNMEASURED, never zero."""
    try:
        u = json.loads(Path(spend).read_text(encoding="utf-8")).get("usage")
        if isinstance(u, dict):
            return u
    except (OSError, ValueError, AttributeError):
        pass
    try:
        stream = Path(events).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "UNMEASURED"
    u = event_usage(stream)
    return u if isinstance(u, dict) else rollout_usage(stream, home)


def run(cwd, prompt, result, events, spend, *, model=None, effort=None, sandbox=None, timeout=7200, call=None,
        meter=None, agent=None, codex_home=None):
    """Always persist a runner-specific spend/result envelope, including refused runs.

    The events file streams during the run; `result` gets the last message only of a run that answered. The envelope
    is transport status, never a Designer result or a Judge verdict. `call` replaces door_agent.agent in tests.
    """
    cwd, result, events, spend = map(lambda p: Path(p).resolve(), (cwd, result, events, spend))
    for p in (result, events, spend):
        p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"runner": "codex", "usage": "UNMEASURED", "state": "failed"}
    answer, error, read_result, rc = "", None, None, 1
    try:
        rec["quota"] = quota_gate(meter)
        if agent:
            p = cwd / ".claude/agents" / (agent + ".md")
            prompt = p.read_text(encoding="utf-8") + "\n\n" + prompt
        # "inherit" leaves the model to the sign-in folder's config.toml, as before
        model = model or os.environ.get("CODEX_MODEL") or "inherit"
        effort = effort or os.environ.get("CODEX_EFFORT") or "high"
        if call is None:
            door = dispatch_door.load("door_agent")
            call = door.agent
            timeout = door.DEFAULT_TIMEOUT_S if timeout is None else timeout
        result.unlink(missing_ok=True)              # a result of an earlier run is never this run's answer
        r = call(prompt, cwd, result=result, events=events, model=model, effort=effort, sandbox=sandbox,
                 home=codex_home, timeout=timeout, caller="rimmandrake/agent_runner")
        rc = r.rc
        rec.update(sandbox=r.sandbox, model="config" if model == "inherit" else model, effort=effort,
                   codex_side="wsl", codex_home=r.home, outcome=r.outcome, kind=r.kind, job=r.job)
        answer = r.text
        if not r.answered:
            prefix, detail = "Codex %s (%s): " % (r.kind, r.outcome), (r.detail or "").strip()
            error = prefix + detail
            if len(detail) > 1500:
                read_result = prefix + detail[-1500:]  # cut-ok: existing quota search and reviewer parsing window
        rec["state"] = "failed" if error else "done"
    except Exception as e:
        error = "%s: %s" % (type(e).__name__, e)
    stream = events.read_text(encoding="utf-8", errors="replace") if events.is_file() and rec.get("kind") else ""
    usage = event_usage(stream)
    if not isinstance(usage, dict) and stream:
        usage = rollout_usage(stream, rec.get("codex_home"))
    rec.update(usage=usage, error=error, returncode=rc)
    rec["usage_from"] = "turn.completed events in %s" % events
    events.write_text(stream, encoding="utf-8")
    spend.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return {"runner": "codex", "is_error": rec["state"] != "done", "codex_usage": rec["usage"],
            "result": error or answer, "subtype": rec["state"], "spend": str(spend),
            **({"read_result": read_result} if read_result is not None else {})}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cwd", required=True)
    ap.add_argument("--prompt")
    ap.add_argument("--agent", help="inline the named project's .claude/agents definition")
    ap.add_argument("--result", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--spend", required=True)
    ap.add_argument("--codex-home", help="another sign-in folder that has its own sign-in (default: the one folder)")
    ap.add_argument("--model")
    ap.add_argument("--effort")
    ap.add_argument("--sandbox", choices=("read-only", "workspace-write", "danger-full-access"))
    ap.add_argument("--timeout", type=int, default=7200)
    a = ap.parse_args(argv)
    prompt = a.prompt if a.prompt is not None else sys.stdin.read()
    res = run(a.cwd, prompt, a.result, a.events, a.spend,
              model=a.model, effort=a.effort, sandbox=a.sandbox, timeout=a.timeout, agent=a.agent, codex_home=a.codex_home)
    print(json.dumps(res))
    return 1 if res["is_error"] else 0


if __name__ == "__main__":
    sys.exit(main())
