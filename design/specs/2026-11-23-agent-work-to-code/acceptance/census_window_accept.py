#!/usr/bin/env python3
"""Acceptance for the census window, the second part of RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES. All
five small items are measured with it.

Why: the census scripts of 2026-11-23 have a lower time bound and no upper one, write over the baseline's own pickles
in D:\\ClaudeWork\\rimmandrake\\scratch\\a2c, and import role_launch from a clone that is gone (outc.py fails today with
ModuleNotFoundError). So the same command cannot be run again for a later week.

Contract: census/window.py --end <ISO time> [--days 7] --out DIR [--projects DIR]
  It counts turns by the same rules as p3.py, p5.py, p6.py, cond.py, pure.py and pure2.py (move the rules, do not write
  new ones) and writes DIR/rates.json:
    {"window": {"start", "end"}, "status": "value"|"empty"|"could_not_look", "why", "runs", "weighted", "torn_lines",
     "unpriced_models": [..], "counts": {KEY: {"turns", "weighted", "per_100_runs"}}}
  KEYS: help, help_ledger_verbs, show, raw_ledger, wait, wait_repeat, fetch_result, report_after_fetch, wake_reading,
  state_reads, progress_note, lease_renew, wrong_flag, pure_landing, publish_refused, one_test, red_green,
  cache_rebuilt_after_gap.
  runs: transcripts with at least one priced turn in the window. Exit 0 value or empty, 2 could not look or a refused
  --out (a folder that already holds another window's reading or a census pickle is never written over).
Expected when built: PASS 12/12."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

TOOL = os.path.join(H.REPO, "design/specs/2026-11-23-agent-work-to-code/census/window.py")
END = "2026-11-30T20:00:00+00:00"
KEYS = ("help help_ledger_verbs show raw_ledger wait wait_repeat fetch_result report_after_fetch wake_reading state_reads "
        "progress_note lease_renew wrong_flag pure_landing publish_refused one_test red_green cache_rebuilt_after_gap").split()


def turn(ts, cmd, mid, model="claude-opus-5-5", out=100):
    return json.dumps({"type": "assistant", "timestamp": ts, "cwd": "/x", "message": {
        "id": mid, "model": model, "usage": {"input_tokens": 10, "output_tokens": out, "cache_read_input_tokens": 1000},
        "content": [{"type": "tool_use", "id": "t" + mid, "name": "Bash", "input": {"command": cmd}}]}})


IN = "2026-11-28T10:00:0%d.000Z"
BASE = [json.dumps({"type": "user", "message": {"content": "a brief"}}), turn(IN % 0, "ls", "m0"),
        turn(IN % 1, "python3 src/RimMandrake/rimflow/cli.py file --help", "m1", out=101),
        turn(IN % 2, "python3 src/RimMandrake/rimflow/cli.py show ITEM_X | tail -5", "m2", out=102)]


def run(files, out=None, projects=None):
    if not os.path.isfile(TOOL):
        raise RuntimeError("no file census/window.py")
    d = projects
    if d is None:
        d = tempfile.mkdtemp()
        for i, lines in enumerate(files):
            sub = os.path.join(d, "-home-rm-clones-ITEM-%d-det" % i)
            os.makedirs(sub)
            p = os.path.join(sub, "s%d.jsonl" % i)
            with open(p, "w") as f:
                f.write("\n".join(lines) + "\n")
    out = out or os.path.join(tempfile.mkdtemp(), "o")
    r = subprocess.run([sys.executable, TOOL, "--end", END, "--days", "7", "--out", out, "--projects", d],
                       capture_output=True, text=True, timeout=120, cwd=H.REPO)
    p = os.path.join(out, "rates.json")
    return r.returncode, (json.load(open(p)) if os.path.isfile(p) else None), out, r.stdout + r.stderr


def c(files, key):
    return run(files)[1]["counts"][key]


H.check("it counts a help turn and a show turn inside the window", lambda: c([BASE], "help")["turns"] == 1
        and c([BASE], "help_ledger_verbs")["turns"] == 1 and c([BASE], "show")["turns"] == 1)
H.check("every key is there, and a measured zero is 0", lambda: sorted(run([BASE])[1]["counts"]) == sorted(KEYS)
        and c([BASE], "lease_renew")["turns"] == 0)
H.check("a turn after the window's end is not counted", lambda: c(
    [BASE + [turn("2026-12-01T00:00:00.000Z", "x.py --help", "m9", out=109)]], "help")["turns"] == 1)
H.check("a turn before the window's start is not counted", lambda: c(
    [BASE + [turn("2026-11-20T00:00:00.000Z", "x.py --help", "m8", out=108)]], "help")["turns"] == 1)
H.check("a turn that a resumed session repeats is counted once", lambda: c([BASE, BASE], "help")["turns"] == 1)
H.check("the rate is per 100 runs", lambda: c([BASE, [BASE[0], turn(IN % 5, "ls", "k0", out=55)]], "help")["per_100_runs"] == 50)
H.check("torn: a half line is counted as torn, and the rest is read", lambda: (
    lambda r: r["torn_lines"] == 1 and r["counts"]["help"]["turns"] == 1)(run([BASE + ['{"type": "assistant", "mess']])[1]))
H.check("a model with no price is named, never counted as zero cost", lambda: run(
    [BASE + [turn(IN % 6, "ls", "m6", model="claude-nobody-9")]])[1]["unpriced_models"] == ["claude-nobody-9"])
H.check("empty: no turns in the window reads empty, exit 0", lambda: (
    lambda r: r[0] == 0 and r[1]["status"] == "empty")(run([[BASE[0]]])))
H.check("missing: no projects folder reads could not look, exit 2", lambda: (
    lambda r: r[0] == 2 and "could not look" in r[3].lower())(run([], projects="/no/such/folder")))


def keeps():
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "scan3.pkl"), "wb") as f:
        f.write(b"baseline")
    rc = run([BASE], out=d)[0]
    return rc == 2 and open(os.path.join(d, "scan3.pkl"), "rb").read() == b"baseline" and os.listdir(d) == ["scan3.pkl"]


H.check("it never writes over the baseline's folder", keeps)
H.check("weighted tokens come from MODEL_PRICES (0 < weighted, and no list price is printed)", lambda: (
    lambda r: r[1]["weighted"] > 0 and "$" not in r[3])(run([BASE])))
H.done(12)
