#!/usr/bin/env python3
"""why_sample.py: why a Conductor window reads a run's out.json by hand after a run-end wake (run_result_why.md).

Run on the machine that holds the Conductor transcripts (Archmagi), after extract.py:
    cd design/specs/2026-11-26-script-candidates/measure
    SCAN_DAYS=9 SCAN_DIR=<scratch dir> python3 -I extract.py    # SCAN_DAYS: sessions changed in that many days
    SCAN_DIR=<scratch dir> python3 -I why_sample.py [--n 20] [--seed 1126] [--tx-dir <dir>] > <scratch>/why.txt

What it does:
  1. Takes the hand reads of rows.py's EXTRA section (inline python on *.out.json that reads 'result'): the same filter.
  2. Gives EVERY hand read a mechanical class from the transcript (MECH below) and prints the counts over all of them.
  3. Samples --n of them: the reads sorted by time, cut into --n bins of equal count, one read per bin drawn with
     --seed, a window not yet drawn preferred. For each it prints the transcript path, the line of the turn before the
     call and of the call, what that turn held, the window's own words between them, and the command. The page's
     class for a sampled read is a person's reading of that print; MECH is only where to start.

MECH (first match wins):
  wake_without_result   the turn before is a run-end wake with no "whole last message" (code before c45e242f32,
                        2026-11-23 9:31 PM PST, or a wake that failed to render the result)
  not_after_wake        the turn before the call is not a run-end wake (owner words, restart, task notice, other)
  after_compaction      a compaction boundary lies between that wake and the call
  other_run             the wake carried results, but no unit the command reads is in this wake or an earlier one of
                        the window
  extra_fields          the command reads a field the wake does not carry (cost, turns, session id, duration, usage)
  read_again            the wake carried this run's whole last message and nothing above applies: re-check or habit,
                        told apart only by reading the window's words
  unknown_unit          the command names no unit (a glob or a variable): read by hand
"""
import argparse
import collections
import glob
import json
import os
import random
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import calls, turns, bcmd  # noqa: E402

CARRY_SHA_TS = datetime(2026, 11, 24, 5, 31, tzinfo=timezone.utc).timestamp()   # c45e242f32, 2026-11-23 9:31 PM PST
EXTRA_FIELDS = re.compile(r"total_cost_usd|cost_usd|num_turns|session_id|duration_ms|duration_api_ms|usage|stopped_by|"
                          r"modelUsage|permission_denials")
RUN_ID = re.compile(r"\b(rm-detached-[a-z0-9-]+-\d{10})\b")  # a loop names its runs bare: "for u in rm-detached-...; do"
UNIT_IN_CMD = re.compile(r"([A-Za-z0-9_.-]+?)\.out\.json")
UNIT_IN_WAKE = re.compile(r"^(?:-----|-) (\S+) ended ", re.M)


def hand_reads():
    """The filter of rows.py (EXTRA section), unchanged."""
    return [c for c in calls if c["name"] == "Bash" and re.search(r"python3?[^\n]*(-c|<<|-\s)", bcmd(c))
            and ".out.json" in bcmd(c) and re.search(r"\['result'\]|get\('result'|\.result|\"result\"", bcmd(c))]


def pst(ts):
    import zoneinfo
    return datetime.fromtimestamp(ts, zoneinfo.ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M")


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def load_tx(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            try:
                rows.append((n, json.loads(line)))
            except ValueError:
                continue
    return rows


def is_turn(d):
    """The same turn test as extract.py: a user record with promptId/turnOrigin and text."""
    if d.get("type") != "user" or not (d.get("promptId") or d.get("turnOrigin")):
        return False
    c = d.get("message", {}).get("content")
    return isinstance(c, str) or (isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "text" for b in c))


def queued_text(d):
    """A wake that comes while the window is busy is not a user turn: the harness gives it to the model as an
    attachment of type queued_command (measured: 2c5e1f2d line 666, 2026-11-22). -> its prompt text, or ''."""
    a = d.get("attachment") if d.get("type") == "attachment" else None
    if isinstance(a, dict) and a.get("type") == "queued_command":
        p = a.get("prompt")
        return p if isinstance(p, str) else text_of(p)
    return ""


def delivery_text(d):
    """The text of a turn, or of a queued wake attachment; None when the record is neither."""
    if is_turn(d) and not d.get("isCompactSummary"):
        return text_of(d.get("message", {}).get("content"))
    q = queued_text(d)
    return q if q and is_wake(q) else None


def is_wake(txt):
    return "Stop hook feedback" in txt and "run_end_wake" in txt


def is_compaction(d):
    return (d.get("type") == "system" and d.get("subtype") == "compact_boundary") or bool(d.get("isCompactSummary"))


def examine(c, rows, path):
    """-> one dict: the call's line, the turn before it, the window's words between, and its MECH class."""
    cmd = bcmd(c)
    at = None
    for i, (n, d) in enumerate(rows):
        if d.get("type") == "assistant" and d.get("timestamp") == c["ts"]:
            for b in d.get("message", {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and (b.get("input") or {}).get("command", "")[:4000] == cmd:
                    at = i
    if at is None:
        return {"path": path, "call_line": None, "mech": "call_not_found", "cmd": cmd[:600]}
    turn_i = next((j for j in range(at, -1, -1) if delivery_text(rows[j][1]) is not None), None)
    words, compacted = [], False
    for j in range((turn_i or 0) + 1, at + 1):
        d = rows[j][1]
        compacted = compacted or is_compaction(d)
        if d.get("type") == "assistant":
            for b in d.get("message", {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") in ("text", "thinking") and (b.get("text") or b.get("thinking")):
                    words.append("[%d %s] %s" % (rows[j][0], b["type"], (b.get("text") or b.get("thinking")).strip()))
    turn_txt = delivery_text(rows[turn_i][1]) if turn_i is not None else ""
    units = sorted((set(UNIT_IN_CMD.findall(cmd)) | set(RUN_ID.findall(cmd))) - {""})
    units = [u for u in units if "*" not in u and "$" not in u and "{" not in u]
    wake_units = set(UNIT_IN_WAKE.findall(turn_txt))
    earlier_carried = set()
    for j in range(0, turn_i or 0):
        d = rows[j][1]
        t = delivery_text(d)
        if t:
            if is_wake(t) and "whole last message" in t:
                earlier_carried |= set(UNIT_IN_WAKE.findall(t))
    carried = is_wake(turn_txt) and "whole last message" in turn_txt
    in_this = [u for u in units if u in wake_units]
    if not is_wake(turn_txt):
        mech = "not_after_wake"
    elif not carried:
        mech = "wake_without_result"
    elif compacted:
        mech = "after_compaction"
    elif not units:
        mech = "unknown_unit"
    elif not in_this and not (set(units) & earlier_carried):
        mech = "other_run"
    elif EXTRA_FIELDS.search(cmd):
        mech = "extra_fields"
    else:
        mech = "read_again"
    return {"path": path, "call_line": rows[at][0], "turn_line": rows[turn_i][0] if turn_i is not None else None,
            "turn_kind": "wake" if is_wake(turn_txt) else "other", "turn_chars": len(turn_txt),
            "turn_carried_result": carried, "turn_units": sorted(wake_units), "cmd_units": units,
            "cmd_in_this_wake": in_this, "cmd_extra_fields": sorted(set(EXTRA_FIELDS.findall(cmd))),
            "compaction_between": compacted, "before_carry_sha": c["t"] < CARRY_SHA_TS, "mech": mech,
            "turn_head": turn_txt[:500], "words": words, "cmd": cmd[:1500]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1126)
    ap.add_argument("--tx-dir", default=os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench"))
    ap.add_argument("--json", help="write every examined read here, one JSON per line")
    ap.add_argument("--from-utc", default="2026-11-20T01:46:00+00:00",
                    help="first call time read (default: the 7 days of one_page.md, 2026-11-19 5:46 PM PST)")
    ap.add_argument("--to-utc", default="2026-11-27T01:46:00+00:00", help="last call time read (2026-11-26 5:46 PM PST)")
    a = ap.parse_args(argv)
    lo_t, hi_t = (datetime.fromisoformat(x).timestamp() for x in (a.from_utc, a.to_utc))
    rr = sorted((c for c in hand_reads() if lo_t <= c["t"] <= hi_t), key=lambda c: c["t"])
    txs = {}
    for f in glob.glob(os.path.join(a.tx_dir, "*.jsonl")):
        txs.setdefault(os.path.basename(f)[:8], f)
    cache, out = {}, []
    for c in rr:
        path = txs.get(c["sid"])
        if not path:
            out.append((c, {"path": None, "mech": "no_transcript"}))
            continue
        if path not in cache:
            cache = {path: load_tx(path)}            # one transcript in memory at a time; rr is time-sorted
        out.append((c, examine(c, cache[path], path)))
    print("hand reads read: %d | windows: %d | first %s | last %s | before c45e242f32: %d" % (
        len(rr), len(set(c["sid"] for c in rr)), pst(rr[0]["t"]) if rr else "-", pst(rr[-1]["t"]) if rr else "-",
        sum(1 for c in rr if c["t"] < CARRY_SHA_TS)))
    tally = collections.Counter(e["mech"] for _, e in out)
    tally_after = collections.Counter(e["mech"] for c, e in out if c["t"] >= CARRY_SHA_TS)
    print("MECH over all:", dict(tally.most_common()))
    print("MECH after c45e242f32:", dict(tally_after.most_common()))
    if a.json:
        with open(a.json, "w") as f:
            for c, e in out:
                f.write(json.dumps(dict(e, ts=c["ts"], sid=c["sid"])) + "\n")
    rng = random.Random(a.seed)
    picks, used = [], set()
    n = min(a.n, len(out))
    for k in range(n):
        lo, hi = k * len(out) // n, (k + 1) * len(out) // n
        bin_ = out[lo:hi]
        fresh = [x for x in bin_ if x[0]["sid"] not in used] or bin_
        pick = rng.choice(fresh)
        used.add(pick[0]["sid"])
        picks.append(pick)
    print("sample: %d reads, %d windows, %d days" % (len(picks), len(set(c["sid"] for c, _ in picks)),
                                                     len(set(pst(c["t"])[:10] for c, _ in picks))))
    for k, (c, e) in enumerate(picks, 1):
        print("\n##### %d  %s PST  window %s  mech %s" % (k, pst(c["t"]), c["sid"], e["mech"]))
        print("transcript %s  turn line %s  call line %s" % (e.get("path"), e.get("turn_line"), e.get("call_line")))
        for key in ("turn_kind", "turn_chars", "turn_carried_result", "turn_units", "cmd_units", "cmd_in_this_wake",
                    "cmd_extra_fields", "compaction_between", "before_carry_sha"):
            if key in e:
                print("  %s: %s" % (key, e[key]))
        print("  TURN HEAD: %s" % (e.get("turn_head") or "").replace("\n", " | "))
        for w in e.get("words", [])[-6:]:
            print("  WORDS %s" % w[:700].replace("\n", " | "))
        print("  CMD: %s" % (e.get("cmd") or c["inp"].get("command", ""))[:1200].replace("\n", " | "))
    return 0


if __name__ == "__main__":
    sys.exit(main())
