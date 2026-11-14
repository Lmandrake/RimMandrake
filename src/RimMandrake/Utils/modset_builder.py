"""Build a minimal, dependency-complete ModsConfig for a named test tier.

WHY THIS EXISTS. Bisecting a 568-mod stack by hand is how loads get wasted. A
cold load is ~23-30 minutes; a 5-mod load is seconds. Proving RimBridge against
the full stack means every failure has 568 suspects, and "debug actions do not
work" could be the bridge, a Harmony conflict, or any of four hundred mods that
patch the dev menu. Prove it on bare Core first, then add exactly what the next
test needs and nothing else.

THE HARD PART is not choosing mods, it is dependency closure. Asking for
"KotOR weapons" without Vanilla Expanded Framework or Humanoid Alien Races
produces a load that fails in a way that looks like the thing you were testing.
This walks <modDependencies> transitively so a tier is always complete.

ORDERING. RimWorld cares about load order, and About.xml declares it through
<loadAfter>, <loadBefore> and <forceLoadAfter>/<forceLoadBefore>. This does a
topological sort over those edges, with Core and Harmony pinned to the front and
our own mods pinned to the back, which is the invariant the whole armoury rests
on: our patches must have the final word.

SAFETY. This NEVER writes ModsConfig.xml while RimWorld is running -- the game
holds its list in memory and rewrites the file on exit, so an edit made during a
session is silently discarded. It refuses, loudly, if Player.log is newer than a
few minutes. Always back up first; --apply does that automatically.

    python src/RimMandrake/Utils/modset_builder.py --list
    python src/RimMandrake/Utils/modset_builder.py --tier bridge          # plan only
    python src/RimMandrake/Utils/modset_builder.py --tier bridge --apply  # writes ModsConfig
    python src/RimMandrake/Utils/modset_builder.py --restore              # back to the pre-swap list (before-copy, md5-verified)
    python src/RimMandrake/Utils/modset_builder.py --tier ratchet_pilot --apply --by relentless   # an OWNED swap
    python src/RimMandrake/Utils/modset_builder.py --restore-own relentless                     # undo only that one
    python src/RimMandrake/Utils/modset_builder.py --repair-reset                               # a crash reset the list to Core+DLC mid-swap: before-copy back

OWNED SWAPS (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD). `--by NAME` keeps the swap's marker and before-copy in agent storage
(<agent storage>/modset_swaps/NAME/), not in this clone's deployed/config: Relentless's staging worker writes the tier
from the item's clone and the supervisor restores it from the books clone, so a per-clone marker would never be seen
by the one that must undo it. `--restore-own NAME` undoes only NAME's swap and is the only restore that may run with
the game up: ModsConfig describes the NEXT load, and RimWorld rewrites it only when the list changes in-game (measured
2026-08-13, below), the same reasoning modlist_swap.py --enable already writes under.
                                                        # --restore-full writes FULL.LATEST explicitly
"""
import argparse
import collections
import io
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

# 🔴 A TIER'S `why` TEXT CARRIES EMOJI, AND WINDOWS PYTHON DEFAULTS TO cp1252.
# Printing the `shrublandfauna` tier's 🔑 raised UnicodeEncodeError and aborted
# --apply BEFORE ModsConfig was written, so the swap silently did not happen and
# the next launch ran the previous list (FOUNDRY, 2026-09-21). PYTHONIOENCODING
# does not survive the WSL->python.exe hop, so the fix has to live in the script.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# Per-platform, not hardcoded to C:\ — see src/RimMandrake/Utils/game_paths.py. These were
# Windows literals until 2026-08-13 and so were unusable under WSL.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import LOCALLOW, WORKSHOP, LOCAL_MODS, GAME_DATA  # noqa: E402

LOWDIR = LOCALLOW
GAME = os.path.dirname(LOCAL_MODS)      # ...\common\RimWorld
DATA = GAME_DATA
CONFIG = os.path.join(LOWDIR, "Config", "ModsConfig.xml")
PLAYERLOG = os.path.join(LOWDIR, "Player.log")
BACKUPS = os.path.join(ROOT, "deployed", "config")
# 🔴 Was a dated one-off snapshot (ModsConfig.full-568.2026-08-11.xml, 568 mods)
# that drifted stale as the owner's real list grew -- measured 2026-09-06: it
# silently dropped 30 mods (568 vs the then-live 598) on a --restore after a
# --tier swap. ModsConfig.FULL.LATEST.xml is the doctrinally frozen, kept-current
# full list (CLAUDE.md / rimworld-load-round skill) -- restore to THAT, always.
FULL_BACKUP = os.path.join(ROOT, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")

CORE = "ludeon.rimworld"
HARMONY = "brrainz.harmony"
BRIDGE = "brrainz.rimbridgeserver"

# Owner policy 2026-10-04: EVERY debug set carries the extra camera-zoom mod so he can zoom in
# and study what is happening. Added in resolve_tier, so no tier can forget it. Incompatible
# with Camera+ (brrainz.cameraplus); a tier that wants Camera+ must say so via `no_zoom`.
ZOOM = "ray1203.simplecamerasetting"

# Ours always loads last; this is the invariant the armoury patches depend on.
OURS_PREFIX = "mandrake."

# --------------------------------------------------------------------- tiers
# Each tier lists only what it WANTS. Dependencies are resolved automatically,
# so these stay readable and honest about intent.
#
# 🔴 dlc is ALWAYS True now — owner ruling 2026-09-19, verbatim: "ALL TEST MOD
# LISTS should include ALL THE EXPANSIONS; we're not trying to ablate
# expansions out of our list at this time." Trigger: a FireHawk flight test
# ran and looked broken, and the first question was whether Odyssey had even
# been loaded (it had — this specific test used the full live list, not a
# tier — but the standing tiers below still excluded DLC on principle, which
# is exactly the gap this rule closes). A tier's "why" can still narrow the
# MOD count for isolation; it no longer narrows the DLC set.
TIERS = {
    "bridge": {
        "why": "Prove RimBridge connects and debug actions fire, with nothing "
               "else that could explain a failure.",
        "want": [BRIDGE],
        "dlc": True,
    },
    "luminouspigment": {
        "why": "DEEPFIRE_PAINT_LIVE_VERIFY_1 spec §10 step 5 quicktest: prove "
               "CompDeepfire + the designator/WorkGiver/JobDriver + the "
               "spawned-invisible-proxy light system against GroundGlowAt.",
        "want": [BRIDGE, "mandrake.rm.luminouspigment"],
        "dlc": True,
    },
    "luminouspigment_ns": {
        "why": "LUMINOUS_PIGMENT_FIRST_SCRIPT_1: the north-star script for LuminousPigment "
               "(src/RimMandrake/LuminousPigment/validation.py). The `luminouspigment` tier plus "
               "Ninefold (inside Salvation Rites, mandrake.rut.rites, since 2026-10-22), so the god-delta "
               "chain (godsReact, DeepfireGodDeltas) is MEASURED instead of UNMEASURED.",
        "want": [BRIDGE, "mandrake.rm.luminouspigment", "mandrake.rut.antiquities", "mandrake.rut.ashkarrlandmarkart",
                 "mandrake.rut.rites"],
        "dlc": True,
    },
    "weepingstones": {
        "why": "Live-load/quicktest proof for WEEPINGSTONES_RM_MOD_BUILD_1: does "
               "mandrake.rm.weepingstones load clean, does RM_WeepingStones "
               "resolve and generate a map, and do its native fauna/flora, the "
               "stocked-pool bestiary and the Utinni-patched RSW_ Star Wars "
               "fauna (WildAnimals_WeepingStones.xml, mandrake.rut.patches) all "
               "spawn/resolve with no cross-reference errors. "
               "mandrake.rm.environmentalhazards is a hard <modDependencies> "
               "entry (RM_WaterTruceExtension); mandrake.rut.rotsporekit is "
               "needed for the shared RUT_Dewshrooms wildPlants row; "
               "mandrake.rsw.swbestiary supplies the Star Wars fauna (the "
               "art donors it once pulled, Alpha Animals and the Star Wars "
               "Animal Collection, were retired 2026-10-18 and never load).",
        "want": [
            # BAROQUE_BIOMES_WAVE2_FOLD_1: weepingstones + environmentalhazards
            # both folded into mandrake.rm.biomes, one entry covers both now.
            BRIDGE,
            "mandrake.rm.biomes",
            "mandrake.rut.patches",
            "mandrake.rsw.swbestiary",
        ],
        "dlc": True,
    },
    "slime": {
        "why": "Prove the Gelatinous Slime gene machine (SLIME_GENE_ARCHIVE_BUILD_1): "
               "the campaign's RUT_SlimeGeneArchive (priority 100) must win over "
               "GelatinousSlime's own universal RM_Archive_Default (priority 0), so "
               "Dialog_GeneArchive offers the frozen A-list, not the 17 vanilla "
               "placeholders. Needs Biotech for GeneDef at all.",
        "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rut.patches"],  # BAROQUE_BIOMES_WAVE2_FOLD_1: gelatinousslime folded
        "dlc": True,
    },
    "flowworks": {
        "why": "FLOWWORKS_NORTHSTAR trial (FlowWorks_trial_plan.md 3.1): FlowWorks "
               "alone with the bridge -- canals, the depth/fill primitive, liquid "
               "stock, superdeep pits. All five DLCs and Harmony resolve "
               "automatically. REFUSES if the stale mandrake.rm.pits (22/22 "
               "defName collision) or a terrain donor (Alpha Biomes, ManyWaters) "
               "is in the closure, so a slime/tar terrain cannot come from a donor.",
        # GSS rides along for the TOOLING, not the test: JawaBench's FlowWorks and GSS playtest runners share one
        # partial class (JawaBenchTerrainTools), so its compiler-generated lambda cache names GSS types and every
        # jawa/playtest_start throws TypeLoadException (LaidPiece) without GSS loaded (live 2026-10-06).
        "want": [BRIDGE, "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.patches"],
        "forbid": ["mandrake.rm.pits", "sarg.alphabiomes"],
        "forbid_substr": ["manywaters"],
        "dlc": True,
    },
    "fw_gss_sitting": {
        "why": "FW/GSS owed-criteria sitting (Transient/flowworks_gss_owed_20261011.md section 3): the `flowworks` "
               "tier plus CrackedLands and ExplosiveGrowth, so CrackedLands/validation.py runs on the same load "
               "(River Colors, once its own mod here, is part of FlowWorks since 2026-10-16). CrackedLands has NO runtime packageId: it ships "
               "composed in mandrake.rm.biomes (Biomes.compose.json), so that is what loads; a FlowWorks GREEN-MIN on "
               "it records as fw_gss_sitting, never flowworks-minimal. Alpha Biomes is not in its forbid because it "
               "is retired (2026-10-18) and retired_mods.json already keeps it off every list. The other "
               "guards stay (stale pits, ManyWaters, Invisible Conduit Continued for the GSS rows).",
        # VEF core named explicitly: insectoid2 (retired 2026-10-18) used to drag it in, and without it the composed
        # Biomes loses VEF comps/extensions and quicktest map generation NREs (live 2026-10-19, flowworks_hugethings)
        "want": [BRIDGE, "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "oskarpotocki.vanillafactionsexpanded.core"],
        # ExplosiveGrowth is composed in mandrake.rm.biomes (EXPLOSIVE_GROWTH_MERGE_COMES_HOME); its old standalone
        # packageId would load it twice.
        "forbid": ["mandrake.rm.pits", "glitchgoblin.invisibleconduitcont", "mandrake.rm.explosivegrowth"],
        "forbid_substr": ["manywaters"],
        "dlc": True,
    },
    "explosiveknockback": {
        "why": "Explosive Knockback first script (ExplosiveKnockback/validation.py, knockback_runner.py): the mod "
               "with FlowWorks (pit scenes, blasts break covers) and Gimme Some Slack (hose drop) on a dev "
               "quicktest map. Harmony and all five DLCs resolve automatically. Same FlowWorks guards as its tier.",
        "want": [BRIDGE, "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.explosiveknockback"],
        "forbid": ["mandrake.rm.pits", "sarg.alphabiomes", "glitchgoblin.invisibleconduitcont"],
        "forbid_substr": ["manywaters"],
        "dlc": True,
    },
    "kineticarms": {
        "why": "Kinetic Arms first script (KineticArms/validation.py, KINETIC_BLAST_WEAPONS_1): the explosiveknockback "
               "tier plus Kinetic Arms. FlowWorks and Gimme Some Slack ride along for JawaBench's shared playtest "
               "partial class and the KA.cords scene. Harmony and all five DLCs resolve automatically.",
        "want": [BRIDGE, "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.explosiveknockback",
                 "mandrake.rm.kineticarms"],
        "forbid": ["mandrake.rm.pits", "sarg.alphabiomes", "glitchgoblin.invisibleconduitcont"],
        "forbid_substr": ["manywaters"],
        "dlc": True,
    },
    "gimmesomeslack": {
        "why": "MESSY_CONDUIT_MOD_1 phase 1a functional script (GimmeSomeSlack/validation.py): "
               "the cord overlay alone with the bridge on a dev quicktest map. Harmony and all "
               "five DLCs resolve automatically. REFUSES Invisible Conduit Continued, whose "
               "unconditional wire prefix would erase the overlay lines the script checks.",
        "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.patches"],
        "forbid": ["glitchgoblin.invisibleconduitcont"],
        "dlc": True,
    },
    "builds_biomes": {
        "why": "Live def-resolve proof of the biome-mod content built 2026-10-03 (Abyss, Stillsand, Scarlands, "
               "Contagion suites run through the situational re-run job). Those mods are folded into the "
               "composed mandrake.rm.biomes, so that is the one packageId to ask for.",
        "want": [BRIDGE, "mandrake.rm.biomes"],
        "dlc": True,
    },
    "visibility": {
        "why": "Prove mandrake.rm.visibility's threat-point Prefix and "
               "tile-memory round trip (COLONY_VISIBILITY_BUILD_1) with "
               "nothing else on the list that could explain a failure. "
               "Needs Odyssey for GravshipUtility/Building_GravEngine.",
        "want": [BRIDGE, "mandrake.rm.visibility"],
        "dlc": True,
    },
    "graffiti": {
        "why": "Prove mandrake.rm.graffiti + mandrake.rm.sacredgraffiti load "
               "clean and the absorbed vandal spree mechanic runs, with "
               "Mlie.GraffitiMod already retired and nothing else on the "
               "list that could explain a failure.",
        "want": [BRIDGE, "mandrake.rm.graffiti", "mandrake.rm.sacredgraffiti"],
        "dlc": True,
    },
    "graffiti_solo": {
        "why": "GRAFFITI_NORTHSTAR trial: mandrake.rm.graffiti ALONE with the bridge. "
               "NOT the `graffiti` tier above -- that one adds SacredGraffiti, whose "
               "RM_SacredMark_* defs inherit RM_BaseGraffiti and join the mark pool and "
               "gallery, so a GREEN would no longer be Graffiti's. All five DLCs and "
               "Harmony resolve automatically (BreachBiasHook is a Harmony postfix).",
        "want": [BRIDGE, "mandrake.rm.graffiti"],
        "dlc": True,
    },
    "bench": {
        "why": "RimBridge + our mods + the smallest content set that can answer "
               "the open balance questions: saber vs vibro vs armour, ion vs "
               "droids, and megafauna butcher yields.",
        "want": [
            BRIDGE,
            # --- ours
            "mandrake.rsw.armoury", "mandrake.rut.doctrine",
            "mandrake.rut.patches", "mandrake.rsw.ionweapons",
            "mandrake.rm.rimdefdump",
            # --- weapons and armour matrix (L3 / L14)
            "lee.theforce.lightsaber",      # lightsabers, Heat damage
            "guy762.mm.kotorcore",          # durasteel + matrix armour
            "guy762.kotorweapons",          # vibro-weapons, the AP contrast
            # --- ion versus droids (the flesh-type flip)
            "neronix17.asimov",             # Asimov_Automaton flesh type
            "neronix17.outerrim.droiddepot",  # the actual droid RACES to shoot
            # --- butcher yields (bodySize^2 meat and bone)
            "mandrake.rm.biomes",           # RM_BoneAmount stat (Bones engine; sihv.rombonesport retired)
        ],
        "dlc": True,
    },
    "xenotypes": {
        "why": "LOOK at our Star Wars species. Stages the naked-races grid for "
               "XENOTYPE_CANON_CORRECTION_1's ruled sequence (skin colour -> grid "
               "-> head shapes -> grid). Needs the xenotype mod plus whatever its "
               "About.xml pulls in transitively -- Biotech for genes at all, and "
               "the gene/head frameworks the defs actually reference. 🔑 Head types "
               "carry TabulaRasa.DefModExt_HeadTypeStuff under MayRequire, so "
               "neronix17.toolbox is named explicitly: a MayRequire that does not "
               "resolve drops the extension SILENTLY and every head reads as "
               "misconfigured rather than absent.",
        "want": [
            BRIDGE,
            "mandrake.rsw.starwarsraces",
            "neronix17.toolbox",
        ],
        "dlc": True,
    },
    "beastmechanics": {
        "why": "Live-verify PORTED_BEAST_MECHANICS_REBUILD_1's three rebuilt donor "
               "mechanics (steel-eating ferroclaw, two chemfuel ejectors) on "
               "RM_Khorrak (steel diet in RimMandrake.CreatureBehaviors since "
               "KHORRAK_STEEL_DIET_TIER_1 retired RSW_Khorrak) / RSW_Vozzik / RSW_Zhakka, AND "
               "DRUM_LURE_PREDATOR_BUILD_1's vibration-lure ambush + egg-trap clutch "
               "on RM_Drazzik / RM_DrazzikEggFertilized (mandrake.rm.biomes since the RSW_ "
               "copies were retired 2026-10-05) -- same dependency closure. "
               "🔑 All of these carry comps from RimMandrakeBeastMechanicsRSW.dll or "
               "RimMandrake.CreatureBehaviors, and a missing comp TYPE discards the "
               "whole def silently -- so criterion 1 (no 'Could not find type named') "
               "is the first thing this tier exists to answer. "
               "The art donors (sarg.alphaanimals, mlie.starwarsanimalcollection) "
               "were retired 2026-10-18 (infrastructure/state/facts/retired_mods.json) "
               "and never load; SWBestiary no longer inherits from them.",
        "want": [
            BRIDGE,
            "mandrake.rsw.swbestiary",
            # 🔴 BOTH of these are REQUIRED by SWBestiary and INVISIBLE to
            # dependency closure. MEASURED live 2026-09-20 on this tier:
            #  - mandrake.rm.creaturebehaviors supplies five RM_CompProperties_*
            #    classes. It is listed only under <loadAfter>, which is an
            #    ORDERING hint, not a dependency -- so closure (which walks
            #    <modDependencies>) skips it, the comp types fail to resolve, and
            #    a missing comp type DISCARDS THE WHOLE DEF silently. That ate
            #    RSW_Drazzik, RSW_WraidAlpha and the BiomesTeamPort races.
            #  - (OskarPotocki.VFE.Insectoid2 used to be listed here for the Fuelmite
            #    art; retired 2026-10-18, its twins carry the art now.)
            "mandrake.rm.biomes",  # BAROQUE_BIOMES_WAVE2_FOLD_1: creaturebehaviors folded
            # 🔑 ADDED 2026-09-20 for DRUM_LURE_PREDATOR_BUILD_1: RSW_DrazzikEgg-
            # Fertilized's trap comp is MayRequire="mandrake.rm.proximityhatch" and
            # is also only in SWBestiary's <loadAfter>, not <modDependencies> --
            # same invisible-to-closure shape as the two above. Without it the def
            # still loads (MayRequire degrades gracefully) but falls back to
            # CompHatcher's vanilla timer, so the actual trap mechanic (hatch on
            # approach) is unprovable without this mod present.
            "mandrake.rm.proximityhatch",
        ],
        "dlc": True,
    },
    "warlab": {
        "why": "Prove ANCIENT_WAR_LAB_1's KCSG dungeon (RUT_WarLab_Complex) "
               "spawns, guardians/fauna present, connectivity holds -- "
               "mandrake.rut.injections is NOT in the owner's live FULL list "
               "yet, so this is the smallest closure that loads it.",
        "want": [BRIDGE, "mandrake.rut.injections"],
        "dlc": True,
    },
    "oracle": {
        "why": "Prove ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1's live 'Test Ohm "
               "letter' debug action fires a real claude -p subprocess call "
               "-- start_debug_game_ready is unreliable on the owner's full "
               "590-mod stack (WorldGenStep errors, quicktest-crashes-full-"
               "modlist-use-cheap-mechanism-list), so prove it here instead.",
        "want": [BRIDGE, "mandrake.rm.oracle"],
        "dlc": True,
    },
    "beskar_armorer": {
        "why": "Prove BESKAR_ARMORER_QUEST_1 live (src/RimUtinni/BeskarArmorer/prove_beskar_armorer.py --live): "
               "the covert, both routes, the forge and the harm rule, with the Armoury's gear and Blackstar's kinds.",
        "want": [BRIDGE, "mandrake.rut.beskararmorer"],
        "dlc": True,
    },
    "bacta": {
        "why": "Prove BACTA_TANK_CORE_1's live healing loop (tuned-rate heal, "
               "scar erasure, organ-heals-but-doesn't-regrow, brain untouched, "
               "fluid drain/eject, all 6 settings toggles) with nothing else on "
               "the map that could explain a failure. No hard <modDependencies> "
               "beyond Core -- mandrake.rm.flowworks is only <loadAfter>, not "
               "required for the tank/comp mechanics themselves.",
        "want": [BRIDGE, "mandrake.rsw.bacta"],
        "dlc": True,
    },
    "explosivegrowth": {
        "why": "Live-verify EXPLOSIVE_PLANT_GROWTH_1 on the CAMPAIGN path: the engine (everyday bands, x10 in the wet "
               "jungles, and the soak), composed in Baroque Biomes (mandrake.rm.biomes), plus the Utinni patch layer "
               "mandrake.rut.patches, which carries the campaign roster (scopeAllBiomes, the RUT_ wet twins, the "
               "PoisonForest stalled band) and RUT_BloomBurst. Biomes brings its own hard dependencies. The retired "
               "standalone ids (mandrake.rm.explosivegrowth, and mandrake.rut.plantgrowth, absorbed by "
               "PLANT_GROWTH_MERGE_NEVER_MEANT_APART) are forbidden: either would multiply growth twice.",
        "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rut.patches"],
        "forbid": ["mandrake.rm.explosivegrowth", "mandrake.rut.plantgrowth"],
        "dlc": True,
    },
    "explosivegrowth_solo": {
        "why": "EXPLOSIVE_GROWTH_FIRST_SCRIPT_1 north-star script on the smallest list that loads the engine: "
               "that is Baroque Biomes (mandrake.rm.biomes, which composes it, everyday bands included since "
               "PLANT_GROWTH_MERGE_NEVER_MEANT_APART) with the bridge, and no campaign layer: the RM-tier script must "
               "not depend on one, and a campaign roster's scopeAllBiomes would hide the default biome scope. The "
               "quicktest map's biome is outside that scope, so the suite runs under its test-only every-biome "
               "override. The retired standalone "
               "ids are forbidden.",
        "want": [BRIDGE, "mandrake.rm.biomes"],
        "forbid": ["mandrake.rm.explosivegrowth", "mandrake.rut.plantgrowth"],
        "dlc": True,
    },
    "fish": {
        "why": "Prove FISH_BESTIARY_BUILD_1's live fishing wiring (Scald, "
               "Wasteland brine mining, Cracked Lands, Weeping Stones, "
               "Greentide) with Odyssey's water/fishing mechanics present "
               "and nothing else on the map that could explain a failure.",
        "want": [BRIDGE, "mandrake.rut.patches", "mandrake.rsw.swbestiary"],
        "dlc": True,
    },
    "desertplants": {
        "why": "Live-verify the desert shade plants and the SWBestiary body-part "
               "repoint in one load: DESERT_LEACHMOSS_LIVE_VERIFY_1 (RM_Leachmoss "
               "spawn competition on the desert), VENOMVINE_LIVE_VERIFY_1 "
               "(CompContactVenom / MapComponent_ContactVenom), and "
               "SWBESTIARY_BODYPART_LIVE_VERIFY_1 (zero 'BodyPartRecord with null "
               "def' / RSW_ body-part cross-reference lines). All three subjects "
               "met in the old desert twin's wildPlants, which names RM_Leachmoss and "
               "RM_Venomvine (mandrake.rm.environmentalhazards), RSW_Ultracactus "
               "and four more SWBestiary plants, and RUT_Vorrel "
               "-- a MayRequire that does not resolve "
               "drops the entry SILENTLY, so every one of those mods must be "
               "present or the biome reads as misconfigured rather than absent. "
               "mandrake.rm.proximityhatch is named explicitly because SWBestiary "
               "carries it only under <loadAfter>, which closure does not walk.",
        "want": [
            BRIDGE,
            "mandrake.rm.biomes",  # BAROQUE_BIOMES_WAVE2_FOLD_1: environmentalhazards folded
            "mandrake.rut.patches",
            "mandrake.rsw.swbestiary",
            "mandrake.rm.proximityhatch",
        ],
        "dlc": True,
    },
    "diving": {
        "why": "Prove SCALD_DIVING_MOD_1's dive-site float menu, job "
               "completion, terrain burn ticks and Mod Settings load clean "
               "against the actual RUT_ScaldWater* terrain it patches, with "
               "nothing else on the map that could explain a failure.",
        "want": [BRIDGE, "mandrake.rut.patches", "mandrake.rm.biomes"],  # BAROQUE_BIOMES_WAVE2_FOLD_1: divinginteraction folded
        "dlc": True,
    },
    "warcasket": {
        "why": "Live-verify WARCASKET_SUIT_CLASS_1: RM_Warcasket's stat offsets "
               "(Insulation_Cold/Heat, VacuumResistance, ToxicEnvironmentResistance, "
               "RM_HazardousTerrainProtection), RM_CompWarcasketIntegrity's "
               "compound-failure comp resolving its Class, and "
               "RM_MapComponent_HazardousTerrainImmersion running against the "
               "Wasteland's real RM_WastesBrine* terrain, with nothing else on "
               "the map that could explain a failure.",
        "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rm.warcasket"],  # BAROQUE_BIOMES_WAVE2_FOLD_1: environmentalhazards+wasteland folded
        "dlc": True,
    },
    "wasterun": {
        "why": "Live-verify WARCASKET_WASTE_RUN_REMAINDER_1: RUT_WasteRun generates, "
               "the RM_CaskBay gains the waste-run command, and each destination "
               "signal ends the quest on its own branch.",
        "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rm.warcasket", "mandrake.rut.wasterun"],
        "dlc": True,
    },
    "shrublandfauna": {
        "why": "The union of `beastmechanics` and `desertplants`: one load that can "
               "answer SHRUBLAND_GIANT_ENRAGE_1 (RSW_ShrublandGiant + "
               "RM_CompParentalEnrage), SCRAPNEST_BIRD_LIVE_VERIFY_1 "
               "(RSW_ScrapNestBird's JobGiver_HoardScrap, in "
               "RimMandrakeBeastMechanicsRSW.dll), FILTH_ON_NATURAL_TERRAIN_NOOP_1 "
               "(RSW_ShadeWhale's RM_CompDungSeeder / RM_FilterFeedExtension and the "
               "new RSW_Filth_WhaleDung) and VENOMVINE_PATHCOST_AND_FLYER_1 "
               "(RM_Venomvine, mandrake.rm.environmentalhazards). "
               "🔑 mandrake.rm.biomes (creaturebehaviors folded in) and "
               "mandrake.rm.proximityhatch are named EXPLICITLY for the reasons "
               "spelled out on the `beastmechanics` tier -- SWBestiary carries them "
               "under <loadAfter> or not at all, closure walks only "
               "<modDependencies>, and a missing comp TYPE discards the whole def "
               "silently. Dropping any of them makes a working mechanic read as a "
               "clean negative.",
        "want": [
            BRIDGE,
            "mandrake.rsw.swbestiary",
            "mandrake.rm.biomes",  # BAROQUE_BIOMES_WAVE2_FOLD_1: creaturebehaviors + environmentalhazards both folded
            "mandrake.rm.proximityhatch",
            "mandrake.rut.patches",
        ],
        "dlc": True,
    },
    "donor_off_w4": {
        "why": "DONOR_DEFS_PORT_TO_OURS_1 W4 gate: the Star Wars donor (mlie.starwarsanimalcollection) is NOT in the list. "
               "Same cast as `shrublandfauna` plus mandrake.rsw.shokk. Both art donors (it and sarg.alphaanimals) were retired "
               "2026-10-18 and never load in any tier, so this now matches `shrublandfauna` on donors. "
               "Read the first exception, every cross-ref/config error and texture miss on RSW_/RUT_/RM_ or sw* paths.",
        "want": [
            BRIDGE,
            "mandrake.rsw.swbestiary",
            "mandrake.rm.biomes",
            "mandrake.rm.proximityhatch",
            "mandrake.rut.patches",
            "mandrake.rsw.shokk",
        ],
        "dlc": True,
    },
    "donor_off_phase0": {
        "why": "Phase 0 step L1 (design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §0.5.4-0.5.5): the donor-off "
               "round for retiring BOTH art donors. Neither mlie.starwarsanimalcollection nor sarg.alphaanimals (nor "
               "its Outposts patch) may be in the closure: `forbid` refuses the tier if any dependency drags one back. "
               "Alpha Biomes (sarg.alphabiomes) was retired too (owner 2026-10-18), so retired_mods.json keeps it out; "
               "until the composed mandrake.rm.biomes is redeployed its OLD deployed About still hard-depends on it and "
               "this tier is refused. VEF core was only ever dragged in by "
               "insectoid2 (retired 2026-10-18), so it is now named explicitly; it carries the oomb growth/split comp and the bulloo/zhool Floating comp. "
               "Driver: src/RimMandrake/Utils/modcheck/l1_donor_off_round.py; runbook Transient/phase0_L1_runbook.md.",
        "want": [
            BRIDGE,
            "mandrake.rsw.swbestiary",
            "mandrake.rm.biomes",
            "mandrake.rm.proximityhatch",
            "mandrake.rut.patches",
            "mandrake.rsw.shokk",
            "oskarpotocki.vanillafactionsexpanded.core",
            # The fixed world carries Deep Orbit's PlanetLayerDef Orbit2; without it WorldGrid.CreateRequiredLayers
            # NREs and the SAVE_LOAD row falls back to the main menu (PHASE0_L1_SAVE_LOAD, live 2026-10-16).
            "broms.deeporbit",
        ],
        "forbid": ["mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts"],
        "dlc": True,
    },
    "leaningscrub": {
        "why": "LEANINGSCRUB_RM_MOD_BUILD_1's own quicktest load-proof: does "
               "mandrake.rm.leaningscrub load clean, does its RM_LeaningScrub "
               "BiomeDef carry its 5 inline non-Star-Wars fauna rows plus its "
               "renamed RM_ plant defs, and does WildAnimals_LeaningScrub.xml "
               "(UtinniPatches) land its 40 Star Wars PatchOperationAdd rows onto "
               "it. Its Terrorworm row is now RM_Vurra (LeaningScrub), so no "
               "donor is named explicitly any more.",
        "want": [
            BRIDGE,
            # BAROQUE_BIOMES_WAVE2_FOLD_1: leaningscrub + environmentalhazards
            # both folded into mandrake.rm.biomes, one entry covers both now.
            "mandrake.rm.biomes",
            "mandrake.rsw.swbestiary",
            "mandrake.rut.patches",
        ],
        "dlc": True,
    },
}

# ------------------------------------------------- BIOME_LOAD_PROOF_WAVE_1
# One `proof_<biome>` tier per shipped biome mod, generated below so the wave
# stays uniform and re-runnable. Each wants only BRIDGE + the mod itself;
# <modDependencies> closure supplies the rest, so whatever a biome genuinely
# needs comes along and nothing else does.
#
# 🔑 Deliberately MINIMAL, because PROVEN is deliberately narrow here. The
# owner ruled it 2026-09-26: "here PROVEN doesn't mean fully functional, it
# means PROVEN for donor retirement purposes". The question each tier answers
# is only "does this mod load clean by itself" — NOT whether its roster is
# complete, its art final or its mechanics firing. Isolation is the point: an
# error under one of these tiers has exactly one mod of ours to blame.
#
# ⛔ RETIRED 2026-09-28 (BAROQUE_BIOMES_WAVE2_FOLD_1): this whole mechanism
# generated one `proof_<biome>` tier per biome wanting that biome's OLD
# STANDALONE packageId. All 29 candidate biomes/kits are now folded into
# mandrake.rm.biomes, deploy_custom_mods.py REFUSES to deploy any of them
# standalone (folded() check, points at --compose biomes instead), and their
# standalone Mods/ folders are deleted — every one of these tiers would fail
# to enable its own "want" mod. The question they asked ("does this biome
# load clean on its own") is answered instead by `baroque_wave0` below,
# which now covers the composed mod (all 29, both waves). Deleted rather
# than left broken in place (CLAUDE.md: inaccurate material is deleted, not
# superseded-in-place).

# BAROQUE_BIOMES_COMPOSE_1 / WAVE2_FOLD_1: the composed 'RimMandrake: Baroque
# Biomes' (deploy_custom_mods.py --compose biomes) on its own. Closure over
# the GENERATED About.xml supplies the engines it still hard-depends on
# (FlowWorks, LuminousPigment...; Alpha Biomes is retired). Covers all 29 folded
# biomes/kits as of wave 2 (2026-09-28), not just wave 0's original 12.
# ⛔ Never add a folded biome's standalone packageId here: its defs and types
# would load twice.
TIERS["baroque_wave0"] = {
    "why": "BAROQUE_BIOMES_COMPOSE_1 / WAVE2_FOLD_1: does the composed "
           "mandrake.rm.biomes load clean — LoadFolders content roots, "
           "per-root Assemblies, every composed biome's defs resolved "
           "(biomes_compose_prove.py), and the settings shell's worldgen "
           "gate applied. Live-proven three times (waves 1-3, all 29 "
           "entries), kept as the fast single-mod re-check for future "
           "changes to any folded biome's content.",
    "want": [BRIDGE, "mandrake.rm.biomes"],
    "dlc": True,
}
# ⛔ RETIRED 2026-09-28 (BAROQUE_BIOMES_WAVE2_FOLD_1): baroque_wave0_control
# wanted the folded biomes' OLD STANDALONE packageIds for an A/B Player.log
# diff against baroque_wave0 — that comparison already ran during waves 0-2's
# own load-proving, and it can never run again: those standalone Mods/
# folders are deleted and deploy_custom_mods.py refuses to redeploy them.

# THEY_MOD_REPLICATION_1 / GREENTIDE_ANTS_MIGRATE_NO_ANT_LEFT_BEHIND: do the Greentide's giant ants (RM_GreentideAntRace,
# both pawn kinds, the hidden RM_GreentideAntFaction, the carapace leather/wall and RM_ThinkTree_GreentideAnt with
# RM_JobGiver_DirectedAssault) load and resolve clean WITHOUT Sapiently.TheyAtomicMonsters -- the donor is simply
# not in this want list, which is the retirement test. Since Biome card 8 (2026-10-22) the ants ship inside the
# free Greentide mod, composed into mandrake.rm.biomes; mandrake.rut.greentideraidant is retired.
TIERS["greentideant"] = {
    "why": "THEY_MOD_REPLICATION_1: prove the Greentide's giant ants (race, 2 pawnkinds, hidden raid faction, "
           "carapace leather/wall, RM_ThinkTree_GreentideAnt) load and resolve with no missing-def / "
           "cross-reference errors, on a list that does NOT include Sapiently.TheyAtomicMonsters at all.",
    "want": [BRIDGE, "mandrake.rm.biomes"],
    "dlc": True,
}

# PYRELANDS_GREEN_MINIMAL_1 / Pyrelands_trial_plan.md §3.1. Pyrelands ships COMPOSED in
# mandrake.rm.biomes, so that (never mandrake.rm.pyrelands) is what loads. swbestiary is
# load-bearing: WildAnimals_Pyrelands.xml adds seven RSW_ keys under a MayRequire on a
# top-level <Operation>, which the engine ignores, so without it GenStep_Animals NREs.
# `forbid` (tier_guard) refuses the tier, plan or apply, if any of these lands in the
# resolved closure (neighbour bleed / plantDensity rewrite / flora injection).
# sarg.alphabiomes was retired 2026-10-18 (retired_mods.json keeps it out of every tier) and
# no composed entry of mandrake.rm.biomes depends on it any more. Plant purity is guarded by
# WildPlantAllowlist + bar 1.
TIERS["pyrelands"] = {
    "why": "PYRELANDS_NORTHSTAR_TRIAL_1: the composed Baroque Biomes + the Utinni "
           "fauna/mechanics patch closure for the Pyrelands north-star trial, with "
           "biome transitions, Map Designer and flora injectors kept off the list. mandrake.rm.patches "
           "rides along so metal, stone and gem walls do not burn (owner 2026-11-08, ca4586309b).",
    "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rut.patches",
             "mandrake.rsw.swbestiary", "mandrake.rut.pyrelandsmechanics", "mandrake.rm.patches"],
    "forbid": ["m00nl1ght.geologicallandforms",
               "m00nl1ght.geologicallandforms.biometransitions",
               "zylle.mapdesigner",
               "kopp.biomecompatibilityproject",
               "noxilie.regrow.wmb.alphabiomes"],
    "dlc": True,
}

TIERS["ratchet_pilot"] = {
    "why": "RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP (owner 2026-10-11: the pilot is Pyrelands + FlowWorks + "
           "GimmeSomeSlack loaded TOGETHER): the `pyrelands` tier plus FlowWorks and Gimme Some Slack, with the "
           "union of both tiers' guards (retired Alpha Biomes needs none: retired_mods.json keeps it off every list). "
           "A FlowWorks run here records as ratchet_pilot, never flowworks-minimal. mandrake.rm.patches was "
           "hand-added as 'ratchet_pilot+patches' in rounds 1-2 and is declared here so `modcheck record` accepts "
           "the set. Star Wars Animal Collection (mlie.starwarsanimalcollection) is FORBIDDEN since 3898fe6212: "
           "SWBestiary no longer depends on it (ported), no pilot mod hard-depends on it, and rm.patches/rut.patches "
           "only reach it through guarded patches. Round 4 applied its list before that commit and loaded it, so "
           "`modcheck record` refused the suites; forbidding it makes a stale list fail at the plan, not at record.",
    "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rut.patches", "mandrake.rsw.swbestiary",
             "mandrake.rut.pyrelandsmechanics", "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack",
             "mandrake.rm.patches"],
    "forbid": ["m00nl1ght.geologicallandforms",
               "m00nl1ght.geologicallandforms.biometransitions",
               "zylle.mapdesigner",
               "kopp.biomecompatibilityproject",
               "noxilie.regrow.wmb.alphabiomes",
               "mandrake.rm.pits",
               "glitchgoblin.invisibleconduitcont",
               "mlie.starwarsanimalcollection"],
    "forbid_substr": ["manywaters"],
    "dlc": True,
}

def _composed_in_biomes(key):
    """True when Biomes.compose.json composes `key` into mandrake.rm.biomes (wave <= compose_wave).
    Read at import so a tier follows a fold the moment it lands in the compose file."""
    try:
        import json
        with open(os.path.join(ROOT, "src", "RimMandrake", "Biomes.compose.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        cw = d.get("compose_wave", 0)
        return any(e.get("key") == key and e.get("wave", 99) <= cw for e in d.get("entries", ()))
    except (OSError, ValueError):
        return False


# BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (next_sprint_plan_2026-10-15.md §3 "one launch serves every suite";
# kickoff packet §1 M1-M6, §1.4 X1). ratchet_pilot + nothing per biome: none of Cauldron, Contagion or
# LeaningScrub has its own Utinni mechanics mod (MEASURED 2026-10-16), all three are composed in mandrake.rm.biomes.
# 🔑 ExplosiveGrowth guard (EXPLOSIVE_GROWTH_MERGE_COMES_HOME, FOUNDRY): until the fold lands it loads standalone;
# once Biomes.compose.json composes it, the standalone packageId flips to FORBIDDEN (its defs/types would load twice).
_EG_FOLDED = _composed_in_biomes("ExplosiveGrowth")
TIERS["biomes_sprint"] = {
    "why": "BIOME_SPRINT_PROVE_SCRUB_SETS_PACE: ONE launch for every sprint suite -- all of Baroque Biomes (Cauldron, "
           "Contagion, LeaningScrub and the rest, composed) + the pilot mods (FlowWorks, GSS, Pyrelands mechanics) with "
           "ratchet_pilot's guards, so the pilot guards (M6) run on the same load. Phase 0 donors (Star Wars Animal "
           "Collection, Alpha Animals and its Outposts patch) are forbidden: a dependency dragging one back fails the "
           "plan. Huge Things (mandrake.rm.hugethings) loads in every sprint test (owner 2026-10-16: 'We have so many huge "
           "things, we want to make sure we're always compatible with them'). ExplosiveGrowth: %s." % (
               "composed into mandrake.rm.biomes with the everyday growth bands (the former mandrake.rut.plantgrowth, "
               "absorbed 2026-10-16); both standalone packageIds forbidden" if _EG_FOLDED else
               "NOT yet folded (EXPLOSIVE_GROWTH_MERGE_COMES_HOME), so the standalone mandrake.rm.explosivegrowth loads"),
    # VEF core (2026-10-21): Baroque Biomes' donor ports name VEF classes (VEF.Plants.DualCropExtension,
    # VEF.AnimalBehaviours.CompProperties_AnimalProduct) and About.xml does not declare it, so without this the 19-mod
    # load discarded those defs and RM_TestSite_cauldron_v1 (saved with VEF) died in Map.FinalizeLoading.
    # mandrake.rut.rites: the Nine's engine (Ninefold) lives there.
    "want": list(TIERS["ratchet_pilot"]["want"]) + ["mandrake.rm.hugethings",
                                                     "oskarpotocki.vanillafactionsexpanded.core", "mandrake.rut.rites"]
            + ([] if _EG_FOLDED else ["mandrake.rm.explosivegrowth"]),
    "forbid": list(TIERS["ratchet_pilot"]["forbid"]) + ["sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts"]
              + (["mandrake.rm.explosivegrowth", "mandrake.rut.plantgrowth"] if _EG_FOLDED else []),
    "forbid_substr": list(TIERS["ratchet_pilot"]["forbid_substr"]),
    "dlc": True,
}

TIERS["evening_20261113"] = {
    "why": "Evening showing 2026-11-13 (RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE): ratchet_pilot (Pyrelands + FlowWorks + "
           "Gimme Some Slack) plus Explosive Knockback and Kinetic Arms, so the liquid-look fixes, pit furniture, fire-hawk "
           "reads and knockback scenes all run on ONE load. Union of both tiers' guards.",
    # VEF core: Baroque Biomes' donor ports name VEF classes (see biomes_sprint); coldstorage: the keeper saves
    # UNDER_LIQUID_LAW_*_20261112* were written with it
    "want": list(TIERS["ratchet_pilot"]["want"]) + ["mandrake.rm.explosiveknockback", "mandrake.rm.kineticarms",
                                                     "oskarpotocki.vanillafactionsexpanded.core", "mandrake.rm.coldstorage"],
    "forbid": list(TIERS["ratchet_pilot"]["forbid"]) + ["sarg.alphabiomes"],
    "forbid_substr": list(TIERS["ratchet_pilot"]["forbid_substr"]),
    "dlc": True,
}

TIERS["flowworks_hugethings"] = {
    "why": "BIG_CREATURES_DESIGN_WALLS_AND_SLOTS A2-A8 live sitting (HugeThings/northstar/walls_slots_live.py): Huge Things beside "
           "FlowWorks. Huge Things has no dependency on FlowWorks; the walls-and-slots rows need its titans (RM_Hwelgrue, RM_Totchak, "
           "RM_Oommok come from mandrake.rm.biomes) and Large Pawns (2x2 to 4x4 footprints, so the squeeze exception is exercised); "
           "the vanilla Elephant is the B 2 creature. Same FlowWorks guards as the `flowworks` tier, so a FlowWorks run here records "
           "as flowworks_hugethings, never flowworks-minimal.",
    # VEF core: see fw_gss_sitting (Biomes needs it since insectoid2 retired; live 2026-10-19 map gen NRE'd without it)
    "want": [BRIDGE, "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.hugethings", "mandrake.rm.biomes", "neku.largepawns",
             "oskarpotocki.vanillafactionsexpanded.core"],
    "forbid": ["mandrake.rm.pits"],
    "forbid_substr": ["manywaters"],
    "dlc": True,
}

TIERS["flowworks_vepipe"] = {
    "why": "FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES A2: the `flowworks` tier plus one Vanilla Expanded PipeSystem mod "
           "(Vanilla Chemfuel Expanded, which brings VEF and the shared VCHE_PipeNetworks designation category), so the "
           "pipe-network tab can be read for FlowWorks' pipes/tanks/reel and Player.log for a duplicate-tab error.",
    "want": [BRIDGE, "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "vanillaexpanded.vchemfuele"],
    "forbid": ["mandrake.rm.pits", "sarg.alphabiomes"],
    "forbid_substr": ["manywaters"],
    "dlc": True,
}

TIERS["cameraplus_nozoom"] = {
    "why": "CAMERAPLUS_TIER_BUILD_EVERY_LIST_ADDS_RIVAL: the one load where ART_RESOLUTION_MEASURE_AT_MAX_ZOOM A1's "
           "precondition holds -- Camera+ (brrainz.cameraplus) at its defaults and SimpleCameraSetting ABSENT, so "
           "set_camera_zoom settles at Camera+'s own floor. `no_zoom` stops resolve_tier adding the rival zoom mod "
           "(it adds it to every other tier), and `forbid` refuses the tier if a dependency drags it back. Plus the "
           "bridge and Gimme Some Slack (JawaBench's companion tools TypeLoad-fail without it).",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "brrainz.cameraplus"],
    "forbid": [ZOOM],
    "no_zoom": True,
    "dlc": True,
}

TIERS["weepingstones_solo"] = {
    "why": "WEEPING_STONES_FIRST_SCRIPT_1: the north-star script for WeepingStones "
           "(src/RimMandrake/WeepingStones, packageId mandrake.rm.weepingstones). That "
           "dev folder is SOURCE only: the biome ships composed inside "
           "mandrake.rm.biomes (Biomes.compose.json), so the thing to load is the composed "
           "mod and nothing else -- NOT the older `weepingstones` tier, which adds the "
           "Utinni patch layer and swbestiary for the campaign fauna and "
           "carries a retired packageId (mandrake.rut.rotsporekit). All five DLCs and "
           "Harmony resolve automatically.",
    "want": [BRIDGE, "mandrake.rm.biomes"],
    "dlc": True,
}

TIERS["rites"] = {
    "why": "The north-star script for Salvation Rites (mandrake.rut.rites): the liturgy research "
           "tree on mandrake.rut.antiquities, its rituals and precepts, and Ishko's three Odyssey "
           "LandmarkDefs, whose icon textures come from mandrake.rut.ashkarrlandmarkart. Ishko's "
           "landmarks were their own mod (mandrake.rut.ishkolandmarks, the old `ishko` tier) until "
           "2026-10-22. Nothing else, so a GREEN is this mod's. All five DLCs (Odyssey is a "
           "dependency) and Harmony resolve automatically.",
    # gimmesomeslack: JawaBench's companion tools TypeLoad-fail (map_info, get_defs ...) without it -- MEASURED 2026-10-07,
    # the first live_session run of the Ishko chains was REFUSED at game_loaded for exactly this.
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rut.antiquities", "mandrake.rut.ashkarrlandmarkart",
             "mandrake.rut.rites"],
    "dlc": True,
}


TIERS["acc_l1x"] = {
    "why": "FOUNDRY acceptance 2026-10-07: the L1 def reads whose owning mods the earlier sitting did "
           "not carry (FallLineArrivals, EggReckoning, WreckedMachines, TrophyCraft, ShipShields, "
           "UnfinishedLine, AcousticScanner) plus ProximityHatch, GimmeSomeSlack (JawaBench get_defs "
           "TypeLoads without it) and the composed biomes mod.",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rut.falllinearrivals",
             "mandrake.rut.eggreckoning", "mandrake.rm.wreckedmachines", "mandrake.rsw.trophycraft",
             "mandrake.rut.shipshields", "mandrake.rut.unfinishedline", "mandrake.rm.acousticscanner",
             "mandrake.rm.proximityhatch"],
    "dlc": True,
}


TIERS["acc_harness"] = {
    "why": "FOUNDRY acceptance 2026-10-07: re-run the five fixed validation chains (LuminousPigment settings_apply, "
           "WreckedMachines def read-back and config errors, Droidworks protocol droid, FallLineArrivals gate, "
           "UnfinishedLine volunteer) plus GimmeSomeSlack for JawaBench get_defs.",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.luminouspigment", "mandrake.rm.wreckedmachines",
             "mandrake.rsw.droidworks", "mandrake.rut.falllinearrivals", "mandrake.rut.unfinishedline", "mandrake.rut.patches", "mandrake.rm.hugethings",
             "mandrake.rm.biomes", "mandrake.rm.shipvermin"],  # FallLineArrivals vermin_burst needs ShipVermin, which depends on biomes
    "dlc": True,
}


TIERS["acc_biomes"] = {
    "why": "FOUNDRY acceptance 2026-10-07: the composed biomes mod (Greentide, Stillsand, LeaningScrub, CreatureBehaviors "
           "and the rest fold into it) plus GimmeSomeSlack, which JawaBench get_defs needs.",
    "want": [BRIDGE, "mandrake.rm.biomes", "mandrake.rm.gimmesomeslack"],
    "dlc": True,
}

TIERS["live_20261008"] = {
    "why": "FOUNDRY live checks 2026-10-08: HugeThings titanic cctor fix, Contagion/Wasteland suites and Ledges of Mercy "
           "(CrackedLands) on the composed biomes mod.",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rm.hugethings"],
    "dlc": True,
}

TIERS["live_20261008b"] = {
    "why": "FOUNDRY live checks 2026-10-08 (second pass): Watchers + FlowWorks + GimmeSomeSlack + LuminousPigment on the composed biomes mod, "
           "plus the Utinni patch layer (RUT_ScarlandsMark, RM_DyingCreep) and Visibility, so every owed L1/L2 read of the day runs on one load.",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rm.watchers", "mandrake.rm.flowworks",
             "mandrake.rm.luminouspigment", "mandrake.rut.patches", "mandrake.rm.visibility"],
    "dlc": True,
}

TIERS["acc_20261009"] = {
    "why": "FOUNDRY acceptance 2026-10-09: sitting 1/2 union of acc_l1x, acc_harness, acc_biomes, live_20261008b, kineticarms, explosiveknockback, flowworks and every converted mod with its own packageId.",
    "want": ["brrainz.rimbridgeserver", "mandrake.rm.acousticscanner", "mandrake.rm.aftermath", "mandrake.rm.biomes", "mandrake.rm.explosiveknockback", "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.gravshiplanding", "mandrake.rm.hugethings", "mandrake.rm.inhabited", "mandrake.rm.keelhoist", "mandrake.rm.kineticarms", "mandrake.rm.luminouspigment", "mandrake.rut.rites", "mandrake.rm.planetpresetprime", "mandrake.rm.proximityhatch", "mandrake.rm.raidredesigner", "mandrake.rm.shipvermin", "mandrake.rm.solarmirrors", "mandrake.rm.visibility", "mandrake.rm.watchers", "mandrake.rm.wreckedmachines", "mandrake.rsw.droidworks", "mandrake.rsw.trophycraft", "mandrake.rut.eggreckoning", "mandrake.rut.falllinearrivals", "mandrake.rut.patches", "mandrake.rut.shipshields", "mandrake.rut.unfinishedline"],
    "dlc": True,
}

TIERS["acc_20261009b"] = {
    "why": "FOUNDRY acceptance sitting 2 (2026-10-09): acc_20261009 plus the mods sitting 1 lacked (bacta, bazaar, empirepursuit, cathedralpass, "
           "swbestiary + Utinni/StarWars patch layers, graffiti, rites, wasterun, warcasket) so ~60 skipped criteria and "
           "everything built after the first deploy (Illisk, venomvines, LongShade, WasteRun proof hooks) can be measured.",
    "want": list(TIERS["acc_20261009"]["want"]) + ["mandrake.rsw.bacta", "mandrake.rm.bazaar", "mandrake.rut.empirepursuit", "mandrake.rut.cathedralpass",
             "mandrake.rsw.swbestiary", "mandrake.rm.graffiti", "mandrake.rut.rites", "mandrake.rut.wasterun",
             "mandrake.rm.warcasket"],
    "dlc": True,
}

TIERS["acc_20261009c"] = {
    "why": "FOUNDRY acceptance sitting 3 (2026-10-09): acc_20261009b plus the Star Wars races, the Utinni patch layer and the structure injections, "
           "so a RUT_Jawa_ faction exists and the Long Shade's dead-crawler terminus is placed (LONGSHADE_JAWATOW_RECHECK_1).",
    "want": list(TIERS["acc_20261009b"]["want"]) + ["mandrake.rsw.starwarsraces", "mandrake.rut.patches", "mandrake.rsw.injections"],
    "dlc": True,
}

TIERS["acc_20261009d"] = {
    "why": "FOUNDRY belt deploy sitting 2026-10-09: acc_20261009c plus the RUT structure injections (vault flesh seal, VAULT_SEAL_PLUG_1), "
           "so the morning's builds (throat cask, casked Junkers, pit-lip cut, Answering rite, death bursts, creep-web harvest) get live-checked.",
    "want": list(TIERS["acc_20261009c"]["want"]) + ["mandrake.rut.injections", "mandrake.rut.wasterun", "mandrake.rm.warcasket",
                                                   "mandrake.rut.rites", "mandrake.rm.graffiti", "mandrake.rm.flowworks"],
    "dlc": True,
}

TIERS["watchers_live"] = {
    "why": "FOUNDRY live checks 2026-10-08: the Watchers kit (WATCHER_CREATURES_MOD_1) with its one shipped member, the piinnok, "
           "from the composed biomes mod.",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rm.watchers"],
    "dlc": True,
}

TIERS["gizkastowaway"] = {
    "why": "GIZKA_STOWAWAY_UNMEASURED_ROWS_1: the north-star list for Gizka Stowaway (mandrake.rsw.gizkastowaway). "
           "The mod has no hard dependency on a gizka creature (donor OR SWBestiary's RSW_Gizka), so on MINIMAL "
           "alone every creature row read UNMEASURED; SWBestiary carries RSW_Gizka and needs mandrake.rm.biomes. "
           "gimmesomeslack: JawaBench's companion tools TypeLoad-fail without it (see the rites tier).",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rsw.swbestiary",
             "mandrake.rsw.gizkastowaway"],
    "dlc": True,
    "modcheck_closure": True,    # modcheck/runner.py closure_ids: `modcheck run GizkaStowaway` composes this list
}


def mod_env(rel):
    """(EXTRA_IDS, FORBID) of a mod's `modcheck_env.py`, the per-mod test environment kept beside its validation.py.
    Read with ast as data (never imported, so a broken mod file cannot break the tier table); a missing or
    malformed file raises by name, because a tier that silently lost its donors would test the wrong list."""
    import ast
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    vals = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            vals[node.targets[0].id] = ast.literal_eval(node.value)
    if not vals.get("EXTRA_IDS"):
        raise RuntimeError("%s: no EXTRA_IDS list" % path)
    return [p.lower() for p in vals["EXTRA_IDS"]], [p.lower() for p in vals.get("FORBID", [])]


# MODCHECK_DONOR_ENVIRONMENTS_1: the two mature mods whose donor environment was never composed. Their lists live
# beside their validation.py (modcheck_env.py); these tiers only carry them, so `modcheck run Armoury` and
# `modset_builder --tier armoury` load the same mods.
for _tier, _rel, _why in (
        ("armoury", "src/RimStarWars/Armoury/modcheck_env.py",
         "MODCHECK_DONOR_ENVIRONMENTS_1: Armoury's modcheck environment, the closure of its own modDependencies. "
         "ModularWeapons2 is cut (forbidden here) and KotORCore is absorbed, so neither donor loads."),
        ("wreckedmachines", "src/RimMandrake/WreckedMachines/modcheck_env.py",
         "MODCHECK_DONOR_ENVIRONMENTS_1: Wrecked Machines' modcheck environment, VFEFactory and its VE Framework. "
         "No other VE mod is needed: VFEFactory's auto-process generator reads only vanilla and its own defs.")):
    _ids, _forbid = mod_env(_rel)
    TIERS[_tier] = {"why": _why, "want": [BRIDGE] + _ids, "dlc": True, "forbid": _forbid,
                    "modcheck_closure": True, "env_file": _rel}


TIERS["acc_green_min"] = {
    "why": "FOUNDRY acceptance 2026-10-07 GREEN-MIN batch: one cold load for Abyss, Scarlands, ShipVermin, HugeThings (Titanic Creatures merged in), "
           "Warcasket, GizkaStowaway, OasisMaker, ScarlandsLadder, LeaningScrub, "
           "GelatinousSlime, GravshipLanding, Stillsand, Pyrinth (composed biomes mod carries several).",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rsw.swbestiary", "mandrake.rut.patches",
             "mandrake.rm.shipvermin", "mandrake.rm.hugethings", "mandrake.rm.warcasket", "mandrake.rsw.gizkastowaway",
             "mandrake.rm.oasismaker", "mandrake.rut.scarlandsladder",
             "mandrake.rm.gravshiplanding", "mandrake.rm.pyrinth"],
    "dlc": True,
}


TIERS["acc_green_min2"] = {
    "why": "FOUNDRY acceptance 2026-10-07 GREEN-MIN batch 2: Stillsand retry, CreatureBehaviors, Greentide, PyrelandsMechanics, "
           "LuminousPigment (with Ninefold, which its gods chain needs; Ninefold is inside Salvation Rites since "
           "2026-10-22) on the composed biomes mod.",
    "want": [BRIDGE, "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "mandrake.rsw.swbestiary", "mandrake.rut.patches",
             "mandrake.rm.luminouspigment", "mandrake.rut.antiquities", "mandrake.rut.ashkarrlandmarkart",
             "mandrake.rut.rites", "mandrake.rut.pyrelandsmechanics"],
    "dlc": True,
}


# HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE: the top rungs of the reload-retention ladder. SteveDesktop holds 56 of the full list's
# 316 mods (read 2026-11-06), so these are the full list's own mods that it can load, and half of them in the full list's order.
TIERS["heap_full_on_steve"] = {
    "why": "HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE: every mod of ModsConfig.FULL.LATEST.xml installed on SteveDesktop, so a slope "
           "measured here is a slope of the owner's list, not of a test mix.",
    "want": [
              "brrainz.harmony", "adaptive.storage.framework", "unlimitedhugs.hugslib",
              "oskarpotocki.vanillafactionsexpanded.core", "7f.alienworlds", "unlimitedhugs.allowtool",
              "falconne.bwm", "brrainz.cameraplus", "void.charactereditor", "mlie.decorativecliffs",
              "merthsoft.designatorshapes", "dubwise.dubsmintmenus", "dubwise.dubsmintminimap",
              "mandrake.rm.injections", "mandrake.rm.graffiti", "mandrake.rm.inhabited", "mandrake.rut.injections",
              "jaxe.bubbles", "m00nl1ght.mappreview", "andromeda.milkyway", "dawnsglow.qualcolor",
              "brrainz.rimbridgeserver", "weilbyte.snapout", "marvinkosh.ughyougotme",
              "vanillaexpanded.vanillabackstoriesexpanded", "vanillaexpanded.vanillatraitsexpanded",
              "7f.alienworlds.tidallylocked", "memegoddess.replacestuff", "jaxe.rimhud", "mandrake.rm.weathersuite",
              "erdelf.humanoidalienraces", "mehni.pickupandhaul", "vanillaexpanded.vmemese", "neronix17.toolbox",
              "divinederivative.romance", "neronix17.outerrim.core", "frozensnowfox.complexjobs",
              "mandrake.rsw.ionweapons", "mandrake.rut.shipmemory", "mandrake.rm.gimmesomeslack",
              "mandrake.rm.flowworks", "mandrake.rm.luminouspigment", "mandrake.rsw.droidworks", "kutte.stairs",
              "mandrake.rm.biomes", "mandrake.rsw.cuisine", "mandrake.rsw.armoury", "mandrake.rsw.swbestiary",
              "mandrake.rut.patches", "mandrake.rut.pyrelandsmechanics"
    ],
    "dlc": True,
}

TIERS["heap_full_on_steve_half"] = {
    "why": "HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE: the first half of heap_full_on_steve in the full list's order, the rung that "
           "splits it.",
    "want": [
              "brrainz.harmony", "adaptive.storage.framework", "unlimitedhugs.hugslib",
              "oskarpotocki.vanillafactionsexpanded.core", "7f.alienworlds", "unlimitedhugs.allowtool",
              "falconne.bwm", "brrainz.cameraplus", "void.charactereditor", "mlie.decorativecliffs",
              "merthsoft.designatorshapes", "dubwise.dubsmintmenus", "dubwise.dubsmintminimap",
              "mandrake.rm.injections", "mandrake.rm.graffiti", "mandrake.rm.inhabited", "mandrake.rut.injections",
              "jaxe.bubbles", "m00nl1ght.mappreview", "andromeda.milkyway", "dawnsglow.qualcolor",
              "brrainz.rimbridgeserver", "weilbyte.snapout", "marvinkosh.ughyougotme",
              "vanillaexpanded.vanillabackstoriesexpanded"
    ],
    "dlc": True,
}


# LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT: a tier named by its mods, so every live-proof line can go to SteveDesktop
# through testq (a job's profile is tier:<name>, and the worker resolves the name here, at the job's source_sha).
# `mods__<token>__<token>...`: each token a packageId lowercased with its dots as `_` (mandrake.rm.flowworks ->
# mandrake_rm_flowworks), decoded against the installed mods; `mods__base` is none beyond the base. Every such tier
# carries the bridge and Gimme Some Slack (JawaBench's companion tools TypeLoad-fail without it, see the rites tier)
# and all five DLC. relentless_game.mods_tier writes the name; it is the inverse of mods_tier_tokens below.
MODS_TIER_PREFIX = "mods__"
MODS_TIER_BASE = MODS_TIER_PREFIX + "base"
MODS_TIER_ALWAYS = (BRIDGE, "mandrake.rm.gimmesomeslack")
MODS_TIER_MAX = 160     # the name rides in ModsConfig.before-tier-<name>.xml: one Windows path component


def mods_tier_tokens(name):
    """`mods__a_b__c_d` -> ["a_b", "c_d"]; `mods__base` -> []; anything else (a TIERS key, a malformed name) -> None."""
    if not name.startswith(MODS_TIER_PREFIX) or len(name) > MODS_TIER_MAX:
        return None
    if name == MODS_TIER_BASE:
        return []
    toks = name[len(MODS_TIER_PREFIX):].split("__")
    if not all(t and re.match(r"^[a-z0-9][a-z0-9_]*[a-z0-9]$|^[a-z0-9]$", t) for t in toks):
        return None
    return toks


def mods_token(pid):
    return pid.lower().replace(".", "_")


def tier_def(name, installed=None):
    """The tier record for `name`: a TIERS entry, or a mods__ tier built from its name; None for no tier. With
    `installed` (scan()), each mods__ token decodes to the one installed packageId it spells; one no installed mod
    spells stays as written, so close_over reports it missing (a loud refusal, never a quieter list); one that two
    installed packageIds spell raises ValueError."""
    if name in TIERS:
        return TIERS[name]
    toks = mods_tier_tokens(name)
    if toks is None:
        return None
    want = list(MODS_TIER_ALWAYS)
    for t in toks:
        hits = sorted(p for p in (installed or ()) if mods_token(p) == t)
        if len(hits) > 1:
            raise ValueError("tier %s: token %s spells %d installed packageIds %s" % (name, t, len(hits), hits))
        pid = hits[0] if hits else t
        if pid not in want:
            want.append(pid)
    return {"why": "LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT: the mods a live-proof file needs (its build's mods and "
                   "its live-mods), with the bridge, Gimme Some Slack and all five DLC: %s" % ", ".join(want),
            "want": want, "dlc": True}


def tier_arg(name):
    """argparse type for --tier: a TIERS key or a mods__ name."""
    if tier_def(name) is None:
        raise argparse.ArgumentTypeError("%r is no modset_builder tier (--list names them) and no mods__ name" % name)
    return name


def resolve_tier(name, installed):
    """(ordered packageIds, missing, refusals) for a tier -- the exact list --apply
    writes. `refusals` is tier_guard's list (forbidden mod in the closure, a DLC
    missing); non-empty means the tier is refused. Also the manifest a pre-flight
    compares the running list against (preflight_pyrelands.py)."""
    t = tier_def(name, installed)
    # A donor the owner RETIRED (infrastructure/state/facts/retired_mods.json) never enters a tier, even one written
    # while it was live (2026-10-18: SWAC, Alpha Animals + its Outposts patch, Alpha Biomes). tier_guard refuses the
    # tier if a dependency drags one back.
    want = [w for w in t["want"] if not _is_retired_donor(w)]
    if t["dlc"]:
        want += [p for p in installed if p.startswith("ludeon.rimworld")]
    else:
        want += [CORE]
    want += [HARMONY]
    # a tier that wants Camera+, or pulls it in as a dependency, never gets the rival zoom mod, whether or not it says
    # no_zoom (Codex cd905b re-review): the zoom mod is added only after the closure is known to hold no Camera+
    pids, missing = close_over(want, installed)
    if not t.get("no_zoom") and ZOOM in installed and "brrainz.cameraplus" not in {p.lower() for p in pids}:
        pids, missing = close_over(want + [ZOOM], installed)
    ordered = order(pids, installed)
    return ordered, missing, tier_guard(t, ordered)


def read_about(path):
    try:
        r = ET.parse(path).getroot()
    except Exception as e:
        print("  ! could not parse %s (%s: %s) -- this mod will read as "
              "NOT INSTALLED" % (path, type(e).__name__, e), file=sys.stderr)
        return None
    pid = (r.findtext("packageId") or "").strip()
    if not pid:
        return None

    def lst(tag):
        out = []
        # <tagByVersion><v1.6><li>…</li></v1.6></tagByVersion> is the shape 44 installed
        # workshop About.xml files use (some ONLY that, no plain <tag>); ignoring it
        # silently dropped their dependencies from the closure and the ordering.
        nodes = [r.find(tag)]
        bv = r.find(tag + "ByVersion")
        if bv is not None:
            nodes.append(bv.find("v1.6"))
        for node in nodes:
            if node is None:
                continue
            for li in node.findall("li"):
                # modDependencies entries are objects with a packageId child;
                # loadAfter entries are bare strings. Handle both shapes.
                v = (li.findtext("packageId") or li.text or "").strip()
                if v:
                    out.append(v.lower())
        return out

    return {
        "packageId": pid.lower(),
        "name": (r.findtext("name") or pid).strip(),
        "deps": lst("modDependencies"),
        "after": lst("loadAfter") + lst("forceLoadAfter"),
        "before": lst("loadBefore") + lst("forceLoadBefore"),
    }


def scan():
    """packageId -> record, across DLC, workshop and local mods."""
    found = {}
    for base in (DATA, WORKSHOP, LOCAL_MODS):
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            about = os.path.join(base, d, "About", "About.xml")
            if not os.path.isfile(about):
                continue
            rec = read_about(about)
            if rec and rec["packageId"] not in found:
                rec["dir"] = os.path.join(base, d)
                found[rec["packageId"]] = rec
    return found


def close_over(want, installed):
    """Transitive dependency closure. Reports anything not installed."""
    seen, missing, queue = set(), [], list(want)
    while queue:
        pid = queue.pop(0).lower()
        if pid in seen:
            continue
        rec = installed.get(pid)
        if rec is None:
            missing.append(pid)
            continue
        seen.add(pid)
        queue.extend(rec["deps"])
    return seen, missing


_SCANNED = None


def package_closure(pids, installed=None):
    """packageIds (a Relentless `live-mods:` line may name a workshop mod by packageId, LIVE_MODS_FIX_WORKSHOP_UNNAMEABLE)
    -> (closure, missing): every packageId, in load order (order), the load must hold for them, their About.xml dependencies walked
    transitively (close_over) across the Steam workshop content folder, the game's Mods folder and the DLC (scan), and
    the ones installed in none of them. DLC are never missing (every DLC is assumed). `installed` defaults to one scan
    per process (about 11 s over the Windows mount, so it is paid only when a packageId is asked for)."""
    global _SCANNED
    if installed is None:
        if _SCANNED is None:
            _SCANNED = scan()
        installed = _SCANNED
    seen, missing = close_over([p.lower() for p in pids], installed)
    return order(seen, installed), sorted(m for m in set(missing) if not m.startswith(CORE))


def order(pids, installed):
    """Topological sort over loadAfter/loadBefore, Core first, ours last."""
    pids = set(pids)
    edges = collections.defaultdict(set)      # node -> must come after these
    for pid in pids:
        rec = installed[pid]
        for a in rec["deps"] + rec["after"]:
            if a in pids:
                edges[pid].add(a)
        for b in rec["before"]:
            if b in pids:
                edges[b].add(pid)

    def rank(pid):
        if pid == CORE:
            return 0
        if pid.startswith("ludeon.rimworld."):
            return 1                            # official DLC
        if pid == HARMONY:
            return 2
        if pid.startswith(OURS_PREFIX):
            return 9                            # ours last, always
        return 5

    out, placed = [], set()
    pool = sorted(pids, key=lambda p: (rank(p), p))
    guard = 0
    while pool and guard < 10000:
        guard += 1
        for pid in list(pool):
            if edges[pid] <= placed:
                out.append(pid)
                placed.add(pid)
                pool.remove(pid)
                break
        else:
            # A cycle, or an edge we cannot satisfy. Take the lowest-rank
            # remaining item and move on rather than looping forever -- but
            # say so: this is exactly the case where a mod can end up loading
            # before something it needed to follow.
            pid = pool.pop(0)
            unmet = sorted(edges[pid] - placed)
            print("  ! order: forcing %s into place with unmet ordering "
                  "constraint(s) on %s (cycle or unsatisfiable loadAfter/"
                  "loadBefore)" % (pid, unmet), file=sys.stderr)
            out.append(pid)
            placed.add(pid)
    return out


def game_running():
    """Is RimWorld actually up?

    Ask the OS, not the clock. This used to infer "live" from Player.log having
    been touched in the last 3 minutes, which is a proxy for the thing we
    actually care about and gets it wrong in the direction that wastes the
    owner's time: for three minutes after a clean exit it refuses to do work
    that is perfectly safe. A closed game is closed, immediately.

    When the process list is unavailable (powershell missing, timed out, or
    exiting non-zero) we cannot ask, so we assume live and refuse. The old
    Player.log mtime fallback read a missing or quiet log as "stopped", so a
    failed tasklist let a swap write under a running game (Codex cd905b).
    """
    import game_instance
    try:
        return game_instance.running()      # this list's game: another game has its own data folder and its own list
    except game_instance.Blind as e:
        why = str(e)
    print("  ! could not ask the OS whether RimWorld runs (%s) -- assuming it is live" % why, file=sys.stderr)
    return True


def full_mod_count():
    """Current size of the full mod list, for the tier-savings line.

    Never a baked-in baseline -- the owner's full list keeps growing (measured
    2026-09-06: a dated snapshot read 568 while the live list was already 598),
    so a literal number here goes stale the same way and just lies quietly.
    """
    try:
        return len(ET.parse(FULL_BACKUP).getroot().find("activeMods").findall("li"))
    except Exception:
        return None


DLC_IDS = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
           "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")


_RETIRED = None


def _retired_ids():
    """{packageId: composed packageId} for every mod folded into or absorbed by mandrake.rm.biomes (read once)."""
    global _RETIRED
    if _RETIRED is None:
        try:
            import biomes_compose
            _RETIRED = dict(biomes_compose.folded_ids(os.path.join(ROOT, "src")))
        except Exception as e:      # a broken manifest must not hide the tier's own guards; it says so
            print("  ! the biomes compose manifest could not be read (%s: %s): no folded-package guard this run"
                  % (type(e).__name__, e), file=sys.stderr)
            _RETIRED = {}
    return _RETIRED


def _is_retired_donor(pid):
    try:
        import retired_mods
    except ImportError:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import retired_mods
    return retired_mods.is_retired(pid)


def tier_guard(tier, pids):
    """Refusals for a resolved tier list (empty = fine). A tier's `forbid` ids and
    `forbid_substr` fragments must be absent from the dependency CLOSURE, not just
    from `want` -- a dependency can drag a forbidden mod in. A `dlc` tier must
    resolve all five expansions (owner ruling 2026-09-19); a missing one is a
    refusal, never a quieter list."""
    pids = [p.lower() for p in pids]
    out = []
    for f in tier.get("forbid", ()):
        if f.lower() in pids:
            out.append("forbidden mod in closure: %s" % f)
    # Every tier: a packageId folded into (or absorbed by) Baroque Biomes would load its defs and types a second
    # time beside the composed copy (PLANT_GROWTH_MERGE_NEVER_MEANT_APART: "forbidden in every modset tier").
    named = {f.lower() for f in tier.get("forbid", ())}
    for f in sorted(_retired_ids()):
        if f in pids and f not in named:
            out.append("retired packageId in closure (folded into %s): %s" % (_retired_ids()[f], f))
    for f in pids:
        if _is_retired_donor(f) and f not in named:
            out.append("retired donor in closure (infrastructure/state/facts/retired_mods.json): %s" % f)
    for frag in tier.get("forbid_substr", ()):
        hit = [p for p in pids if frag.lower() in p]
        if hit:
            out.append("forbidden mod in closure (matches %r): %s" % (frag, hit))
    if tier.get("dlc"):
        miss = [d for d in DLC_IDS if d not in pids]
        if miss:
            out.append("DLC missing from the resolved list: %s" % miss)
    return out


def write_config(pids, version_from, before_replace=None):
    """Write `pids` as the live list (CONFIG). before_replace(md5) runs with the new file's md5 before it replaces the
    live one, so a kill between the two never leaves a tier list its swap marker cannot recognise (Codex cd905b)."""
    import zoom_guard
    # the engine's IsActive is case-sensitive on the file's ids (zoom_guard); first spelling of a repeat wins
    pids = list(dict.fromkeys(p.lower() for p in pids))
    if not any(p == ZOOM or p.lower() == "brrainz.cameraplus" for p in pids):
        pids = zoom_guard.with_zoom(pids)          # raises when the zoom mod is not installed: never write without
    tree = ET.parse(version_from)
    root = tree.getroot()
    active = root.find("activeMods")
    for li in list(active):
        active.remove(li)
    for pid in pids:
        ET.SubElement(active, "li").text = pid
    # Preserve the file's own newline convention; a text-mode round trip once
    # rewrote every ending and made the whole file read as changed.
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    # tmp + replace: a kill mid-write must not leave the game's live list half-written
    import hashlib
    data = buf.getvalue().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    tmp = CONFIG + ".modset-tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    if before_replace is not None:
        before_replace(hashlib.md5(data).hexdigest())
    try:
        os.replace(tmp, CONFIG)
    except BaseException:
        # the stamp went first; a replace that failed leaves the old list live, so the stamp goes back to it, or a
        # later restore would read the swap's own list as "moved on" (Codex cd905b round 3)
        if before_replace is not None and os.path.exists(CONFIG):
            before_replace(_md5(CONFIG))
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def bridge_ok(override):
    """BRIDGE_LOCK_CROSS_CLONE_RACE_1: a tier swap from a window that does not hold the bridge
    rewrote the other window's next load (2026-10-07). The owner (no window seat) always passes."""
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake"))
    try:
        from rimflow import model as rfmodel
    except Exception as e:                       # the tool must still work without rimflow importable
        print("  (bridge gate skipped: rimflow not importable: %s)" % e)
        return True
    seat = rfmodel.ambient_window_seat()
    why = rfmodel.bridge_gate(seat, rfmodel.ambient_bridge_host())     # a named game's list: that game's bridge
    if why is None:
        return True
    if override:
        print("  BRIDGE GATE OVERRIDDEN by %s: %s -- reason given: %s" % (seat, why, override))
        return True
    print("\n  REFUSING TO WRITE ModsConfig.xml: %s\n  (override: --not-my-bridge \"<reason>\")" % why)
    return False


class RestoreRefused(Exception):
    pass


SWAP_MARKER = "ModsConfig.swap-active.json"
# One writer of the live ModsConfig at a time, across every clone on the machine: two concurrent --apply runs each took
# a before-copy and a marker of their own, so one restore could hand back the other's tier list (Codex cd905b).
CONFIG_LOCK = os.environ.get("RM_MODSET_LOCK", "/home/mandrake/rm/.modset-config.lock")


class config_lock(object):
    """with config_lock(): ... holds an exclusive flock on CONFIG_LOCK (its directory missing: the temp dir), waiting up
    to wait_s, else RestoreRefused naming the lock."""

    def __init__(self, path=None, wait_s=120.0):
        self.path = path or CONFIG_LOCK
        if not os.path.isdir(os.path.dirname(self.path) or "."):
            import tempfile
            self.path = os.path.join(tempfile.gettempdir(), os.path.basename(self.path))
        self.wait_s, self.fd = wait_s, None

    @staticmethod
    def _try(fd):
        try:
            import fcntl
        except ImportError:     # native Windows Python: msvcrt's byte-range lock on the file's first byte
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    @staticmethod
    def _untry(fd):
        try:
            import fcntl
        except ImportError:
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            return
        fcntl.flock(fd, fcntl.LOCK_UN)

    def __enter__(self):
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        end = time.time() + self.wait_s
        while True:
            try:
                self._try(self.fd)
                return self
            except OSError:
                if time.time() >= end:
                    os.close(self.fd)
                    self.fd = None
                    raise RestoreRefused("another ModsConfig write holds %s (waited %ds)" % (self.path, self.wait_s))
                time.sleep(0.5)

    def __exit__(self, *exc):
        if self.fd is not None:
            self._untry(self.fd)
            os.close(self.fd)
            self.fd = None
        return False


def atomic_copy(src, dst):
    """Copy src over dst through a temp file and os.replace: a kill mid-copy never leaves the live list half-written
    (Codex cd905b: restores copied straight over ModsConfig.xml)."""
    tmp = dst + ".modset-tmp"
    shutil.copy2(src, tmp)
    os.replace(tmp, dst)


def _md5(path):
    import hashlib
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


GAME_RESET_ID = re.compile(r"ludeon\.rimworld(\.[a-z0-9_]+)?")


def is_game_reset_list(path):
    """True when the list at `path` holds Core and official expansions and nothing else: what RimWorld writes over
    ModsConfig.xml when a load crashes (resetModsConfigOnCrash, Prefs.template.xml; STEVE_MODSCONFIG_REPAIR_CRASH_RESETS_LIST,
    specimen SteveDesktop 2026-11-06 after canary 618fb0). No modset_builder tier is this bare. An unreadable list is no
    reset: nothing here may write on a guess."""
    try:
        ids = [(li.text or "").strip().lower() for li in ET.parse(path).getroot().find("activeMods")]
    except (OSError, ET.ParseError, TypeError):      # TypeError: no <activeMods> to iterate
        return False
    return "ludeon.rimworld" in ids and all(GAME_RESET_ID.fullmatch(i) for i in ids)


def repair_game_reset(config, backups):
    """A crash reset the live list while a swap was active -> put the swap's before-copy back, md5-verified, and end the
    swap; returns a one-line account. None when there is nothing to repair: no swap is on record, the live list is no
    reset, or it is the before-copy or the tier list the swap wrote. RestoreRefused when the before-copy cannot be
    trusted, with the live list untouched. Without this every later swap and restore refuses the list as "neither"."""
    import json
    marker = os.path.join(backups, SWAP_MARKER)
    if not os.path.exists(marker) or not is_game_reset_list(config):
        return None
    try:
        with open(marker) as fh:
            m = json.load(fh)
        before, want = os.path.join(backups, m["before"]), m["md5"]
    except (ValueError, KeyError, TypeError, OSError) as e:
        raise RestoreRefused("the game reset ModsConfig to Core+DLC, but swap marker %s is unreadable (%s)" % (marker, e))
    live = _md5(config)
    if live in (want, m.get("tier_md5")):
        return None
    if not os.path.exists(before) or _md5(before) != want:
        raise RestoreRefused("the game reset ModsConfig to Core+DLC, but before-copy %s is missing or changed; nothing "
                             "written. Recover the list by hand, then delete %s." % (before, marker))
    atomic_copy(before, config)
    if _md5(config) != want:
        raise RestoreRefused("wrote %s but its md5 is not the before-copy's %s" % (config, want[:8]))
    os.remove(marker)
    return "REPAIRED a game-reset ModsConfig (Core+DLC, md5 %s): restored %s (md5 %s), swap %r over" % (
        live[:8], m["before"], want[:8], m.get("tier"))


def take_before_copy(config, backups, tier):
    """Copy the live list aside before a tier swap and record which copy --restore must use.

    If a swap is already active (marker present) the ORIGINAL before-copy is kept, but only when
    the live list is provably still the tier list that swap wrote (marker `tier_md5`). Anything
    else raises RestoreRefused rather than snapshotting a list that may be a tier list:
      - unreadable marker / missing or changed before-copy: the original is gone, and the live
        file mid-swap IS the tier list, so snapshotting it would hand back the tier as the owner's;
      - live list == the before-copy: the owner's list is already back (stale marker, e.g. a
        RimSort restore), so a fresh snapshot is the same content and is safe;
      - live list is the game's crash reset: the before-copy goes back first (repair_game_reset),
        then the case above;
      - live list is anything else (hand-edited, or the game rewrote it): ambiguous, so refuse.
    Returns the before-copy path."""
    import json
    os.makedirs(backups, exist_ok=True)
    marker = os.path.join(backups, SWAP_MARKER)
    repaired = repair_game_reset(config, backups)
    if repaired:
        print("  " + repaired)
    if os.path.exists(marker):
        try:
            with open(marker) as fh:
                m = json.load(fh)
            cur = os.path.join(backups, m["before"])
            want = m["md5"]
        except (ValueError, KeyError, TypeError, OSError) as e:
            raise RestoreRefused("swap marker %s unreadable (%s); the owner's original list cannot be "
                                 "confirmed. Inspect it, then delete the marker to proceed." % (marker, e))
        if not os.path.exists(cur) or _md5(cur) != want:
            raise RestoreRefused("swap marker names before-copy %s but it is missing or changed; the live "
                                 "ModsConfig may be a tier list. Recover the owner's list by hand, then "
                                 "delete %s to proceed." % (cur, marker))
        live = _md5(config)
        if live == m.get("tier_md5"):
            return cur                               # mid-swap: keep the ORIGINAL before-copy
        if live != want:
            raise RestoreRefused("swap %r is active but the live ModsConfig (md5 %s) is neither its tier "
                                 "list nor its before-copy (%s); cannot tell whether it is the owner's. "
                                 "Resolve by hand, then delete %s to proceed."
                                 % (m.get("tier"), live[:8], want[:8], marker))
        # live == before-copy: stale marker, owner's list is already back -> fall through, re-snapshot
    stamp = os.path.join(backups, "ModsConfig.before-tier-%s.xml" % tier)
    shutil.copy2(config, stamp)
    with open(marker, "w") as f:
        json.dump({"tier": tier, "before": os.path.basename(stamp), "md5": _md5(stamp)}, f)
    return stamp


def owned_backups(by):
    """--by NAME -> the shared directory holding NAME's swap marker and before-copy (module docstring, OWNED SWAPS)."""
    if not by or not all(c.isalnum() or c in "-_" for c in by):
        raise ValueError("--by names a swap owner in letters, digits, - and _: %r" % by)
    import rmpaths
    try:
        return rmpaths.rm_str("modset_swaps", by)
    except rmpaths.RmDataRootUnset as e:      # fails by name, never a fallback into the clone (CLAUDE.md agent storage)
        raise ValueError("agent storage is unset, so no owned swap can be kept: %s" % e)


def restore_own(config, backups):
    """Undo the owned swap whose marker lives in `backups` -> a one-line account; RestoreRefused when it cannot.

    No marker: nothing of this owner's is active. Live == the tier list the swap wrote: the before-copy goes back,
    md5-verified. Live == the before-copy: already back, the marker is cleared. Live is neither: the list moved on
    since (the owner, or another tool, wrote it); the swap is over, so its marker is cleared and its before-copy stays
    on disk, never written over a list this owner did not write. A tier list whose before-copy is missing or changed
    is RestoreRefused: that is the one case where the owner's list is unrecoverable by this tool."""
    import json
    marker = os.path.join(backups, SWAP_MARKER)
    if not os.path.exists(marker):
        return "no owned swap is active in %s; nothing written" % backups
    repaired = repair_game_reset(config, backups)
    if repaired:
        return repaired
    try:
        with open(marker) as fh:
            m = json.load(fh)
        before, want = os.path.join(backups, m["before"]), m["md5"]
    except (ValueError, KeyError, TypeError, OSError) as e:
        raise RestoreRefused("owned swap marker %s unreadable: %s" % (marker, e))
    live = _md5(config) if os.path.exists(config) else None
    if live == want:
        os.remove(marker)
        return "live ModsConfig already equals %s; owned swap marker cleared, nothing written" % m["before"]
    if live is None or live != m.get("tier_md5"):
        os.remove(marker)
        return ("live ModsConfig is no longer tier %r's list (md5 %s); the list moved on, so the owned swap is over: "
                "marker cleared, nothing written (before-copy kept at %s)" % (m.get("tier"), (live or "none")[:8], before))
    if not os.path.exists(before) or _md5(before) != want:
        raise RestoreRefused("tier %r is live but its before-copy %s is missing or changed; nothing written"
                             % (m.get("tier"), before))
    atomic_copy(before, config)
    if _md5(config) != want:
        raise RestoreRefused("wrote %s but its md5 is not the before-copy's %s" % (config, want[:8]))
    os.remove(marker)
    return "restored %s (md5 %s, tier %s) -> ModsConfig.xml, verified" % (m["before"], want[:8], m.get("tier"))


def record_tier_written(config, backups, md5=None):
    """Stamp the tier list's md5 (`md5`, else the live file's) into the marker, which is how a LATER swap
    proves the live file is still that tier list and not something the owner restored by hand. The marker is
    replaced whole (tmp + os.replace), never left half-written."""
    import json
    marker = os.path.join(backups, SWAP_MARKER)
    with open(marker) as fh:
        m = json.load(fh)
    m["tier_md5"] = md5 or _md5(config)
    tmp = marker + ".tmp"
    with open(tmp, "w") as f:
        json.dump(m, f)
    os.replace(tmp, marker)


def clear_swap_marker(backups):
    """--restore-full ends the swap: a left-behind marker would pin a stale before-copy."""
    marker = os.path.join(backups, SWAP_MARKER)
    if os.path.exists(marker):
        os.remove(marker)
        return True
    return False


def restore_before(config, backups):
    """Restore the before-copy named by the swap marker; verify md5 both ways or raise.

    Writes only when the live list is provably the tier list this swap wrote (marker `tier_md5`).
    Live == before-copy: the owner's list is already back, so the stale marker is just cleared.
    Live is neither (the owner restored a NEWER list by hand and the marker was left behind, or
    the file was edited): refuse -- copying the before-copy would put yesterday's list over his."""
    import json
    marker = os.path.join(backups, SWAP_MARKER)
    if not os.path.exists(marker):
        raise RestoreRefused("no active-swap marker (%s) -- no matching --tier --apply is on record. "
                             "Pick the file yourself (copy a ModsConfig.before-tier-*.xml) or use "
                             "--restore-full for FULL.LATEST." % SWAP_MARKER)
    repaired = repair_game_reset(config, backups)
    if repaired:
        return repaired
    try:
        with open(marker) as fh:
            m = json.load(fh)
        before, want = os.path.join(backups, m["before"]), m["md5"]
    except (ValueError, KeyError, TypeError, OSError) as e:
        raise RestoreRefused("marker unreadable: %s" % e)
    if not os.path.exists(before):
        raise RestoreRefused("before-copy %s is missing" % before)
    if _md5(before) != want:
        raise RestoreRefused("before-copy %s changed since the swap (md5 %s != recorded %s)"
                             % (before, _md5(before), want))
    live = _md5(config)
    if live == want:
        os.remove(marker)
        return "live ModsConfig already equals %s (md5 %s); stale swap marker cleared, nothing written" \
               % (m["before"], want[:8])
    if live != m.get("tier_md5"):
        raise RestoreRefused("live ModsConfig (md5 %s) is neither swap %r's tier list nor its before-copy "
                             "(%s); it may be a newer owner list. Nothing written. If it really is a tier "
                             "list, copy %s over it by hand, then delete %s."
                             % (live[:8], m.get("tier"), want[:8], before, marker))
    atomic_copy(before, config)
    got = _md5(config)
    if got != want:
        raise RestoreRefused("wrote %s but live md5 %s != before-copy %s" % (config, got, want))
    os.remove(marker)
    return "restored %s (md5 %s, tier %s) -> ModsConfig.xml, verified" % (m["before"], want[:8], m["tier"])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", type=tier_arg, help="a TIERS key (--list) or mods__<packageId tokens>")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--restore-full", action="store_true",
                    help="explicitly write FULL.LATEST instead of the swap's before-copy")
    ap.add_argument("--by", metavar="OWNER",
                    help="with --tier --apply: an owned swap, marker in agent storage (docstring, OWNED SWAPS)")
    ap.add_argument("--restore-own", metavar="OWNER",
                    help="undo only OWNER's swap (--by OWNER); allowed with the game up")
    ap.add_argument("--repair-reset", action="store_true",
                    help="if a crash reset the live list to Core+DLC mid-swap, put the swap's before-copy back "
                         "(--by OWNER for an owned swap); allowed with the game up")
    ap.add_argument("--not-my-bridge", metavar="REASON",
                    help="write anyway although this window does not hold the bridge (recorded on stdout)")
    a = ap.parse_args()

    if a.repair_reset:      # needs no mod scan, and may run with the game up: same reasoning as --restore-own
        if not bridge_ok(a.not_my_bridge):
            return 1
        try:
            with config_lock():
                print(repair_game_reset(CONFIG, owned_backups(a.by) if a.by else BACKUPS)
                      or "no game-reset list to repair; nothing written")
        except (RestoreRefused, ValueError) as e:
            print("REFUSING --repair-reset: %s" % e)
            return 1
        return 0
    if a.restore_own:       # needs no mod scan: it reads only the marker, the before-copy and the live list
        if not bridge_ok(a.not_my_bridge):
            return 1
        try:
            with config_lock():
                print(restore_own(CONFIG, owned_backups(a.restore_own)))
        except (RestoreRefused, ValueError) as e:
            print("REFUSING --restore-own: %s" % e)
            return 1
        return 0
    backups = BACKUPS
    if a.by:
        try:
            backups = owned_backups(a.by)
        except ValueError as e:
            ap.error(str(e))

    installed = scan()
    print("installed mods discovered: %d" % len(installed))

    if a.list:
        for name, t in sorted(TIERS.items()):
            pids, missing = close_over(t["want"], installed)
            print("\n  %-8s %d wanted -> %d with dependencies%s"
                  % (name, len(t["want"]), len(pids),
                     "  MISSING %s" % missing if missing else ""))
            print("           %s" % t["why"])
        return 0

    if (a.apply or a.restore or a.restore_full) and not bridge_ok(a.not_my_bridge):
        return 1

    if a.restore or a.restore_full:
        if game_running():
            print("REFUSING: RimWorld looks live. Exit first.")
            return 1
        # 🔴 --restore puts back the BEFORE-COPY taken by the matching --tier --apply,
        # verified by md5, and refuses otherwise. It used to write FULL_BACKUP
        # (FULL.LATEST) unconditionally and only warn on a mod-count mismatch, so the
        # owner's actual pre-swap list was silently replaced by a different one
        # (TESTENV_MODSET_RESTORE_WRONG_FILE: md5 1ab545a0 written, before-copy was ee01dae9).
        # FULL.LATEST is now reachable only by the explicit --restore-full.
        try:
            with config_lock():
                if game_running():      # it may have started while this waited for the lock
                    raise RestoreRefused("RimWorld looks live (rechecked under the lock). Exit first.")
                if a.restore_full:
                    atomic_copy(FULL_BACKUP, CONFIG)
                    if clear_swap_marker(BACKUPS):
                        print("cleared the active-swap marker (the swap is over)")
                    print("restored FULL.LATEST (explicit --restore-full) from %s"
                          % os.path.relpath(FULL_BACKUP, ROOT))
                else:
                    print(restore_before(CONFIG, BACKUPS))
        except RestoreRefused as e:
            print("REFUSING --restore: %s" % e)
            return 1
        return 0

    if not a.tier:
        ap.error("give --tier, --list or --restore")

    t = tier_def(a.tier, installed)
    ordered, missing, refusals = resolve_tier(a.tier, installed)

    print("\ntier '%s': %s\n" % (a.tier, t["why"]))
    for i, pid in enumerate(ordered, 1):
        print("  %3d  %-44s %s" % (i, pid, installed[pid]["name"][:40]))
    if missing:
        print("\n  ! NOT INSTALLED (tier is incomplete): %s" % missing)
        return 1
    if refusals:
        for r in refusals:
            print("\n  REFUSING tier '%s': %s" % (a.tier, r))
        return 1
    full_n = full_mod_count()
    print("\n  %d mods%s." % (len(ordered),
                              ", down from %d" % full_n if full_n else ""))

    if not a.apply:
        print("  plan only. Re-run with --apply to write ModsConfig.xml.")
        return 0
    if game_running():
        print("\n  REFUSING TO WRITE: RimWorld looks live (Player.log touched "
              "in the last 3 minutes).\n  A running game holds its mod list in "
              "memory, and if the list is changed IN-GAME the engine writes "
              "ModsConfig\n  itself and clobbers this edit; the running game "
              "would also ignore it regardless.\n  Exit the game, then re-run."
              "\n  (This refusal used to say 'the game rewrites ModsConfig on "
              "exit'. That is FALSE -- measured\n  2026-08-13: at a clean exit "
              "the config's mtime was OLDER than the exit. RimWorld rewrites it "
              "only\n  when the list changes in-game. The guard is still right, "
              "for the reason above.)")
        return 1

    try:
        with config_lock():     # the before-copy, the write and its md5 stamp are one act
            if game_running():      # it may have started while this waited for the lock
                raise RestoreRefused("RimWorld looks live (rechecked under the lock). Exit the game, then re-run.")
            stamp = take_before_copy(CONFIG, backups, a.tier)
            write_config(ordered, CONFIG, before_replace=lambda h: record_tier_written(CONFIG, backups, h))
            record_tier_written(CONFIG, backups)
    except RestoreRefused as e:
        print("\n  REFUSING TO WRITE: %s" % e)
        return 1
    print("\n  backed up  -> %s" % (stamp if a.by else os.path.relpath(stamp, ROOT)))     # another drive: no relpath
    print("  wrote      -> ModsConfig.xml (%d active)" % len(ordered))
    try:  # telemetry `modlist` event (TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED); never fails the write
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry"))
        from telemetry_emit import emit_change
        emit_change("modlist", "tier:%s" % a.tier, detail={"tier": a.tier, "active": len(ordered)})
    except Exception:  # noqa: BLE001
        pass
    print("  restore with: python src/RimMandrake/Utils/modset_builder.py %s"
          % ("--restore-own %s" % a.by if a.by else "--restore"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
