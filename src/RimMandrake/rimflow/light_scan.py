#!/usr/bin/env python3
"""light_scan.py: one bounded question-list scan by a light model, reusable at any door (the light scan of
design/specs/2026-11-15-cheap-guards-at-every-door.md section 5; RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED).

It judges what no program here can see: whether a scene that runs cleanly asks what its bar promises (FlowWorks visit 1:
scene_coating_wash passed with no coat ever seen; the walk scene's off/on row never switched the engine off). The model
reads the declared inputs and nothing else: no tools, no files, no settings, no MCP, run from /tmp; one call; a fixed
JSON answer or "did not run". A scan that cannot be read never blocks. The model is reached as every LLM call here is,
the `claude` CLI in print mode with a model alias the CLI resolves from the environment; it is never told its spend
(owner, 2026-11-16), so `max_usd` is a record kept beside the answer, not a flag.

    python3 src/RimMandrake/rimflow/light_scan.py <list_id> <subject> --input NAME=PATH [--input ...] [--model sonnet]

Contract: the docstring of acceptance/guard_light_scan_accept.py (the filing seat's; the builder does not edit it).
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "light_scan_questions.json"), encoding="utf-8") as _f:
    QUESTIONS = {k: v for k, v in json.load(_f).items() if not k.startswith("_")}
MODELS = ("sonnet", "opus")     # Haiku is banned; this is a light scan, not a judge
ANSWERS = ("yes", "no", "cannot_tell")
TIMEOUT_S = 600
CITE = re.compile(r"\b([A-Za-z0-9_.\-]+):(\d+)\b")

SYSTEM = ("You answer a fixed list of questions about the inputs you are given, and nothing else. Reply with ONE JSON "
          "object and no other text: {\"answers\": [{\"q\": <question id>, \"answer\": \"yes\" | \"no\" | "
          "\"cannot_tell\", \"evidence\": <text>}]}, one entry per question id, no other ids. A \"no\" must cite the "
          "input line that shows it, as <input name>:<line number>. Answer \"cannot_tell\" when the inputs do not "
          "settle it.")


def _prompt(list_id, subject, inputs):
    qs = QUESTIONS[list_id]
    out = ["Subject: %s" % subject, "", "Questions (answer every id):"]
    out += ["- %s: %s" % (q["q"], q["text"]) for q in qs]
    for name, text in inputs.items():
        out += ["", "=== input %s (lines numbered) ===" % name]
        out += ["%d: %s" % (i, ln) for i, ln in enumerate(str(text).splitlines(), 1)]
    out += ["", "Reply with the one JSON object only."]
    return "\n".join(out)


def _answer_obj(stdout):
    """-> (the answers object, usd or None) from the CLI's stdout: its --output-format json wrapper, or the object."""
    try:
        out = json.loads(stdout)
    except (TypeError, ValueError):
        return None, None
    if not isinstance(out, dict):
        return None, None
    if "answers" in out:
        return out, None
    usd = out.get("total_cost_usd")
    usd = float(usd) if isinstance(usd, (int, float)) else None
    txt = out.get("result")
    if not isinstance(txt, str):
        return None, usd
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        obj = json.loads(m.group(0)) if m else None
    except ValueError:
        obj = None
    return (obj if isinstance(obj, dict) else None), usd


def scan(list_id, subject, inputs, runner=subprocess.run, model="sonnet", max_input_chars=60000, max_usd=0.25):
    """-> {"ran", "ok", "answers", "refusals", "did_not_run", "usd", "max_usd"}. ok is False only on a refusal."""
    if model not in MODELS:
        raise ValueError("light_scan model %r: only %s (Haiku is banned; a light scan is no judge)" % (
            model, ", ".join(MODELS)))
    qs = QUESTIONS[list_id]
    out = {"ran": False, "ok": True, "answers": [], "refusals": [], "did_not_run": None, "usd": None,
           "max_usd": max_usd, "list": list_id, "subject": subject}
    size = sum(len(str(v)) for v in (inputs or {}).values())
    if not inputs:
        out["did_not_run"] = "no inputs were declared"
        return out
    if size > max_input_chars:
        out["did_not_run"] = "the inputs hold %d characters, over the %d cap; never truncated, so not run" % (
            size, max_input_chars)
        return out
    argv = ["claude", "-p", "--model", model, "--output-format", "json", "--strict-mcp-config", "--tools", "",
            "--setting-sources", "", "--no-session-persistence", "--system-prompt", SYSTEM]
    try:
        r = runner(argv, input=_prompt(list_id, subject, inputs), capture_output=True, text=True, timeout=TIMEOUT_S,
                   cwd="/tmp")
    except Exception as e:  # noqa: BLE001  a timeout or a start failure: the scan did not run, it never blocks
        out["did_not_run"] = "the model call did not finish: %s: %s" % (type(e).__name__, str(e)[:200])
        return out
    out["ran"] = True
    obj, out["usd"] = _answer_obj(r.stdout)
    if r.returncode != 0:
        out["did_not_run"] = "the model call exited %s: %s" % (r.returncode, (r.stderr or r.stdout or "")[:200])
        return out
    ans = obj.get("answers") if isinstance(obj, dict) else None
    want = [q["q"] for q in qs]
    if not isinstance(ans, list) or not all(isinstance(a, dict) for a in ans):
        out["did_not_run"] = "the answer is not the fixed JSON object: %s" % str(r.stdout)[:200]
        return out
    got = [a.get("q") for a in ans]
    if sorted(got) != sorted(want) or len(set(got)) != len(got):
        out["did_not_run"] = "the answer's question ids %s are not the list's %s" % (got, want)
        return out
    bad = [a for a in ans if a.get("answer") not in ANSWERS]
    if bad:
        out["did_not_run"] = "an answer outside %s: %s" % ("/".join(ANSWERS), bad[0].get("answer"))
        return out
    names = set(inputs)
    uncited = [a["q"] for a in ans if a["answer"] == "no"
               and not any(n in names for n, _ in CITE.findall(str(a.get("evidence") or "")))]
    if uncited:
        out["did_not_run"] = "a no that cites no input line (%s): an unsupported no refuses nothing" % ", ".join(uncited)
        return out
    out["answers"] = ans
    text = {q["q"]: q["text"] for q in qs}
    for a in ans:
        if a["answer"] == "no":
            out["refusals"].append({
                "q": a["q"], "evidence": str(a.get("evidence")),
                "would_pass": "the scene does what the question asks: %s" % text[a["q"]],
                "smallest_fix": "change the scene at the cited line so it %s, then rerun this scan" % (
                    "reads the promised state from the game" if a["q"] == "observes_the_promise" else
                    "checks the judged event happened first" if a["q"] == "event_happened" else
                    "drives the game into each compared state")})
    out["ok"] = not out["refusals"]
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="one bounded light-model scan")
    ap.add_argument("list_id", choices=sorted(QUESTIONS))
    ap.add_argument("subject")
    ap.add_argument("--input", action="append", default=[], metavar="NAME=PATH")
    ap.add_argument("--model", default="sonnet", choices=MODELS)
    a = ap.parse_args(argv)
    inputs = {}
    for x in a.input:
        name, _, path = x.partition("=")
        with open(path, encoding="utf-8") as f:
            inputs[name] = f.read()
    print(json.dumps(scan(a.list_id, a.subject, inputs, model=a.model), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
