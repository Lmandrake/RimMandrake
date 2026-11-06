#!/usr/bin/env python3
"""live_log_check.py -- does the RUNNING game's Player.log name a token in an error line? Read-only, no bridge call.

    python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_ExplosiveGrowthRoster --absent RUT_PaleMoss [--warnings]

For criteria worded "Player.log carries no error naming X" (RA_S09_LIVE_WIRE_ONE_REAL_LEAF). A line is an error line when
it matches ERROR_RE (with --warnings, WARN_RE too); a token is matched as a literal substring of such a line.

--never TOKEN fails on ANY line naming the token, error word or not. Player.log carries no level marker: a Log.Warning
is bare text (stack traces are off), so a warning without the word "warn" in it is invisible to --warnings. Name such a
message by its own text with --never ("[RM Minerals] quarry", "name only disabled mineables").

Exit 0 no error line names any token, 1 one does (a real FAIL; the lines are printed), 2 UNMEASURED: no running game,
a log older than the running game (it belongs to an earlier session), or a log without the anchor (default
"Bridge token:", printed once the load finished and RimBridge came up: a log before that has not seen the load's
errors yet). Pair it with live_def_check.py when the criterion also needs the mod to be loaded: an absent token in a
load that never had the mod is not a pass, and this file cannot tell.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL, UNMEASURED = 0, 1, 2
# Word-ended so an identifier is not an error: RUT_ErrorPlant and "0 errors" are not error lines, NullReferenceException,
# "2 errors" and "Config error in" are. The tokens and every underscore identifier are blanked out first (MASK_RE).
ERROR_RE = re.compile(r"errors?\b|exceptions?\b|\bfailed\b|\bcould not\b|\bcouldn't\b", re.I)
WARN_RE = re.compile(r"warn(ing)?s?\b", re.I)
NONE_RE = re.compile(r"\b(0|no|zero|without)\s+(errors?|exceptions?|warnings?)\b", re.I)
IDENT_RE = re.compile(r"\w*_\w*")
# A line that continues the record above it (a stack trace, an inner exception, a [Ref] stub), not a message of its
# own. Blank lines never split a record: "Exception:\n\n  defName: X" is one record. A failed patch prints its file on
# the next line, unindented ("file: C:\\...\\Patches\\X.xml"): without `file: ` a token naming the patch file was missed.
CONT_RE = re.compile(r"^(\s|at |file: |\(Filename|--- |Rethrow|\[0x|\[Ref |(Verse|RimWorld|UnityEngine|System|HarmonyLib|Mono)\.\S*[:(])")
ANCHOR = "Bridge token:"


def records(text):
    """-> [(first line number, [lines])]: a message line plus the continuation lines under it."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if out and CONT_RE.match(line):
            out[-1][1].append(line)
        else:
            out.append((n, [line]))
    return out


def judge(text, tokens, warnings=False, anchor=ANCHOR, never=()):
    """-> (exit code, lines). Pure: `text` is the whole Player.log. A record (a message and its stack trace) fails when
    any of its lines is an error line (with `warnings`, a warning line too) and any of its lines names a token, as a
    literal substring: RUT_PaleMoss also hits RUT_PaleMossLarge, a false FAIL at worst, never a false PASS."""
    if anchor and anchor not in text:
        return UNMEASURED, ["UNMEASURED: the log has no %r yet: the load has not finished" % anchor]
    hits, recs = [], records(text)
    for n, lines in recs:
        named = [t for t in never if any(t in x for x in lines)]
        if named:
            hits.append("FAIL line %d names %s, which may never appear: %s" % (n, ", ".join(named),
                                                                              " | ".join(x.strip() for x in lines)[:240]))
    mask = re.compile("|".join(re.escape(t) for t in sorted(tokens, key=len, reverse=True)))

    def bad(line):
        line = NONE_RE.sub(" ", IDENT_RE.sub(" ", mask.sub(" ", line)))
        return ERROR_RE.search(line) or (warnings and WARN_RE.search(line))

    for n, lines in recs if tokens else ():
        named = [t for t in tokens if any(t in x for x in lines)]
        if named and any(bad(x) for x in lines):
            hits.append("FAIL line %d names %s: %s" % (n, ", ".join(named), " | ".join(x.strip() for x in lines)[:240]))
    if hits:
        return FAIL, hits[:40] + (["... %d more" % (len(hits) - 40)] if len(hits) > 40 else [])
    return PASS, (["PASS no %s line names %s" % ("error or warning" if warnings else "error", ", ".join(tokens))] if tokens
                  else []) + (["PASS no line names %s" % ", ".join(never)] if never else [])


def game_started():
    """The running RimWorld's start, epoch seconds to the millisecond; None when none or two run, or it cannot be read."""
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            "Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | ForEach-Object "
                            "{ $_.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ') }"],
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        lines = [x.strip() for x in r.stdout.splitlines() if x.strip()]
        if len(lines) != 1:
            return None
        return datetime.datetime.strptime(lines[0], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=datetime.timezone.utc).timestamp()
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


RECHECK_TRIES = 3
RECHECK_PAUSE = 2.0


def same_game(started, probe=None, tries=RECHECK_TRIES, pause=RECHECK_PAUSE, sleep=time.sleep):
    """-> None when the game that started at `started` still runs, else the reason it cannot be said.

    The post-read recheck. game_started() answers None for an unreadable process list (a powershell.exe hiccup) as
    well as for no game, so a lone None is re-asked, never taken as a change
    (GAMEENV_FIX_PROOFSITE_B7C18A7D_ITEMS_WAIT: one such None read as "the running game changed")."""
    probe = probe or game_started
    now = None
    for i in range(max(1, tries)):
        now = probe()
        if now is not None:
            break
        if i + 1 < tries:
            sleep(pause)
    if now is None:
        return "the running game's start could not be re-read after the log was read (%d tries)" % max(1, tries)
    if now != started:
        return "the running game changed while the log was read"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--absent", action="append", default=[], metavar="TOKEN")
    ap.add_argument("--never", action="append", default=[], metavar="TOKEN",
                    help="any line naming this fails, error word or not (a Log.Warning has no marker in Player.log)")
    ap.add_argument("--warnings", action="store_true", help="a warning line naming a token fails too")
    ap.add_argument("--log", default=None, help="another log (default: game_paths.PLAYER_LOG); skips the game check")
    a = ap.parse_args(argv)
    tokens = [t for t in (x.strip() for x in a.absent) if t]
    never = [t for t in (x.strip() for x in a.never) if t]
    if not tokens and not never:
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
            if os.path.getmtime(path) <= started:
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
    if a.log is None:
        why = same_game(started)
        if why:
            print("UNMEASURED: " + why)
            return UNMEASURED
    code, lines = judge(text, tokens, a.warnings, never=never)
    print("\n".join(lines))
    print({PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code])
    return code


def safe_main(argv=None):
    """main(), where nothing may escape: an uncaught exception exits 1, which the runner would record as a FAIL."""
    try:
        return main(argv)
    except SystemExit:
        raise
    except BaseException as e:
        sys.stdout.write("UNMEASURED: " + ascii("%s: %s" % (type(e).__name__, str(e)[:200])) + "\n")
        return UNMEASURED


if __name__ == "__main__":
    sys.exit(safe_main())
