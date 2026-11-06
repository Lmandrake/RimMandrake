#!/usr/bin/env python3
"""nulltex_log_check.py -- read the NullTexTrace mod's lines out of the RUNNING game's Player.log. No bridge call.

    python3 src/RimMandrake/NullTexTrace/nulltex_log_check.py A1 [--log PATH] [--wait 150]
    python3 src/RimMandrake/NullTexTrace/nulltex_log_check.py A2 [--log PATH] [--wait 150]

WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR. The mod (Source/NullTexTrace.cs) patches Unity's internal 12-arg
GUI.DrawTexture from its Mod constructor and writes, through UnityEngine.Debug.Log:
    [NullTexTrace] installed target=... rimthemes=True menushell=True
    [NullTexTrace] caller #1 at n=1 state=Entry longEvent=False: <caller> <- <frame> ...
    [NullTexTrace] summary n=10 callers=1 dropped=0 top: <caller> x10 || <caller> x3

A1  installed, with RimThemes and MenuShell active, and >=1 null call named by a managed caller frame.
A2  the top caller of the LAST summary line lives in aRandomKiwi.RimThemes (the offline prediction:
    UI_BackgroundMain_Patch.Prefix drawing VideoPlayer.texture with no null check). Another top caller is a FAIL,
    and the line printed names it. The ranking is trusted only from a summary of >=10 calls, with no tie at the top
    and fewer calls from unnamed (past-64) callers than the top count; anything less is UNMEASURED.

Exit 0 PASS, 1 FAIL, 2 UNMEASURED. UNMEASURED covers: no running game; a log older than the game; no installed line
(the mod is not in this load); RimThemes or MenuShell inactive (a wrong list); and 0 null calls after --wait seconds
(inconclusive, never a FAIL: the menu drew no null texture yet). Summaries print at n = 1, 10, 100 ..., so the last
one is the ranking as of the last power of ten.
"""
import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
PASS, FAIL, UNMEASURED = 0, 1, 2
TAG = "[NullTexTrace] "
SUSPECT = "aRandomKiwi.RimThemes"
INSTALLED_RE = re.compile(r"\[NullTexTrace\] installed target=.* rimthemes=(\w+) menushell=(\w+)")
NOT_INSTALLED_RE = re.compile(r"\[NullTexTrace\] NOT installed: (.*)")
CALLER_RE = re.compile(r"\[NullTexTrace\] caller #(\d+) at n=(\d+) state=(\S+) longEvent=(\w+): (.*)")
SUMMARY_RE = re.compile(r"\[NullTexTrace\] summary n=(\d+) callers=(\d+) dropped=(\d+) top: (.*)")
TOP_ITEM_RE = re.compile(r"^(.*) x(\d+)$")
MIN_RANKED = 10  # A2 ranks only from a summary of >=10 calls: the n=1 summary names whoever drew first


def parse(text):
    """-> dict: installed (None | (rimthemes, menushell)), not_installed, callers [(k, n, state, frames)], summary
    (None | (n, dropped, [(caller, count)])), the last summary only."""
    out = {"installed": None, "not_installed": None, "callers": [], "summary": None}
    for line in text.splitlines():
        if TAG not in line:
            continue
        m = INSTALLED_RE.search(line)
        if m:
            out["installed"] = (m.group(1) == "True", m.group(2) == "True")
            continue
        m = NOT_INSTALLED_RE.search(line)
        if m:
            out["not_installed"] = m.group(1).strip()
            continue
        m = CALLER_RE.search(line)
        if m:
            out["callers"].append((int(m.group(1)), int(m.group(2)), m.group(3), m.group(5).strip()))
            continue
        m = SUMMARY_RE.search(line)
        if m:
            top = []
            for item in m.group(4).split(" || "):
                t = TOP_ITEM_RE.match(item.strip())
                if t:
                    top.append((t.group(1), int(t.group(2))))
            out["summary"] = (int(m.group(1)), int(m.group(3)), top)
    return out


def judge(text, clause):
    """-> (exit code, [lines]). Pure: `text` is the whole Player.log."""
    p = parse(text)
    if p["installed"] is None:
        why = ("the mod says NOT installed: " + p["not_installed"]) if p["not_installed"] else \
            "no [NullTexTrace] installed line: the mod is not in this load"
        return UNMEASURED, ["UNMEASURED: " + why]
    rimthemes, menushell = p["installed"]
    if not (rimthemes and menushell):
        return UNMEASURED, ["UNMEASURED: wrong list: rimthemes=%s menushell=%s" % (rimthemes, menushell)]
    managed = [c for c in p["callers"] if not c[3].startswith("<no managed caller")]
    if not p["callers"]:
        return UNMEASURED, ["UNMEASURED: installed, but 0 null GUI.DrawTexture calls so far (inconclusive)"]
    if clause == "A1":
        if not managed:
            return FAIL, ["FAIL %d null-call caller line(s), none with a managed frame" % len(p["callers"])]
        lines = ["caller #%d at n=%d state=%s: %s" % (k, n, st, fr[:300]) for k, n, st, fr in managed[:10]]
        return PASS, lines + ["PASS installed, %d managed caller(s) named" % len(managed)]
    if p["summary"] is None or not p["summary"][2] or p["summary"][0] < MIN_RANKED:
        return UNMEASURED, ["UNMEASURED: no summary of >=%d calls yet (too few to rank)" % MIN_RANKED]
    n, dropped, top = p["summary"]
    lines = ["summary n=%d dropped=%d: " % (n, dropped) + " || ".join("%s x%d" % t for t in top)]
    caller = top[0][0]
    if len(top) > 1 and top[1][1] >= top[0][1]:
        return UNMEASURED, lines + ["UNMEASURED: the top two callers tie at %d" % top[0][1]]
    if dropped >= top[0][1]:
        return UNMEASURED, lines + ["UNMEASURED: %d calls from unnamed callers could outrank the top one" % dropped]
    if SUSPECT in caller:
        return PASS, lines + ["PASS top caller is in %s: %s" % (SUSPECT, caller)]
    return FAIL, lines + ["FAIL top caller is NOT in %s; the real one: %s" % (SUSPECT, caller)]


def read_running_log():
    """-> (text, None) or (None, why): the running game's Player.log, only if written since that game started."""
    sys.path.insert(0, UTILS)
    from game_paths import PLAYER_LOG
    from live_log_check import game_started, same_game
    started = game_started()
    if started is None:
        return None, "no running game (or two)"
    try:
        if os.path.getmtime(PLAYER_LOG) <= started:
            return None, "%s was last written before the running game started" % PLAYER_LOG
        with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return None, str(e)
    why = same_game(started)
    if why:
        return None, why
    return text, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clause", choices=["A1", "A2"])
    ap.add_argument("--log", default=None, help="judge this file instead (no game check, no wait)")
    ap.add_argument("--wait", type=int, default=150,
                    help="seconds to keep re-reading while the answer is UNMEASURED for want of null calls")
    a = ap.parse_args(argv)
    deadline = time.time() + max(0, a.wait)
    while True:
        if a.log:
            with open(a.log, encoding="utf-8", errors="replace") as f:
                text, why = f.read(), None
        else:
            text, why = read_running_log()
        if text is None:
            code, lines = UNMEASURED, ["UNMEASURED: " + why]
        else:
            code, lines = judge(text, a.clause)
        starved = "0 null" in lines[0] or "too few to rank" in lines[0]
        retry = (code == UNMEASURED and text is not None and not a.log and starved
                 and time.time() < deadline)
        if not retry:
            break
        time.sleep(10)
    print("\n".join(lines))
    print({PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code])
    return code


def safe_main(argv=None):
    """main(), where nothing may escape: an uncaught exception would exit 1, which a runner records as a FAIL."""
    try:
        return main(argv)
    except SystemExit:
        raise
    except BaseException as e:
        sys.stdout.write("UNMEASURED: " + ascii("%s: %s" % (type(e).__name__, str(e)[:200])) + "\n")
        return UNMEASURED


if __name__ == "__main__":
    sys.exit(safe_main())
