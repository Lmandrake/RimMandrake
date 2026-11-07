"""prove_beer_policy_live.py -- live proof A1 of BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS.

    python3 src/RimMandrake/MandrakePatches/prove_beer_policy_live.py            # running game, site loaded
    python3 src/RimMandrake/MandrakePatches/prove_beer_policy_live.py --selftest # offline: every mutant goes red

The site is RM_TestSite_calm_v2 (live-site line), whose saved drug policies list Beer. A1 holds when ALL read true:
  1 deployed  the game's RimMandrakePatches.dll is byte-identical to the repo's
  2 list      the running load holds mandrake.rm.patches and Owlchemist.CherryPicker (whose kill list cuts Beer)
  3 site      this process's Player.log has "Loading game from file RM_TestSite_calm_v2"
  4 repaired  the log since that load names Beer in CutDrugPolicyGuard's line: the save really listed it and the
              guard removed it, so a silent log below is the fix working and not a save with nothing to trip on
  5 ran       the game clock moved at least MIN_TICKS, so pawns thought (vanilla logged this every pawn think)
  6 logging   Verse.Log still writes after the advance (log_alive) and no cap line fell in the watched window
  7 silent    no "AllowedToTakeScheduledEver on non-drug" since the load

Exit 0 A1 holds, 1 a clause is false, 2 UNMEASURED (no game, bridge down, wrong site, log capped).
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
sys.path.insert(0, UTILS)

PASS, FAIL, UNMEASURED = 0, 1, 2
PACKAGE_ID = "mandrake.rm.patches"
CHERRY_PICKER = "owlchemist.cherrypicker"
DLL_REL = os.path.join("Assemblies", "RimMandrakePatches.dll")
REPO_DLL = os.path.join(HERE, DLL_REL)
SITE_LINE = "Loading game from file RM_TestSite_calm_v2"
PROCESS_ANCHOR = "Bridge token:"
ERROR_TEXT = "AllowedToTakeScheduledEver on non-drug"
GUARD_TAG = "[RimMandrake Patches] cut drug in policy:"     # CutDrugPolicyGuard.LogTag
CAP_LINE = "Reached max messages limit"
MIN_TICKS = 2500


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def since_load(log_text):
    """The log after the last SITE_LINE of this process, or None when this process never loaded the site."""
    start = log_text.rfind(PROCESS_ANCHOR)
    body = log_text[start:] if start >= 0 else None
    if body is None:
        return None
    at = body.rfind(SITE_LINE)
    return body[at:] if at >= 0 else None


def judge(repo_dll, game_dll, running, ticks_moved, alive, log_text, watched):
    """Pure. -> (code, lines). running: lower-cased packageId set or None; ticks_moved: int or None; alive: bool (a
    marker written after the advance reached the log); log_text: this game's Player.log; watched: its tail from the
    moment Verse.Log was revived."""
    out, fails, unk = [], [], []
    if game_dll is None:
        fails.append("deployed: no %s in the game's Mods/MandrakePatches" % DLL_REL)
    elif game_dll != repo_dll:
        fails.append("deployed: game DLL %s... is not the repo DLL %s..." % (game_dll[:12], repo_dll[:12]))
    else:
        out.append("ok deployed: game DLL == repo DLL %s..." % repo_dll[:12])
    if running is None:
        unk.append("list: running mods unreadable")
    elif PACKAGE_ID not in running:
        fails.append("list: %s is not in the running load" % PACKAGE_ID)
    elif CHERRY_PICKER not in running:
        unk.append("list: Cherry Picker is not in the running load, so Beer is still a drug here")
    else:
        out.append("ok list: patches and Cherry Picker in the running load (%d mods)" % len(running))
    body = since_load(log_text)
    if body is None:
        unk.append("site: this game never loaded RM_TestSite_calm_v2")
    else:
        out.append("ok site: loaded RM_TestSite_calm_v2")
        if ticks_moved is None:
            unk.append("ran: game tick unreadable")
        elif ticks_moved < MIN_TICKS:
            unk.append("ran: the clock moved under the bar, so pawns may not have thought")
        else:
            out.append("ok ran: %d ticks (bar %d)" % (ticks_moved, MIN_TICKS))
        if not alive:
            unk.append("logging: the marker written after the advance never reached the log")
        elif CAP_LINE in watched:
            unk.append("logging: Verse.Log hit its cap inside the watched window")
        else:
            out.append("ok logging: live after the advance, no cap line in the window")
        errors = body.count(ERROR_TEXT)
        if errors:
            fails.append("silent: %d '%s' lines since the load" % (errors, ERROR_TEXT))
        else:
            out.append("ok silent: 0 '%s' lines since the load" % ERROR_TEXT)
        if GUARD_TAG + " Beer " not in body:
            unk.append("repaired: no guard line names Beer, so the save gave the error nothing to trip on")
        else:
            out.append("ok repaired: the guard removed Beer from the saved policies")
    code = FAIL if fails else UNMEASURED if unk else PASS
    lines = out + ["FAIL " + x for x in fails] + ["UNMEASURED: " + x for x in unk]
    return code, lines + [{PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code]]


def live():
    import validation_core as V
    from game_paths import LOCAL_MODS, PLAYER_LOG
    from live_def_check import running_ids
    game_dll_path = os.path.join(LOCAL_MODS, "MandrakePatches", DLL_REL)
    game_dll = sha(game_dll_path) if os.path.isfile(game_dll_path) else None
    B = V.Bridge()
    running = running_ids(B.call("jawa/running_mods", details=False, assembly=""))
    running = {x.lower() for x in running} if running is not None else None
    start = os.path.getsize(PLAYER_LOG)
    V.log_revive(B)
    before = V.ticks_game(B)
    B.ticks(MIN_TICKS)
    after = V.ticks_game(B)
    moved = after - before if isinstance(before, int) and isinstance(after, int) else None
    alive = bool(V.log_alive(B, "beer_policy_after").get("alive"))
    with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
        text = f.read()
    with open(PLAYER_LOG, "rb") as f:
        f.seek(start)
        watched = f.read().decode("utf-8", "replace")
    return judge(sha(REPO_DLL), game_dll, running, moved, alive, text, watched)


def selftest():
    """Every clause broken one at a time must go red (FAIL or UNMEASURED, never PASS); the sound case must PASS."""
    ids = {PACKAGE_ID, CHERRY_PICKER, "ludeon.rimworld"}
    good = "init\n%s abc\n%s with mods:\n%s Beer is no longer a drug\nmarker\n" % (PROCESS_ANCHOR, SITE_LINE, GUARD_TAG)
    base = dict(repo_dll="a" * 64, game_dll="a" * 64, running=set(ids), ticks_moved=MIN_TICKS, alive=True,
                log_text=good, watched="marker\n")
    earlier = "%s with mods:\n%s\n%s old\n" % (SITE_LINE, ERROR_TEXT, PROCESS_ANCHOR)
    cases = [
        ("sound", {}, PASS),
        ("errors only in an earlier process", {"log_text": earlier + good}, PASS),
        ("errors only before the last load", {"log_text": good.replace("marker\n", ERROR_TEXT + " Beer\n" + SITE_LINE
                                              + "\n%s Beer x\n" % GUARD_TAG)}, PASS),
        ("the error still fires", {"log_text": good + ERROR_TEXT + " Beer\n"}, FAIL),
        ("not deployed", {"game_dll": None}, FAIL),
        ("stale deploy", {"game_dll": "b" * 64}, FAIL),
        ("patches not loaded", {"running": ids - {PACKAGE_ID}}, FAIL),
        ("Cherry Picker not loaded", {"running": ids - {CHERRY_PICKER}}, UNMEASURED),
        ("running list unread", {"running": None}, UNMEASURED),
        ("another save was loaded", {"log_text": good.replace("RM_TestSite_calm_v2", "other")}, UNMEASURED),
        ("site loaded by an earlier process", {"log_text": "%s\n%s new\n" % (SITE_LINE, PROCESS_ANCHOR)}, UNMEASURED),
        ("clock did not move", {"ticks_moved": 0}, UNMEASURED),
        ("clock unread", {"ticks_moved": None}, UNMEASURED),
        ("log dead after the advance", {"alive": False}, UNMEASURED),
        ("log capped in the window", {"watched": CAP_LINE + "\n"}, UNMEASURED),
        ("save never listed Beer", {"log_text": good.replace(GUARD_TAG + " Beer", "nothing")}, UNMEASURED),
    ]
    bad = 0
    for name, kw, want in cases:
        code, _ = judge(**dict(base, **kw))
        ok = code == want
        bad += not ok
        print("%s %-36s want %s got %s" % ("ok  " if ok else "BAD ", name, want, code))
    cs = open(os.path.join(HERE, "Source", "CutDrugPolicyGuard", "CutDrugPolicyGuard.cs"), encoding="utf-8").read()
    for frag in ('LogTag = "%s"' % GUARD_TAG, 'LogTag + " " + drug.defName + " is no longer a drug'):
        if frag not in cs:
            bad += 1
            print("BAD  CutDrugPolicyGuard.cs no longer carries %s" % frag)
    print("SELFTEST %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="offline mutant table; no game")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    code, lines = live()
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                       # an instrument that crashes has measured nothing
        print("UNMEASURED: %s: %s" % (type(e).__name__, e))
        sys.exit(UNMEASURED)
