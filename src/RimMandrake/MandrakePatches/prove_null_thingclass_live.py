"""prove_null_thingclass_live.py -- live proof A1 of QUICKTEST_POLICY_NRE_FULLLIST_1. Read-only; never takes the bridge.

    python3 src/RimMandrake/MandrakePatches/prove_null_thingclass_live.py [--list <ModsConfig>]
    python3 src/RimMandrake/MandrakePatches/prove_null_thingclass_live.py --selftest     # offline: every mutant goes red

A1 holds when ALL of these read true in the RUNNING game:
  1 deployed  the game's Mods/MandrakePatches/Assemblies/RimMandrakePatches.dll is byte-identical to the repo's DLL
  2 loaded    jawa/running_mods holds mandrake.rm.patches
  3 full list the running list equals --list (default ModsConfig.FULL.LATEST.xml) as a packageId set
  4 game      rimworld/get_game_info says status game_loaded with mapCount >= 1: a Game exists, so Game..ctor (the only
              caller of ReadingPolicyDatabase.GenerateStartingPolicies) ran in this process. A load that stops at the
              main menu, or a quicktest that crashed back to it, is a FAIL here, never a pass.
  5 no NRE    Player.log of THIS process (written after the game started, past the "Bridge token:" anchor) has no line
              naming GenerateStartingPolicies or ReadingPolicyDatabase..ctor (live_log_check.judge, --never)
It then REPORTS every "[RimMandrake Patches] null thingClass:" line (the guard's isolation of the offending mod: def,
mod name, packageId, file), or says there were none. A guard line that does not name a mod in the shipped shape
"from mod '<name>' (<packageId>)" is a FAIL: the line exists to isolate the mod.

Exit 0 A1 holds, 1 a clause is false (lines say which), 2 UNMEASURED (no running game, bridge unreachable, a log from
an earlier session, an unreadable list).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
sys.path.insert(0, UTILS)

PASS, FAIL, UNMEASURED = 0, 1, 2
PACKAGE_ID = "mandrake.rm.patches"
DLL_REL = os.path.join("Assemblies", "RimMandrakePatches.dll")
REPO_DLL = os.path.join(HERE, DLL_REL)
FULL_LIST = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
NEVER = ("GenerateStartingPolicies", "ReadingPolicyDatabase..ctor")
GUARD_TAG = "[RimMandrake Patches] null thingClass:"          # NullThingClassGuard.LogTag
GUARD_RE = re.compile(r"ThingDef (\S+) from mod '([^']*)' \(([^)]*)\), file (.*?), has no thingClass")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def list_ids(path):
    root = ET.parse(path).find("activeMods")
    if root is None:
        raise ValueError("%s has no <activeMods>" % path)
    return {(li.text or "").strip().lower() for li in root if (li.text or "").strip()}


def unwrap(reply):
    """A bridge reply -> its result dict (the client may print it bare or under result/structuredContent)."""
    for _ in range(3):
        if isinstance(reply, dict) and isinstance(reply.get("result"), dict):
            reply = reply["result"]
        elif isinstance(reply, dict) and isinstance(reply.get("structuredContent"), dict):
            reply = reply["structuredContent"]
        else:
            break
    return reply if isinstance(reply, dict) else None


def judge(repo_dll, game_dll, running, expected, game_info, log_code, log_lines, log_text):
    """Pure. -> (code, lines). running/expected: packageId sets (None = unread); game_info: dict or None;
    log_code/log_lines: live_log_check.judge's answer on log_text (or an UNMEASURED freshness verdict)."""
    out, fails, unk = [], [], []
    if game_dll is None:
        fails.append("deployed: no %s in the game's Mods/MandrakePatches (not deployed)" % DLL_REL)
    elif repo_dll != game_dll:
        fails.append("deployed: game DLL %s... is not the repo DLL %s... (stale deploy)" % (game_dll[:12], repo_dll[:12]))
    else:
        out.append("ok deployed: game DLL == repo DLL %s..." % repo_dll[:12])
    if running is None:
        unk.append("loaded: jawa/running_mods unreadable")
    elif PACKAGE_ID not in running:
        fails.append("loaded: %s is not in the running load (%d mods)" % (PACKAGE_ID, len(running)))
    else:
        out.append("ok loaded: %s in the running load" % PACKAGE_ID)
    if running is not None:
        if expected is None:
            unk.append("full list: the expected list is unreadable")
        elif running != expected:
            fails.append("full list: running %d mods != expected %d (missing %s; extra %s)" % (
                len(running), len(expected), sorted(expected - running)[:5], sorted(running - expected)[:5]))
        else:
            out.append("ok full list: running == expected (%d mods)" % len(expected))
    if game_info is None:
        unk.append("game: rimworld/get_game_info unreadable")
    else:
        st, maps = game_info.get("status"), game_info.get("mapCount")
        if st != "game_loaded" or not isinstance(maps, int) or maps < 1:
            fails.append("game: no started map (status %r, mapCount %r): Game..ctor never ran or the start crashed" % (st, maps))
        else:
            out.append("ok game: status game_loaded, mapCount %d" % maps)
    if log_code == FAIL:
        fails.extend("no NRE: " + x for x in log_lines)
    elif log_code == PASS:
        out.append("ok no NRE: " + "; ".join(log_lines))
    else:
        unk.append("no NRE: " + "; ".join(log_lines))
    guard = [x.strip() for x in (log_text or "").splitlines() if GUARD_TAG in x]
    if log_code in (PASS, FAIL):
        if not guard:
            out.append("report: no %r line: no ThingDef on this list had a null thingClass" % GUARD_TAG)
        for x in guard[:60]:
            m = GUARD_RE.search(x)
            if m and m.group(2) not in ("", "?") and m.group(3) not in ("", "?"):
                out.append("report: def %s <- mod %r (%s), file %s" % m.groups())
            else:
                fails.append("report: a guard line does not name its mod: %s" % x[:240])
        if len(guard) > 60:
            out.append("report: ... %d more guard lines" % (len(guard) - 60))
    code = FAIL if fails else UNMEASURED if unk else PASS
    lines = out + ["FAIL " + x for x in fails] + ["UNMEASURED " + x for x in unk]
    return code, lines + [{PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code]]


def _bridge(tool, params, timeout=60):
    from live_def_check import _bridge as b
    reply, _ = b(tool, params, timeout)
    return unwrap(reply)


def read_log():
    """-> (code, lines, text): live_log_check's freshness gate and --never verdict on the running game's Player.log."""
    import live_log_check as llc
    from game_paths import PLAYER_LOG
    started = llc.game_started()
    if started is None:
        return UNMEASURED, ["no running game"], ""
    try:
        if os.path.getmtime(PLAYER_LOG) <= started:
            return UNMEASURED, ["Player.log predates the running game"], ""
        with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return UNMEASURED, [str(e)], ""
    why = llc.same_game(started)
    if why:
        return UNMEASURED, [why], ""
    code, lines = llc.judge(text, [], never=NEVER)
    return code, lines, text


def live(list_path):
    from game_paths import LOCAL_MODS
    game_dll_path = os.path.join(LOCAL_MODS, "MandrakePatches", DLL_REL)
    game_dll = sha(game_dll_path) if os.path.isfile(game_dll_path) else None
    try:
        expected = list_ids(list_path)
    except (OSError, ET.ParseError, ValueError):
        expected = None
    from live_def_check import running_ids
    rm = _bridge("jawa/running_mods", {"details": False, "assembly": ""})
    running = running_ids(rm) if rm is not None else None
    gi = _bridge("rimworld/get_game_info", {})
    log_code, log_lines, text = read_log()
    return judge(sha(REPO_DLL), game_dll, running, expected, gi, log_code, log_lines, text)


def selftest():
    """Every clause broken one at a time must go red (FAIL or UNMEASURED, never PASS); the sound case must PASS."""
    import live_log_check as llc
    ids = {"ludeon.rimworld", PACKAGE_ID, "x.y"}
    good_log = "init\nBridge token: abc\nquicktest map generated\n"
    named = GUARD_TAG + " ThingDef RSW_FooJuv from mod 'Rim Star Wars Fauna' (mandrake.sw.fauna), file Foo.xml, has no thingClass; set to Pawn at startup so the game can start."
    base = dict(repo_dll="a" * 64, game_dll="a" * 64, running=set(ids), expected=set(ids),
                game_info={"status": "game_loaded", "mapCount": 1}, log_text=good_log)

    def run(**kw):
        d = dict(base, **kw)
        c, ls = llc.judge(d["log_text"], [], never=NEVER)
        return judge(d["repo_dll"], d["game_dll"], d["running"], d["expected"], d["game_info"], c, ls, d["log_text"])

    cases = [
        ("sound", {}, PASS),
        ("sound with a named guard line", {"log_text": good_log + named + "\n"}, PASS),
        ("not deployed", {"game_dll": None}, FAIL),
        ("stale deploy", {"game_dll": "b" * 64}, FAIL),
        ("patches not loaded", {"running": ids - {PACKAGE_ID}, "expected": ids - {PACKAGE_ID}}, FAIL),
        ("minimal list, not the full one", {"running": {PACKAGE_ID, "ludeon.rimworld"}}, FAIL),
        ("main menu only (checker's probe)", {"game_info": {"status": "main_menu", "mapCount": 0}}, FAIL),
        ("game but no map", {"game_info": {"status": "game_loaded", "mapCount": 0}}, FAIL),
        ("bridge silent", {"game_info": None}, UNMEASURED),
        ("running list unread", {"running": None}, UNMEASURED),
        ("NRE in GenerateStartingPolicies", {"log_text": good_log + "Exception: NullReferenceException at RimWorld.ReadingPolicyDatabase.GenerateStartingPolicies ()\n"}, FAIL),
        ("NRE in ReadingPolicyDatabase..ctor", {"log_text": good_log + "  at RimWorld.ReadingPolicyDatabase..ctor ()\n"}, FAIL),
        ("load not finished (no anchor)", {"log_text": "init\n"}, UNMEASURED),
        ("guard line naming no mod", {"log_text": good_log + GUARD_TAG + " ThingDef RSW_FooJuv from mod '?' (?), file ?, has no thingClass\n"}, FAIL),
    ]
    bad = 0
    for name, kw, want in cases:
        code, lines = run(**kw)
        ok = code == want
        bad += not ok
        print("%s %-36s want %s got %s" % ("ok  " if ok else "BAD ", name, want, code))
        if name == "sound with a named guard line" and not any("RSW_FooJuv <- mod 'Rim Star Wars Fauna' (mandrake.sw.fauna)" in x for x in lines):
            bad += 1
            print("BAD  the guard line's def and mod are not reported")
    # the shipped C# message must still match the shape this proof parses
    cs = open(os.path.join(HERE, "Source", "NullThingClassGuard", "NullThingClassGuard.cs"), encoding="utf-8").read()
    for frag in ('LogTag = "%s"' % GUARD_TAG, '" ThingDef "', '" from mod \'"', '"\' ("', '"), file "', '", has no thingClass; set to "'):
        if frag not in cs:
            bad += 1
            print("BAD  NullThingClassGuard.cs no longer carries %s" % frag)
    print("SELFTEST %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", default=FULL_LIST, help="the ModsConfig the running game must equal (default FULL.LATEST)")
    ap.add_argument("--selftest", action="store_true", help="offline mutant table; no game")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    code, lines = live(a.list)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                       # an instrument that crashes has measured nothing
        print("UNMEASURED: %s: %s" % (type(e).__name__, e))
        sys.exit(UNMEASURED)
