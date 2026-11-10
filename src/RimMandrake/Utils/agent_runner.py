#!/usr/bin/env python3
"""Codex transport for role workers. Task acceptance belongs to the caller.

Ext4 work uses the existing drive-local Codex scratch and wsl.exe commands against
the original clone (GIT_WORKFLOW.md); no second working tree or UNC file reads.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/generating-images/scripts"))
import codex_image as CX


class Refused(RuntimeError):
    pass


def quota_gate(points=None):
    if points is None:
        try:
            import ops_watch
            points = ops_watch.c_codex(time.time(), ops_watch.load_rules(), {})
        except Exception as e:
            raise Refused("Codex weekly meter unreadable: %s" % e) from e
    for key in ("codex.week_used_pct", "codex.hours_to_reset"):
        p = points.get(key, {})
        v = p.get("v")
        if (p.get("m") != "MEASURED" or type(v) not in (int, float)
                or not math.isfinite(v) or v < 0):
            raise Refused("Codex weekly meter unreadable: %s %s" % (key, p))
    if points["codex.hours_to_reset"]["v"] <= 0:
        raise Refused("Codex weekly reset unreadable")
    if points["codex.week_used_pct"]["v"] > 90:
        raise Refused("Codex weekly quota exceeds 90%")
    return points


def launch_argv(cwd, result, model=None, effort=None, sandbox=None, exe=None):
    argv = [str(exe or CX.find_codex_cli()), "exec", "--sandbox",
            sandbox or os.environ.get("CODEX_SANDBOX", "workspace-write"),
            "--skip-git-repo-check", "-C", CX.wsl_to_win(Path(cwd)),
            "-o", CX.wsl_to_win(Path(result)), "--json",
            "-c", 'model_reasoning_effort="%s"' % (effort or os.environ.get("CODEX_EFFORT", "high"))]
    model = model or os.environ.get("CODEX_MODEL")
    if model:
        argv += ["-m", model]
    return argv + ["-"]


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


def event_error(stream):
    last_message = ""
    for line in stream.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("type") in ("error", "turn.failed"):
            return str(ev)
        item = ev.get("item") if isinstance(ev, dict) else None
        if isinstance(item, dict) and item.get("type") == "agent_message":
            last_message = item.get("text") or ""
    # Do not mistake source code or an expected failing test quoted in a tool
    # event for an authentication failure. Inspect only a final failure report.
    if re.match(r"(?:Blocked|Failed|Error|You've hit|Not logged)", last_message, re.I) and re.search(
            r"setup refresh had errors|Wsl/Service/E_ACCESSDENIED|usage_limit_reached|authentication_failed|quota|auth", last_message):
        return "Codex quota, authentication or sandbox setup failure (see event stream)"
    return None


def run(cwd, prompt, result, events, spend, *, model=None, effort=None,
        sandbox=None, timeout=7200, invoke=subprocess.run, meter=None, agent=None):
    """Always persist a runner-specific spend/result envelope, including refused runs.

    stdout is retained verbatim as events; -o is only the final message. The
    envelope is transport status, never a Designer result or a Judge verdict.
    """
    cwd, result, events, spend = map(lambda p: Path(p).resolve(), (cwd, result, events, spend))
    for p in (result, events, spend):
        p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"runner": "codex", "usage": "UNMEASURED", "state": "failed"}
    stream, answer, error, rc = "", "", None, 1
    try:
        rec["quota"] = quota_gate(meter)
        if agent:
            p = cwd / ".claude/agents" / (agent + ".md")
            prompt = p.read_text(encoding="utf-8") + "\n\n" + prompt
        work = cwd
        target = result
        if not CX.on_windows_drive(cwd):
            work = CX.CODEX_SCRATCH / ("agent-" + uuid.uuid4().hex)
            work.mkdir(parents=True, exist_ok=False)
            target = work / "last-message.txt"
            rec["staging_cwd"] = str(work)
        if CX.in_wsl():
            # Windows shell tools enter WSL explicitly: every read/write/test/git
            # operates on the leased clone, never on a mirror or copied snapshot.
            prefix = ("Runtime adapter: your shell is Windows. The repository is in WSL Ubuntu at %s. "
                      "For ALL repository reads, writes, git, Python and tests, call "
                      "wsl.exe -d Ubuntu -e bash -lc %s (append your command after cd). "
                      "Do not use UNC file tools or Windows git. Preserve LF. rg is not installed; use find/grep. "
                      "The task below and its result paths refer to that WSL tree.\n\n") % (
                          cwd, shlex.quote("cd %s && <command>" % shlex.quote(str(cwd))))
            runtime_keys = ("AGENT_SEAT", "RIMFLOW_SEAT", "RIMFLOW_BRIDGE_SEAT", "RELENTLESS_ROOT",
                            "RELENTLESS_RULES", "RELENTLESS_GEN", "RELENTLESS_HELP_NONCE")
            exports = " ".join("%s=%s" % (k, shlex.quote(os.environ[k])) for k in runtime_keys if k in os.environ)
            if exports:
                prefix += "Preserve the worker lease and seat in every WSL command: export %s\n\n" % exports
            prompt = prefix + prompt
        rec["sandbox"] = sandbox or os.environ.get("CODEX_SANDBOX", "workspace-write")
        rec["model"] = model or os.environ.get("CODEX_MODEL") or "config"
        rec["effort"] = effort or os.environ.get("CODEX_EFFORT", "high")
        target.unlink(missing_ok=True)
        argv = launch_argv(work, target, model, effort, sandbox)
        proc = invoke(argv, input=prompt, cwd=str(work), capture_output=True,
                      text=True, errors="replace", timeout=timeout)
        stream, rc = proc.stdout or "", proc.returncode
        error = event_error(stream)
        if rc:
            error = error or (proc.stderr or "Codex exited %s" % rc)[-2000:]
        if target.is_file():
            answer = target.read_text(encoding="utf-8", errors="replace")
            if target != result:
                result.write_text(answer, encoding="utf-8")
        if not answer.strip():
            error = error or "Codex produced no last message"
        rec["state"] = "failed" if error else "done"
    except subprocess.TimeoutExpired as e:
        stream = e.stdout or ""
        if isinstance(stream, bytes):
            stream = stream.decode("utf-8", errors="replace")
        error = "Codex timeout: %s" % timeout
    except Exception as e:
        error = "%s: %s" % (type(e).__name__, e)
    rec.update(usage=event_usage(stream), error=error, returncode=rc)
    events.write_text(stream, encoding="utf-8")
    spend.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return {"runner": "codex", "is_error": rec["state"] != "done", "codex_usage": rec["usage"],
            "result": error or answer, "subtype": rec["state"], "spend": str(spend)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cwd", required=True)
    ap.add_argument("--prompt")
    ap.add_argument("--agent", help="inline the named project's .claude/agents definition")
    ap.add_argument("--result", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--spend", required=True)
    ap.add_argument("--model")
    ap.add_argument("--effort")
    ap.add_argument("--sandbox", choices=("read-only", "workspace-write", "danger-full-access"))
    ap.add_argument("--timeout", type=int, default=7200)
    a = ap.parse_args(argv)
    prompt = a.prompt if a.prompt is not None else sys.stdin.read()
    res = run(a.cwd, prompt, a.result, a.events, a.spend,
              model=a.model, effort=a.effort, sandbox=a.sandbox, timeout=a.timeout, agent=a.agent)
    print(json.dumps(res))
    return 1 if res["is_error"] else 0


if __name__ == "__main__":
    sys.exit(main())
