#!/usr/bin/env python3
"""Run a real multi-turn tool-calling loop against an NVIDIA-hosted model.

nemotron_probe.py proved a model will emit ONE well-formed tool call. That is not the
same as driving a seat. This runs the loop that actually breaks non-Claude models:
the model must chain grep -> read -> arithmetic over this repo's real def XML, feed
each tool RESULT back into its own next decision, and stop on its own.

The task has a checkable ground truth (src/Jawa/JawaIonWeapons/Defs/HediffDefs_JawaIonStun.xml):
  defName JawaIon_Stun, 4 stages, severityPerDay -1.2, top stage minSeverity 0.9
  => 0.9 / 1.2 = 0.75 day = 18 hours to decay from the top stage to zero.

Usage:  source ~/.config/secrets/nvidia.env
        python3 nemotron_agent_trial.py [--model M] [--out PATH] [--max-turns N]
"""
import argparse, json, os, re, subprocess, sys, time, urllib.error, urllib.request

BASE = "https://integrate.api.nvidia.com/v1/chat/completions"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
DEFS_GLOB = "src"

TASK = (
    "This repository contains RimWorld mod XML under src/. A Jawa ion weapon mod "
    "defines a hediff that builds up and eventually knocks a target down.\n\n"
    "Using ONLY the tools provided - do not answer from memory - determine:\n"
    "  1. the defName of that hediff\n"
    "  2. how many stages it has\n"
    "  3. how many HOURS it takes for severity to decay from the TOP stage's "
    "minSeverity back to zero, given the hediff's severityPerDay\n\n"
    "Show the arithmetic for part 3. Finish with a line formatted exactly:\n"
    "ANSWER: <defName> | <stages> | <hours>"
)

TOOLS = [
    {"type": "function", "function": {
        "name": "grep_defs",
        "description": "Search the repository's mod XML for a regex. Returns matching "
                       "file paths with line numbers, capped at 40 hits.",
        "parameters": {"type": "object",
                       "properties": {"pattern": {"type": "string",
                                                  "description": "regex to search for"}},
                       "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "read_def_file",
        "description": "Read a def XML file by its repo-relative path.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string",
                                               "description": "repo-relative path"}},
                       "required": ["path"]}}},
]


def t_grep(pattern):
    try:
        r = subprocess.run(["grep", "-rn", "--include=*.xml", "-E", pattern, DEFS_GLOB],
                           cwd=ROOT, capture_output=True, text=True, timeout=30)
    except Exception as e:
        return f"grep failed: {e}"
    lines = [l for l in r.stdout.splitlines() if l.strip()][:40]
    return "\n".join(lines) if lines else "(no matches)"


def t_read(path):
    p = os.path.normpath(os.path.join(ROOT, path))
    if not p.startswith(ROOT):
        return "refused: path escapes the repository"
    if not os.path.isfile(p):
        return f"(no such file: {path})"
    with open(p, encoding="utf-8", errors="replace") as f:
        d = f.read(60000)
    return d


DISPATCH = {"grep_defs": lambda a: t_grep(a.get("pattern", "")),
            "read_def_file": lambda a: t_read(a.get("path", ""))}


def post(body, key, timeout=300):
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"detail": type(e).__name__}


def grade(text):
    """Ground truth: JawaIon_Stun | 4 | 18."""
    t = (text or "")
    m = re.search(r"ANSWER:\s*(.+)$", t, re.M)
    line = m.group(1).strip() if m else ""
    low = t.lower()
    return {"answer_line": line[:120],
            "format_followed": bool(m),
            "defName_correct": "jawaion_stun" in low,
            "stages_correct": bool(re.search(r"\b4\b", line)) or "4 stage" in low,
            "hours_correct": bool(re.search(r"\b18\b", line)) or "18 hour" in low}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="nvidia/nemotron-3-super-120b-a12b")
    ap.add_argument("--out", default="research/nemotron_agent_trial.json")
    ap.add_argument("--max-turns", type=int, default=10)
    ap.add_argument("--retries", type=int, default=4)
    a = ap.parse_args()
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        sys.exit("NVIDIA_API_KEY unset. source ~/.config/secrets/nvidia.env")

    msgs = [{"role": "user", "content": TASK}]
    trace, t0 = [], time.time()
    final = ""
    for turn in range(a.max_turns):
        for attempt in range(a.retries):
            st, d = post({"model": a.model, "max_tokens": 8192, "tools": TOOLS,
                          "tool_choice": "auto", "messages": msgs}, key)
            if st == 200:
                break
            print(f"  turn {turn+1}: HTTP {st}, retry {attempt+1}", flush=True)
            time.sleep(8)
        if st != 200:
            trace.append({"turn": turn + 1, "http": st, "fatal": True})
            break
        ch = (d.get("choices") or [{}])[0]
        msg = ch.get("message") or {}
        calls = msg.get("tool_calls") or []
        content = msg.get("content") or ""
        trace.append({"turn": turn + 1, "finish_reason": ch.get("finish_reason"),
                      "n_tool_calls": len(calls),
                      "tools": [c["function"]["name"] for c in calls],
                      "args": [c["function"]["arguments"][:160] for c in calls],
                      "content_preview": content.strip()[:200],
                      "usage": d.get("usage", {})})
        # echo the assistant turn back verbatim, minus vendor-only fields
        msgs.append({k: v for k, v in msg.items()
                     if k in ("role", "content", "tool_calls")})
        if not calls:
            final = content
            print(f"  turn {turn+1}: no tool calls, model finished", flush=True)
            break
        for c in calls:
            name = c["function"]["name"]
            try:
                args = json.loads(c["function"]["arguments"] or "{}")
            except Exception:
                args = {}
            res = DISPATCH.get(name, lambda _a: "unknown tool")(args)
            print(f"  turn {turn+1}: {name}({json.dumps(args)[:70]}) "
                  f"-> {len(res)} chars", flush=True)
            msgs.append({"role": "tool", "tool_call_id": c["id"],
                         "content": res[:60000]})

    out = {"model": a.model, "task": TASK, "turns_used": len(trace),
           "wall_s": round(time.time() - t0, 1),
           "ground_truth": {"defName": "JawaIon_Stun", "stages": 4, "hours": 18},
           "grade": grade(final), "final": final[-1500:], "trace": trace}
    with open(os.path.join(ROOT, a.out), "w") as f:
        json.dump(out, f, indent=2)
    g = out["grade"]
    print(f"\n{a.model}")
    print(f"  turns {out['turns_used']}  wall {out['wall_s']}s")
    print(f"  grade: {json.dumps(g)}")
    print(f"  wrote {a.out}")


if __name__ == "__main__":
    main()
