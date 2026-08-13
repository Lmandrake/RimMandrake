"""prove_new_tools.py - prove the companion tools the terrain harness does not.

WHAT THIS IS FOR
================
`prove_capture_restore.py` covers the terrain three. This covers the other
thirteen:

    jawa/get_def       jawa/drain_log     jawa/list_pawns    jawa/refresh_rect
    jawa/set_plants    jawa/spawn_batch   jawa/destroy_batch
    jawa/set_roof_batch  jawa/get_roof_batch
    jawa/spawn_pawn    jawa/damage
    jawa/fire_incident jawa/send_letter   (GM pair -- see SAFETY)

Each check prints the deciding string from NEXT_RELOAD.md B2, so a pass here is
the queue item closed, not a vague "it returned success".

STATUS: 14 of 16 PROVEN LIVE 2026-08-12 on the 573-mod stack (20 passed, 0
failed) against a dev quicktest colony. The roof pair -- set_roof_batch and
get_roof_batch -- was built and deployed in the SAME shutdown window and has
never run. This file is both the regression harness and the proof run for those
two; run it after any companion change, not just after a deploy.

THE FIRST CHECK IS THE ONLY ONE THAT MATTERS UNTIL IT PASSES
============================================================
Count the registered `jawa/` tools. 16 = the deploy took. 14 = the game is on
the pre-roof build. 7 = an older companion still. 0 = RimBridgeServer did not
load the bundle at all. Every other result here is uninformative until that
reads 16, so the script says so loudly and keeps going only to gather evidence
about WHICH build is live.

READ THE SCHEMA, DO NOT GUESS IT
================================
Four of the five failures in the first live run were this file's fault, not the
tools': guessed parameter names (`destroy_batch` takes `rects`/`categories`, not
`ops`/`category`), guessed response shapes (`spawn_pawn` puts faction/hostile on
each `pawns` entry; `damage` answers with `targetsHit` + `results`), a pause
check reading a tool that has no pause field, and a `drain_log` window too small
to tell filtering from a no-op. Every one recorded a FAIL against working code.
`CLAUDE.md`'s "never guess a defName, a field, or a namespace" covers tool
parameters and response keys. `inputSchema.properties` is right there.

SAFETY -- read this before adding to it
=======================================
This runs against whatever map is loaded, which may be a colony that matters.

  * `jawa/fire_incident` is called with `dryRun: true` and there is NO flag to
    make it fire. Firing an incident on someone's colony is a deliberate act,
    not something a proof script should be one typo away from doing.
  * Pawn spawning is OFF unless you pass --pawns, because the worst outcome
    here is a live hostile the script failed to clean up. When enabled it
    spawns ONE pawn, at the map EDGE, with the game PAUSED, and kills it with
    `jawa/damage` -- which is also how `damage` gets tested against a hostile,
    the thing the stock bridge could never do.
  * The script REFUSES to mutate anything if it cannot confirm the game is
    paused. Per traps.md, unpausing with freshly-spawned hostiles on the map
    once wiped half a colony.
  * Planted vegetation is removed again via `jawa/destroy_batch`.

If cleanup fails the script does not fail quietly -- it prints the pawn id and
position and tells you to deal with it.

    python.exe src/RimMandrake/bridgetools/prove_new_tools.py                # safe subset
    python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns        # + spawn/damage
    python3     src/RimMandrake/bridgetools/prove_new_tools.py --selftest    # no game needed
"""
import argparse
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils", "rimbench"))

OK, BAD, SKIP = "  ok  ", "  FAIL", "  skip"
RESULTS = []

# The full deployed set, in the order build.py ships them.
ALL_TOOLS = [
    "jawa/set_terrain", "jawa/set_terrain_batch", "jawa/get_terrain_batch",
    "jawa/spawn_batch", "jawa/destroy_batch", "jawa/list_pawns",
    "jawa/set_plants", "jawa/damage", "jawa/get_def", "jawa/drain_log",
    "jawa/refresh_rect", "jawa/spawn_pawn", "jawa/fire_incident",
    "jawa/send_letter", "jawa/set_roof_batch", "jawa/get_roof_batch",
]
# Present in the 7-tool build that shipped earlier the same day. Used to tell
# "old companion" apart from "bundle did not load", which have different fixes.
OLD_SEVEN = set(ALL_TOOLS[:7])


def check(name, cond, detail=""):
    print("%s %s%s" % (OK if cond else BAD, name, ("   " + detail) if detail else ""))
    RESULTS.append((name, bool(cond)))
    return bool(cond)


def skip(name, why):
    print("%s %s   %s" % (SKIP, name, why))
    RESULTS.append((name, None))


def ok(resp):
    return isinstance(resp, dict) and resp.get("success") is True


# ------------------------------------------------------------------ 0. census

def census(s):
    """Which companion tools this game registered. THE gate check."""
    print("\n0. deploy census -- nothing below means anything until this reads 16")
    try:
        names = {t.get("name") for t in s._rb.list_tools()}
    except Exception as e:
        print("     could not list tools: %s" % str(e)[:140])
        return set()

    jawa = {n for n in names if n and n.startswith("jawa/")}
    for t in ALL_TOOLS:
        print("     %-26s %s" % (t, "registered" if t in jawa else "MISSING"))

    check("all %d companion tools registered" % len(ALL_TOOLS),
          len(jawa) == len(ALL_TOOLS),
          "%d of %d (%d tools on the bridge overall)"
          % (len(jawa), len(ALL_TOOLS), len(names)))

    if len(jawa) != len(ALL_TOOLS):
        if not jawa:
            print("\n     0 jawa/ tools: RimBridgeServer did not load the bundle.")
            print("     Check <RimWorld>\\BridgeTools\\JawaBench\\ exists and the")
            print("     game was restarted AFTER the deploy.")
        elif jawa <= OLD_SEVEN:
            print("\n     Only the old seven: the game is running a STALE companion.")
            print("     The DLL cannot be overwritten while RimWorld runs, so the")
            print("     deploy silently did not happen. Close the game and re-run")
            print("     src/RimMandrake/bridgetools/build.py --gm --apply.")
        else:
            print("\n     Unexpected subset -- record it, this has not been seen.")
    return jawa


# -------------------------------------------------------- 1. read-only tools

def prove_get_def(s, have):
    """statBases for a def the OFFLINE dump shows as bare -- the whole point."""
    if "jawa/get_def" not in have:
        return skip("jawa/get_def", "not registered")
    r = s.call("jawa/get_def", defName="Steel", defType="ThingDef")
    stats = (r or {}).get("statBases") or {}
    check("jawa/get_def returns a resolved def", ok(r),
          "mod=%s" % (r or {}).get("mod"))
    check("  ...with statBases the def dump omits", bool(stats),
          "%d stat(s): %s" % (len(stats), list(stats)[:4]))


def prove_drain_log(s, have):
    """Deciding string: it sees messages logged DURING step_game_ticks, which
    the per-call `effects.logs` channel structurally cannot."""
    if "jawa/drain_log" not in have:
        return skip("jawa/drain_log", "not registered")
    # Ask for a LARGE window on purpose. At limit=25 on a modded load the newest
    # 25 messages are all red, so errorsOnly returns 25 of 25 and "the filter
    # works" is indistinguishable from "the filter is a no-op". A weak test that
    # passes is worse than no test: it retires the question.
    r = s.call("jawa/drain_log", limit=200)
    msgs = (r or {}).get("messages") or []
    check("jawa/drain_log returns messages", ok(r), "%d message(s)" % len(msgs))
    e = s.call("jawa/drain_log", limit=200, errorsOnly=True)
    emsgs = (e or {}).get("messages") or []
    if len(msgs) == len(emsgs):
        skip("  ...and errorsOnly filters",
             "INCONCLUSIVE: %d of %d — every message in the window is an "
             "error, so this cannot tell filtering from a no-op" % (len(emsgs), len(msgs)))
    else:
        check("  ...and errorsOnly filters", ok(e) and len(emsgs) < len(msgs),
              "%d error/warning of %d" % (len(emsgs), len(msgs)))


def prove_list_pawns(s, have):
    """Deciding string: returns hostiles and animals, not just colonists --
    totalOnMap must exceed the colonist count."""
    if "jawa/list_pawns" not in have:
        return skip("jawa/list_pawns", "not registered")
    r = s.call("jawa/list_pawns")
    # "No current map" is not a verdict on this tool. Distinguish it, or the
    # run records a FAIL against a tool that was never actually exercised.
    if not ok(r) and "no current map" in str((r or {}).get("message", "")).lower():
        return skip("jawa/list_pawns",
                    "no current map yet — tool not exercised, not failed")
    total = (r or {}).get("totalOnMap")
    try:
        ncol = len(s.colonists())
    except Exception:
        ncol = None
    check("jawa/list_pawns answers", ok(r), "totalOnMap=%s" % total)
    if total is None or ncol is None:
        return skip("  ...sees more than colonists", "no count to compare")
    check("  ...sees more than colonists", total > ncol,
          "%s on map vs %d colonists" % (total, ncol))


# ------------------------------------------------------- 2. harmless mutation

def prove_refresh_rect(s, have, x, z):
    """Cannot be proven by a return value -- it dirties a mesh. What IS provable
    is that it accepts a rect and rejects a malformed one, which is the half a
    script can honestly settle. The visual half needs an eye; say so."""
    if "jawa/refresh_rect" not in have:
        return skip("jawa/refresh_rect", "not registered")
    r = s.call("jawa/refresh_rect", rect="%d,%d,4,4" % (x, z))
    check("jawa/refresh_rect accepts a rect", ok(r))
    bad = s.call("jawa/refresh_rect", rect="not-a-rect")
    check("  ...and REFUSES a malformed one", not ok(bad),
          "refused as intended" if not ok(bad) else "accepted garbage")
    print("     note: the visible half (a stale section redrawing) needs an eye.")
    print("     Paint with refresh=false, look, then call this and look again.")


def prove_spawn_batch(s, have, x, z):
    """Deciding string: many things in ONE call, filth routed via FilthMaker,
    and a cell that cannot take filth REFUSES rather than silently succeeding.

    ⚠️ The ops grammar is NOT the same as set_terrain_batch's, despite sharing a
    parser. Terrain reads 'Terrain:x,z,w,h' as a RECT. Spawn reads
    'Def:x,z[,count]' where count is the STACK SIZE -- 'Steel:x,z,50' makes ONE
    thing labelled "Steel x50", not 50 things and not a 50-wide rect. `spawned`
    counts ops, not items. Measured 2026-08-12; guessing it cost a wrong
    conclusion about the tool being broken.
    """
    if "jawa/spawn_batch" not in have:
        return skip("jawa/spawn_batch", "not registered")

    ops = ";".join("ChunkSlagSteel:%d,%d" % (x + i, z) for i in range(3))
    r = s.call("jawa/spawn_batch", ops=ops)
    check("jawa/spawn_batch spawns many in ONE call",
          ok(r) and (r or {}).get("spawned") == 3,
          "spawned=%s of opsRequested=%s perDef=%s"
          % ((r or {}).get("spawned"), (r or {}).get("opsRequested"),
             (r or {}).get("perDef")))

    st = s.call("jawa/spawn_batch", ops="Steel:%d,%d,50" % (x, z + 2))
    check("  ...and `count` is a STACK SIZE, not a rect or a repeat",
          ok(st) and (st or {}).get("spawned") == 1,
          "one thing, stackCount 50 (spawned=%s)" % (st or {}).get("spawned"))

    # The honest-refusal path. A silent success on a cell that cannot hold
    # filth would be indistinguishable from a working call.
    f = s.call("jawa/spawn_batch", ops="Filth_Dirt:%d,%d" % (x, z + 4))
    errs = (f or {}).get("errors") or []
    if (f or {}).get("spawned"):
        skip("  ...and a refusing cell says WHY",
             "this cell accepted the filth — inconclusive, not a failure")
    else:
        check("  ...and a refusing cell says WHY", bool(errs),
              str([e.get("error") for e in errs])[:90])

    if "jawa/destroy_batch" in have:
        d = s.call("jawa/destroy_batch", rects="%d,%d,6,6" % (x, z),
                   categories="Item,Filth")
        check("  ...and destroy_batch clears them", ok(d),
              "destroyed=%s across %s cell(s)"
              % ((d or {}).get("destroyed"), (d or {}).get("cellsExamined")))
    else:
        print("     WARNING: destroy_batch missing, spawned items LEFT at %d,%d"
              % (x, z))


def prove_roofs(s, have, x, z):
    """Deciding string: capture -> roof -> restore returns the grid EXACTLY,
    including cells that had no roof (those must come back to None, not be
    skipped). The capture replays as the restore with no translation, same
    contract as the terrain pair.
    """
    if "jawa/set_roof_batch" not in have or "jawa/get_roof_batch" not in have:
        return skip("jawa/set_roof_batch", "not registered")

    rect = "%d,%d,4,4" % (x, z)
    cap = s.call("jawa/get_roof_batch", rects=rect)
    before = (cap or {}).get("ops")
    check("jawa/get_roof_batch captures in one call", ok(cap) and bool(before),
          "%s cell(s), roofs=%s" % ((cap or {}).get("cellsRead"),
                                    (cap or {}).get("roofs")))

    w = s.call("jawa/set_roof_batch", ops="RoofConstructed:%s" % rect)
    check("jawa/set_roof_batch roofs cells", ok(w),
          "changed=%s failedVerify=%s"
          % ((w or {}).get("cellsChanged"), (w or {}).get("cellsFailedVerify")))
    check("  ...and every cell verified against the grid",
          (w or {}).get("cellsFailedVerify") == 0, "read back after writing")

    mid = (s.call("jawa/get_roof_batch", rects=rect) or {}).get("ops")
    check("  ...and the read-back shows the new roof",
          bool(mid) and "RoofConstructed" in str(mid), str(mid)[:60])

    # The capture replays straight back -- no translation step.
    r = s.call("jawa/set_roof_batch", ops=before)
    after = (s.call("jawa/get_roof_batch", rects=rect) or {}).get("ops")
    check("  ...and the capture REPLAYS as an exact restore",
          ok(r) and after == before,
          "identical" if after == before else "got %s want %s"
                                             % (str(after)[:40], str(before)[:40]))

    check("  ...including cells that had NO roof (None round-trips)",
          "None" not in str(before) or "None" in str(after),
          "unroofed cells are a fact the restore needs")


def prove_set_plants(s, have, x, z):
    """Deciding string: planted > 0 at the requested growth, and a refused cell
    says WHY. Cleans up with destroy_batch."""
    if "jawa/set_plants" not in have:
        return skip("jawa/set_plants", "not registered")
    # Parameter and response names below are READ from the tool schema
    # (`inputSchema.properties`), not guessed. Guessing cost a false FAIL on
    # 2026-08-12: destroy_batch takes `rects`/`categories`, not `ops`/`category`,
    # and the tool was fine. CLAUDE.md's "never guess a field" covers tool
    # parameters too.
    r = s.call("jawa/set_plants", ops="Plant_Grass:%d,%d,3,3" % (x, z),
               growth=0.5)
    planted = (r or {}).get("planted")
    check("jawa/set_plants plants something", ok(r) and (planted or 0) > 0,
          "planted=%s cleared=%s rejected=%s"
          % (planted, (r or {}).get("cleared"), (r or {}).get("rejected")))
    reasons = (r or {}).get("rejectionReasons") or (r or {}).get("errors")
    if reasons:
        print("     a rejected cell says WHY: %s" % str(reasons)[:110])

    if "jawa/destroy_batch" in have:
        d = s.call("jawa/destroy_batch", rects="%d,%d,3,3" % (x, z),
                   categories="Plant")
        check("  ...and destroy_batch removes them again", ok(d),
              "destroyed=%s pawnsSkipped=%s"
              % ((d or {}).get("destroyed"), (d or {}).get("pawnsSkipped")))
    else:
        print("     WARNING: destroy_batch missing, planted grass LEFT at %d,%d"
              % (x, z))


# ------------------------------------------------------------ 3. the GM pair

def prove_gm(s, have, send_letter):
    """fire_incident is proven ONLY through dryRun. There is deliberately no
    flag to make this script fire one."""
    if "jawa/fire_incident" not in have:
        skip("jawa/fire_incident", "not registered")
    else:
        r = s.call("jawa/fire_incident", incidentDef="TraderCaravanArrival",
                   dryRun=True)
        fired = (r or {}).get("fired")
        check("jawa/fire_incident dryRun answers canFireNow", ok(r),
              "canFireNow=%s" % (r or {}).get("canFireNow"))
        check("  ...and dryRun did NOT fire it", fired is False or fired is None,
              "fired=%s" % fired)
        print("     firing for real is a deliberate act. Not scripted here.")

    if "jawa/send_letter" not in have:
        skip("jawa/send_letter", "not registered")
    elif not send_letter:
        skip("jawa/send_letter", "needs --letter (it writes to the player's pane)")
    else:
        r = s.call("jawa/send_letter", label="RimBench proof",
                   text="Sent by prove_new_tools.py. Safe to dismiss.",
                   letterDef="NeutralEvent")
        check("jawa/send_letter sends", ok(r),
              "as %s -- CHECK THE PANE" % (r or {}).get("letterDef"))


# ------------------------------------------------- 4. spawn + damage (opt-in)

def prove_pawns(s, have, x, z):
    """The only genuinely risky check, so it is opt-in and self-cleaning.

    Deciding strings, two at once:
      jawa/spawn_pawn -- the pawn is ACTUALLY hostile (the debug menu always
                         spawns player-side, which is the bug it exists to fix)
      jawa/damage     -- it damages a HOSTILE, which ResolvePawn could never
                         reach, and the hediffs are read back afterwards
    """
    for t in ("jawa/spawn_pawn", "jawa/damage", "jawa/list_pawns"):
        if t not in have:
            return skip("pawn spawn/damage", "%s not registered" % t)

    r = s.call("jawa/spawn_pawn", kindDef="Scavenger", x=x, z=z,
               faction="hostile", count=1)
    if not ok(r):
        return check("jawa/spawn_pawn spawns a hostile", False,
                     str(r)[:120])
    # Response shape READ from a live call, not guessed. spawn_pawn puts
    # faction/hostile on each entry of `pawns`, NOT at the top level; damage
    # answers with `targetsHit` plus a `results` list carrying
    # totalDamageDealt / hediffsBefore / hediffsAfter / dead. Guessing these
    # produced three false FAILs against tools that were working perfectly.
    pawns = (r or {}).get("pawns") or []
    p0 = pawns[0] if pawns else {}
    pid = p0.get("id")
    check("jawa/spawn_pawn spawns a hostile", ok(r) and bool(pid),
          "id=%s faction=%s hostile=%s" % (pid, p0.get("faction"),
                                           p0.get("hostile")))
    check("  ...and it really is NOT player-side", p0.get("hostile") is True,
          "faction=%s — the debug menu always spawns player-side"
          % p0.get("faction"))

    # ONE HIT DOES NOT KILL, whatever `amount` says. RimWorld caps a single
    # damage instance by body part, so amount=400 landed as 32.0 dealt and left
    # a wounded hostile standing -- measured 2026-08-12, twice. `amount` is a
    # request, not a delivery. So hit until dead, bounded, and treat running
    # out of attempts as a loud failure rather than a quiet one.
    d = s.call("jawa/damage", damageDef="Bullet", amount=400, thingId=pid)
    res = ((d or {}).get("results") or [{}])[0]
    first = res
    for _ in range(24):
        if res.get("dead") or res.get("destroyed"):
            break
        d2 = s.call("jawa/damage", damageDef="Bullet", amount=400, thingId=pid)
        if not (d2 or {}).get("targetsHit"):
            break                       # gone from the map entirely
        res = ((d2 or {}).get("results") or [{}])[0]
    # Evidence about the tool comes from the FIRST hit -- that it reached a
    # hostile at all and grew the hediff list. The loop is cleanup, not proof.
    res, kill = first, res
    check("jawa/damage reaches a HOSTILE", ok(d) and (d or {}).get("targetsHit"),
          "targetsHit=%s dealt=%s" % ((d or {}).get("targetsHit"),
                                      res.get("totalDamageDealt")))
    grew = (res.get("hediffsAfter") or 0) > (res.get("hediffsBefore") or 0)
    check("  ...and hediffs are read back AFTER the fact", grew,
          "hediffs %s -> %s, dead=%s" % (res.get("hediffsBefore"),
                                         res.get("hediffsAfter"),
                                         res.get("dead")))
    check("  ...and it never touches colonists",
          (d or {}).get("colonistsSkipped") == 0,
          "colonistsSkipped=%s (none were in range)"
          % (d or {}).get("colonistsSkipped"))

    still = [p for p in ((s.call("jawa/list_pawns") or {}).get("pawns") or [])
             if p.get("id") == pid and not p.get("dead")]
    if still:
        print("\n     *** CLEANUP INCOMPLETE ***")
        print("     Pawn %s is STILL ALIVE at (%d,%d). The game is paused; deal"
              % (pid, x, z))
        print("     with it before unpausing -- traps.md has the colony-wipe entry.")
    check("  ...and the test pawn is gone", not still,
          "cleaned up" if not still else "STILL ALIVE -- see above")


# ------------------------------------------------------------------- selftest

class _StubBridge(object):
    def __init__(self, tools=None):
        self._tools = ALL_TOOLS if tools is None else tools

    def list_tools(self):
        return [{"name": n} for n in self._tools] + [{"name": "rimworld/x"}]


class _StubSession(object):
    """Enough of Session to exercise every branch with no game.

    The point is that the LOAD is not spent debugging this file. A stub that
    always says yes would prove nothing, so the refusal paths answer failure.
    """
    def __init__(self, tools=None, hostile_survives=False):
        self._rb = _StubBridge(tools)
        self._hostile_survives = hostile_survives
        self._roof = "None:10,10,4,1"

    def colonists(self):
        return [{"id": "c%d" % i} for i in range(4)]

    def call(self, tool, **p):
        if tool == "rimbridge/get_bridge_status":
            return {"success": True, "state": {
                "paused": True, "mapCount": 1, "currentMapReady": True,
                "longEventPending": False, "playable": True}}
        if tool == "jawa/get_def":
            return {"success": True, "mod": "Core",
                    "statBases": {"MarketValue": 1.9, "Mass": 0.008}}
        if tool == "jawa/drain_log":
            n = 3 if p.get("errorsOnly") else 11
            return {"success": True, "messages": [{"text": "m"}] * n}
        if tool == "jawa/list_pawns":
            # Must match the id the spawn stub hands back, or the cleanup check
            # compares against a pawn that was never spawned and reports a
            # clean-up that did not happen. The selftest caught exactly that.
            alive = ([{"id": "Human1", "dead": False}]
                     if self._hostile_survives else [])
            return {"success": True, "totalOnMap": 19, "pawns": alive}
        if tool == "jawa/refresh_rect":
            return ({"success": False, "message": "rect must be 'x,z,w,h'"}
                    if "," not in str(p.get("rect")) else {"success": True})
        if tool == "jawa/set_plants":
            return {"success": True, "planted": 9, "refused": 0}
        if tool == "jawa/get_roof_batch":
            return {"success": True, "cellsRead": 16,
                    "ops": self._roof, "roofs": [self._roof.split(":")[0]]}
        if tool == "jawa/set_roof_batch":
            self._roof = str(p.get("ops", "None:10,10,4,1"))
            return {"success": True, "cellsChanged": 16, "cellsFailedVerify": 0,
                    "perDef": {}, "errors": []}
        if tool == "jawa/spawn_batch":
            ops = str(p.get("ops", ""))
            n = ops.count(";") + 1 if ops else 0
            if ops.startswith("Filth_"):
                return {"success": False, "spawned": 0, "opsRequested": n,
                        "errors": [{"op": 0, "def": "Filth_Dirt",
                                    "error": "terrain does not accept this filth"}]}
            return {"success": True, "spawned": n, "opsRequested": n,
                    "perDef": {"ChunkSlagSteel": n}, "errors": []}
        if tool == "jawa/destroy_batch":
            return {"success": True, "destroyed": 9, "cellsExamined": 36,
                    "pawnsSkipped": 0}
        if tool == "jawa/fire_incident":
            return {"success": True, "canFireNow": True, "fired": False}
        if tool == "jawa/send_letter":
            return {"success": True, "letterDef": "NeutralEvent"}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [
                {"id": "Human1", "faction": "Insect", "hostile": True}]}
        if tool == "jawa/damage":
            return {"success": True, "targetsHit": 1, "colonistsSkipped": 0,
                    "results": [{"id": "Human1", "totalDamageDealt": 60.0,
                                 "hediffsBefore": 4, "hediffsAfter": 6,
                                 "dead": True, "destroyed": True}]}
        return {"success": True}


def _run_all(s, letter=True):
    have = census(s)
    prove_get_def(s, have)
    prove_drain_log(s, have)
    prove_list_pawns(s, have)
    prove_refresh_rect(s, have, 10, 10)
    prove_spawn_batch(s, have, 10, 10)
    prove_roofs(s, have, 10, 10)
    prove_set_plants(s, have, 10, 10)
    prove_gm(s, have, send_letter=letter)
    prove_pawns(s, have, 10, 10)


def selftest():
    """Exercise the GOOD path and the three bad ones.

    A stub that answers yes to everything only proves the happy path parses.
    The output that actually earns its keep is what this prints when the deploy
    did NOT take -- so those branches get run too, and the run fails if a
    scenario that should produce failures produces none.
    """
    global RESULTS
    scenarios = [
        ("all 14 registered", dict(), 0, None),
        ("STALE companion -- only the old 7", dict(tools=ALL_TOOLS[:7]), 1,
         "old seven"),
        ("bundle never loaded -- 0 jawa tools", dict(tools=[]), 1, "0 jawa"),
        ("cleanup FAILED -- hostile survived", dict(hostile_survives=True), 1,
         "still alive"),
    ]
    bad = 0
    for name, kw, want_failures, _ in scenarios:
        print("\n" + "=" * 68)
        print("SELFTEST SCENARIO: %s" % name)
        print("=" * 68)
        RESULTS = []
        _run_all(_StubSession(**kw))
        failed = [n for n, v in RESULTS if v is False]
        if want_failures and not failed:
            print("\n  SELFTEST BUG: this scenario should have produced "
                  "failures and produced none.")
            bad += 1
        elif not want_failures and failed:
            print("\n  SELFTEST BUG: the good path should pass cleanly.")
            bad += 1
        else:
            print("\n  scenario behaved as intended (%d failure(s))" % len(failed))

    print("\n" + "=" * 68)
    print("SELFTEST %s -- %d scenario(s) misbehaved"
          % ("FAILED" if bad else "OK", bad))
    print("The harness is exercised in all four worlds, so the load is not")
    print("spent debugging this file.")
    return 1 if bad else 0


# -------------------------------------------------------------------- driver

def summarise():
    passed = [n for n, v in RESULTS if v is True]
    failed = [n for n, v in RESULTS if v is False]
    skipped = [n for n, v in RESULTS if v is None]
    print("\n%d passed, %d failed, %d skipped" %
          (len(passed), len(failed), len(skipped)))
    for n in failed:
        print("  FAILED: %s" % n)
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--x", type=int, default=10,
                    help="test cell X. Default is deliberately near the map edge.")
    ap.add_argument("--z", type=int, default=10)
    ap.add_argument("--pawns", action="store_true",
                    help="also spawn ONE hostile at --x/--z and kill it with "
                         "jawa/damage. Off by default: the worst outcome here "
                         "is a live hostile the script failed to clean up.")
    ap.add_argument("--letter", action="store_true",
                    help="also send a real letter to the player's pane.")
    ap.add_argument("--selftest", action="store_true",
                    help="run against a stub. No game, no socket.")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    from core import Session                                   # noqa: E402
    with Session() as s:
        have = census(s)

        # Read-only first: if the bridge is sick, find out before mutating.
        print("\n1. read-only tools")
        prove_get_def(s, have)
        prove_drain_log(s, have)
        prove_list_pawns(s, have)

        # `paused` lives on rimbridge/get_bridge_status, NOT on
        # rimworld/get_game_info -- which returns status/ticksGame/mapCount and
        # no pause field at all. Reading the wrong tool gives paused=None, and
        # this check then blocks itself forever while looking like a game
        # problem. Cost a cycle on 2026-08-12.
        state = (s.call("rimbridge/get_bridge_status") or {}).get("state") or {}
        paused = state.get("paused")
        if paused is not True:
            print("\n*** GAME IS NOT CONFIRMED PAUSED (paused=%r). ***" % paused)
            print("Refusing to mutate. Pause the game and re-run; traps.md has")
            print("the entry where unpausing with fresh hostiles wiped a colony.")
            return summarise()

        # mapCount > 0 is TRUE AND INSUFFICIENT: the map can exist while
        # Find.CurrentMap is still null, and every companion tool that opens
        # with "No current map" then fails for a reason that has nothing to do
        # with the tool. Gate on the readiness flags instead.
        if not state.get("currentMapReady") or state.get("longEventPending"):
            print("\n*** MAP EXISTS BUT IS NOT CURRENT YET. ***")
            print("     mapCount=%s currentMapReady=%s longEventPending=%s "
                  "playable=%s" % (state.get("mapCount"),
                                   state.get("currentMapReady"),
                                   state.get("longEventPending"),
                                   state.get("playable")))
            print("Companion tools will fail with 'No current map. Load a game")
            print("first.' -- which reads like a broken tool and is not one.")
            print("Wait for currentMapReady, then re-run.")
            return summarise()

        print("\n2. harmless mutation")
        prove_refresh_rect(s, have, args.x, args.z)
        prove_spawn_batch(s, have, args.x, args.z)
        prove_roofs(s, have, args.x, args.z)
        prove_set_plants(s, have, args.x, args.z)

        print("\n3. the GM pair -- dryRun only")
        prove_gm(s, have, args.letter)

        print("\n4. spawn + damage")
        if args.pawns:
            prove_pawns(s, have, args.x, args.z)
        else:
            skip("pawn spawn/damage", "needs --pawns")

    return summarise()


if __name__ == "__main__":
    sys.exit(main())
