"""human_review.py -- FlowWorks capability review sheet (owner, 2026-10-05).

    python3 src/RimMandrake/FlowWorks/human_review.py            # writes northstar/review/FlowWorks_review.html
    python3 src/RimMandrake/FlowWorks/human_review.py --out X.html --result R.json

Owner, 2026-10-05 (typed): *"make a dense, comprehensive, efficient human review sheet based on the intended
functionality in flow works even if it's not built yet so we can see what's there, what's working or not, and what
remains to be built easily."*

One row per INTENDED capability (the CAPS table below, data). Nothing on a row is a hand-typed verdict:
  * BUILT is DERIVED from declared probes (a class / def / setting / texture / file that must exist on disk);
  * PROVEN-LIVE is DERIVED from a PASS row in the newest northstar/validation_v2_result_*.json (+ any proof_*.json),
    mapped to MECHANISM rows only (never the harness rows L1/L2/L4, SITE*, A0, E9, Z; L3_defs_live is a MOD row);
  * the owning item's state is read from the rimflow ledger at generation time, and the "what remains to build"
    list is derived from it (open items only).
Status: PROVEN-LIVE (a mapped row PASSed) > BUILT-UNPROVEN (every probe present) > PARTIAL (some) > NOT BUILT (none).

Why this file name and folder: modcheck's mod_hash skips `human_review.py` and `northstar/`, so neither this script
nor its sheet (northstar/review/) moves FlowWorks' recorded GREEN hash. DEPLOY_HOLD keeps northstar/review/ out of
the game copy. The decisions file is written ONCE (when absent) and never overwritten -- the sidecar owns it after.
"""
import argparse
import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NSDIR = os.path.join(HERE, "northstar")
REVIEW = os.path.join(NSDIR, "review")
DEFAULT_OUT = os.path.join(REVIEW, "FlowWorks_review.html")
DEC_NAME = "FlowWorks_review.decisions.json"
TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
SETTINGS_CS = os.path.join(HERE, "Source", "RimMandrakeFlowWorksMod.cs")
CANON = os.path.join(REPO, "design", "RimStarWars", "canon_references")
SELF_FILES = ("human_review.py", "selftest_human_review.py")   # never let a probe match its own declaration
HARNESS_PREFIXES = ("L0", "L1", "L2", "L4", "L5", "SITE", "A0", "E9", "Z")   # harness rows: never capability evidence
# (L3_defs_live is a MOD row since the 2026-10-05 densification: the live path costs of the four channel defs)

STATUSES = ("PROVEN-LIVE", "BUILT-UNPROVEN", "PARTIAL", "NOT BUILT")
COLOR = {"PROVEN-LIVE": "#5ac37f", "BUILT-UNPROVEN": "#6aa6e8", "PARTIAL": "#e8b64c", "NOT BUILT": "#e06c6c"}
OPEN_STATES = ("proposed", "ready", "doing")

# Screenshots of the live 2026-10-05 run (Transient/belt_bridge5_review, scene groups) and one owner/design
# reference image cited by PIT_SUPERDEEP_COLLAPSE_1 (ruling 33). Copied (downscaled JPEG) into review/shots/ so the
# sheet survives Transient's ~14-day shelf life.
SHOTS = {
    "S_ladder": "Transient/belt_bridge5_review/S_ladder.png",
    "E2_flow": "Transient/belt_bridge5_review/E2_flow.png",
    "E3_E4": "Transient/belt_bridge5_review/E3_E4.png",
    "E5_sinks": "Transient/belt_bridge5_review/E5_sinks.png",
    "J_jobs": "Transient/belt_bridge5_review/J_jobs.png",
    "P_pits": "Transient/belt_bridge5_review/P_pits.png",
    "X_promoted": "Transient/belt_bridge5_review/X_promoted.png",
    "REF_quarry": "design/RimMandrake/references/quarry_pit_perspective_2026-09-16.jpg",
}

GROUPS = {
    "A": "A · Digging & depth",
    "B": "B · Fill & flow engine",
    "C": "C · Reservoirs: stock, budget, recession, rain, sinks",
    "D": "D · Fluids: viscosity, identity, roster",
    "E": "E · Fire, ignition, corrosion",
    "F": "F · Pits: superdeep capture & escape",
    "G": "G · Pits: prison room, capture down, temperature",
    "H": "H · Pit hardware: ladder, spikes, cover, fill effects",
    "I": "I · Doors: sluice & security grate",
    "J": "J · Pawn height draw & excavation art",
    "K": "K · Bottles, tanks, drilling, industry",
    "L": "L · Shores, rivers, weirs, swale, irrigation",
    "M": "M · Quarry digging",
    "N": "N · Settings, proofs, shipping",
}

BP = "FLOWWORKS_BUILD_PROGRAM_1"
# ------------------------------------------------------------------------------------------------ THE CAPABILITY TABLE
# id, group letter, label, intended behaviour (what it DOES), owning item, probes, live rows, north-star bars, shots,
# src (where the intent is written down).
# probe grammar: cs:RX (FlowWorks Source/**.cs) · xml:RX (FlowWorks Defs+Patches) · set:NAME (Mod Settings field) ·
#   tex:RX (FlowWorks Textures relpath) · file:REPO_REL · rx:REPO_REL_DIR:RX (any text file below) · "!" prefix negates.
CAPS = [
    # ---- A digging & depth
    dict(id="A01", g="A", label="Dig-canal order: a colonist carves a channel", item="FLOWWORKS_BUILD_PROGRAM_1",
         effect="Designate soil; a colonist digs it to D=1 (RM_Channel_Empty). Refuses edifices, water, existing channel.",
         probes=["cs:class Designator_DigCanal", "cs:class WorkGiver_DigCanal", "cs:class JobDriver_DigCanal"],
         rows=["E8_player_dig", "J_workgiver_selection", "J_orders_accepted"], shots=["J_jobs"], src="Build program Ph2"),
    dict(id="A02", g="A", label="Four dug depths D1..D4 (shallow/mid/deep/SUPERDEEP)", item=BP,
         effect="Every excavated cell carries depth D 0-4; each level is its own terrain (Empty/Mid/Deep/Superdeep).",
         probes=["xml:defName>RM_Channel_Empty<", "xml:defName>RM_Channel_Mid<", "xml:defName>RM_Channel_Deep<",
                 "xml:defName>RM_Channel_Superdeep<"], rows=["S1_dig_ladder"], shots=["S_ladder"], src="Ruling 19"),
    dict(id="A03", g="A", label="Deepen an existing channel (dig to depth)", item=BP,
         effect="Re-designating a dug cell deepens it one level; refused at SUPERDEEP (as far down as it goes).",
         probes=["set:digToDepthEnabled"], rows=["S6_digToDepth_gate", "S1n_superdeep_is_max"], src="Build program Ph2"),
    dict(id="A04", g="A", label="Depth + fill grid saved with the map", item=BP,
         effect="Per-map D and F grids live on one MapComponent and survive save/load; F is clamped 0 <= F <= D.",
         probes=["cs:class RM_MapComponent_Excavation", "cs:Scribe"], rows=["S2_fill_clamp"], src="Build program Ph2"),
    dict(id="A05", g="A", label="Fill-in order: lower a channel back toward ground", item="CANAL_FILL_IN_DISPLACEMENT_1",
         effect="A fill-in designation lowers D; liquid in the cell is pushed back into the network (see B12).",
         probes=["cs:class Designator_FillInCanal", "cs:class WorkGiver_FillInCanal", "cs:class JobDriver_FillInCanal"],
         rows=["E7a_fillin_displaces"], shots=["J_jobs"], src="Build program Ph2"),
    dict(id="A06", g="A", label="Dry depth slows movement (30/45/80, superdeep impassable)", item=BP,
         effect="Dry path cost climbs with depth so an unfilled trench is a real barrier (ruling 17).",
         probes=["xml:<pathCost>30</pathCost>", "xml:<pathCost>45</pathCost>", "xml:<pathCost>80</pathCost>"],
         rows=["L3_defs_live"], bars=["canal_dry_reads_as_obstacle"], src="Ruling 17 / Ph5"),
    dict(id="A07", g="A", label="Flooded is always slower than dry (depth x fill cost matrix)", item="DEPTH_FILL_COST_MATRIX_1",
         effect="Each fluid has a cost per depth x fill tier, strictly worse flooded than the same depth dry.",
         probes=["xml:defName>RM_Fill_Water_Half", "cs:pathCost|PathCost"], bars=["filled_excavation_reads_as_obstacle"],
         src="Collapse [E]"),
    dict(id="A08", g="A", label="A pit is only a D=4 cell (no holder Thing, no old pit building)", item="SUPERDEEP_HOLDER_RETIRE_1",
         effect="Trapping is a grid rule on a spawned pawn; the old Building_OpenPit / RM_SuperdeepPit model is gone.",
         probes=["cs:class RM_SuperdeepTrap", "!cs:class Building_OpenPit"], rows=["S1p_pit_is_grid_only"],
         src="Collapse ruling"),
    # ---- B fill & flow
    dict(id="B01", g="B", label="Flow runs on a pulse, never per tick", item=BP,
         effect="Liquid moves only at pulse boundaries (default every 250 ticks); the cadence is a setting.",
         probes=["set:pulseIntervalTicks"], rows=["E1a_cadence_shipped", "E1c_cadence_real_scheduler", "A_pulse_contract"],
         src="Framework pillar 2"),
    dict(id="B02", g="B", label="Pulse interval cannot be set below 60 ticks", item=BP,
         effect="A too-fast pulse setting is clamped to 60 so the engine cannot become a per-tick sim.",
         probes=["set:pulseIntervalTicks"], rows=["E1b_pulse_clamp"], src="Build program Ph3"),
    dict(id="B03", g="B", label="Sort + overflow: a canal fills from its source in every direction", item="FLOWWORKS_CHANNEL_OSCILLATION_1",
         effect="Deepest-first pour to F=D, full cells overflow into neighbours; E/N/S/W channels all fill, bottom-up.",
         probes=["cs:PickDonor"], rows=["E2_east_A", "E2_north", "E2_south", "E2_west", "E2_channels_fill_every_direction",
                                        "A_global_vs_oracle", "G_every_cell_vs_oracle"],
         bars=["canal_fill_spreads_along_itself", "canal_fill_front_watchable"], shots=["E2_flow"], src="Build program Ph3"),
    dict(id="B04", g="B", label="Two channels off one source both fill", item="FLOWWORKS_SHARED_SOURCE_STALL_1",
         effect="A source cell shared by several channels feeds all of them (the old shared-visited stall is fixed).",
         probes=["cs:PickDonor"], rows=["E2s_shared_source_oracle", "E2s_shared_source_both_fill", "G_every_cell_vs_oracle"], src="Bug item"),
    dict(id="B05", g="B", label="Flow is deterministic (twins and re-runs identical)", item=BP,
         effect="Identical channels and a re-run produce the same pulse-by-pulse fill vectors.",
         probes=["cs:class RM_StockMath"], rows=["E2_twins_identical", "E2_rerun_determinism", "R_global_vs_oracle", "G_every_cell_vs_oracle"],
         src="Build program verify"),
    dict(id="B06", g="B", label="Liquid stays in the dug channel", item=BP,
         effect="Fill never spreads onto undug ground beside a channel; confinement is a setting (default ON).",
         probes=["set:channelConfinementEnabled", "cs:CanLiquidEnter"], rows=["E2_dry_ring"],
         bars=["canal_holds_only_the_channel", "never_liquid_on_open_ground"], shots=["E2_flow"], src="Owner experience"),
    dict(id="B07", g="B", label="Master switch: depth engine off freezes all flow", item=BP,
         effect="With the engine off no cell moves past its due pulse; turning it back on resumes on schedule.",
         probes=["set:depthEngineEnabled"], rows=["E4_engine_off", "E4_engine_on_scheduled"], shots=["E3_E4"],
         src="Settings rule 2026-09-12"),
    dict(id="B08", g="B", label="Partial fill tiers: trace / half / brim / superdeep per fluid", item=BP,
         effect="A part-filled canal draws a lighter tier than a full one; four fill terrains per fluid (ruling 5).",
         probes=["xml:defName>RM_Fill_Water_Trace", "xml:defName>RM_Fill_Water_Half", "xml:defName>RM_Fill_Water_Brim"],
         bars=["canal_partial_fill_distinct", "fill_tier_legible"], shots=["S_ladder"], src="Ruling 5"),
    dict(id="B09", g="B", label="Canal reads as the same liquid as its reservoir", item=BP,
         effect="A filled canal draws the fill ladder of the fluid it came from (water from water, tar from tar).",
         probes=["xml:defName>RM_Fill_Tar_Brim", "cs:fillTerrain|FillTerrain"], rows=["X6_two_fluids_distinct"],
         bars=["canal_reads_as_same_liquid_as_reservoir"], shots=["X_promoted"], src="Owner experience"),
    dict(id="B10", g="B", label="Fill-in pushes liquid back (conserved)", item="CANAL_FILL_IN_DISPLACEMENT_1",
         effect="Filling a wet cell credits its liquid to connected channel/source cells with room; nothing vanishes.",
         probes=["set:fillInDisplacementEnabled"], rows=["E7a_fillin_displaces"], shots=["J_jobs"], src="Ph4"),
    dict(id="B11", g="B", label="Disclosed overflow: only liquid with nowhere to go is destroyed", item="CANAL_FILL_IN_DISPLACEMENT_1",
         effect="The single conservation exception, counted and disclosed (overflowDestroyedTotal), never silent.",
         probes=["cs:overflowDestroyed|OverflowDestroyed"], rows=["E7b_overflow_sanctioned"], src="Ph4"),
    dict(id="B12", g="B", label="Every pulse balances against an oracle (no leaks)", item=BP,
         effect="Whole-map fill matches an independent oracle every pulse across the scripted phases.",
         probes=["cs:class RM_StockMath"], rows=["B_global_vs_oracle", "C_global_vs_oracle", "G_every_cell_vs_oracle"], src="Build program verify"),
    dict(id="B13", g="B", label="Canyon floods drive FlowWorks instead of erasing canals", item="CANYON_FLOOD_ERASES_CANALS_1",
         effect="FloodedCanyon is a flood-driver client; its floods use FlowWorks' recoverable temp-terrain release.",
         probes=["cs:class Flood_FlowWorks", "cs:SetTempTerrain"], src="Ruling 8"),
    # ---- C reservoirs
    dict(id="C01", g="C", label="A source is just deep liquid terrain (no reservoir building)", item=BP,
         effect="Ruling 24/34: placed deep liquid tiles ARE the reservoir; the old CompFluidReservoir is deleted.",
         probes=["cs:class RM_LiquidBody", "!cs:class CompFluidReservoir"], rows=["S3_classification"], src="Rulings 24/34"),
    dict(id="C02", g="C", label="Limited vs limitless: touching the map edge (and big enough)", item=BP,
         effect="A body touching the edge with >= min cells is limitless; an enclosed body is limited stock.",
         probes=["set:minLimitlessBodyCells", "cs:touchesEdge"], rows=["S3_classification"], src="Owner experience"),
    dict(id="C03", g="C", label="Limitless is sticky (classified once, never flickers)", item=BP,
         effect="Once limitless, a body stays limitless even as it recedes; a setting can turn stickiness off.",
         probes=["set:stickyLimitlessEnabled"], rows=["S5_sticky_limitless"], src="Ph4"),
    dict(id="C04", g="C", label="5:1 budget: each source cell feeds five canal cells, then stops", item=BP,
         effect="An enclosed pond supplies exactly its budget, then the wet front stops; budget OFF = old behaviour.",
         probes=["set:sourceBudgetEnabled", "set:sourceBudgetMultiplier"], rows=["E3_budget_exhaustion", "E3n_budget_off_supplies"],
         bars=["empty_reservoir_stops_flow", "never_full_reservoir_after_heavy_draw"], shots=["E3_E4"], src="Owner experience"),
    dict(id="C05", g="C", label="The source visibly recedes as it pays out", item=BP,
         effect="Supplying a canal shrinks an enclosed body cell by cell from the outside in, restoring the old ground.",
         probes=["set:recessionEnabled", "cs:recededCount|Recede"], rows=["E3b_recession_shipped"],
         bars=["reservoir_fill_visibly_drops", "reservoir_shoreline_recedes"], shots=["E3_E4"], src="Owner experience"),
    dict(id="C06", g="C", label="Slow refill from rain, season and seepage", item=BP,
         effect="A drawn-down body slowly regains level; a very small body refills slowest.",
         probes=["set:refillEnabled", "set:refillRateMultiplier", "cs:void Refill"],
         bars=["reservoir_recharge_progress_visible"], src="Owner scarcity ruling"),
    dict(id="C07", g="C", label="Rain fills unroofed excavations only", item=BP,
         effect="Rain adds fill to open dug cells; a roofed twin stays dry; the toggle stops it.",
         probes=["set:rainFillsExcavationsEnabled", "set:rainFillPerPulse"],
         rows=["E6_rain_fills_unroofed", "E6_roof_readback", "E6n_rain_toggle_off"], shots=["J_jobs"], src="Ruling 25"),
    dict(id="C08", g="C", label="Map-edge sinks drain a canal off-map", item="LIQUID_SINK_DRAINAGE_1",
         effect="A channel reaching the edge band transfers liquid off-map (counted), an interior twin holds.",
         probes=["set:edgeSinksEnabled"], rows=["S4_sink_band", "E5_sink_drains", "E5_inner_holds", "E5n_sinks_off",
                                                "E5_sinks_back_on"], shots=["E5_sinks"], src="Ph4"),
    dict(id="C09", g="C", label="Pumping into tanks draws a source down", item=BP,
         effect="A pump moves liquid from a source or canal into a tank; one full tank = 5 canal cells of stock.",
         probes=["cs:class \\w*Pump"], src="Owner experience; Ph8"),
    # ---- D fluids
    dict(id="D01", g="D", label="Viscosity: tar flows slower than water", item=BP,
         effect="Each fluid moves on its own stride; from equal starts tar trails water. Toggle restores equal speed.",
         probes=["set:viscosityEnabled", "cs:ViscosityStride"], rows=["X7_tar_front_lags_water", "X7n_viscosity_off"],
         bars=["tar_fill_front_lags_water"], shots=["X_promoted"], src="Owner: tar needs viscosity most"),
    dict(id="D02", g="D", label="Fluid identity per cell / body", item="LIQUID_BODY_FLUID_IDENTITY_1",
         effect="Each wet cell and body records its own fluid, so oil in one pit and water in the next can coexist.",
         probes=["cs:fluidGrid", "cs:FluidAt"], rows=["X6_two_fluids_distinct"], src="Collapse [F]"),
    dict(id="D03", g="D", label="Fluids never mix: fronts meet and stop", item="LIQUID_BODY_FLUID_IDENTITY_1",
         effect="A dry cell is claimed by the first fluid to reach it; the other front stops; drain one side and the other advances.",
         probes=["cs:FluidsCompatible"], src="Owner Q3 2026-10-02"),
    dict(id="D04", g="D", label="Old saves migrate; lost fluids are warned, not converted", item="LIQUID_BODY_FLUID_IDENTITY_1",
         effect="A save with only the per-map fluid stamps it onto every wet cell; a removed FluidDef warns once.",
         probes=["cs:ReportLostPaletteFluids"], src="Identity step 4"),
    dict(id="D05", g="D", label="Map fluid cannot be switched after filling", item="LIQUID_BODY_FLUID_IDENTITY_1",
         effect="Changing the map's active fluid after classification is refused (no silent conversion).",
         probes=["cs:ActiveFluid"], rows=["T0n_fluid_switch_refused"], src="Identity"),
    dict(id="D06", g="D", label="Different fluids look different in a canal", item="LIQUID_BODY_FLUID_IDENTITY_1",
         effect="A tar row and a water row draw different fill terrains; bespoke per-fluid art is still placeholder.",
         probes=["xml:defName>RM_Fill_Tar_Brim", "xml:defName>RM_Fill_Water_Brim"], rows=["X6_two_fluids_distinct"],
         bars=["fill_fluid_distinct"], shots=["X_promoted"], src="Bar ruling 2026-09-17"),
    dict(id="D07", g="D", label="Tar has a viscous surface, not tinted water", item="TAR_VISCOUS_SURFACE_ART_1",
         effect="Tar adopts Alpha Biomes' tar surfaces when present (MayRequire), else a tinted fallback.",
         probes=["xml:AB_Tar"], src="Ph7"),
    dict(id="D08", g="D", label="Slime reads thick and opaque, not recoloured water", item=BP,
         effect="Slime canals draw a thick opaque surface. Today slime fill is a tint on the water ramp.",
         probes=["xml:defName>RM_Fluid_SlimeGreen", "tex:(?i)slime"], bars=["slime_reads_as_viscous_not_water"], src="Owner experience"),
    dict(id="D09", g="D", label="Slime is nearly impossible to cross, slow to escape", item=BP,
         effect="Owner: slime is so slippery it is nearly uncrossable and escape takes a long time.",
         probes=["cs:(?i)slime\\w*(slip|escape)"], src="Owner experience"),
    dict(id="D10", g="D", label="A pawn in slime is drawn sunk into it", item="PIT_DEPTH_DRAW_OFFSET_1",
         effect="An occupant of a slime-filled D=4 cell is drawn down in the slime, not on its surface.",
         probes=["cs:class RM_Patch_PitDepthDraw"], rows=["X5_slime_occupant_below_surface"],
         bars=["slime_occupant_below_surface"], shots=["X_promoted"], src="Bar"),
    dict(id="D11", g="D", label="Liquid registry: one row per liquid", item="LIQUID_REGISTRY_CORE_1",
         effect="LiquidDef rows carry properties + form slots (terrain, bottle, trade) for every liquid.",
         probes=["cs:class LiquidDef", "xml:defName>RM_Liquid_Tar<", "xml:defName>RM_Liquid_FreshWater<"], src="Registry"),
    dict(id="D12", g="D", label="Canal fluids: water, tar, oil, poison, four slimes", item=BP,
         effect="FluidDefs that a canal can hold; oil and poison are contents, not pit fittings (collapse Q7).",
         probes=["xml:defName>RM_Fluid_Water<", "xml:defName>RM_Fluid_Tar<", "xml:defName>RM_Fluid_Oil<",
                 "xml:defName>RM_Fluid_Poison<", "xml:defName>RM_Fluid_SlimeRed<"], src="Collapse Q7"),
    dict(id="D13", g="D", label="Many Waters liquid terrains (brine, boiling, propane, acid...)", item="LIQUID_TYPES_MOD_1",
         effect="Shallow/deep terrain pairs for the whole roster, plus coloured waters with bottles.",
         probes=["xml:defName>RM_WaterBrineDeep<", "xml:defName>RM_PropaneDeep<", "xml:defName>RM_Water_Amber<"], src="Roster"),
    dict(id="D14", g="D", label="Each liquid has its faces: flood, rain, river, lake, ocean", item="FLOWWORKS_LIQUID_FACES_1",
         effect="Every registry liquid declares how it appears as a flood, rain, river, lake and ocean.",
         probes=["cs:class LiquidTerrainSuite"], src="Faces item"),
    # ---- E fire
    dict(id="E01", g="E", label="Burnable liquid catches from any fire", item=BP,
         effect="A vanilla fire on or beside tar/oil/propane lights the liquid (Harmony on Fire.SpawnSetup).",
         probes=["cs:class RM_Patch_FireLightsLiquid", "set:canalFireEnabled"], src="Ph6"),
    dict(id="E02", g="E", label="One travelling front: creeping fuse or detonation", item=BP,
         effect="Per fluid: tar/propane creep, astrofuel/chemfuel detonate; one front a player can outrun.",
         probes=["cs:RM_FluidFireKind", "set:fireFrontSpeedMultiplier"], src="Ph6"),
    dict(id="E03", g="E", label="Burns for a long time: 1 canal level/day, 1 source level/5 days", item=BP,
         effect="Burn is a rate on the depth ladder; a limitless source burns effectively forever.",
         probes=["set:canalBurnDaysPerLevel", "set:sourceBurnDaysPerLevel"], bars=["canal_fire_persists"], src="Ruling 7"),
    dict(id="E04", g="E", label="Fire travels back into the source", item=BP,
         effect="A lit canal lights its connected reservoir (up to sourceFireReach cells in).",
         probes=["set:sourceFireReach"], bars=["canal_fire_reaches_reservoir"], src="Owner experience"),
    dict(id="E05", g="E", label="Burning liquid reads as the surface alight", item=BP,
         effect="A flame per burning cell (vanilla fire graphic today); bespoke burning-liquid art is owed.",
         probes=["xml:defName>RM_LiquidFlame<", "tex:(?i)(burning|liquidflame)"], bars=["canal_burning_reads_as_burning_liquid"],
         src="Ph6 owed art"),
    dict(id="E06", g="E", label="A burned-out channel reads scorched and empty", item=BP,
         effect="Burned-dry canal cells get ash today; bespoke scorched art is owed.",
         probes=["cs:Ash", "tex:(?i)scorch"], bars=["canal_spent_after_burn"], src="Ph6 owed art"),
    dict(id="E07", g="E", label="Pawns in a burning cell catch fire (D=4 occupant always)", item=BP,
         effect="Fire harms whoever stands in the burning liquid; a trapped occupant always catches (ruling 22).",
         probes=["cs:class RM_LiquidFire"], src="Ruling 22"),
    dict(id="E08", g="E", label="Explosions ignite liquid", item=BP,
         effect="An explosion (not only a fire) over burnable liquid lights it. Owed per Ph6.",
         probes=["cs:class RM_Patch_\\w*Explosion"], src="Ph6 owed"),
    dict(id="E09", g="E", label="Burning liquid can be put out", item=BP,
         effect="Firefighting / rain can extinguish burning liquid. Owed per Ph6 (only burn-out exists).",
         probes=["cs:class RM_Patch_\\w*Extinguish"], src="Ph6 owed"),
    dict(id="E10", g="E", label="Liquid corrosion spike (ships OFF)", item=BP,
         effect="Corrosive liquids damage what stands in them; an older spike, default off.",
         probes=["cs:class LiquidCorrosionMapComponent", "set:liquidCorrosionEnabled"], src="Ph1 escalation"),
    # ---- F pits capture
    dict(id="F01", g="F", label="SUPERDEEP traps absolutely: no climbing out", item="SUPERDEEP_HOLDER_RETIRE_1",
         effect="A pawn that walks or falls into D=4 stays spawned and cannot path out; no lip cell is reachable.",
         probes=["set:superdeepCaptureEnabled", "cs:class RM_Patch_Reachability_SuperdeepVeto"],
         rows=["P3_walk_in_held", "P1_width_matrix"], bars=["never_snared_standing"], shots=["P_pits"], src="Collapse ruling"),
    dict(id="F02", g="F", label="Pit must be as wide as the creature to hold it", item="SUPERDEEP_HOLDER_RETIRE_1",
         effect="Owner Q4: a creature too large for the pit's width walks out; fill-in that narrows a pit frees it.",
         probes=["set:pitWidthBodySizeMultiplier"], rows=["P1_width_matrix", "P2_fillin_releases_large"], shots=["P_pits"],
         src="Owner Q4 2026-10-02"),
    dict(id="F03", g="F", label="Own colonists are not captured (shipped carve-out)", item="FLOWWORKS_PIT_PAWN_ROWS_RED_1",
         effect="By default a colonist entering D=4 is not trapped; a setting makes the pit catch your own too.",
         probes=["set:superdeepCapturesOwnFaction"], rows=["P5n_own_faction_carveout"], shots=["P_pits"], src="Settings"),
    dict(id="F04", g="F", label="Falling in hurts", item=BP,
         effect="A descent into a deep cell deals fall damage (setting + multiplier).",
         probes=["set:fallDamageEnabled", "set:fallDamageMultiplier"], rows=["P3_walk_in_held"], src="Pit model"),
    dict(id="F05", g="F", label="'Jump into pit' button strands the jumper", item="PIT_SUPERDEEP_COLLAPSE_1",
         effect="A gizmo lets a pawn jump into a superdeep cell (warns and confirms); they are stuck there too.",
         probes=["cs:class RM_Patch_Pawn_JumpIntoPitGizmo"], src="Collapse ruling"),
    dict(id="F06", g="F", label="Superdeep occupant fires only at its 8 neighbours", item=BP,
         effect="Ruling 23, the one sight exception: a D=4 pawn trades fire only with pawns at its own lip.",
         probes=["cs:class RM_Patch_Verb_CanHitTargetFrom", "set:superdeepShootingRuleEnabled"], src="Ruling 23"),
    dict(id="F07", g="F", label="AI does not pick a pit occupant as a ranged target", item=BP,
         effect="Raiders skip SUPERDEEP occupants in target selection instead of failing shots.",
         probes=["cs:class RM_Patch_AttackTargetFinder_BestAttackTarget"], src="Ph5"),
    dict(id="F08", g="F", label="A trapped pawn is not counted as able to reach the map edge", item=BP,
         effect="Flee/exit logic treats a trapped pawn as stuck rather than walking it off-map.",
         probes=["cs:class RM_Patch_Reachability_SuperdeepMapEdge"], src="Pit model"),
    dict(id="F09", g="F", label="Inspect line names the pit state", item=BP,
         effect="Selecting a pit occupant says it is trapped (and why).",
         probes=["cs:class RM_Patch_Pawn_PitInspectLine"], src="Pit model"),
    dict(id="F10", g="F", label="Blast / blowback can knock a pawn into a pit", item="PIT_SUPERDEEP_COLLAPSE_1",
         effect="Involuntary entry by anything that moves a pawn against its will (weapon blowback, explosions).",
         probes=["cs:class RM_Patch_\\w*(Knockback|Blowback|Stagger)"], src="Collapse ruling 6"),
    # ---- G prison / temperature
    dict(id="G01", g="G", label="An enclosed superdeep area is a ROOM", item="SUPERDEEP_PRISON_ROOM_1",
         effect="LAW 2 exception [D]: depth bounds a room, so a dug pit area is one room (holds trapped enemies).",
         probes=["cs:class RM_Patch_\\w*(Region|District|RoomFromDepth)"], src="Collapse [D]"),
    dict(id="G02", g="G", label="A prisoner bed makes the pit a prison; fed and tended from the lip", item="SUPERDEEP_PRISON_ROOM_1",
         effect="With a vanilla prisoner bed the room is a prison on vanilla's terms; wardens never enter.",
         probes=["cs:(?i)(WardenFromLip|FeedFromLip|PitPrison)"], src="Collapse Q1"),
    dict(id="G03", g="G", label="Capture down (from the lip)", item="SUPERDEEP_PRISON_ROOM_1",
         effect="A warden ADJACENT to the lip captures a trapped/downed pawn without entering the pit.",
         probes=["cs:(?i)capturedown|capture_down"], src="Collapse Q1 / [B-item]"),
    dict(id="G04", g="G", label="Convert down (recruit from the lip)", item="SUPERDEEP_PRISON_ROOM_1",
         effect="Recruitment/conversion interaction works from the lip; nobody climbs down.",
         probes=["cs:(?i)convertdown|convert_down"], src="Collapse Q1"),
    dict(id="G05", g="G", label="Too-wide creature is not offered capture down", item="SUPERDEEP_PRISON_ROOM_1",
         effect="A pawn the pit cannot hold (width rule) is not 'trapped' and gets no capture-down option.",
         probes=["cs:(?i)capturedown|capture_down", "set:pitWidthBodySizeMultiplier"], src="Owner Q4"),
    dict(id="G06", g="G", label="Open pit heats fast in sun, chills fast at night", item="PIT_TEMPERATURE_SOFTENING_1",
         effect="An unroofed superdeep room tracks ambient faster than a roofed room (coupling multiplier).",
         probes=["cs:class RM_Patch_PitRoomCoupling", "set:pitTemperatureCoupling"], src="Collapse Q5"),
    dict(id="G07", g="G", label="Exposure wears down resistance", item="PIT_TEMPERATURE_SOFTENING_1",
         effect="RM_PitExposure accumulates on an exposed occupant and lowers recruitment resistance; vanilla heat/cold does the harm.",
         probes=["cs:class RM_PitExposure", "xml:defName>RM_PitExposure<", "set:pitExposureEnabled",
                 "set:pitResistanceLossMultiplier"], src="Collapse [H]"),
    dict(id="G08", g="G", label="'Exposed Prisoner' thought: cruel, and reads as cruel", item="PIT_TEMPERATURE_SOFTENING_1",
         effect="Compassionate colonists feel it; psychopaths (built) and hard-morality cultures (NOT yet) do not.",
         probes=["xml:defName>RM_ExposedPrisoner<", "rx:src/RimMandrake/FlowWorks/Defs:(?i)precept.*ExposedPrisoner|ExposedPrisoner.*precept"],
         src="Collapse [A-item]"),
    # ---- H pit hardware
    dict(id="H01", g="H", label="Ladder: lowered lets people out, raised strands them", item="LADDER_PRISON_DOOR_1",
         effect="A ladder in the D=4 cell works like a prison door: lowered = held False, raised = nobody climbs out.",
         probes=["cs:class RM_CompLadder", "xml:defName>RM_Ladder<", "set:ladderPrisonDoorEnabled",
                 "set:ladderRequiredToExitEnabled"], rows=["P4_ladder_frees", "P4b_ladder_raised_strands"],
         bars=["ladder_state_legible"], shots=["P_pits"], src="Collapse ruling 4"),
    dict(id="H02", g="H", label="Ladders only on an excavation", item="LADDER_PRISON_DOOR_1",
         effect="Placement refuses a ladder anywhere but a dug cell.",
         probes=["cs:class PlaceWorker_LadderOnExcavation"], src="Ladder item"),
    dict(id="H03", g="H", label="Spikes: per-cell, D=4 only, hurt only on a fall in", item="CANAL_BOTTOM_SPIKES_1",
         effect="Spikes in one superdeep cell; walking up to them is harmless; any descent into that cell triggers them.",
         probes=["cs:class RM_SpikeUtility", "xml:defName>RM_Spikes<", "cs:class PlaceWorker_SpikesOnSuperdeep",
                 "set:spikesEnabled"], src="Collapse Q6 / [G]"),
    dict(id="H04", g="H", label="Spike damage: massive Sharp, scaled by body size, survivable", item="SPIKE_DAMAGE_NUMBERS_RULING_1",
         effect="Regular Stab damage (3 hits ~40 x BodySize PROPOSED), never instant death; armour applies.",
         probes=["set:spikeDamageMultiplier", "cs:BodySize"], src="Collapse [G]"),
    dict(id="H05", g="H", label="Pit cover hides the hole (looks like the ground)", item="PIT_COVER_FALL_REWIRE_1",
         effect="A multi-cell terrain-mimic deck over D=4 prints the surrounding surface; slight seam at max zoom.",
         probes=["cs:class TerrainMimicPrinter", "cs:class Building_PitCover"], rows=["X8_cover_hides_pit", "X9_cover_deck_uniform"],
         bars=["pit_covered_invisible", "pit_covered_seam_at_max_zoom"], shots=["X_promoted"], src="Collapse ruling 6"),
    dict(id="H06", g="H", label="Covered pit drops whoever steps on it", item="PIT_COVER_FALL_REWIRE_1",
         effect="Weight on a cover makes it give way and the pawn falls into the superdeep cell below.",
         probes=["cs:class CompPitCoverTrigger", "set:trapTriggerEnabled", "set:trapSensitivityMultiplier"], src="Collapse ruling 6"),
    dict(id="H07", g="H", label="Three cover builds (plank lattice, woven scrap, reinforced frame)", item="PIT_COVER_FALL_REWIRE_1",
         effect="Cover tiers differ in what weight they bear; placed only over superdeep cells.",
         probes=["xml:defName>RM_PitCover_PlankLattice<", "xml:defName>RM_PitCover_WovenScrap<",
                 "xml:defName>RM_PitCover_ReinforcedFrame<", "cs:class PlaceWorker_PitCoverOnSuperdeep"], src="Cover item"),
    dict(id="H08", g="H", label="Drowning: liquid in an occupied D=4 cell drowns non-swimmers", item="PIT_FILL_EFFECTS_1",
         effect="F>0 at D=4 builds RM_PitDrowning on non-swimmers (swimmers and fliers spared).",
         probes=["cs:class RM_PitFillEffects", "xml:defName>RM_PitDrowning<", "set:pitDrowningEnabled",
                 "set:pitDrowningRateMultiplier"], src="Collapse Q3"),
    dict(id="H09", g="H", label="Poison fill: toxin keyed to fill level", item="PIT_FILL_EFFECTS_1",
         effect="A poison-filled cell applies toxic buildup scaled by F/D and toxic resistance, any depth.",
         probes=["xml:defName>RM_Fluid_Poison<", "cs:toxicPerDayAtBrim", "set:poisonFillEnabled"], src="Collapse Q7"),
    dict(id="H10", g="H", label="Oil fill: ignitable, burns the occupant", item="PIT_FILL_EFFECTS_1",
         effect="Oil is a creeping-fuse FluidDef; lit oil in an occupied pit burns the occupant (ruling 22).",
         probes=["xml:defName>RM_Fluid_Oil<", "cs:CreepingFuse"], src="Collapse Q7"),
    dict(id="H11", g="H", label="Flood an occupied pit by opening a sluice", item="PIT_FILL_EFFECTS_1",
         effect="Opening a sluice onto an occupied pit lets liquid in (the scripted route is not written yet).",
         probes=["rx:src/RimMandrake/FlowWorks:(?i)sluice.{0,40}drown|drown.{0,40}sluice"], src="Fill-effects verify"),
    dict(id="H12", g="H", label="No pit def borrows vanilla's spike-trap art", item="EXCAVATION_WALL_ART_1",
         effect="Nothing ships Things/Building/Security/TrapSpikeArmed (today the ladder still does).",
         probes=["!xml:TrapSpikeArmed"], bars=["pit_not_vanilla_trap"], src="Collapse verify"),
    # ---- I doors
    dict(id="I01", g="I", label="Sluice: cheap stuffable door that passes liquid, holds small creatures", item="FLOWWORKS_DOOR_FAMILY_1",
         effect="Two defs, both stuffable; stuff decides armour and fire survival ('learn what happens if made of wood').",
         probes=["xml:defName>RM_Sluice<", "cs:class Building_RM_FlowDoor"], src="Door commission"),
    dict(id="I02", g="I", label="Security grate door: passes liquid AND holds a real prisoner", item="FLOWWORKS_DOOR_FAMILY_1",
         effect="The prisoner door at a canal's end: fluid enters without opening it.",
         probes=["xml:defName>RM_SecurityGrateDoor<", "cs:class RM_FlowDoorRules"], src="Door commission"),
    dict(id="I03", g="I", label="Doors cannot be opened from inside the pit", item="FLOWWORKS_DOOR_FAMILY_1",
         effect="A sluice/grate on a superdeep cell opens from outside or above only.",
         probes=["set:flowDoorsSealedFromPitEnabled"], src="Collapse ruling 7"),
    dict(id="I04", g="I", label="Release a held mech/creature through a sluice", item="FLOWWORKS_DOOR_FAMILY_1",
         effect="Opening a sluice lets a big trapped creature walk out: the pit is a holding pen.",
         probes=["set:sluiceLetsBigThroughEnabled"], src="Collapse [C]"),
    dict(id="I05", g="I", label="Liquid flows through an open sluice / any grate", item="FLOWWORKS_DOOR_FAMILY_1",
         effect="The flow engine treats an open sluice and a grate as passable for liquid.",
         probes=["cs:IsFlowDoor\\(edifice\\)"],
         src="Door commission"),
    dict(id="I06", g="I", label="Sluice open vs shut is visible without selecting it", item="FLOWWORKS_DOOR_FAMILY_1",
         effect="Own art for both doors; today they borrow vanilla DoorSimple_Mover.",
         probes=["xml:defName>RM_Sluice<", "tex:(?i)(sluice|grate)"], bars=["sluice_gate_state_legible"], src="Bar"),
    # ---- J pawn draw & art
    dict(id="J01", g="J", label="Pawns sit lower at every deeper step", item="PIT_DEPTH_DRAW_OFFSET_1",
         effect="Draw offset per depth (0.3 cell/level PROVISIONAL): D0..D4 strictly lower.",
         probes=["cs:class RM_Patch_PitDepthDraw", "set:pitDepthDrawOffsetEnabled", "set:pitSinkPerLevel"],
         rows=["X1_pawn_height_ladder"], bars=["pawn_height_ladder_legible"], shots=["X_promoted"], src="Depth ruling"),
    dict(id="J02", g="J", label="A pawn walking into a deeper cell visibly lowers", item="PIT_DEPTH_DRAW_OFFSET_1",
         effect="The offset is lerped along the step, so descending reads as movement down.",
         probes=["cs:class RM_Patch_PitDepthDraw"], rows=["X2_pawn_lowers_walking_in"], bars=["pawn_lowers_on_deeper_cell"],
         shots=["X_promoted"], src="Depth ruling"),
    dict(id="J03", g="J", label="A pawn walking out visibly rises", item="PIT_DEPTH_DRAW_OFFSET_1",
         effect="Climbing out (by ladder) lifts the pawn back to ground level along the step.",
         probes=["cs:class RM_Patch_PitDepthDraw"], rows=["X3_pawn_rises_walking_out"], bars=["pawn_rises_on_shallower_cell"],
         shots=["X_promoted"], src="Depth ruling"),
    dict(id="J04", g="J", label="At D=4 the walls stand 20% above the occupant's head", item="PIT_DEPTH_DRAW_OFFSET_1",
         effect="Owner's only number: wall top >= 1.2 x head height, so climbing out is visibly impossible.",
         probes=["cs:class RM_PitDrawMath"], rows=["X4_pit_wall_over_head"], bars=["pit_trapped_reads_as_trapped"],
         shots=["X_promoted"], src="Depth ruling"),
    dict(id="J05", g="J", label="Occupant reads as down in the hole; occupied vs empty at a glance", item="EXCAVATION_WALL_ART_1",
         effect="Draw offset (built) + wall faces rising around the pawn (art owed).",
         probes=["cs:class RM_Patch_PitDepthDraw", "tex:(?i)(excavation|pitwall|wallface|channel)"],
         bars=["pit_occupant_below_floor", "pit_occupied_distinguishable"], shots=["REF_quarry"], src="Rulings 33 + depth"),
    dict(id="J06", g="J", label="Wall-face art for all four depths (Quarry perspective)", item="EXCAVATION_WALL_ART_1",
         effect="Shared rim + per-depth wall gradient; every depth legible and different from the others.",
         probes=["tex:(?i)(excavation|pitwall|wallface|rim)"], bars=["pit_depth_ladder_legible", "pit_walls_have_visible_depth"],
         shots=["REF_quarry"], src="Ruling 33 / depth ruling"),
    dict(id="J07", g="J", label="Spike art: some spike visibly projects", item="EXCAVATION_WALL_ART_1",
         effect="Camera angle must let some spike show; today spikes borrow Skullspike.",
         probes=["xml:defName>RM_Spikes<", "tex:(?i)spike"], bars=["spikes_read_distinct"], src="Spike/camera ruling"),
    dict(id="J08", g="J", label="Ladder art: raised vs lowered drawn on the wall", item="EXCAVATION_WALL_ART_1",
         effect="Ladders drawn in perspective, raised beside the rim vs lowered into the hole.",
         probes=["xml:defName>RM_Ladder<", "tex:(?i)ladder"], bars=["ladder_state_legible"], shots=["REF_quarry"], src="Ruling 33"),
    dict(id="J09", g="J", label="A dug channel looks dug (recessed bed, earthen walls), not gravel", item="EXCAVATION_WALL_ART_1",
         effect="Today the channel borrows Terrain/Surfaces/Gravel.",
         probes=["tex:(?i)(channel|excavation)"], bars=["canal_reads_as_dug_channel", "never_gravel_path"], shots=["S_ladder"],
         src="Bar"),
    dict(id="J10", g="J", label="A superdeep cell reads as a big dark hole at play zoom", item="EXCAVATION_WALL_ART_1",
         effect="Owner: 'we need a big dark pit', not a trap graphic.",
         probes=["xml:defName>RM_Channel_Superdeep<", "tex:(?i)(superdeep|pit)"], bars=["pit_reads_as_hole"], shots=["REF_quarry"],
         src="Owner 2026-09-13"),
    dict(id="J11", g="J", label="A multi-cell pit reads as one place, not a tile grid", item="EXCAVATION_WALL_ART_1",
         effect="Irregular organic edges, Quarry-style, so an area reads as one excavation (and as a room).",
         probes=["tex:(?i)(superdeep|pit|excavation)"], bars=["pit_reads_at_size"], shots=["REF_quarry"], src="Ruling 33"),
    dict(id="J12", g="J", label="The bare excavation never reads as a building", item="EXCAVATION_WALL_ART_1",
         effect="The pit is terrain (built); its art must not look like a placed object on the floor (owed).",
         probes=["xml:defName>RM_Channel_Superdeep<", "!cs:class Building_OpenPit", "tex:(?i)(superdeep|excavation)"],
         bars=["never_reads_as_building"], src="Bar"),
    dict(id="J13", g="J", label="Depth and fill legible together in one view", item="EXCAVATION_WALL_ART_1",
         effect="Same fill/different depth and same depth/different fill all distinguishable.",
         probes=["xml:defName>RM_Fill_Water_Half", "tex:(?i)(excavation|wallface|rim)"],
         bars=["depth_and_fill_jointly_legible"], shots=["S_ladder"], src="Bar"),
    dict(id="J14", g="J", label="Dry and filled channels read as obstacles without a tooltip", item="EXCAVATION_WALL_ART_1",
         effect="Path cost exists (A06/A07); the look of impeding is the art's job.",
         probes=["xml:<pathCost>30</pathCost>", "tex:(?i)(channel|excavation)"],
         bars=["canal_dry_reads_as_obstacle", "filled_excavation_reads_as_obstacle"], src="Bar"),
    # ---- K containers & industry
    dict(id="K01", g="K", label="Bottles: fill at a shore or tank, drink/use", item="LIQUID_BOTTLE_LOOP_1",
         effect="Empty bottle -> fill job -> per-liquid bottle -> use.",
         probes=["cs:class JobDriver_FillBottle", "cs:class JobDriver_FillBottleFromTank", "xml:defName>RM_Bottle_FreshWater<",
                 "set:bottleLoopEnabled"], src="Liquids framework §4"),
    dict(id="K02", g="K", label="Dirty bottles and washing (toggle, default ON)", item="LIQUID_BOTTLE_LOOP_1",
         effect="Use leaves a dirty bottle; washing consumes water and returns an empty one.",
         probes=["cs:class JobDriver_WashBottle", "xml:defName>RM_BottleDirty<", "set:bottleDirtyStageEnabled"], src="Bottle item"),
    dict(id="K03", g="K", label="Buckets and barrels: bigger bottles, same chain", item="LIQUID_BOTTLE_LOOP_1",
         effect="Buckets and ~25-unit barrels; barrels are the vanilla-native bulk trade route.",
         probes=["xml:defName>RM_BucketEmpty<", "xml:defName>RM_BarrelEmpty<", "tex:RM_Barrel"], src="Owner 2026-09-13"),
    dict(id="K04", g="K", label="Special bottle behaviours: boiling reverts, blood rots", item="LIQUID_BOTTLE_LOOP_1",
         effect="Row data, no per-liquid C#: a revert timer (boiling/icy -> fresh) and rot (blood -> hemopack race).",
         probes=["cs:(?i)revert", "xml:(?i)hemopack"], src="Bottle item"),
    dict(id="K05", g="K", label="Bottles carry cuisine tags", item="LIQUID_BOTTLE_LOOP_1",
         effect="ThingCategories so a future cuisine mod cooks against tags, never defNames.",
         probes=["xml:(?i)cuisine"], src="Bottle item"),
    dict(id="K06", g="K", label="Liquid tank: fill from and empty into bottles", item=BP,
         effect="A universal container building; bottles empty into it and fill from it.",
         probes=["cs:class Building_LiquidTank", "xml:defName>RM_LiquidTank<", "cs:class JobDriver_EmptyBottleIntoTank",
                 "set:tankLoopEnabled"], src="Ph8"),
    dict(id="K07", g="K", label="Liquid drill and tap raise subsurface liquid", item="MANY_WATERS_DRILL_BUILDINGS_1",
         effect="On maps whose biome yields it, a drill/tap brings liquid up into an excavated outlet.",
         probes=["cs:class Building_LiquidDrill", "xml:defName>RM_LiquidDrill<", "xml:defName>RM_LiquidTap<",
                 "cs:class PlaceWorker_DrillNeedsExcavatedOutlet", "set:liquidDrillingEnabled"], src="Drill item"),
    dict(id="K08", g="K", label="Pumps", item=BP,
         effect="Universal pump moving liquid between sources, canals and tanks.",
         probes=["xml:defName>RM_\\w*Pump\\w*<"], src="Ph8"),
    dict(id="K09", g="K", label="Flexible hoses (built in Gimme Some Slack)", item="FLOWWORKS_HOSE_DEPLOY_DRAG_1",
         effect="Hose reels a colonist drags out; lives in GimmeSomeSlack, carries no real liquid yet.",
         probes=["file:src/RimMandrake/GimmeSomeSlack/Source/Hose/CompHoseReel.cs"], src="Ph8 / hose item"),
    dict(id="K10", g="K", label="Per-net adapters", item=BP,
         effect="Adapters joining pipe/hose nets (the Ph8 internal interface boundary).",
         probes=["cs:class \\w*Adapter"], src="Ph8"),
    dict(id="K11", g="K", label="Found liquid industry: desal, detox, tar refinery, pumping station", item="LIQUID_INDUSTRY_SETPIECES_1",
         effect="Industrial scale is FOUND (wrecked -> repaired), never built from the menu in the campaign.",
         probes=["rx:src/RimMandrake:(?i)defName>\\w*(Desal|TarRefiner|PumpingStation)"], src="Liquids framework §4"),
    dict(id="K12", g="K", label="Water cleaning chain wired to thirst", item="LIQUID_THIRST_CHAIN_1",
         effect="Crude/household/industrial cleaning tiers feed Dubs Bad Hygiene thirst.",
         probes=["cs:LiquidThirstQuality", "rx:src/RimMandrake/FlowWorks/Defs:(?i)DBHThirst"], src="Thirst item"),
    # ---- L shores, rivers, swale
    dict(id="L01", g="L", label="Typed liquid shores on new maps", item="WORLDMAP_LIQUID_TAGS_1",
         effect="A landing GenStep repaints shores to the tile's liquid (affects newly generated maps).",
         probes=["cs:class RM_GenStep_LiquidShores", "set:typedLiquidShoresEnabled"], src="Liquid tags item"),
    dict(id="L02", g="L", label="World liquid tags on the frozen map", item="WORLDMAP_LIQUID_TAGS_1",
         effect="worldTags mark which tiles carry which liquid, read by shores and set-piece siting.",
         probes=["cs:class RM_WorldComponent_LiquidTags"], src="Liquid tags item"),
    dict(id="L03", g="L", label="Coloured steam rising from rivers", item="RIVER_STEAM_ANIMATION_1",
         effect="Animated steam flecks over hot rivers, coloured per river.",
         probes=["cs:class MapComponent_RiverSteam", "xml:defName>RM_Fleck_Steam_Amber<"], src="Steam item"),
    dict(id="L04", g="L", label="Nobody goes recreational swimming in sand", item=BP,
         effect="Swim joy is refused on sand-like liquid terrains.",
         probes=["cs:class RM_Patch_JoyGiver_GoSwimming_NoSandSwim"], src="Many Waters"),
    dict(id="L05", g="L", label="Swale: a fed canal slowly improves the soil beside it", item="CRACKEDLANDS_MECHANICS_BUILD_1",
         effect="While carrying water, adjacent cells climb sand -> soil -> rich soil, capped, slow.",
         probes=["cs:class RM_CompSwale", "xml:defName>RM_Swale<", "set:swaleEnabled", "set:swaleRateMultiplier"],
         src="Cracked Lands ruling"),
    dict(id="L06", g="L", label="Swale locked in the campaign until discovered", item="CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1",
         effect="World-level unlock earned in the Cracked Lands; free tier stays a normal buildable.",
         probes=["rx:src/RimMandrake:(?i)swale\\w*(unlock|discover)"], src="Cracked Lands ruling"),
    dict(id="L07", g="L", label="Swale art from a real canal", item="SWALE_CANAL_ART_REFERENCE_1",
         effect="Today the swale borrows GraveEmpty; its art waits on screenshots of a real canal.",
         probes=["tex:(?i)swale"], src="Owner art sheet"),
    dict(id="L08", g="L", label="Irrigation: plants beside a filled canal act watered", item=BP,
         effect="Owner experience: 'natural irrigation of crops'. Solved in FloodedCanyon, not wired here.",
         probes=["cs:class \\w*Irrigat"], src="Owner experience"),
    dict(id="L09", g="L", label="River Works slice 1: river current + ford stones", item="SURFACE_RIVER_WEIRS_1",
         effect="Surface current on vanilla rivers, fordable stones, swept-away pawns (new mod RiverWorks).",
         probes=["file:src/RimMandrake/RiverWorks/Source/RM_MapComponent_RiverCurrent.cs",
                 "file:src/RimMandrake/RiverWorks/Defs/TerrainDefs/RM_FordStones.xml"], src="River works design"),
    dict(id="L10", g="L", label="Weirs on ordinary rivers", item="SURFACE_RIVER_WEIRS_1",
         effect="Build a weir across a surface river to hold and raise water.",
         probes=["rx:src/RimMandrake/RiverWorks:(?i)weir"], src="Owner-typed 2026-09-26"),
    dict(id="L11", g="L", label="Silt-trap, stake-line and hopper bank-works", item="SURFACE_RIVER_WEIRS_1",
         effect="The bank-works family from the weir system, on surface rivers.",
         probes=["rx:src/RimMandrake/RiverWorks:(?i)silt", "rx:src/RimMandrake/RiverWorks:(?i)stake", "rx:src/RimMandrake/RiverWorks:(?i)hopper"],
         src="Owner-typed 2026-09-26"),
    dict(id="L12", g="L", label="Untended weir + flood = breach cascade", item="SURFACE_RIVER_WEIRS_1",
         effect="A weir left untended when a flood comes breaches and cascades downstream.",
         probes=["rx:src/RimMandrake/RiverWorks:(?i)breach"], src="Owner-typed 2026-09-26"),
    dict(id="L13", g="L", label="River Works slice 2: fish catch, drift, ferry", item="SURFACE_RIVER_WEIRS_1",
         effect="The rest of the surface-river works beyond weirs and bank-works.",
         probes=["rx:src/RimMandrake/RiverWorks:(?i)ferry", "rx:src/RimMandrake/RiverWorks:(?i)drift", "rx:src/RimMandrake/RiverWorks:(?i)fish"],
         src="Remaining inventory #12"),
    # ---- M quarry
    dict(id="M01", g="M", label="Digging a canal turns up local materials (a lump on the bank)", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="Excavation can yield biome-local materials dropped on the bank (availability by biome, configurable).",
         probes=["cs:(?i)quarry|canaldigfind|digfind"], src="Quarry item / remaining inventory #6"),
    dict(id="M02", g="M", label="A letter on the first find of each material per map", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="The first time a material turns up on a map, a letter says what and where.",
         probes=["cs:(?i)(firstfind|first_find)"], src="Remaining inventory #6"),
    dict(id="M03", g="M", label="Deep cuts reach deep-drill minerals; mineral-less biomes give rock chunks", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="Depth decides what can turn up; a biome with no minerals yields local rock chunks instead.",
         probes=["cs:(?i)quarry\\w*(deep|depth)|deepdrillmineral"], src="Remaining inventory #6"),
    dict(id="M04", g="M", label="Reads the mineral abundance registry", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="What can turn up comes from the shared mineral abundance registry, not a FlowWorks list.",
         probes=["cs:(?i)mineralabundance|MineralRegistry"], src="Quarry item"),
    dict(id="M05", g="M", label="Sluice box: a stream slowly yields ore", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="River Works half; waits on the rivers-carry column of MINERALS_WHERE_THEY_BELONG_1.",
         probes=["rx:src/RimMandrake:(?i)defName>\\w*SluiceBox"], src="Quarry item"),
    dict(id="M06", g="M", label="Panning for gold in a river", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="A colonist pans a river cell for a slow trickle of gold (River Works half).",
         probes=["rx:src/RimMandrake:(?i)defName>\\w*(GoldPan|Panning)\\w*<"], src="Quarry item"),
    # ---- N settings & shipping
    dict(id="N01", g="N", label="Every mechanic has a Mod Settings toggle, grouped by section", item="MOD_OPTIONS_RETROFIT_1",
         effect="Defaults = shipped behaviour; the settings screen is grouped (excavation, stock, fire, pits, containers...).",
         probes=["cs:class RimMandrakeFlowWorksSettings", "cs:CheckboxLabeled"], src="Standing rule 2026-09-12"),
    dict(id="N02", g="N", label="All mechanics off still digs dry channels", item="FLOWWORKS_NORTHSTAR_SHIP_1",
         effect="An all-off component proves the mod degrades to a channel digger.",
         probes=["rx:src/RimMandrake/FlowWorks:all_off_still_digs"], src="Ship item"),
    dict(id="N03", g="N", label="Worldgen-affecting toggle labelled as such", item="FLOWWORKS_NORTHSTAR_SHIP_1",
         effect="The shores toggle says it affects newly generated maps.",
         probes=["cs:affects newly generated maps"], src="Settings rule"),
    dict(id="N04", g="N", label="Bridge proof surface (static calls) for every promoted row", item="FLOWWORKS_NORTHSTAR_WIRE_1",
         effect="Proof*/Report static calls the north-star driver reads state through.",
         probes=["cs:class RM_PromotionProofs", "cs:class RM_LiquidFireProof", "cs:class FlowWorksDebugActions"], src="North star"),
]

# ------------------------------------------------------------------------------------------------ probes
_cache = {}


def _texts(kind):
    if kind in _cache:
        return _cache[kind]
    roots = {"cs": [os.path.join(HERE, "Source")],
             "xml": [os.path.join(HERE, "Defs"), os.path.join(HERE, "Patches")]}[kind]
    ext = "." + kind
    out = []
    for r in roots:
        for dp, dn, fn in os.walk(r):
            dn[:] = [d for d in dn if d not in ("bin", "obj", "__pycache__")]
            for f in fn:
                if f.endswith(ext):
                    try:
                        out.append(open(os.path.join(dp, f), encoding="utf-8", errors="replace").read())
                    except OSError:
                        pass
    _cache[kind] = out
    return out


def _textures():
    if "tex" not in _cache:
        base = os.path.join(HERE, "Textures")
        _cache["tex"] = [os.path.relpath(os.path.join(dp, f), base).replace(os.sep, "/")
                         for dp, _, fn in os.walk(base) for f in fn]
    return _cache["tex"]


def _rx_dir(path, rx):
    p = os.path.join(REPO, path)
    files = [p] if os.path.isfile(p) else [os.path.join(dp, f) for dp, dn, fn in os.walk(p)
                                          if "__pycache__" not in dp and "/bin" not in dp and "/obj" not in dp for f in fn
                                          if f.endswith((".cs", ".xml", ".py")) and f not in SELF_FILES]
    r = re.compile(rx)
    for f in files:
        try:
            if r.search(open(f, encoding="utf-8", errors="replace").read()):
                return True
        except OSError:
            pass
    return False


def probe(spec):
    """-> bool. Present means the thing the spec names exists on disk now."""
    neg = spec.startswith("!")
    s = spec[1:] if neg else spec
    kind, _, arg = s.partition(":")
    if kind in ("cs", "xml"):
        r = re.compile(arg)
        hit = any(r.search(t) for t in _texts(kind))
    elif kind == "set":
        txt = _cache.setdefault("set", open(SETTINGS_CS, encoding="utf-8").read())
        hit = re.search(r"public static \w+ %s\s*=" % re.escape(arg), txt) is not None
    elif kind == "tex":
        r = re.compile(arg)
        hit = any(r.search(t) for t in _textures())
    elif kind == "file":
        hit = os.path.exists(os.path.join(REPO, arg))
    elif kind == "rx":
        d, _, rx = arg.partition(":")
        hit = _rx_dir(d, rx)
    else:
        raise ValueError("unknown probe kind: %s" % spec)
    return (not hit) if neg else hit


# ------------------------------------------------------------------------------------------------ evidence sources
def latest_result(path=None):
    """-> (label, {row_id: (status, detail)}). Newest validation_v2_result_*.json plus every proof_*.json."""
    files = [path] if path else sorted(glob.glob(os.path.join(NSDIR, "validation_v2_result_*.json")))[-1:]
    files += sorted(glob.glob(os.path.join(NSDIR, "proof_*.json"))) if not path else []
    rows = {}
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for r in d.get("rows", []):
            if r.get("id"):
                rows[r["id"]] = (str(r.get("status", "")), str(r.get("detail", "")))
    label = ", ".join(os.path.basename(f) for f in files) or "(no result file)"
    return label, rows


def ledger_states(ids):
    """-> {item: (state, title)}; state 'unfiled' when the ledger has never seen it, 'UNMEASURED' when it cannot be read."""
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))
    try:
        from rimflow import cli
        _, w = cli.load()
    except (Exception, SystemExit) as e:  # a ledger that cannot be read is UNMEASURED, never "all closed"
        return {i: ("UNMEASURED", str(e)[:80]) for i in ids}
    out = {}
    for i in ids:
        it = w.items.get(i)
        out[i] = (it.state, it.title or "") if it else ("unfiled", "")
    return out


# ------------------------------------------------------------------------------------------------ derivation
def derive_status(cap, rows, probe_fn=probe):
    """-> dict(status, probes[(spec, ok)], live[(row, status)], proven). The ONLY place status is decided."""
    pr = [(p, bool(probe_fn(p))) for p in cap.get("probes", [])]
    live = [(r, rows[r][0] if r in rows else "absent") for r in cap.get("rows", [])]
    proven = any(s == "PASS" for _, s in live)
    oks = [ok for _, ok in pr]
    if proven:
        st = "PROVEN-LIVE"
    elif oks and all(oks):
        st = "BUILT-UNPROVEN"
    elif any(oks):
        st = "PARTIAL"
    else:
        st = "NOT BUILT"
    return dict(status=st, probes=pr, live=live, proven=proven)


def remains(caps_d, states):
    """Open owning items with their NOT BUILT / PARTIAL rows (and a count of their unproven ones)."""
    out = {}
    for c in caps_d:
        st, title = states.get(c["item"], ("?", ""))
        if st not in OPEN_STATES:
            continue
        e = out.setdefault(c["item"], dict(state=st, title=title, todo=[], unproven=0))
        if c["d"]["status"] in ("NOT BUILT", "PARTIAL"):
            e["todo"].append(c)
        elif c["d"]["status"] == "BUILT-UNPROVEN":
            e["unproven"] += 1
    return {k: v for k, v in out.items() if v["todo"] or v["unproven"]}


def walk_bars():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
    try:
        import northstar as N
        w = N.parse(N.find_walk(REPO, "FlowWorks"))
        return list(w["must_show"]), list(w["cannot_show"]), w.get("state")
    except Exception:
        return [], [], "UNMEASURED"


def canon_note():
    """FlowWorks subjects are terrain/hardware; say so only after checking the library for any of our subjects."""
    if not os.path.isdir(CANON):
        return "canon library not on disk: UNMEASURED"
    names = " ".join(os.listdir(CANON)).lower()
    hits = [w for w in ("sluice", "ladder", "canal", "pit", "tar", "slime", "spike") if re.search(r"\b%s" % w, names)]
    return ("no canon entry for any FlowWorks subject (checked %d entries)" % len(os.listdir(CANON)) if not hits
            else "canon entries possibly relevant: %s" % ", ".join(hits))


# ------------------------------------------------------------------------------------------------ shots
def ensure_shots(out_dir):
    """Copy each shot as a downscaled JPEG into <out_dir>/shots/ (prefer the committed review/shots copy). -> {name: rel}."""
    dst = os.path.join(out_dir, "shots")
    os.makedirs(dst, exist_ok=True)
    got = {}
    for name, src in SHOTS.items():
        rel = "shots/%s.jpg" % name
        target = os.path.join(out_dir, rel)
        committed = os.path.join(REVIEW, rel)
        if os.path.exists(target):
            got[name] = rel
            continue
        if os.path.exists(committed):
            with open(committed, "rb") as a, open(target, "wb") as b:
                b.write(a.read())
            got[name] = rel
            continue
        s = os.path.join(REPO, src)
        if not os.path.exists(s):
            continue
        try:
            from PIL import Image
            im = Image.open(s).convert("RGB")
            if im.width > 1400:
                im = im.resize((1400, int(im.height * 1400 / im.width)))
            im.save(target, "JPEG", quality=82)
            got[name] = rel
        except Exception:
            continue
    return got


# ------------------------------------------------------------------------------------------------ the sheet
RENDER_JS = r"""<script id="RENDER">
window.itemBody = it => {
  const e = window.esc, s = it.fw || {};
  const pr = (s.probes || []).map(p => `<span class="mark ${p[1] ? '' : 'inferred'}" style="${p[1] ? 'color:#8fd3a8;border-color:#2b5a3b' : ''}" title="declared probe">${p[1] ? '✓' : '✗'} ${e(p[0])}</span>`).join('');
  const lv = (s.live || []).map(r => `<span class="mark" style="${r[1] === 'PASS' ? 'color:#5ac37f;border-color:#2b5a3b' : 'color:#e06c6c;border-color:#5a2b2b'}" title="${e(r[2] || '')}">${e(r[0])} ${e(r[1])}</span>`).join('');
  const bars = (s.bars || []).map(b => `<span class="mark absent" title="north-star bar">★ ${e(b)}</span>`).join('');
  return `<div class="effect"><b style="color:${e(s.color)}">${e(s.status)}</b> · ${e(it.effect)}</div>
    <div class="marks"><span class="mark absent">${e(s.item)} <b>${e(s.itemState)}</b></span><span class="mark absent">intent: ${e(s.src)}</span>${bars}</div>
    <div class="marks">${lv}${pr}</div>`;
};
</script>
"""


def build(out=DEFAULT_OUT, result=None, states=None, probe_fn=probe, caps=None, write_decisions=True):
    caps = caps if caps is not None else CAPS
    out = os.path.abspath(out)
    out_dir = os.path.dirname(out)
    os.makedirs(out_dir, exist_ok=True)
    rlabel, rows = latest_result(result)
    states = states if states is not None else ledger_states(sorted({c["item"] for c in caps}))
    shots = ensure_shots(out_dir)
    must, cannot, walk_state = walk_bars()
    caps_d = []
    for c in caps:
        d = derive_status(c, rows, probe_fn)
        caps_d.append(dict(c, d=d))
    counts = {s: sum(1 for c in caps_d if c["d"]["status"] == s) for s in STATUSES}
    rem = remains(caps_d, states)
    covered = {b for c in caps for b in c.get("bars", [])}
    uncovered = [b for b in must + cannot if b not in covered]

    items = []
    for c in caps_d:
        d = c["d"]
        st_item = states.get(c["item"], ("?", ""))[0]
        thumb = next((shots[s] for s in c.get("shots", []) if s in shots), None)
        wanted = d["status"] in ("NOT BUILT", "PARTIAL") and st_item in OPEN_STATES
        it = dict(id=c["id"], label="[%s] %s" % (d["status"], c["label"]), group=GROUPS[c["g"]], effect=c["effect"],
                  prefill="wanted" if wanted else None,
                  fw=dict(status=d["status"], color=COLOR[d["status"]], item=c["item"], itemState=st_item, src=c.get("src", ""),
                          bars=c.get("bars", []), probes=d["probes"],
                          live=[(r, s, rows.get(r, ("", ""))[1][:200]) for r, s in d["live"]]))
        if thumb:
            it["thumb"] = thumb
        items.append(it)

    def esc(x):
        return html.escape(str(x))
    pills = " ".join('<span style="color:%s"><b>%d</b> %s</span> ·' % (COLOR[s], counts[s], s) for s in STATUSES)
    rem_html = "".join(
        "<li><b>%s</b> <i>(%s)</i> %s: %s%s</li>" % (
            esc(k), esc(v["state"]), esc(v["title"][:90]),
            ", ".join("%s %s [%s]" % (esc(c["id"]), esc(c["label"]), esc(c["d"]["status"])) for c in v["todo"]) or "nothing unbuilt",
            (" · <i>%d built, unproven</i>" % v["unproven"]) if v["unproven"] else "")
        for k, v in sorted(rem.items()))
    brief = (
        "<p><b>%d intended capabilities</b> of FlowWorks, built or not. %s</p>"
        "<p><b>Status is derived, never typed:</b> PROVEN-LIVE = a mapped mechanism row PASSed in <code>%s</code>; "
        "BUILT-UNPROVEN = every declared probe (class / def / setting / texture) exists on disk; PARTIAL = some do; "
        "NOT BUILT = none. Each row lists its probes (✓/✗), its live rows, its north-star bars (★) and the owning item with "
        "its ledger state. North-star walk state: <b>%s</b>; %d of %d bars carried by a row%s.</p>"
        "<p><b>Your controls:</b> <i>Looks right</i> / <i>Wrong</i> (say why in the note) / <i>Wanted</i> (not built, and you "
        "still want it). Rows the ledger says are open and unbuilt start on <i>Wanted</i> because their item is open; "
        "nothing else is pre-filled. Thumbnails: the 2026-10-05 live run (load <code>NS_FlowWorks_Review_20261005</code> to walk it) "
        "and the Quarry reference (ruling 33). Canon: %s.</p>"
        "<h3 style='margin:8px 0 2px'>What remains to build (open items, from the ledger)</h3><ul style='margin:0;padding-left:18px'>%s</ul>"
    ) % (len(caps), pills, esc(rlabel), esc(walk_state), len(must + cannot) - len(uncovered), len(must + cannot),
         (" (uncovered: %s)" % esc(", ".join(uncovered))) if uncovered else "", esc(canon_note()), rem_html)
    config = {
        "sheetId": "flowworks_capability_review",
        "title": "FlowWorks — what exists, what works, what remains",
        "subtitle": "%d capabilities · %s" % (len(caps), " · ".join("%d %s" % (counts[s], s) for s in STATUSES)),
        "briefHtml": brief,
        "criterion": "Rows follow the build program's subsystems; status comes from probes + the newest live result, "
                     "which proves a mechanism exists, never that it looks right.",
        "invented": [],
        "posture": {"mode": "whitelist",
                    "explain": "Looks right and Wanted keep a capability in scope; Wrong reopens it. Undecided = not yet looked at."},
        "options": [
            {"key": "right", "label": "Looks right", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "wrong", "label": "Wrong", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
            {"key": "wanted", "label": "Wanted", "hotkey": "3", "color": "#e8b64c", "counts": "in"},
        ],
        "groupLabel": "subsystem",
        "media": True,
        "decisionsFile": DEC_NAME,
        "decisionsPath": "", "sheetPath": "",
    }
    tpl = open(TEMPLATE, encoding="utf-8").read()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(config, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items, indent=0).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<title>Review sheet</title>", "<title>FlowWorks capability review</title>", 1)
    # the RENDER hook goes in LIVE, after the template's commented example (SKILL.md: a hook inside the comment is inert)
    marker = "-->\n\n<script>\n\"use strict\";"
    assert marker in tpl, "template changed: cannot place the RENDER hook"
    tpl = tpl.replace(marker, "-->\n" + RENDER_JS + "\n<script>\n\"use strict\";", 1)
    with open(out, "w", encoding="utf-8") as f:
        f.write(tpl)
    dec = os.path.join(out_dir, DEC_NAME)
    if write_decisions and not os.path.exists(dec):      # never overwrite: once it exists it is the owner's
        with open(dec, "w", encoding="utf-8") as f:
            json.dump({"posture": "whitelist", "decisions": {},
                       "reviewStatus": {"state": "prefill", "by": None, "at": None,
                                        "evidence": "generated by FlowWorks/human_review.py; nobody has ruled"}}, f, indent=1)
    return dict(out=out, items=items, counts=counts, remains=rem, uncovered=uncovered, result=rlabel, caps=caps_d)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--result", help="a specific validation_v2 result json (default: the newest)")
    a = ap.parse_args()
    r = build(a.out, a.result)
    print("%d rows -> %s" % (len(r["items"]), r["out"]))
    print("  " + " · ".join("%d %s" % (r["counts"][s], s) for s in STATUSES))
    print("  result: %s" % r["result"])
    for k, v in sorted(r["remains"].items()):
        print("  remains %s (%s): %s%s" % (k, v["state"], ", ".join(c["id"] for c in v["todo"]) or "-",
                                          " +%d unproven" % v["unproven"] if v["unproven"] else ""))
    if r["uncovered"]:
        print("  bars with no row: %s" % ", ".join(r["uncovered"]))


if __name__ == "__main__":
    main()
