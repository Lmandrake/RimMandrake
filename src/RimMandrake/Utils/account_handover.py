#!/usr/bin/env python3
"""account_handover.py - one account change-over at a named line, once, then it stops itself.

Owner 2026-11-03: "at 1% please changeover to steven. He has authorized using another 20% of his account." A systemd
user timer runs `check`, one per change-over; a later link in a chain idles until its FROM is live.
Arm that timer with the script from the Operations deploy (/home/mandrake/rm/dispatch, systemd/ops_clocks.json), never
a seat clone, whose code moves under it.

    account_handover.py check --from lukas --to system --at 1 [--until 2026-11-04T13:59-08:00] [--dry-run]
    account_handover.py retire --from steven --to system --why "..." [--unit rm-account-handover-steven.timer]

A link is an allowance, and an allowance ends (STEVEN_LINK_ENFORCE_TWENTY_ENDS_AT_RESET: a one-week 20% grant armed
with no end). `--until` makes a link past that moment log `expired` and never switch; `retire` logs the change and
stops the link's timer (default unit rm-account-handover-<from>.timer). Every log row names from/to.

Switches only while FROM is the live account. An exhausted account often cannot be read, so a last good reading within
NEAR of the line that then goes stale or unmeasured counts as past the line. Marker and log: account_handover/ under the
RimMandrake agent storage. `claude-account use` closes every Claude window here and relaunches the Fleet. No AI.
"""
import shutil
import argparse
import datetime
import json
import os
import subprocess
import sys

CLAUDE_ACCOUNT = shutil.which("claude-account") or os.path.expanduser("~/.local/bin/claude-account")  # systemd's PATH lacks ~/.local/bin (OPS_TIMER_REPAIR_PRXC)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/d/ClaudeWork/rimmandrake/account_handover"
NEAR = 1.0


def decide(live, reading, last_good, frm, at):
    """-> (act, why). Pure. `reading` is the meter's row for FROM; `last_good` its last MEASURED figure, or None."""
    if live != frm:
        return "idle", "%s is not live (live: %s)" % (frm, live)
    seen = reading and reading.get("source") == "MEASURED" and not reading.get("stale")
    if seen and reading.get("week_pct_left") is not None:
        left = reading["week_pct_left"]
        return ("switch", "%s MEASURED %s%% left, line %s%%" % (frm, left, at)) if left <= at else (
            "wait", "%s MEASURED %s%% left" % (frm, left))
    if last_good is not None and last_good <= at + NEAR:
        return "switch", "%s unreadable after %s%% left: counted as past the line" % (frm, last_good)
    return "wait", "%s unreadable, last good %s" % (frm, last_good)


def expired(until, now):
    """True when `until` (ISO with offset, or None) is at or before `now` (aware datetime). Pure."""
    if not until:
        return False
    t = datetime.datetime.fromisoformat(until)
    if t.tzinfo is None:
        raise SystemExit("--until needs a UTC offset: %s" % until)
    return now >= t


def sh(*cmd, timeout=240):
    # systemd-run units start with a bare PATH that lacks ~/.local/bin (where claude-account lives)
    env = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + os.pathsep + os.environ.get("PATH", ""))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)


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
    p.add_argument("verb", choices=["check", "retire"])
    p.add_argument("--from", dest="frm", required=True)
    p.add_argument("--to", required=True)
    p.add_argument("--at", type=float)
    p.add_argument("--until", help="ISO time with offset; at or after it the link logs expired and never switches")
    p.add_argument("--why", help="retire: why the link ends")
    p.add_argument("--unit", help="retire: the timer to stop (default rm-account-handover-<from>.timer)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    link = {"from": a.frm, "to": a.to}
    if a.verb == "retire":
        if not a.why:
            p.error("retire needs --why")
        unit = a.unit or "rm-account-handover-%s.timer" % a.frm
        r = sh("systemctl", "--user", "stop", unit, timeout=60) if not a.dry_run else None
        log(dict(act="retired", **link, unit=unit, why=a.why, rc=None if r is None else r.returncode,
                 at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), dry_run=a.dry_run))
        return 0 if r is None or r.returncode == 0 else 1
    if a.at is None:
        p.error("check needs --at")
    if expired(a.until, datetime.datetime.now().astimezone()):
        log(dict(act="expired", **link, why="link ended at %s" % a.until, dry_run=a.dry_run))
        return 0
    marker = os.path.join(OUT, "%s_to_%s.done" % (a.frm, a.to))
    if os.path.exists(marker):
        return 0
    live = json.loads(sh(CLAUDE_ACCOUNT, "--json", "status").stdout)["live"]
    rows = meter()
    row = rows.get(a.frm)
    if live == a.frm and row and row.get("week_pct_left") is not None and row["week_pct_left"] <= a.at + 2 * NEAR and not a.dry_run:
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
    act, why = decide(live, row, last_good, a.frm, a.at)
    log(dict(ts=(row or {}).get("ts"), act=act, **link, why=why, dry_run=a.dry_run))
    if act != "switch" or a.dry_run:
        return 0
    with open("/mnt/d/ClaudeWork/rimmandrake/conductor/log.md", "a", encoding="utf-8") as f:
        f.write("\n- ACCOUNT CHANGE-OVER %s -> %s: %s. Windows relaunch now.\n" % (a.frm, a.to, why))
    host = sh("hostname").stdout.strip().lower()
    sh(CLAUDE_ACCOUNT, "arm", "--confirm", host)
    r = sh(CLAUDE_ACCOUNT, "use", a.to, "--confirm", host, timeout=600)
    log(dict(act="switched", **link, rc=r.returncode, out=(r.stdout + r.stderr)[-400:]))
    if r.returncode:
        return 1        # no marker: the next tick tries again
    open(marker, "w", encoding="utf-8").close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
