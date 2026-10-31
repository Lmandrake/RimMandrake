#!/usr/bin/env python3
"""arena_model_snapshot.py - record which model the judge's Opus call RESOLVES to, outside arena_judge.py.

    python3 src/RimMandrake/Utils/arena/arena_model_snapshot.py --out RUN_DIR [--no-probe]

ARENA_JUDGE_RECORD_RESOLVED_MODEL_NOT_ALIAS. The judge (arena_judge.OpusCLI) runs `claude -p --model <opus_model()>
--output-format text`, so its records carry the requested string (an alias or an id, from $ARENA_JUDGE_OPUS_MODEL
or $ANTHROPIC_DEFAULT_OPUS_MODEL), never the id the CLI ran. arena_judge.py is in the vet key
(arena_tasks.vet_runner_id hashes the whole file), so the capture lives HERE and leaves the key alone: at trial start
this writes RUN_DIR/resolved_models.json with
  - env: the model-selection variables as the trial sees them (MODEL_VARS; unset -> null),
  - judge.requested: arena_judge.opus_model() (refuses by name when neither variable is set),
  - judge.resolved: the modelUsage keys of ONE tiny `claude -p --output-format json` probe run with the judge's own
    argv flags and its own environment (arena_judge.judge_env, read-only use), i.e. what the alias resolves to now.
  - judge.ok: exactly one model resolved, and it is the requested id or contains the requested alias.
Exit 0 ok; 2 a required variable is missing (named); 3 the probe failed or resolved to something else (the file is
still written with the evidence). No model or account name is written in this file: everything is read from the
environment and from the CLI's own answer. LIMIT: a snapshot proves the resolution at trial start, not per vote; an
environment changed mid-trial is not seen (the judge's own records still carry only the requested string)."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

MODEL_VARS = ("ARENA_JUDGE_OPUS_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL",
              "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL")
OUT_NAME = "resolved_models.json"
PROBE_PROMPT = "Reply with the single word ok."
PROBE_TIMEOUT = 180


def env_snapshot(env=None) -> dict:
    src = os.environ if env is None else env
    return {k: (src.get(k) or None) for k in MODEL_VARS}


def resolves_to(requested: str, resolved: list) -> bool:
    return len(resolved) == 1 and (resolved[0] == requested or requested in resolved[0])


def probe(requested: str, *, exe=None, env=None, timeout=PROBE_TIMEOUT) -> dict:
    """One `claude -p` with the judge's flags but JSON output -> {resolved, cost_usd, rc, error}."""
    argv = list(exe or [shutil.which("claude") or "claude"]) + [
        "-p", "--model", requested, "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
        "--no-session-persistence", "--output-format", "json"]
    try:
        r = subprocess.run(argv, input=PROBE_PROMPT, capture_output=True, text=True, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"resolved": [], "rc": None, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return {"resolved": [], "rc": r.returncode, "error": "no JSON envelope: %s" % (r.stderr or r.stdout)[-300:]}
    mu = d.get("modelUsage") if isinstance(d, dict) else None
    return {"resolved": sorted(mu) if isinstance(mu, dict) else [], "rc": r.returncode,
            "cost_usd": d.get("total_cost_usd"), "is_error": d.get("is_error"),
            "error": None if isinstance(mu, dict) and mu else "envelope has no modelUsage"}


def snapshot(out_dir, *, run_probe=True, exe=None, env=None) -> tuple[int, dict]:
    import arena_judge as J                     # read-only use: opus_model() and judge_env(); the file is not edited
    doc = {"schema": "arena_resolved_models/1", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "env": env_snapshot(env), "judge": {}}
    try:
        if env is None:
            requested = J.opus_model()
        else:
            requested = next((env[k].strip() for k in MODEL_VARS[:2] if (env.get(k) or "").strip()), None)
            if not requested:
                raise J.JudgeUnavailable("no Opus model in the environment (%s)" % " / ".join(MODEL_VARS[:2]))
    except J.JudgeUnavailable as e:
        doc["judge"] = {"error": str(e)}
        return 2, doc
    doc["judge"]["requested"] = requested
    rc = 0
    if run_probe:
        jenv = J.judge_env(None, None, "model") if env is None else dict(env)
        p = probe(requested, exe=exe, env=jenv)
        ok = not p["error"] and resolves_to(requested, p["resolved"])
        doc["judge"].update(p, ok=ok)
        rc = 0 if ok else 3
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / (OUT_NAME + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, out / OUT_NAME)
    return rc, doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="the trial's run dir; writes %s there" % OUT_NAME)
    ap.add_argument("--no-probe", action="store_true", help="record the environment only (no model call)")
    a = ap.parse_args(argv)
    rc, doc = snapshot(a.out, run_probe=not a.no_probe)
    j = doc.get("judge", {})
    if rc == 2:
        print("arena_model_snapshot: %s" % j.get("error"), file=sys.stderr)
    elif rc == 3:
        print("arena_model_snapshot: judge model %r resolved to %s (%s)" % (j.get("requested"), j.get("resolved"),
                                                                        j.get("error")), file=sys.stderr)
    print(json.dumps({"rc": rc, "requested": j.get("requested"), "resolved": j.get("resolved"),
                      "out": str(Path(a.out) / OUT_NAME) if rc != 2 else None}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
