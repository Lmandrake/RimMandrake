"""SITTING GAPS live proof: one row per owed FlowWorks criterion that NO proof row could discharge on 2026-10-23 (FOUNDRY proof
coverage helper; the sitting order is Transient/flowworks_live_sitting_plan.md). One row per (item, criterion); every row
names both, so `rimflow verify <item> --criterion <C>` reads straight off it.

  python.exe src/RimMandrake/FlowWorks/northstar/sitting_gaps_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]
             [--player-log PATH] [--drink-ticks N] [--no-shots]
  python3    src/RimMandrake/FlowWorks/northstar/sitting_gaps_proof.py --mock [--mock-faults a,b] [--only a,b]
             every path offline against FakeBridge (a small world model, NOT the mod); every row is written SKIP with the
             verdict it would have reached kept under detail.mock (proves the script, never the game). Each fault of
             FakeBridge.FAULTS turns its own row red or UNMEASURED: selftest_sitting_gaps_proof.py (the mutation harness).

Run from the repo root with python.exe on the minimal `flowworks` tier (Utils/modset_builder.py; all five DLC), the
bridge held. Exit 0 = every row PASS; 1 = a FAIL; 2 = a row could not be measured. WRITTEN OFFLINE 2026-10-23: every row
is OWED to its first live run; plot geometry is plot-local from --origin (default 40,120; site rect origin-(2,4), 100 x 62).
A guess about the layout that is wrong reads UNMEASURED/SITE, never FAIL.

ROWS (PROVE / EXPECT / LIES), in run order:
  RIVER_LAYER_REDRAWS_CLEAN   FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM A1. riverColorsEnabled read True; a log sentinel
     alive; jawa/world_commit(redraw only) runs WorldDrawLayer_Rivers.RegenerateNow on the main thread (RM_RiverTint's
     GeneratePaths prefix runs once per river tile). EXPECT the step 'ok' and no InvalidOperationException / RiverColors line
     in the journal since the tap. LIES: a world with no river never runs the prefix (riverCount, when the companion
     reports one, 0 = UNMEASURED/SITE); a journal that lost entries or a dead sentinel reads clean (UNMEASURED/HARNESS).
     The path-compression code the item fixed was replaced on 2026-10-20 (RIVER_WATER_BY_BIOME): this row is the
     regression read of the CURRENT draw path, which is what the criterion's words ask.
  CONVERTER_BIG_RECIPE_RUNS   FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST A1.
  REACTOR_NEXT_REACTION_RUNS  FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT A1.
     A def CENSUS first (pure, over this mod's Defs = the deployed set when B0's assembly identity holds): the converter
     scene needs ONE converter def whose processes reach two input liquids with DIFFERENT products (so one product tank can
     be full while the other has room); the reactor scene needs TWO RM_LiquidReactionDefs. MEASURED 2026-10-23: every
     shipped conversion makes RM_Liquid_FreshWater (tar refines to chemfuel alone) and the only reaction is
     RM_Reaction_TarAcid, so neither scene can be built from shipped content: both rows read UNMEASURED/SITE naming what
     is missing (never PASS). The fixes are proved offline (Gpt1016_converter_blocked_small_recipe_does_not_starve_big_one,
     the reactor SelfTest); the criteria need a re-scope or a test-only def (filed on both items). A census that finds a
     stageable pair reads UNMEASURED/HARNESS "stager owed" until a live stager is written.
  RAILING_HAS_STUFF           RAILING_MATERIAL_FIX_MADE_OF_NOTHING A1. A 4 m trench (1..6, 0); ProofBuild timber god over
     (0,0)-(7,0); ProofRails on (god). EXPECT railed > 0, every RM_SuspensionRailing on the drag carries a stuff
     (jawa/list_things), and no 'RM_SuspensionRailing is madeFromStuff but stuff=null' line since the tap. The player path
     (a blueprint) takes its stuff from the same RailingStuffFor call before the godMode branch
     (RM_MapComponent_SuspensionBridges.PlaceRailing): INFERRED from that shared line, not built here. LIES: no railing
     placed = nothing to judge (UNMEASURED/SITE).
  FAUCET_TAB_PIPE_ONLY        PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE A1. The VCHE_PipeNetworks architect category (FlowWorks
     ships it itself, Defs/Machinery/RM_PipeNetworksTab.xml, so it exists with or without a VE pipe mod) lists an
     RM_PipeFaucet designator; RM_LineProofs.ProofCanPlace refuses it on bare Soil (10,0) and accepts it on an
     RM_UniversalPipe (12,0); --player-log (this load's Player.log) has no error/exception line naming RM_PipeFaucet and does
     carry the load's own 'RimWorld' header. LIES: an empty category listing is the tool, not the mod (UNMEASURED/HARNESS);
     an unreadable log is no clean log (that half UNMEASURED).
  T30_pipe_faucet             PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE A2 (validation.py T30 names this bar; its live half is this
     row). RM_LiquidTank (0,6) filled 20,000 dL fresh water, RM_UniversalPipe (2..4,6), RM_PipeFaucet on (4,6); one spawned
     colonist at (7,6) at RM_Thirst 0.15, fed and rested; every other colonist drafted. Polled every 60 ticks up to
     --drink-ticks: EXPECT the tank to fall by a whole number of drinks (15 dL = 1.5 L each), RM_DrinkFromFaucet seen or the
     need up >= 0.3, and no RM_Thought_DrankRough memory. LIES: a colonist seen drinking elsewhere (terrain, a bottle) while
     the tank never moved = another drink on the map (UNMEASURED/SITE, never FAIL).
  FAUCET_LOOKS_RESOLVE        FAUCET_REDRAW_BORROWED_BLEED_WELL A2. Per look (Scrapper/Industrial/Modern/Futuristic): a pipe
     at (10+3k, 12) styled RM_UniversalPipe_<Look> (jawa/set_thing_props, read back through jawa/thing_graphic: the pipe's
     path names the look), then a faucet built on it. EXPECT each faucet's graphicPath under Faucet/<Look>/ and badTex False,
     and no error naming RM_PipeFaucet since the tap. LIES: a pipe whose style did not take is not that look's scene
     (UNMEASURED/SITE for that look).
  FAUCET_TAKES_MODERN         FAUCET_REDRAW_BORROWED_BLEED_WELL A3, the MatchPipeUnder half: the Modern faucet of the scene
     above reads Faucet/Modern/. The clamp-on-axis half is the ThingStyleDef drawOffset measured on the art (def data); it is
     recorded, not judged here (a frame for the art judge is taken with --shots).
  GUARDRAIL_ATLAS_RESOLVES    GUARDRAIL_ART_RESKIN_BORROWED_FENCE A2. A 2 m pit (20..21, 2); RM_PitGuardrail on (20,3) in
     WoodLog and on (21,3) in Steel. EXPECT each graphicPath under RimMandrake/FlowWorks/Guardrail, the chain through
     Graphic_Appearances, badTex False. LIES: a guardrail that did not spawn in its stuff (list_things) = UNMEASURED/SITE.
  REEL_FACINGS_LAY_ALONG_AXIS HOSE_REEL_FIX_TURNS_WITH_THE_SHIP A1 (the four-rotation half; a turning gravship is not staged).
     RM_HoseReel on footprint corners (34+16r, 22) built facing r = N/E/S/W, each laid 11-13 cells straight out along its
     facing. EXPECT (HoseProbe census) the nozzle tip on the facing's side of the footprint, the first drawn cell past the
     footprint on that side, and no drawn cell behind the reel (a U-turn). LIES: a lay refused = UNMEASURED/SITE.
  S3_HOSES_ON_BARE_GROUND     HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE A1. The water_scenes_walk S3 rig, plot-local at (0,30)
     (s3_geom shifted; selftest checks the copy): a 4x3 WaterDeep pond, a 6-cell depth-1 canal, pump (9,32), reel A on
     (9,33) laid to the pond edge Intake, reel B on (9,30) laid to the canal Outflow, battery (12,36). EXPECT neither hose's
     drawn cells (census poseCells) enter the pump square, the battery, or the OTHER reel's footprint. LIES: an unlaid hose
     draws nothing (UNMEASURED/SITE).
  SETTINGS_SEARCH_FINDS_ROW   SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND A1. FlowWorks Mod Settings opened; each of 'Liquid
     crosses', 'huge network', 'pieces' typed into the search box: EXPECT the row 'Liquid crosses between the pieces of a huge
     network' among the visible labels. Control: 'zzqxv' must hide it, else the read cannot tell (UNMEASURED/HARNESS).
  CANAL_LAKE_ONE_DEF          CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES A1 (L3). A 6x6 WaterDeep lake (40..45, 40..45) and a canal
     (46..51, 42) dug 3 m and filled brim-full against it; 500 ticks. EXPECT RM_WaterLookProofs.ProofWaterLook to read the
     SAME terrain def on canal (48,42) and lake (43,42) at water depths within 0.5 m; the frame (--shots) is the L3 judge's
     input -- an Opus judge, not this script, decides the colour. LIES: a canal that did not fill (dug / fill not set) is
     not the scene (UNMEASURED/SITE).
  POND_LAST_DROP_DRAWN        POND_PUMP_FIX_LAST_DROP_COUNTS A2.
  POND_DRY_STAGES_TO_BED      POND_PUMP_FIX_LAST_DROP_COUNTS A3.
     pond_pump.py's rig plot-local at (70,40): a 3x2 WaterShallow pond (72..74, 45..46), pump (73,47), battery (76,46),
     pipes (73,48..49), RM_LiquidTank (73,50). levelExactEnabled must read True; refill off for the draw; the body set to
     0.6 notch (600 L) by ProofSetBodyFraction. Up to 12 pump cycles: EXPECT stock to reach 0 dL and the tank to gain
     exactly the starting dL (+-1). A3, one pulse after dry: ProofPondDepth wet=0 (or no formed pond) and no pond square's
     terrain still a water def. LIES: an unpowered pump moves nothing (UNMEASURED/SITE); a pond never pumped dry cannot
     show A3 (UNMEASURED/SITE).

ANTI-GUESSING NOTES
- Every tool and proof hook named here exists in the 2026-10-23 tree (JawaBench.BridgeTools, RM_*Proofs.cs, HoseProbe);
  the faucet, guardrail, pipe-style and reel defs were read from FlowWorks Defs, never guessed.
- RIVER: the drawing happens in RegenerateNow, which world_commit runs synchronously and reports per step; the world map
  need not be on screen.
- The start colony is drafted and walked out of the site for the whole run (SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL: an
  undrafted bystander walks onto squares a later scene digs and takes a fall).
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402
from level_water import _volume_const  # noqa: E402  (constants read from RM_Volume.cs, never restated)

DEFS = os.path.abspath(os.path.join(HERE, "..", "Defs"))
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
WLOOK = "RimMandrake.FlowWorks.RM_WaterLookProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_TH = "RimMandrake.FlowWorks.Thirst.RM_ThirstSettings"
S_RIVER = "RimMandrake.FlowWorks.RiverColors.RM_RiverColorsSettings"
MOD_ID = "mandrake.rm.flowworks"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")        # RM_PipeFaucet_<Look> / RM_UniversalPipe_<Look> ThingStyleDefs
FRESH = "RM_Liquid_FreshWater"
UNITS_PER_LITRE = _volume_const("UnitsPerLitre", 10)
UNITS_PER_LEVEL = _volume_const("UnitsPerLevel", 10000)
DRINK_DL = int(round(1.5 * UNITS_PER_LITRE))                    # RM_DrinkFromFaucet takes 1.5 L (T30 bar)
SEARCH_LABEL = "Liquid crosses between the pieces of a huge network"
SEARCH_QUERIES = ("Liquid crosses", "huge network", "pieces")
SEARCH_CONTROL = "zzqxv"
RAIL_ERR = "is madeFromStuff but stuff=null"
DIRS = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}           # Rot4 N E S W
REEL_CORNERS = {r: (34 + 16 * r, 22) for r in range(4)}
REEL_REACH = 11                                                  # cells from the footprint edge along the facing
# water_scenes_walk.s3_geom() shifted to plot-local (its INTERIOR S3 origin (40,30) -> (0,30)); selftest checks the copy
S3 = dict(pond=[(1 + i, 31 + j) for i in range(4) for j in range(3)], canal=[(15 + i, 32) for i in range(6)], pump=(9, 32),
          reelA=(9, 33), reelB=(9, 30), intake=(4, 32), intake_alt=[(4, 31), (4, 33)], outflow=(15, 32), battery=(12, 36))
LAKE = (40, 40, 6, 6)
CANAL = [(46 + i, 42) for i in range(6)]
POND = [(72 + i, 45 + j) for j in (0, 1) for i in range(3)]
POND_RIG = dict(pump=(73, 47), battery=(76, 46), pipes=[(73, 48), (73, 49)], tank=(73, 50))
POND_START_LEVELS = 0.6                                          # 600 L: "a natural pond holding under 1,000 L"

ROW_IDS = ["RIVER_LAYER_REDRAWS_CLEAN", "CONVERTER_BIG_RECIPE_RUNS", "REACTOR_NEXT_REACTION_RUNS", "RAILING_HAS_STUFF",
           "FAUCET_TAB_PIPE_ONLY", "T30_pipe_faucet", "FAUCET_LOOKS_RESOLVE", "FAUCET_TAKES_MODERN", "GUARDRAIL_ATLAS_RESOLVES",
           "REEL_FACINGS_LAY_ALONG_AXIS", "S3_HOSES_ON_BARE_GROUND", "SETTINGS_SEARCH_FINDS_ROW", "CANAL_LAKE_ONE_DEF",
           "POND_LAST_DROP_DRAWN", "POND_DRY_STAGES_TO_BED"]
ROW_ITEM = {
    "RIVER_LAYER_REDRAWS_CLEAN": ("FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM", "A1"),
    "CONVERTER_BIG_RECIPE_RUNS": ("FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST", "A1"),
    "REACTOR_NEXT_REACTION_RUNS": ("FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT", "A1"),
    "RAILING_HAS_STUFF": ("RAILING_MATERIAL_FIX_MADE_OF_NOTHING", "A1"),
    "FAUCET_TAB_PIPE_ONLY": ("PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE", "A1"),
    "T30_pipe_faucet": ("PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE", "A2"),
    "FAUCET_LOOKS_RESOLVE": ("FAUCET_REDRAW_BORROWED_BLEED_WELL", "A2"),
    "FAUCET_TAKES_MODERN": ("FAUCET_REDRAW_BORROWED_BLEED_WELL", "A3"),
    "GUARDRAIL_ATLAS_RESOLVES": ("GUARDRAIL_ART_RESKIN_BORROWED_FENCE", "A2"),
    "REEL_FACINGS_LAY_ALONG_AXIS": ("HOSE_REEL_FIX_TURNS_WITH_THE_SHIP", "A1"),
    "S3_HOSES_ON_BARE_GROUND": ("HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE", "A1"),
    "SETTINGS_SEARCH_FINDS_ROW": ("SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND", "A1"),
    "CANAL_LAKE_ONE_DEF": ("CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES", "A1"),
    "POND_LAST_DROP_DRAWN": ("POND_PUMP_FIX_LAST_DROP_COUNTS", "A2"),
    "POND_DRY_STAGES_TO_BED": ("POND_PUMP_FIX_LAST_DROP_COUNTS", "A3"),
}
# rows whose criterion is wider than the row: verify --result partial, never pass, from this row alone
PARTIAL = {"REEL_FACINGS_LAY_ALONG_AXIS": "the turning-gravship half is not staged",
           "FAUCET_TAKES_MODERN": "the clamp-on-axis half is def data (drawOffset), recorded not judged"}


def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ====================================================================== pure verdicts (selftest_sitting_gaps_proof.py)
def log_ok(alive, lost):
    """None when the journal can be trusted for an absence, else the why."""
    if not alive:
        return "the log sentinel did not come back (Verse.Log cap or a dead journal)"
    if lost:
        return "the journal tap lost %d entries" % lost
    return None


def river_verdict(enabled, alive, lost, step, bad, river_count=None):
    """step: the world_commit step dict for WorldDrawLayer_Rivers.RegenerateNow (None = absent); bad: matching log lines."""
    if enabled is not True:
        return "UNMEASURED", "SITE", "riverColorsEnabled reads %r" % (enabled,)
    if river_count == 0:
        return "UNMEASURED", "SITE", "the world has no river: the tint prefix never runs"
    if not step:
        return "UNMEASURED", "HARNESS", "world_commit reported no river-layer step"
    if str(step.get("status")) == "failed":
        return "FAIL", "MOD", "river layer regenerate threw: %s" % step.get("error")
    why = log_ok(alive, lost)
    if why:
        return "UNMEASURED", "HARNESS", why
    if bad:
        return "FAIL", "MOD", "%d exception line(s) during the river redraw" % len(bad)
    return ("PASS" if str(step.get("status")) == "ok" else "UNMEASURED"), "MOD", ""


def _li(el, tag):
    return [x.text for x in el.findall("%s/li" % tag) if x.text]


def def_census(defs_dir=DEFS):
    """(converters, conversions, reactions) from this mod's Defs: converters = [(defName, tier, processes)],
    conversions = {liquid: [(process, tier, product)]}, reactions = [defName]. Pure file read."""
    conv, rows, reac = [], {}, []
    for f in glob.glob(os.path.join(defs_dir, "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except (ET.ParseError, OSError):
            continue
        for d in root:
            name = d.findtext("defName")
            if d.tag.endswith("RM_LiquidReactionDef") and name:
                reac.append(name)
            c = d.find("conversions")
            if c is not None and name:
                for li in c.findall("li"):
                    rows.setdefault(name, []).append((li.findtext("process"), li.findtext("tier"),
                                                      li.findtext("product") or li.findtext("productThing")))
            if d.tag == "ThingDef":
                for li in d.iter("li"):
                    if str(li.get("Class", "")).endswith("CompProperties_LiquidConverter"):
                        conv.append((name, li.findtext("tier") or "Crude", _li(li, "processes")))
    return conv, rows, reac


TIERS = ("Crude", "Household", "Industrial")


def converter_pairs(conv, rows):
    """[(converter, liquidA, productA, liquidB, productB)]: one machine reaching two input liquids whose products differ."""
    out = []
    for name, tier, procs in conv:
        if not name:
            continue
        rank = TIERS.index(tier) if tier in TIERS else 0
        reach = []
        for liquid, steps in rows.items():
            for proc, t, prod in steps:
                if proc in procs and (TIERS.index(t) if t in TIERS else 0) <= rank and prod:
                    reach.append((liquid, prod))
                    break
        for i, (la, pa) in enumerate(reach):
            for lb, pb in reach[i + 1:]:
                if pa != pb:
                    out.append((name, la, pa, lb, pb))
    return out


def census_verdict(kind, conv, rows, reac):
    if kind == "converter":
        pairs = converter_pairs(conv, rows)
        if not pairs:
            prods = sorted({p for st in rows.values() for _, _, p in st if p})
            return "UNMEASURED", "SITE", dict(why="no shipped converter reaches two input liquids with different products, so 'the "
                                                  "small recipe's output full' cannot be staged while the big one has room",
                                              products=prods, converters=[c[0] for c in conv],
                                              owed="re-scope A1 or ship a test-only converter def")
        return "UNMEASURED", "HARNESS", dict(why="a stageable pair exists; the live stager for it is owed", pairs=pairs[:4])
    if len(reac) < 2:
        return "UNMEASURED", "SITE", dict(why="the reactor scene needs two reaction defs (A+B blocked, C+D runs); shipped: %s" % reac,
                                          owed="re-scope A1 or ship a test-only second RM_LiquidReactionDef")
    return "UNMEASURED", "HARNESS", dict(why="two reactions exist; the live stager is owed", reactions=reac)


def railing_verdict(alive, lost, railed, stuffs, bad):
    if railed is None:
        return "UNMEASURED", "HARNESS", "ProofRails did not answer"
    if railed <= 0:
        return "UNMEASURED", "SITE", "no railing placed: nothing to judge"
    why = log_ok(alive, lost)
    if why:
        return "UNMEASURED", "HARNESS", why
    if bad:
        return "FAIL", "MOD", "%d 'madeFromStuff but stuff=null' line(s)" % len(bad)
    if not stuffs:
        return "UNMEASURED", "HARNESS", "list_things found no RM_SuspensionRailing to read"
    nostuff = [s for s in stuffs if not s or str(s).lower() in ("none", "null")]
    if nostuff:
        return "FAIL", "MOD", "%d of %d railings have no stuff" % (len(nostuff), len(stuffs))
    return "PASS", "MOD", ""


def faucet_tab_verdict(category, listed, bare, piped, log_lines, log_read, n_categories=1):
    """category: the pipe-networks category id or None; listed: designator found; bare/piped: ProofCanPlace kv;
    n_categories: how many architect categories the listing returned (0 = the tool read nothing)."""
    if not n_categories:
        return "UNMEASURED", "HARNESS", "list_architect_categories returned nothing"
    if not category:
        return "FAIL", "MOD", "no VCHE_PipeNetworks category although FlowWorks ships it (RM_PipeNetworksTab.xml)"
    if not bare or not piped:
        return "UNMEASURED", "HARNESS", "ProofCanPlace did not answer"
    bad = []
    if not listed:
        bad.append("no RM_PipeFaucet designator in %s" % category)
    if bare.get("ok") != "False":
        bad.append("placeable on bare ground")
    if piped.get("ok") != "True":
        bad.append("refused on a universal pipe (%s)" % piped.get("why"))
    if log_read and log_lines:
        bad.append("%d Player.log error line(s) naming RM_PipeFaucet" % len(log_lines))
    if bad:
        return "FAIL", "MOD", "; ".join(bad)
    if not log_read:
        return "UNMEASURED", "HARNESS", "tab and placement pass; the Player.log half was not readable"
    return "PASS", "MOD", ""


OTHER_DRINKS = ("RM_DrinkFromTerrain", "RM_DrinkFromContainer", "RM_DrinkWaterItem", "Ingest")


def faucet_drink_verdict(u0, u1, jobs, need0, need1, memories):
    if u0 is None or u1 is None:
        return "UNMEASURED", "HARNESS", "the tank did not read"
    drop = u0 - u1
    seen = "RM_DrinkFromFaucet" in (jobs or [])
    if drop <= 0 and not seen:
        if any(j in OTHER_DRINKS for j in jobs or []):
            return "UNMEASURED", "SITE", "the colonist drank something else on the map (%s)" % sorted(set(jobs) & set(OTHER_DRINKS))
        return "FAIL", "MOD", "no drink at the faucet in the window (jobs %s)" % sorted(set(jobs or []))[:6]
    if drop <= 0:
        return "FAIL", "MOD", "a faucet drink job ran and the tank did not move"
    if drop % DRINK_DL:
        return "FAIL", "MOD", "the tank fell %d dL, not a whole number of %d dL drinks" % (drop, DRINK_DL)
    rose = need0 is not None and need1 is not None and need1 - need0 >= 0.3
    if not (seen or rose):
        return "FAIL", "MOD", "the tank fell but no faucet drink was seen and the need did not rise"
    if "RM_Thought_DrankRough" in (memories or []):
        return "FAIL", "MOD", "a faucet drink at home left RM_Thought_DrankRough"
    return "PASS", "MOD", ""


def look_verdict(per_look, looks=LOOKS, bad_log=()):
    """per_look: {look: {styled, path, badTex}}; PASS when every look's faucet resolves its own art."""
    missing = [lk for lk in looks if lk not in per_look]
    if missing:
        return "UNMEASURED", "HARNESS", "no read for %s" % missing
    unstyled = [lk for lk in looks if not per_look[lk].get("styled")]
    if unstyled:
        return "UNMEASURED", "SITE", "the pipe style did not take for %s" % unstyled
    bad = []
    for lk in looks:
        r = per_look[lk]
        if r.get("path") is None:
            return "UNMEASURED", "HARNESS", "thing_graphic read nothing for the %s faucet" % lk
        if "/faucet/%s/" % lk.lower() not in str(r.get("path")).lower() + "/":
            bad.append("%s faucet draws %s" % (lk, r.get("path")))
        if r.get("badTex") is not False:
            bad.append("%s faucet badTex %r" % (lk, r.get("badTex")))
    if bad_log:
        bad.append("%d error line(s) naming RM_PipeFaucet" % len(bad_log))
    return ("FAIL" if bad else "PASS"), "MOD", "; ".join(bad)


def guardrail_verdict(reads):
    """reads: {stuff: {spawned, path, chain, badTex}}."""
    if not reads:
        return "UNMEASURED", "HARNESS", "nothing read"
    bad = []
    for stuff, r in sorted(reads.items()):
        if not r.get("spawned"):
            return "UNMEASURED", "SITE", "no %s guardrail spawned" % stuff
        if r.get("path") is None:
            return "UNMEASURED", "HARNESS", "thing_graphic read nothing for the %s guardrail" % stuff
        if "rimmandrake/flowworks/guardrail" not in str(r.get("path")).lower():
            bad.append("%s rail draws %s" % (stuff, r.get("path")))
        if "appearances" not in " ".join(str(c) for c in r.get("chain") or []).lower():
            bad.append("%s rail graphic chain %s has no Graphic_Appearances" % (stuff, r.get("chain")))
        if r.get("badTex") is not False:
            bad.append("%s rail badTex %r" % (stuff, r.get("badTex")))
    return ("FAIL" if bad else "PASS"), "MOD", "; ".join(bad)


def reel_target(c, rot):
    """The lay target REEL_REACH cells straight out of a 2x2 footprint on corner c facing rot (centre-line cell)."""
    dx, dz = DIRS[rot]
    if dx:
        return (c[0] + 2 + REEL_REACH if dx > 0 else c[0] - 1 - REEL_REACH, c[1])
    return (c[0], c[1] + 2 + REEL_REACH if dz > 0 else c[1] - 1 - REEL_REACH)


def reel_axis_problems(c, rot, nozzle, pose):
    """[] when the hose of a reel on footprint corner c facing rot leaves along its facing: nozzle tip on that side of the
    footprint centre, the first drawn cell outside the footprint on that side, no drawn cell behind the reel."""
    dx, dz = DIRS[rot]
    cx, cz = c[0] + 1.0, c[1] + 1.0
    out = []
    if not nozzle or len(nozzle) < 2:
        return ["no nozzle tip read"]
    ndx, ndz = nozzle[0] - cx, nozzle[1] - cz
    if (ndx * dx + ndz * dz) <= 0.25 or abs(ndx * dz) + abs(ndz * dx) > abs(ndx * dx + ndz * dz):
        out.append("nozzle tip %s is not on the %s side of the footprint centre (%.1f,%.1f)" % (nozzle, "NESW"[rot], cx, cz))
    fp = {(c[0] + i, c[1] + j) for i in (0, 1) for j in (0, 1)}
    cells = [tuple(p) for p in pose or [] if tuple(p) not in fp]
    if not cells:
        return out + ["no drawn cell outside the footprint"]
    f = cells[0]
    side = {0: f[1] >= c[1] + 2, 1: f[0] >= c[0] + 2, 2: f[1] <= c[1] - 1, 3: f[0] <= c[0] - 1}[rot]
    if not side:
        out.append("the first drawn cell %s is not on the %s side" % (f, "NESW"[rot]))
    behind = [p for p in cells if {0: p[1] < c[1], 1: p[0] < c[0], 2: p[1] > c[1] + 1, 3: p[0] > c[0] + 1}[rot]]
    if behind:
        out.append("%d drawn cell(s) behind the reel (a U-turn), first %s" % (len(behind), behind[0]))
    return out


def reel_verdict(per_rot):
    """per_rot: {rot: {laid, problems}}."""
    if sorted(per_rot) != [0, 1, 2, 3]:
        return "UNMEASURED", "HARNESS", "not every facing was read: %s" % sorted(per_rot)
    unlaid = [r for r in range(4) if not per_rot[r].get("laid")]
    if unlaid:
        return "UNMEASURED", "SITE", "lay refused for facing(s) %s" % ["NESW"[r] for r in unlaid]
    bad = ["%s: %s" % ("NESW"[r], "; ".join(per_rot[r]["problems"])) for r in range(4) if per_rot[r].get("problems")]
    return ("FAIL" if bad else "PASS"), "MOD", " | ".join(bad)


def footprint(c):
    return {(c[0] + i, c[1] + j) for i in (0, 1) for j in (0, 1)}


def s3_forbidden(origin, own):
    """Absolute cells a hose of reel `own` ('A'|'B') must not draw across: pump, battery (1x2), the other reel's 2x2."""
    ox, oz = origin
    other = S3["reelB"] if own == "A" else S3["reelA"]
    cells = {S3["pump"], S3["battery"], (S3["battery"][0], S3["battery"][1] + 1)} | footprint(other)
    return {(x + ox, z + oz) for x, z in cells}


def s3_verdict(laid, crossings):
    """laid: {A, B} bools; crossings: {A: [cells], B: [cells]}."""
    if not all(laid.get(k) for k in ("A", "B")):
        return "UNMEASURED", "SITE", "hose(s) not laid: %s" % [k for k in ("A", "B") if not laid.get(k)]
    bad = ["hose %s crosses %s" % (k, sorted(crossings.get(k) or [])[:4]) for k in ("A", "B") if crossings.get(k)]
    return ("FAIL" if bad else "PASS"), "MOD", "; ".join(bad)


def search_verdict(opened, box, found, control_shows):
    """found: {query: bool}; control_shows: the label visible under the nonsense query."""
    if not opened:
        return "UNMEASURED", "HARNESS", "the FlowWorks settings dialog did not open"
    if not box:
        return "UNMEASURED", "HARNESS", "no search box in the dialog's layout"
    if control_shows is None or control_shows:
        return "UNMEASURED", "HARNESS", "the nonsense query still shows the row: the read cannot tell a hit from no filter"
    miss = [q for q in SEARCH_QUERIES if not found.get(q)]
    return ("FAIL" if miss else "PASS"), "MOD", ("not found by %s" % miss) if miss else ""


def canal_lake_verdict(canal, lake):
    """canal/lake: ProofWaterLook kv."""
    if not canal or not lake:
        return "UNMEASURED", "HARNESS", "ProofWaterLook did not answer"
    if canal.get("dug") != "True" or (fnum(canal.get("waterM")) or 0) <= 0:
        return "UNMEASURED", "SITE", "the canal square is not dug and wet (%s)" % canal
    wc, wl = fnum(canal.get("waterM")), fnum(lake.get("waterM"))
    if wc is None or wl is None:
        return "UNMEASURED", "HARNESS", "no water depth read"
    if abs(wc - wl) > 0.5:
        return "UNMEASURED", "SITE", "not the same water depth (canal %.2f m, lake %.2f m)" % (wc, wl)
    same = canal.get("terrain") == lake.get("terrain")
    return ("PASS" if same else "FAIL"), "MOD", "" if same else "canal draws %s, lake %s" % (canal.get("terrain"), lake.get("terrain"))


def pond_draw_verdict(powered, s0, s_end, u0, u1):
    """s0/s_end: body stock in notches; u0/u1: tank dL. PASS = drained to 0 dL and the tank gained exactly that."""
    if not powered:
        return "UNMEASURED", "SITE", "the pump never read powered"
    if None in (s0, s_end, u0, u1):
        return "UNMEASURED", "HARNESS", "a read returned nothing"
    if s0 * UNITS_PER_LEVEL >= 10000 or s0 <= 0:
        return "UNMEASURED", "SITE", "the pond did not start under 1,000 L (stock %.3f notches)" % s0
    left_dl = s_end * UNITS_PER_LEVEL
    gained = u1 - u0
    want = int(round(s0 * UNITS_PER_LEVEL))
    if left_dl > 0.5:
        return "FAIL", "MOD", "the pond kept %.1f dL the pump never took" % left_dl
    if abs(gained - want) > 1:
        return "FAIL", "MOD", "the tank gained %d dL, the pond held %d" % (gained, want)
    return "PASS", "MOD", ""


def pond_dry_verdict(drained, pond_kv, terrains):
    """pond_kv: ProofPondDepth kv ({} = no formed pond any more); terrains: {cell: defName}."""
    if not drained:
        return "UNMEASURED", "SITE", "the pond was never pumped dry"
    if not terrains or any(t is None for t in terrains.values()):
        return "UNMEASURED", "HARNESS", "a pond square's terrain did not read"
    bad = []
    wet = pond_kv.get("wet") if pond_kv else None
    if wet not in (None, "0"):
        bad.append("ProofPondDepth reads wet=%s at stock %s" % (wet, pond_kv.get("stock")))
    still = sorted(c for c, t in terrains.items() if "water" in str(t).lower())
    if still:
        bad.append("%d square(s) still draw water: %s" % (len(still), [terrains[c] for c in still][:3]))
    return ("FAIL" if bad else "PASS"), "MOD", "; ".join(bad)


# ====================================================================== the run
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,120")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--player-log", default=None, help="this load's Player.log (default: game_paths.PLAYER_LOG)")
    ap.add_argument("--drink-ticks", type=int, default=3000)
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-faults", default="", help="comma list: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    only = [x.strip() for x in a.only.split(",") if x.strip()] or list(ROW_IDS)
    if set(only) - set(ROW_IDS):
        ap.error("unknown --only row(s) %s" % ",".join(sorted(set(only) - set(ROW_IDS))))
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    if a.mock:
        raw = FakeBridge(faults)
        player_log = raw.player_log
    else:
        import proof_hose as PH          # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
        player_log = a.player_log or V.PLAYER_LOG
    B = V.guard(raw)
    out = a.out or (os.path.join(tempfile.gettempdir(), "sitting_gaps_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "sitting_gaps_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "sitting_gaps_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    if a.mock:
        res["mode"] = "mock"
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, cls, det):
        st, cls, det = V.PRE.judge(st, cls, det if isinstance(det, dict) else {"why": det})
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        item, crit = ROW_ITEM[rid]
        r = {"id": rid, "status": st, "class": cls, "item": item, "criterion": crit, "detail": det}
        if rid in PARTIAL:
            r["partial"] = PARTIAL[rid]
        rows.append(r)
        print("%-28s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def static(ty, method, arg, answer=False):
        r = B.call("jawa/static_call", type=ty, method=method, args=arg, _answer=answer) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        ok = r.get("success") is True and not txt.startswith("REFUSED")
        if not answer:
            V.require(ok, "%s answered" % method, txt[:200], cls="HARNESS")
        return (parse(txt) if ok else {}), txt

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        V.require(r.get("success") is not False, "the clock moved %d ticks" % n, r, cls="HARNESS")
        return r.get("success") is not False

    def build(ops, stuff=None):
        kw = dict(ops=ops, faction="player", wipeExisting=False)
        if stuff:
            kw["stuff"] = stuff
        return B.call("jawa/build_batch", **kw) or {}

    def sget(ty, f):
        return (B.call("jawa/mod_settings_field", typeName=ty, action="get", field=f, _answer=True) or {}).get("value")

    def sset(ty, f, v):
        return B.call("jawa/mod_settings_field", typeName=ty, action="set", field=f, value=str(v), _answer=True) or {}

    def truthy(v):
        return {True: True, False: False, "true": True, "false": False, "True": True, "False": False}.get(v)

    def tap():
        t = V.LogTap(B)
        return t, V.log_alive(B, "sitting_gaps").get("alive")

    def lines(t, *needles):
        return [str(e.get("Message", ""))[:200] for e in t.since()
                if all(n.lower() in str(e.get("Message", "")).lower() for n in needles)]

    def graphic(rect, defs):
        r = B.call("jawa/thing_graphic", rect="%d,%d,%d,%d" % rect, defs=defs, _answer=True) or {}
        return r.get("things") or []

    def dig(c, n, fill=-1):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}

    def shot(name, rect):
        if a.no_shots or a.mock:
            return None
        B.call("jawa/clear_ui", all=True, _answer=True)
        B.call("rimworld/set_camera_zoom", rootSize=8, _answer=True)
        B.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=2, _answer=True)
        time.sleep(1.5)
        return (B.call("jawa/take_screenshot", fileName="sitting_gaps_%s_%d" % (name, int(time.time())), _answer=True) or {}).get("filePath")

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)        # noqa: E731
    xz = lambda c: "%d,%d" % c                   # noqa: E731

    # ------------------------------------------------------------------ preflight
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        for rid in only:
            row(rid, "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    if not a.mock:
        rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
        res["running"] = len(rm.get("packageIds") or [])
        V.log_revive(B)
        V.tap_start(B)
        res["site_calm"] = V.site_calm(B)
        B.call("jawa/kill_hostiles")
        B.call("jawa/weather_set", weather="Clear", lockWeather=True)
        B.call("jawa/incident_queue_clear")
        site_rows = []
        rect = (max(ox - 2, 1), max(oz - 4, 1), 100, 62)
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "sitting_gaps_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            for rid in only:
                row(rid, "UNMEASURED", "SITE", {"why": "site not prepared", "rect": rect, "site": bad[:3]})
            return 2
    # the start colony drafted and walked off the site for the whole run (SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL)
    start = [c.get("pawnId") for c in (B.call("rimworld/list_colonists", currentMapOnly=True, _answer=True) or {}).get("colonists") or []
             if not c.get("dead") and c.get("pawnId")]
    park = (max(ox - 8, 2), max(oz - 8, 2))
    res["startColonistsParked"] = [(pid, (B.call("jawa/order_pawn", pawnId=pid, x=park[0], z=park[1], waitTicks=1, draft=True,
                                                 unpause=False, _answer=True) or {}).get("success")) for pid in start]
    ctx = dict(a=a, B=B, P=P, xz=xz, row=row, static=static, ticks=ticks, build=build, sget=sget, sset=sset, truthy=truthy,
               tap=tap, lines=lines, graphic=graphic, dig=dig, shot=shot, res=res, only=only, player_log=player_log,
               origin=(ox, oz))
    for name, fn in SCENES:
        mine = [r for r in SCENE_ROWS[name] if r in only]
        if mine:
            print("== scene %s (%s)" % (name, ",".join(mine)), flush=True)
            with V.scope(name):
                try:
                    fn(ctx, mine)
                except Exception as ex:  # noqa: BLE001 - a crashed scene is UNMEASURED/HARNESS, the run goes on
                    done = {r["id"] for r in rows}
                    for rid in mine:
                        if rid not in done:
                            row(rid, "UNMEASURED", "HARNESS", {"why": "scene %s raised %r" % (name, ex)})
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
        print("MOCK: sitting gaps: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    unm = [r for r in rows if r["status"] != "PASS"]
    print("sitting gaps: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), len(unm), out))
    return 1 if fails else (2 if unm else 0)


# ====================================================================== scenes
def scene_river(ctx, mine):
    B, row = ctx["B"], ctx["row"]
    en = ctx["truthy"](ctx["sget"](S_RIVER, "riverColorsEnabled"))
    t, alive = ctx["tap"]()
    r = B.call("jawa/world_commit", redraw=True, clearCaches=False, recalcPaths=False, lazy=False, _answer=True) or {}
    step = next((s for s in r.get("steps") or [] if "Rivers" in str(s.get("step"))), None)
    bad = ctx["lines"](t, "InvalidOperationException") + ctx["lines"](t, "RiverColor")
    st, cls, why = river_verdict(en, alive, t.lost, step, bad, r.get("riverCount"))
    row("RIVER_LAYER_REDRAWS_CLEAN", st, cls, dict(why=why, enabled=en, step=step, badLines=bad[:4], lost=t.lost, alive=alive,
                                                   commit=r.get("success")))


def scene_census(ctx, mine):
    conv, rows_, reac = def_census()
    if "CONVERTER_BIG_RECIPE_RUNS" in mine:
        st, cls, det = census_verdict("converter", conv, rows_, reac)
        ctx["row"]("CONVERTER_BIG_RECIPE_RUNS", st, cls, det)
    if "REACTOR_NEXT_REACTION_RUNS" in mine:
        st, cls, det = census_verdict("reactor", conv, rows_, reac)
        ctx["row"]("REACTOR_NEXT_REACTION_RUNS", st, cls, det)


def scene_railing(ctx, mine):
    B, P, xz, static = ctx["B"], ctx["P"], ctx["xz"], ctx["static"]
    t, alive = ctx["tap"]()
    for i in range(1, 7):
        r = ctx["dig"](P(i, 0), 8)
        V.require(r.get("depth", 8) == 8, "trench (%d,0) dug to 8" % i, r)
    kv, txt = static(SUSP, "ProofBuild", "%s;%s;timber;god" % (xz(P(0, 0)), xz(P(7, 0))))
    V.require(kv.get("ok") == "True", "the timber bridge stands", txt)
    kr, tr = static(SUSP, "ProofRails", "%s;on" % xz(P(2, 0)), answer=True)
    railed = int(kr["railed"]) if str(kr.get("railed", "")).isdigit() else (0 if tr.startswith("RAILS none") else None)
    lt = B.call("jawa/list_things", defName="RM_SuspensionRailing", rect="%d,%d,10,3" % P(-1, -1), limit=50, _answer=True) or {}
    stuffs = [x.get("stuff") for x in lt.get("things") or []]
    bad = ctx["lines"](t, RAIL_ERR)
    st, cls, why = railing_verdict(alive, t.lost, railed, stuffs, bad)
    ctx["row"]("RAILING_HAS_STUFF", st, cls, dict(why=why, build=txt, rails=tr, stuffs=stuffs[:12], badLines=bad[:3], lost=t.lost,
                                                  playerPath="INFERRED: RailingStuffFor runs before the godMode branch"))


def _pipe_category(B):
    """(category id or None, number of categories listed)."""
    cats = (B.call("rimworld/list_architect_categories", _answer=True) or {}).get("categories") or []
    for c in cats:
        key = re.sub(r"[^a-z]", "", (str(c.get("id")) + str(c.get("label"))).lower())
        if "pipenetwork" in key:
            return c.get("id"), len(cats)
    return None, len(cats)


def _listed(B, cat, needle="pipefaucet"):
    off = 0
    for _ in range(20):
        r = B.call("rimworld/list_architect_designators", categoryId=cat, includeHidden=False, offset=off, _answer=True) or {}
        for d in r.get("designators") or []:
            if needle in re.sub(r"[^a-z]", "", json.dumps(d).lower()):
                return d.get("id") or d.get("label")
        off = (r.get("page") or {}).get("nextOffset")
        if not off:
            return None
    return None


def player_log_errors(path, needle="RM_PipeFaucet"):
    """(read_ok, [error lines naming needle]) from a Player.log copy. read_ok needs the load's own header line."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            txt = f.read()
    except (OSError, TypeError):
        return False, []
    if "RimWorld" not in txt[:4000]:
        return False, []
    bad = [ln.strip()[:200] for ln in txt.splitlines()
           if needle in ln and re.search(r"error|exception|could not|failed", ln, re.I)]
    return True, bad


def scene_faucet(ctx, mine):
    B, P, xz, static, row = ctx["B"], ctx["P"], ctx["xz"], ctx["static"], ctx["row"]
    if "FAUCET_TAB_PIPE_ONLY" in mine:
        cat, ncat = _pipe_category(B)
        listed = _listed(B, cat) if cat else None
        kb, tb = static(LPROOF, "ProofCanPlace", "RM_PipeFaucet;%s" % xz(P(10, 0)))
        ctx["build"]("RM_UniversalPipe:%d,%d" % P(12, 0))
        kp, tp = static(LPROOF, "ProofCanPlace", "RM_PipeFaucet;%s" % xz(P(12, 0)))
        read_ok, bad = player_log_errors(ctx["player_log"])
        st, cls, why = faucet_tab_verdict(cat, listed, kb, kp, bad, read_ok, ncat)
        row("FAUCET_TAB_PIPE_ONLY", st, cls, dict(why=why, category=cat, designator=listed, bare=tb, piped=tp, logRead=read_ok,
                                                  logLines=bad[:4]))
    if "T30_pipe_faucet" in mine:
        _faucet_drink(ctx)
    if {"FAUCET_LOOKS_RESOLVE", "FAUCET_TAKES_MODERN"} & set(mine):
        _faucet_looks(ctx, mine)


def _faucet_drink(ctx):
    B, P, row = ctx["B"], ctx["P"], ctx["row"]
    was = ctx["truthy"](ctx["sget"](S_TH, "pipeFaucetsEnabled"))
    if was is not True:
        ctx["sset"](S_TH, "pipeFaucetsEnabled", True)
    try:
        tank = P(0, 6)
        b = ctx["build"](";".join(["RM_LiquidTank:%d,%d" % tank] + ["RM_UniversalPipe:%d,%d" % P(x, 6) for x in (2, 3, 4)]))
        V.require(b.get("success") is not False, "tank and pipe built", b)
        ctx["build"]("RM_PipeFaucet:%d,%d" % P(4, 6))
        f = B.hp("filltank:%d,%d=%s,20000" % (tank + (FRESH,)))
        V.require(f.get("success") is True, "the tank filled", f)
        sp = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(7, 6)[0], z=P(7, 6)[1], faction="player", count=1) or {}
        pid = ((sp.get("pawns") or [{}])[0]).get("id")
        V.require(pid is not None, "a colonist spawned", sp)
        for nd in ("Food", "Rest", "Joy"):
            B.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=1.0, _answer=True)
        B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.15, _answer=True)

        def need_mem():
            r = B.call("jawa/pawn_need", pawn=pid, action="list", _answer=True) or {}
            lv = next((fnum(n.get("level")) for n in r.get("needs") or [] if n.get("need") == "RM_Thirst"), None)
            return lv, [m.get("def") for m in r.get("memories") or []]

        def units():
            r = B.hp("tank:%d,%d" % tank, answer=True)
            return r.get("units") if r.get("success") else None

        n0, _m0 = need_mem()
        u0, jobs, waited = units(), [], 0
        while waited < ctx["a"].drink_ticks:
            if not ctx["ticks"](60):
                break
            waited += 60
            for c in (B.call("rimworld/list_colonists", currentMapOnly=True, _answer=True) or {}).get("colonists") or []:
                if str(c.get("pawnId")).replace("Thing_", "") == str(pid).replace("Thing_", "") and c.get("job"):
                    jobs.append(str(c.get("job")))
            u = units()
            if u is not None and u0 is not None and u < u0 and "RM_DrinkFromFaucet" not in (jobs[-1:] or [None]):
                break
        n1, m1 = need_mem()
        u1 = units()
        st, cls, why = faucet_drink_verdict(u0, u1, jobs, n0, n1, m1)
        row("T30_pipe_faucet", st, cls, dict(why=why, u0=u0, u1=u1, jobs=sorted(set(jobs)), need0=n0, need1=n1,
                                             rough="RM_Thought_DrankRough" in (m1 or []), waited=waited, settingWas=was))
    finally:
        if was is False:
            ctx["sset"](S_TH, "pipeFaucetsEnabled", False)


def _faucet_looks(ctx, mine):
    B, P, row = ctx["B"], ctx["P"], ctx["row"]
    t, alive = ctx["tap"]()
    per = {}
    for k, look in enumerate(LOOKS):
        c = P(10 + 3 * k, 12)
        ctx["build"]("RM_UniversalPipe:%d,%d" % c)
        pipe = ((B.call("jawa/list_things", defName="RM_UniversalPipe", rect="%d,%d,1,1" % c, limit=2, _answer=True) or {})
                .get("things") or [{}])[0].get("id")
        sp = B.call("jawa/set_thing_props", thing=pipe, style="RM_UniversalPipe_%s" % look, _answer=True) if pipe else {}
        pg = ctx["graphic"]((c[0], c[1], 1, 1), "RM_UniversalPipe")
        styled = bool(pipe) and sp.get("success") is not False and any("/%s/" % look.lower() in str(g.get("graphicPath")).lower()
                                                                     for g in pg)
        ctx["build"]("RM_PipeFaucet:%d,%d" % c)
        fg = ctx["graphic"]((c[0], c[1], 1, 1), "RM_PipeFaucet")
        g = fg[0] if fg else {}
        per[look] = dict(styled=styled, path=g.get("graphicPath") if fg else None, badTex=g.get("badTex"), pipePath=[x.get("graphicPath") for x in pg][:1])
    bad = ctx["lines"](t, "RM_PipeFaucet", "rror")
    why_log = log_ok(alive, t.lost)
    shot = ctx["shot"]("faucet_looks", (P(10, 12)[0], P(10, 12)[1], 12, 1))
    if "FAUCET_LOOKS_RESOLVE" in mine:
        st, cls, why = look_verdict(per, LOOKS, bad)
        if st == "PASS" and why_log:
            st, cls, why = "UNMEASURED", "HARNESS", why_log
        row("FAUCET_LOOKS_RESOLVE", st, cls, dict(why=why, looks=per, badLines=bad[:3], shot=shot))
    if "FAUCET_TAKES_MODERN" in mine:
        st, cls, why = look_verdict(per, ("Modern",))
        row("FAUCET_TAKES_MODERN", st, cls, dict(why=why, modern=per.get("Modern"), shot=shot, clamp="def data: RM_PipeFaucet_Modern drawOffset"))


def scene_guardrail(ctx, mine):
    B, P, row = ctx["B"], ctx["P"], ctx["row"]
    for x in (20, 21):
        r = ctx["dig"](P(x, 2), 4)
        V.require(r.get("depth", 4) == 4, "pit (%d,2) dug" % x, r)
    reads = {}
    for x, stuff in ((20, "WoodLog"), (21, "Steel")):
        c = P(x, 3)
        ctx["build"]("RM_PitGuardrail:%d,%d" % c, stuff=stuff)
        lt = B.call("jawa/list_things", defName="RM_PitGuardrail", rect="%d,%d,1,1" % c, limit=2, _answer=True) or {}
        th = lt.get("things") or []
        g = ctx["graphic"]((c[0], c[1], 1, 1), "RM_PitGuardrail")
        g0 = g[0] if g else {}
        # list_things' stuff may come back as the defName or its label ("wood log", "steel"): match the word, not the spelling
        reads[stuff] = dict(spawned=bool(th) and stuff.lower()[:4] in str(th[0].get("stuff")).lower(), stuffRead=th[0].get("stuff") if th else None,
                            path=g0.get("graphicPath") if g else None,
                            chain=g0.get("graphicChain") or [g0.get("graphicClass")], badTex=g0.get("badTex"))
    st, cls, why = guardrail_verdict(reads)
    row("GUARDRAIL_ATLAS_RESOLVES", st, cls, dict(why=why, reads=reads, shot=ctx["shot"]("guardrail", (P(19, 1)[0], P(19, 1)[1], 4, 4))))


def _census_hose(B, corner):
    for h in (B.hp("census", answer=True) or {}).get("hoses") or []:
        if V.reel_at(h.get("reel"), corner):
            return h
    return None


def scene_reels(ctx, mine):
    B, P = ctx["B"], ctx["P"]
    per = {}
    for rot in range(4):
        c = P(*REEL_CORNERS[rot])
        ctx["build"]("RM_HoseReel:%d,%d,%d" % (V.reel_pos(c, rot) + (rot,)))
        tgt = reel_target(c, rot)
        la = B.hp("lay:%d,%d,%d,%d" % (V.reel_pos(c, rot) + tgt), answer=True)
        h = _census_hose(B, c) or {}
        laid = la.get("success") is True and bool(h.get("laid"))
        probs = reel_axis_problems(c, rot, h.get("nozzleTip"), h.get("poseCells")) if laid else []
        per[rot] = dict(laid=laid, problems=probs, target=tgt, reason=la.get("reason"), nozzle=h.get("nozzleTip"),
                        reelArt=(h.get("draw") or {}).get("reelArt"))
    st, cls, why = reel_verdict(per)
    ctx["row"]("REEL_FACINGS_LAY_ALONG_AXIS", st, cls, dict(why=why, facings={"NESW"[r]: v for r, v in per.items()},
                                                            gravship="not staged"))


def scene_s3(ctx, mine):
    B, P = ctx["B"], ctx["P"]
    L = lambda c: P(c[0], c[1])                 # noqa: E731
    xs = [c[0] for c in S3["pond"]]
    zs = [c[1] for c in S3["pond"]]
    B.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,4,3" % L((min(xs), min(zs))))
    ctx["ticks"](2)
    B.call("jawa/flowworks_body_report", x=L(S3["pond"][0])[0], z=L(S3["pond"][0])[1], classify=True, _answer=True)
    for c in S3["canal"]:
        ctx["dig"](L(c), 1)
    ra, rb = L(S3["reelA"]), L(S3["reelB"])
    opA, opB = V.reel_toward(ra, L(S3["intake"])), V.reel_toward(rb, L(S3["outflow"]))
    ctx["build"](";".join(["RM_LiquidPump:%d,%d" % L(S3["pump"]), opA, opB, "Battery:%d,%d" % L(S3["battery"])]))
    posA = tuple(int(v) for v in opA.split(":")[1].split(",")[:2])
    posB = tuple(int(v) for v in opB.split(":")[1].split(",")[:2])
    la = B.hp("lay:%d,%d,%d,%d" % (posA + L(S3["intake"])), answer=True)
    for alt in S3["intake_alt"]:
        if la.get("success"):
            break
        la = B.hp("lay:%d,%d,%d,%d" % (posA + L(alt)), answer=True)
    lb = B.hp("lay:%d,%d,%d,%d" % (posB + L(S3["outflow"])), answer=True)
    laid, cross = {}, {}
    for k, corner in (("A", ra), ("B", rb)):
        h = _census_hose(B, corner) or {}
        laid[k] = bool(h.get("laid")) and (la if k == "A" else lb).get("success") is True
        bad = s3_forbidden(ctx["origin"], k)
        cross[k] = sorted({tuple(p) for p in h.get("poseCells") or []} & bad)
    st, cls, why = s3_verdict(laid, cross)
    ctx["row"]("S3_HOSES_ON_BARE_GROUND", st, cls, dict(why=why, laid=laid, crossings=cross, layA=la.get("reason"),
                                                        layB=lb.get("reason"),
                                                        shot=ctx["shot"]("s3_hoses", L((-2, 28)) + (26, 12))))


def scene_search(ctx, mine):
    B = ctx["B"]
    surf = None
    for o in _walk_dicts(B.call("rimworld/list_mod_settings_surfaces", _answer=True) or {}):
        if o.get("handleTypeName") == "RimMandrakeFlowWorksMod" and str(o.get("modId", "")).startswith("mod-settings:" + MOD_ID):
            surf = o["modId"]
            break
    opened = (B.call("rimworld/open_mod_settings", modId=surf or MOD_ID, replaceExisting=True, _answer=True) or {}).get("success") is True
    found, control, box = {}, None, None
    try:
        if opened:
            box = _search_box(B)
            if box:
                for q in SEARCH_QUERIES:
                    found[q] = _typed_finds(B, q)
                control = _typed_finds(B, SEARCH_CONTROL)
    finally:
        B.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True, _answer=True)
    st, cls, why = search_verdict(opened, box, found, control)
    ctx["row"]("SETTINGS_SEARCH_FINDS_ROW", st, cls, dict(why=why, surface=surf, found=found, controlShows=control))


def _walk_dicts(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            for x in _walk_dicts(v):
                yield x
    elif isinstance(o, list):
        for v in o:
            for x in _walk_dicts(v):
                yield x


def _settings_elements(B):
    lay = B.call("rimworld/get_ui_layout", _answer=True) or {}
    surf = [x for x in lay.get("surfaces") or [] if "ModSettings" in str(x.get("type"))]
    return (surf[-1] if surf else {}).get("elements") or []


def _search_box(B):
    fields = [e for e in _settings_elements(B) if str(e.get("kind")) == "text_field"]
    # the search box is the narrow one (live_session._search_box: wide entries are labelled-entry rows)
    return min(fields, key=lambda e: (e.get("screenRect") or {}).get("width", 9999)) if fields else None


def _typed_finds(B, q):
    """Type q into the search box, read only LABEL elements (the box itself now holds q), clear the box."""
    box = _search_box(B)
    if not box:
        return None
    B.call("rimworld/set_text_field", targetId=box.get("targetId"), text=q, mode="instant", _answer=True)
    labels = [str(e.get("label") or "") for e in _settings_elements(B)
              if str(e.get("kind")) in ("label", "checkbox", "button", "section_header") and e.get("label")]
    hit = any(SEARCH_LABEL.lower() in t.lower() for t in labels)
    box2 = _search_box(B)
    if box2:
        B.call("rimworld/set_text_field", targetId=box2.get("targetId"), text="", mode="instant", _answer=True)
    return hit


def scene_canal_lake(ctx, mine):
    B, P, static = ctx["B"], ctx["P"], ctx["static"]
    x0, z0, w, h = LAKE
    B.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,%d,%d" % (P(x0, z0) + (w, h)))
    ctx["ticks"](2)
    B.call("jawa/flowworks_body_report", x=P(x0 + 2, z0 + 2)[0], z=P(x0 + 2, z0 + 2)[1], classify=True, _answer=True)
    for c in CANAL:
        ctx["dig"](P(*c), 6, fill=6)
    ctx["ticks"](500)
    kc, tc = static(WLOOK, "ProofWaterLook", "%d,%d" % P(48, 42))
    kl, tl = static(WLOOK, "ProofWaterLook", "%d,%d" % P(43, 42))
    st, cls, why = canal_lake_verdict(kc, kl)
    ctx["row"]("CANAL_LAKE_ONE_DEF", st, cls, dict(why=why, canal=tc, lake=tl, judge="L3: an Opus judge reads the frame",
                                                   shot=ctx["shot"]("canal_lake", P(38, 38) + (16, 10))))


def scene_pond(ctx, mine):
    B, P, static, row = ctx["B"], ctx["P"], ctx["static"], ctx["row"]
    exact = ctx["truthy"](ctx["sget"](S_FW, "levelExactEnabled"))
    refill_was = ctx["sget"](S_FW, "refillEnabled")
    pond = [P(*c) for c in POND]
    try:
        if exact is not True:
            for rid in mine:
                row(rid, "UNMEASURED", "SITE", {"why": "levelExactEnabled reads %r" % (exact,)})
            return
        B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % pond[0])
        cls_r = B.call("jawa/flowworks_body_report", x=pond[1][0], z=pond[1][1], classify=True, _answer=True) or {}
        body = cls_r.get("body") or {}
        V.require(body and not body.get("limitless") and body.get("cellCount") == 6, "a 6-square limited pond", body, cls="SITE")
        ctx["sset"](S_FW, "refillEnabled", False)
        cap = fnum(body.get("capacity")) or 0
        V.require(cap > 0, "the pond has a capacity", body, cls="SITE")
        static(NPROOF, "ProofSetBodyFraction", "%d;%d;%.6f" % (pond[1][0], pond[1][1], POND_START_LEVELS / cap if cap else 0))
        rig = POND_RIG
        ctx["build"](";".join(["RM_LiquidPump:%d,%d" % P(*rig["pump"]), "Battery:%d,%d" % P(*rig["battery"])]
                              + ["RM_UniversalPipe:%d,%d" % P(*c) for c in rig["pipes"]] + ["RM_LiquidTank:%d,%d" % P(*rig["tank"])]))
        ctx["ticks"](2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % P(*rig["battery"]), limit=2, _answer=True) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0, _answer=True)

        def stock():
            r = B.call("jawa/flowworks_body_report", x=pond[1][0], z=pond[1][1], classify=False, _answer=True) or {}
            b = r.get("body")
            return 0.0 if (r.get("success") is not False and b is None) else fnum((b or {}).get("stock"))

        def units():
            r = B.hp("tank:%d,%d" % P(*rig["tank"]), answer=True)
            return r.get("units") if r.get("success") else None

        s0, u0, powered, trace = stock(), units(), False, []
        for _ in range(12):
            ctx["ticks"](250)
            pm = B.hp("pump:%d,%d" % P(*rig["pump"]), answer=True)
            powered = powered or pm.get("powered") is True
            s, u = stock(), units()
            trace.append(dict(stock=s, units=u, moved=pm.get("lastMovedUnits")))
            if s is not None and s * UNITS_PER_LEVEL <= 0.5:
                break
        s_end, u1 = trace[-1]["stock"] if trace else None, trace[-1]["units"] if trace else None
        if "POND_LAST_DROP_DRAWN" in mine:
            st, cls, why = pond_draw_verdict(powered, s0, s_end, u0, u1)
            row("POND_LAST_DROP_DRAWN", st, cls, dict(why=why, s0=s0, sEnd=s_end, u0=u0, u1=u1, trace=trace, capacity=cap))
        if "POND_DRY_STAGES_TO_BED" in mine:
            drained = s_end is not None and s_end * UNITS_PER_LEVEL <= 0.5
            B.hp("flick:%d,%d=off" % P(*rig["pump"]), answer=True)
            ctx["ticks"](260)
            kp, tp = static(PROMO, "ProofPondDepth", "%d,%d" % pond[1], answer=True)
            terr = {}
            for c in pond:
                ci = B.call("rimworld/get_cell_info", x=c[0], z=c[1], _answer=True) or {}
                terr["%d,%d" % c] = (ci.get("cell") or {}).get("terrainDefName")
            st, cls, why = pond_dry_verdict(drained, kp, terr)
            row("POND_DRY_STAGES_TO_BED", st, cls, dict(why=why, pondDepth=tp, terrains=terr,
                                                        shot=ctx["shot"]("pond_dry", P(70, 43) + (8, 9))))
    finally:
        if refill_was is not None:
            ctx["sset"](S_FW, "refillEnabled", refill_was)


SCENES = [("river", scene_river), ("census", scene_census), ("railing", scene_railing), ("faucet", scene_faucet),
          ("guardrail", scene_guardrail), ("reels", scene_reels), ("s3", scene_s3), ("search", scene_search),
          ("canal_lake", scene_canal_lake), ("pond", scene_pond)]
SCENE_ROWS = {"river": ["RIVER_LAYER_REDRAWS_CLEAN"], "census": ["CONVERTER_BIG_RECIPE_RUNS", "REACTOR_NEXT_REACTION_RUNS"],
              "railing": ["RAILING_HAS_STUFF"],
              "faucet": ["FAUCET_TAB_PIPE_ONLY", "T30_pipe_faucet", "FAUCET_LOOKS_RESOLVE", "FAUCET_TAKES_MODERN"],
              "guardrail": ["GUARDRAIL_ATLAS_RESOLVES"], "reels": ["REEL_FACINGS_LAY_ALONG_AXIS"], "s3": ["S3_HOSES_ON_BARE_GROUND"],
              "search": ["SETTINGS_SEARCH_FINDS_ROW"], "canal_lake": ["CANAL_LAKE_ONE_DEF"],
              "pond": ["POND_LAST_DROP_DRAWN", "POND_DRY_STAGES_TO_BED"]}


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small world model answering in the live tools' shapes. It knows nothing about the game: a mock verdict proves the
    script's control flow and its MOD/SITE/HARNESS split only. Faults, one wrong thing each (expected rows in the selftest):
      river_throws      MOD: the river layer regenerate throws InvalidOperationException
      river_off         riverColorsEnabled reads False                                  -> UNMEASURED/SITE
      log_dead          the log sentinel never comes back                               -> journal rows UNMEASURED/HARNESS
      rail_nostuff      MOD: railings made with stuff=null (and the error line)
      rail_none         ProofRails places no railing                                    -> UNMEASURED/SITE
      no_pipenet_tab    MOD: the VCHE_PipeNetworks category FlowWorks ships is missing   -> FAUCET_TAB FAIL
      faucet_anywhere   MOD: the faucet places on bare ground
      faucet_untabbed   MOD: the faucet has no designator in the pipe tab
      faucet_log_error  MOD: Player.log carries a config error naming RM_PipeFaucet
      faucet_dry        MOD: a thirsty colonist never drinks at the faucet
      faucet_rough      MOD: a faucet drink leaves RM_Thought_DrankRough
      other_water       the colonist drinks terrain water elsewhere                     -> T30 UNMEASURED/SITE
      faucet_nomatch    MOD: every faucet keeps the Scrapper look (MatchPipeUnder dead) -> LOOKS + MODERN FAIL
      pipe_style_refused the pipe style never takes                                     -> LOOKS + MODERN UNMEASURED/SITE
      rail_fence_art    MOD: the guardrail draws the vanilla fence atlas
      reel_fixed_west   MOD: every reel's outlet stays West whatever its facing
      reel_lay_refused  the lays are refused                                            -> REEL UNMEASURED/SITE
      hose_over_pump    MOD: hose A is drawn across the pump square
      search_misses     MOD: 'pieces' finds nothing
      search_unfiltered the search never filters (control shows the row)                -> UNMEASURED/HARNESS
      no_dialog         the settings dialog does not open                               -> UNMEASURED/HARNESS
      canal_two_defs    MOD: canal and lake draw different defs at equal depth
      canal_dry         the canal fill never takes                                      -> UNMEASURED/SITE
      pond_remainder    MOD: the pump leaves the sub-notch remainder                    -> DRAWN FAIL, DRY UNMEASURED/SITE
      pond_wet_at_zero  MOD: the dry pond still draws water
      pump_unpowered    the pump never powers                                           -> both POND rows UNMEASURED/SITE"""
    FAULTS = ("river_throws", "river_off", "log_dead", "rail_nostuff", "rail_none", "no_pipenet_tab", "faucet_anywhere",
              "faucet_untabbed", "faucet_log_error", "faucet_dry", "faucet_rough", "other_water", "faucet_nomatch",
              "pipe_style_refused", "rail_fence_art", "reel_fixed_west", "reel_lay_refused", "hose_over_pump", "search_misses",
              "search_unfiltered", "no_dialog", "canal_two_defs", "canal_dry", "pond_remainder", "pond_wet_at_zero",
              "pump_unpowered")

    def __init__(self, faults=()):
        self.f = set(faults)
        self.seq = 9
        self.logs = []
        self._log("Message", "fake journal start")     # a real journal is never empty: the tap's first read has a sequence
        self.nid = 100
        self.things = {}        # id -> dict(def, cell, stuff, style, rot)
        self.tanks = {}         # cell -> units
        self.dug = {}           # cell -> (depth, fill)
        self.terrain = {}
        self.pawns = {}
        self.reels = {}         # pos -> dict(rot, corner, laid, to)
        self.query = ""
        self.dialog = False
        self.stock = None
        self.cap = 12.0
        self.pond_pump = self.pond_tank = None
        self.pump_off = False
        fd, self.player_log = tempfile.mkstemp(suffix="_Player.log")
        with os.fdopen(fd, "w") as f:
            f.write("Mono path[0] = ...\nRimWorld 1.6.4630 rev123\n")
            if "faucet_log_error" in self.f:
                f.write("Config error in RM_PipeFaucet: graphicData is null\n")

    def _log(self, level, msg):
        self.seq += 1
        self.logs.append({"Sequence": self.seq, "Level": level, "Message": msg, "RepeatCount": 1})

    def _thing(self, d, c, stuff=None, rot=0, style=None):
        self.nid += 1
        tid = "%s%d" % (d, self.nid)
        self.things[tid] = dict(defName=d, cell=c, stuff=stuff, rot=rot, style=style)
        return tid

    def _at(self, d, c):
        return [t for t, v in self.things.items() if v["defName"] == d and v["cell"] == c]

    def _in(self, d, rect):
        x, z, w, h = rect
        ds = set(str(d).split(",")) if d else None
        return [t for t, v in self.things.items() if (ds is None or v["defName"] in ds)
                and x <= v["cell"][0] < x + w and z <= v["cell"][1] < z + h]

    # ---- the hose probe
    def hp(self, cmd, wait_s=20.0):
        verb, _, arg = cmd.partition(":")
        if cmd == "census":
            hoses = []
            for pos, r in self.reels.items():
                c, rot = r["corner"], r["rot"]
                out = 3 if "reel_fixed_west" in self.f else rot
                dx, dz = DIRS[out]
                noz = [c[0] + 1 + dx * 1.1, c[1] + 1 + dz * 1.1]
                pose = []
                if r["laid"]:
                    # straight out of the nozzle side, then to the target (the fixed-West fault U-turns past the reel)
                    sx, sz = (c[0] + (2 if dx > 0 else (-1 if dx < 0 else 0)), c[1] + (2 if dz > 0 else (-1 if dz < 0 else 0)))
                    cur = (sx, sz)
                    pose.append(cur)
                    tx, tz = r["to"]
                    while cur != (tx, tz):
                        cur = (cur[0] + (tx > cur[0]) - (tx < cur[0]), cur[1] + ((tz > cur[1]) - (tz < cur[1]) if cur[0] == tx else 0))
                        pose.append(cur)
                    if "hose_over_pump" in self.f and r.get("tag") == "A":
                        pose.append(r["pump"])
                hoses.append({"reel": list(pos), "laid": r["laid"], "nozzleTip": noz, "poseCells": [list(p) for p in pose],
                              "draw": {"reelArt": "Things/Hose/Reel_%s" % "NESW"[out]}})
            return {"success": True, "hoses": hoses}
        if verb == "lay":
            rx, rz, x, z = (int(v) for v in arg.split(","))
            r = self.reels.get((rx, rz))
            if r is None:
                return {"success": False, "error": "no hose reel at %d,%d" % (rx, rz)}
            if "reel_lay_refused" in self.f and r.get("tag") is None:     # the four facing reels only (S3's are tagged)
                return {"success": False, "reason": "mock: lay refused"}
            r.update(laid=True, to=(x, z))
            return {"success": True, "layOk": True}
        if verb == "filltank":
            c = tuple(int(v) for v in arg.split("=")[0].split(","))
            if c not in self.tanks:
                return {"success": False, "error": "no tank there"}
            self.tanks[c] = int(arg.split("=")[1].split(",")[1])
            return {"success": True}
        if verb == "tank":
            c = tuple(int(v) for v in arg.split(","))
            return {"success": True, "units": self.tanks[c]} if c in self.tanks else {"success": False, "error": "no tank there"}
        if verb == "pump":
            return {"success": True, "powered": "pump_unpowered" not in self.f, "lastMovedUnits": 0}
        if verb == "flick":
            self.pump_off = True
            return {"success": True}
        return {"success": False, "error": "unknown verb"}

    def _tick(self, n):
        # the thirsty colonist and the faucet
        for pid, p in self.pawns.items():
            if p.get("thirst", 1.0) < 0.3 and self.tanks:
                if "other_water" in self.f:
                    p["job"] = "RM_DrinkFromTerrain"
                elif "faucet_dry" not in self.f and self._in("RM_PipeFaucet", (-999, -999, 9999, 9999)):
                    p["job"] = "RM_DrinkFromFaucet"
                    tank = sorted(self.tanks)[0]
                    self.tanks[tank] -= DRINK_DL
                    p["thirst"] = min(1.0, p["thirst"] + 0.5)
                    if "faucet_rough" in self.f:
                        p["mem"].append("RM_Thought_DrankRough")
            else:
                p["job"] = "Wait_Wander"
        # the pump drawing the pond (one draw per 250-tick cycle)
        if n >= 250 and self.stock is not None and not self.pump_off and "pump_unpowered" not in self.f and self.pond_tank:
            take = min(self.stock, 0.25)
            if "pond_remainder" in self.f:
                take = min(take, max(0.0, self.stock - 0.05))
            if take > 0:
                self.stock = round(self.stock - take, 6)
                self.tanks[self.pond_tank] += int(round(take * UNITS_PER_LEVEL))

    def static(self, ty, m, arg):
        if ty == "Verse.Log":
            if m == "Warning" and "log_dead" not in self.f:
                self._log("Warning", arg)
            return "ok"
        if m == "ProofBuild":
            if "rail_nostuff" in self.f:
                for _ in range(6):
                    self._log("Error", "MakeThing error: RM_SuspensionRailing is madeFromStuff but stuff=null. Assigning default.")
            return "BUILD ok=True anchors=2 decks=6 blueprints=0 reason=none"
        if m == "ProofRails":
            if "rail_none" in self.f:
                return "RAILS on=True railed=0"
            x, z = (int(v) for v in arg.split(";")[0].split(","))
            for i in range(6):
                self._thing("RM_SuspensionRailing", (x - 1 + i, z), stuff=None if "rail_nostuff" in self.f else "WoodLog")
            return "RAILS on=True railed=6"
        if m == "ProofCanPlace":
            d, c = arg.split(";")
            c = tuple(int(v) for v in c.split(","))
            on_pipe = bool(self._at("RM_UniversalPipe", c))
            ok = on_pipe or "faucet_anywhere" in self.f
            return "PLACE ok=%s kind=none surface=SolidGround why=%s" % (ok, "" if ok else "Must_be_placed_on_a_universal_pipe.")
        if m == "ProofWaterLook":
            c = tuple(int(v) for v in arg.split(","))
            if c in self.dug:
                dep, fill = self.dug[c]
                wet = fill > 0 and "canal_dry" not in self.f
                ter = ("RM_WaterChestDeepStill" if "canal_two_defs" in self.f else "WaterDeep") if wet else "Soil"
                return "WATERLOOK cell=%d,%d terrain=%s still=True dug=True hollow=0 waterM=%s" % (c[0], c[1], ter, fill * 0.5 if wet else 0)
            return "WATERLOOK cell=%d,%d terrain=%s still=True dug=False hollow=0 waterM=3.0" % (c[0], c[1], self.terrain.get(c, "Soil"))
        if m == "ProofSetBodyFraction":
            x, z, frac = arg.split(";")
            self.stock = round(self.cap * float(frac), 6)
            return "SET #1 frac %s stock %.3f of %.1f" % (frac, self.stock, self.cap)
        if m == "ProofPondDepth":
            if self.stock is None:
                return "REFUSED: no formed pond at " + arg
            wet = "6" if (self.stock > 0 or "pond_wet_at_zero" in self.f) else "0"
            return "POND id=1 limitless=False stock=%.2f capacity=%.2f wet=%s census=mud:%s" % (self.stock, self.cap, wet, 6 - int(wet))
        return "REFUSED: unknown " + m

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            return {"success": True, "result": self.static(kw.get("type"), kw.get("method"), kw.get("args") or "")}
        if tool == "rimbridge/list_logs":
            after = int(kw.get("afterSequence") or 0)
            got = [x for x in self.logs if x["Sequence"] > after]
            return {"success": True, "logs": got[-int(kw.get("limit") or 1000):] if kw.get("limit") != 1 else self.logs[-1:]}
        if tool == "rimworld/step_game_ticks":
            n = int(kw.get("ticks") or 0)
            for _ in range(n // 250):
                self._tick(250)                  # one pump cycle per whole 250 ticks
            if n % 250 or n < 250:
                self._tick(n % 250 or n)
            return {"success": True}
        if tool == "jawa/mod_settings_field":
            key = (kw.get("typeName"), kw.get("field"))
            if kw.get("action") == "set":
                setattr(self, "set_%s" % kw.get("field"), kw.get("value"))
                return {"success": True}
            if key == (S_RIVER, "riverColorsEnabled"):
                return {"success": True, "value": "river_off" not in self.f}
            if key[1] in ("levelExactEnabled", "pipeFaucetsEnabled", "refillEnabled"):
                return {"success": True, "value": True}
            return {"success": True, "value": None}
        if tool == "jawa/world_commit":
            st = {"step": "WorldDrawLayer_Rivers.RegenerateNow", "status": "ok"}
            if "river_throws" in self.f:
                st = dict(st, status="failed", error="InvalidOperationException: Collection was modified")
                self._log("Error", "InvalidOperationException: Collection was modified; enumeration operation may not execute.")
            return {"success": True, "steps": [{"step": "WorldDrawLayer_Terrain.RegenerateNow", "status": "ok"}, st]}
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            d = self.dug.get(c, (0, 0))[0] + int(kw.get("deepenLevels") or 0)
            fill = int(kw.get("setFill", -1))
            self.dug[c] = (d, fill if fill >= 0 else self.dug.get(c, (0, 0))[1])
            return {"success": True, "depth": d, "fillSet": fill >= 0}
        if tool == "jawa/build_batch":
            for op in [o for o in str(kw.get("ops") or "").split(";") if o]:
                d, _, rest = op.partition(":")
                p = rest.split(",")
                c, rot = (int(p[0]), int(p[1])), (int(p[2]) if len(p) > 2 else 0)
                if d == "RM_HoseReel":
                    sx, sz = V.REEL_POS_SHIFT[rot % 4]
                    self.reels[c] = dict(rot=rot, corner=(c[0] - sx, c[1] - sz), laid=False, to=None, tag=None)
                    continue
                if d == "RM_LiquidTank":
                    self.tanks[c] = 0
                    if self.pond_pump is not None:
                        self.pond_tank = c
                if d == "RM_LiquidPump":
                    self.pond_pump = c
                    self.pond_tank = None
                    for r in self.reels.values():
                        r.setdefault("pump", c)
                style = None
                if d == "RM_PipeFaucet":
                    under = [self.things[t]["style"] for t in self._at("RM_UniversalPipe", c)]
                    style = (under[0] if under and "faucet_nomatch" not in self.f else None) or "RM_UniversalPipe_Scrapper"
                    style = style.replace("RM_UniversalPipe_", "RM_PipeFaucet_")
                self._thing(d, c, stuff=kw.get("stuff"), rot=rot, style=style)
            # S3: tag the two reels of the rig once the pump stands (A = the one north of the pump)
            pump = self.pond_pump
            if pump:
                for pos, r in self.reels.items():
                    if r["tag"] is None and abs(r["corner"][0] - pump[0]) <= 1 and abs(r["corner"][1] - pump[1]) <= 3:
                        r["tag"] = "A" if r["corner"][1] > pump[1] else "B"
                        r["pump"] = pump
            return {"success": True}
        if tool == "jawa/list_things":
            x, z, w, h = (int(v) for v in str(kw.get("rect")).split(","))
            return {"success": True, "things": [dict(id=t, defName=self.things[t]["defName"], stuff=self.things[t]["stuff"])
                                                for t in self._in(kw.get("defName"), (x, z, w, h))]}
        if tool == "jawa/set_thing_props":
            t = self.things.get(kw.get("thing"))
            if t is None or "pipe_style_refused" in self.f:
                return {"success": False, "error": "mock: style refused"}
            t["style"] = kw.get("style")
            return {"success": True}
        if tool == "jawa/thing_graphic":
            x, z, w, h = (int(v) for v in str(kw.get("rect")).split(","))
            out = []
            for t in self._in(kw.get("defs"), (x, z, w, h)):
                v = self.things[t]
                look = (v["style"] or "_Scrapper").split("_")[-1]
                if v["defName"] == "RM_UniversalPipe":
                    path = "RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas" % look
                    chain = ["Graphic_Linked", "Graphic_Single"]
                elif v["defName"] == "RM_PipeFaucet":
                    path = "RimMandrake/FlowWorks/Faucet/%s/RM_PipeFaucet" % look
                    chain = ["Graphic_Single"]
                elif v["defName"] == "RM_PitGuardrail":
                    fence = "rail_fence_art" in self.f
                    path = "Things/Building/Linked/Fence/Fence_Atlas" if fence else "RimMandrake/FlowWorks/Guardrail"
                    chain = ["Graphic_LinkedAsymmetric", "Graphic_Single" if fence else "Graphic_Appearances"]
                else:
                    path, chain = "Things/x", ["Graphic_Single"]
                out.append(dict(id=t, graphicPath=path, graphicChain=chain, badTex=False))
            return {"success": True, "things": out}
        if tool == "rimworld/list_architect_categories":
            cats = [{"id": "architect-category:structure", "label": "Structure"}]
            if "no_pipenet_tab" not in self.f:
                cats.append({"id": "architect-category:vche_pipenetworks", "label": "Pipe networks"})
            return {"success": True, "categories": cats}
        if tool == "rimworld/list_architect_designators":
            ds = [{"id": "architect-designator:pipes:build-vche-chemfuelpipe", "label": "chemfuel pipe"}]
            if "faucet_untabbed" not in self.f:
                ds.append({"id": "architect-designator:pipes:build-rm-pipefaucet", "label": "pipe faucet"})
            return {"success": True, "designators": ds, "page": {"nextOffset": None}}
        if tool == "jawa/spawn_pawn":
            self.nid += 1
            pid = "Thing_Human%d" % self.nid
            self.pawns[pid] = dict(thirst=1.0, job="Wait_Wander", mem=[])
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/pawn_need":
            p = self.pawns.get(kw.get("pawn"))
            if p is None:
                return {"success": False, "error": "no pawn"}
            if kw.get("action") == "need" and kw.get("need") == "RM_Thirst":
                p["thirst"] = float(kw.get("level"))
            return {"success": True, "needs": [{"need": "RM_Thirst", "level": p["thirst"]}], "memories": [{"def": m} for m in p["mem"]]}
        if tool == "rimworld/list_colonists":
            return {"success": True, "colonists": [{"pawnId": pid, "job": p["job"], "dead": False} for pid, p in self.pawns.items()]}
        if tool == "jawa/flowworks_body_report":
            if self.stock is None and kw.get("classify") and any(v == "WaterShallow" for v in self.terrain.values()):
                return {"success": True, "body": {"id": 1, "limitless": False, "stock": self.cap, "capacity": self.cap, "cellCount": 6}}
            if self.stock is not None:
                if self.stock <= 0 and "pond_wet_at_zero" not in self.f:
                    return {"success": True, "body": None}
                return {"success": True, "body": {"id": 1, "limitless": False, "stock": self.stock, "capacity": self.cap, "cellCount": 6}}
            return {"success": True, "body": None}
        if tool == "jawa/set_terrain_batch":
            ter, rect = str(kw.get("ops")).split(":")
            x, z, w, h = (int(v) for v in rect.split(","))
            for i in range(w):
                for j in range(h):
                    self.terrain[(x + i, z + j)] = ter
            return {"success": True}
        if tool == "rimworld/get_cell_info":
            c = (kw["x"], kw["z"])
            ter = self.terrain.get(c, "Soil")
            if self.stock is not None and self.stock * UNITS_PER_LEVEL <= 0.5 and ter == "WaterShallow" and "pond_wet_at_zero" not in self.f:
                ter = "Mud"
            return {"success": True, "cell": {"terrainDefName": ter}}
        # settings dialog
        if tool == "rimworld/list_mod_settings_surfaces":
            return {"success": True, "surfaces": [{"modId": "mod-settings:%s:abc" % MOD_ID, "handleTypeName": "RimMandrakeFlowWorksMod"}]}
        if tool == "rimworld/open_mod_settings":
            self.dialog = "no_dialog" not in self.f
            return {"success": self.dialog}
        if tool == "rimworld/get_ui_layout":
            if not self.dialog:
                return {"success": True, "surfaces": []}
            q = self.query.lower()
            show = (not q or "search_unfiltered" in self.f
                    or (q in SEARCH_LABEL.lower() and not (q == "pieces" and "search_misses" in self.f)))
            els = [{"kind": "text_field", "targetId": "box", "screenRect": {"width": 420}, "text": self.query},
                   {"kind": "text_field", "targetId": "wide", "screenRect": {"width": 840}}]
            if show:
                els.append({"kind": "checkbox", "label": SEARCH_LABEL})
            return {"success": True, "surfaces": [{"type": "RimWorld.Dialog_ModSettings", "elements": els}]}
        if tool == "rimworld/set_text_field":
            if kw.get("targetId") == "box":
                self.query = kw.get("text") or ""
            return {"success": True}
        if tool == "jawa/window_list_close":
            self.dialog = False
            return {"success": True}
        return {"success": True}


if __name__ == "__main__":
    sys.exit(main())
