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

🔴 **"IT LOOKED FINE" IS A RESULT. WRITE IT DOWN.** Owner's directive, 2026-08-13:
all new art fixes are stopped until someone verifies the art was actually broken,
because the missing-art premise is itself suspect. So a row that comes back
looking NORMAL is the evidence being asked for, not a check that failed to fire.
This is the null-baseline problem in another costume -- without knowing what the
UNFIXED art looks like, a fix that changed nothing is indistinguishable from a
fix that worked. Record what you saw either way.

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
import time
import traceback

# 🔴 Windows console defaults to cp1252, and a def label with a non-cp1252
# character (VAEA/RR apparel, Cherry Picker's removal list) raises
# UnicodeEncodeError *inside the print*, AFTER the tool call succeeded but
# BEFORE the item asserts. The item is then reported ERROR and counted as a
# failure, when in truth it was never measured. Measured 2026-08-14: A6 and P5
# both died this way, and the same bug class silently hid a spawn failure
# earlier the same day. An unreadable result must never look like a failed one.
# errors="replace" so a stray glyph degrades to '?' instead of killing a run
# that cost a 25-minute cold load.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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


def ok(r):
    """The call RAN and reported success. Every jawa tool sets `success = true`
    explicitly, so anything else is a NO-ANSWER, not a no."""
    return bool(r) and r.get("success") is True


def absent(r):
    """`get_def` failed *because the def is not in the DefDatabase* -- as opposed
    to any other reason the call came back false.

    🔴 The two are not the same verdict and the payload is nearly identical.
    `No <defType> named '<defName>'.` is a real absence; `No def type named
    '<defType>'.` is a typo in MY question, and a timeout is no reading at all.
    Reading either of the last two as absence is this seat's standing failure --
    an absent input scored as an empty one -- and in group A below absence is the
    PASS, so the mistake manufactures a green row out of a broken call."""
    if ok(r):
        return False
    msg = str((r or {}).get("message") or "")
    return " named " in msg and not msg.startswith("No def type named")


# --------------------------------------------------------------- gates

def census(s, expect=None):
    """THE gate. Every other result is uninformative until this passes.

    24 = the current GM deploy, with jawa/get_defs and jawa/fire_quest.
    22 = the build before them.  21 = before world_stats.  20 = before order_pawn.
    22 with the GM pair missing = a build made without --gm.
    0 = RimBridgeServer never loaded the bundle at all.

    🔴 The number is DERIVED from EXPECTED_TOOLS, never written twice. Three
    documents disagreed about it on 2026-08-13 (17 / 20 / 21) and it moved again
    the same night; a gate two files answer differently is worse than no gate.
    """
    if expect is None:
        expect = len(EXPECTED_TOOLS)
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


def settle(s, cfg):
    """🔴 THE BRIDGE ANSWERING IS NOT THE GAME BEING REACTIVE.

    Owner, 2026-08-14: the game does not really become reactive until about
    FORTY SECONDS after the bridge first responds. Every readiness flag we have
    -- `currentMapReady`, `longEventPending`, `playable` -- can be satisfied
    inside that window, so a script that trusts them alone starts mutating into
    a game that is still settling and gets results it cannot attribute.

    This is the same shape as every other entry in traps.md: a signal that says
    the TOOL is ready being read as the GAME being ready. Read-only calls are
    fine during it; mutation waits.
    """
    if cfg.settle <= 0:
        return
    waited = 0
    while waited < cfg.settle:
        time.sleep(2)
        waited += 2
    record("A0b", "settle window", PASS,
           "waited %ds after first bridge contact before mutating (owner: the "
           "game is not reactive for ~40s, whatever the ready flags say)"
           % waited)


def playable(s):
    """Refuse to mutate a map that is not actually ready.

    `paused` lives on rimbridge/get_bridge_status, NOT on rimworld/get_game_info
    -- reading the wrong one gives paused=None forever. And mapCount > 0 is TRUE
    AND INSUFFICIENT: the map can exist while Find.CurrentMap is still null, at
    which point every companion tool fails with "No current map" and reads like
    a broken tool.
    """
    r = s.call("rimbridge/get_bridge_status") or {}
    # 🔴 CHECK `success` BEFORE READING ANY FLAG. Measured live 2026-08-14: while
    # the game is still coming up this call returns
    #   success: false, "Timed out waiting for main-thread work after 5000ms"
    # with NO `state` object at all. Reading straight through gives
    # currentMapReady=None, mapCount=None, paused=None -- which is
    # indistinguishable from "a map has not loaded yet" and is actually "the
    # question was never asked". Two states, one face. The tool metadata answers
    # throughout, because listing tools never touches the main thread, so the
    # bridge looks entirely healthy while nothing simulation-side can run.
    if r.get("success") is False:
        return False, {"_callFailed": True,
                       "_message": str(r.get("message"))[:160]}
    st = r.get("state") or {}
    ready = st.get("currentMapReady") and not st.get("longEventPending")
    return ready, st


EXPECTED_TOOLS = [
    "jawa/set_terrain", "jawa/set_terrain_batch", "jawa/get_terrain_batch",
    "jawa/spawn_batch", "jawa/destroy_batch", "jawa/list_pawns",
    "jawa/set_plants", "jawa/damage", "jawa/get_def", "jawa/drain_log",
    "jawa/refresh_rect", "jawa/spawn_pawn", "jawa/set_pawn_style",
    "jawa/set_pawn_rotation", "jawa/set_pawn_xenotype", "jawa/fire_incident",
    "jawa/send_letter", "jawa/set_roof_batch", "jawa/get_roof_batch",
    "jawa/list_factions", "jawa/order_pawn", "jawa/world_stats",
    # ✅ Deployed 2026-08-14 in the shutdown window; the game copy measures 24,
    # md5 ea5952e2, and both names are in it. The gate is raised in the SAME
    # commit as the deploy and never before it -- a gate ahead of the deploy
    # fails a CORRECT companion, which is the false alarm that stops a census
    # from being believed at all.
    "jawa/get_defs", "jawa/fire_quest",
    # Same window, same rule: deployed BEFORE this line was written. md5 55b2362.
    "jawa/list_things", "jawa/clear_ui",
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
    world. A retired seat's queue, item B-new, was written when the Rebel Alliance failing
    to generate was an unexplained mystery. It is not one any more: ruling R2
    ruled it stays suppressed, and `Jawa_Patches\\Patches\\RebelAlliance_Suppress.xml`
    exists to do exactly that. `WORLDGEN_FACTION_CHECKLIST.md:244` --
    "ABSENT is the DESIRED outcome ... do NOT revert the patch at the screen."

    So PRESENT is the failure here: it means the suppression patch did not take.
    The control is vanilla `Empire`, which must be present -- that also closes the
    EXPECTED_FAILURES A3 live half in the same call.

    🔴 CONTROL RE-POINTED 2026-08-20, owner's ruling: "OuterRim_GalacticEmpire is
    no longer in the game, we patch Empire." The control USED to be
    `OuterRim_GalacticEmpire`; that def is a mod faction nothing patches and nothing
    in the design uses, so its presence or absence proved nothing about our world.
    The Galactic Empire is vanilla `Empire` (Royalty), reskinned by
    `Jawa_Patches/Patches/GalacticEmpire.xml`.
    See infrastructure/state/OWNER_DECISIONS.md.

    ⚠️ The substitution is a plain string membership test against the defNames
    `jawa/list_factions` returns -- nothing else in this item depends on the value.

    ⚠️ Nothing in Player.log reports a faction that simply fails to appear. That
    cuts both ways, which is why this is checked by name rather than inferred.
    """
    r = s.call("jawa/list_factions", includeHidden=True)
    rows = (r or {}).get("factions") or []
    names = {f.get("defName") for f in rows}
    want = "OuterRim_RebelAlliance"
    control = "Empire"          # vanilla Royalty vessel; see docstring (2026-08-20)
    here, ctrl = want in names, control in names
    record("A1", "Rebel Alliance stays suppressed", FAIL if here else PASS,
           "%s %s (absent is CORRECT, ruling R2); %d factions, "
           "countAllIncludingHidden=%s"
           % (want, "PRESENT -- suppression patch did not take" if here
              else "absent",
              len(rows), (r or {}).get("countAllIncludingHidden")))
    record("A1b", "  ...control: Galactic Empire generated",
           PASS if ctrl else FAIL,
           "%s %s" % (control, "present" if ctrl else "ABSENT"))


def i_pilot_console(s, cfg):
    """A retired seat's item 6. The cheapest gate we have: a predicate on a paused game.

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
    cid = cfg.console_id
    if not cid:
        # 🔴 This USED to be a flat SKIP: "find the ThingID first (select it in
        # game)". A v1 launch gate was lost on 2026-08-14 to exactly that, because
        # nothing on the bridge could produce a ThingID for a non-pawn and a human
        # at the keyboard was the only source. `jawa/list_things` is that source
        # now, so the id is looked up instead of demanded.
        # Vanilla defName read from Odyssey/Defs/ThingDefs_Buildings/
        # Buildings_Gravship.xml, not recalled.
        found = s.call("jawa/list_things", defName="PilotConsole", limit=5)
        rows = (found or {}).get("things") or []
        if not rows:
            # ⚠️ Distinguish "no console on this map" from "the call did not run".
            # They read identically here and have completely different fixes.
            why = ("no PilotConsole on this map (%d thing(s) examined)"
                   % (found or {}).get("scanned", -1)) if ok(found) else \
                  ("list_things did not run: %s"
                   % str((found or {}).get("message"))[:80])
            return record("A2", "NoPathToPilotConsole", SKIP, why)
        cid = rows[0]["id"]
        record("A2p", "  ...console located", PASS,
               "%s id=%s at (%s,%s)" % (rows[0].get("def"), cid,
                                        rows[0].get("x"), rows[0].get("z")))
    r = s.call("jawa/order_pawn", pawnId="colonists", targetId=cid,
               waitTicks=0, unpause=False)
    rows = (r or {}).get("pawns") or []
    reach = [p for p in rows if p.get("canReach")]
    record("A2", "NoPathToPilotConsole", PASS if reach else FAIL,
           "%d of %d colonists reach %s (pathEndMode=%s). No movement, "
           "game left paused."
           % (len(reach), len(rows), (r or {}).get("targetLabel"),
              (r or {}).get("pathEndMode")))


def i_cherry_picker(s, cfg):
    """Filed by a retired seat. SILENCE IS NOT CONFIRMATION here.

    Cherry Picker logs `" - FAILED: <key>"` only when a def was FOUND and
    RemoveDef threw. An unresolvable key and a def outside its `allDefs` scope
    are both **completely silent** -- so a clean log is consistent with every
    removal having worked and with none of them having worked.

    🔴 And one line means total loss, not partial: `Error processing master def
    list` means EVERY removal was lost, not the one that broke. Worth a call on
    its own because nothing else surfaces it.
    """
    r = s.call("jawa/drain_log", limit=200, contains="Cherry Picker")
    msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
    fatal = [m for m in msgs if "Error processing master def list" in m]
    failed = [m for m in msgs if "FAILED:" in m]
    record("A6", "Cherry Picker: no total-loss line",
           FAIL if fatal else PASS,
           "%d Cherry Picker line(s); %d FAILED; %s"
           % (len(msgs), len(failed),
              "🔴 MASTER DEF LIST ERROR -- every removal was lost"
              if fatal else "no master-list error"))
    if failed:
        record("A6b", "  ...per-key failures", FAIL, "; ".join(failed)[:200])
    record("A6c", "  ...and silence proves nothing", SKIP,
           "an unresolvable key logs NOTHING. The keys are read back below.")
    cherry_keys(s, cfg)


def i_world_stats(s, cfg):
    """The owner's sea spec, measured instead of argued.

    Spec: about a quarter ocean, in three oddly-shaped bodies. The generator
    unaided gives 43-55% in scattered blobs, and ocean is an elevation rule at
    worldgen step 0 that no setting moves.

    ⚠️ The body count is the half that matters. Two worlds can report an
    identical waterPct and be nothing alike -- three oceans versus the same
    water smeared into forty puddles. `bodiesOverMinSize`, not `bodiesTotal`.

    ⚠️ On a QUICKTEST this measures whatever default world the quicktest made,
    which is not a campaign world. Say which it was; a quicktest and a campaign
    are different claims, not different confidence in one claim.
    """
    r = s.call("jawa/world_stats", minBodySize=8, limit=25)
    if not ok(r):
        return record("A7", "world_stats", FAIL,
                      str((r or {}).get("message"))[:120])
    wp = r.get("waterPct")
    big = r.get("bodiesOverMinSize")
    near = (wp is not None and 20 <= wp <= 30)
    record("A7", "sea vs the owner's spec (~25%, 3 bodies)",
           PASS if (near and big == 3) else NEEDS_EYES,
           "water %s%% in %s bodies >=8 tiles (%s total), largest %s%% of "
           "planet; seed=%s coverage=%s. Spec is ~25%% in 3."
           % (wp, big, r.get("bodiesTotal"), r.get("largestBodyPct"),
              r.get("seedString"), r.get("planetCoverage")))


def i_dune_seas(s, cfg):
    """v1 row 4, the dune-seas override. NOT an eyeball check.

    This closes on a live `terrainPatchMakers` read -- SoftSand's
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
            record("A5-%s" % biome, "dune seas %s" % biome, FAIL,
                   "get_def returned no terrainPatchMakers -- the companion "
                   "predates the BiomeDef branch. Census said 21; check the deploy.")
            continue
        soft = [(pm.get("index"), t.get("min"))
                for pm in pms
                for t in (pm.get("thresholds") or [])
                if t.get("terrain") == "SoftSand"]
        hit = any(abs((m or 0) - target) < 0.001 for _, m in soft)
        record("A5-%s" % biome, "dune seas widened in %s" % biome,
               PASS if hit else FAIL,
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


# TEST_PLAN.md Part 1. That plan owns WHAT to look at; this table owns the
# driving. Names are the corrected ones -- `ToolBelt` does not exist anywhere and
# the research kits are APPAREL, whose fix touches wornGraphicPath, not the
# directionless ground texPath.
#   (id, defName, kind, note printed with the shot)
ART_ROWS = [
    ("P1", "AV_DogSled", "vehicle",
     "VehicleDef, not a ThingDef. Want TWO EOPIE not four dogs, and a BROWN "
     "body -- the brown is a def patch (graphicData/color 99,65,24), so grey "
     "means the patch did not apply, NOT that the art is wrong."),
    ("P2", "PH_DoorBlastCDoor", "building", "rotated EAST, open and closed"),
    ("P3", "PH_DoorThickBlastBDoor", "building", "rotated EAST, open and closed"),
    ("P4", "PH_DoorBlastDDoor", "building", "EAST; the iris ring must survive"),
    ("P5", "VAEA_Apparel_ToolBelt", "apparel-worn",
     "⚠️ NOT `ToolBelt`, which exists nowhere. Two mods label an item 'tool "
     "belt', so never spawn this by label. WORN, pawn facing WEST."),
    ("P6", "RR_FieldResearchKitSimple", "apparel-worn", "WORN, facing EAST"),
    ("P7", "RR_FieldResearchKitHiTech", "apparel-worn", "WORN, facing EAST"),
    ("P8", "RR_FieldResearchKitMultiAnalyzer", "apparel-worn", "WORN, facing EAST"),
    ("P9", "RR_FieldResearchKitRemote", "apparel-worn", "WORN, facing EAST"),
    ("P10", "VGE_Astronaut", "pawn",
     "facing NORTH, and spawn BOTH life stages -- the adult's north was never "
     "broken, so a juvenile-only shot can pass on art nobody fixed"),
    ("P11", "OuterRim_MSEDroid", "pawn", "facing NORTH"),
    ("P12", "OuterRim_CereanMane", "hair", "facing SOUTH; donor is 1,514 B of "
     "fully transparent pixels, so the failure is a bald head"),
    ("P13", "VRESaurids_Littlefoot", "hair", "facing NORTH; centre frill"),
]


def i_art_rows(s, cfg):
    """Part 1. Spawn or dress, point the camera, shoot, and DO NOT judge.

    ⚠️ Apparel has no bridge tool. The only route is `rimworld/select_pawn`
    then the `Actions\\Wear apparel (selected)...` debug action, which works on
    PLAYER COLONISTS ONLY -- so the wearer must be spawned faction=player. Rows
    marked apparel-worn are recorded SKIP with that note rather than silently
    shot on the ground: the ground sprite is a different, unfixed texture, and
    photographing it would be a false PASS.
    """
    bx, bz = cfg.x, cfg.z + 20
    step = 6
    for n, (rid, defName, kind, note) in enumerate(ART_ROWS):
        x, z = bx + (n % 6) * step, bz + (n // 6) * step
        try:
            if kind == "apparel-worn":
                # No apparel tool exists on the bridge. The only route is
                # select_pawn + the `Actions\\Wear apparel (selected)...` debug
                # action, which accepts PLAYER COLONISTS ONLY.
                sp = s.call("jawa/spawn_pawn", kindDef=cfg.wearer, x=x, z=z,
                            faction="player", count=1)
                row = ((sp or {}).get("pawns") or [{}])[0]
                pid = row.get("id")
                if not pid:
                    record(rid, defName, FAIL,
                           "could not spawn a wearer (%s): %s"
                           % (cfg.wearer, str((sp or {}).get("message"))[:80]))
                    continue
                litter("pawn %s (%s wearer)" % (pid, defName), "(%d,%d)" % (x, z))
                # rimworld/* wants Thing_-prefixed ids; jawa/* returns bare.
                s.call("rimworld/select_pawn", pawnId="Thing_" + pid)
                s.call("rimworld/execute_debug_action",
                       path="Actions" + chr(92) + "Wear apparel (selected)..."
                            + chr(92) + defName)
                face = "west" if defName.startswith("VAEA") else "east"
                s.call("jawa/set_pawn_rotation", pawnId=pid, dir=face,
                       lockRotation=True)
                shot = s.look(x, z, name=rid.lower(), zoom=11)
                # 🔴 debugRotLocked is written by Thing.ExposeData and survives a
                # save/load. Unlock every pawn we froze, in the same breath.
                s.call("jawa/set_pawn_rotation", pawnId=pid, dir="unlock")
                record(rid, defName, NEEDS_EYES,
                       "WORN, facing %s. %s" % (face.upper(), note), shot)
                continue

            if kind in ("pawn", "hair"):
                kd = defName if kind == "pawn" else cfg.wearer
                sp = s.call("jawa/spawn_pawn", kindDef=kd, x=x, z=z,
                            faction="player", count=1)
                row = ((sp or {}).get("pawns") or [{}])[0]
                pid = row.get("id")
                if not pid:
                    record(rid, defName, FAIL,
                           "spawn failed: %s"
                           % str((sp or {}).get("message"))[:100])
                    continue
                litter("pawn %s (%s)" % (pid, defName), "(%d,%d)" % (x, z))
                if kind == "hair":
                    st = s.call("jawa/set_pawn_style", pawnId=pid, hair=defName)
                    srow = ((st or {}).get("pawns") or [{}])[0]
                    if not srow.get("ok"):
                        record(rid, defName, FAIL,
                               "set_pawn_style refused the hair: %s"
                               % str(srow.get("error")
                                     or (st or {}).get("message"))[:90])
                        continue
                face = "south" if "Cerean" in defName else "north"
                rot = s.call("jawa/set_pawn_rotation", pawnId=pid, dir=face,
                             lockRotation=True)
                rrow = ((rot or {}).get("pawns") or [{}])[0]
                shot = s.look(x, z, name=rid.lower(), zoom=11)
                s.call("jawa/set_pawn_rotation", pawnId=pid, dir="unlock")
                # A rotation that did not take makes the shot worthless -- say so
                # on the row rather than letting the picture be judged as art.
                warn = ("" if rrow.get("applied")
                        else " ⚠️ ROTATION DID NOT TAKE (%s) -- this shot may be "
                             "another facing." % rrow.get("note"))
                record(rid, defName, NEEDS_EYES,
                       "facing %s. %s%s" % (face.upper(), note, warn), shot)
                continue

            # buildings and the vehicle
            rot = 1 if kind == "building" else 0
            sb = s.call("jawa/spawn_batch", ops="%s:%d,%d" % (defName, x, z),
                        rot=rot)
            if not (sb or {}).get("spawned"):
                record(rid, defName,
                       FAIL if kind == "building" else NEEDS_EYES,
                       "spawn_batch placed nothing: %s%s"
                       % (str((sb or {}).get("errors"))[:90],
                          " -- a VehicleDef may not construct through "
                          "spawn_batch at all; that is a TOOL gap, not a "
                          "verdict on the art." if kind == "vehicle" else ""))
                continue
            litter("%s x%s" % (defName, (sb or {}).get("spawned")),
                   "(%d,%d)" % (x, z))
            shot = s.look(x, z, name=rid.lower(), zoom=11)
            record(rid, defName, NEEDS_EYES,
                   "%s%s" % ("rotated EAST. " if kind == "building" else "",
                             note), shot)
        except Exception as e:
            record(rid, defName, ERROR, "%s: %s" % (type(e).__name__,
                                                    str(e)[:120]))


ITEMS = [
    ("A1", ANY_MAP, "Rebel Alliance faction watch", i_factions),
    ("A2", ANY_MAP, "NoPathToPilotConsole predicate", i_pilot_console),
    ("A4", ANY_MAP, "order_pawn walks and returns", i_order_pawn_walk),
    # A3 is NOT the salt-crust paint. That PASSED live already
    # (row 4, "1 of 3 SEEN"), so re-proving the def
    # and the art would be spending live time on a closed row. What is still
    # open is DECIDE's B-v1 CAPABILITY question, which is a different thing.
    # Row 5 was RULED CLOSED by a retired seat -- BTD_Jawa
    # survives the BTD dedup and the pawnkind pins were remapped onto it,
    # measured live from Player.log. `i_row5_xenotype` stays in this file
    # because the read is now free and would turn "measured from the log" into
    # "measured from the pawn", but it does NOT run by default: a closed row
    # must not spend live time.
    ("A5", ANY_MAP, "dune seas: BiomeDef terrainPatchMakers", i_dune_seas),
    ("A6", ANY_MAP, "Cherry Picker actually removed things", i_cherry_picker),
    ("A7", ANY_MAP, "world_stats: the sea, measured", i_world_stats),
    ("P", ANY_MAP, "TEST_PLAN Part 1 - the art rows", i_art_rows),
    # ⛔ Row 7 / rows 2 / Configure Factions are HELD BY THE OWNER -- the sea
    # spec is unsolved and the click is irreversible. Not this session.
    # FRESH_MAP now means a QUICKTEST, which rule 1c permits freely and which
    # `TEST_PLAN.md:99-101` accepts for the map-generation overrides.
    # The ground hulk and the scrapfields are both registered on
    # MapGeneratorDef[Base_Player] with NO biome filter, so they fire on any
    # quicktest. Salt pans and dune seas are biome-patched and only appear if
    # the quicktest happens to land on Desert/ExtremeDesert/AridShrubland --
    # a non-desert quicktest is not a failure of those two.
    ("F1", FRESH_MAP, "v1 row 7 desert worldgen (HELD -- do not run)",
     i_desert_worldgen),
]


# ------------------------------------------------------------------- run

# A retired seat's list, 2026-08-14. 🔴 Cherry Picker DELETES only 13 def types and
# NEUTERS the rest, so `get_def` returns almost every key whether the pick
# worked or not. **Absence is the right test for exactly two of them.** For the
# others the tell is a FIELD VALUE, which is why `get_def` grew combatPower,
# tradeability and thingCategories the same night.
#   A: must be ABSENT from the DefDatabase
#   B: present, combatPower must read float.MaxValue (3.4028235E+38)
#   C: present, MarketValue 0 / tradeability None / no thingCategories
#   D: present; report what is seen -- no expectation is set, and inventing one
#      then "confirming" it is how a measurement becomes a story
CHERRY = [
    ("A", "RecipeDef", "GhoulInfusion"),
    ("A", "RecipeDef", "Make_GravcoreGF"),
    ("B", "PawnKindDef", "ShamblerSoldier"),
    ("B", "PawnKindDef", "ShamblerSwarmer"),
    ("B", "PawnKindDef", "Ghoul"),
    ("B", "PawnKindDef", "Metalhorror"),
    ("B", "PawnKindDef", "Trispike"),
    ("C", "ThingDef", "GoldenCube"),
    ("C", "ThingDef", "RevenantSpine"),
    ("C", "ThingDef", "VoidNode"),
    ("C", "ThingDef", "WarpedObelisk_Duplicator"),
    ("C", "ThingDef", "WarpedObelisk_Abductor"),
    ("C", "ThingDef", "GravForge"),
    ("C", "ThingDef", "AdvShip_GravReactor"),
    ("D", "IncidentDef", "ShamblerAssault"),
    ("D", "IncidentDef", "ShamblerSwarm"),
    ("D", "IncidentDef", "SmallShamblerSwarm"),
    ("D", "IncidentDef", "ShamblerSwarmAnimals"),
    ("D", "IncidentDef", "GhoulAttack"),
    ("D", "IncidentDef", "CreepJoinerJoin_Metalhorror"),
    ("D", "IncidentDef", "WarpedObelisk_Duplicator"),
    ("D", "IncidentDef", "WarpedObelisk_Abductor"),
]


def cherry_keys(s, cfg):
    """Read every Cherry Picker key back BY TYPE, not by name.

    ⚠️ `WarpedObelisk_Duplicator` and `_Abductor` each exist as BOTH a ThingDef
    and an IncidentDef. `jawa/get_def` takes an explicit `defType`, so the two
    are separable -- a bare-name lookup would answer about one of them and the
    reader would not know which.
    """
    for grp, dtype, name in CHERRY:
        rid = "A6%s-%s" % (grp, name[:18])
        try:
            r = s.call("jawa/get_def", defName=name, defType=dtype)
        except Exception as e:
            record(rid, "%s/%s" % (dtype, name), ERROR, str(e)[:110])
            continue
        present = ok(r)
        if not present and not absent(r):
            record(rid, "%s/%s" % (dtype, name), ERROR,
                   "call did not run, so this is NOT a reading on the def: %s"
                   % str((r or {}).get("message"))[:90])
            continue
        extra = (r or {}).get("extra") or {}

        if grp == "A":
            note = ("absent from the DefDatabase, as intended" if not present
                    else "PRESENT -- the pick did not delete it")
            if present and name == "Make_GravcoreGF":
                note += ". 🔴 The GravTech scarcity gate is OPEN."
            if not present and name == "GhoulInfusion":
                note += (". ⚠️ 1,144 defs reference it in <recipes> as direct "
                         "object references resolved before startup, so absence "
                         "here does NOT mean the surgery is gone -- check a pawn.")
            record(rid, "%s/%s absent" % (dtype, name),
                   PASS if not present else FAIL, note)

        elif grp == "B":
            if not present:
                record(rid, "%s/%s neutered" % (dtype, name), FAIL,
                       "def not found at all -- expected present-but-neutered")
                continue
            record(rid, "%s/%s combatPower" % (dtype, name),
                   PASS if extra.get("combatPowerIsMaxValue") else FAIL,
                   "combatPower=%s (want float.MaxValue; a NORMAL value means "
                   "the pick did not apply, and the def existing means nothing)"
                   % extra.get("combatPower"))

        elif grp == "C":
            if not present:
                record(rid, "%s/%s neutered" % (dtype, name), FAIL,
                       "def not found at all -- expected present-but-neutered")
                continue
            mv = ((r or {}).get("statBases") or {}).get("MarketValue")
            cats = extra.get("thingCategoryCount")
            good = (not mv) and extra.get("tradeability") == "None" and not cats
            record(rid, "%s/%s neutered" % (dtype, name),
                   PASS if good else FAIL,
                   "MarketValue=%s tradeability=%s thingCategories=%s"
                   % (mv, extra.get("tradeability"), cats))

        else:
            record(rid, "%s/%s" % (dtype, name), NEEDS_EYES,
                   "%s, label=%r -- reporting what is there; no expectation set"
                   % ("present" if present else "ABSENT", (r or {}).get("label")))


def run(s, cfg):
    have = census(s)
    if not have:
        return
    ready, st = playable(s)
    if not ready and st.get("_callFailed"):
        print("\n*** THE STATUS CALL ITSELF FAILED — this is NOT a verdict on the map ***")
        print("     %s" % st.get("_message"))
        print("     The main thread is busy: the game is still coming up, or a")
        print("     long event is running. Tool metadata answers throughout, so")
        print("     a healthy-looking bridge proves nothing here. Wait and re-run.")
        return
    if not ready:
        print("\n*** MAP IS NOT CURRENT YET ***")
        print("     mapCount=%s currentMapReady=%s longEventPending=%s"
              % (st.get("mapCount"), st.get("currentMapReady"),
                 st.get("longEventPending")))
        print("Companion tools would fail with 'No current map', which reads")
        print("like a broken tool and is not one. Wait, then re-run.")
        return

    settle(s, cfg)

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
    eyes = [r for r in RESULTS if r["verdict"] == NEEDS_EYES]
    if eyes:
        lines += ["", "## Awaiting a look - %d item(s)" % len(eyes), "",
                  "🔴 **Record what you actually saw, INCLUDING \"this looked "
                  "normal\".** Owner's directive 2026-08-13: art fixes are "
                  "stopped until someone verifies the art was broken in the "
                  "first place, so a normal-looking row is the evidence being "
                  "asked for. A blank entry loses it.", "",
                  "| id | item | what I saw |", "|---|---|---|"]
        lines += ["| %s | %s |  |" % (r["id"], r["title"]) for r in eyes]
    lines += ["", "## Left on the map", ""]
    lines += (["- %s" % x for x in LITTER] if LITTER else
              ["Nothing. Every mutation was reverted in-run."])
    lines += ["", "⚠️ **The release message is written from the list above, "
              "not from memory.**", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


class FakeSession(object):
    """A scripted `s` for offline item tests. `calls` maps tool name -> response,
    or to an Exception instance to be raised."""

    def __init__(self, calls):
        self.calls = calls
        self.seen = []

    def call(self, tool, **kw):
        self.seen.append((tool, kw))
        r = self.calls.get(tool, {"success": False, "message": "not scripted"})
        if isinstance(r, Exception):
            raise r
        return r


def _item_selftests():
    """🔴 The ledger plumbing was the ONLY thing under test, and that is exactly
    where the 2026-08-14 session did not fail: two items died `NameError` on a
    helper that was never defined, mid-live-session, and no offline test could
    have caught it because no item was ever executed offline.

    These run real item functions against a scripted session. They cost nothing
    and they are the difference between a bug found now and a bug found at live
    prices."""
    bad = 0
    console = {"success": True, "scanned": 4891, "things": [
        {"id": "Thing_PilotConsole12345", "def": "PilotConsole", "x": 128, "z": 130}]}
    reach = {"success": True, "targetLabel": "pilot console",
             "pathEndMode": "InteractionCell",
             "pawns": [{"id": "p1", "canReach": True}]}
    cfg = argparse.Namespace(console_id=None)

    cases = [
        ("console found -> A2 scored", {"jawa/list_things": console,
                                        "jawa/order_pawn": reach}, "A2", PASS),
        ("no console on the map -> SKIP", {"jawa/list_things":
                                           {"success": True, "scanned": 4891,
                                            "things": []}}, "A2", SKIP),
        ("list_things did not run -> SKIP, and it says so",
         {"jawa/list_things": {"success": False, "message": "timed out"}}, "A2", SKIP),
    ]
    for title, scripted, want_id, want_verdict in cases:
        del RESULTS[:]
        try:
            i_pilot_console(FakeSession(scripted), cfg)
        except Exception as e:
            print("  SELFTEST BUG: %s raised %s: %s" % (title, type(e).__name__, e))
            bad += 1
            continue
        got = [r for r in RESULTS if r["id"] == want_id]
        if len(got) != 1 or got[0]["verdict"] != want_verdict:
            print("  SELFTEST BUG: %s -> %s" % (title, [(r["id"], r["verdict"])
                                                        for r in RESULTS]))
            bad += 1

    # The A6 tri-state, the other half of the same bug: a call that did not run
    # must never be scored as a def that is absent.
    if absent({"success": False, "message": "No ThingDef named 'Foo'."}) is not True:
        print("  SELFTEST BUG: a real absence is not being recognised"); bad += 1
    for not_absence in ({"success": False, "message": "No def type named 'Foo'."},
                        {"success": False, "message": "Timed out after 5000ms"},
                        None):
        if absent(not_absence):
            print("  SELFTEST BUG: %r scored as ABSENT" % (not_absence,)); bad += 1
    del RESULTS[:]
    return bad


def selftest():
    """Exercise the ledger and the verdict plumbing with no game and no socket.

    The point is that a live session is not spent debugging this file.
    """
    item_bad = _item_selftests()
    record("A0", "companion census", PASS, "21 jawa tools of 21")
    record("A1", "Rebel Alliance generated", FAIL, "ABSENT; control present")
    record("A3c", "reads as evaporite", NEEDS_EYES, "", "C:/shots/salt_001.png")
    record("F1", "row 7 desert terrain", SKIP, "phase=fresh")
    litter("Jawa_SaltCrust painted 10x10", "(100,100)")
    cfg = argparse.Namespace(date="0000-00-00", phase="all", x=0, z=0,
                             console_id=None, wearer="Colonist", settle=0,
                             trace=False)
    p = ledger(cfg)
    body = open(p, encoding="utf-8").read()
    bad = 0
    for must in ("NEEDS EYES", "Left on the map", "Jawa_SaltCrust painted",
                 "salt_001.png", "| A1 | FAIL |"):
        if must not in body:
            print("  SELFTEST BUG: ledger is missing %r" % must)
            bad += 1
    bad += item_bad
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
    ap.add_argument("--settle", type=int, default=40,
                    help="Seconds to wait after the bridge answers before "
                         "mutating anything. The owner measured ~40s during "
                         "which the game is NOT reactive even though every "
                         "readiness flag is already true. 0 disables it.")
    ap.add_argument("--wearer", default="Colonist",
                    help="PawnKindDef used as the body for the apparel and "
                         "hair rows. Must be humanlike and is spawned "
                         "faction=player, because the Wear apparel debug "
                         "action accepts player colonists only.")
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
