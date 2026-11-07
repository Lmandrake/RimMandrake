"""prove_log_spam_off_live.py -- live proof A2 of LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS.

    python3 src/RimMandrake/MandrakePatches/prove_log_spam_off_live.py
    python3 src/RimMandrake/MandrakePatches/prove_log_spam_off_live.py --selftest     # offline: every mutant goes red
    python3 src/RimMandrake/MandrakePatches/prove_log_spam_off_live.py --selftest --replay-log <Player.log>
                                                      # and the same judge on a real log's line order

Needs a started game on a list holding RimMandrake Patches, Intimacy and Mood Chain Reaction. It advances MIN_TICKS, then
A2 holds when ALL of these read true:
  1 deployed  the game's Mods/MandrakePatches/Assemblies/RimMandrakePatches.dll is byte-identical to the repo's DLL
  2 list      the three mods are in the running load
  3 patched   this process logged LogSpamOff's "patched" line for both sinks; they come from a startup static
              constructor, so they stand BEFORE RimBridge's token: "this process" starts at Unity's first log line and
              the token only says the load finished
  4 reached   this process logged its "first line dropped" line for both, so the silence is a silenced sink and not a
              sink that never ran here; a mod that has not reached its sink yet is UNMEASURED, never a pass
  5 silent    no line of either mod's debug output since those patched lines
  6 ran       the clock moved MIN_TICKS and a marker written after the advance reached the log, with no cap line in the
              window: a dead log would read as silence

Exit 0 A2 holds, 1 a clause is false (lines say which), 2 UNMEASURED.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
sys.path.insert(0, UTILS)
import log_rise_census as lrc

PASS, FAIL, UNMEASURED = 0, 1, 2
PACKAGE_ID = "mandrake.rm.patches"
INTIMACY_ID = "lovelydovey.sex.witheuterpe"
MOODCHAIN_ID = "acutus.moodchainreaction"
DLL_REL = os.path.join("Assemblies", "RimMandrakePatches.dll")
REPO_DLL = os.path.join(HERE, DLL_REL)
PROCESS_START = "Mono path[0] ="       # Unity's first line of every Player.log: where this process begins
PROCESS_ANCHOR = "Bridge token:"       # printed once the load finished; the mods' startup lines stand before it
CAP_LINE = lrc.CAP_LINE
TAG = "[RimMandrake Patches] log spam off:"                 # LogSpamOff.LogTag
INTIMACY_SINK = "LoveyDoveySexWithEuterpe.SexUtilities"     # LogSpamOff.IntimacyType
MOODCHAIN_SINK = "MoodChainReaction.Hediff_MCRMoodChain"    # LogSpamOff.MoodChainType
PATCHED = TAG + " patched %s"
DROPPED = TAG + " first line dropped from %s"
MIN_TICKS = 1800       # a pawn's Mood Chain scan runs every 600 ticks (Hediff_MCRMoodChain.ScanInterval); three of them


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def judge(repo_dll, game_dll, running, ticks_moved, alive, log_text, watched):
    """Pure. -> (code, lines). running: lower-cased packageId set or None; ticks_moved: int or None; alive: bool;
    log_text: this game's Player.log; watched: its tail from before the advance."""
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
    elif INTIMACY_ID not in running or MOODCHAIN_ID not in running:
        unk.append("list: Intimacy or Mood Chain Reaction is not in the running load, so there is nothing to silence")
    else:
        out.append("ok list: the three mods are in the running load")
    start = log_text.rfind(PROCESS_START)
    body = log_text[start:] if start >= 0 else ""
    if PROCESS_ANCHOR not in body:     # no start line, or a load that has not finished
        unk.append("patched: this process wrote no %r line after %r" % (PROCESS_ANCHOR, PROCESS_START))
        body = ""
    marks = [body.find(PATCHED % s) for s in (INTIMACY_SINK, MOODCHAIN_SINK)]
    if body and min(marks) < 0:
        fails.append("patched: LogSpamOff did not patch %s" % " and ".join(
            s for s, m in zip((INTIMACY_SINK, MOODCHAIN_SINK), marks) if m < 0))
    elif body:
        out.append("ok patched: both sinks")
        since = body[min(marks):]
        missing = [s for s in (INTIMACY_SINK, MOODCHAIN_SINK) if DROPPED % s not in since]
        if missing:
            unk.append("reached: no first-drop line yet from a sink, so its silence proves nothing")
        else:
            out.append("ok reached: both sinks dropped a line")
        names = [lrc.source_of(x.rstrip("\r")) for x in since.split("\n") if TAG not in x]
        spam = sum(1 for n in names if n in lrc.SPAM)
        if spam:
            fails.append("silent: %d lines of those mods' debug output since the patch" % spam)
        else:
            out.append("ok silent: 0 lines of those mods' debug output in %d lines" % len(names))
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
    alive = bool(V.log_alive(B, "log_spam_off_after").get("alive"))
    with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
        text = f.read()
    with open(PLAYER_LOG, "rb") as f:
        f.seek(start)
        watched = f.read().decode("utf-8", "replace")
    return judge(sha(REPO_DLL), game_dll, running, moved, alive, text, watched)


def replay(path):
    """The judge on a REAL log's line order (the fixture's order once hid an anchor no working game could satisfy): the
    log with both mods' lines gone and LogSpamOff's lines added where the startup constructor can write them must PASS;
    each clause broken on that same log must not. -> number of bad cases, or None when the log cannot show it."""
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        raw = f.read().split("\n")
    nl = "\r\n" if raw[0].endswith("\r") else "\n"
    raw = [x.rstrip("\r") for x in raw]
    spam = [i for i, x in enumerate(raw) if lrc.source_of(x) in lrc.SPAM]
    starts = [i for i, x in enumerate(raw) if PROCESS_START in x]
    tokens = [i for i, x in enumerate(raw) if PROCESS_ANCHOR in x]
    if len(starts) != 1 or len(tokens) != 1 or not starts[0] < tokens[0] or len(spam) < 1000:
        print("UNMEASURED: replay log: %d start lines, %d tokens, %d spam lines" % (len(starts), len(tokens), len(spam)))
        return None
    tok = tokens[0]
    clean = [x for x in raw if lrc.source_of(x) not in lrc.SPAM]
    ctok = clean.index(raw[tok])
    pi, pm = PATCHED % INTIMACY_SINK + ".HandNotesToEuterpe.", PATCHED % MOODCHAIN_SINK + ".DebugLog."
    di, dm = DROPPED % INTIMACY_SINK, DROPPED % MOODCHAIN_SINK
    ids = {PACKAGE_ID, INTIMACY_ID, MOODCHAIN_ID}

    def text(lines, at, drop_at, patched=(pi, pm), dropped=(di, dm)):
        """lines with the patched lines inserted before index `at` and the drop lines before index `drop_at`."""
        out = lines[:at] + list(patched) + lines[at:drop_at] + list(dropped) + lines[drop_at:]
        return nl.join(out)

    def verdict(log):
        return judge("a" * 64, "a" * 64, set(ids), MIN_TICKS, True, log, "marker\n")[0]

    end = len(clean)
    rtok = tok
    mid = spam[len(spam) // 2]                       # half the real spam stands before this line, none after it
    before, after = raw[:mid], [x for x in raw[mid:] if lrc.source_of(x) not in lrc.SPAM]
    cases = []
    for at in (starts[0] + 1, ctok // 2, ctok):      # first line after the start, mid-load, the line before the token
        for drop_at in (at, ctok + 1, end):
            cases.append(("patched at %d, dropped at %d of %d" % (at, drop_at, end), text(clean, at, drop_at), PASS))
    cases += [
        ("the real log's own spam kept after the patch", text(raw, rtok, rtok + 1), FAIL),
        ("the real log's spam kept only before the patch", text(before + after, mid, mid), PASS),
        ("Intimacy unpatched", text(clean, ctok, ctok + 1, patched=(pm,)), FAIL),
        ("Mood Chain unpatched", text(clean, ctok, ctok + 1, patched=(pi,)), FAIL),
        ("Intimacy sink never ran", text(clean, ctok, ctok + 1, dropped=(dm,)), UNMEASURED),
        ("Mood Chain sink never ran", text(clean, ctok, ctok + 1, dropped=(di,)), UNMEASURED),
        ("load not finished", text(clean[:ctok], ctok // 2, ctok // 2), UNMEASURED),
        ("all of it in an earlier process", text(clean, ctok, ctok + 1) + nl + clean[0] + nl + "init", UNMEASURED),
        ("patched in an earlier process only",
         text(clean, ctok, ctok + 1) + nl + nl.join(clean), FAIL),
    ]
    bad = 0
    for name, log, want in cases:
        got = verdict(log)
        bad += got != want
        print("%s replay %-46s want %s got %s" % ("ok  " if got == want else "BAD ", name, want, got))
    print("replay of %s: %d lines, %d of them spam, token at line %d" % (os.path.basename(path), len(raw), len(spam), tok + 1))
    return bad


def selftest(replay_log=None):
    """Every clause broken one at a time must go red (FAIL or UNMEASURED, never PASS); the sound case must PASS."""
    global PROCESS_START
    ids = {PACKAGE_ID, INTIMACY_ID, MOODCHAIN_ID, "ludeon.rimworld"}
    pi, pm = PATCHED % INTIMACY_SINK, PATCHED % MOODCHAIN_SINK
    di, dm = DROPPED % INTIMACY_SINK, DROPPED % MOODCHAIN_SINK
    head = PROCESS_START + " 'Managed'\ninit\n"
    good = "%s%s\n%s\nlate load\n%s abc\n%s\n%s\nmarker\n" % (head, pi, pm, PROCESS_ANCHOR, di, dm)  # a real log's order
    token_first = "%s%s abc\n%s\n%s\n%s\n%s\nmarker\n" % (head, PROCESS_ANCHOR, pi, pm, di, dm)
    earlier_all = good.replace(pi, "x").replace(pm, "x")
    base = dict(repo_dll="a" * 64, game_dll="a" * 64, running=set(ids), ticks_moved=MIN_TICKS, alive=True,
                log_text=good, watched="marker\n")
    mcr = "[MCR][MoodChain] Pat: Scan finished. NewlyAddedMemories=0\n"
    lov = "IntimacyGiver_Sex: Pat cannot currently do lovin'\n"
    cases = [
        ("sound", {}, PASS),
        ("sound: token before the patched lines", {"log_text": token_first}, PASS),
        ("sound: first drops before the token", {"log_text": "%s%s\n%s\n%s\n%s\n%s abc\nmarker\n"
                                                 % (head, pi, pm, di, dm, PROCESS_ANCHOR)}, PASS),
        ("spam in an earlier process's log tail", {"log_text": good + mcr + lov + good}, PASS),
        ("spam after the patch, before the token", {"log_text": good.replace("late load", mcr.strip())}, FAIL),
        ("patched only in an earlier process", {"log_text": good + earlier_all}, FAIL),
        ("first drops only in an earlier process",
         {"log_text": good + good.replace(di, "x").replace(dm, "x")}, UNMEASURED),
        ("token only in an earlier process", {"log_text": good + head + pi + "\n" + pm + "\n"}, UNMEASURED),
        ("no Unity start line", {"log_text": good.replace(PROCESS_START, "x")}, UNMEASURED),
        ("spam only in an earlier process", {"log_text": mcr + lov + good}, PASS),
        ("spam only before the patch", {"log_text": good.replace(pi, mcr + lov + pi, 1)}, PASS),
        ("a Mood Chain line after the patch", {"log_text": good + mcr}, FAIL),
        ("an Intimacy line after the patch", {"log_text": good + lov}, FAIL),
        ("not deployed", {"game_dll": None}, FAIL),
        ("stale deploy", {"game_dll": "b" * 64}, FAIL),
        ("patches not loaded", {"running": ids - {PACKAGE_ID}}, FAIL),
        ("Intimacy not loaded", {"running": ids - {INTIMACY_ID}}, UNMEASURED),
        ("Mood Chain not loaded", {"running": ids - {MOODCHAIN_ID}}, UNMEASURED),
        ("running list unread", {"running": None}, UNMEASURED),
        ("no process anchor", {"log_text": good.replace(PROCESS_ANCHOR, "x")}, UNMEASURED),
        ("Intimacy unpatched", {"log_text": good.replace(pi, "x")}, FAIL),
        ("Mood Chain unpatched", {"log_text": good.replace(pm, "x")}, FAIL),
        ("Intimacy sink never ran", {"log_text": good.replace(di, "x")}, UNMEASURED),
        ("Mood Chain sink never ran", {"log_text": good.replace(dm, "x")}, UNMEASURED),
        ("clock did not move", {"ticks_moved": 0}, UNMEASURED),
        ("clock unread", {"ticks_moved": None}, UNMEASURED),
        ("log dead after the advance", {"alive": False}, UNMEASURED),
        ("log capped in the window", {"watched": CAP_LINE + "\n"}, UNMEASURED),
    ]
    bad = 0
    for name, kw, want in cases:
        code, _ = judge(**dict(base, **kw))
        ok = code == want
        bad += not ok
        print("%s %-36s want %s got %s" % ("ok  " if ok else "BAD ", name, want, code))
    cs = open(os.path.join(HERE, "Source", "LogSpamOff", "LogSpamOff.cs"), encoding="utf-8").read()
    for frag in ('LogTag = "%s"' % TAG, 'IntimacyType = "%s"' % INTIMACY_SINK, 'MoodChainType = "%s"' % MOODCHAIN_SINK,
                 'LogTag + " patched " + typeName + "." + method', 'LogTag + " first line dropped from " + source'):
        if frag not in cs:
            bad += 1
            print("BAD  LogSpamOff.cs no longer carries %s" % frag)
    # The anchor mutant: "this process" back at the token must go red on a sound real-order log, or this table cannot
    # see the defect that made A2 unprovable.
    kept, PROCESS_START = PROCESS_START, PROCESS_ANCHOR
    mutant = judge(**base)[0]
    PROCESS_START = kept
    print("%s anchor mutant (process starts at the token) got %s, must not be %s"
          % ("ok  " if mutant != PASS else "BAD ", mutant, PASS))
    bad += mutant == PASS
    if replay_log:
        if not os.path.isfile(replay_log):
            print("UNMEASURED: no replay log at %s" % replay_log)
            return UNMEASURED
        r = replay(replay_log)
        if r is None:
            return UNMEASURED
        bad += r
    print("SELFTEST %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="offline mutant table; no game")
    ap.add_argument("--replay-log", help="with --selftest: also run the judge over this real Player.log's line order")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(a.replay_log)
    code, lines = live()
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                       # an instrument that crashes has measured nothing
        print("UNMEASURED: %s: %s" % (type(e).__name__, e))
        sys.exit(UNMEASURED)
