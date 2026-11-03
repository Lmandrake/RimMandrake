#!/usr/bin/env python3
"""tidal_lock_readback.py -- is the LOADED planet tidally locked? Read-only (TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING).

    python3 src/RimMandrake/Utils/tidal_lock_readback.py [--expect-restored] [--log Player.log] [--no-bridge]

Two instruments, both must agree:
  1. Player.log: the LAST line RM_TidalLockPresetGuard wrote at a save load,
       [RM CreatureBehaviors] planet lock at load: saved=<t> preset=<p> backend=<b> current=<t> lockPatches=<B> action=<a>
     must read current=TidallyLocked lockPatches=True. With --expect-restored it must also read action=restored
     (the load of a save made without Worldbuilder: saved=TidallyLocked, preset=(none)) -- the guard did the work.
  2. The bridge (three jawa/static_call reads): AlienWorlds.PlanetTypeManager.get_Current = TidallyLocked,
     HarmonyLib.Harmony.HasAnyPatches("7f.alienworlds.tidallylocked") = True, and, when Worldbuilder is loaded,
     Worldbuilder.World_ExposeData_Patch.get_WorldPresetName = TidallyLocked -- what the NEXT save writes as
     <worldPresetName>, beside Alien Worlds' <alienWorldsFrameworkPlanetType> (= Current), so a save written now
     cannot read Default.
Exit 0 locked, 1 the game answered and the planet is not locked (a real FAIL), 2 UNMEASURED (no load line in the log,
no bridge answer). Callers hold the bridge lock; this never takes it. The Player.log path parse is `parse_line()`,
covered offline by selftest_tidal_lock_guard.py.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PASS, FAIL, UNMEASURED = 0, 1, 2
LOCKED = "TidallyLocked"
LOCK_HARMONY_ID = "7f.alienworlds.tidallylocked"
LINE_RE = re.compile(r"\[RM CreatureBehaviors\] planet lock at load: (.*)$")
FIELD_RE = re.compile(r"(\w+)=(\S+)")


def parse_line(line):
    """-> dict of the guard line's fields, or None when the line is not one."""
    m = LINE_RE.search(line)
    if not m:
        return None
    return dict(FIELD_RE.findall(m.group(1)))


def last_load_line(path):
    last = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            d = parse_line(line)
            if d is not None:
                last = d
    return last


def judge_line(d, expect_restored=False):
    """-> (verdict, why) for one parsed guard line."""
    if d is None:
        return UNMEASURED, "no 'planet lock at load:' line: no save loaded since launch, or CreatureBehaviors predates the guard"
    bad = []
    if d.get("current") != LOCKED:
        bad.append("current=%s" % d.get("current"))
    if d.get("lockPatches") != "True":
        bad.append("lockPatches=%s" % d.get("lockPatches"))
    if expect_restored and d.get("action") != "restored":
        bad.append("action=%s (expected restored: saved=%s preset=%s)" % (d.get("action"), d.get("saved"), d.get("preset")))
    return (FAIL, "log: " + ", ".join(bad)) if bad else (PASS, "log: %s" % " ".join("%s=%s" % kv for kv in sorted(d.items())))


def _result(reply):
    if not isinstance(reply, dict) or not reply.get("success"):
        return None
    return str(reply.get("result")).strip().strip('"')


def worldbuilder_absent(reply):
    """A static_call that failed because the TYPE does not exist (Worldbuilder not loaded), not for any other reason."""
    return (isinstance(reply, dict) and not reply.get("success")
            and "Type not found" in str(reply.get("error") or reply.get("message") or ""))


def bridge_reads(timeout=60):
    """-> (verdict, why). Three read-only static calls through the Windows-side client."""
    from live_def_check import _bridge
    cur, why = _bridge("jawa/static_call", {"type": "AlienWorlds.PlanetTypeManager", "method": "get_Current", "args": ""}, timeout, read_only_static=True)
    if cur is None:
        return UNMEASURED, "bridge: " + why
    patched, why = _bridge("jawa/static_call", {"type": "HarmonyLib.Harmony", "method": "HasAnyPatches", "args": LOCK_HARMONY_ID}, timeout, read_only_static=True)
    if patched is None:
        return UNMEASURED, "bridge: " + why
    preset, why = _bridge("jawa/static_call", {"type": "Worldbuilder.World_ExposeData_Patch", "method": "get_WorldPresetName", "args": ""}, timeout, read_only_static=True)
    if preset is None:
        return UNMEASURED, "bridge: " + why
    c, p = _result(cur), _result(patched)
    if c is None or p is None:
        return UNMEASURED, "bridge: a static call failed: %r %r" % (cur, patched)
    wb = _result(preset)
    if wb is None and not worldbuilder_absent(preset):
        return UNMEASURED, "bridge: the preset-name read failed: %r" % (preset,)
    bad = []
    if c != LOCKED:
        bad.append("Current=%s" % c)
    if p.lower() != "true":
        bad.append("HasAnyPatches(%s)=%s" % (LOCK_HARMONY_ID, p))
    # wb None here: Worldbuilder is not loaded (the standalone backend writes the planet type alone)
    if wb is not None and wb != LOCKED:
        bad.append("WorldPresetName=%s" % wb)
    msg = "Current=%s HasAnyPatches=%s WorldPresetName=%s" % (c, p, wb if wb is not None else "(no Worldbuilder)")
    return (FAIL, "bridge: " + ", ".join(bad)) if bad else (PASS, "bridge: " + msg)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--expect-restored", action="store_true", help="the guard must have restored the preset at this load")
    ap.add_argument("--log", default=None, help="another Player.log (default game_paths.PLAYER_LOG)")
    ap.add_argument("--no-bridge", action="store_true", help="the log line only")
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args(argv)
    path = a.log
    if path is None:
        from game_paths import PLAYER_LOG
        path = PLAYER_LOG
    if not os.path.isfile(path):
        print("UNMEASURED: no log at %s" % path)
        return UNMEASURED
    try:
        last = last_load_line(path)
    except OSError as e:
        print("UNMEASURED: cannot read %s: %s" % (path, e))
        return UNMEASURED
    results = [judge_line(last, a.expect_restored)]
    if not a.no_bridge:
        results.append(bridge_reads(a.timeout))
    for v, why in results:
        print({PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED"}[v] + "  " + why)
    verdicts = [v for v, _ in results]
    return FAIL if FAIL in verdicts else UNMEASURED if UNMEASURED in verdicts else PASS


if __name__ == "__main__":
    sys.exit(main())
