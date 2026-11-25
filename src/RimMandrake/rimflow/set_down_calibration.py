#!/usr/bin/env python3
"""set_down_calibration.py: run the set-down judge on the 25 real set-downs of 2026-11-25 and measure its agreement
with the Conductor's classes. The model check of the row `set_down_judge` in infrastructure/state/judge_calibration.json
(refusal_contract.py calibrate --model set_down_judge runs it; it spends 25 model calls).

Item RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS; page design/specs/2026-11-24-filing-gate/boundary.md.
Cases: design/specs/2026-11-24-filing-gate/set_down_cases.json (each set-down word for word, the rebuilt class, the
filing run's transcript). Each case is judged as the door judges it: the transcript up to the filing, and the earlier
refusals of the same unit and id. A "could not judge" counts as a pass (the door passes it).

    python3 src/RimMandrake/rimflow/set_down_calibration.py            run the 25, write the table and the results
    python3 src/RimMandrake/rimflow/set_down_calibration.py --table <raw.json>   rewrite the table from a stored run

The case results go to $RM_CALIBRATION_RESULTS when it is set (refusal_contract.judge_cases), the raw verdicts to the
agent storage scratch folder, and the agreement table to judge_agreement.md beside the page.
"""
import concurrent.futures
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import filing_gate as FG  # noqa: E402
import set_down_judge as SJ  # noqa: E402

PAGE_DIR = os.path.join(REPO, "design", "specs", "2026-11-24-filing-gate")
CASES = os.path.join(PAGE_DIR, "set_down_cases.json")
TABLE = os.path.join(PAGE_DIR, "judge_agreement.md")
REAL_STATE = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
# Danger: 25 calls one after another hold the calibration for about 25 times one call; more at once may meet the
# account's rate of requests. Five at once is the shape guiding_prose's reader has not needed; no rate refusal is on
# record for five.
WORKERS = 5
BIND_TOLERATE = 3   # the Conductor's ruling (brief of 2026-11-25): at most 3 disagreements of 25


def case_id(c):
    return "n%02d" % c["n"]


def scratch_dir():
    try:
        root = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                              capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        root = ""
    if not root:
        raise SystemExit("set_down_calibration: the agent storage root could not be read (agent_storage.py)")
    d = os.path.join(root, "scratch", "set_down_judge_calibration")
    os.makedirs(d, exist_ok=True)
    return d


def judge_case(c):
    sd = {"door": "file", "id": c["id"] or "(no id)", "title": c.get("title") or "", "kind": c.get("kind") or "task",
          "class": c["class"], "evidence": c["evidence"]}
    try:
        rows = FG.refusals_of(c["unit"], REAL_STATE, c["id"])
    except OSError as e:
        rows = [{"at": "?", "why": "could not look: the record of earlier refusals of this run cannot be read (%s)" % e}]
    earlier = [r for r in rows if str(r.get("at") or "") < c["ts"]]
    t0 = time.time()
    v = SJ.judge(sd, c.get("transcript"), earlier, until=c["ts"])
    v["seconds"] = round(time.time() - t0, 1)
    dg, _ = SJ.digest(c.get("transcript"), until=c["ts"]) if c.get("transcript") else (None, "")
    v["digest_chars"] = len(dg or "")
    v["earlier"] = len(earlier)
    return v


def program_of(c):
    """-> "pass" or "refuse": the program half of the gate (filing_gate.decide) on the case, read as the door reads it."""
    own = FG.own_mod_read(FG.own_mod_of(c["unit"]))[0] if c.get("unit") else None
    d = FG.decide(c.get("kind") or "task", c.get("unit") or "u", False, "", "%s: %s" % (c["class"], c["evidence"]),
                  None, lambda m: any(os.path.isdir(os.path.join(REPO, x, m)) for x in ("design/concepts", "src/RimMandrake")),
                  own_mod=own)
    return "pass" if d.ok else "refuse"


def got_of(v):
    return "refuse" if v.get("verdict") == "REFUSED" else "pass"


def table(cases, raw, at):
    rows, wrong = [], []
    for c in cases:
        v = raw[case_id(c)]
        agree = got_of(v) == c["label"]
        if not agree:
            wrong.append(c["n"])
        prog = program_of(c)
        gate = "refuse" if "refuse" in (prog, got_of(v)) else "pass"
        rows.append("| %d | %s | %s%s | %s | %s | %s | %s | %s | %s |" % (
            c["n"], c["class"], c["label"], " (unsure)" if c.get("unsure") else "", v.get("verdict"),
            "yes" if agree else "**no**", prog, gate if gate == c["label"] else "**%s**" % gate,
            str(v.get("missing") or v.get("why") or "").replace("|", "/")[:160], v.get("seconds")))
    n = len(cases)
    secs = [raw[case_id(c)].get("seconds") or 0 for c in cases]
    binds = len(wrong) <= BIND_TOLERATE
    head = ["# The set-down judge on the 25 real set-downs: agreement with the Conductor's classes", "",
            "Run at %s by `python3 src/RimMandrake/rimflow/set_down_calibration.py` (item "
            "`RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS`). The cases and the rebuilt labels are in "
            "`set_down_cases.json` beside this file; each label is a reconstruction from the Conductor's counts, and "
            "`unsure` marks the two that the counts do not fix. A `could not judge` counts as a pass (the door passes "
            "it). The judge binds at most %d disagreements of 25 (the Conductor's ruling)." % (at, BIND_TOLERATE), "",
            "**Measured: %d of %d agree; %d disagree%s.** Longest call: %.0f s; median: %.0f s." % (
                n - len(wrong), n, len(wrong), (" (cases %s)" % ", ".join(map(str, wrong))) if wrong else "",
                max(secs), sorted(secs)[len(secs) // 2]),
            "Within the bind rule: %s." % ("yes" if binds else "no"), "",
            "`program` is filing_gate.decide on the same words (it binds now). `gate` is program and judge together: refuse "
            "when either refuses; in bold where it differs from the Conductor's class.", "",
            "| n | class | Conductor's class | judge | agree | program | gate | the judge's missing part, or why it "
            "could not judge | s |",
            "|---|---|---|---|---|---|---|---|---|"]
    return "\n".join(head + rows) + "\n", wrong


def main(argv):
    with open(CASES, encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    at = time.strftime("%Y-%m-%d %H:%M %Z")
    if argv[:1] == ["--table"]:
        with open(argv[1], encoding="utf-8") as f:
            raw = json.load(f)["verdicts"]
    else:
        with concurrent.futures.ThreadPoolExecutor(WORKERS) as ex:
            got = list(ex.map(judge_case, cases))
        raw = {case_id(c): v for c, v in zip(cases, got)}
        path = os.path.join(scratch_dir(), "run_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"at": at, "verdicts": raw}, f, indent=1)
        print("raw verdicts: %s" % path)
    text, wrong = table(cases, raw, at)
    with open(TABLE, "w", encoding="utf-8") as f:
        f.write(text)
    res = os.environ.get("RM_CALIBRATION_RESULTS")
    if res:
        with open(res, "w", encoding="utf-8") as f:
            json.dump({"cases": [{"id": case_id(c), "expect": c["label"], "got": got_of(raw[case_id(c)])}
                                 for c in cases]}, f)
    cnj = sum(1 for v in raw.values() if v.get("verdict") == "could not judge")
    print("agreement %d of %d; disagree: %s; could not judge: %d" % (len(cases) - len(wrong), len(cases),
                                                                       wrong or "none", cnj))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
