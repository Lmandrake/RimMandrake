"""prove_new_tools.py - prove the companion tools the terrain harness does not.

WHAT THIS IS FOR
================
`prove_capture_restore.py` covers the terrain three. This covers the other
eighteen:

    jawa/get_def       jawa/drain_log     jawa/list_pawns    jawa/refresh_rect
    jawa/set_plants    jawa/spawn_batch   jawa/destroy_batch
    jawa/set_roof_batch  jawa/get_roof_batch  jawa/list_factions
    jawa/spawn_pawn    jawa/damage
    jawa/set_pawn_rotation  jawa/set_pawn_style  jawa/set_pawn_xenotype
    jawa/order_pawn    (the real walk needs --walk -- see SAFETY)
    jawa/fire_incident jawa/send_letter   (GM pair -- see SAFETY)

Each check prints the deciding string from NEXT_RELOAD.md B2, so a pass here is
the queue item closed, not a vague "it returned success".

STATUS: run `--census` for what is deployed right now; this paragraph does not
try to hold that number. What matters and does not go stale: several tools have
been BUILT and DEPLOYED but never once driven in a live game -- the roof pair,
list_factions, the three pawn-appearance tools and order_pawn were all authored
offline with the game down. This file is both the regression harness and the
first proof run for those; run it after any companion change, not just after a
deploy.

THE FIRST CHECK IS THE ONLY ONE THAT MATTERS UNTIL IT PASSES
============================================================
The census compares the tools the GAME registered against the tools the DEPLOYED
DLL actually contains. Both sides are measured, so there is no expected number
to keep up to date and none is written here on purpose -- an earlier version of
this header listed seven of them and every one went stale. If the two disagree
the script names the individual tools, which is the answer you wanted anyway.

`--gm` needs no special case: a non-GM build simply contains two fewer names
(fire_incident, send_letter), and the deployed DLL reports that itself.

0 registered means RimBridgeServer did not load the bundle at all; a subset
matching the old seven means a stale companion, which is what happens when a
deploy was attempted while the game held the file.

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
  * `jawa/order_pawn`'s real walk is OFF unless you pass --walk, because it
    UNPAUSES the game for a couple of seconds -- the one thing the pause gate
    below exists to prevent. Without --walk the tool is still exercised, but
    only in its zero-tick form, which touches nothing.

If cleanup fails the script does not fail quietly -- it prints the pawn id and
position and tells you to deal with it.

    python.exe src/RimMandrake/bridgetools/prove_new_tools.py --census      # READ ONLY
    python.exe src/RimMandrake/bridgetools/prove_new_tools.py                # + mutation
    python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns        # + spawn/damage
    python3     src/RimMandrake/bridgetools/prove_new_tools.py --selftest    # no game needed

Only --census and --selftest are non-destructive. The bare form is NOT a "safe
subset": it spawns things, builds roofs, sets plants and fires a dryRun
incident. On an irreplaceable map use --census and nothing else.
"""
import argparse
import os
import sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils", "rimbench"))

OK, BAD, SKIP = "  ok  ", "  FAIL", "  skip"
RESULTS = []

# 🔴 DERIVED FROM THE DEPLOYED BINARY, never hand-written.
#
# This used to be a hardcoded list and it drifted three times. The failure is
# always the same shape and it is always wired to a FAIL verdict: ship a tool,
# forget the list, and the census reads "24 of 22" -- a FAIL on a CORRECT
# deploy, which is exactly how a census stops being believed. A retired seat caught the
# fourth instance before it landed on the irreversible worldgen run.
#
# The right invariant is not "the game has the tools I remembered". It is
# "the game registered every tool the DEPLOYED BINARY actually contains".
# That number cannot drift, because both sides are measured. It also handles
# --gm for free: a non-GM build simply contains two fewer names.
#
# ⚠️ `strings -a` is the correct scan HERE and nowhere near sufficient in
# general. A [Tool("jawa/x")] name is an attribute argument, so it lives in the
# UTF-8 #Strings heap and a 7-bit scan reads it. A message inside a method body
# is UTF-16LE in #US and needs `strings -a -el`. Proving a NAME shipped is this
# check's whole job; do not reuse this helper to prove a MESSAGE shipped.
# ⚠️ This script is run BOTH ways: `python.exe ...` for a live run (Windows
# paths) and `python3 ... --selftest` from WSL (/mnt/c paths). A single-form
# constant reads as "CANNOT MEASURE" under the other interpreter, which is a
# silent downgrade of the gate rather than an error. So try both forms.
_GAME_DLL_REL = (r"Steam\steamapps\common\RimWorld"
                 r"\BridgeTools\JawaBench\JawaBench.BridgeTools.dll")
GAME_DLL_CANDIDATES = (
    "C:\\Program Files (x86)\\" + _GAME_DLL_REL,
    "/mnt/c/Program Files (x86)/" + _GAME_DLL_REL.replace("\\", "/"),
)


def _game_dll():
    """First candidate that exists; else the Windows form, so the error names
    the path a reader will recognise."""
    for p in GAME_DLL_CANDIDATES:
        if os.path.exists(p):
            return p
    return GAME_DLL_CANDIDATES[0]


GAME_DLL = _game_dll()


def tools_in_binary(path=None):
    """The jawa/ tool names present in a compiled companion DLL.

    Returns a sorted list, or [] if the file cannot be read -- the caller must
    treat [] as "could not measure", NOT as "the binary has no tools". An
    unreadable file and an empty one are different answers and this returns the
    same value for both, so the caller checks existence separately.
    """
    import re
    p = path or GAME_DLL
    try:
        with open(p, "rb") as fh:
            blob = fh.read()
    except OSError:
        return []
    # ASCII-only on purpose: see the encoding note above.
    return sorted({m.decode("ascii")
                   for m in re.findall(rb"jawa/[a-z_]{3,40}", blob)})


ALL_TOOLS = tools_in_binary()

# Present in the 7-tool build that shipped earlier the same day. Used to tell
# "old companion" apart from "bundle did not load", which have different fixes.
# Named explicitly rather than sliced off ALL_TOOLS, which is now sorted and
# derived -- a slice of it would silently mean something else.
OLD_SEVEN = {
    "jawa/set_terrain", "jawa/set_terrain_batch", "jawa/get_terrain_batch",
    "jawa/spawn_batch", "jawa/destroy_batch", "jawa/list_pawns",
    "jawa/set_plants",
}


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
    expected = set(ALL_TOOLS)
    if not expected:
        # Not a pass and not a fail: the yardstick itself is missing.
        check("companion census", False,
              "CANNOT MEASURE -- could not read %s" % GAME_DLL)
        return set()

    print("\n0. deploy census -- expected set DERIVED from the deployed DLL "
          "(%d tools), not from a list in this file" % len(expected))

    # The build/deploy gap, checked before the game is even asked. The artifact
    # is what build.py just produced; the game copy is what RRimWorld actually
    # loaded. A tool present in one and not the other is the single most common
    # state in this project, because the DLL cannot be overwritten while the
    # game holds it -- and it is silent.
    art = os.path.join(_ROOT, "src", "RimMandrake", "bridgetools", "artifacts",
                       "BridgeTools", "JawaBench", "JawaBench.BridgeTools.dll")
    built = set(tools_in_binary(art))
    if built and built != expected:
        undeployed = sorted(built - expected)
        vanished = sorted(expected - built)
        print("     STOP -- artifact and game copy disagree.")
        if undeployed:
            print("       built but NOT deployed: %s" % ", ".join(undeployed))
            print("       -> deploy needs the game CLOSED (build.py --gm --apply)")
        if vanished:
            print("       deployed but not in the artifact: %s" % ", ".join(vanished))
            print("       -> the game copy is NEWER than your build, or --gm was omitted")

    try:
        names = {t.get("name") for t in s._rb.list_tools()}
    except Exception as e:
        # Must be a recorded FAILURE, not a silent early return: an omitted
        # check contributes nothing to RESULTS, so summarise() would print
        # "0 failed" for a run where the gate check never actually ran --
        # the same "success without verification" shape this census exists
        # to catch, one level up.
        check("companion census", False,
              "could not list tools: %s" % str(e)[:140])
        return set()

    jawa = {n for n in names if n and n.startswith("jawa/")}
    for t in ALL_TOOLS:
        print("     %-26s %s" % (t, "registered" if t in jawa else "MISSING"))

    # A tool the GAME has that the binary does not is not a pass either -- it
    # means the scan or the deploy path is wrong, and a census that only checks
    # a count would call that green.
    unexpected = sorted(jawa - expected)
    if unexpected:
        print("     registered but NOT in the deployed DLL: %s"
              % ", ".join(unexpected))

    check("every tool in the deployed DLL registered", jawa == expected,
          "%d of %d (%d tools on the bridge overall)"
          % (len(jawa & expected), len(expected), len(names)))

    if jawa != expected:
        missing = sorted(expected - jawa)
        if missing:
            print("\n     MISSING from the running game: %s" % ", ".join(missing))
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


def prove_list_factions(s, have):
    """jawa/list_factions -- the header names it as one of the eighteen this
    file covers, but until this function existed the tool was never actually
    called: a stale claim, not just an untested tool.

    Deciding strings, per JawaBenchTerrainTools.cs's own 2026-08-13 finding
    (a caller reading `count` alone got a subset and called it the total):
      * settlementCount summed across factions equals settlementsTotal.
      * a defName filter narrows countReturned to 1 while
        countAllIncludingHidden still reports the FULL roster -- the exact
        subset-as-total shape that finding exists to make impossible.
    """
    if "jawa/list_factions" not in have:
        return skip("jawa/list_factions", "not registered")

    r = s.call("jawa/list_factions", includeHidden=True)
    factions = (r or {}).get("factions") or []
    check("jawa/list_factions lists the world's factions", ok(r) and bool(factions),
          "count=%s settlementsTotal=%s" % ((r or {}).get("count"),
                                            (r or {}).get("settlementsTotal")))
    check("  ...and includeHidden=True returns the complete roster",
          (r or {}).get("isCompleteList") is True,
          "hiddenSkipped=%s truncated=%s filtered=%s"
          % ((r or {}).get("hiddenSkipped"), (r or {}).get("truncated"),
             (r or {}).get("filtered")))

    summed = sum(f.get("settlementCount") or 0 for f in factions)
    check("  ...and settlementCount sums to settlementsTotal",
          summed == (r or {}).get("settlementsTotal"),
          "sum(settlementCount)=%d vs settlementsTotal=%s"
          % (summed, (r or {}).get("settlementsTotal")))

    check("  ...and exactly one faction is the player",
          sum(1 for f in factions if f.get("isPlayer")) == 1,
          "isPlayer rows: %d" % sum(1 for f in factions if f.get("isPlayer")))

    total_full = (r or {}).get("countAllIncludingHidden")
    target = next((f.get("defName") for f in factions if not f.get("isPlayer")), None)
    if target is None:
        skip("  ...and a defName filter narrows countReturned without losing the total",
             "no non-player faction on this world to filter on")
    else:
        r2 = s.call("jawa/list_factions", includeHidden=True, defName=target)
        rows2 = (r2 or {}).get("factions") or []
        check("  ...and a defName filter narrows countReturned without losing the total",
              ok(r2) and (r2 or {}).get("countReturned") == 1
              and len(rows2) == 1 and rows2[0].get("defName") == target
              and (r2 or {}).get("countAllIncludingHidden") == total_full,
              "countReturned=%s countAllIncludingHidden=%s (want %s)"
              % ((r2 or {}).get("countReturned"),
                 (r2 or {}).get("countAllIncludingHidden"), total_full))


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

# Xenotypes to try, in order. NONE of these is guaranteed: Hussar and Genie ship
# with Biotech, the Jawa three come from mods, and a stack without Biotech has no
# XenotypeDef at all. So the harness ASKS the game which one exists rather than
# hardcoding one and recording a FAIL against a tool that worked.
# ⚠️ Baseliner must never be used here: Pawn_GeneTracker.get_Xenotype returns
# XenotypeDefOf.Baseliner when the field is null, so "converted to Baseliner"
# reads back true even if SetXenotype did nothing at all.
XENOTYPE_CANDIDATES = ["BTD_Jawa", "OuterRim_Jawa", "guy762_xenotype_jawa",
                       "Jawa_Xeno_Gamorrean", "Hussar", "Genie"]


def pick_xenotype(s, have):
    """First XenotypeDef of the candidates that this game actually has."""
    if "jawa/get_def" not in have:
        return None
    for name in XENOTYPE_CANDIDATES:
        try:
            r = s.call("jawa/get_def", defName=name, defType="XenotypeDef")
        except Exception:
            return None
        if ok(r):
            return name
    return None


def prove_pawn_rotation(s, have, pid):
    """Deciding string: the rotation READS BACK off the pawn, and it holds --
    a bare write is undone by Pawn_RotationTracker on the next tick, and
    Thing.set_Rotation returns silently on an already-locked pawn."""
    if "jawa/set_pawn_rotation" not in have:
        return skip("jawa/set_pawn_rotation", "not registered")

    r = s.call("jawa/set_pawn_rotation", pawnId=pid, dir="east",
               lockRotation=True)
    row = ((r or {}).get("pawns") or [{}])[0]
    # `applied` is computed in the tool from pawn.Rotation read back AFTER the
    # write, so it is the assertion; `after` is a Translate()d string and is
    # detail only -- asserting on it would fail on a non-English game.
    check("jawa/set_pawn_rotation turns a pawn east",
          ok(r) and (r or {}).get("turned") == 1 and row.get("applied") is True,
          "after=%s posture=%s visible=%s" % (row.get("after"),
                                              row.get("posture"),
                                              row.get("visible")))
    check("  ...and LOCKS the facing against the engine",
          row.get("locked") is True and (r or {}).get("locked") is True,
          "debugRotLocked=%s" % row.get("locked"))

    # Turning it again while locked is the trap: without the clear->set->lock
    # order this second call is a silent no-op.
    r2 = s.call("jawa/set_pawn_rotation", pawnId=pid, dir="north",
                lockRotation=True)
    row2 = ((r2 or {}).get("pawns") or [{}])[0]
    check("  ...and a LOCKED pawn can still be turned again",
          ok(r2) and row2.get("applied") is True
          and str(row2.get("after")) != str(row.get("after")),
          "%s -> %s" % (row.get("after"), row2.get("after")))

    # ALWAYS unlock: debugRotLocked is written by Thing.ExposeData, so a pawn
    # left locked stays locked across a save and load.
    u = s.call("jawa/set_pawn_rotation", pawnId=pid, dir="unlock")
    urow = ((u or {}).get("pawns") or [{}])[0]
    check("  ...and unlock releases it", ok(u) and urow.get("locked") is False,
          "locked=%s" % urow.get("locked"))


def prove_pawn_style(s, have, pid):
    """Deciding string: the hair def reads back off pawn.story AFTER the write,
    and the tool refuses a typo instead of half-applying it."""
    if "jawa/set_pawn_style" not in have:
        return skip("jawa/set_pawn_style", "not registered")

    r = s.call("jawa/set_pawn_style", pawnId=pid, hair="Bald",
               hairColor="#402808")
    rows = (r or {}).get("pawns") or [{}]
    changes = {c.get("field"): c for c in (rows[0].get("changes") or [])}
    hair = changes.get("hair") or {}
    check("jawa/set_pawn_style sets hair, read back off the pawn",
          ok(r) and (r or {}).get("pawnsChanged") == 1
          and hair.get("now") == "Bald" and hair.get("ok") is True,
          "hair %s -> %s" % (hair.get("was"), hair.get("now")))
    col = changes.get("hairColor") or {}
    check("  ...and the hair colour with it",
          col.get("now") is not None,
          "hairColor %s -> %s" % (col.get("was"), col.get("now")))

    # A typo must change NOTHING. Half a restyled pawn that returns success is
    # the failure this tool's up-front def resolution exists to prevent.
    bad = s.call("jawa/set_pawn_style", pawnId=pid, hair="NoSuchHairDef_zzz")
    check("  ...and refuses an unknown HairDef outright",
          not ok(bad) and "hairdef" in str((bad or {}).get("message", "")).lower(),
          str((bad or {}).get("message", ""))[:70])


def prove_pawn_xenotype(s, have, pid, xeno):
    """Deciding string: pawn.genes.Xenotype reads back as the def asked for, and
    it is NOT Baseliner -- which is what get_Xenotype returns for a pawn whose
    xenotype was never set, and therefore what a silent no-op looks like."""
    if "jawa/set_pawn_xenotype" not in have:
        return skip("jawa/set_pawn_xenotype", "not registered")
    if not xeno:
        return skip("jawa/set_pawn_xenotype",
                    "no XenotypeDef of %s exists here -- Biotech absent, or a "
                    "different xenotype mod set" % "/".join(XENOTYPE_CANDIDATES[:3]))

    r = s.call("jawa/set_pawn_xenotype", pawnId=pid, xenotype=xeno)
    row = ((r or {}).get("pawns") or [{}])[0]
    check("jawa/set_pawn_xenotype converts a pawn in place",
          ok(r) and (r or {}).get("pawnsChanged") == 1
          and row.get("now") == xeno and row.get("now") != "Baseliner",
          "%s -> %s (%s genes in def)" % (row.get("was"), row.get("now"),
                                          row.get("genesInDef")))
    check("  ...and the genes actually landed",
          (row.get("genesInDef") or 0) == 0
          or ((row.get("endogenesAfter") or 0) + (row.get("xenogenesAfter") or 0)) > 0,
          "endo=%s xeno=%s inheritable=%s" % (row.get("endogenesAfter"),
                                              row.get("xenogenesAfter"),
                                              row.get("inheritable")))
    bad = s.call("jawa/set_pawn_xenotype", pawnId=pid, xenotype="NoSuchXeno_zzz")
    check("  ...and refuses an unknown XenotypeDef",
          not ok(bad),
          str((bad or {}).get("message", ""))[:70])


def prove_spawn_pawn_xenotype(s, have, xeno, x, z):
    """Deciding string: the FORCED xenotype is on the pawn as generated, not
    applied afterwards. Returns the spawned pawn's id so it can be cleaned up."""
    if not xeno:
        skip("jawa/spawn_pawn xenotype=", "no XenotypeDef available here")
        return None
    r = s.call("jawa/spawn_pawn", kindDef="Scavenger", x=x, z=z,
               faction="hostile", count=1, xenotype=xeno)
    row = ((r or {}).get("pawns") or [{}])[0]
    check("jawa/spawn_pawn forces a xenotype at GENERATION time",
          ok(r) and row.get("xenotype") == xeno
          and row.get("xenotypeApplied") is True,
          "id=%s xenotype=%s requested=%s" % (row.get("id"), row.get("xenotype"),
                                              row.get("xenotypeRequested")))
    check("  ...and counts only pawns that really spawned",
          (r or {}).get("spawnedCount") == 1 and (r or {}).get("failedCount") == 0,
          "spawnedCount=%s failedCount=%s"
          % ((r or {}).get("spawnedCount"), (r or {}).get("failedCount")))
    return row.get("id")


def prove_order_pawn(s, have, pid, x, z, walk):
    """Deciding string: the pawn's READ-BACK position, not the accept bool.

    TryTakeOrderedJob returns true for a job it merely enqueued and never looks
    at reachability (IL_013f / IL_01ac / IL_01fa in Pawn_JobTracker). So the
    only thing that closes this row is a position read back off the map after
    real ticks have passed.

    Two halves, deliberately split by risk:

      always (--pawns)  the PAUSED probe. waitTicks=0, unpause=False, so the
                        game is not touched. It asserts the tool REFUSES to
                        call a no-movement result a success -- the exact
                        silent-success shape this seat exists to kill.
      opt-in (--walk)   the real walk. This UNPAUSES the game for a couple of
                        seconds, which is why it is not on by default: the
                        script's own safety gate demands a paused game before
                        it mutates anything, and a live hostile that gets a
                        turn is a different risk from one standing frozen.
    """
    if "jawa/order_pawn" not in have:
        return skip("jawa/order_pawn", "not registered")
    if not pid:
        return skip("jawa/order_pawn", "no test pawn id")

    # --- half one: paused, zero ticks, nothing touched.
    r = s.call("jawa/order_pawn", pawnId=pid, x=x + 6, z=z,
               waitTicks=0, unpause=False, draft=False)
    check("jawa/order_pawn will not call a no-tick result a success",
          isinstance(r, dict) and r.get("success") is False
          and r.get("ticksElapsed") == 0,
          "success=%s ticksElapsed=%s"
          % ((r or {}).get("success"), (r or {}).get("ticksElapsed")))
    row = ((r or {}).get("pawns") or [{}])[0]
    check("  ...and it reports canReach, computed BEFORE the order",
          "canReach" in row,
          "canReach=%s orderAccepted=%s" % (row.get("canReach"),
                                            row.get("orderAccepted")))

    # Two refusals, both free. A tool that accepts a destination it cannot have
    # understood is the same silent-success shape as one that accepts a job it
    # cannot run -- and pathEndMode is the parameter that decides whether
    # canReach answers the game's question or a neighbouring one.
    bad = s.call("jawa/order_pawn", pawnId=pid, waitTicks=0, unpause=False)
    check("  ...and it REFUSES an order with no destination at all",
          isinstance(bad, dict) and bad.get("success") is False,
          str((bad or {}).get("message"))[:90])
    bad2 = s.call("jawa/order_pawn", pawnId=pid, x=x, z=z, waitTicks=0,
                  unpause=False, pathEndMode="nearby")
    check("  ...and it REFUSES an unknown pathEndMode instead of guessing one",
          isinstance(bad2, dict) and bad2.get("success") is False,
          str((bad2 or {}).get("message"))[:90])

    if not walk:
        return skip("jawa/order_pawn actually moves a pawn",
                    "needs --walk (it unpauses the game)")

    # The walk uses a COLONIST, not the test hostile. A hostile has no drafter,
    # so its own Lord duty overrides the Goto within a few ticks and a perfectly
    # working tool reads as a FAIL. A DRAFTED colonist holds the destination --
    # that is the whole reason the vanilla right-click order drafts first.
    lp = s.call("jawa/list_pawns", faction="player")
    cands = [p for p in ((lp or {}).get("pawns") or [])
             if not p.get("dead") and not p.get("downed") and p.get("id")]
    if not cands:
        return skip("jawa/order_pawn actually moves a pawn",
                    "no standing player pawn to walk")
    c = cands[0]
    cid, hx, hz = c.get("id"), c.get("x"), c.get("z")

    # Out six cells, then back to the cell they were standing in. Self-cleaning:
    # the colonist ends where it started, undrafted.
    w = s.call("jawa/order_pawn", pawnId=cid, x=hx + 6, z=hz,
               waitTicks=240, timeoutSeconds=20, draft=True, undraftAfter=False)
    wrow = ((w or {}).get("pawns") or [{}])[0]
    if wrow.get("canReach") is False:
        skip("jawa/order_pawn actually moves a pawn",
             "(%s,%s) unreachable from (%s,%s) -- a map fact, not a tool fault"
             % (hx + 6, hz, hx, hz))
    else:
        check("jawa/order_pawn actually moves a pawn",
              ok(w) and wrow.get("arrived") is True,
              "%s: start=%s end=%s arrived=%s ticksElapsed=%s"
              % (c.get("name"), wrow.get("start"), wrow.get("end"),
                 wrow.get("arrived"), (w or {}).get("ticksElapsed")))
        check("  ...and the game really ticked while it walked",
              ((w or {}).get("ticksElapsed") or 0) > 0,
              "ticksElapsed=%s timedOut=%s" % ((w or {}).get("ticksElapsed"),
                                               (w or {}).get("timedOut")))

    # Put them back, and undraft. Reported either way -- litter that is not
    # reconciled is this seat's characteristic failure.
    b = s.call("jawa/order_pawn", pawnId=cid, x=hx, z=hz,
               waitTicks=240, timeoutSeconds=20, draft=True, undraftAfter=True)
    brow = ((b or {}).get("pawns") or [{}])[0]
    check("  ...and the colonist is back where it started, undrafted",
          brow.get("arrived") is True
          and not ((b or {}).get("leftDrafted") or []),
          "home=(%s,%s) end=%s leftDrafted=%s speedRestored=%s"
          % (hx, hz, brow.get("end"), (b or {}).get("leftDrafted"),
             (b or {}).get("speedRestored")))


def kill_pawn(s, pid):
    """Hit until dead, bounded. `amount` is a request, not a delivery."""
    d = s.call("jawa/damage", damageDef="Bullet", amount=400, thingId=pid)
    first = ((d or {}).get("results") or [{}])[0]
    res = first
    for _ in range(24):
        if res.get("dead") or res.get("destroyed"):
            break
        d2 = s.call("jawa/damage", damageDef="Bullet", amount=400, thingId=pid)
        if not (d2 or {}).get("targetsHit"):
            break                       # gone from the map entirely
        res = ((d2 or {}).get("results") or [{}])[0]
    return d, first


def prove_pawns(s, have, x, z, walk=False):
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

    # ---- the three pawn-appearance tools, on the pawn already standing there.
    # They run BEFORE the damage checks: a downed or dead pawn makes
    # set_pawn_rotation a documented no-op (the renderer calls LayingFacing()
    # for any non-standing posture), which would read as a broken tool.
    xeno = pick_xenotype(s, have)
    prove_pawn_rotation(s, have, pid)
    prove_pawn_style(s, have, pid)
    prove_pawn_xenotype(s, have, pid, xeno)
    prove_order_pawn(s, have, pid, x, z, walk)

    # A SECOND hostile, forced to the xenotype at generation time. Cleaned up
    # in the same pass below -- both ids are killed and both are checked gone.
    pid2 = (prove_spawn_pawn_xenotype(s, have, xeno, x, z)
            if "jawa/spawn_pawn" in have else None)

    # ONE HIT DOES NOT KILL, whatever `amount` says. RimWorld caps a single
    # damage instance by body part, so amount=400 landed as 32.0 dealt and left
    # a wounded hostile standing -- measured 2026-08-12, twice. `amount` is a
    # request, not a delivery. So hit until dead, bounded, and treat running
    # out of attempts as a loud failure rather than a quiet one.
    d, first = kill_pawn(s, pid)
    # Evidence about the tool comes from the FIRST hit -- that it reached a
    # hostile at all and grew the hediff list. The loop is cleanup, not proof.
    res = first
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

    if pid2:
        kill_pawn(s, pid2)

    wanted = {q for q in (pid, pid2) if q}
    still = [p for p in ((s.call("jawa/list_pawns") or {}).get("pawns") or [])
             if p.get("id") in wanted and not p.get("dead")]
    if still:
        print("\n     *** CLEANUP INCOMPLETE ***")
        print("     Pawn(s) %s are STILL ALIVE at (%d,%d). The game is paused; deal"
              % (", ".join(str(p.get("id")) for p in still), x, z))
        print("     with it before unpausing -- traps.md has the colony-wipe entry.")
    check("  ...and every test pawn is gone", not still,
          "cleaned up (%d spawned)" % len(wanted) if not still
          else "STILL ALIVE -- see above")


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
        self._spawned = 0
        self._rot = "South"
        # The stub game "has" exactly one of the candidate xenotypes, which is
        # what a real stack looks like: pick_xenotype must walk past the ones
        # that are absent rather than assume the first name resolves.
        self._xenotype = "Hussar"

    def colonists(self):
        return [{"id": "c%d" % i} for i in range(4)]

    def call(self, tool, **p):
        if tool == "rimbridge/get_bridge_status":
            return {"success": True, "state": {
                "paused": True, "mapCount": 1, "currentMapReady": True,
                "longEventPending": False, "playable": True}}
        if tool == "jawa/get_def":
            if p.get("defType") == "XenotypeDef":
                return ({"success": True, "mod": "Biotech"}
                        if p.get("defName") == self._xenotype
                        else {"success": False,
                              "message": "No XenotypeDef named '%s'."
                                         % p.get("defName")})
            return {"success": True, "mod": "Core",
                    "statBases": {"MarketValue": 1.9, "Mass": 0.008}}
        if tool == "jawa/drain_log":
            n = 3 if p.get("errorsOnly") else 11
            return {"success": True, "messages": [{"text": "m"}] * n}
        if tool == "jawa/list_pawns":
            if p.get("faction") == "player":
                return {"success": True, "totalOnMap": 19, "pawns": [
                    {"id": "Colonist1", "name": "Tam", "x": 40, "z": 40,
                     "dead": False, "downed": False}]}
            # Must match the id the spawn stub hands back, or the cleanup check
            # compares against a pawn that was never spawned and reports a
            # clean-up that did not happen. The selftest caught exactly that.
            alive = ([{"id": "Human1", "dead": False}]
                     if self._hostile_survives else [])
            return {"success": True, "totalOnMap": 19, "pawns": alive}
        if tool == "jawa/list_factions":
            if p.get("defName"):
                return {"success": True,
                        "factions": [{"defName": p["defName"], "name": p["defName"],
                                      "isPlayer": False, "hostile": True, "goodwill": -50,
                                      "hidden": False, "permanentEnemy": False,
                                      "settlementCount": 2}],
                        "count": 1, "countReturned": 1, "countAllIncludingHidden": 3,
                        "isCompleteList": False, "settlementsTotal": 5,
                        "hiddenSkipped": 0, "filtered": 2, "truncated": 0}
            return {"success": True, "factions": [
                {"defName": "PlayerColony", "name": "Player", "isPlayer": True,
                 "hostile": False, "goodwill": 0, "hidden": False,
                 "permanentEnemy": False, "settlementCount": 1},
                {"defName": "OtherFaction", "name": "Other", "isPlayer": False,
                 "hostile": True, "goodwill": -50, "hidden": False,
                 "permanentEnemy": False, "settlementCount": 2},
                {"defName": "ThirdFaction", "name": "Third", "isPlayer": False,
                 "hostile": False, "goodwill": 20, "hidden": False,
                 "permanentEnemy": False, "settlementCount": 2}],
                    "count": 3, "countReturned": 3, "countAllIncludingHidden": 3,
                    "isCompleteList": True, "settlementsTotal": 5,
                    "hiddenSkipped": 0, "filtered": 0, "truncated": 0}
        if tool == "jawa/order_pawn":
            # The stub must NOT answer yes to the zero-tick call: the check it
            # feeds asserts the tool refuses to call no movement a success.
            want = {"x": p.get("x"), "z": p.get("z")}
            if p.get("x") is None and not p.get("targetId"):
                return {"success": False, "message": "No destination. Pass 'x' and "
                                                     "'z' for a cell, or 'targetId'."}
            if p.get("pathEndMode") not in (None, "oncell", "touch", "closesttouch",
                                            "interactioncell", "none"):
                return {"success": False,
                        "message": "pathEndMode '%s' is not a mode." % p.get("pathEndMode")}
            if not p.get("waitTicks"):
                return {"success": False, "ticksElapsed": 0, "arrivedCount": 0,
                        "message": "0/1 pawn(s) standing on the cell after 0 "
                                   "tick(s). THE GAME DID NOT TICK",
                        "leftDrafted": [], "pawns": [
                            {"id": p.get("pawnId"), "canReach": True,
                             "orderAccepted": True, "arrived": False,
                             "start": {"x": 40, "z": 40}, "end": {"x": 40, "z": 40}}]}
            left = [] if p.get("undraftAfter") else [p.get("pawnId")]
            return {"success": True, "ticksElapsed": 240, "arrivedCount": 1,
                    "timedOut": False, "speedRestored": True,
                    "leftDrafted": left, "pawns": [
                        {"id": p.get("pawnId"), "name": "Tam", "canReach": True,
                         "orderAccepted": True, "arrived": True,
                         "start": {"x": 40, "z": 40}, "end": want}]}
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
            self._spawned += 1
            xeno = p.get("xenotype")
            return {"success": True, "spawnedCount": 1, "failedCount": 0,
                    "xenotypeRequested": xeno,
                    "pawns": [{"ok": True, "id": "Human%d" % self._spawned,
                               "faction": "Insect", "hostile": True,
                               "spawned": True, "xenotype": xeno or "Baseliner",
                               "xenotypeRequested": xeno,
                               "xenotypeApplied": True}]}
        if tool == "jawa/set_pawn_rotation":
            d = str(p.get("dir", "")).lower()
            if d == "unlock":
                return {"success": True, "turned": 1, "locked": False,
                        "pawns": [{"id": p.get("pawnId"), "applied": True,
                                   "after": self._rot, "locked": False,
                                   "posture": "Standing", "visible": True}]}
            self._rot = {"north": "North", "east": "East", "south": "South",
                         "west": "West"}.get(d, "South")
            return {"success": True, "turned": 1,
                    "locked": bool(p.get("lockRotation", True)),
                    "notVisible": 0,
                    "pawns": [{"id": p.get("pawnId"), "applied": True,
                               "after": self._rot,
                               "locked": bool(p.get("lockRotation", True)),
                               "posture": "Standing", "visible": True}]}
        if tool == "jawa/set_pawn_style":
            hair = p.get("hair")
            if hair and hair.startswith("NoSuch"):
                return {"success": False,
                        "message": "No HairDef named '%s'." % hair}
            changes = [{"field": "hair", "was": "Afro", "now": hair, "ok": True}]
            if p.get("hairColor"):
                changes.append({"field": "hairColor", "was": "1,1,1",
                                "now": "0.251,0.157,0.031", "ok": True})
            return {"success": True, "pawnsChanged": 1,
                    "pawns": [{"id": p.get("pawnId"), "ok": True,
                               "changes": changes}]}
        if tool == "jawa/set_pawn_xenotype":
            x = p.get("xenotype")
            if x != self._xenotype:
                return {"success": False,
                        "message": "No XenotypeDef named '%s'." % x}
            return {"success": True, "pawnsChanged": 1, "xenotype": x,
                    "pawns": [{"id": p.get("pawnId"), "ok": True,
                               "was": "Baseliner", "now": x, "requested": x,
                               "inheritable": False, "genesInDef": 5,
                               "endogenesBefore": 0, "endogenesAfter": 0,
                               "xenogenesBefore": 0, "xenogenesAfter": 5,
                               "endogenesCleared": 0, "hybrid": False,
                               "staleEndogenes": False}]}
        if tool == "jawa/damage":
            return {"success": True, "targetsHit": 1, "colonistsSkipped": 0,
                    "results": [{"id": "Human1", "totalDamageDealt": 60.0,
                                 "hediffsBefore": 4, "hediffsAfter": 6,
                                 "dead": True, "destroyed": True}]}
        return {"success": True}


def _run_all(s, letter=True, walk=True):
    have = census(s)
    prove_get_def(s, have)
    prove_drain_log(s, have)
    prove_list_pawns(s, have)
    prove_list_factions(s, have)
    prove_refresh_rect(s, have, 10, 10)
    prove_spawn_batch(s, have, 10, 10)
    prove_roofs(s, have, 10, 10)
    prove_set_plants(s, have, 10, 10)
    prove_gm(s, have, send_letter=letter)
    prove_pawns(s, have, 10, 10, walk=walk)


def selftest():
    """Exercise the GOOD path and the three bad ones.

    A stub that answers yes to everything only proves the happy path parses.
    The output that actually earns its keep is what this prints when the deploy
    did NOT take -- so those branches get run too, and the run fails if a
    scenario that should produce failures produces none.
    """
    global RESULTS
    scenarios = [
        ("all 22 registered", dict(), 0, None),
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
    ap.add_argument("--walk", action="store_true",
                    help="also drive jawa/order_pawn's real walk: draft a "
                         "colonist, send it 6 cells and back, undraft. Off by "
                         "default because it UNPAUSES the game for a few "
                         "seconds, which the script otherwise refuses to do.")
    ap.add_argument("--letter", action="store_true",
                    help="also send a real letter to the player's pane.")
    ap.add_argument("--selftest", action="store_true",
                    help="run against a stub. No game, no socket.")
    ap.add_argument("--census", action="store_true",
                    help="READ ONLY. Take the deploy census and exit before "
                         "anything is spawned, damaged, built or fired. Safe on "
                         "an irreplaceable map.")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    from core import Session                                   # noqa: E402
    with Session() as s:
        have = census(s)

        # 🔴 --census exits HERE, and the exit must come before the pause check
        # below, because that check is a guard on MUTATION and this path does
        # not mutate. Requiring a paused game to take a read would make the
        # safe option the harder one, which is how people end up running the
        # unsafe one.
        #
        # WHY THIS FLAG EXISTS. Everything after this point spawns pawns,
        # damages them to death, sets plants, builds roofs, fires incidents and
        # sends letters. The census was nonetheless described in a run sheet as
        # "read line 0" and scheduled against a brand-new campaign map that
        # cannot be regenerated. The selftest already scripts a "pawns STILL
        # ALIVE" cleanup failure, so litter is a known outcome, not a risk.
        # A gate that certifies a deploy must not be able to damage what it
        # certifies.
        if args.census:
            print("\n--census: read only, exiting before any mutation.")
            return summarise()

        # Read-only first: if the bridge is sick, find out before mutating.
        print("\n1. read-only tools")
        prove_get_def(s, have)
        prove_drain_log(s, have)
        prove_list_pawns(s, have)
        prove_list_factions(s, have)

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
            prove_pawns(s, have, args.x, args.z, walk=args.walk)
        else:
            skip("pawn spawn/damage", "needs --pawns")

    return summarise()


if __name__ == "__main__":
    sys.exit(main())
