#!/usr/bin/env python3
"""account_handover.py - one account change-over at a named line, once, then it stops itself.

Owner 2026-11-03: "at 1% lukas, please trigger a change-over to system". A systemd user timer runs `check`.

    account_handover.py check --from lukas --to system --at 1 [--dry-run]

Switches only while FROM is the live account. An exhausted account often cannot be read, so a last good reading at or
under NEAR that then goes stale or unmeasured counts as past the line. Marker and log: account_handover/ under the
RimMandrake agent storage. `claude-account use` closes every Claude window here and relaunches the Fleet. No AI.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/d/ClaudeWork/rimmandrake/account_handover"
NEAR = 2.0


def decide(live, reading, last_good, frm, at):
    """-> (act, why). Pure. `reading` is the meter's row for FROM; `last_good` its last MEASURED figure, or None."""
    if live != frm:
        return "done", "%s is not live (live: %s)" % (frm, live)
    seen = reading and reading.get("source") == "MEASURED" and not reading.get("stale")
    if seen and reading.get("week_pct_left") is not None:
        left = reading["week_pct_left"]
        return ("switch", "%s MEASURED %s%% left, line %s%%" % (frm, left, at)) if left <= at else (
            "wait", "%s MEASURED %s%% left" % (frm, left))
    if last_good is not None and last_good <= NEAR:
        return "switch", "%s unreadable after %s%% left: counted as past the line" % (frm, last_good)
    return "wait", "%s unreadable, last good %s" % (frm, last_good)


def sh(*cmd, timeout=240):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def log(row):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps(row))


def meter():
    r = sh(sys.executable, os.path.join(HERE, "account_usage.py"), "now", "--json")
    return json.loads(r.stdout)["accounts"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("verb", choices=["check"])
    p.add_argument("--from", dest="frm", required=True)
    p.add_argument("--to", required=True)
    p.add_argument("--at", type=float, required=True)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    marker = os.path.join(OUT, "%s_to_%s.done" % (a.frm, a.to))
    if os.path.exists(marker):
        return 0
    rows = meter()
    row = rows.get(a.frm)
    if row and row.get("week_pct_left") is not None and row["week_pct_left"] <= NEAR + 1 and not a.dry_run:
        sh(sys.executable, os.path.join(HERE, "account_usage.py"), "poll", timeout=200)     # near the line: read it fresh
        rows = meter()
        row = rows.get(a.frm)
    good_path = os.path.join(OUT, "%s_last_good.json" % a.frm)
    last_good = None
    if os.path.exists(good_path):
        last_good = json.load(open(good_path, encoding="utf-8"))["left"]
    if row and row.get("source") == "MEASURED" and not row.get("stale") and row.get("week_pct_left") is not None:
        last_good = row["week_pct_left"]
        os.makedirs(OUT, exist_ok=True)
        json.dump({"left": last_good}, open(good_path, "w", encoding="utf-8"))
    live = json.loads(sh("claude-account", "--json", "status").stdout)["live"]
    act, why = decide(live, row, last_good, a.frm, a.at)
    log({"ts": (row or {}).get("ts"), "act": act, "why": why, "dry_run": a.dry_run})
    if act == "wait" or a.dry_run:
        return 0
    if act == "switch":
        with open("/mnt/d/ClaudeWork/rimmandrake/conductor/log.md", "a", encoding="utf-8") as f:
            f.write("\n- ACCOUNT CHANGE-OVER %s -> %s: %s. Windows relaunch now.\n" % (a.frm, a.to, why))
        host = sh("hostname").stdout.strip().lower()
        sh("claude-account", "arm", "--confirm", host)
        r = sh("claude-account", "use", a.to, "--confirm", host, timeout=600)
        log({"act": "switched", "rc": r.returncode, "out": (r.stdout + r.stderr)[-400:]})
        if r.returncode:
            return 1        # no marker: the next tick tries again
    open(marker, "w", encoding="utf-8").close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
