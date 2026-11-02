#!/usr/bin/env python3
"""live_log_check.py -- does the RUNNING game's Player.log name a token in an error line? Read-only, no bridge call.

    python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_ExplosiveGrowthRoster --absent RUT_PaleMoss [--warnings]

For criteria worded "Player.log carries no error naming X" (RA_S09_LIVE_WIRE_ONE_REAL_LEAF). A line is an error line when
it matches ERROR_RE (with --warnings, WARN_RE too); a token is matched as a literal substring of such a line.

Exit 0 no error line names any token, 1 one does (a real FAIL; the lines are printed), 2 UNMEASURED: no running game,
a log older than the running game (it belongs to an earlier session), or a log without the anchor (default
"Bridge token:", printed once the load finished and RimBridge came up: a log before that has not seen the load's
errors yet). Pair it with live_def_check.py when the criterion also needs the mod to be loaded: an absent token in a
load that never had the mod is not a pass, and this file cannot tell.
"""
import argparse
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL, UNMEASURED = 0, 1, 2
ERROR_RE = re.compile(r"error|exception|failed|could not|couldn't", re.I)
WARN_RE = re.compile(r"warn", re.I)
ANCHOR = "Bridge token:"


def judge(text, tokens, warnings=False, anchor=ANCHOR):
    """-> (exit code, lines). Pure: `text` is the whole Player.log."""
    if anchor and anchor not in text:
        return UNMEASURED, ["UNMEASURED: the log has no %r yet: the load has not finished" % anchor]
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if not (ERROR_RE.search(line) or (warnings and WARN_RE.search(line))):
            continue
        for t in tokens:
            if t in line:
                hits.append("FAIL line %d names %s: %s" % (n, t, line.strip()[:240]))
    if hits:
        return FAIL, hits[:40] + (["... %d more" % (len(hits) - 40)] if len(hits) > 40 else [])
    return PASS, ["PASS no %s line names %s" % ("error or warning" if warnings else "error", ", ".join(tokens))]


def game_started():
    """The running RimWorld's start, epoch seconds; None when none runs or it cannot be read."""
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            "(Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1)"
                            ".StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')"],
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return time.mktime(time.strptime(r.stdout.strip(), "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--absent", action="append", required=True, metavar="TOKEN")
    ap.add_argument("--warnings", action="store_true", help="a warning line naming a token fails too")
    ap.add_argument("--log", default=None, help="another log (default: game_paths.PLAYER_LOG); skips the game check")
    a = ap.parse_args(argv)
    tokens = [t for t in (x.strip() for x in a.absent) if t]
    if not tokens:
        print("UNMEASURED: no token to look for")
        return UNMEASURED
    path = a.log
    if path is None:
        sys.path.insert(0, HERE)
        from game_paths import PLAYER_LOG as path
        started = game_started()
        if started is None:
            print("UNMEASURED: no running game")
            return UNMEASURED
        try:
            if os.path.getmtime(path) < started:
                print("UNMEASURED: %s was last written before the running game started" % path)
                return UNMEASURED
        except OSError as e:
            print("UNMEASURED: %s" % e)
            return UNMEASURED
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        print("UNMEASURED: %s" % e)
        return UNMEASURED
    code, lines = judge(text, tokens, a.warnings)
    print("\n".join(lines))
    print({PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code])
    return code


if __name__ == "__main__":
    sys.exit(main())
