#!/usr/bin/env python3
"""code_review_calibration.py - the `code_review` family's calibration (RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS).

The `model_check` of the `code_review` row in infrastructure/state/judge_calibration.json. Codex is handed the review
brief (roles/code_review.md) and the control store's page (design/specs/2026-11-18-pipeline-control-surface/
boundary.md) and sorts the 35 claims of code_review_calibration_set.json (id and claim text only; the labels stay
here) as problem, polish or next_version. It reads no code: the call runs `gpt_consult.py --lockdown` (no tools).
A problem is a refusal (`got: refuse`), anything else a pass; one row per claim goes to $RM_CALIBRATION_RESULTS, and
refusal_contract.judge_cases compares them with the labels. The labels are `page_rule` (owner card 2026-11-19
13:27:48Z: a rare failure is "not handled", not a Problem), not the analyst's `expect`. The run also prints the pass
mark on the 10 `agreed` claims (every agreed real one called a Problem, no agreed polish one called a Problem) and the
agreement on all 35. The row reads CALIBRATED when the pass mark passes (the row's `pass_mark`, refusal_contract.
judge_cases; owner, 2026-11-25 8:43 PM PST); the count of exact labels is a reading.

It spends one Codex call, so it runs only from `refusal_contract.py calibrate --model code_review`, never on a
schedule. Owner card 2026-11-19 about 12:40 AM PST: "Codex sorts the 35 old complaints one time. It reviews no new
code and no ticket comes from it." A call that gets no answer exits with gpt_consult's code and writes no results.

    python3 src/RimMandrake/rimflow/code_review_calibration.py run     ask Codex once, write the results, one line each
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

SET = os.path.join(HERE, "code_review_calibration_set.json")
BRIEF = "src/RimMandrake/rimflow/roles/code_review.md"
CONSULT = os.path.join(REPO, "src", "RimMandrake", "Utils", "gpt_consult.py")
ANSWER_DIR = "/mnt/d/ClaudeWork/rimmandrake/conductor"
CLASSES = ("problem", "polish", "next_version")
CONSULT_S = 500   # the first call took 211 s [measured, gpt_call_log round code_review_calibration]; under the 540 s cap


def load_set():
    with open(SET, encoding="utf-8") as f:
        return json.load(f)


def prompt(cal):
    lines = ["You are the reviewer the attached brief describes (roles/code_review.md). The attached boundary.md is the",
             "control store's page. You are not reviewing code: you are sorting claims another reviewer already made",
             "about the store. Take each claim's described behaviour as true and decide only its class against the",
             "page, by the brief's rules. Use only the brief, the page and the claim text.",
             "",
             "Return ONLY a JSON array with one object per claim, in the brief's return format",
             '({"id", "class", "reason", "page_entry", "why"}), %d objects, ids exactly as given.' % len(cal["claims"]),
             "", "## The claims", ""]
    lines += ["- %s: %s" % (c["id"], c["claim"]) for c in cal["claims"]]
    return "\n".join(lines) + "\n"


def parse(answer):
    """-> {id: row} from the answer's JSON array; {} when there is none."""
    m = re.search(r"\[\s*\{.*\}\s*\]", answer or "", re.S)
    try:
        rows = json.loads(m.group(0)) if m else []
    except ValueError:
        return {}
    return {str(r["id"]): r for r in rows if isinstance(r, dict) and r.get("id") and r.get("class") in CLASSES}


def label(c):
    """-> refuse | pass: the page rule's label (real = a Problem), else the analyst's."""
    return {"real": "refuse", "not": "pass"}.get(c.get("page_rule"), c["expect"])


def results(cal, parsed):
    """-> the case rows: a claim Codex did not sort gets no row (judge_cases reads it as did not run)."""
    return [{"id": c["id"], "expect": label(c), "agreed": bool(c.get("agreed")),
             "got": "refuse" if parsed[c["id"]]["class"] == "problem" else "pass",
             "class": parsed[c["id"]]["class"], "page_entry": parsed[c["id"]].get("page_entry"),
             "why": parsed[c["id"]].get("why")} for c in cal["claims"] if c["id"] in parsed]


def pass_mark(cal, rows):
    """-> (passed, caught, real, false_alarms, polish, agree, sorted) on the `agreed` claims; an agreed claim not
    sorted counts against the mark."""
    got = {r["id"]: r["got"] for r in rows}
    agreed = [c for c in cal["claims"] if c.get("agreed")]
    real = [c["id"] for c in agreed if label(c) == "refuse"]
    polish = [c["id"] for c in agreed if label(c) == "pass"]
    caught = sum(got.get(i) == "refuse" for i in real)
    false_alarms = sum(got.get(i) != "pass" for i in polish)
    agree = sum(r["got"] == r["expect"] for r in rows)
    return caught == len(real) and false_alarms == 0, caught, len(real), false_alarms, len(polish), agree, len(rows)


def run():
    cal = load_set()
    out = os.path.join(ANSWER_DIR, "code_review_calibration_answer_page_rule.md")
    with tempfile.TemporaryDirectory() as tmp:
        ask = os.path.join(tmp, "ask.md")
        with open(ask, "w", encoding="utf-8") as f:
            f.write(prompt(cal))
        cmd = [sys.executable, CONSULT, "--prompt-file", ask, "-f", BRIEF, "-f", cal["page"], "--out", out,
               "--lockdown", "--round", "code_review_calibration", "--timeout", str(CONSULT_S),
               "--required", "owner card 2026-11-19 13:27:48Z: one more Codex calibration of the code_review brief, "
                             "after the page rule"]
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=CONSULT_S + 30)
    if p.returncode != 0:
        print("UNRUN: gpt_consult exit %d: %s" % (p.returncode, (p.stderr.strip().splitlines() or [""])[-1]))
        print("command: %s" % " ".join(cmd))
        return p.returncode
    rows = results(cal, parse(p.stdout))
    path = os.environ.get(RC.RESULTS_ENV)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cases": rows}, f, indent=1)
    for r in rows:
        print("%-6s expect %-6s got %-6s %-12s %s" % (r["id"], r["expect"], r["got"], r["class"], r["page_entry"]))
    ok, caught, real, fa, polish, agree, n = pass_mark(cal, rows)
    print("sorted %d of %d; %d as labelled; answer: %s" % (len(rows), len(cal["claims"]), agree, out))
    print("pass mark %s: agreed real caught %d of %d (limit all); agreed polish called problem %d of %d (limit 0); "
          "exact labels (a reading): %d of %d" % ("PASS" if ok else "FAIL", caught, real, fa, polish, agree, n))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(run() if sys.argv[1:] == ["run"] else (print(__doc__) or 2))
