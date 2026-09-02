#!/usr/bin/env python3
"""harvest_log.py — one-command triage of a RimWorld Player.log.

Written 2026-08-12 by a retired seat. A cold load costs ~23-30 minutes, so the
greps that decide each queued item are written down BEFORE the load, not
invented after it. Run this the moment the game reaches the main menu.

    python.exe src/RimMandrake/Utils/harvest_log.py                 # the live Player.log
    python.exe src/RimMandrake/Utils/harvest_log.py --log <path>    # a saved copy
    python.exe src/RimMandrake/Utils/harvest_log.py --show cross    # print matching lines

Baselines below were measured from the 2026-08-12 13:45 log. A check is RED
when it exceeds its baseline, AMBER when it improves on one (tell the docs),
GREEN when it matches.

WHY THIS EXISTS, and the one thing it cannot do
-----------------------------------------------
On 2026-08-12 a mod was DEAD in a log whose `static constructor` and
`TypeInitializationException` counts were both 0 - the two strings this project
called its highest-priority check. RimAI Core died with
`ReflectionTypeLoadException` instead, a signature nobody had listed, and took
three defs down with it. Both strings are in DEAD_MOD below now.

But note what this script is NOT evidence of. `PatchOperationConditional` and
`PatchOperationFindMod` BOTH return true when they match nothing, so a patch
that silently does nothing logs nothing. An empty log is not proof a patch
worked - only the screen is. The same applies to art: a texture that loads but
is visually empty (alpha 0) is a successful load to the engine. Two such bugs
were found by reading pixels on 2026-08-12, and neither would ever appear here.

WHICH RUN IS THIS? - the freshness gate, added 2026-08-12 23:10
-----------------------------------------------------------------
This script used to answer "is this log clean" when the question that matters
is "is this log from the run I am asking about". Those come apart the moment
the game is shut down and the stack is changed: at 23:00 it printed ALL GREEN
against the 22:36 log, which was the 573-mod run from BEFORE
`mandrake.missingartfixes` was enabled at 22:38. Every one of the five items
that restart was testing was absent from the file it was reading, and the
report was indistinguishable from a genuine pass.

So the run provenance is now printed FIRST and checked, not assumed:

  * the log's mtime, against `ModsConfig.xml`'s. A mod list written AFTER the
    log means the log predates the current stack -> hard REFUSE (exit 2).
  * whether the run has EXITED. Unity writes its memory-usage block on a clean
    shutdown, so a log ending in one is a finished run, not a live game.
  * `--since HH:MM` asserts the log postdates a launch you name yourself.

Use `--stale-ok` only to deliberately re-read an old log, and say so out loud
when you quote the result. Generalises: a checker that compares a proxy for
the artifact fails in the direction that looks like success.
"""

import argparse
import datetime
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import DEF_DUMP, MODS_CONFIG, PLAYER_LOG, PREV_LOG                    # noqa: E402

# ⚠️ The WIN_/WSL pair these two used to carry is what `game_paths.resolve()`
# already does — Windows form first, /mnt/c second, whichever EXISTS wins.
DEFAULT_LOG = PLAYER_LOG

# The mod list the game will have loaded. Its mtime is the launch-time anchor:
# RimWorld reads this at startup and rewrites it on exit, so a ModsConfig
# NEWER than the log can only mean the log is from an earlier run.
DEFAULT_MODSCONFIG = MODS_CONFIG

# Unity writes this block only when the process shuts down cleanly. Its
# presence at the tail of a log means the run is OVER.
EXITED_MARKER = "Peak usage frame count"

# The def dump is the only AFFIRMATIVE "this game finished starting up" signal
# we have. The game services DefDump/dump_request.txt at startup, and the
# manifest it writes records the mod count it actually loaded - so comparing
# that count against ModsConfig answers "did THIS stack finish loading",
# which no timestamp can. Arm it before the load:
#     echo all > ".../DefDump/dump_request.txt"
DEFAULT_MANIFEST = os.path.join(DEF_DUMP, "manifest.json")

# Unity rotates Player.log -> Player-prev.log at launch, PRESERVING the old
# file's mtime. So Player-prev.log's mtime is the previous run's last write,
# which is a hard lower bound on the current run's launch time. That is the
# anchor the modCount check needs: see WHICH RUN IS THIS below.
DEFAULT_PREVLOG = PREV_LOG

# ---------------------------------------------------------------------------
# ⏳ BASELINES vs THE 573 STACK — read before trusting a number below
# ---------------------------------------------------------------------------
# Every baseline here was measured on a stack that INCLUDED
# wiggler310.mythologicalcreatures. The owner unsubscribed it 2026-08-13 and
# the stack is now 573 (fingerprint 87050b782f95012f). The first harvest after
# that change is the one at risk of reading a mod's departure as a regression.
#
# ✅ PRE-CHECKED OFFLINE 2026-08-13, so the first run does not have to guess:
#
#   patchfail  EXPECT 5, UNCHANGED. Our two patch files that touch that mod's
#              defs — Armour_Leather.xml (2 ops) and MegafaunaYield.xml (6) —
#              are ALL PatchOperationConditional inside PatchOperationFindMod.
#              Both return true on no match, so all 8 become silent no-ops
#              rather than failures. Verified by walking each op to its
#              nearest guarding wrapper, not by reading the file's top.
#
#   crossref   EXPECT 25, unchanged. No installed mod declares a dependency on
#              wiggler310.mythologicalcreatures (swept the workshop tree).
#
#   defdiscard EXPECT 2, unchanged. Same reason.
#
#   scribe     EXPECT 0. This is the ONE with real exposure: it fires when a
#              SAVED FILE holds a dead name, which is exactly what removing a
#              mod with spawned creatures produces. The campaign save had zero
#              instantiated mythical pawns and the owner has confirmed current
#              saves are throwaway, so a hit here is informative, not urgent.
#              ⚠️ Do NOT "fix" a scribe hit by re-subscribing — that decision
#              is settled (design/Jawa/mods/forbidden_mods.md).
#
# If any of the first three DOES move, that is a real finding and not the
# unsubscribe. The whole point of writing the prediction down before the load
# is that "it changed because of the mod removal" stops being available as a
# lazy explanation after the fact.
#
# ✅ INDEPENDENTLY CONFIRMED 2026-08-13 07:2x, by a different method — and the
# two methods are what makes this worth a line rather than a repetition. The
# block above reasons A PRIORI from patch structure (every op walked to its
# guarding wrapper). The confirmation is A POSTERIORI, measured from
# Player-prev.log, the 574-mod run that INCLUDED the mod: it contributed 0 of
# the 25 cross-references and 0 of the 5 patch-op failures, its only traces
# being one [MeleeAnim] info line and its own entry in the mod list.
#
# Structure predicted no change; the last run that contained the mod shows no
# contribution to change. A prediction and a measurement agreeing is stronger
# than either, and they could have disagreed.
# ⚠️ That log is GONE after the next rotation, so this cannot be re-derived.
# ---------------------------------------------------------------------------

# key, human label, regex, baseline, note
CHECKS = [
    ("dead", "DEAD MODS (static ctor)",
     r"static constructor|TypeInitializationException", 0,
     "a dead mod is the highest-priority finding in any log"),
    ("reflect", "DEAD MODS (type load)",
     r"ReflectionTypeLoadException|Could not resolve type with token", 0,
     "was 2+24 for RimAI; the load-order fix should take these to 0"),
    ("defdiscard", "DEFS DISCARDED",
     r"Exception loading def from file", 2,
     "baseline 2 = Onimods torches (benign). Was 5; 3 were RimAI collateral"),
    ("crossref", "cross-reference (def loader)",
     r"Could not resolve cross-reference", 25,
     "16 Punch_HitBuilding + 1 VWE_Tool_Whip + 8 BMT_* = 25, all triaged. "
     "2026-08-22 read 128: the excess 101 were ALL 'No RimWorld.SkillDef named li', "
     "one per cast def discarded by CAST_ROSTER_SKILLS_DISCARDED_1. When that lands "
     "this should fall straight back to 25 - if it does not, the remainder is NEW"),
    # Baseline stays 0, and as of 2026-08-22 that is a CLEANED zero rather than an
    # aspirational one. The 08-22 08:40 load read 8; all 8 were triaged to two CONFIG
    # artifacts remembering names from mods we cut or turned off, and both were then
    # edited (backups: *.bak-2026-08-22):
    #   pokean.xtp                          3 guy762_* GeneDefs, Star Wars Xenotypes is off
    #   Mod_3532608331_DeepStorageMod.xml   5 RG_* ThingDefs, 4 Cherry-Picked + 1 from
    #                                       ReGrowth: Boiling, which we dropped
    # ⚠️ "Could not load reference to" is Scribe reading a SAVED ARTIFACT, and that is a
    # different system from "Could not resolve cross-reference" (the def loader against
    # the live mod set). It fires at STARTUP for .xtp and mod-settings files, not only
    # when a save is loaded - so a hit here is not evidence about any savegame.
    ("scribe", "stale saved data (Scribe)",
     r"Could not load reference to", 0,
     "a SAVED FILE holds a dead name - different system from cross-ref. "
     "The 8 seen 2026-08-22 were cleaned out of pokean.xtp and Deep Storage's "
     "settings; any hit now is NEW"),
    # Added 2026-08-13 after HAR's transpiler on PregnancyUtility.CanEverProduceChild
    # died against Universal Pregnancy's and NOTHING here counted it. The cost was
    # not the bug - it was that with no standing check we could not DATE it: the
    # only prior log (Player-prev.log, 708 lines) never reached the patching phase,
    # so "did this start today?" was unanswerable. Baseline 1 = that HAR/UP pair,
    # investigated and deliberately left alone (see
    # observed/2026-08-13_HAR_pregnancy_patch_failure.md).
    # 🔴 This is the C#/Harmony system. Do NOT reason about it with §1.2's "a
    # failed patch is a no-op" - that rule is about the XML PatchOperation system
    # and it is WRONG here. A Harmony transpiler that throws is discarded, so the
    # method silently keeps whatever OTHER mods did to it. The failure is loud;
    # the consequence is silent.
    # ⚠️ Count EVENTS, not lines. `Wrong null argument: brtrue NULL` is the
    # exception DETAIL on the line after `Error during patching`, not a second
    # failure - including it here reported 2 for a single event. Match only the
    # line that opens a failure. Measured: lines 3474 (event) and 3475 (detail).
    ("harmonyfail", "Harmony patch failures (C#)",
     r"Error during patching|Exception from HarmonyInstance", 1,
     "baseline 1 = HAR vs Universal Pregnancy on CanEverProduceChild, triaged. "
     "ANY rise means a new transpiler collision - name the target METHOD"),
    ("tex", "texture path failures",
     r"Failed to find any textures at", 0,
     "fires ONLY if ALL directions missing - a partial set is silent"),
    # 🔴 ADDED 2026-09-02 (BENCH) BECAUSE THIS WHOLE CLASS WAS UNWATCHED, AND IT WAS
    # HIDING OUR OWN BUGS. Def.ConfigErrors() runs after every patch and every
    # inheritance resolve, so it is the ONLY reporter for "the def loaded, and it is
    # wrong". Nothing above catches it: validate_patch.py passes clean, the patchfail
    # baseline stays green, and the def is in the dump - it is simply misconfigured.
    # This is the SECOND time the project has been bitten (the first cost 9 real
    # ConfigErrors behind a clean validator, `facts/` has it); the difference now is
    # that a standing check will not let it happen silently a third time.
    #
    # 🔴 MEASURED 36 on the 2026-09-02T19:36Z load (593 mods), and TWELVE ARE OURS:
    #   12  RSW_FE_{Ash_Trace,Ash_Light,Ground_Sand,Ground_Gravel,Ground_Soil,
    #       Ground_SoilRich} "burnedDef is flammable" x2 each -- OUR fire-ecology
    #       terrain. CONFIRMED NOT A DEFECT (FOUNDRY, 2026-09-02, source-verified
    #       via RimSage): `TerrainDef.ConfigErrors()` only ever `yield return`s a
    #       string -- it cannot block a load or alter behavior for any def type.
    #       `TerrainGrid.Notify_TerrainBurned` (Verse/TerrainGrid.cs:599) sets
    #       `terrain.burnedDef` unconditionally, with no check on whether that
    #       target is itself flammable -- exactly what AshLadder.xml's own
    #       header already documents as the deliberate trace->light->heavy->deep
    #       escalating-burn ladder (design/Jawa/proposals/fire_ecology_deep_design.md
    #       §3), not an oversight. See FIRE_ECOLOGY_BURNEDDEF_FLAMMABLE_1 (closed).
    #   18  Sign* "impassable, player-buildable building that can be shot/seen over"
    #       x2 each, another mod's signs
    #    2  TG_Husbandry -- TraderGen's own ConfigErrors() throws NRE (present since
    #       at least 2026-08-26)
    #    2  CannibalPirate / PirateYttakin ConfigErrors() NRE, vanilla FactionDefs,
    #       some broad FactionDef patch, unattributed
    #    2  Techprint_* "description has trailing whitespace"
    # ⚠️ This baseline is a FLOOR TO DRIVE DOWN for the 24 that AREN'T ours, not
    # a target to preserve. The 12 RSW_FE ones are permanent, by design -- do
    # NOT chase this number down to 24, and do not read a future 36 as
    # regression if it's still exactly these same 12 plus something new. Do
    # not "fix" a BETTER reading by editing the number
    # back up.
    ("configerror", "def ConfigErrors (loaded but WRONG)",
     r"Config error in |Exception in ConfigErrors\(\) of ", 36,
     "36 = 12 OURS (RSW_FE burnedDef is flammable) + 18 Sign* + 2 TraderGen NRE + "
     "2 vanilla FactionDef NRE + 2 techprint whitespace. Read with --show configerror. "
     "A def with a config error LOADED and is WRONG - validate_patch cannot see this"),
    # Baseline 5, MEASURED 2026-08-12 by diffing the 568-mod load (18:18,
    # Player-prev.log) against the 573-mod load (21:09). Byte-for-byte the same
    # three mods, same ops, same counts - so the five mods added that day
    # contributed ZERO patch failures. All five are other people's mods:
    #   3x [Intimacy - Gender Works]  PatchOperationRemove genderPrerequisite
    #                                 on ExtractOvum/TerminatePregnancy/ImplantIUD
    #   1x [Vanilla Mining Outpost Patch] PatchOperationFindMod(Gemstones, Jewelry)
    #   1x [Biomes! Caverns] PatchOperationReplace GroundPenetratingScanner
    # The previous note here said to "expect the JawaVoice steamWorkshopUrl nag".
    # That nag appears in NEITHER log. A note telling you to expect something
    # that never happens teaches you to wave the whole check through, which is
    # exactly what a no-baseline "?" already encourages. Rule 0.6, instance 4.
    ("patchfail", "patch operations failed",
     r"[Pp]atch operation .* failed|PatchOperation.*failed", 5,
     "5 = 3 Intimacy + 1 Mining Outpost + 1 Biomes! Caverns, all pre-existing "
     "and all other mods. A 6th is NEW - read it with --show patchfail"),
    # Added 2026-08-20 by BUILD. Both were found by reading a log by hand and both
    # would otherwise have to be re-found the same way every load.
    # 🔴 The dictionary-shape error is the loudest silent bug this project has had:
    # 28 lines per load while `biomeConfigs` read `[]` and all 27 biome score offsets
    # did nothing, with `biomeBlacklist` working perfectly beside it so the def LOOKED
    # configured. The message never says "ignored" - it says "XML format error" and then
    # the game carries on.
    ("dictshape", "dictionary field given <li> children",
     r"is not <li>.*(biomeConfigs|xenotypeChances)", 0,
     "was 28 for JawaWorld_BiomeMix before 2026-08-19. A dictionary-keyed field fed "
     "<li> loses the WHOLE field and keeps loading. Same family as B56, where the "
     "reverse shape discarded five FactionDefs outright"),
    # 🔴 These are defNames this project USED to target and that no longer exist. A
    # PatchOperationConditional on a missing def returns true and logs nothing, so the
    # only way these surface is if something still references them by name in a context
    # that DOES log. Zero is the pass; any hit means a patch was reverted or a file
    # was restored from an old copy.
    ("deadnames", "defNames we retired (should be extinct)",
     r"OuterRim_Jawa\b|BTD_Jawa\b|HC_gamorreanaxe", 0,
     "OuterRim_Jawa and BTD_Jawa both stopped existing when the donor mods went off; "
     "HC_gamorreanaxe never existed at all. Retargeted 2026-08-19/20"),
]

# Items queued for this specific load. Each is (label, regex, expectation).
QUEUED = [
    ("MegafaunaYield fix (THE must-confirm)", r"Jawa Doctrine Patches", 0),
    ("Jawa_Patches ops", r"Jawa_Patches", 0),
    # Baselined at 2 on 2026-08-13 after reading the lines, which is what the
    # previous `None` was asking someone to do. Both hits are the SAME cosmetic
    # About.xml warning, emitted twice per load (Player-prev.log lines 23 and
    # 600 of the 574-mod run):
    #   Mod JawaVoice (SpeakUp reskin) dependency (JPT.speakup) needs to have
    #   <downloadUrl> and/or <steamWorkshopUrl> specified.
    # It is metadata-only, fires whether or not SpeakUp is installed, and is NOT
    # a patch failure - no V2 conclusion may be drawn from it in either
    # direction. A 3rd hit is new and worth reading.
    ("JawaVoice ops", r"JawaVoice", 2),
    ("Jawa eye glow art resolved", r"JawaEyes/jawaeyes_glow", 0),
    ("Hutt reptile eyes resolved", r"ReptileEyes/", 0),
    ("Hutt feline eyes (saved pawns)", r"FelineEyes/", 0),
    ("Twi'lek Lekku head types", r"Lekku", 0),
    ("Wookiee head swap", r"OuterRim_WookieeHead", 0),
    # NOT a bare /RimAI/ - that matches the mod's own healthy chatter
    # ("[RimAI.Framework]SettingsManager: ...") and reports a working mod as
    # RED. Caught on 2026-08-12 by running this script against a real log
    # before trusting it. Match the failure signatures only.
    ("RimAI errors (fix should hold)",
     r"RimAI\.Core.*Exception|assembly RimAI|RimAI\.Framework\.Contracts", 0),
    # --- the 573 stack: five mods added 2026-08-12 17:26 ------------------
    # W6 collateral. The suppression retunes four fields on
    # OuterRim_RebelAlliance and deliberately does NOT delete the def, because
    # Scenario_Rebel.xml references it by name. If that reasoning were wrong we
    # would see the def named in a cross-reference failure here. Zero hits is
    # necessary but NOT sufficient - see IN_GAME below.
    ("Rebel suppression collateral", r"OuterRim_RebelAlliance", 0),
    ("Outer Rim new-mod errors",
     r"OuterRim.*(Exception|[Ff]ailed)|Neronix17.*[Ff]ailed", 0),
    ("LK mineables / mineshaft errors",
     r"(MineablesOR|Mines2patch|[Mm]ineshaft).*(Exception|[Ff]ailed)", 0),
]

# Lines that are POSITIVE evidence - present means healthy, absent is the
# finding. The inverse of everything above, and easy to forget to look for.
EXPECTED = [
    ("RimAI Core booted", r"\[RimAI\.Core\] All Parts Boot OK"),
    # 🔴 Reads "[RimMandrake.Inhabited] ready: N patches, C characters, ...".
    # The COUNT is the finding, not the presence — on 2026-08-22 this line was
    # present and said 193 against 294 CharacterDefs on disk, because all 101
    # that carry a <skills> block are discarded at load
    # (CAST_ROSTER_SKILLS_DISCARDED_1). Read the number every time; a present
    # line is not a passing one. Regex updated 2026-09-02 (FOUNDRY): the mod
    # namespace moved to RimMandrake.Inhabited under the three-tier naming
    # migration and the old bare `[Inhabited]` prefix stopped matching,
    # reading as a false MISSING while the mod was actually alive.
    ("Inhabited ready (READ THE COUNT)", r"\[RimMandrake\.Inhabited\] ready:"),
    # ✅ ADDED 2026-08-23. JawaBench HAS a startup line now, so its absence is a
    # real finding rather than a permanent false RED. Read the COUNT, not just
    # the presence: `[JawaBench] ready: 121 tools, build d49eaf42545b`.
    #   121 = the current build   ·   120 = vehicle_components missing
    #   119 = the whole 2026-08-22 build never landed   ·   106 = never deployed
    ("JawaBench ready (READ THE COUNT)", r"\[JawaBench\] ready:"),
]

# 🔴 SUPERSEDED 2026-08-23 — this block used to say JawaBench was deliberately
# EXCLUDED from EXPECTED because it had no startup line: "Every Log call in
# JawaBench.BridgeTools is a Log.Warning inside a catch, so the assembly is
# silent when it works AND silent when it never loaded." That was true when it
# was written and it is not true now — JAWABENCH_HAS_NO_INIT_LINE_1 added the
# line, and tonight's log carries it. The entry above is that fix.
#
# ⚠️ THE TRAP THAT REMAINS, and it bit the scoring of §5 and §6: BOTH ready lines
# are among the LAST lines the game writes. Scoring a log while the game is still
# loading reports them ABSENT, which reads identically to the assembly failing.
# An absent line means "not finished loading" until the process has settled — ask
# a running bridge for the tool count when you need the answer early.

# Questions this script STRUCTURALLY CANNOT answer, and that a green run above
# will silently imply it did. Added 2026-08-12 after W6 exposed the gap: the
# Rebel Alliance suppression is four PatchOperationConditional ops, and a
# conditional that matched NOTHING logs exactly what one that worked logs. So
# "0 errors" is consistent with the patch never having applied at all.
#
# Every item here is a NEGATIVE or ON-SCREEN observation. If you can state the
# success condition without naming a log string, it belongs in this list, not
# in CHECKS or QUEUED.
IN_GAME = [
    # TOP OF THE LIST DELIBERATELY. This is the only item here that CANNOT log
    # even in principle: JawaIonWeapons.dll's user-string heap is 4 bytes, all
    # zero, so the assembly is physically incapable of emitting a message, and
    # Apply() has four unlogged early returns. Every other entry below could at
    # least in theory produce a line; this one never will. Measured 2026-08-13,
    # signatures in infrastructure/state/EXPECTED_FAILURES_next_load.md (A2).
    ("JawaIonWeapons - ion vs a KotOR droid ACTUALLY does something",
     "Dev-spawn a KotOR droid, hit it with the ion weapon. Want: severity "
     "climbs, 'downed: true', pawn still exists (stunned, not killed). "
     "PROTECT THIS TEST IF THE SESSION RUNS SHORT - a clean log is NOT "
     "evidence it worked, and no other observation substitutes."),
    ("W6 - Rebel Alliance faction is ABSENT",
     "World map -> faction list. NOT the visible tiles; scroll the list. "
     "A settlement anywhere means the suppression did not apply."),
    ("W6 - OuterRim_A280Blaster still SPAWNS",
     "Dev mode -> spawn the weapon. This is the half that proves the "
     "suppression cut the faction WITHOUT taking its gear with it."),
    ("Hutt eyes at drawSize 0.42 read as TWO separated eyes",
     "Dev-spawn a FRESH Hutt. Too small -> 0.48. Never above 0.55, which "
     "is measured to abut."),
    ("V2 Ideology lines fire",
     "Needs the game UNPAUSED - SpeakUp will not fire at TPS 0. "
     "Prisoner AND slave."),
]


def active_mod_count(path):
    """Count <activeMods> entries. NEVER grep -c '<li>' - <knownExpansions>
    adds exactly 5 and every count in the docs that did this was wrong by 5
    (as per the trap file). Returns (count, mtime) or (None, mtime) if it will not parse."""
    import xml.etree.ElementTree as ET
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    try:
        # utf-8-sig: RimSort has written a BOM here at least once.
        with open(path, "rb") as fh:
            root = ET.fromstring(fh.read().decode("utf-8-sig"))
        node = root.find("activeMods")
        return (len(node.findall("li")) if node is not None else None, mtime)
    except Exception:
        return (None, mtime)


def provenance(path, lines, since=None, stale_ok=False):
    """Say WHICH RUN this log is from before saying anything about its
    contents, and refuse when the answer is 'not the current one'.

    Returns a list of complaint strings; empty means the log is usable."""
    log_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    mc_path = DEFAULT_MODSCONFIG

    build = next((l.strip() for l in lines[:800]
                  if l.startswith("RimWorld 1.")), "unknown build")
    exited = any(EXITED_MARKER in l for l in lines[-40:])

    # A log from a load that is 10% done under-counts everything, and
    # under-counting prints as BETTER-than-baseline: the same
    # failure-that-looks-like-success as reading the wrong run, arriving from
    # the other direction. Found by a retired seat 2026-08-12 23:15, while the gate
    # above was being written - a 10%-loaded log passes BOTH mtime and
    # not-exited.
    #
    # "Is it growing" does NOT settle it and must not be used as the gate: the
    # game goes quiet for minutes mid-load, and it keeps writing at the main
    # menu. Sampled here for information only.
    growing = False
    if not exited:
        import time
        first = os.path.getsize(path)
        time.sleep(2.0)
        growing = os.path.getsize(path) > first

    print(colour("WHICH RUN IS THIS", "bold"))
    print(f"  log            {path}")
    print(f"  {len(lines):,} lines   last written "
          f"{colour(f'{log_mtime:%Y-%m-%d %H:%M:%S}', 'bold')}")
    print(f"  build          {build}")
    if exited:
        state = colour("EXITED - this run is over, the game is not writing "
                       "to it", "amber")
    elif growing:
        state = colour("LIVE AND GROWING - the load is still in progress",
                       "red")
    else:
        state = colour("no exit marker, not growing right now - game may be "
                       "sitting at the menu, or paused mid-load", "dim")
    print(f"  state          {state}")

    problems = []
    count = None
    if os.path.exists(mc_path):
        count, mc_mtime = active_mod_count(mc_path)
        drift = (mc_mtime - log_mtime).total_seconds()
        shown = f"{count} active mods" if count is not None else "unparsed"
        print(f"  ModsConfig     {shown}, written {mc_mtime:%Y-%m-%d %H:%M:%S}"
              f"  ({drift:+.0f}s vs the log)")
        if drift > 0:
            problems.append(
                f"ModsConfig.xml was written {drift:.0f}s AFTER this log. The "
                f"stack changed since this run, so this log is from a "
                f"DIFFERENT mod set than the one on disk now.")
    else:
        print(colour("  ModsConfig     not found - freshness UNCHECKED",
                     "amber"))

    # DID THE LOAD FINISH? Compare mod COUNTS, not timestamps: the manifest
    # records what the game actually loaded, so a stale count is proof the
    # current run has not written its dump yet.
    man_path = DEFAULT_MANIFEST
    if exited:
        pass                      # a finished run is complete by definition
    elif not os.path.exists(man_path):
        print(colour("  def dump       no manifest - COMPLETION UNCHECKED",
                     "amber"))
    else:
        import json
        try:
            with open(man_path, encoding="utf-8-sig") as fh:
                man = json.load(fh)
            man_count = man.get("modCount")
            man_mtime = datetime.datetime.fromtimestamp(
                os.path.getmtime(man_path))
            print(f"  def dump       {man_count} mods, captured "
                  f"{man.get('capturedUtc')}  ({man.get('gameVersion')}), "
                  f"written {man_mtime:%H:%M:%S}")
            if count is not None and man_count != count:
                problems.append(
                    f"the def dump was written by a {man_count}-mod run but "
                    f"ModsConfig has {count}. This load has NOT finished "
                    f"starting up - its dump is not on disk yet, so the log "
                    f"below is a PARTIAL load and every count in it is an "
                    f"undercount. An undercount prints as BETTER-than-"
                    f"baseline, which is indistinguishable from a real pass.")

            # THE COUNT ALONE IS NOT ENOUGH, and this bit us live on
            # 2026-08-12 23:35. The count only separates runs when the mod set
            # CHANGED between them. Restart the game with an unchanged stack -
            # exactly what happened when the owner closed it by accident - and
            # the PREVIOUS run's manifest still reads 574 against a 574
            # ModsConfig, so a 10%-loaded log sails through. Same
            # failure-looks-like-success, third time.
            #
            # So also require the manifest to POSTDATE the previous run. Unity
            # rotates Player.log -> Player-prev.log at launch and preserves its
            # mtime, so that mtime is the previous run's last write and any
            # dump newer than it was written by the run happening now.
            prev = DEFAULT_PREVLOG
            if not exited and os.path.exists(prev):
                prev_mtime = datetime.datetime.fromtimestamp(
                    os.path.getmtime(prev))
                print(f"  previous run   ended {prev_mtime:%H:%M:%S} "
                      f"(Player-prev.log)")
                if man_mtime <= prev_mtime:
                    problems.append(
                        f"the def dump was written {man_mtime:%H:%M:%S}, "
                        f"BEFORE the previous run ended "
                        f"({prev_mtime:%H:%M:%S}). It belongs to that earlier "
                        f"run, not to the one writing this log. The mod "
                        f"counts agree only because the stack did not change "
                        f"across the restart - which is exactly when the "
                        f"count check cannot tell two runs apart.")
        except Exception as exc:
            print(colour(f"  def dump       manifest unreadable ({exc}) - "
                         f"COMPLETION UNCHECKED", "amber"))

    if since:
        try:
            hh, mm = (int(x) for x in since.split(":"))
        except ValueError:
            sys.exit(f"--since wants HH:MM, got {since!r}")
        launch = log_mtime.replace(hour=hh, minute=mm, second=0, microsecond=0)
        print(f"  --since        {launch:%Y-%m-%d %H:%M:%S} (asserted launch)")
        if log_mtime < launch:
            problems.append(
                f"log was last written {log_mtime:%H:%M:%S}, BEFORE the "
                f"{since} launch you named. It cannot contain that run.")

    if problems:
        print()
        for p in problems:
            for chunk in textwrap.wrap("REFUSING: " + p, 74):
                print(colour("  " + chunk, "red"))
        print()
        if stale_ok:
            print(colour("  --stale-ok given: continuing anyway. Say so OUT "
                         "LOUD when you quote this run.", "amber"))
        else:
            print(colour("  Nothing below would be about the run you care "
                         "about, and a green report here is indistinguishable "
                         "from a real pass. Wait for the load, or pass "
                         "--stale-ok deliberately.", "amber"))
            print()
            sys.exit(2)
    print()
    return problems


# 🔴 The patch-file INVENTORY is not evidence, and counting it lied three times.
# LogAfterDefError prints a flat manifest of every mod and every patch file it
# loaded, as hundreds of contiguous alphabetical pairs:
#     [Source: Jawa Doctrine Patches]
#     [File: C:\...\Mods\Jawa_Doctrine\Patches\MegafaunaYield.xml]
# A bare mod-name regex hits every one of them. On 2026-08-22 that reported
# "MegafaunaYield fix 303", "Jawa_Patches ops 5252" and "JawaVoice ops 2224"
# as RED against baseline 0 — three confident wrong numbers, none of them an
# error, all of them just the manifest saying the files exist.
# This is the SAME mistake already recorded against the bare /RimAI/ pattern
# below, which matched a healthy mod's own chatter. The lesson did not get
# applied to the Jawa checks, so it is enforced here instead of re-documented.
# A line that is ONLY [Source: …] or [File: …] is metadata. It is never an
# error and never an applied op, so it cannot count toward either.
INVENTORY = re.compile(r"^\s*\[(Source|File):")


def count(lines, rx):
    """Matching lines, excluding the load-time patch-file manifest."""
    return sum(1 for l in lines if rx.search(l) and not INVENTORY.match(l))


def colour(s, c):
    if not sys.stdout.isatty():
        return s
    return {"red": "\033[31m", "green": "\033[32m", "amber": "\033[33m",
            "bold": "\033[1m", "dim": "\033[2m"}.get(c, "") + s + "\033[0m"


def verdict(n, baseline):
    if baseline is None:
        return "  ? ", "dim", "no baseline - read the lines"
    if n > baseline:
        return " RED", "red", f"ABOVE baseline {baseline}"
    if n < baseline:
        return "BETTER", "amber", f"below baseline {baseline} - update the docs"
    return "  ok", "green", f"= baseline {baseline}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=None)
    ap.add_argument("--show", metavar="KEY",
                    help="print the matching lines for one check key")
    ap.add_argument("--since", metavar="HH:MM",
                    help="assert the log postdates a launch at this time")
    ap.add_argument("--stale-ok", action="store_true",
                    help="read a log that predates the current mod list "
                         "anyway - deliberate re-reads only")
    args = ap.parse_args()

    path = args.log or DEFAULT_LOG
    if not os.path.exists(path):
        sys.exit(f"log not found: {path}\n"
                 "Pass --log. Note WSL needs the /mnt/c/... form.")

    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    print()
    provenance(path, lines, since=args.since, stale_ok=args.stale_ok)

    if args.show:
        pat = dict((k, r) for k, _, r, _, _ in CHECKS).get(args.show)
        if not pat:
            pat = dict((l, r) for l, r, _ in QUEUED).get(args.show)
        if not pat:
            sys.exit(f"unknown key {args.show!r}; "
                     f"try one of {[c[0] for c in CHECKS]}")
        rx = re.compile(pat)
        for i, l in enumerate(lines, 1):
            if rx.search(l) and not INVENTORY.match(l):
                print(f"{i:>7}: {l.rstrip()[:200]}")
        return

    print(colour("STANDING CHECKS", "bold"))
    red = 0
    for key, label, pat, base, note in CHECKS:
        rx = re.compile(pat)
        n = count(lines, rx)
        tag, col, expl = verdict(n, base)
        red += col == "red"
        print(f"  {colour(tag, col)}  {label:<32} {n:>5}   "
              f"{colour(expl, 'dim')}")
        print(f"        {colour(note, 'dim')}")

    print("\n" + colour("QUEUED FOR THIS LOAD", "bold"))
    for label, pat, base in QUEUED:
        rx = re.compile(pat)
        n = count(lines, rx)
        tag, col, expl = verdict(n, base)
        red += col == "red"
        print(f"  {colour(tag, col)}  {label:<38} {n:>5}   "
              f"{colour(expl, 'dim')}")

    print("\n" + colour("EXPECTED PRESENT (absence is the finding)", "bold"))
    for label, pat in EXPECTED:
        rx = re.compile(pat)
        n = count(lines, rx)
        ok = n > 0
        red += not ok
        print(f"  {colour('  ok' if ok else ' RED', 'green' if ok else 'red')}"
              f"  {label:<38} {n:>5}   "
              f"{colour('present' if ok else 'MISSING', 'dim')}")

    print("\n" + colour("THE LOG CANNOT ANSWER THESE - go and look", "bold"))
    print(colour("  A green run above does NOT cover any of the following.",
                 "amber"))
    for label, how in IN_GAME:
        print(f"  {colour('[ ]', 'amber')}  {colour(label, 'bold')}")
        for chunk in textwrap.wrap(how, 68):
            print(f"        {colour(chunk, 'dim')}")

    print("\n" + colour("REMEMBER", "bold"))
    print("  A no-op patch logs NOTHING. PatchOperationConditional and")
    print("  PatchOperationFindMod both return true on no match, so a clean")
    print("  log is not evidence the eyes, the yields or the art worked.")
    print("  Those are settled on screen. Use --show <key> to read lines.\n")

    if not red:
        print(colour("  Exit 0 means the LOG is clean. It does not mean the "
                     "load passed.", "amber") + "\n")

    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()
