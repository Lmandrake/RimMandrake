#!/usr/bin/env python3
"""load_session.py - drive one whole live session from a written script.

WHY THIS EXISTS
===============
A cold load on this stack is 23-30 minutes and it is the scarcest resource in
the project. The way it gets wasted is not by any single slow call: it is by
COMPOSING the calls while the game is up -- looking up a defName, guessing a
parameter, discovering halfway through that a thing was never deployed. All of
that is offline work being done at live prices.

So every item below is written, ordered and argued BEFORE the game boots, and
the session becomes "run this and look at the images".

    python.exe src/RimMandrake/bridgetools/load_session.py --phase any
    python.exe src/RimMandrake/bridgetools/load_session.py --phase fresh
    python3     src/RimMandrake/bridgetools/load_session.py --selftest

WHAT THIS SCRIPT WILL AND WILL NOT DECIDE
=========================================
🔴 **It does not adjudicate art.** Every visual check ends in `NEEDS EYES` plus
a screenshot path. A script cannot tell "the frame draws in front of the leaves"
from "it does not", and a script that claimed it could would be the exact
silent-success shape this seat exists to kill. It gathers evidence; a human or
an agent looking at the image decides.

It DOES decide anything with a read-back: a position, a terrain defName, a
faction list, a count. Those are PASS/FAIL here and need no eyes.

ORDERING, AND WHY IT IS NOT NEGOTIABLE
======================================
1. **Census first.** Nothing below is interpretable until the companion reports
   its full tool count. A missing tool means a stale deploy, and a stale deploy
   is a SHUTDOWN-window fix -- you want to learn that while the window is still
   open, not after the anchor load is spent.
2. **ANY_MAP items before worldgen.** They de-risk the tooling on a map we do
   not care about. If `order_pawn` is broken, that is better learned on a
   quicktest than on the world we just spent 25 minutes generating.
3. **FRESH_MAP items last**, because they are the ones that cannot be retried
   without paying again.

THE LEDGER IS THE DELIVERABLE
=============================
Everything lands in `observed/<date>_load_session.md`: one row per item, its
verdict, its evidence, and its screenshot path. The terminal gets one line per
item and nothing else -- `CLAUDE.md` forbids spewing to the owner's screen, and
a live session is exactly when that rule matters most.

LITTER
======
This seat's characteristic failure is leaving things on the map and forgetting
they are ours. Every spawn, paint and draft goes in `LITTER` and the ledger
prints it at the end, whether the run passed or not. The release message is
written FROM that list, not from memory.
"""
import argparse
import datetime
import os
import sys
import traceback

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils", "rimbench"))

ANY_MAP, FRESH_MAP = "any", "fresh"

# Verdicts. NEEDS_EYES is not a hedge -- it is the honest verdict for anything
# whose PASS condition is "it looks right", and it carries a path so the call
# is cheap to make.
PASS, FAIL, NEEDS_EYES, SKIP, ERROR = "PASS", "FAIL", "NEEDS EYES", "SKIP", "ERROR"

RESULTS = []
LITTER = []


def record(item_id, title, verdict, evidence="", shot=None):
    RESULTS.append(dict(id=item_id, title=title, verdict=verdict,
                        evidence=evidence, shot=shot))
    tail = ("   %s" % evidence) if evidence else ""
    print("  %-11s %-6s %s%s" % (verdict, item_id, title, tail))
    if shot:
        print("              shot: %s" % shot)


def litter(what, where=""):
    """Anything left on the map. Reconciled in the release message."""
    LITTER.append("%s%s" % (what, (" at %s" % where) if where else ""))


# --------------------------------------------------------------- gates

def census(s, expect=21):
    """THE gate. Every other result is uninformative until this passes.

    21 = the 2026-08-13 22:03 GM deploy, with jawa/order_pawn.
    19 = a build made without --gm; the GM pair was compiled out.
    20 = the build before order_pawn.  0 = the bundle never loaded.
    """
    names = {t.get("name") for t in s._rb.list_tools()}
    jawa = sorted(n for n in names if n and n.startswith("jawa/"))
    ok = len(jawa) == expect
    record("A0", "companion census", PASS if ok else FAIL,
           "%d jawa tools of %d expected (%d on the bridge overall)"
           % (len(jawa), expect, len(names)))
    if not ok:
        print("\n     *** STOP AND READ THIS ***")
        print("     The deployed companion is not the one this script was")
        print("     written against. A tool count that is too low is a STALE")
        print("     DEPLOY, and the DLL cannot be replaced while RimWorld runs.")
        print("     Fix it in the shutdown window:")
        print("       python.exe src/RimMandrake/bridgetools/build.py --gm --apply")
        print("     Missing: %s" % (set(EXPECTED_TOOLS) - set(jawa) or "none"))
    return set(jawa)


def playable(s):
    """Refuse to mutate a map that is not actually ready.

    `paused` lives on rimbridge/get_bridge_status, NOT on rimworld/get_game_info
    -- reading the wrong one gives paused=None forever. And mapCount > 0 is TRUE
    AND INSUFFICIENT: the map can exist while Find.CurrentMap is still null, at
    which point every companion tool fails with "No current map" and reads like
    a broken tool.
    """
    st = (s.call("rimbridge/get_bridge_status") or {}).get("state") or {}
    ready = st.get("currentMapReady") and not st.get("longEventPending")
    return ready, st


EXPECTED_TOOLS = [
    "jawa/set_terrain", "jawa/set_terrain_batch", "jawa/get_terrain_batch",
    "jawa/spawn_batch", "jawa/destroy_batch", "jawa/list_pawns",
    "jawa/set_plants", "jawa/damage", "jawa/get_def", "jawa/drain_log",
    "jawa/refresh_rect", "jawa/spawn_pawn", "jawa/set_pawn_style",
    "jawa/set_pawn_rotation", "jawa/set_pawn_xenotype", "jawa/fire_incident",
    "jawa/send_letter", "jawa/set_roof_batch", "jawa/get_roof_batch",
    "jawa/list_factions", "jawa/order_pawn",
]


# ----------------------------------------------------------------- items
#
# Each item is (id, phase, title, fn). `fn(s, cfg)` records its own verdict.
# Items must NOT raise on a bad result -- they record FAIL and return. Raising
# is reserved for the harness losing the bridge, which run() catches per item so
# one dead item cannot take the session with it.

def i_factions(s, cfg):
    """OuterRim_RebelAlliance: ABSENT IS THE DESIRED OUTCOME.

    🔴 I had this backwards and it would have raised a false alarm on a correct
    world. `queue/BRIDGE.md` B-new was written when the Rebel Alliance failing
    to generate was an unexplained mystery. It is not one any more: VISION R2
    ruled it stays suppressed, and `Jawa_Patches\\Patches\\RebelAlliance_Suppress.xml`
    exists to do exactly that. `WORLDGEN_FACTION_CHECKLIST.md:244` --
    "ABSENT is the DESIRED outcome ... do NOT revert the patch at the screen."

    So PRESENT is the failure here: it means the suppression patch did not take.
    The control is `OuterRim_GalacticEmpire`, which must be present -- that also
    closes the EXPECTED_FAILURES A3 gate in the same call.

    ⚠️ Nothing in Player.log reports a faction that simply fails to appear. That
    cuts both ways, which is why this is checked by name rather than inferred.
    """
    r = s.call("jawa/list_factions", includeHidden=True)
    rows = (r or {}).get("factions") or []
    names = {f.get("defName") for f in rows}
    want = "OuterRim_RebelAlliance"
    control = "OuterRim_GalacticEmpire"
    here, ctrl = want in names, control in names
    record("A1", "Rebel Alliance stays suppressed", FAIL if here else PASS,
           "%s %s (absent is CORRECT, VISION R2); %d factions, "
           "countAllIncludingHidden=%s"
           % (want, "PRESENT -- suppression patch did not take" if here
              else "absent",
              len(rows), (r or {}).get("countAllIncludingHidden")))
    record("A1b", "  ...control: Galactic Empire generated",
           PASS if ctrl else FAIL,
           "%s %s" % (control, "present" if ctrl else "ABSENT"))


def i_pilot_console(s, cfg):
    """CREATE item 6. The cheapest gate we have: a predicate on a paused game.

    RimWorld's own launch gate is
      ReachabilityUtility.CanReach(pawn, console, PathEndMode.InteractionCell,
                                   Danger.Deadly, false, false, ByPawn)
    at RitualBehaviorWorker_GravshipLaunch::PawnCanFillRole IL_0065-006A,
    emitting "NoPathToPilotConsole" at IL_0072. targetId + the default
    pathEndMode reproduce that call exactly.

    ⚠️ OnCell would answer a NEIGHBOURING question -- a pawn can reach the cell
    beside a console and still fail InteractionCell. Do not "simplify" this to
    x/z. traps.md, "A correct measurement of the WRONG predicate".
    """
    consoles = [t for t in ((s.call("jawa/list_pawns") or {}).get("pawns") or [])]
    del consoles                                   # pawns are not the target
    found = s.call("rimworld/get_cell_info", x=cfg.x, z=cfg.z)
    del found
    cid = cfg.console_id
    if not cid:
        return record("A2", "NoPathToPilotConsole", SKIP,
                      "no --console-id given; find the PilotConsole ThingID "
                      "first (select it in game, or spawn one)")
    r = s.call("jawa/order_pawn", pawnId="colonists", targetId=cid,
               waitTicks=0, unpause=False)
    rows = (r or {}).get("pawns") or []
    reach = [p for p in rows if p.get("canReach")]
    record("A2", "NoPathToPilotConsole", PASS if reach else FAIL,
           "%d of %d colonists reach %s (pathEndMode=%s). No movement, "
           "game left paused."
           % (len(reach), len(rows), (r or {}).get("targetLabel"),
              (r or {}).get("pathEndMode")))


def i_dune_seas(s, cfg):
    """v1 row 4, the dune-seas override. NOT an eyeball check.

    V1_SCOPE ruled this closes on a live `terrainPatchMakers` read -- SoftSand's
    `min` widened from vanilla 0.65 to 0.55 (Desert) and 0.50 (ExtremeDesert) --
    because a 15% density change is not judgeable by looking at a map.

    🔴 That gate had NO COLLECTABLE EVIDENCE until 2026-08-13. `jawa/get_def`
    built its `extra` block for ThingDefs only, so a BiomeDef came back as label
    plus description and nothing else. The field was added rather than the gate
    weakened. Needs no map at all -- defs are loaded before any map exists.

    ⚠️ Patchmaker ORDER matters: the first threshold whose band contains the
    noise value wins. The index is reported; do not sort the list.
    """
    want = {"Desert": 0.55, "ExtremeDesert": 0.50}
    for biome, target in sorted(want.items()):
        r = s.call("jawa/get_def", defName=biome, defType="BiomeDef")
        extra = (r or {}).get("extra") or {}
        pms = extra.get("terrainPatchMakers")
        if pms is None:
            record("A5", "dune seas %s" % biome, FAIL,
                   "get_def returned no terrainPatchMakers -- the companion "
                   "predates the BiomeDef branch. Census said 21; check the deploy.")
            continue
        soft = [(pm.get("index"), t.get("min"))
                for pm in pms
                for t in (pm.get("thresholds") or [])
                if t.get("terrain") == "SoftSand"]
        hit = any(abs((m or 0) - target) < 0.001 for _, m in soft)
        record("A5", "dune seas widened in %s" % biome, PASS if hit else FAIL,
               "SoftSand min = %s, want %.2f (vanilla 0.65); %d patchmaker(s)"
               % (", ".join("pm%s:%s" % (i, m) for i, m in soft) or "not found",
                  target, extra.get("patchMakerCount")))


def i_row5_xenotype(s, cfg):
    """v1 row 5. WHICH Jawa xenotype a pawn actually carries.

    Three are live at once, so "a Jawa spawned" is not evidence. It closes on
    `BTD_Jawa`: BTD Xenotype Remix rewrites the xenotype set AT LOAD (250 -> 150)
    and `OuterRim_Jawa` does not survive the dedup, so our patches target the
    right thing only if the live pawn reads BTD_Jawa.

    🔴 Until 2026-08-13 this row had NO collectable evidence. `list_pawns` did
    not return a xenotype, so the only read-back was `set_pawn_xenotype`'s `was`
    field -- i.e. CONVERTING a campaign pawn in order to discover what it
    already was. A mutation to answer a read is not an acceptable gate, so the
    field was added to `list_pawns` instead and this item is now read-only.

    ⚠️ `xenotype: null` is not "no xenotype": a pawn with no gene tracker and a
    baseliner both read null. `hasGenes` separates them.
    """
    r = s.call("jawa/list_pawns", limit=500)
    rows = (r or {}).get("pawns") or []
    if rows and "xenotype" not in rows[0]:
        return record("A3", "row 5 xenotype read-back", FAIL,
                      "list_pawns returned no `xenotype` key -- the companion "
                      "predates the field. Census said 21; check the deploy.")
    jawas = [p for p in rows
             if "jawa" in str(p.get("xenotype", "")).lower()
             or "jawa" in str(p.get("kind", "")).lower()]
    kinds = {}
    for p in jawas:
        k = p.get("xenotype") or ("baseliner" if p.get("hasGenes") else "no genes")
        kinds[k] = kinds.get(k, 0) + 1
    want = "BTD_Jawa"
    record("A3", "row 5: which Jawa xenotype",
           PASS if kinds.get(want) else FAIL,
           "%d Jawa-ish pawns of %d on map; xenotypes: %s (row closes on %s)"
           % (len(jawas), len(rows),
              ", ".join("%s x%d" % kv for kv in sorted(kinds.items())) or "none",
              want))


def i_salt_crust(s, cfg):
    """B-v1, the owner's live terrain edit. Proves the def and the art.

    ⚠️ terrainDef, NOT def. An unknown parameter name is dropped silently
    before the tool runs, so `def=` would paint nothing and report success.
    """
    x, z, w, h = cfg.x, cfg.z, 10, 10
    before = s.call("jawa/get_terrain_batch", rects="%d,%d,%d,%d" % (x, z, w, h))
    r = s.call("jawa/set_terrain", x=x, z=z, terrainDef="Jawa_SaltCrust",
               width=w, height=h)
    after = s.call("jawa/get_terrain_batch", rects="%d,%d,%d,%d" % (x, z, w, h))
    changed = (r or {}).get("cellsChanged") or (r or {}).get("changed") or 0
    litter("Jawa_SaltCrust painted %dx%d" % (w, h), "(%d,%d)" % (x, z))
    hit = "Jawa_SaltCrust" in str(after)
    record("A3", "Jawa_SaltCrust paints", PASS if (changed and hit) else FAIL,
           "cellsChanged=%s, read-back contains the def: %s. Restore ops "
           "captured for undo." % (changed, hit))
    record("A3b", "  ...restore string", SKIP,
           "captured %d chars; feed back to jawa/set_terrain_batch to undo"
           % len(str((before or {}).get("ops") or "")))
    shot = s.look(x + w // 2, z + h // 2, name="saltcrust", zoom=13)
    record("A3c", "  ...and it reads as evaporite, not sand", NEEDS_EYES,
           "reuses Odyssey Terrain/Surfaces/DryLakeBed -- looking like a dry "
           "lake bed is CORRECT, not a bug", shot)


def i_order_pawn_walk(s, cfg):
    """B4. The tool is built, deployed and has never moved a pawn.

    TryTakeOrderedJob returns true for a job it merely ENQUEUED and never
    consults reachability, so arrival is the only evidence that counts.
    """
    lp = s.call("jawa/list_pawns", faction="player")
    cands = [p for p in ((lp or {}).get("pawns") or [])
             if not p.get("dead") and not p.get("downed") and p.get("id")]
    if not cands:
        return record("A4", "order_pawn moves a pawn", SKIP,
                      "no standing player pawn")
    c = cands[0]
    cid, hx, hz = c["id"], c["x"], c["z"]
    out = s.call("jawa/order_pawn", pawnId=cid, x=hx + 6, z=hz,
                 waitTicks=240, timeoutSeconds=20, draft=True)
    row = ((out or {}).get("pawns") or [{}])[0]
    litter("drafted %s" % c.get("name"), "(%d,%d)" % (hx, hz))
    record("A4", "order_pawn moves a pawn",
           PASS if row.get("arrived") else FAIL,
           "%s %s -> %s, ticksElapsed=%s, canReach=%s"
           % (c.get("name"), row.get("start"), row.get("end"),
              (out or {}).get("ticksElapsed"), row.get("canReach")))
    back = s.call("jawa/order_pawn", pawnId=cid, x=hx, z=hz, waitTicks=240,
                  timeoutSeconds=20, draft=True, undraftAfter=True)
    brow = ((back or {}).get("pawns") or [{}])[0]
    clean = brow.get("arrived") and not ((back or {}).get("leftDrafted") or [])
    if clean:
        LITTER.remove("drafted %s at (%d,%d)" % (c.get("name"), hx, hz))
    record("A4b", "  ...and put back, undrafted", PASS if clean else FAIL,
           "home=(%d,%d) end=%s leftDrafted=%s"
           % (hx, hz, brow.get("end"), (back or {}).get("leftDrafted")))


def i_desert_worldgen(s, cfg):
    """v1 row 7. Ordinary desert worldgen confirmed ON THE MAP.

    A biome def existing is not the observation. The terrain under the camera is.
    """
    rect = "%d,%d,%d,%d" % (cfg.x, cfg.z, 32, 32)
    t = s.call("jawa/get_terrain_batch", rects=rect)
    ops = str((t or {}).get("ops") or "")
    kinds = {}
    for chunk in ops.split(";"):
        name = chunk.split(":")[0].strip()
        if name:
            kinds[name] = kinds.get(name, 0) + 1
    top = sorted(kinds.items(), key=lambda kv: -kv[1])[:5]
    record("F1", "row 7 desert terrain on the map",
           PASS if kinds else FAIL,
           "top terrains in a 32x32 at (%d,%d): %s"
           % (cfg.x, cfg.z, ", ".join("%s x%d" % kv for kv in top) or "none"))
    shot = s.look(cfg.x + 16, cfg.z + 16, name="row7_desert", zoom=15)
    record("F1b", "  ...and it READS as desert", NEEDS_EYES, "", shot)


ITEMS = [
    ("A1", ANY_MAP, "Rebel Alliance faction watch", i_factions),
    ("A2", ANY_MAP, "NoPathToPilotConsole predicate", i_pilot_console),
    ("A4", ANY_MAP, "order_pawn walks and returns", i_order_pawn_walk),
    # A3 is NOT the salt-crust paint. That PASSED live already
    # (queue/CREATE.md:38, V1_SCOPE row 4 "1 of 3 SEEN"), so re-proving the def
    # and the art would be spending live time on a closed row. What is still
    # open is VISION's B-v1 CAPABILITY question, which is a different thing.
    # Row 5 was RULED CLOSED by PROJECT (V1_SCOPE.md:608-633) -- BTD_Jawa
    # survives the BTD dedup and the pawnkind pins were remapped onto it,
    # measured live from Player.log. `i_row5_xenotype` stays in this file
    # because the read is now free and would turn "measured from the log" into
    # "measured from the pawn", but it does NOT run by default: a closed row
    # must not spend live time.
    ("A5", ANY_MAP, "dune seas: BiomeDef terrainPatchMakers", i_dune_seas),
    # ⛔ Row 7 / rows 2 / Configure Factions are HELD BY THE OWNER -- the sea
    # spec is unsolved and the click is irreversible. Not this session.
    # FRESH_MAP now means a QUICKTEST, which rule 1c permits freely and which
    # `CREATE_TEST_PLAN.md:99-101` accepts for the map-generation overrides.
    # The ground hulk and the scrapfields are both registered on
    # MapGeneratorDef[Base_Player] with NO biome filter, so they fire on any
    # quicktest. Salt pans and dune seas are biome-patched and only appear if
    # the quicktest happens to land on Desert/ExtremeDesert/AridShrubland --
    # a non-desert quicktest is not a failure of those two.
    ("F1", FRESH_MAP, "v1 row 7 desert worldgen (HELD -- do not run)",
     i_desert_worldgen),
]


# ------------------------------------------------------------------- run

def run(s, cfg):
    have = census(s)
    if not have:
        return
    ready, st = playable(s)
    if not ready:
        print("\n*** MAP IS NOT CURRENT YET ***")
        print("     mapCount=%s currentMapReady=%s longEventPending=%s"
              % (st.get("mapCount"), st.get("currentMapReady"),
                 st.get("longEventPending")))
        print("Companion tools would fail with 'No current map', which reads")
        print("like a broken tool and is not one. Wait, then re-run.")
        return

    for item_id, phase, title, fn in ITEMS:
        if cfg.phase != "all" and phase != cfg.phase:
            record(item_id, title, SKIP, "phase=%s, this run is %s"
                   % (phase, cfg.phase))
            continue
        try:
            fn(s, cfg)
        except Exception as e:                     # one dead item, not a dead run
            record(item_id, title, ERROR, "%s: %s" % (type(e).__name__,
                                                      str(e)[:160]))
            if cfg.trace:
                traceback.print_exc()


def ledger(cfg):
    """Write the deliverable. The terminal got one line per item; this is where
    the detail goes, because a live session is exactly when the owner's screen
    must not be spewed to."""
    day = cfg.date or datetime.datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(_ROOT, "observed", "%s_load_session.md" % day)
    counts = {}
    for r in RESULTS:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    lines = ["# Live session ledger - %s" % day, "",
             "_Written by `src/RimMandrake/bridgetools/load_session.py`. "
             "`NEEDS EYES` is a real verdict: the evidence is collected and the "
             "picture has not been looked at yet._", "",
             "  ".join("**%s** %d" % (k, v) for k, v in sorted(counts.items())),
             "", "| id | verdict | item | evidence |", "|---|---|---|---|"]
    for r in RESULTS:
        lines.append("| %s | %s | %s | %s |"
                     % (r["id"], r["verdict"], r["title"],
                        r["evidence"].replace("|", "/")))
    shots = [r for r in RESULTS if r["shot"]]
    if shots:
        lines += ["", "## Screenshots - open these", ""]
        lines += ["- `%s` - %s" % (r["shot"], r["title"]) for r in shots]
    lines += ["", "## Left on the map", ""]
    lines += (["- %s" % x for x in LITTER] if LITTER else
              ["Nothing. Every mutation was reverted in-run."])
    lines += ["", "⚠️ **The release message is written from the list above, "
              "not from memory.**", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def selftest():
    """Exercise the ledger and the verdict plumbing with no game and no socket.

    The point is that a live session is not spent debugging this file.
    """
    record("A0", "companion census", PASS, "21 jawa tools of 21")
    record("A1", "Rebel Alliance generated", FAIL, "ABSENT; control present")
    record("A3c", "reads as evaporite", NEEDS_EYES, "", "C:/shots/salt_001.png")
    record("F1", "row 7 desert terrain", SKIP, "phase=fresh")
    litter("Jawa_SaltCrust painted 10x10", "(100,100)")
    cfg = argparse.Namespace(date="0000-00-00", phase="all", x=0, z=0,
                             console_id=None, trace=False)
    p = ledger(cfg)
    body = open(p, encoding="utf-8").read()
    bad = 0
    for must in ("NEEDS EYES", "Left on the map", "Jawa_SaltCrust painted",
                 "salt_001.png", "| A1 | FAIL |"):
        if must not in body:
            print("  SELFTEST BUG: ledger is missing %r" % must)
            bad += 1
    print("\nSELFTEST %s -- ledger at %s" % ("FAILED" if bad else "OK", p))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=[ANY_MAP, FRESH_MAP, "all"],
                    default=ANY_MAP,
                    help="'any' runs what needs no fresh map -- run this FIRST, "
                         "before worldgen, so a tooling problem is found while "
                         "the shutdown window is still open.")
    ap.add_argument("--x", type=int, default=100, help="working cell X")
    ap.add_argument("--z", type=int, default=100, help="working cell Z")
    ap.add_argument("--console-id",
                    help="ThingID of the PilotConsole, for the "
                         "NoPathToPilotConsole predicate")
    ap.add_argument("--date", help="override the ledger date stamp")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="no game, no socket")
    cfg = ap.parse_args(argv)

    if cfg.selftest:
        return selftest()

    from core import Session                                   # noqa: E402
    with Session(strict=False) as s:
        run(s, cfg)
    path = ledger(cfg)
    fails = [r for r in RESULTS if r["verdict"] in (FAIL, ERROR)]
    eyes = [r for r in RESULTS if r["verdict"] == NEEDS_EYES]
    print("\n%d item(s), %d failed, %d awaiting a look" %
          (len(RESULTS), len(fails), len(eyes)))
    print("ledger: %s" % path)
    if LITTER:
        print("LEFT ON THE MAP (say this in the release message):")
        for x in LITTER:
            print("  - %s" % x)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
