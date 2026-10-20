"""live_session.py -- ONE cold load of the `flowworks` tier, ONE map, ONE driver run that discharges every owed FlowWorks
live row it can, in the cheapest order. Plan and per-row table: design/RimMandrake/flowworks_live_session_plan_2026-10-18.md.

Owner, 2026-10-18: *"Anything else we can work on now to get FlowWorks ready to review when it's our turn? Best to do it
all at once."* and *"Perhaps there are some validation scripts to review to see if we can compress them to test the same
material in a tighter timeline?"*

  python3    src/RimMandrake/FlowWorks/northstar/live_session.py --dry-run           # the plan + time budget, no bridge
  python3    src/RimMandrake/FlowWorks/northstar/live_session.py --mock              # every path offline (FakeGame)
  python.exe src/RimMandrake/FlowWorks/northstar/live_session.py                     # LIVE: bridge held, flowworks tier,
                                                                                     # a fresh Playing quicktest map
  options: --only B1,B2 (blocks, a PARTIAL run: never recordable) --skip B9 --frame-budget-ms 150 --out-dir DIR
           --no-owner-save --list (catalog only). A crashed block is always recorded and the run goes on (no flag).
  Wrap the live run for the keeper-saves check:
  python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe <this script>

ORDER (cheapest first; every map-global side effect is placed AFTER the rows it would spoil):
  B0  preflight         tier truth (jawa/running_mods count + FlowWorks assembly sha), log_revive + tap, calm, clock rate
  B1  validation_v2     subprocess, --live --current-map: it destroy_bulks every non-colonist and paints its plots over
                        the whole map, so it runs FIRST, before any pawn of ours exists
  B2  zero-tick reads   settings dialog labels (5 items' A1 "dialog not rendered"), tall-tank capacity, readout strings
  B3  serial scripts    trench_cover_proof, climb_proof, sprinkler_live, liquid_checks, proof_hose (each clears its own
                        site, reads it, and is done before the next starts, so they may reuse ground)
  B4  shared clock      native blocks on DISJOINT zones staged together, then ONE clock serves them all: the scheduler
                        advances to the earliest checkpoint any block waits on (cover tiers, pit access A1-A4, dug
                        reservoir fish roll, dig-rate, dehydration riding the session clock)
  B5  cold snap         ice on dug water: ColdSnap + DeepFreeze, judged only below -7 C (map-wide temperature: after B4)
  B6  flood             torrential-rain flood seeded at the canal itself (map-wide: after B5)
  B7  save + reload     ONE save, ONE load; pockets, depths, readouts, pipe look, settings re-read == before
  B8  raid              raid_trench_proof (hostiles roam: after every quiet row; serves P2 raid, trench A3, raiders trench)
  B9  owner review      owner_review_stage.main (ladders, spikes, gates, shallows, sprinklers, hoses) + the pit-access
                        in-situ props; kill hostiles; ONE named save for the owner
  B10 thirst tail       thirst_live: it paints EVERY potable water cell on the map to Soil, so it runs LAST, after the
                        owner's save (its docstring: never save the map afterwards)

Every row: {id, item, criterion, status PASS|FAIL|UNMEASURED|SKIP, class MOD|SITE|HARNESS|OWED, detail, block, eyes}.
"Could not ask" is UNMEASURED, never PASS. A row the scheduler could not run (block crashed, precondition never held)
is UNMEASURED/HARNESS with the reason. Ledger-ready lines for PASS/FAIL criteria are written to verify_lines.txt; they
are NOT run (a human or the driving agent runs them after reading the evidence).

ANTI-GUESSING NOTES
- Every bridge tool named here is in src/RimMandrake/bridgetools (jawa/*) or already used by a committed script
  (rimworld/*); every defName was read from FlowWorks Defs or the vanilla def index (RimSage), never guessed.
- jawa/order_pawn(waitTicks=N) advances the clock INSIDE the call; B4 orders with waitTicks=1 and lets the shared clock
  move, so one advance serves every block (the old scripts spent 900 ticks per order, serially).
- A long property is compressed or decomposed and INFERRED (debug_process.md "Long-duration properties"): T6's
  60,000-tick dehydration rides the session clock and is extrapolated from the measured rate; DIG_COST reads the job's
  work total, never a 26-digger-day dig.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
MOD_ID = "mandrake.rm.flowworks"
NOTCH_M = 0.5
TPS_STEP = 60.0            # MEASURED: step_game_ticks ~60 ticks/s (bench_live_20261012/SITTING.md, 595 ticks in 10.1 s)
CALL_S = 0.15              # ESTIMATED wall seconds per bridge call (v2: ~1,000 calls in 209-310 s with 14k ticks)
MAP_DEFAULT = (250, 250)

# ============================================================================ the catalog (pure data)
# One entry per owed ledger criterion. block = who discharges it; source = the existing script/function reused;
# ticks / wall = ESTIMATED cost inside THIS session (M: = MEASURED from a run log, quoted in the plan doc);
# eyes = the owner must look (L4 or an in-situ judgement) -- the run stages it and saves it, it never judges it.
C = []


def crit(item, cid, block, source, ticks, wall, eyes=False, note=""):
    C.append(dict(item=item, crit=cid, block=block, source=source, ticks=ticks, wall=wall, eyes=eyes, note=note))


# B1 validation_v2 (M: 209-310 s, 61 rows, ~14,000 ticks)
crit("VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG", "live", "B1", "validation_v2.run_live --current-map", 14000, 280,
     note="M: 61/0/0 twice on DLL 6699957b8; reconcile = one more green run on THIS DLL + the written triage")
crit("FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1", "run", "B1", "validation_v2 + modcheck record", 0, 0, eyes=True,
     note="needs the v2 JSON recorded and his sheet review (record_owner_review)")
# B2 zero-tick
for item, cid in (("FALL_DAMAGE_BUILD_DEEP_DROPS_KILL", "A1"), ("PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER", "A1"),
                  ("PIT_ALERT_BUILD_RED_MEANS_HELP", "A1"), ("BEACH_RING_RETIRE_DRAINED_MEANS_DRY", "A1"),
                  ("FALL_GUARDRAILS_BUILD_REAL_OBJECT", "A2")):
    crit(item, cid, "B2", "native settings_dialog (LuminousPigment/validation.py open_mod_settings pattern)", 0, 6,
         note="every earlier verify was partial for ONE reason: 'dialog not rendered'; one dialog open serves five")
crit("LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD", "A2", "B2", "native settings_dialog + readout_strings", 0, 4, eyes=True)
crit("DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE", "A2", "B2", "native readout_strings (Walk.readout)", 2, 8, eyes=True)
crit("TANK_TALL_BUILD_TWICE_THE_DRINK", "live", "B2", "native tank_tall (ProofTank)", 2, 6)
# B3 serial scripts
crit("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A2", "B3", "trench_cover_proof.py --origin", 140, 40)
crit("PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP", "A1", "B3", "climb_proof.py --origin", 6600, 330,
     note="E: climb_proof spends 900 ticks inside each of 3 order_pawn calls + up to 3600 in the ramped-floor haul (G)")
crit("PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "pocket+mask", "B3", "climb_proof.py", 0, 0)
crit("SPRINKLER_HEADS_BUILD_PUMP_REQUIRED", "spray", "B3", "sprinkler_live.py --origin", 2600, 60,
     note="M: 59 s, 9 rows; T22 is the SALT_BOTTLE regression row")
crit("SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING", "T22", "B3", "sprinkler_live.py brine + thirst_live T5 (B10)", 0, 0)
crit("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A3", "B3", "liquid_checks.py --only L2,L4,L5,L6", 4000, 300)
crit("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A5", "B3", "liquid_checks.py L4", 0, 0)
crit("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A6", "B3", "liquid_checks.py L5", 0, 0)
crit("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A7", "B3", "liquid_checks.py L6 (goodwill/day INFERRED, --theft-day off)", 0, 0,
     note="a day is 60,000 ticks (~17 min at 60 t/s): the per-check charge is read, the daily total inferred")
crit("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A4", "B3", "NO SCRIPT ROW (NS_intake_needs_pump has no live driver)", 0, 0,
     note="UNMEASURED until a row exists; proof_hose realflow is the nearest block")
crit("HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A5", "B3", "proof_hose.py --only realflow,save_load", 3000, 300,
     note="M: proof_hose full 526-685 s; realflow ~147 s; A5 = LIQUID_LEDGER A2-A8")
# B4 shared clock
crit("SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT", "A3", "B4", "native cover_tiers (ProofCover, pawn_stats Mass)", 400, 40)
for cid, t in (("A1", 1500), ("A2", 1500), ("A3", 300), ("A4", 6000)):
    crit("PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", cid, "B4", "native pit_access (ProofClimb pawn:<id>)", t, 30)
crit("PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT", "A2", "B4", "native dig_depth (drive to 8 m, ProofReadout, job probe)", 10, 8)
crit("DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT", "A2", "B4", "native dig_depth (RM_DigDepthMath.WorkToCut live + job_probe)", 0, 4,
     note="the bar's 'progress-bar time' is read as the job's work total + one rate sample: INFERRED, never a full dig")
crit("THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY", "T6", "B4", "native dehydration_ride (rides the whole session clock)", 0, 4,
     note="thirst_live T6 holds need 0 for 60,000 ticks serially (E ~16 min); here it rides every other block's ticks")
crit("FISH_ROLL_MEND_PONDS_BORN_BARREN", "A2", "B4", "native dug_reservoir (jawa/fishing water-body fish roll)", 500, 15)
crit("POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A7", "B4", "native dug_reservoir (map_zones fishing + jawa/fishing + ordered_job Fish)",
     8500, 140, note="E: one vanilla Fish job, 7500/FishingSpeed ticks; the longest B4 wait. Needs the companion with jawa/fishing")
crit("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A4", "B4", "native grenade (explosion_at Bomb, pawn_get hediffs)", 10, 10)
crit("FALL_GUARDRAILS_BUILD_REAL_OBJECT", "A3", "B4", "native rail_lip (records: AI never steps off an unrailed lip)", 900, 15,
     note="day 6: the unrailed CONTROL never fell either; the row records it again and the plan asks for the bar's ruling")
# B5 / B6
crit("POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A5", "B5", "native cold_snap (game_condition ColdSnap + DeepFreeze, sub -7 C gate)", 30000, 600)
crit("POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A6", "B6", "native flood (weather_set TorrentialRain: the flood seeds at the canal)", 12000, 220)
# B7
crit("PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT", "A3", "B7", "native reload (snapshot before/after one save+load)", 0, 40)
crit("PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP", "A2", "B7", "native reload (ProofPocket before/after)", 0, 0)
crit("PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "save_reload_pockets_identical", "B7", "native reload", 0, 0)
crit("HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A2", "B7", "native reload (pipe look before/after; objects_sheet.choose_look)", 0, 0,
     note="the blueprint->frame->building half needs a colonist build: staged as a blueprint in B4, read in B7")
# B8
crit("PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "raid", "B8", "raid_trench_proof.main", 15000, 360,
     note="E: 5-8 min; 60 chunks of 250 ticks; one raid also feeds TRENCH A3 and RAIDERS_TRENCH observation")
crit("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A3", "B8", "raid_trench_proof (cast squares read from the raid)", 0, 0,
     note="needs a 1 m canal line facing the raid: the raid site digs it (raid_trench_proof scene) -> partial until a row reads cast cells")
crit("RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP", "live", "B8", "raid_trench_proof (once built)", 0, 0, note="item is doing: rows once built")
# B9 owner review (his eyes)
crit("FLOWWORKS_LADDER_RAISE_LOWER_1", "A2", "B9", "owner_review_stage ladders", 50, 40, eyes=True)
crit("PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A5", "B9", "native in-situ props + owner_review_stage", 0, 10, eyes=True)
crit("POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A8", "B9", "owner_review_stage shallows (thin water in situ)", 1750, 40, eyes=True)
crit("SPRINKLER_HEADS_BUILD_PUMP_REQUIRED", "looks", "B9", "owner_review_stage sprinklers (four nozzle looks spraying)", 2800, 60, eyes=True)
crit("HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME", "walk", "B9", "owner_review_stage --only hoses (sibling's row)", 700, 90, eyes=True)
crit("HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A4", "B9", "owner judges the four pipe atlases (hoses row shots)", 0, 0, eyes=True)
crit("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A9", "B9", "spill art + 'Fitting:' relabel in the owner save", 0, 0, eyes=True)
crit("PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT", "A4", "B9", "deep wall faces / sink / tint past 2 m in the owner save", 0, 0, eyes=True)
crit("LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP", "A2", "B9", "lake_floor_stage.py savegame (mountainous map: NOT this map)", 0, 0, eyes=True,
     note="needs a mountainous-biome map: a second quicktest in the same load (~8 s) or the staged save")
crit("WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES", "A2", "P10", "water_scenes_walk go S5/S6 + level_surface_bar (the epic's P10 walk)", 9000, 330,
     note="M: S5 229 s; the epic's P10 integration walk owns it (FOUNDRY); same load, run after B9 if P10 is ready")
# B10 thirst tail
crit("THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY", "T1-T5,T7,T9,T10", "B10", "thirst_live.py --only T7,T1,T2,T3,T4,T5,T10,T9", 9000, 420,
     note="M: full thirst_live 807-855 s; T6 moved to B4; T1/T7 need --log (this load's Player.log copy)")
crit("THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL", "T15,T16,T27", "OUT", "thirst_live.py --only T15,T16,T27 (needs mandrake.rm.biomes)", 4000, 200,
     note="SITE, 2026-10-18: the meltwater can, RM_Slime_Liquid and the red/green/white hediffs are mandrake.rm.biomes content; "
          "the flowworks tier reads them UNMEASURED SITE. One run on a list with Biomes after this session")
crit("SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING", "T5", "B10", "thirst_live.py T5", 0, 0)
# not on this load
crit("CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS", "A1", "OUT", "prove_contagion_burn.py (Contagion is not in the flowworks tier)", 0, 0,
     note="separate tier: one modlist swap (~70 s launch, M) after this session")
crit("CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME", "burn_forced", "OUT", "Contagion tier", 0, 0)
for item in ("SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS", "SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD",
             "SUSPENSION_JETTY_BUILD_WALK_THE_PLANK", "SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP",
             "SUSPENSION_WATERS_BUILD_MAY_BACKTRACK", "WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS"):
    crit(item, "L2 rows", "LATER", "RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved)", 0, 0,
         note="not built yet: a B4 zone is reserved; the block registers itself when the item reaches built")

# ============================================================================ blocks
BLOCKS = []      # (id, title, kind, phase order)


def block(bid, title, kind):
    BLOCKS.append(dict(id=bid, title=title, kind=kind))


block("B0", "preflight: tier truth, log revive, calm, clock rate", "native")
block("B1", "validation_v2 --live --current-map", "sub")
block("B2", "zero-tick reads: settings dialog, tall tank, readout strings", "native")
block("B3", "serial scripts: trench cover, climb, sprinklers, liquid checks, hose realflow", "sub")
block("B4", "shared clock: covers, pit access, dig depth, reservoir, grenade, rail lip, dehydration ride", "native")
block("B5", "cold snap: ice on dug water", "native")
block("B6", "torrential flood over a wet canal", "native")
block("B7", "one save + one load: snapshot rows", "native")
block("B8", "raid against a sheer trench", "sub")
block("B9", "owner review staging + ONE save", "stage")
block("B10", "thirst tail (paints all water to Soil: last)", "sub")

# serial subprocess steps: (block, script, argv template, out flag style, row->criterion map)
#   {origin} is filled from the zone allocator; {out} the result path; {log} this load's Player.log copy.
SUBS = [
    ("B1", "validation_v2.py", ["--live", "--current-map", "--out", "{out}"], {"*": ("VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG", "live")}),
    ("B3", "trench_cover_proof.py", ["{out}", "--origin", "{origin:trench}"],
     {"TRENCH_square_on": ("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A2"), "TRENCH_enfilade": ("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A2"),
      "TRENCH_wet": ("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A2"), "TRENCH_lip": ("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A2"),
      "TRENCH_one_back": ("TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A2")}),
    ("B3", "climb_proof.py", ["{out}", "--origin", "{origin:climb}"], {"*": ("PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP", "A1")}),
    ("B3", "sprinkler_live.py", ["{out}", "--origin", "{origin:sprinkler}"],
     {"T22": ("SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING", "T22"), "*": ("SPRINKLER_HEADS_BUILD_PUMP_REQUIRED", "spray")}),
    ("B3", "liquid_checks.py", ["{out}", "--only", "L2,L4,L5,L6", "--origin-l2", "{origin:l2}", "--origin-l2b", "{origin:l2b}",
                                "--origin-l6", "{origin:l6}", "--origin-l4", "{origin:l4}", "--origin-l5", "{origin:l5}"],
     {"L2": ("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A3"), "L4": ("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A5"),
      "L5": ("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A6"), "L6": ("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A7")}),
    ("B3", "proof_hose.py", ["--live", "--no-fresh-map", "--skip-offline", "--only", "realflow,save_load", "--out", "{out}"],
     {"NS_": ("HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A5"), "SL": ("HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A5")}),
    ("B8", "raid_trench_proof.py", ["{out}"], {"*": ("PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "raid")}),
    ("B10", "thirst_live.py", ["{out}", "--only", "T7,T1,T2,T3,T4,T5,T10,T9", "--site", "{origin:thirst}", "--log", "{log}"],
     {"T5": ("SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING", "T5"),
      "*": ("THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY", "T1-T5,T7,T9,T10")}),
]

# ============================================================================ zones (pure)
# Footprints (w, h) of each staged site, read from the scripts' own docstrings/geometry. Serial (B3/B8/B10) sites may
# overlap each other (each clears and finishes before the next); B4 zones must be disjoint from each other AND from the
# owner zone, which must stand until the B9 save.
FOOT = dict(trench=(30, 16), climb=(46, 12), sprinkler=(16, 86), l2=(30, 18), l2b=(30, 18), l6=(30, 18), l4=(30, 18),
            l5=(30, 18), thirst=(96, 42),
            covers=(26, 10), access=(40, 14), digdepth=(12, 8), reservoir=(16, 26), grenade=(20, 10), raillip=(16, 14),
            ride=(6, 6), tanks=(12, 6), readout=(22, 16), ice=(16, 8), flood=(18, 10), suspension=(40, 16),
            owner=(216, 78), props=(30, 10))
GAP = 6
SHARED = ("covers", "access", "digdepth", "reservoir", "grenade", "raillip", "ride", "tanks", "readout", "ice", "flood",
          "suspension", "props")


def shelf_pack(names, region, gap=GAP):
    """Pack footprints left-to-right, row by row, inside region (x, z, w, h). Returns {name: (x, z, w, h)}; raises when
    something does not fit (a run never starts with overlapping zones)."""
    rx, rz, rw, rh = region
    x, z, row_h, out = rx, rz, 0, {}
    for n in names:
        w, h = FOOT[n]
        if x + w > rx + rw:
            x, z, row_h = rx, z + row_h + gap, 0
        if w > rw or z + h > rz + rh:
            raise ValueError("zone %s (%dx%d) does not fit region %s" % (n, w, h, region))
        out[n] = (x, z, w, h)
        x += w + gap
        row_h = max(row_h, h)
    return out


def overlaps(a, b, gap=0):
    ax, az, aw, ah = a
    bx, bz, bw, bh = b
    return not (ax + aw + gap <= bx or bx + bw + gap <= ax or az + ah + gap <= bz or bz + bh + gap <= az)


def plan_zones(size=MAP_DEFAULT):
    """Owner zone across the north band, shared-clock zones packed in the south band, serial sites re-use the south band
    (they run BEFORE B4 stages). 15-cell edge margin (site_spec.EDGE_LIMITED)."""
    W, H = size
    m = 15
    zones = {"owner": (m + 3, H - m - FOOT["owner"][1], FOOT["owner"][0], FOOT["owner"][1])}
    south = (m, m, W - 2 * m, H - 2 * m - FOOT["owner"][1] - GAP)
    zones.update(shelf_pack(SHARED, south))
    # B2_readout_sea_never_dry: the readout zone's painted lake must TOUCH the map edge to be limitless (every map-edge
    # body is limitless by wetness since 392300ef0d, RM_StockMath.IsLimitlessByWetness), so the zone sits flush with the
    # east edge, south band (its packed slot is left empty, so nothing else moves). The owner zone (216 wide, north band)
    # and every other shared zone stay >= 2 cells away: checked below.
    zones["readout"] = (W - FOOT["readout"][0], m, FOOT["readout"][0], FOOT["readout"][1])
    serial = shelf_pack(("trench", "climb", "sprinkler", "l2", "l2b", "l6", "l4", "l5"), south)
    zones.update(serial)
    zones["thirst"] = (m, m, FOOT["thirst"][0], FOOT["thirst"][1])
    shared = [zones[n] for n in SHARED]
    for i, a in enumerate(shared):
        for b in shared[i + 1:]:
            if overlaps(a, b, gap=2):
                raise ValueError("shared zones overlap: %s %s" % (a, b))
        if overlaps(a, zones["owner"], gap=2):
            raise ValueError("shared zone %s overlaps the owner zone" % (a,))
    return zones


# ============================================================================ the shared-clock scheduler (pure)
class Wait(object):
    """A block yields Wait(ticks) to be resumed after `ticks` more game ticks, or Wait(ticks, until=fn, every=n) to be
    resumed as soon as fn() is true (polled every n ticks) or when ticks run out (then .timed_out is set)."""

    def __init__(self, ticks, until=None, every=60):
        self.ticks, self.until, self.every, self.timed_out = int(ticks), until, max(1, int(every)), False


def run_shared(gens, advance, now, log=print):
    """Run generator-blocks concurrently against ONE clock. gens: {name: generator}. advance(n) moves the game n ticks;
    now() reads the game tick. Every block's wait is honoured; the clock only ever moves by the smallest step any live
    block needs, so N blocks waiting 1,500 ticks cost 1,500 ticks, not N x 1,500. Returns {name: 'done'|'crashed: ..'}
    and the ticks spent."""
    live, due, out = {}, {}, {}
    t0 = now()

    def resume(name, g, t):
        try:
            w = next(g)
        except StopIteration:
            out[name] = "done"
            return
        except Exception as ex:  # noqa: BLE001 - one block's crash never stops the others
            out[name] = "crashed: %s" % ex
            log("  BLOCK %s CRASHED:\n%s" % (name, traceback.format_exc()))
            return
        if not isinstance(w, Wait):
            w = Wait(int(w or 0))
        live[name] = (g, w)
        due[name] = (t + w.ticks, t + (w.every if w.until else w.ticks))

    for name, g in gens.items():
        resume(name, g, now())
    while live:
        t = now()
        ready = []
        for name, (g, w) in list(live.items()):
            end, poll = due[name]
            if w.until is not None and t >= poll:
                try:
                    ok = bool(w.until())
                except Exception:  # noqa: BLE001
                    ok = False
                if ok:
                    ready.append(name)
                    continue
                due[name] = (end, t + w.every)
            if t >= end:
                if w.until is not None:
                    w.timed_out = True
                ready.append(name)
        for name in ready:
            g, _w = live.pop(name)
            resume(name, g, t)
        if not live:
            break
        if ready:
            continue
        # only LIVE blocks set the step: a finished block's stale deadline left in `due` made every later step 1 tick
        # (live 2026-10-19: B4 crawled at ~4 ticks/s for 20 min)
        step = max(1, min(min(due[n]) for n in live) - t)
        step = min(step, 2500)
        advance(step)
        if now() <= t:              # the clock did not move: a 0-tick step (live day 4) voids every waiting block
            for name in list(live):
                out[name] = "clock stalled at tick %s" % t
                live.pop(name)
            break
    return out, now() - t0


# ============================================================================ session context
class Session(object):
    def __init__(self, args, out_dir):
        self.args, self.out_dir = args, out_dir
        self.rows, self.notes, self.timing = [], [], {}
        self.mock, self.dry = args.mock, args.dry_run
        self.w = None
        self.size = MAP_DEFAULT
        self.zones = plan_zones(self.size)
        self.env = {}
        self.snap_before = {}
        self.pawns = {}
        self.ride_stop = False
        self.site_bad = {}          # zone -> [why]: a site that did not read back clear, or a dig that missed its depth

    # ---- output
    def say(self, s):
        print(s, flush=True)

    def row(self, rid, item, cid, status, cls, detail, block, eyes=False):
        zone = zone_of_row(rid)
        if zone and self.site_bad.get(zone) and status in ("PASS", "FAIL"):
            # a verdict read on a site that never read back clear (or was dug to the wrong depth) is no verdict
            detail = dict(detail, statusIfSiteReady=status, siteNotReady=self.site_bad[zone][:6])
            status, cls = "UNMEASURED", "SITE"
        r = dict(id=rid, item=item, criterion=cid, status=status, cls=cls, detail=detail, block=block, eyes=eyes)
        self.rows.append(r)
        self.say("  %-34s %-10s %-7s %s %s" % (rid, status, cls, "%s %s" % (item[:34], cid), json.dumps(detail, default=str)[:160]))
        self.save()
        return r

    def save(self):
        p = os.path.join(self.out_dir, "session.json")
        with open(p + ".tmp", "w", encoding="utf-8") as f:
            json.dump(dict(script="live_session.py", mode="mock" if self.mock else "live", env=self.env, zones=self.zones,
                           timing=self.timing, rows=self.rows, notes=self.notes, args=vars(self.args)), f, indent=1, default=str)
        os.replace(p + ".tmp", p)

    # ---- bridge
    def call(self, tool, **kw):
        if self.w is None:
            return {}
        try:
            return self.w.call(tool, **kw) or {}
        except Exception as ex:  # noqa: BLE001 - a failed call is an UNMEASURED reading, never a crash of the session
            return {"success": False, "error": "call raised: %s" % ex}

    def proof(self, typ, method, arg):
        r = self.call("jawa/static_call", type=typ, method=method, args=arg)
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return r.get("success") is True and not txt.startswith("REFUSED"), txt

    def now(self):
        if self.w is None:
            return 0
        if self.mock:
            return getattr(self.w.B, "tick", 0)
        return int((self.call("jawa/flowworks_engine_state") or {}).get("ticksGame") or 0)

    def advance(self, n):
        """Game ticks through jawa/safe_advance with a raised frame budget (default 40 ms -> --frame-budget-ms), the
        vitals latch kept; Walk.ticks (feeds colonists, resumes one GovernorStop) on mock or when safe_advance refuses."""
        if self.w is None:
            return
        if self.mock or not self.args.frame_budget_ms:
            self.w.ticks(n)
            return
        # keep the colony fed across long shared clocks (a Starving colonist stops every governed advance)
        self._since_feed = getattr(self, "_since_feed", 0) + int(n)
        if self._since_feed >= 2500:
            self._since_feed = 0
            feed_colonists(self)
        r = self.call("jawa/safe_advance", action="start", ticks=int(n), frameBudgetMs=float(self.args.frame_budget_ms),
                      timeoutMs=max(60000, int(n) * 100))
        rem = advance_remainder(r, n)
        if rem and r.get("state") == "running":     # still stepping after timeoutMs: stop it before stepping ourselves
            self.call("jawa/safe_advance", action="cancel")
            st = (self.call("jawa/safe_advance", action="status") or {}).get("advance") or {}
            rem = advance_remainder(dict(st, success=False), n)
        if rem > 0:
            # a stopped (latch) or refused advance stepped `executed` of n: only the REST goes through Walk.ticks (the
            # old fallback re-advanced all n on top of a partial run)
            self.w.ticks(rem)

    def spawn(self, kind, c, faction="player"):
        r = self.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1)
        return ((r.get("pawns") or [{}])[0]).get("id")

    def dig(self, c, n, fill=-1):
        """One excavation_drive; the reply is READ: a refused drive or a depth other than n (every staged cell starts at 0
        after clear_zone's ProofResetRect) marks the zone holding c not ready, so its rows read UNMEASURED/SITE."""
        r = self.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill)
        bad = dig_miss(r, n) if not self.mock else None
        if not bad and fill >= 0 and not self.mock and r.get("fillSet") is False:     # dry where the row needs water
            bad = "fill %s not set (fillSet false)" % fill
        if bad:
            z = zone_at(self.zones, c)
            if z:
                self.site_bad.setdefault(z, []).append("dig %d,%d: %s" % (c[0], c[1], bad))
        return r

    def pit(self, sw, w, h, notches, fill=-1):
        for i in range(w):
            for j in range(h):
                self.dig((sw[0] + i, sw[1] + j), notches, fill)

    def climb(self, pid):
        """ProofClimb pawn:<id> -> dict(cell, depth, held, trapped) or {} (unread). depth is the CELL's dug depth
        (ProofPocket -> ClimbDepthAt), deck-blind: a pawn on an intact cover over a 2 m cell reads 4."""
        ok, txt = self.proof(NSP, "ProofClimb", "pawn:%s" % pid)
        kv = kvparse(txt) if ok else {}
        if "cell" not in kv:
            return {}
        try:
            x, z = (int(v) for v in kv["cell"].split(","))
        except ValueError:
            return {}
        return dict(cell=(x, z), depth=fnum(kv.get("depth")), held=kv.get("held"), trapped=kv.get("trapped"), raw=txt[:200])

    def order(self, pid, c):
        return self.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=1, draft=True, unpause=False)

    def sget(self, f):
        return self.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(self, f, v):
        return self.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))


def kvparse(txt):
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


# row id prefix -> the zone its verdict was read on (Session.row demotes a verdict on a zone that is not ready)
ROW_ZONE = (("B2_tank", "tanks"), ("B2_readout", "readout"), ("B4_cover", "covers"), ("B4_access", "access"),
            ("B4_dig", "digdepth"), ("B4_reservoir", "reservoir"), ("B4_grenade", "grenade"), ("B4_rail", "raillip"),
            ("B4_dehydration", "ride"), ("B5_", "ice"), ("B6_", "flood"), ("B9_props", "props"))


def zone_of_row(rid):
    return next((z for p, z in ROW_ZONE if str(rid).startswith(p)), None)


def zone_at(zones, c):
    """The staged zone holding cell c (shared and event zones only: the serial sites are their scripts' own)."""
    for n in SHARED + ("tanks",):
        if n in zones:
            x, z, w, h = zones[n]
            if x <= c[0] < x + w and z <= c[1] < z + h:
                return n
    return None


def dig_miss(r, n):
    """None when an excavation_drive reply says the cell is at depth n; else why not (refused, or another depth: a cell
    that was not reset, or the dig ceiling / max-dig setting clamped it). A reply with no depth field is not judged."""
    if not isinstance(r, dict) or r.get("success") is not True:
        return "drive refused: %s" % str((r or {}).get("error") or (r or {}).get("message") or r)[:100]
    if n and "depth" in r and fnum(r.get("depth")) != float(n):
        return "depth %s after the drive, wanted %d" % (r.get("depth"), n)
    return None


def order_taken(s, r, pid):
    """True when jawa/order_pawn says the pawn accepted the order (its row's orderAccepted); mock has no such rows. A
    refused order leaves the pawn where it stood, which a row must not read as 'could not climb out'."""
    if s.mock:
        return True
    for p in (r or {}).get("pawns") or []:
        if p.get("id") == pid:
            return p.get("orderAccepted") is True
    return False


def draft(s, pid):
    """Draft pid and READ IT BACK. jawa/set_draft with no `drafted` changes nothing (JawaBenchJobTools SetDraft: "Omit to
    leave unchanged"), which left tonight's cover, grenade and dehydration colonists free to wander. True on mock."""
    if not pid:
        return False
    r = s.call("jawa/set_draft", pawnId=pid, drafted=True)
    return True if s.mock else r.get("drafted") is True


def advance_remainder(r, n):
    """Ticks still owed after a jawa/safe_advance reply: 0 when it finished; n - executed when it stopped (vitals latch),
    was refused (executed absent = 0) or is still running."""
    if r.get("success") is True:
        return 0
    done = int(fnum(r.get("executed")) or 0)
    return max(0, int(n) - done)


def clear_zone(s, name):
    """Reset a zone (ProofResetRect: old digs filled back in, rolled depths forgotten) and prepare it (validation_core
    prepare_site: no things, Soil, no roof, unfogged, READ BACK). Anything left over is recorded in s.site_bad[name], so
    every row read on that zone is UNMEASURED/SITE rather than a mod verdict (the old code ignored clear_site's answer,
    and prepare_site's own SITE rows went to the Walk, never into session.json)."""
    s.site_bad.pop(name, None)
    if s.mock:
        return True
    rect = s.zones[name]
    why = []
    ok, txt = s.w.proof(NSP, "ProofResetRect", "%d;%d;%d;%d" % rect)
    if not ok or kvparse(txt).get("left", "0") != "0":
        why.append("ProofResetRect: %s" % txt[:120])
    site_rows = []
    if not s.w.V.prepare_site(s.w.B, rect, site_rows, "site_%s" % name):
        why += [str(r.get("detail") or r)[:160] for r in site_rows if r.get("status") != "PASS"] or ["prepare_site: not ready"]
    if why:
        s.site_bad[name] = why
        s.notes.append("zone %s not ready: %s" % (name, why))
    return not why


def hediffs(snap):
    """{defName: severity} from a jawa/pawn_get snapshot, whatever the key spelling; {} when none are listed."""
    out = {}
    for p in (snap.get("pawns") or [snap]):
        if not isinstance(p, dict):
            continue
        hs = p.get("hediffs")
        if hs is None and isinstance(p.get("health"), dict):
            hs = p["health"].get("hediffs")
        for h in hs or []:
            if isinstance(h, dict):
                d = h.get("def") or h.get("defName") or h.get("hediff")
                out[d] = out.get(d, 0.0) + (fnum(h.get("severity")) or 0.0)
    return out


# ============================================================================ B0 preflight
def b0_preflight(s):
    rm = s.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False)
    ids = [p.lower() for p in rm.get("packageIds") or []]
    s.env.update(running=len(ids), flowworks=MOD_ID in ids, assembly_matches=len((rm.get("assembly") or {}).get("matches") or []))
    s.env["config"] = "min-%d" % len(ids) if ids else "UNMEASURED"
    big = len(ids) > 40
    s.row("B0_tier_truth", "-", "-", "PASS" if ids and MOD_ID in ids and not big else "UNMEASURED", "HARNESS",
          dict(running=len(ids), flowworks=MOD_ID in ids, why="the flowworks tier is ~11-13 mods" if big else ""), "B0")
    if not s.mock:
        try:
            import validation_core as V
            V.log_revive(s.w.B)
            V.tap_start(s.w.B)
        except Exception as ex:  # noqa: BLE001
            s.notes.append("log_revive/tap_start: %s" % ex)
    s.call("jawa/kill_hostiles")
    s.call("jawa/weather_set", weather="Clear", lockWeather=True)
    s.call("jawa/incident_queue_clear")
    mi = s.call("jawa/map_info")
    if mi.get("sizeX"):
        s.size = (int(mi["sizeX"]), int(mi.get("sizeZ") or mi["sizeX"]))
        s.zones = plan_zones(s.size)
    t0, w0 = s.now(), time.time()
    s.advance(600)
    dt, dw = s.now() - t0, max(1e-3, time.time() - w0)
    s.env["ticks_per_s"] = round(dt / dw, 1)
    s.row("B0_clock_rate", "-", "-", "PASS" if dt >= 600 else "UNMEASURED", "HARNESS",
          dict(ticks=dt, wall_s=round(dw, 2), ticks_per_s=s.env["ticks_per_s"], frameBudgetMs=s.args.frame_budget_ms), "B0")


# ============================================================================ B2 zero-tick reads
DIALOG_LABELS = {
    ("FALL_DAMAGE_BUILD_DEEP_DROPS_KILL", "A1"): "A deep fall can kill",
    ("PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER", "A1"): "A pit room's floor is at least",
    ("PIT_ALERT_BUILD_RED_MEANS_HELP", "A1"): "Red alert: a colonist stuck in a pit",
    ("BEACH_RING_RETIRE_DRAINED_MEANS_DRY", "A1"): "Shore shelf",
    ("FALL_GUARDRAILS_BUILD_REAL_OBJECT", "A2"): "Guardrails and fences stop falls off a lip",
}


def _texts(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and k.lower() in ("label", "text", "title", "tooltip", "content", "caption"):
                acc.append(v)
            else:
                _texts(v, acc)
    elif isinstance(o, list):
        for v in o:
            _texts(v, acc)
    return acc


def settings_surface(s, handle="RimMandrakeFlowWorksMod"):
    """The exact settings-surface id of FlowWorks' MAIN Mod class. The packageId alone matches two surfaces
    (RimMandrakeFlowWorksMod and RiverSteamMod) and open_mod_settings refuses it (live 2026-10-19: 'matched multiple')."""
    if getattr(s, "_surface", None):
        return s._surface
    r = s.call("rimworld/list_mod_settings_surfaces") or {}
    found = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("handleTypeName") == handle and str(o.get("modId", "")).startswith("mod-settings:" + MOD_ID):
                found.append(o["modId"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(r)
    s._surface = found[0] if found else MOD_ID
    return s._surface


def b2_settings_dialog(s):
    """The five 'dialog not rendered' partials, in ONE open: every label must be found in the open dialog's UI text
    (rimworld/get_ui_layout); a dialog with no readable text is UNMEASURED, its screenshot kept for an eye check. Then
    the disk round trip: flip pitGuardrailEnabled, close the dialog (WriteSettings), read the config file, restore."""
    r = s.call("rimworld/open_mod_settings", modId=settings_surface(s), replaceExisting=True)
    opened = r.get("success") is True
    lay = s.call("rimworld/get_ui_layout") if opened else {}
    texts = " | ".join(_texts(lay, []))
    shot = s.call("jawa/take_screenshot", fileName="live_session_settings_%d" % int(time.time())).get("filePath") if opened else None
    for (item, cid), label in DIALOG_LABELS.items():
        if not opened or not texts:
            st, why = "UNMEASURED", "dialog not opened" if not opened else "get_ui_layout returned no text"
        elif label.lower() in texts.lower():
            st, why = "PASS", ""
        elif "reset this section" in texts.lower():
            # pass 2 (2026-10-19, HARNESS): since 5c75405998 the dialog is ONE scrolled column (screenshot: sections draw
            # below "Reset all" with a scrollbar) and get_ui_layout returns only the rows inside the visible scroll rect,
            # so a label further down is not "missing". The body draws; the label's own row is not readable from here.
            st, why = "UNMEASURED", "label below the fold: get_ui_layout reads only the visible rows of the scrolled list"
        else:
            st, why = "FAIL", "the dialog draws no section body (no 'Reset this section')"
        # two words of the item: PIT_ROOM/PIT_ALERT and FALL_GUARDRAILS/FALL_DAMAGE shared one id on the first word alone
        s.row("B2_dialog_%s_%s" % ("_".join(item.split("_")[:2]).lower(), cid), item, cid, st, "MOD" if st == "FAIL" else "HARNESS" if st != "PASS" else "MOD",
              dict(label=label, why=why, shot=shot, textChars=len(texts)), "B2", eyes=not texts)
    s.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    before = s.sget("pitGuardrailEnabled")
    set_ok = (s.sset("pitGuardrailEnabled", False) or {}).get("success") is not False
    opened2 = s.call("rimworld/open_mod_settings", modId=settings_surface(s), replaceExisting=True).get("success") is True
    s.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    # a dialog that never opened never closes, so nothing is written: that is UNMEASURED, not a MOD fail (live 2026-10-19)
    disk = read_settings_file(s) if opened2 else None
    s.sset("pitGuardrailEnabled", before if before is not None else True)
    s.call("rimworld/open_mod_settings", modId=settings_surface(s), replaceExisting=True)
    s.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    disk2 = read_settings_file(s)
    if disk is None or disk2 is None or not set_ok or before is None:     # an unread file / refused flip is no round trip
        st = "UNMEASURED"
    else:
        st = "PASS" if ("pitGuardrailEnabled>False" in disk and (disk2 or "").find("pitGuardrailEnabled>False") < 0) else "FAIL"
    s.row("B2_guardrail_disk_roundtrip", "FALL_GUARDRAILS_BUILD_REAL_OBJECT", "A2", st, "MOD" if st == "FAIL" else "HARNESS" if st != "PASS" else "MOD",
          dict(before=before, fileHadFalse=None if disk is None else "pitGuardrailEnabled>False" in disk), "B2")


def read_settings_file(s):
    """The mod's settings XML in the Config folder (Mod_<packageId-ish>_<ModClass>.xml); None when not found."""
    if s.mock:
        return None
    try:
        import validation_core as V
        cfg = os.path.join(os.path.dirname(V.SAVES), "Config")
        for n in sorted(os.listdir(cfg)):
            if n.startswith("Mod_") and "FlowWorks" in n and n.endswith(".xml"):
                with open(os.path.join(cfg, n), encoding="utf-8", errors="replace") as f:
                    return f.read()
    except OSError:
        return None
    return None


def b2_tank_tall(s):
    """TANK_TALL: a tall tank holds twice a short one. Both built, both offered far more than either holds through
    ProofTank Store; the stored units read back. A reply that stores everything offered (no clamp) cannot answer."""
    x, z, _w, _h = s.zones["tanks"]
    import fw_walk_common as FC
    clear_zone(s, "tanks")          # B2 runs before B4's clears: the tanks were placed on uncleared quicktest ground
    a = FC.place(s.w, "RM_LiquidTank", (x + 1, z + 1)) if not s.mock else dict(survived=True)
    b = FC.place(s.w, "RM_LiquidTankTall", (x + 6, z + 1)) if not s.mock else dict(survived=True)
    offer = 10 ** 7
    got = []
    for c in ((x + 1, z + 1), (x + 6, z + 1)):
        ok, txt = s.proof(NSP, "ProofTank", "%d,%d;Store;RM_Liquid_FreshWater;%d" % (c[0], c[1], offer))
        m = re.search(r"\(capacity (\d+)\)", txt) if not ok else None
        if m:   # ProofTank REFUSES an offer over capacity (it never clamps) and names the capacity: fill to exactly it
            ok, txt = s.proof(NSP, "ProofTank", "%d,%d;Store;RM_Liquid_FreshWater;%s" % (c[0], c[1], m.group(1)))
        s.timing.setdefault("tank_tall", []).append(txt[:160])
        got.append(fnum(kvparse(txt).get("units")) if ok else None)
    short, tall = got
    if not (a.get("survived") and b.get("survived")) or None in got or short in (0, offer) or tall == offer:
        st = "UNMEASURED"
    else:
        st = "PASS" if abs(tall - 2 * short) <= 1 else "FAIL"
    s.row("B2_tank_tall_twice", "TANK_TALL_BUILD_TWICE_THE_DRINK", "live", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(short=short, tall=tall, offered=offer, placed=[a.get("note") or a.get("survived"), b.get("note") or b.get("survived")]), "B2")


def b2_readouts(s):
    """DEPTH_READOUT A2 / LIQUID_DEPTH A2: the mouseover strings over a dug dry cell, a filled canal, a dug pond, dry
    ground and a painted lake that TOUCHES the east map edge (the readout zone is edge-flush, plan_zones), so it is
    limitless by wetness (LAKE_GROUNDWATER_REFILL_BUILD_WETNESS_CUT, 392300ef0d: every map-edge body is limitless) and
    its readout must say the sea never runs dry. A lake that did not reach the edge, or stickyLimitlessEnabled off, is
    UNMEASURED/SITE (sea_verdict)."""
    rect = s.zones["readout"]
    x, z, _w, _h = rect
    W = s.size[0]
    clear_zone(s, "readout")
    dry, canal, pond, ground = (x + 1, z + 1), [(x + 3 + i, z + 1) for i in range(5)], (x + 10, z + 1), (x + 1, z + 4)
    s.dig(dry, 2)
    for c in canal:
        s.dig(c, 1, 1)
    s.pit(pond, 3, 3, 4, 3)
    lake = (x + 4, z + 5, W - (x + 4), 11)          # east edge column W-1 included
    s.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,%d,%d" % lake)
    # pass 2 (2026-10-19, HARNESS, presumed): 2 ticks after the paint the lake read "Hole 2 m · Water 2.00 m (4,000 L)"
    # -- a body the engine had not classified yet. Ask the engine to classify it (as v2 S3 and B4's reservoir do) and
    # give it a pulse; the body report is kept beside the readout so a limitless body with a limited readout is visible.
    s.advance(300)
    lake_body = (s.call("jawa/flowworks_body_report", x=x + 10, z=z + 10, classify=True) or {}).get("body") or {}
    s.advance(2)
    edge = str(s.call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (W - 1, z + 10)).get("ops") or "")
    sticky = s.sget("stickyLimitlessEnabled")
    reads = {}
    for name, c in (("dug_dry", dry), ("canal", canal[2]), ("pond", (pond[0] + 1, pond[1] + 1)), ("ground", ground),
                    ("lake", (x + 10, z + 10))):
        ok, txt = s.proof(NSP, "ProofReadout", "%d,%d" % c)
        reads[name] = txt if ok else "UNREAD " + txt[:80]
    s.timing["readouts"] = reads
    import water_scenes_walk as WS
    p = {k: WS.parse_readout(v) for k, v in reads.items()}
    unparsed = [k for k, v in p.items() if v is None]
    fmt_ok = p.get("canal") and p["canal"].get("kind") == "water" and p.get("pond") and p["pond"].get("kind") == "water"
    st = "UNMEASURED" if unparsed or any(str(v).startswith("UNREAD") for v in reads.values()) else ("PASS" if fmt_ok else "FAIL")
    sst, scls, swhy = sea_verdict(p.get("lake"), "WaterDeep" in edge, sticky)
    s.row("B2_readout_sea_never_dry", "DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE", "A2", sst, scls,
          dict(lake=reads.get("lake"), lakeRect=lake, edgeCell=edge[:60], sticky=sticky, why=swhy,
               lakeBody={k: lake_body.get(k) for k in ("id", "limitless", "cellCount", "stock", "capacity")}), "B2")
    s.row("B2_readout_two_numbers_and_sea", "DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE", "A2", st, "MOD" if st == "FAIL" else "HARNESS" if st != "PASS" else "MOD",
          dict(reads=reads, wording="owner looks at these strings (V8 kept by card)"), "B2", eyes=True)
    st2 = st if st == "UNMEASURED" else ("PASS" if all(" m " in str(v) and " L)" in str(v) for k, v in reads.items() if k in ("canal", "pond")) else "FAIL")
    s.row("B2_readout_metres_litres", "LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD", "A2", st2, "MOD" if st2 == "FAIL" else "HARNESS" if st2 != "PASS" else "MOD",
          dict(canal=reads.get("canal"), pond=reads.get("pond"), eyes="settings UI by eye: B2 dialog screenshot"), "B2", eyes=True)


def sea_verdict(lake, edge_painted, sticky):
    """B2_readout_sea_never_dry -> (status, class, why). lake = parse_readout of the lake square (None = unread).
    PASS: the edge-touching lake reads limitless ('Open water ...'). FAIL/MOD: it reads as a limited body although its
    paint reached the map edge with sticky-limitless on. UNMEASURED/SITE: unread, the paint never reached the edge
    column, or stickyLimitlessEnabled is off (then a limited read is the mod's design, not a defect)."""
    if lake is None:
        return "UNMEASURED", "HARNESS", "lake readout unread"
    if not edge_painted:
        return "UNMEASURED", "SITE", "the painted lake does not reach the map-edge column (read back)"
    if str(sticky) not in ("True", "true", "1"):
        return "UNMEASURED", "SITE", "stickyLimitlessEnabled is %r: an edge body is limited by design" % (sticky,)
    if lake.get("kind") == "limitless":
        return "PASS", "MOD", ""
    return "FAIL", "MOD", "an edge-touching lake read %r, not limitless" % (lake.get("text") or lake.get("kind"))


# ============================================================================ B4 shared-clock blocks (generators)
HUMAN = "Colonist"


def g_cover_tiers(s):
    """SUSPENSION_BASE A3: one six-cover deck over 2 m (superdeep) cells per tier (40/120/220 kg). Colonists are
    stood on the deck one per cover, one at a time; each pawn's Mass is READ (pawn_stats), never assumed. A cover must hold while
    the summed mass is under its rating and give way (the deck is gone from the map and the pawn stands on a dug cell) once
    over it."""
    x, z, _w, _h = s.zones["covers"]
    tiers = (("RM_PitCover_WovenScrap", 40.0), ("RM_PitCover_PlankLattice", 120.0), ("RM_PitCover_ReinforcedFrame", 220.0))
    import fw_walk_common as FC
    for k, (d, rating) in enumerate(tiers):
        c = (x + 1 + k * 8, z + 3)
        # ONE deck of six covers in a row, one pawn per cover: a second pawn spawned on an occupied cell lands BESIDE
        # it, off the cover (live 2026-10-19: 120/220 tiers 'held' 121 kg and 231 kg that were never on them)
        deck = [(c[0] + i, c[1]) for i in range(6)]
        for cc in deck:
            s.dig(cc, 4)
        # the cover spares its OWN faction (CompPitCoverTrigger: LoadOn(.., parent.Faction, superdeepCapturesOwnFaction)),
        # so a player cover never weighs colonists: own the cover by another faction instead of flipping the map-wide
        # setting under the shared clock (live 2026-10-19: all three tiers 'held' a colonist at 60.7 kg)
        if not s.mock:
            s.call("jawa/build_batch", ops=";".join("%s:%d,%d" % (d, cc[0], cc[1]) for cc in deck), faction="hostile", wipeExisting=False)
            got = [t for t in FC.list_things(s.w, [d], (c[0] - 1, c[1] - 1, 8, 3)) if t["cell"] is not None]
            placed = dict(survived=len(got) >= len(deck), note="" if len(got) >= len(deck) else "%d of %d covers on the map after build_batch" % (len(got), len(deck)))
        else:
            placed = dict(survived=True)
        if not placed.get("survived"):
            s.row("B4_cover_%d" % int(rating), "SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT", "A3", "UNMEASURED", "SITE",
                  dict(def_=d, note=placed.get("note")), "B4")
            continue
        total, held_under, dropped_over, pids, trail = 0.0, True, None, [], []
        for n in range(6):
            pid = s.spawn(HUMAN, deck[n])
            if pid is None:
                break
            pids.append(pid)
            # set_draft with no `drafted` changes NOTHING: the colonists stayed undrafted and wandered off the deck between
            # reads (live rerun 20261019T010244: 120 "held" 121.0 kg, 220 "held" 244.3 kg with depths 4 -> 0 and all six
            # covers standing; PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON). Draft, and read the draft back.
            dr = s.call("jawa/set_draft", pawnId=pid, drafted=True)
            if not s.mock and dr.get("drafted") is not True:
                trail.append(dict(n=n + 1, drafted="UNREAD", note=str(dr.get("message") or dr.get("error") or "")[:120]))
                break
            ms = s.call("jawa/pawn_stats", pawn=pid, stats="Mass")
            m = None
            for st in ms.get("stats") or []:
                if isinstance(st, dict) and (st.get("stat") or st.get("defName")) == "Mass":
                    m = fnum(st.get("value"))
            if m is None:
                trail.append(dict(n=n, mass="UNREAD"))
                break
            total += m
            yield Wait(70)                          # the trigger scans the deck every 30 ticks
            reads = [s.climb(p) or {} for p in pids]
            down = [r.get("depth") for r in reads]
            # every pawn must still stand on (or have fallen through) its deck cell, or the load the row sums is not the
            # load on the deck: a pawn found elsewhere makes the row UNMEASURED, never "held"
            off = [] if s.mock else [r.get("cell") for r in reads if tuple(r.get("cell") or ()) not in deck]
            if off:
                trail.append(dict(n=n + 1, total=round(total, 1), depths=down, off_deck=off))
                break
            # "gave way" is read off the COVER, never ProofClimb's depth: that is the cell's dug depth (ProofPocket ->
            # ClimbDepthAt, deck-blind), 4 under a colonist on an INTACT cover too (live 2026-10-19 run 20261018T233414:
            # 120/220 "gave way" under one ~60 kg colonist; PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON). A deck gives way whole.
            left = None                             # mock: FakeGame models no covers, the depth alone decides
            if not s.mock:
                got = [t for t in FC.list_things(s.w, [d], (c[0] - 1, c[1] - 1, 8, 3)) if t["cell"] in deck]
                if not got and (getattr(s.w, "last_list", None) or {}).get("countMatched") is None:
                    trail.append(dict(n=n + 1, total=round(total, 1), depths=down, covers_left="UNREAD"))
                    break
                left = len(got)
            fell = (left is None or left == 0) and any(dd is not None and dd > 0 for dd in down)
            trail.append(dict(n=n + 1, total=round(total, 1), depths=down, covers_left=left))
            if total < rating and fell:
                held_under = False
                break
            if total >= rating:
                dropped_over = fell
                break
        if any(t.get("mass") == "UNREAD" or t.get("covers_left") == "UNREAD" or t.get("drafted") == "UNREAD" or t.get("off_deck")
               for t in trail):
            st = "UNMEASURED"
        elif not held_under:          # gave way UNDER its rating: an answer, and the wrong one (was read as UNMEASURED)
            st = "FAIL"
        elif dropped_over is None:
            st = "UNMEASURED"
        else:
            st = "PASS" if dropped_over else "FAIL"
        s.row("B4_cover_%d" % int(rating), "SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT", "A3", st,
              "MOD" if st != "UNMEASURED" else "HARNESS", dict(def_=d, rating=rating, trail=trail), "B4")


def g_pit_access(s):
    """PIT_ACCESS A1-A4 on one strip: four 3x3 pits (2 m with a portable ladder; 4 m sheer for climbing gear and its
    no-gear control; 3 m for the jump pack; 3 m sheer with a downed colonist and nobody able to reach)."""
    x, z, _w, _h = s.zones["access"]
    import fw_walk_common as FC
    P1, P2, P3, P4 = (x + 1, z + 1), (x + 10, z + 1), (x + 19, z + 1), (x + 28, z + 1)
    s.pit(P1, 3, 3, 4)          # 2 m
    s.pit(P2, 3, 3, 8)          # 4 m sheer
    s.pit(P3, 3, 3, 6)          # 3 m
    # pass 2 (2026-10-19, HARNESS, presumed): at 3 m the A2 climbing-gear colonist (climbs sheer 4 m) can reach the downed
    # one, so RM_MapComponent_PitRescueLadder.AnyRescuerReaches is true and NO ladder is queued -- by design. 5 m is past
    # every rescuer's reach on this map, which is the A4 scene ("nobody can go").
    # RESCUE_LADDER_DIAGNOSE_NOBODY_FETCHES_IT (2026-10-19): FALSE premise. Climbing gear climbs ANY wall (ClimbLimitOf ->
    # RM_PitAccessMath.ScalesAnyWall, k=7 in the ProofClimb read), so depth never excludes the gear wearer. It is drafted
    # (s.order drafts), and vanilla's DoctorRescue never runs drafted: the MOD fix is that AnyRescuerReaches no longer
    # counts a drafted / Doctor-disabled rescuer, so this scene (gear wearer drafted) is "nobody will go" and a ladder queues.
    s.pit(P4, 3, 3, 10)         # 5 m sheer, no ladder
    lad = FC.place(s.w, "RM_LadderPortable", (P1[0] + 1, P1[1] + 2), rot=0) if not s.mock else dict(survived=True)
    a = s.spawn(HUMAN, (P1[0] + 1, P1[1] + 1))
    g = s.spawn(HUMAN, (P2[0] + 1, P2[1] + 1))
    ctl = s.spawn(HUMAN, (P2[0] + 1, P2[1] + 0))
    j = s.spawn(HUMAN, (P3[0] + 1, P3[1] + 5))
    d = s.spawn(HUMAN, (P4[0] + 1, P4[1] + 1))
    gear = s.call("jawa/pawn_gear", **{"pawn": g, "action": "wear", "def": "RM_ClimbingGear", "stuff": ""}) if g else {}
    jp = s.call("jawa/pawn_gear", **{"pawn": j, "action": "wear", "def": "Apparel_PackJump", "stuff": ""}) if j else {}
    out = (x + 5, z + 10)
    ordered = {}
    for pid in (a, g, ctl):
        if pid:
            ordered[pid] = order_taken(s, s.order(pid, out), pid)
    # downed WITHOUT bleeding (a bleeder dies inside the 6,000-tick wait) and read back: a colonist that is not downed
    # is not the A4 scene (the reply was never read)
    inc = s.call("jawa/pawn_force_incapacitate", pawn=d, action="downed", allowBleedingWounds=False) if d else {}
    downed = s.mock or inc.get("downedAfter") is True
    rescue_t0 = s.now()
    yield Wait(1500, until=lambda: all((s.climb(p) or {}).get("depth") == 0 for p in (a, g) if p), every=150)
    ra, rg, rc = s.climb(a) if a else {}, s.climb(g) if g else {}, s.climb(ctl) if ctl else {}

    def st_out(r, want_out=True):
        if not r:
            return "UNMEASURED"
        return "PASS" if ((r.get("depth") == 0) == want_out) else "FAIL"
    st = st_out(ra) if lad.get("survived") and ordered.get(a, False) else "UNMEASURED"
    s.row("B4_access_portable_ladder_out", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A1",
          st, "MOD" if st != "UNMEASURED" else "SITE" if not lad.get("survived") else "HARNESS", dict(ladder=lad, pawn=ra, orderTaken=ordered.get(a),
          owed="build-by-colonist, uninstall/re-set and the 4 m refusal are not read by this row"), "B4")
    s.row("B4_access_gear_climbs_sheer_4m", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A2",
          st_out(rg) if gear.get("success") and ordered.get(g, False) else "UNMEASURED",
          "MOD" if gear.get("success") and ordered.get(g, False) else "HARNESS",
          dict(gear=str(gear)[:160], pawn=rg, orderTaken=ordered.get(g)), "B4")
    st = st_out(rc, want_out=False) if ordered.get(ctl, False) else "UNMEASURED"
    s.row("B4_access_no_gear_stays_in", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A2", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(pawn=rc), "B4")
    # A3: jump pack in and out (the jump verb is driven by jawa/pawn_use_verb on the pack; refused = UNMEASURED)
    jin = {}
    if jp.get("success"):
        vl = s.call("jawa/pawn_use_verb", pawn=j, action="list")
        # the list sits under "result" ({success, action, result: {pawn, verbCount, verbs}}, JawaBenchAbilityTools); the
        # top-level read found none (live 20261018T233414: "no jump verb listed"). Cast by the verb's load id: a jump
        # pack's verbProps.label may be null
        listed = (vl.get("result") or {}).get("verbs") if isinstance(vl.get("result"), dict) else vl.get("verbs")
        verbs = [v for v in (listed or []) if "jump" in str(v).lower()]
        lab = ((verbs[0].get("id") or verbs[0].get("label")) if isinstance(verbs[0], dict) else str(verbs[0])) if verbs else None
        if lab:
            jin = s.call("jawa/pawn_use_verb", pawn=j, action="cast", verb=lab, x=P3[0] + 1, z=P3[1] + 1)
        else:
            jin = {"success": False, "why": "no jump verb listed", "verbs": str(vl)[:120]}
    yield Wait(180)
    rj = s.climb(j) if j else {}
    hed = hediffs(s.call("jawa/pawn_get", pawn=j)) if j else {}
    fall = [k for k in hed if k and ("Fall" in k or "Bruise" in k or "Crack" in k)]
    st = "UNMEASURED" if not (jp.get("success") and jin.get("success") and rj) else (
        "PASS" if (rj.get("depth") or 0) > 0 and not fall else "FAIL")
    s.row("B4_access_jump_pack_in_no_fall", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A3", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(pack=str(jp)[:120], jump=str(jin)[:160], pawn=rj, hediffs=hed,
               owed="jump back out, skip, knockback-still-falls: not read"), "B4")
    # A4: a downed colonist in a sheer pit -> a ladder job queued at the nearest wall, built, colonist rescued
    def ladder_there():
        lr = s.call("jawa/list_things", defName="RM_Ladder,RM_LadderPortable,Blueprint_RM_Ladder,Frame_RM_Ladder,"
                    "Blueprint_RM_LadderPortable,Frame_RM_LadderPortable", rect="%d,%d,5,5" % (P4[0] - 1, P4[1] - 1), limit=10)
        if lr.get("success") is not True:           # a refused read is not "no ladder queued"
            return None
        return bool(lr.get("things"))
    yield Wait(6000, until=ladder_there, every=250)
    seen = ladder_there()
    rd = s.climb(d) if d else {}
    st = "UNMEASURED" if not d or not downed or not rd or not (rd.get("depth") or 0) > 0 or seen is None else ("PASS" if seen else "FAIL")
    s.row("B4_access_rescue_ladder_queued", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A4", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(ladderSeen=seen, afterTicks=s.now() - rescue_t0, downed=rd, incapacitate=str(inc)[:160],
               owed="'built and the colonist carried out' needs a longer ride: read again in B7"), "B4")
    s.pawns["rescue"] = d


def g_dig_depth(s):
    """PIT_DEPTH A2 + DIG_COST A2: a square driven to 8 m (16 notches) reads 'Hole 8 m' in the readout; the dig job on a
    7.5 m square reports its work total, compared with the curve (3,200 x notch, DigCost selftest)."""
    x, z, _w, _h = s.zones["digdepth"]
    a, b = (x + 2, z + 2), (x + 6, z + 2)
    s.dig(a, 16)
    s.dig(b, 15)
    yield Wait(2)
    ok, txt = s.proof(NSP, "ProofReadout", "%d,%d" % a)
    import water_scenes_walk as WS
    p = WS.parse_readout(txt) if ok else None
    hole = None
    if p and p.get("kind") == "water":
        hole = p.get("hole_m")
    elif ok and "Hole" in txt:
        hole = fnum(txt.split("Hole", 1)[1].strip().split()[0].replace(",", ""))
    st = "UNMEASURED" if hole is None else ("PASS" if abs(hole - 8.0) < 0.01 else "FAIL")
    s.row("B4_dig_8m_readout", "PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT", "A2", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(readout=txt[:160], owed="'a colonist digs it by Dig to depth' is the P10 walk: job read below"), "B4")
    # jawa/flowworks_job_probe reports the designator and WorkGiver verdicts only, NO work total (its ResultDescription):
    # the old row read workTotal/work/... off it and could never answer. The dig job prices each cut with
    # RM_ExcavationDepth.WorkToDeepen(current) = RM_DigDepthMath.WorkToCut(current + 1, digCostRisesWithDepth): read that
    # production function live for the 15 -> 16 cut on b, with the LIVE setting, and keep the probe as the "a dig job
    # exists here" evidence.
    jp = s.call("jawa/flowworks_job_probe", x=b[0], z=b[1], kind="dig")
    rises = s.sget("digCostRisesWithDepth")
    st, why, work = dig_cost_verdict(rises, *s.proof("RimMandrake.FlowWorks.RM_DigDepthMath", "WorkToCut",
                                                       "16|%s" % ("false" if str(rises).lower() == "false" else "true")))
    s.row("B4_dig_cost_notch16", "DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT", "A2", st, "MOD" if st in ("PASS", "FAIL") else
          "SITE" if "setting" in why else "HARNESS",
          dict(work=work, want=3200 * 16, setting=rises, why=why, designator=(jp.get("designator") if isinstance(jp, dict) else None),
               how="INFERRED: the job's per-cut work function read live, the progress bar not timed"), "B4")


FISH_CERTAIN_SIZE = 200     # vanilla FishingUtility.ChanceForCommonFishFromWaterBodySizeCurve: 0 <75, .05@75, .5@100, 1@200


def fish_roll_verdict(fr):
    """B4_reservoir_fish_rolled -> (status, class, why) from a jawa/fishing read of the filled 10x20 dug reservoir.
    Fish are a ROLL on the body's size (WaterBody.SetFishTypes; the FlowWorks mend re-rolls at 75/100/200): only a body
    of 200+ squares is certain. pass 2 (2026-10-19, HARNESS): a 100-square body PASSed in pass2 and FAILed in pass2c on
    the same build -- the 52.5% coin (1 - .95 x .5), not a bug. A fishless body under 200 is UNMEASURED/SITE."""
    if not isinstance(fr, dict) or fr.get("success") is not True or not isinstance(fr.get("body"), dict):
        return "UNMEASURED", "HARNESS", "jawa/fishing read failed: %s" % str((fr or {}).get("error") or fr)[:100]
    wb = fr["body"]
    if wb.get("hasBody") is not True:
        return "UNMEASURED", "SITE", "no vanilla water body under the reservoir (filled? see its dig rows)"
    if wb.get("hasFish") is True or wb.get("commonFish"):
        return "PASS", "MOD", ""
    size = fnum(str(wb.get("size")))
    if size is None or size < FISH_CERTAIN_SIZE:
        return "UNMEASURED", "SITE", "a %s-square body lost the game's size roll (certain only at %d+)" % (
            wb.get("size"), FISH_CERTAIN_SIZE)
    return "FAIL", "MOD", "a %s-square dug water body rolled no fish (certain at %d+)" % (wb.get("size"), FISH_CERTAIN_SIZE)


def dig_cost_verdict(rises, ok, txt):
    """B4_dig_cost_notch16 -> (status, why, work). ok/txt = the WorkToCut(16, setting) static_call. The bar is the curve
    ("deep is a megaproject": 3,200 x notch, 51,200 for the 16th); with digCostRisesWithDepth off the flat cost is the
    designed answer, so the row cannot judge the curve: UNMEASURED/SITE."""
    if str(rises).lower() not in ("true", "false"):
        return "UNMEASURED", "digCostRisesWithDepth unread (%r)" % (rises,), None
    work = fnum(str(txt).strip()) if ok else None
    if work is None:
        return "UNMEASURED", "WorkToCut unread: %s" % str(txt)[:80], None
    if str(rises).lower() == "false":
        return "UNMEASURED", "the setting digCostRisesWithDepth is off: flat cost by design", work
    return ("PASS" if work == 3200 * 16 else "FAIL"), "", work


POND = "POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD"


def g_reservoir(s):
    """FISH_ROLL A2 / POND_DEPTH A7: a 10x20 (200-square) dug reservoir, filled; its body report after a pulse names the
    fish it rolled (200 squares: the game's chance is 1.0, so a fishless body is the mend failing). A7, the catch: a vanilla fishing zone over the dug water
    (jawa/map_zones zoneType=fishing, which names each refused cell), one colonist on the vanilla Fish job
    (jawa/ordered_job, fishCell + standSpot from jawa/fishing), and the map's Fish-group total read before and after.
    PASS = the total rose. A zone refused for 'no fish' / 'no water-body type' or a zone that lost its cells during the
    job is FAIL/MOD (dug water that cannot be fished). No catch with the zone intact is UNMEASURED/SITE: the job's 2%
    negative-outcome roll gives no fish by design, and a needs interrupt ends the job; the detail says which to re-run."""
    x, z, _w, _h = s.zones["reservoir"]
    # pass 2 (2026-10-19, SITE): a uniform 4-notch (2 m) pit is all WaterDeep, and vanilla
    # Designator_ZoneAdd_Fishing.CanDesignateCell refuses Impassable terrain, so every cell was refused ("impassable
    # terrain WaterDeep", read live) -- a lake is fished from its shallows too. Shape it like a pond: a 2-notch (1 m,
    # WaterShallow) rim, a 4-notch 6x16 middle, both filled to the brim (one surface, one body). 10x20 = 200 squares,
    # where vanilla's fish chance reaches 1.0 (pass 2c: a 10x10 body lost its 52.5% roll).
    for i in range(10):
        for j in range(20):
            mid = 2 <= i <= 7 and 2 <= j <= 17     # each cell dug ONCE: dig() reads back depth == n from 0
            s.dig((x + 2 + i, z + 2 + j), 4 if mid else 2, 4 if mid else 2)
    yield Wait(500)
    # flowworks_body_report has NO fish field (body{id, limitless, stock, capacity, cellCount, ...}): the old row read
    # fish/fishTypes/fishCount off it, so every read body was a FAIL. The fish roll is the vanilla WaterBody's, read by
    # jawa/fishing (body{hasBody, hasFish, commonFish, population, ...}); the FlowWorks body stays as detail.
    b = s.call("jawa/flowworks_body_report", x=x + 6, z=z + 11, classify=True).get("body") or {}
    fr = s.call("jawa/fishing", action="read", x=x + 6, z=z + 11)
    st, cls, why = fish_roll_verdict(fr)
    wb = fr.get("body") if isinstance(fr.get("body"), dict) else {}
    s.row("B4_reservoir_fish_rolled", "FISH_ROLL_MEND_PONDS_BORN_BARREN", "A2", st, cls,
          dict(why=why, waterBody={k: wb.get(k) for k in ("hasBody", "type", "size", "hasFish", "commonFish", "population")},
               fwBody={k: b.get(k) for k in ("id", "cellCount", "stock", "capacity", "limitless")}), "B4")

    def a7(st, cls, **d):
        s.row("B4_reservoir_catch", POND, "A7", st, cls, d, "B4")

    zr = s.call("jawa/map_zones", action="createZone", zoneType="fishing", rect="%d,%d,10,20" % (x + 2, z + 2))
    if not zr.get("success"):
        # pass 2 (2026-10-19, HARNESS): the companion's Fail() nests the cells under "details" ({success, message,
        # details: {cellsRequested, refusedCells}}); the top-level read saw none, so a "no fish" refusal scored HARNESS
        det = zr.get("details") if isinstance(zr.get("details"), dict) else {}
        whys = sorted(set(str(c.get("why")) for c in (zr.get("refusedCells") or det.get("refusedCells") or [])))
        mod = any("no fish" in w or "no water-body type" in w for w in whys)
        a7("FAIL" if mod else "UNMEASURED", "MOD" if mod else "HARNESS",
           why="fishing zone refused on the dug reservoir", refusals=whys[:6], error=str(zr.get("error") or zr.get("message"))[:200])
        return
    label = zr.get("created")
    p = s.spawn(HUMAN, (x + 1, z + 1))
    rd = s.call("jawa/fishing", action="read", zone=label, pawn=p) if p else {}
    fc, sp = rd.get("fishCell"), rd.get("standSpot")
    if not (p and rd.get("success") and fc and sp):
        a7("UNMEASURED", "HARNESS" if not rd.get("success") else "SITE", why="no pawn, no jawa/fishing read, or no stand spot",
           pawn=p, zone=dict(label=label, cells=zr.get("cells"), refused=zr.get("refusedCount")),
           read=str(rd.get("error") or rd.get("standSpotWhyNone") or rd.get("message"))[:200])
        return
    before = int(rd.get("fishTotal") or 0)
    job_ticks = int(rd.get("jobTicks") or 7500)
    oj = s.call("jawa/ordered_job", pawnId=p, jobDef="Fish", targetAX=fc["x"], targetAZ=fc["z"],
                targetBX=sp["x"], targetBZ=sp["z"], waitTicks=0)
    if not oj.get("accepted"):
        a7("UNMEASURED", "HARNESS", why="Fish job not accepted", job=str(oj)[:240])
        return
    last = {}

    def caught():
        last.update(s.call("jawa/fishing", action="read", zone=label) or {})
        return int(last.get("fishTotal") or 0) > before
    w = Wait(job_ticks + 1500, until=caught, every=250)
    yield w
    caught()
    after, zone_after = int(last.get("fishTotal") or 0), last.get("zone") or {}
    d = dict(zone=label, zoneCells=[zr.get("cells"), zone_after.get("cells")], body=(rd.get("body") or {}),
             fishBefore=before, fishAfter=after, fishOnMap=last.get("fishOnMap"), jobTicks=job_ticks,
             fishCell=fc, standSpot=sp, whyNot=zone_after.get("whyNot"))
    if after > before:
        a7("PASS", "MOD", **d)
    elif not last.get("success") or not zone_after.get("cells"):
        a7("FAIL" if last.get("success") else "UNMEASURED", "MOD" if last.get("success") else "HARNESS",
           why="the fishing zone lost its dug-water cells during the job" if last.get("success") else "jawa/fishing read failed", **d)
    else:
        a7("UNMEASURED", "SITE", why="no catch, zone intact: 2%% negative outcome or the job was interrupted; re-run the block "
           "(waited %d ticks, timed_out=%s)" % (job_ticks + 1500, w.timed_out), **d)


def g_grenade(s):
    """TRENCH_COVER A4: the same Bomb blast on a pawn in a 1 m trench and on an open-ground control: equal harm."""
    x, z, _w, _h = s.zones["grenade"]
    t, o = (x + 3, z + 3), (x + 14, z + 3)
    for i in range(-2, 3):
        s.dig((t[0] + i, t[1]), 2)
    yield Wait(70)
    pt, po = s.spawn(HUMAN, t), s.spawn(HUMAN, o)
    # drafted (and read back) so neither walks off its square; each pawn's cell is read before the blast: a trench pawn
    # not IN the trench, or a control not on open ground, makes the row UNMEASURED (set_draft with no drafted= was a no-op)
    drafted = [draft(s, p) for p in (pt, po)]
    cells = [(s.climb(p) or {}).get("cell") if p and not s.mock else None for p in (pt, po)]
    placed = s.mock or (tuple(cells[0] or ()) == t and tuple(cells[1] or ()) == o)
    # pass 2 (2026-10-19, HARNESS): the sums were whole-body hediff severities, so a spawned pawn's own scars / chronic
    # conditions counted as blast harm (trench 35.0 vs open 20.5 at one 20-damage Bomb each). Read each pawn before the
    # blast and score only the severity the blast ADDED.
    pre_r = [s.call("jawa/pawn_get", pawn=p) if p else {} for p in (pt, po)]
    pre_t, pre_o = (hediffs(r) for r in pre_r)
    pre_read = s.mock or all(r.get("success") is True for r in pre_r)       # an unread pre-state makes every old scar "blast harm"
    r1 = s.call("jawa/explosion_at", at="%d,%d" % t, radius=1.9, damType="Bomb", damAmount=20)
    r2 = s.call("jawa/explosion_at", at="%d,%d" % o, radius=1.9, damType="Bomb", damAmount=20)
    yield Wait(5)
    ht, ho = (hediffs(s.call("jawa/pawn_get", pawn=p)) if p else {} for p in (pt, po))
    ht = {k: v - pre_t.get(k, 0.0) for k, v in ht.items() if v - pre_t.get(k, 0.0) > 1e-6}
    ho = {k: v - pre_o.get(k, 0.0) for k, v in ho.items() if v - pre_o.get(k, 0.0) > 1e-6}
    st, sum_t, sum_o = "UNMEASURED", sum(ht.values()), sum(ho.values())
    if r1.get("success") and r2.get("success") and pt and po and sum_o > 0 and all(drafted) and placed and pre_read:
        st = "PASS" if abs(sum_t - sum_o) <= max(2.0, 0.25 * sum_o) else "FAIL"
    s.row("B4_grenade_no_blast_cover", "TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "A4", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(trench=round(sum_t, 2), open=round(sum_o, 2), added=dict(trench=ht, open=ho), drafted=drafted, cells=cells,
               want=[t, o], note="severity ADDED by the blast (pre-blast read subtracted); a blast is random per part"), "B4")


def g_rail_lip(s):
    """FALL_GUARDRAILS A3 re-asked: a hostile walked along an UNRAILED 7 m lip. Day 6 found the AI never steps off,
    so the control cannot fall and A3 cannot discriminate; this row records that again for the bar's ruling."""
    x, z, _w, _h = s.zones["raillip"]
    s.pit((x + 2, z + 2), 6, 6, 14)
    yield Wait(70)
    h = s.spawn("Pirate", (x + 1, z + 10), faction="hostile") if not s.mock else 1
    if h:
        s.order(h, (x + 13, z + 10))
    yield Wait(900)
    r = s.climb(h) if h else {}
    s.row("B4_rail_unrailed_control", "FALL_GUARDRAILS_BUILD_REAL_OBJECT", "A3", "UNMEASURED", "OWED",
          dict(pawn=r, why="the unrailed control does not fall (AI keeps off lips): the bar needs his ruling, "
                           "A4/A7 knockback rows already discriminate"), "B4")
    s.call("jawa/kill_hostiles")


def g_dehydration_ride(s):
    """THIRST T6 compressed: one drafted colonist held at thirst 0 for the WHOLE shared clock; RM_Dehydration's
    severity rate is measured and extrapolated to 60,000 ticks (bar 0.30 +/- 0.03): INFERRED."""
    x, z, _w, _h = s.zones["ride"]
    p = s.spawn(HUMAN, (x + 2, z + 2))
    if not p:
        s.row("B4_dehydration_rate", "THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY", "T6", "UNMEASURED", "HARNESS", dict(why="no pawn"), "B4")
        return
    if not draft(s, p):
        # an undrafted colonist at thirst 0 walks off to drink: the rate it gives is not the dehydration rate
        s.row("B4_dehydration_rate", "THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY", "T6", "UNMEASURED", "HARNESS",
              dict(why="set_draft did not read back drafted=True"), "B4")
        return
    s.pawns["ride"] = p
    home = (s.climb(p) or {}).get("cell") if not s.mock else None
    wandered = []
    t0 = s.now()
    sev0 = None
    for _ in range(40):
        s.call("jawa/pawn_need", pawn=p, action="need", need="RM_Thirst", level=0.0)
        s.call("jawa/pawn_need", pawn=p, action="need", need="Food", level=1.0)
        sev = hediffs(s.call("jawa/pawn_get", pawn=p)).get("RM_Dehydration")
        if sev0 is None and sev is not None:
            sev0, t0 = sev, s.now()
        yield Wait(500)
        if not s.mock:
            here = (s.climb(p) or {}).get("cell")
            if here != home:
                wandered.append(here)        # a pawn that moved could have drunk: the rate is not the bar's
        if s.ride_stop:
            break
    sev1, t1 = hediffs(s.call("jawa/pawn_get", pawn=p)).get("RM_Dehydration"), s.now()
    if sev0 is None or sev1 is None or t1 - t0 < 2000 or wandered or (home is None and not s.mock):
        st, proj = "UNMEASURED", None
    else:
        proj = (sev1 - sev0) / float(t1 - t0) * 60000.0
        st = "PASS" if abs(proj - 0.30) <= 0.03 else "FAIL"
    s.row("B4_dehydration_rate", "THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY", "T6", st, "MOD" if st != "UNMEASURED" else "HARNESS",
          dict(sev=[sev0, sev1], ticks=t1 - t0, projected60k=proj, home=home, wandered=wandered[:6],
               how="INFERRED from the measured rate"), "B4")


SHARED_GENS = (("covers", g_cover_tiers), ("access", g_pit_access), ("digdepth", g_dig_depth), ("reservoir", g_reservoir),
               ("grenade", g_grenade), ("raillip", g_rail_lip))


def b4_shared(s):
    for n in SHARED:
        clear_zone(s, n)
    s.ride_stop = False
    gens = {n: f(s) for n, f in SHARED_GENS}
    gens["ride"] = g_dehydration_ride(s)
    done = {}
    res, spent = run_shared_with_stop(s, gens, done)
    s.timing["B4_ticks"] = spent
    for name, state in res.items():
        if state != "done":
            s.row("B4_block_%s" % name, "-", "-", "UNMEASURED", "HARNESS", dict(state=state), "B4")


def run_shared_with_stop(s, gens, done):
    """run_shared, but the dehydration ride stops once every other block has finished (it only rides their clock)."""
    others = [k for k in gens if k != "ride"]

    def adv(n):
        s.advance(n)

    def wrap(name, g):
        try:
            for w in g:
                yield w
        finally:
            # a crashed block is finished too: otherwise the ride runs its whole 40 x 500 ticks on the shared clock
            done[name] = True
            if all(done.get(k) for k in others):
                s.ride_stop = True
    return run_shared({k: wrap(k, g) for k, g in gens.items()}, adv, s.now, log=s.say)


# ============================================================================ B5 / B6 map-wide events
FREEZE_AT_C = -7.0          # Verse.FreezeManager.WaterFreezeThreshold (decompiled 1.6): no water freezes above it
STEADY_VISIT_TICKS = 1667   # SteadyEnvironmentEffectsTick visits ceil(Area * 0.0006) cells a tick: each cell ~ every 1667
COLD_CONDITIONS = ("ColdSnap", "DeepFreeze")   # both GameCondition_ColdSnap, -20 C each at full (12,000-tick ramp);
                                               # GameConditionManager.AggregateTemperatureOffset SUMS active conditions
ICE_BUDGET = 24000
ICE_BUDGET_MAX = 36000      # only spent while the freeze expectation is under 4.6 (ice_verdict's bar)
FLOOD_WEATHER = "TorrentialRain"


def freeze_expectation(temps, ncells, step):
    """Expected vanilla freeze events on ncells water squares over the polled temperatures (one per `step` ticks):
    FreezeManager.DoWaterFreezing rolls 0.003 * (T / -5) per steady-effects visit at T <= -7 C (the frozen-fraction and
    surrounded terms only RAISE it, so this is a lower bound). P(no ice) ~ exp(-expectation)."""
    e = 0.0
    for t in temps:
        if t is not None and t <= FREEZE_AT_C:
            e += step * ncells / float(STEADY_VISIT_TICKS) * 0.003 * (t / -5.0)
    return e


ICE_MELT_AT_C = 2.0         # Verse.FreezeManager.IceMeltThreshold (decompiled 1.6, Odyssey): no ice melts below it
THAW_BUDGET_MAX = 36000


def ice_cells(ops):
    """ThinIce squares from get_terrain_batch ops text ('ThinIce:x,z,w,h;...')."""
    out = set()
    for m in re.finditer(r"ThinIce:(-?\d+),(-?\d+),(\d+),(\d+)", ops or ""):
        x, z, w, h = (int(v) for v in m.groups())
        out.update((x + i, z + j) for i in range(w) for j in range(h))
    return out


def melt_candidates(ice):
    """Squares whose steady-effects visit can melt an ice square: DoIceMelting melts ThinIce within radius 2.9 of the
    VISITED cell (which need not be ice itself)."""
    near = set()
    for (x, z) in ice:
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz <= 2.9 * 2.9:
                    near.add((x + dx, z + dz))
    return len(near)


def melt_expectation_step(temp_c, ncand, step):
    """Expected vanilla melt events in one `step`: FreezeManager.DoIceMelting rolls 0.001 * ((T + 5) / 5) per visit at
    T >= 2 C (SurroundedByIce squares are skipped, so this is an upper bound per event, a fair bar for 'none at all')."""
    if temp_c is None or temp_c < ICE_MELT_AT_C:
        return 0.0
    return step * ncand / float(STEADY_VISIT_TICKS) * 0.001 * ((temp_c + 5.0) / 5.0)


def ice_verdict(cond_ok, temps, froze, thaw, same, ncells, step=500, melt_exp=None):
    """B5_ice_freeze_thaw -> (status, class, why). The row judges ice only once the site was really below freezing:
    UNMEASURED/SITE when the conditions did not start or the canal never read <= -7 C (pass 1: ColdSnap alone -> 1.4 C);
    no ice while cold enough that >= 4.6 freeze events were expected (P(no ice) < 1%) is FAIL/MOD, fewer is UNMEASURED/SITE;
    ice that froze then thawed with the readout litres unchanged is PASS, else FAIL/MOD."""
    known = [t for t in temps if t is not None]
    coldest = min(known) if known else None
    if not cond_ok:
        return "UNMEASURED", "SITE", "cold conditions did not start"
    if coldest is None:
        return "UNMEASURED", "HARNESS", "no temperature read"
    if coldest > FREEZE_AT_C:
        return "UNMEASURED", "SITE", "the canal never got below %.0f C (coldest %.1f C): ice not judged" % (FREEZE_AT_C, coldest)
    exp = freeze_expectation(temps, ncells, step)
    if froze is None:
        if exp >= 4.6:
            return "FAIL", "MOD", "%.1f freeze events expected at <= %.0f C, no ice on the dug water" % (exp, FREEZE_AT_C)
        return "UNMEASURED", "SITE", "cold enough but only %.1f freeze events expected (< 4.6): too short to judge" % exp
    if thaw is None:
        # pass 3 (2026-10-19, HARNESS): 12,000 fixed ticks at 26 C was ~2 expected melts (P(none) ~ 11%) -> a false FAIL.
        if melt_exp is not None and melt_exp < 4.6:
            return "UNMEASURED", "SITE", "warm, but only %.1f melt events expected (< 4.6): too short to judge thaw" % melt_exp
        return "FAIL", "MOD", "the ice never thawed after the cold ended"
    return ("PASS", "MOD", "") if same else ("FAIL", "MOD", "the readout litres changed across freeze and thaw")


def b5_cold_snap(s):
    """POND_DEPTH A5: four wet 0.5 m canals (56 squares: more chances for vanilla's per-visit freeze roll, none of them
    surrounded by water, which FreezeManager.CanFreeze refuses); ColdSnap + DeepFreeze (vanilla, -20 C each, summed) and
    ticks in 500s until the dug water reads Ice (ThinIce) or ICE_BUDGET; the canal's temperature is read every step and
    the row only judges ice once it was below -7 C (ice_verdict). Then both conditions end and thaw is polled.
    'Water picture intact' = the readout litres before == after."""
    rect = s.zones["ice"]
    x, z, _w, _h = rect
    canals = [[(x + 1 + i, z + 1 + 2 * r) for i in range(14)] for r in range(4)]   # z+1,3,5,7: a dry row between
    canal = canals[0]
    clear_zone(s, "ice")
    for row_ in canals:
        for c in row_:
            s.dig(c, 1, 1)
    s.advance(300)
    before = [s.w.readout(c) if not s.mock else None for c in canal[:3]]
    gcs = [s.call("jawa/game_condition", action="start", condition=n, durationTicks=60000) for n in COLD_CONDITIONS]
    cond_ok = all(g.get("success") for g in gcs)

    blind = []

    def terr():
        out_ = []
        for c in canals:
            rr = s.call("jawa/get_terrain_batch", rects="%d,%d,14,1" % c[0])
            if not s.mock and (rr.get("success") is False or not rr.get("ops")):
                blind.append(1)             # an unread canal row reads as "no ice": counted, never judged
            out_.append(str(rr.get("ops") or ""))
        return "".join(out_)

    def temp():
        return fnum(s.call("jawa/cell_temperature", cell="%d,%d" % canal[0]).get("temperature"))
    temps, froze = [], None
    # pass 3 (2026-10-19, HARNESS): clear_zone leaves vanilla temp terrain (ThinIce) from an earlier B5 on the same map,
    # which read as 'froze after 500 ticks' at 25 C. Ice before the cold is no reading.
    stale_ice = len(ice_cells(terr())) if not s.mock else 0
    keep = (s.pawns.get("rescue"),)
    try:
        # pass 2 (2026-10-19, HARNESS): 24,000 ticks on a warm map reached only 4.49 expected freezes (bar 4.6) -> UNMEASURED.
        # Past ICE_BUDGET keep going, up to ICE_BUDGET_MAX, only while the expectation is still under the judging bar.
        for k in range(0, ICE_BUDGET_MAX, 500):
            if k >= ICE_BUDGET and freeze_expectation(temps, sum(len(r) for r in canals), 500) >= 4.6:
                break
            s.advance(500)
            temps.append(temp())
            if k % 2000 == 1500:        # -40 C at full: keep the colony alive through the cold (the row reads no pawn)
                heal_colonists(s, keep=keep)
            if "Ice" in terr():
                froze = k + 500
                break
    finally:                            # a crash mid-cold must not leave -40 C on the map for every later block
        for n in COLD_CONDITIONS:
            s.call("jawa/game_condition", action="end", condition=n)
    # 'thawed' = the ice count FELL (vanilla melts a radius-2.9 patch per successful roll; a full thaw of every patch is
    # many independent rolls). Polled until a melt, or until >= 4.6 melts were expected (P(none) < 1%), or the budget.
    thaw, thaw_all, melt_exp, ice_series, thaw_temps = None, None, 0.0, [], []
    if froze is not None:
        ice0 = ice_cells(terr())
        ice_series.append(len(ice0))
        for k in range(0, THAW_BUDGET_MAX, 500):
            if melt_exp >= 4.6 and thaw is None:
                break
            ncand = melt_candidates(ice_cells(terr())) if k else melt_candidates(ice0)
            s.advance(500)
            tt = temp()
            thaw_temps.append(tt)
            melt_exp += melt_expectation_step(tt, ncand, 500)
            if k % 2000 == 1500:
                heal_colonists(s, keep=keep)
            n_ice = len(ice_cells(terr()))
            ice_series.append(n_ice)
            if thaw is None and n_ice < ice_series[0]:
                thaw = k + 500
            if n_ice == 0:
                thaw_all = k + 500
                break
            if thaw is not None and k >= 12000:
                break
    after = [s.w.readout(c) if not s.mock else None for c in canal[:3]]
    same = [(a or {}).get("dl") for a in after] == [(b or {}).get("dl") for b in before]
    st, cls, why = ice_verdict(cond_ok, temps, froze, thaw, same, sum(len(r) for r in canals),
                               melt_exp=melt_exp if froze is not None else None)
    unread_dl = not s.mock and any((x or {}).get("dl") is None for x in before + after)
    if st == "PASS" and unread_dl:
        st, cls, why = "UNMEASURED", "HARNESS", "the readout litres were unread (before/after): 'unchanged' is no reading"
    if stale_ice:
        st, cls, why = "UNMEASURED", "HARNESS", "%d ThinIce squares were on the canals before the cold (an earlier B5 on this map)" % stale_ice
    elif st == "FAIL" and blind and froze is None:
        st, cls, why = "UNMEASURED", "HARNESS", "%d terrain reads of the canals came back empty: 'no ice' is no reading" % len(blind)
    s.row("B5_ice_freeze_thaw", "POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A5", st, cls,
          dict(why=why, conditions=[str(g)[:80] for g in gcs], frozeAfter=froze, thawAfter=thaw,
               coldest=min([t for t in temps if t is not None] or [None]) if any(t is not None for t in temps) else None,
               temps=temps[-6:], staleIce=stale_ice, thawAll=thaw_all, iceSeries=ice_series[:4] + ice_series[-4:],
               thawTemps=thaw_temps[-4:], expectedMelts=round(melt_exp, 2), expectedFreezes=round(freeze_expectation(temps, sum(len(r) for r in canals), 500), 2),
               before=[(b or {}).get("dl") for b in before], after=[(a or {}).get("dl") for a in after]), "B5")
    restore_after_weather(s, "B5")


def flood_verdict(started, reached, receded, same):
    """B6_flood_canal_kept -> (status, class, why). UNMEASURED/SITE unless the flood started AND laid floodwater beside
    the canal (vanilla floods never enter a water square: Flood.CanFloodPotentiallySpreadInto refuses IsWater, so
    'reached' = floodwater on the canal's banks) AND receded; then PASS when every canal square reads as before."""
    if not started:
        return "UNMEASURED", "SITE", "the flood weather did not start"
    if not reached:
        return "UNMEASURED", "SITE", "no floodwater beside the canal"
    if not receded:
        return "UNMEASURED", "SITE", "the floodwater had not receded at the budget"
    return ("PASS", "MOD", "") if same else ("FAIL", "MOD", "canal squares changed across the flood")


def b6_flood(s):
    """POND_DEPTH A6 ("a seasonal or torrential flood over a wet canal leaves the canal's water and floor correct"):
    TorrentialRain (Odyssey WeatherDef) locked by jawa/weather_set; WeatherWorker_TorrentialRain.OnWeatherStart spawns
    a TorrentialRainFlood, whose GetInitialCells seeds from EVERY unroofed freshwater water body's bank squares -- the
    dug canal itself is one (dug water is a vanilla water body, engine doc 2.2) -- so the flood starts AT the canal.
    Pass 1 used SeasonalFlooding: SeasonalFlood seeds only at river banks and spreads <= 12 squares from them, so it can
    never reach a staged canal (and does nothing on a riverless map). StartDelayTicks 4000, then floodwater (*Flood*
    terrain, temp layer) is polled on the banks; weather back to Clear destroys the flood (OnWeatherEnd) and its squares
    recede 2000+ ticks later; recession polled; the canal's cells compared before/after (flood_verdict)."""
    rect = s.zones["flood"]
    x, z, _w, _h = rect
    clear_zone(s, "flood")
    canal = [(x + 2 + i, z + 4) for i in range(12)]
    for c in canal:
        s.dig(c, 2, 1)
    s.advance(300)
    before = s.w.cells(canal)[0] if not s.mock else {}
    w0 = s.call("jawa/weather_get")
    # pass 2 (2026-10-19, HARNESS, presumed): 8+ canal squares "changed across the flood" -- a torrential rain also FILLS
    # open dug squares (rainFillsExcavationsEnabled, the mod's design, proven by its own rows), which this row is not
    # about. Rain fill off for the row (restored in finally); the changed squares keep their before/after values.
    rain_fill_was = s.sget("rainFillsExcavationsEnabled")
    rain_off = (s.sset("rainFillsExcavationsEnabled", False) or {}).get("success") is not False
    ws = s.call("jawa/weather_set", weather=FLOOD_WEATHER, lockWeather=True)
    started = bool(ws.get("success")) and ws.get("after") == FLOOD_WEATHER

    def flood_ops():
        return str(s.call("jawa/get_terrain_batch", rects="%d,%d,16,3" % (x + 1, z + 3)).get("ops") or "")
    reached, reached_at = False, None
    try:
        if started:
            for k in range(0, 14000, 500):
                s.advance(500)
                if "Flood" in flood_ops():
                    reached, reached_at = True, k + 500
                    break
            if reached:
                s.advance(1000)                     # let it lie a while over the banks
    finally:
        # back to B0's locked Clear (also after a crash: a locked torrent would flood every later block): the old lock
        # ends, TransitionTo(Clear) runs TorrentialRain.OnWeatherEnd = the flood is destroyed
        s.call("jawa/weather_set", weather="Clear", lockWeather=True)
        s.sset("rainFillsExcavationsEnabled", rain_fill_was if rain_fill_was is not None else True)   # Clear now: no rain
    receded, gone_at = False, None
    if reached:
        for k in range(0, 12000, 500):
            s.advance(500)
            if "Flood" not in flood_ops():
                receded, gone_at = True, k + 500
                break
    after = s.w.cells(canal)[0] if not s.mock else {}
    st, cls, why = flood_verdict(started, reached, receded, before == after)
    if not s.mock and (not before or not after):       # {} == {} was "every canal square reads as before"
        st, cls, why = "UNMEASURED", "HARNESS", "the canal cells were unread (before %d, after %d)" % (len(before or {}), len(after or {}))
    elif st == "FAIL" and not rain_off:
        st, cls, why = "UNMEASURED", "SITE", "rain fill could not be switched off for the row: the squares may have filled by design"
    s.row("B6_flood_canal_kept", "POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A6", st, cls,
          dict(why=why, weather=str(ws)[:120], weatherBefore=(w0 or {}).get("weather"), floodReachedAfter=reached_at,
               recededAfter=gone_at, changed=[c for c in before if before.get(c) != after.get(c)][:8],
               changedValues=[[str(before.get(c))[:80], str(after.get(c))[:80]] for c in before if before.get(c) != after.get(c)][:4],
               rainFillWas=rain_fill_was), "B6")
    restore_after_weather(s, "B6")


# ============================================================================ B7 one save + one load
def snapshot(s):
    snap = {}
    for n in ("access", "digdepth", "covers"):
        x, z, w, h = s.zones[n]
        r = s.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=True, includeTerrain=False)
        snap["dig_" + n] = r.get("cells") or r.get("rows") or r.get("result")
        ok, txt = s.proof(NSP, "ProofClimb", "%d,%d;3" % (x + 2, z + 2))
        # gen/built/rebuilds are the pocket grid's own rebuild COUNTERS: a load starts them again, so they are not
        # pocket state (live 2026-10-19: every pocket row 'differed' on gen=1421 -> 163 alone)
        snap["pocket_" + n] = re.sub(r"\b(gen|built|rebuilds)=\d+", "", txt).strip() if ok else None
    x, z, _w, _h = s.zones["digdepth"]
    ok, txt = s.proof(NSP, "ProofReadout", "%d,%d" % (x + 2, z + 2))
    snap["readout_8m"] = txt if ok else None      # an error text on both sides compared equal (a vacuous PASS)
    for f in ("pitGuardrailEnabled", "fallDeathEnabled", "pitRoomMinDepthMetres"):
        snap["set_" + f] = s.sget(f)
    return snap


def reload_verdict(ok_io, blind, diff):
    """B7 -> status: UNMEASURED when the save/load failed or any snapshot key was unread on either side; else PASS when
    nothing differs."""
    if not ok_io or blind:
        return "UNMEASURED"
    return "PASS" if not diff else "FAIL"


RELOAD_SETTLE_TICKS = 120      # > RM_PocketGrid.RebuildMinTicks (60): the pocket grid has rebuilt at least once since the load


def b7_reload(s):
    before = snapshot(s)
    name = "RM_live_session_reload_%s" % time.strftime("%Y%m%d_%H%M%S")
    sv = s.call("rimworld/save_game", saveName=name)
    if not s.mock:
        try:
            import validation_core as V
            V._wait_saved(name)
        except Exception as ex:  # noqa: BLE001
            s.notes.append("wait_saved: %s" % ex)
    ld = s.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000)
    if not s.mock:
        try:
            import validation_core as V
            V._wait_playing(s.w.B, leave_s=0)
        except Exception as ex:  # noqa: BLE001
            s.notes.append("wait_playing: %s" % ex)
    after = snapshot(s)
    diff = sorted(k for k in before if before.get(k) != after.get(k))
    # a key unread on EITHER side is no comparison: None == None made the pocket/setting rows PASS with nothing read
    blind = sorted(k for k in before if before.get(k) is None or after.get(k) is None)
    ok_io = (sv.get("success") is True and ld.get("success") is True) or (s.mock and sv.get("success") is not False)
    st = reload_verdict(ok_io, blind, diff)
    # RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS: runs 20261018T232207 / T233414 failed on pocket_covers alone and
    # kept no strings. Keep both sides of every differing key, and one SETTLED re-read (> RM_PocketGrid.RebuildMinTicks
    # = 60 later): a key that agrees once settled was a stale grid read straight after the load (a transient), one that
    # still differs is a real save/load difference. The verdict stays on the immediate read; the settled one is evidence.
    pairs = {k: dict(before=str(before.get(k))[:300], after=str(after.get(k))[:300]) for k in diff}
    settled_same = []
    if diff and ok_io:
        s.advance(RELOAD_SETTLE_TICKS)
        later = snapshot(s)
        for k in diff:
            pairs[k]["settled"] = str(later.get(k))[:300]
        settled_same = [k for k in diff if later.get(k) == before.get(k)]
    for item, cid in (("PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT", "A3"), ("PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP", "A2"),
                      ("PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "save_reload_pockets_identical")):
        s.row("B7_reload_%s" % cid[:24], item, cid, st, "MOD" if st != "UNMEASURED" else "HARNESS",
              dict(save=name, differs=diff, unread=blind, pairs=pairs, settledSame=settled_same,
                   settleTicks=RELOAD_SETTLE_TICKS if diff else 0), "B7")
    s.row("B7_pipe_look_survives", "HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A2", "UNMEASURED", "OWED",
          dict(why="needs a colonist-built styled pipe (blueprint->frame->building); objects_sheet.choose_look stages "
                   "the look, the build half rides B4 once a builder row exists"), "B7")
    if s.pawns.get("rescue"):
        r = s.climb(s.pawns["rescue"])
        s.row("B7_rescued_out_of_pit", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A4",
              "UNMEASURED" if not r else ("PASS" if r.get("depth") == 0 else "FAIL"), "MOD" if r else "HARNESS", dict(downed=r), "B7")


# ============================================================================ B9 owner review
def b9_owner(s):
    """Owner_review_stage's own main() on the owner zone (it clears it, stages ladders/spikes/gates/shallows/sprinklers/
    hoses, shoots, saves ONE save), after the pit-access props he must see in situ are staged east of it."""
    x, z, _w, _h = s.zones["props"]
    import fw_walk_common as FC
    clear_zone(s, "props")
    s.pit((x + 1, z + 1), 3, 3, 4)
    s.pit((x + 8, z + 1), 3, 3, 1)
    if not s.mock:
        FC.place(s.w, "RM_LadderPortable", (x + 2, z + 3), rot=0)      # leans diagonally on a 2 m wall
        FC.place(s.w, "RM_LadderPortable", (x + 9, z + 3), rot=0)      # too short a drop: lies flat
        FC.place(s.w, "RM_ClimbingGear", (x + 15, z + 2))
    s.row("B9_props_staged", "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS", "A5", "UNMEASURED", "OWED",
          dict(rect=s.zones["props"], why="his look: portable ladder diagonal vs flat, climbing gear icon"), "B9", eyes=True)
    s.call("jawa/kill_hostiles")
    heal_colonists(s)
    feed_colonists(s)
    import owner_review_stage as ORS
    ox, oz = s.zones["owner"][0] + 3, s.zones["owner"][1] + 6
    argv = ["--origin", "%d,%d" % (ox, oz), "--only", "ladders,spikes,gates,shallows,sprinklers,hoses,bars_joint,bars_dry,bars_trench,bars_access,bars_bridges"]
    if s.mock:
        argv.append("--mock")
    if s.args.no_owner_save:
        argv.append("--no-save")
    else:
        argv += ["--save-name", "FLOWWORKS_OWNER_REVIEW_%s" % time.strftime("%Y%m%d_%H%M")]
    rc = ORS.main(argv)
    for item, cid in (("FLOWWORKS_LADDER_RAISE_LOWER_1", "A2"), ("POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD", "A8"),
                      ("SPRINKLER_HEADS_BUILD_PUMP_REQUIRED", "looks"), ("HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME", "walk"),
                      ("HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD", "A4"), ("LIQUID_LEDGER_BUILD_NO_UNIT_LOST", "A9"),
                      ("PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT", "A4")):
        s.row("B9_staged_%s_%s" % (item.split("_")[0].lower(), cid), item, cid, "UNMEASURED", "OWED",
              dict(stageExit=rc, why="his eyes: open the owner-review save"), "B9", eyes=True)


# ============================================================================ subprocess steps
WHOLE_BODY_ILLS = ("Hypothermia", "Heatstroke", "BloodLoss", "Malnutrition", "RM_Dehydration")
PART_HURTS = ("Frostbite", "Cut", "Scratch", "Bite", "Bruise", "Crack", "Crush", "Stab", "Gunshot", "Burn", "Shredded",
              "SurgicalCut", "Blunt", "Bomb")


def heal_plan(hediffs_list):
    """[(action, hediff)] that heal one colonist from a pawn_get hediff list: each whole-body ill removed by name (once
    per instance), plus ONE 'restore Torso' when any part injury is listed (RestorePart is recursive: Torso is the
    human root part, so it clears every part's wounds; it never touches whole-body hediffs, hence the removes)."""
    plan, part_hurt = [], False
    for h in hediffs_list or []:
        if not isinstance(h, dict):
            continue
        d = str(h.get("def") or h.get("defName") or "")
        if d in WHOLE_BODY_ILLS:
            plan.append(("remove", d))
        elif h.get("part") and any(k in d for k in PART_HURTS):
            part_hurt = True
    if part_hurt:
        plan.append(("restore", "Torso"))
    return plan


def heal_colonists(s, keep=()):
    """Heal every living colonist (wounds, frostbite, hypothermia, blood loss) before a block that is not about health:
    after B8's raid a bleeding colonist trips the governor's 'hurt' latch and kills the owner staging (live 2026-10-19,
    B9), and B5's -40 C leaves hypothermia for every later block. The old call (pawn_health restore with no bodyPart)
    was REFUSED every time ("Give a bodyPart to restore."), so nobody was ever healed. keep = pawn ids left as they are
    (B4's downed rescue colonist, whose state B7 reads). Returns (healed, refused)."""
    if s.mock:
        return 0, []
    keep = {str(k).replace("Thing_", "") for k in keep if k}
    healed, refused = 0, []
    for c in (s.call("rimworld/list_colonists") or {}).get("colonists") or []:
        pid = c.get("pawnId")
        if c.get("dead") or not pid or str(pid).replace("Thing_", "") in keep:
            continue
        snap = s.call("jawa/pawn_get", pawn=pid)
        p = ((snap.get("pawns") or [snap]) or [{}])[0] if isinstance(snap, dict) else {}
        plan = heal_plan(p.get("hediffs") if isinstance(p, dict) else None)
        for act, what in plan:
            if act == "remove":
                r = s.call("jawa/pawn_health", pawn=pid, action="remove", hediff=what)
            else:
                r = s.call("jawa/pawn_health", pawn=pid, action="restore", bodyPart=what, confirmDestructive=True)
            if r.get("success") is not True:
                refused.append("%s %s %s: %s" % (pid, act, what, str(r.get("error") or r.get("message") or r)[:80]))
        healed += 1 if plan else 0
    if refused:
        s.notes.append("heal_colonists refused: %s" % refused[:6])
    return healed, refused


def restore_after_weather(s, label):
    """After a map-wide weather block (B5's -40 C, B6's flood): heal and feed every colonist except the B4 rescue pawn,
    and put B0's locked Clear back, so the next block does not start on a hypothermic or flooded colony."""
    healed, refused = heal_colonists(s, keep=(s.pawns.get("rescue"),))
    fed = feed_colonists(s)
    ws = s.call("jawa/weather_set", weather="Clear", lockWeather=True)
    s.timing.setdefault("restore", []).append(dict(after=label, healed=healed, refused=len(refused), fed=fed,
                                                   weather=ws.get("after")))


def feed_colonists(s):
    """Top up Food and Rest on every colonist: an unfed quicktest colony reaches Starving inside a session and the
    governor then stops every sub-script's clock (live 2026-10-19: liquid_checks L2-L6 and proof_hose realflow UNMEASURED)."""
    if s.mock:
        return 0
    n = 0
    for c in (s.call("rimworld/list_colonists") or {}).get("colonists") or []:
        if c.get("dead") or not c.get("pawnId"):
            continue
        for need in ("Food", "Rest"):
            s.call("jawa/pawn_need", pawn=c["pawnId"], action="need", need=need, level=1.0)
        n += 1
    return n


def run_sub(s, step):
    bid, script, argv, mapping = step
    path = os.path.join(HERE, script)
    out = os.path.join(s.out_dir, os.path.splitext(script)[0] + "_result.json")
    log = os.path.join(s.out_dir, os.path.splitext(script)[0] + ".log")
    fill = []
    for a in argv:
        if a == "{out}":
            fill.append(out)
        elif a == "{log}":
            fill.append(s.args.player_log or "")
        elif a.startswith("{origin:"):
            zx, zz, _w, _h = s.zones[a[8:-1]]
            fill.append("%d,%d" % (zx, zz))
        else:
            fill.append(a)
    if "--log" in fill and not fill[fill.index("--log") + 1]:
        i = fill.index("--log")
        fill = fill[:i] + fill[i + 2:]
    if s.mock:
        if script == "validation_v2.py":
            fill = ["--mock", "--out", out]
        else:
            s.row("%s_%s" % (bid, script[:-3]), "-", "-", "SKIP", "HARNESS", dict(why="no --mock in %s; live only" % script, argv=fill), bid)
            return
    # re-calm before EVERY script, not once per run: live 2026-10-19 two Mech_Pikeman arrived after B0's sweep and
    # GovernorStop killed climb_proof and sprinkler_live (SITE, not the mod)
    s.call("jawa/kill_hostiles")
    s.call("jawa/incident_queue_clear")
    feed_colonists(s)
    if os.path.exists(out):
        os.remove(out)                      # a crash before the script writes must not re-read an earlier run's rows
    s.say("  RUN %s %s" % (script, " ".join(fill)))
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as lf:
        p = subprocess.Popen([sys.executable, path] + fill, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, encoding="utf-8", errors="replace")
        last, tail = time.time(), ""
        for line in p.stdout:
            lf.write(line)
            tail = line if line.startswith(("MOCK:", "LIVE:")) else tail
            if time.time() - last > 30:                       # a heartbeat for the 600 s silence watchdog
                s.say("    [%s %.0fs] %s" % (script, time.time() - t0, line.strip()[:120]))
                last = time.time()
        rc = p.wait()
    s.timing[script] = round(time.time() - t0, 1)
    rows = []
    try:
        with open(out, encoding="utf-8") as f:
            rows = json.load(f).get("rows") or []
    except (OSError, ValueError):
        pass
    if not rows and s.mock and tail:            # validation_v2 --mock prints its verdict line and writes no JSON
        it, cid = mapping.get("*", ("-", "-"))
        s.row("%s_%s_mock" % (bid, script[:-3]), it, cid, "SKIP", "HARNESS", dict(mockVerdict=tail.strip()[:200],
              why="a mock verdict proves the script's paths, never the game"), bid)
        return
    if not rows:
        s.row("%s_%s" % (bid, script[:-3]), "-", "-", "UNMEASURED", "HARNESS", dict(rc=rc, why="no result rows", log=log), bid)
        return
    for r in rows:
        rid = str(r.get("id") or r.get("row") or "?")
        st = str(r.get("status") or ("PASS" if r.get("ok") is True else "FAIL" if r.get("ok") is False else "UNMEASURED")).upper()
        item, cid = next(((it, c) for k, (it, c) in mapping.items() if k != "*" and rid.startswith(k)), mapping.get("*", ("-", "-")))
        s.row("%s:%s" % (script[:-3], rid), item, cid, st, str(r.get("class") or r.get("cls") or "-"), dict(rc=rc, src=out), bid)


# ============================================================================ verify lines + summary
def verdicts(rows):
    """{(item, crit): (result, [row ids], [evidence])}: pass when every measured row passed and none is UNMEASURED;
    fail when any FAILed; partial when some passed and some could not ask. OWED/SKIP rows give no verdict."""
    by = {}
    for r in rows:
        if r["item"] in ("-", None) or r["cls"] == "OWED" or r["status"] == "SKIP":
            continue
        by.setdefault((r["item"], r["criterion"]), []).append(r)
    out = {}
    for k, rs in by.items():
        sts = [r["status"] for r in rs]
        if "FAIL" in sts:
            res = "fail"
        elif all(x == "PASS" for x in sts):
            res = "pass"
        elif "PASS" in sts:
            res = "partial"
        else:
            continue
        out[k] = (res, [r["id"] for r in rs])
    return out


def write_verify_lines(s):
    p = os.path.join(s.out_dir, "verify_lines.txt")
    ev = os.path.relpath(os.path.join(s.out_dir, "session.json"), REPO)
    lines = []
    if s.env.get("partial"):
        lines.append("# PARTIAL run (--only/--skip): never recordable as the session result; each line stands only for its own rows")
    for (item, cid), (res, ids) in sorted(verdicts(s.rows).items()):
        c = (" --criterion %s" % cid) if cid and cid[0] in "AT" and cid[1:].isdigit() else ""
        lines.append('python3 src/RimMandrake/rimflow/cli.py verify %s%s --result %s --config %s --level L2 --evidence %s '
                     '--why "live_session rows %s"' % (item, c, res, s.env.get("config", "UNMEASURED"), ev, ",".join(ids)[:200]))
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return p, len(lines)


def budget(sel):
    """ESTIMATED session length from the catalog: game ticks at the measured 60 t/s step rate plus wall seconds."""
    by = {}
    for c in C:
        if c["block"] in sel:
            b = by.setdefault(c["block"], [0, 0])
            if c["block"] == "B4":                 # ONE shared clock: the longest wait, not the sum
                b[0] = max(b[0], c["ticks"])
                b[1] += 2 * CALL_S * 10            # ~10 calls per row of setup and reads
            else:
                b[0] += c["ticks"]
                b[1] += c["wall"]
    if "B4" in by:
        by["B4"][1] += by["B4"][0] / TPS_STEP
    return by


def print_plan(s, sel):
    s.say("LIVE SESSION PLAN  zones on %dx%d:" % s.size)
    for n, r in sorted(s.zones.items(), key=lambda kv: (kv[1][1], kv[1][0])):
        s.say("  zone %-10s %s" % (n, r))
    by = budget(sel)
    total = 0.0
    for b in BLOCKS:
        if b["id"] not in sel:
            continue
        t, w = by.get(b["id"], (0, 0))
        total += w
        s.say("%-4s %-82s ~%5d ticks ~%4.0f s (ESTIMATED)" % (b["id"], b["title"][:82], t, w))
        for c in C:
            if c["block"] == b["id"]:
                s.say("       %-44s %-22s %s%s" % (c["item"][:44], c["crit"][:22], c["source"][:70], "  [OWNER EYES]" if c["eyes"] else ""))
    s.say("OUT OF THIS LOAD: " + ", ".join(sorted({c["item"] for c in C if c["block"] in ("OUT", "LATER", "P10")})))
    s.say("ESTIMATED wall for the selected blocks: %.0f s (+ one cold load, MEASURED 44-70 s, + one quicktest map, 2-8 s)" % total)
    return total


# ============================================================================ driver
ORDER = ("B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--list", action="store_true", help="print the catalog as JSON and exit")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="")
    ap.add_argument("--frame-budget-ms", type=float, default=150.0,
                    help="safe_advance main-thread ms per frame (tool default 40; 0 = Walk.ticks / clockgate path)")
    ap.add_argument("--player-log", default="", help="this load's Player.log copy (thirst T1/T7)")
    ap.add_argument("--no-owner-save", action="store_true")
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    if a.list:
        print(json.dumps(dict(blocks=BLOCKS, catalog=C), indent=1))
        return 0
    sel = [b for b in ORDER if (not a.only or b in a.only.split(",")) and b not in a.skip.split(",")]
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out_dir = a.out_dir or os.path.join(REPO, "Transient", "live_session", ("mock_" if a.mock else "dry_" if a.dry_run else "") + stamp)
    os.makedirs(out_dir, exist_ok=True)
    s = Session(a, out_dir)
    s.env["partial"] = bool(a.only or a.skip)
    print_plan(s, sel)
    if a.dry_run:
        s.say("DRY RUN: no bridge touched.")
        return 0
    if not a.mock:
        # live 2026-10-19: companion_profile.json lapsed at 06:00Z mid-run and every test-only tool (static_call,
        # job_probe, log sentinel) came back REFUSED in the CAMPAIGN profile; refuse to start inside the run's budget
        md = os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck")
        if md not in sys.path:
            sys.path.insert(0, md)
        import runner as MR
        try:
            MR.ensure_test_profile(min_minutes=90)
        except RuntimeError as ex:
            s.say("REFUSING TO START: %s" % ex)
            return 2
    import fw_walk_common as FC
    walk_args = argparse.Namespace(mock=a.mock, no_shots=True, mock_fail=None)
    s.w = FC.make_walk(walk_args, os.path.join(out_dir, "walk"))
    t_start = time.time()
    steps = dict(B0=[b0_preflight], B2=[b2_settings_dialog, b2_tank_tall, b2_readouts], B4=[b4_shared], B5=[b5_cold_snap],
                 B6=[b6_flood], B7=[b7_reload], B9=[b9_owner])
    for bid in sel:
        s.say("=== %s %s  (t+%.0fs, tick %s)" % (bid, next(b["title"] for b in BLOCKS if b["id"] == bid), time.time() - t_start, s.now()))
        w0 = time.time()
        for fn in steps.get(bid, []):
            try:
                fn(s)
            except Exception as ex:  # noqa: BLE001 - recorded, the session goes on
                s.say(traceback.format_exc())
                s.row("%s_%s_crashed" % (bid, fn.__name__), "-", "-", "UNMEASURED", "HARNESS", dict(error=str(ex)), bid)
        for step in SUBS:
            if step[0] == bid:
                try:
                    run_sub(s, step)
                except Exception as ex:  # noqa: BLE001
                    s.row("%s_%s_crashed" % (bid, step[1]), "-", "-", "UNMEASURED", "HARNESS", dict(error=str(ex)), bid)
        s.timing[bid] = round(time.time() - w0, 1)
    s.timing["total_s"] = round(time.time() - t_start, 1)
    s.save()
    p, n = write_verify_lines(s)
    counts = {}
    for r in s.rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    s.say("DONE %s rows %s  verify lines %d -> %s  session %s" % (len(s.rows), counts, n, os.path.relpath(p, REPO),
                                                                  os.path.relpath(os.path.join(out_dir, "session.json"), REPO)))
    eyes = sorted({(r["item"], r["criterion"]) for r in s.rows if r.get("eyes")})
    s.say("OWNER EYES (%d): %s" % (len(eyes), "; ".join("%s %s" % e for e in eyes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
