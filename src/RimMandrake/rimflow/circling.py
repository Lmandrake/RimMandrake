#!/usr/bin/env python3
"""circling.py -- the tool-call classifier pulse/time_ledger reads (classify, _ts): a tool call's kind (selftest, live, build,
waiting, editing, reading, report, other) and what it looked at.

The circling watch that judged a running Relentless worker from these kinds and its clone (watch, judge, replay, the stop
gate) was called only by the retired tick and went on 2026-11-18 (RIMMANDRAKE_RETIRE_CIRCLING_WATCH_ONLY_THE_DEAD_TICK_CALLED);
git keeps it. The thresholds time_ledger still reads are run_rules.json `circling`.
"""
import datetime
import json
import re


# anchored on what a shell segment RUNS: a grep of a selftest file is reading, a heredoc writing one is editing
TEST_RX = re.compile(r"((python3?|bash|sh)\s+)?\S*(run_selftests\.py|selftest_\w+\.py)|pytest\b|python3? -m (pytest|unittest)\b")
LIVE_RX = re.compile(r"(\./game|\./bridge|modcheck)\b|((python3?)\s+)?\S*(proof_\w+|validation\w*)\.py")
BUILD_RX = re.compile(r"((python3?)\s+)?\S*(winbuild|deploy_custom_mods)\.py|dotnet\b|msbuild\b|\./publish\b")
WAIT_RX = re.compile(r"(sleep|waitfor)\b")
EDIT_RX = re.compile(r"sed\s+-i|git\s+(commit|add)\b|(cat|echo|printf|tee)\b.*>\s*[\w./~-]+")
READ_RX = re.compile(r"(grep|rg|cat|head|tail|sed|awk|ls|find|wc|diff|jq|git\s+(-C\s+\S+\s+)?(log|show|diff|grep|blame|status))\b")
REPORT_RX = re.compile(r"\brelentless\.py\b")    # a worker's beat and learn lines: every run writes them
HEREDOC_RX = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", re.S)
PREFIX_RX = re.compile(r"^(\s*(timeout\s+\S+|\w+=\S*|cd\s+\S+|set\s+-o\s+\w+)\s+)+")
WRITE_RX = re.compile(r"open\([^)]*['\"][wax]b?\+?['\"]|(?<!stdout)(?<!stderr)\.write(_text|_bytes|lines)?\(|json\.dump\(|os\.replace\(|shutil\.")


def classify(name, inp):
    """-> (kind, target). RW1's six kinds; `target` names what was looked at or run, None when it says nothing."""
    inp = inp if isinstance(inp, dict) else {}
    if name in ("Edit", "Write", "NotebookEdit"):
        return "editing", None
    if name == "Read":
        return "reading", "read:%s:%s" % (inp.get("file_path"), inp.get("offset") or 0)
    if name in ("Grep", "Glob", "WebFetch", "WebSearch", "ToolSearch") or str(name).startswith("mcp__"):
        return "other" if str(name).startswith("mcp__") else "reading", "%s:%s" % (name, json.dumps(inp, sort_keys=True, default=str))
    if name != "Bash":
        return "other", None
    cmd = str(inp.get("command") or "")
    segs = [PREFIX_RX.sub("", x.strip()) for x in re.split(r"[;&|\n]+", HEREDOC_RX.sub("", cmd))]
    target = " ".join(cmd.split())
    for kind, rx in (("selftest", TEST_RX), ("live", LIVE_RX), ("build", BUILD_RX), ("waiting", WAIT_RX),
                     ("editing", EDIT_RX)):
        if any(rx.match(x) for x in segs):
            return kind, None if kind == "editing" else target
    if "<<" in cmd:     # a script: it says what it looked at unless its body writes
        return ("editing", None) if WRITE_RX.search(cmd) else ("other", target)
    if any(READ_RX.match(x) for x in segs):
        return "reading", target
    return "other", None if REPORT_RX.search(cmd) else target


def _ts(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None

