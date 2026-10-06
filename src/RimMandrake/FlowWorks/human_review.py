"""human_review.py -- FlowWorks capability review sheet (owner, 2026-10-05).

    python3 src/RimMandrake/FlowWorks/human_review.py            # writes northstar/review/FlowWorks_review.html
    python3 src/RimMandrake/FlowWorks/human_review.py --out X.html --result R.json

Owner, 2026-10-05 (typed): *"make a dense, comprehensive, efficient human review sheet based on the intended
functionality in flow works even if it's not built yet so we can see what's there, what's working or not, and what
remains to be built easily."*

Owner, same day, on the first version (139 rows, one per capability, ticket ids and code chips in the main view):
*"You proposed a review sheet that was not human readable. Bad medium for review."* So the page he READS shows ~45
FEATURES in plain designer sentences (the FEATURES table), 8 sections, ONE status badge each, an at-a-glance panel
(sections x status, what I need from you, what remains to build -- derived from the ledger), pictures inline, and the
technical evidence behind a closed "details" toggle; plus FlowWorks_status_board.html, the same content as a plain
document. The rules for any sheet like this: design/RimMandrake/northstar_densification_lessons.md, "Review sheet
presentation rules".

Underneath, one EVIDENCE row per intended capability (the CAPS table, data). Nothing is a hand-typed verdict:
  * BUILT is DERIVED from declared probes (a class / def / setting / texture / file that must exist on disk);
  * PROVEN-LIVE is DERIVED from a PASS row in the newest northstar/validation_v2_result_*.json (+ any proof_*.json),
    mapped to MECHANISM rows only (never the harness rows L1/L2/L4, SITE*, A0, E9, Z; L3_defs_live is a MOD row);
  * the owning item's state is read from the rimflow ledger at generation time, and the "what remains to build"
    list is derived from it (open items only).
Status: PROVEN-LIVE (a mapped row PASSed) > BUILT-UNPROVEN (every probe present) > PARTIAL (some) > NOT BUILT (none).
A feature's status (Works in game / Built, not yet seen / Partly built / Not built) is derived from its capabilities in
feature_status() and nowhere else.

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
         probes=["cs:class RM_Patch_ExplosionLightsLiquid", "set:explosionIgnitesLiquidEnabled"], src="Ph6"),
    dict(id="E09", g="E", label="Burning liquid can be put out", item=BP,
         effect="Firefighting / rain can extinguish burning liquid. Owed per Ph6 (only burn-out exists).",
         probes=["cs:IsSmothered", "set:foamSmothersLiquidFireEnabled", "set:rainDousesLiquidFireEnabled"], src="Ph6"),
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
         probes=["cs:class RM_PitRooms", "set:superdeepRoomsEnabled"], src="Collapse [D]"),
    dict(id="G02", g="G", label="A prisoner bed makes the pit a prison; fed and tended from the lip", item="SUPERDEEP_PRISON_ROOM_1",
         effect="With a vanilla prisoner bed the room is a prison on vanilla's terms; wardens never enter.",
         probes=["cs:class RM_Patch_PathFollower_LipService", "set:wardenFromLipEnabled"], src="Collapse Q1"),
    dict(id="G03", g="G", label="Capture down (from the lip)", item="SUPERDEEP_PRISON_ROOM_1",
         effect="A warden ADJACENT to the lip captures a trapped/downed pawn without entering the pit.",
         probes=["set:captureDownEnabled"], src="Collapse Q1 / [B-item]"),
    dict(id="G04", g="G", label="Convert down (recruit from the lip)", item="SUPERDEEP_PRISON_ROOM_1",
         effect="Recruitment/conversion interaction works from the lip; nobody climbs down.",
         probes=["cs:PrisonerConvert", "set:wardenFromLipEnabled"], src="Collapse Q1"),
    dict(id="G05", g="G", label="Too-wide creature is not offered capture down", item="SUPERDEEP_PRISON_ROOM_1",
         effect="A pawn the pit cannot hold (width rule) is not 'trapped' and gets no capture-down option.",
         probes=["set:captureDownEnabled", "set:pitWidthBodySizeMultiplier"], src="Owner Q4"),
    dict(id="G06", g="G", label="Open pit heats fast in sun, chills fast at night", item="PIT_TEMPERATURE_SOFTENING_1",
         effect="An unroofed superdeep room tracks ambient faster than a roofed room (coupling multiplier).",
         probes=["cs:class RM_Patch_PitRoomCoupling", "set:pitTemperatureCoupling"], src="Collapse Q5"),
    dict(id="G07", g="G", label="Exposure wears down resistance", item="PIT_TEMPERATURE_SOFTENING_1",
         effect="RM_PitExposure accumulates on an exposed occupant and lowers recruitment resistance; vanilla heat/cold does the harm.",
         probes=["cs:class RM_PitExposure", "xml:defName>RM_PitExposure<", "set:pitExposureEnabled",
                 "set:pitResistanceLossMultiplier"], src="Collapse [H]"),
    dict(id="G08", g="G", label="'Exposed Prisoner' thought: cruel, and reads as cruel", item="PIT_TEMPERATURE_SOFTENING_1",
         effect="Compassionate colonists feel it; psychopaths (built) and hard-morality cultures (NOT yet) do not.",
         probes=["xml:defName>RM_ExposedPrisoner<", "cs:FeelsForExposedPrisoners"],
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
         probes=["cs:IsFlowDoor\\(edifice\\)", "cs:class RM_PitFillEffects"], src="Fill-effects verify"),
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
         probes=["cs:class RM_Patch_PitDepthDraw", "cs:class SectionLayer_RMExcavationWalls", "tex:(?i)(excavation|pitwall|wallface|channel)"],
         bars=["pit_occupant_below_floor", "pit_occupied_distinguishable"], shots=["REF_quarry"], src="Rulings 33 + depth"),
    dict(id="J06", g="J", label="Wall-face art for all four depths (Quarry perspective)", item="EXCAVATION_WALL_ART_1",
         effect="Shared rim + per-depth wall gradient; every depth legible and different from the others.",
         probes=["cs:class SectionLayer_RMExcavationWalls", "tex:(?i)(excavation|pitwall|wallface|rim)"], bars=["pit_depth_ladder_legible", "pit_walls_have_visible_depth"],
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
    dict(id="L09", g="L", label="Rivers slice 1: river current + ford stones", item="SURFACE_RIVER_WEIRS_1",
         effect="Surface current on vanilla rivers, fordable stones, swept-away pawns (FlowWorks Rivers).",
         probes=["file:src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs",
                 "file:src/RimMandrake/FlowWorks/Defs/Rivers/RM_FordStones.xml"], src="River works design"),
    dict(id="L10", g="L", label="Weirs on ordinary rivers", item="SURFACE_RIVER_WEIRS_1",
         effect="Build a weir across a surface river to hold and raise water.",
         probes=["rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)weir"], src="Owner-typed 2026-09-26"),
    dict(id="L11", g="L", label="Silt-trap, stake-line and hopper bank-works", item="SURFACE_RIVER_WEIRS_1",
         effect="The bank-works family from the weir system, on surface rivers.",
         probes=["rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)silt", "rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)stake", "rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)hopper"],
         src="Owner-typed 2026-09-26"),
    dict(id="L12", g="L", label="Untended weir + flood = breach cascade", item="SURFACE_RIVER_WEIRS_1",
         effect="A weir left untended when a flood comes breaches and cascades downstream.",
         probes=["rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)breach"], src="Owner-typed 2026-09-26"),
    dict(id="L13", g="L", label="Rivers slice 2: fish catch, drift, ferry", item="SURFACE_RIVER_WEIRS_1",
         effect="The rest of the surface-river works beyond weirs and bank-works.",
         probes=["rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)ferry", "rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)drift", "rx:src/RimMandrake/FlowWorks/Source/Rivers:(?i)fish"],
         src="Remaining inventory #12"),
    # ---- M quarry
    dict(id="M01", g="M", label="Digging a canal turns up local materials (a lump on the bank)", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="Excavation can yield biome-local materials dropped on the bank (availability by biome, configurable).",
         probes=["cs:class RM_DigDiscovery\\b", "set:digFindsEnabled"], src="Quarry item / remaining inventory #6"),
    dict(id="M02", g="M", label="A letter on the first find of each material per map", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="The first time a material turns up on a map, a letter says what and where.",
         probes=["set:digFindLetterEnabled"], src="Remaining inventory #6"),
    dict(id="M03", g="M", label="Deep cuts reach deep-drill minerals; mineral-less biomes give rock chunks", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="Depth decides what can turn up; a biome with no minerals yields local rock chunks instead.",
         probes=["cs:ReachesDeep", "cs:LocalRockChunk"], src="Remaining inventory #6"),
    dict(id="M04", g="M", label="Reads the mineral abundance registry", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="What can turn up comes from the shared mineral abundance registry, not a FlowWorks list.",
         probes=["cs:MineralRegistry\\.\\w+\\("], src="Quarry item"),
    dict(id="M05", g="M", label="Sluice box: a stream slowly yields ore", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="Rivers half; waits on the rivers-carry column of MINERALS_WHERE_THEY_BELONG_1.",
         probes=["rx:src/RimMandrake:(?i)defName>\\w*SluiceBox"], src="Quarry item"),
    dict(id="M06", g="M", label="Panning for gold in a river", item="FLOWWORKS_QUARRY_DIGGING_1",
         effect="A colonist pans a river cell for a slow trickle of gold (Rivers half).",
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

# ------------------------------------------------------------------------------------------------ THE DESIGNER VIEW
# Owner, 2026-10-05, on the 139-row capability sheet: *"You proposed a review sheet that was not human readable. Bad
# medium for review."* So the sheet the owner READS is built from the table below, not from CAPS: ~45 FEATURES, each
# a sentence a designer would say, grouped into SECTIONS. CAPS stays the evidence layer — a feature's status is
# DERIVED from its capabilities (never typed here), and the technical detail lives behind a closed "details" toggle.
#
# PLAIN: one designer-language phrase per capability. Used wherever a single capability surfaces in the main view
# (the "what remains to build" list). Rule for every string here: no defName, class, setting, ticket, test or row id.
PLAIN = {
    "A01": "ordering a canal dug and a colonist digging it",
    "A02": "four dug depths, the deepest being a pit",
    "A03": "digging an existing canal one level deeper",
    "A04": "depth and fill saved with the map",
    "A05": "filling a canal back in",
    "A06": "dry trenches slowing people down, deeper slower",
    "A07": "a flooded trench being slower to cross than a dry one",
    "A08": "a pit being just the deepest dug ground, not a building",
    "B01": "flow moving in steady pulses",
    "B02": "a floor on how fast the pulse can be set",
    "B03": "a canal filling from its source in every direction",
    "B04": "two canals off one source both filling",
    "B05": "flow behaving the same way every time",
    "B06": "liquid staying inside the dug channel",
    "B07": "a settings switch that freezes all flow",
    "B08": "a part-filled canal looking different from a full one",
    "B09": "a canal showing the same liquid as its pond",
    "B10": "liquid being pushed along when a canal is filled in",
    "B11": "only liquid with nowhere at all to go being lost, and counted",
    "B12": "no liquid leaking or appearing from nowhere",
    "B13": "canyon floods running through the canals instead of erasing them",
    "C01": "any pond or lake acting as a source",
    "C02": "lakes touching the map edge never running dry",
    "C03": "a never-dry lake staying never-dry as it shrinks",
    "C04": "an enclosed pond feeding about five canal tiles per tile, then stopping",
    "C05": "the pond visibly shrinking as it pays out",
    "C06": "a drawn-down pond slowly refilling",
    "C07": "rain filling open trenches but not roofed ones",
    "C08": "canals draining away off the map edge",
    "C09": "pumping a pond down into tanks",
    "D01": "tar flowing slower than water",
    "D02": "every wet tile remembering which liquid it holds",
    "D03": "two liquids meeting and stopping instead of mixing",
    "D04": "old saves keeping their liquids",
    "D05": "a map's liquid not silently switching after it fills",
    "D06": "different liquids looking different in a canal",
    "D07": "tar having a thick tar surface",
    "D08": "slime looking thick and opaque, not tinted water",
    "D09": "slime being nearly impossible to cross and slow to escape",
    "D10": "someone in slime being drawn sunk into it",
    "D11": "one list of every liquid and its forms",
    "D12": "canal liquids: water, tar, oil, poison and four slimes",
    "D13": "the wider set of liquids as ground (brine, boiling water, propane, acid)",
    "D14": "each liquid's look as a flood, rain, river, lake and sea",
    "E01": "any fire lighting burnable liquid",
    "E02": "flame travelling along a canal as a slow fuse or a fast blast",
    "E03": "a burning canal burning for days",
    "E04": "fire travelling back into the pond",
    "E05": "burning liquid looking alight (its own art)",
    "E06": "a burnt-out canal looking scorched (its own art)",
    "E07": "anyone in burning liquid catching fire",
    "E08": "an explosion lighting liquid",
    "E09": "putting burning liquid out with foam or rain",
    "E10": "corrosive liquids damaging what stands in them",
    "F01": "nobody climbing out of a pit",
    "F02": "a pit only holding creatures that fit its width",
    "F03": "your own colonists not being trapped",
    "F04": "falling into a pit hurting",
    "F05": "a 'jump in' button",
    "F06": "someone in a pit only trading shots with the edge",
    "F07": "raiders not wasting shots on someone in a pit",
    "F08": "a trapped creature not trying to flee off the map",
    "F09": "the info line saying someone is trapped",
    "F10": "an explosion or knockback throwing someone into a pit",
    "G01": "a walled-in pit area counting as a room",
    "G02": "a prisoner bed turning a pit into a prison, tended from the edge",
    "G03": "capturing someone in a pit from the edge",
    "G04": "recruiting or converting a prisoner from the edge",
    "G05": "no capture offered for a creature the pit can't hold",
    "G06": "an open pit getting hot by day and cold by night",
    "G07": "exposure wearing down a prisoner's resistance",
    "G08": "colonists with a conscience minding exposed prisoners",
    "H01": "a ladder that lets people out when lowered and strands them when raised",
    "H02": "ladders only going on dug ground",
    "H03": "spikes at the bottom of a pit",
    "H04": "spike damage: heavy, scaled to size, never instantly fatal",
    "H05": "a pit cover that looks like the ground",
    "H06": "falling through a cover when stepping on it",
    "H07": "three cover builds bearing different weights",
    "H08": "liquid in an occupied pit drowning non-swimmers",
    "H09": "poison in a pit poisoning whoever is in it",
    "H10": "oil in a pit that can be lit",
    "H11": "flooding an occupied pit by opening a gate",
    "H12": "no pit part borrowing the vanilla spike-trap drawing",
    "I01": "a cheap sluice gate in any material",
    "I02": "a grate door that holds a real prisoner",
    "I03": "gates that can't be opened from inside the pit",
    "I04": "letting a held creature out through a gate",
    "I05": "liquid flowing through an open gate or any grate",
    "I06": "a gate looking open or shut at a glance (its own art)",
    "J01": "people sitting lower at every deeper step",
    "J02": "people visibly lowering as they walk in",
    "J03": "people visibly rising as they climb out",
    "J04": "pit walls standing above the occupant's head",
    "J05": "an occupied pit reading differently from an empty one",
    "J06": "painted pit-wall art for all four depths",
    "J07": "spike art where some spike shows",
    "J08": "ladder art, raised and lowered",
    "J09": "a dug canal looking dug, not like a gravel path",
    "J10": "a pit reading as a big dark hole",
    "J11": "a large pit reading as one place, not a grid of tiles",
    "J12": "a bare pit never looking like a building",
    "J13": "depth and fill both readable at once",
    "J14": "trenches looking like obstacles without a tooltip",
    "K01": "bottles you fill at a shore or tank and use",
    "K02": "dirty bottles and washing them",
    "K03": "buckets and barrels",
    "K04": "boiling water cooling and blood spoiling in a bottle",
    "K05": "bottles tagged for future cooking",
    "K06": "a liquid tank",
    "K07": "drills and taps bringing up underground liquid",
    "K08": "pumps",
    "K09": "hoses",
    "K10": "adapters joining pipe and hose networks",
    "K11": "ruined industrial liquid plants you find and repair",
    "K12": "water cleaning feeding into thirst",
    "L01": "new maps getting shores of the local liquid",
    "L02": "the world map knowing which liquid each region has",
    "L03": "coloured steam rising from hot rivers",
    "L04": "nobody swimming in sand for fun",
    "L05": "a swale slowly turning sand into soil",
    "L06": "the swale being locked in the campaign until found",
    "L07": "swale art drawn from a real canal",
    "L08": "crops beside a filled canal counting as watered",
    "L09": "river current and ford stones",
    "L10": "weirs on ordinary rivers",
    "L11": "silt traps, stake lines and hoppers on river banks",
    "L12": "an untended weir breaching in a flood",
    "L13": "fish catches, drift and ferries",
    "M01": "digging turning up local minerals",
    "M02": "a letter the first time each mineral turns up",
    "M03": "deep cuts reaching deep minerals; rock chunks where there are none",
    "M04": "finds following the shared list of which minerals belong where",
    "M05": "a sluice box slowly sifting ore from a stream",
    "M06": "panning a river for gold",
    "N01": "a settings switch for every mechanic",
    "N02": "the mod still digging dry canals with everything switched off",
    "N03": "settings that change new maps saying so",
    "N04": "the hooks automated tests read the game through",
}

# Plain captions for the pictures (the scene-group shots of the 2026-10-05 live test, the Quarry reference, and the
# 2026-09-16 art candidates). A caption says what you are looking at, never which test row produced it.
SHOT_CAPTIONS = {
    "S_ladder": "Live test, 5 Oct: a dug trench and a pit side by side (the test site's depth ladder)",
    "E2_flow": "Live test, 5 Oct: water spreading down a canal from its pond",
    "E3_E4": "Live test, 5 Oct: a pond feeding canals in four directions",
    "E5_sinks": "Live test, 5 Oct: a canal running to the map edge, where it drains away",
    "J_jobs": "Live test, 5 Oct: open vs roofed trenches in rain, a filled-in canal, and a dig order",
    "P_pits": "Live test, 5 Oct: pits of different widths with creatures in them; colonists at the ladder on the right",
    "X_promoted": "Live test, 5 Oct: people standing at each depth, a water and a tar canal, a slime pit, and a pit cover",
    "REF_quarry": "Your reference (16 Sept): the Quarry mod's pit walls, the look the pit art is aiming for",
    "ART_ladder_A": "Ladder drawing A (16 Sept): scrap-metal rails, lashed rungs",
    "ART_ladder_B": "Ladder drawing B (16 Sept): pegged desert timber with a stone counterweight",
}
ART = {   # art candidates the owner is asked to pick between (committed sources, copied into review/shots/)
    "ART_ladder_A": "src/RimMandrake/FlowWorks/art_source/phone_review_2026-09-16/RUT_Ladder_A.png",
    "ART_ladder_B": "src/RimMandrake/FlowWorks/art_source/phone_review_2026-09-16/RUT_Ladder_B.png",
}

SECTIONS = [
    ("dig", "1 · Digging canals and pits"),
    ("flow", "2 · Liquid in canals and ponds"),
    ("fire", "3 · Fire and corrosion"),
    ("catch", "4 · Pits: catching"),
    ("hold", "5 · Pits: holding prisoners"),
    ("look", "6 · How it looks"),
    ("carry", "7 · Bottles, tanks and pumps"),
    ("land", "8 · Rivers, shores and the land"),
]

# id, section, the designer's sentence, one plain line of what the player experiences, caps (decide the status),
# minor (count toward built / not built, never toward "works in game"), shots.
FEATURES = [
    # ---- 1 digging
    dict(id="dig_canal", s="dig", title="You mark ground and a colonist digs a canal there; dig again to go one level deeper",
         say="There are four depths. The fourth is a pit: nothing more than the deepest dug ground.",
         caps=["A01", "A02", "A03", "A08"], minor=["A04"], shots=["S_ladder"]),
    dict(id="dig_fill_in", s="dig", title="You can fill a canal back in, and the liquid in it is pushed along, not deleted",
         say="Only liquid with nowhere at all to go is lost, and the game counts it.",
         caps=["A05", "B10", "B11"], shots=["J_jobs"]),
    dict(id="dig_slows", s="dig", title="Trenches slow people down: deeper is slower, flooded is slower still, and a pit can't be crossed",
         say="A dug line is a real barrier you can build defences with.",
         caps=["A06", "A07"]),
    dict(id="dig_finds", s="dig", title="Digging a canal sometimes turns up local minerals, with a letter the first time each one appears",
         say="Deep cuts can reach the minerals deep drills find; where there are none, you get chunks of local rock.",
         caps=["M01", "M02", "M03", "M04"]),
    # ---- 2 flow
    dict(id="flow_spreads", s="flow", title="Liquid spreads along a canal from its pond, in every direction, and stays inside the dug channel",
         say="It moves in steady pulses, the same way every time; two canals off one pond both fill. Switching the "
             "engine off in settings freezes every canal where it is.",
         caps=["B03", "B04", "B06", "B01", "B05", "B12", "B07"], minor=["B02"], shots=["E2_flow"]),
    dict(id="flow_identity", s="flow", title="Each liquid keeps its own nature: tar crawls while water runs, and a canal shows the liquid it came from",
         say="Water fed from water looks like water; tar fed from tar looks like tar.",
         caps=["D01", "D02", "D05", "D06", "B09"], shots=["X_promoted"]),
    dict(id="flow_no_mix", s="flow", title="Two different liquids never mix: where their fronts meet, both stop",
         say="Drain one side and the other moves in. Old saves keep their liquids.", caps=["D03", "D04"]),
    dict(id="flow_ponds", s="flow", title="Any pond is a source: a lake touching the map edge never runs dry; an enclosed pond runs out",
         say="An enclosed pond feeds about five canal tiles for each tile of water, then the flow stops.",
         caps=["C01", "C02", "C03", "C04"], shots=["E3_E4"]),
    dict(id="flow_shrinks", s="flow", title="A pond visibly shrinks as it pays out, and slowly refills from rain, season and seepage",
         say="You can see a source being drawn down.", caps=["C05", "C06"], shots=["E3_E4"]),
    dict(id="flow_rain", s="flow", title="Rain fills open trenches; roofed ones stay dry",
         say="", caps=["C07"], shots=["J_jobs"]),
    dict(id="flow_drains", s="flow", title="A canal that runs off the edge of the map drains away",
         say="A canal ending inside the map holds its water.", caps=["C08"], shots=["E5_sinks"]),
    dict(id="flow_canyon", s="flow", title="Canyon floods run through your canals instead of wiping them out",
         say="", caps=["B13"]),
    dict(id="flow_slime", s="flow", title="Slime is nearly impossible to cross and slow to climb out of",
         say="Your words: so slippery it is nearly uncrossable.", caps=["D09"]),
    # ---- 3 fire
    dict(id="fire_lights", s="fire", title="Fire or an explosion lights tar, oil or propane, and the flame travels along the canal",
         say="Tar and propane creep like a fuse you can outrun; fuels go up fast.",
         caps=["E01", "E02", "E08"]),
    dict(id="fire_lasts", s="fire", title="A burning canal burns for days, spreads back into its pond, and sets anyone standing in it alight",
         say="About one canal level a day; a pond burns far longer. Corrosive liquids also eat whatever stands in "
             "them (that one is switched off by default).", caps=["E03", "E04", "E07", "E10"]),
    dict(id="fire_out", s="fire", title="Foam or rain puts burning liquid out",
         say="Foam keeps it out while the foam lies there; rain has a chance on open ground.", caps=["E09"]),
    # ---- 4 catching
    dict(id="pit_holds", s="catch", title="Anything that falls into a pit cannot climb out",
         say="It stays where it is; its info line says it is trapped.", caps=["F01"], minor=["F08", "F09"], shots=["P_pits"]),
    dict(id="pit_width", s="catch", title="A pit only holds a creature that fits: anything wider walks out, and narrowing a pit frees it",
         say="Your rule: the pit must be as wide as the creature.", caps=["F02"], shots=["P_pits"]),
    dict(id="pit_fall", s="catch", title="Falling in hurts, and your own colonists are not trapped unless you choose that in settings",
         say="", caps=["F03", "F04"], shots=["P_pits"]),
    dict(id="pit_shooting", s="catch", title="Someone in a pit can only shoot, and be shot at, from the pit's edge",
         say="Raiders don't waste shots on them from further away.", caps=["F06", "F07"]),
    dict(id="pit_ways_in", s="catch", title="A 'jump in' button drops a colonist in on purpose; explosions and knockback can throw people in",
         say="Whoever jumps in is stuck there too.", caps=["F05", "F10"]),
    dict(id="pit_cover", s="catch", title="A pit cover hides the hole and looks like the ground around it",
         say="A faint seam shows only at the closest zoom.", caps=["H05"], shots=["X_promoted"]),
    dict(id="pit_cover_drop", s="catch", title="Step on a cover and you fall through; three cover builds bear different weights",
         say="Plank lattice, woven scrap, reinforced frame.", caps=["H06", "H07"]),
    dict(id="pit_spikes", s="catch", title="Spikes at the bottom stab whoever falls in: badly, scaled to their size, never instantly fatal",
         say="Walking up to the spikes is harmless; only a fall triggers them.", caps=["H03", "H04"]),
    dict(id="pit_flood", s="catch", title="Flood an occupied pit to drown, poison or burn whoever is in it",
         say="Water drowns non-swimmers, poison builds up, oil can be lit; open a gate to let the liquid in.",
         caps=["H08", "H09", "H10", "H11"]),
    # ---- 5 holding
    dict(id="hold_ladder", s="hold", title="A ladder: lowered, people climb out; raised, they're stranded",
         say="It works like a prison door. Ladders only go on dug ground.", caps=["H01"], minor=["H02"], shots=["P_pits"]),
    dict(id="hold_prison", s="hold", title="A walled-in pit is a room; add a prisoner bed and it's a prison you run from the edge",
         say="Wardens feed, tend, capture, recruit and convert from the lip without climbing down; nothing too wide is offered.",
         caps=["G01", "G02", "G03", "G04", "G05"]),
    dict(id="hold_exposure", s="hold", title="An open pit bakes by day and freezes by night, wearing down a prisoner's resistance",
         say="Colonists whose beliefs mind cruelty are upset by it; psychopaths are not.", caps=["G06", "G07", "G08"]),
    dict(id="hold_gates", s="hold", title="Sluice gates and grate doors let liquid through but hold creatures and prisoners",
         say="They can't be opened from inside the pit; open one to let a held creature walk out.",
         caps=["I01", "I02", "I03", "I04", "I05"]),
    # ---- 6 look
    dict(id="look_sink", s="look", title="People sink as the ground deepens and rise as they climb out; in a pit the walls stand over their head",
         say="Someone in slime is drawn sunk into it, not standing on top.", caps=["J01", "J02", "J03", "J04", "D10"],
         shots=["X_promoted"]),
    dict(id="look_canal", s="look", title="A canal looks dug, not like a gravel path, and shows how full it is",
         say="Trace, half and brimming fills look different; trenches read as obstacles without a tooltip.",
         caps=["B08", "J09", "J14"], shots=["S_ladder"]),
    dict(id="look_pit", s="look", title="Pit walls are drawn with depth, Quarry-style, so a pit reads as one big dark hole",
         say="Every depth looks different; an occupied pit reads differently from an empty one; never like a building.",
         caps=["J05", "J06", "J10", "J11", "J12", "J13"], shots=["REF_quarry"]),
    dict(id="look_parts", s="look", title="Spikes, ladders and gates have their own drawings, not borrowed vanilla ones",
         say="Today the ladder still borrows the vanilla spike trap; gates borrow the vanilla door.",
         caps=["J07", "J08", "I06", "H12"], shots=["ART_ladder_A", "ART_ladder_B"]),
    dict(id="look_liquids", s="look", title="Tar looks thick and sticky; slime looks thick and opaque, not tinted water",
         say="", caps=["D07", "D08"]),
    dict(id="look_fire", s="look", title="Burning liquid looks alight, and a burnt-out canal looks scorched",
         say="Today it uses the vanilla fire and ash.", caps=["E05", "E06"]),
    # ---- 7 carry
    dict(id="carry_bottles", s="carry", title="Bottles, buckets and barrels: fill at a shore or tank, use, wash and reuse",
         say="Boiling water cools and blood spoils in a bottle; bottles are tagged for a future cooking mod.",
         caps=["K01", "K02", "K03", "K04", "K05"]),
    dict(id="carry_tanks", s="carry", title="Tanks store liquid; pumps move it from ponds and canals; hoses and adapters connect it all",
         say="One full tank holds about five canal tiles of liquid.", caps=["K06", "K08", "C09", "K09", "K10"]),
    dict(id="carry_drills", s="carry", title="Drills and taps bring underground liquids up, and cleaned water feeds thirst",
         say="", caps=["K07", "K12"]),
    dict(id="carry_industry", s="carry", title="Ruined industrial liquid plants (desalination, tar refinery, pumping station) are found and repaired",
         say="Never built from the menu in the campaign.", caps=["K11"]),
    # ---- 8 land
    dict(id="land_liquids", s="land", title="Many liquids exist as ground: brine, boiling water, propane, acid and more, each with its own flood, rain, river, lake and sea",
         say="Nobody goes swimming in sand for fun.", caps=["D11", "D12", "D13", "D14"], minor=["L04"]),
    dict(id="land_shores", s="land", title="New maps get shores of the local liquid, and hot rivers steam in colour",
         say="The shores change only newly generated maps.", caps=["L01", "L02", "L03"]),
    dict(id="land_swale", s="land", title="A water-fed canal improves the land: a swale turns sand into soil, and crops beside it count as watered",
         say="In the campaign the swale stays locked until found; its art comes from a real canal.",
         caps=["L05", "L06", "L07", "L08"]),
    dict(id="land_rivers", s="land", title="Rivers get current, ford stones, weirs, bank works, breaches in floods, fish catches and ferries",
         say="", caps=["L09", "L10", "L11", "L12", "L13"]),
    dict(id="land_panning", s="land", title="Pan a river for gold, or set a sluice box to sift ore from a stream",
         say="", caps=["M05", "M06"]),
    dict(id="land_settings", s="land", title="Every mechanic can be switched off in Mod Settings, and with everything off the mod still digs dry canals",
         say="", caps=["N01", "N02", "N03"], minor=["N04"]),
]

# Plain status vocabulary: ONE badge per feature, shown once.
F_WORKS, F_BUILT, F_PARTLY, F_NOT = "works", "built", "partly", "not"
F_LABEL = {F_WORKS: "Works in game", F_BUILT: "Built, not yet seen", F_PARTLY: "Partly built", F_NOT: "Not built"}
F_COLOR = {F_WORKS: "#6fae5a", F_BUILT: "#5390c4", F_PARTLY: "#c9a44a", F_NOT: "#c96634"}
F_ORDER = (F_WORKS, F_BUILT, F_PARTLY, F_NOT)
F_MEANS = {
    F_WORKS: "a test in the running game passed for every part of it. Whether it LOOKS right is your call.",
    F_BUILT: "everything is built, but it has not yet been seen working in a running game.",
    F_PARTLY: "some parts are built and some are not.",
    F_NOT: "nothing of it is built yet.",
}

# What I need from you: at most five, each shown only while it is still open (`open_if` reads derived state).
ASKS = [
    dict(id="ask_ladder", title="Pick the ladder drawing: A or B",
         say="Two ladder drawings were made on 16 Sept and never picked; until you pick, the ladder borrows the vanilla "
             "spike-trap picture. Both were drawn before your Quarry-perspective ruling, so 'Not right' means: redraw "
             "it in perspective.",
         short="Two drawings from 16 Sept, never picked; the ladder borrows the vanilla spike trap until you do.",
         shots=["ART_ladder_A", "ART_ladder_B"], kind="pick", open_if=("cap_missing", "J08")),
    dict(id="ask_numbers", title="Sanity-check the first-guess numbers",
         say="You ruled these ship as first guesses and get tuned in live play. Say if any sounds wrong: "
             "people sink 0.3 of a tile per depth level (so pit walls stand 1.2x a person's height); spikes deal three "
             "stabs totalling about 40 for a person, 96 for a muffalo, 160 for a thrumbo; an enclosed pond feeds 5 "
             "canal tiles per tile of water; canal digging can turn up at most 5% of the ore in a map's rock; "
             "about 1 in 70 dug tiles turns something up.",
         short="How far people sink, spike damage, how far a pond reaches, how much digging turns up.",
         kind="numbers", open_if=None),
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
                        t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                        if kind == "cs":   # a probe must find CODE: a comment naming a class is not the class
                            t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
                            t = re.sub(r"(?m)^\s*//.*$|(?<=[;{}),])\s*//.*$", " ", t)
                        out.append(t)
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


# ------------------------------------------------------------------------------------------------ designer derivation
def ledger_needs(ids):
    """-> {item: (needs, blocked_on)} from the rimflow ledger; {} when it cannot be read (waits then read 'unknown')."""
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))
    try:
        from rimflow import cli
        _, w = cli.load()
    except (Exception, SystemExit):
        return {}
    out = {}
    for i in ids:
        it = w.items.get(i)
        if it:
            out[i] = (getattr(it, "needs", "") or "", getattr(it, "blocked_on", None) or "")
    return out


def feature_status(f, capd):
    """-> (status key, part_seen). The ONLY place a feature's status is decided; it reads its capabilities' derived
    statuses and nothing typed. core caps decide 'works in game'; minor caps can only hold a feature back from built."""
    core = [capd[c]["d"]["status"] for c in f["caps"]]
    allst = core + [capd[c]["d"]["status"] for c in f.get("minor", [])]
    built = ("PROVEN-LIVE", "BUILT-UNPROVEN")
    if all(s == "NOT BUILT" for s in allst):
        return F_NOT, False
    if not all(s in built for s in allst):
        return F_PARTLY, any(s == "PROVEN-LIVE" for s in core)
    if all(s == "PROVEN-LIVE" for s in core):
        return F_WORKS, True
    return F_BUILT, any(s == "PROVEN-LIVE" for s in core)


WAITS = ("you", "other", "nothing", "unfiled", "unknown")
WAITS_HEAD = {"you": "Waiting on you", "other": "Waiting on other work first",
              "nothing": "Nothing in the way: ready to build", "unfiled": "Not built, and no open work item for it",
              "unknown": "Could not read the work list (unknown)"}


def waits_on(item, states, needs):
    st = states.get(item, ("?", ""))[0]
    if st == "UNMEASURED":
        return "unknown"
    if st not in OPEN_STATES:
        return "unfiled"
    nd, blocked = needs.get(item, ("", ""))
    if nd == "owner":
        return "you"
    if blocked:
        return "other"
    return "nothing"


def remains_plain(feats, capd, states, needs):
    """-> {waits: [(feature, [phrases])]}: every feature with an unbuilt part, its missing parts in plain words, grouped
    by what it waits on (read from the ledger: needs=owner -> you; blocked_on -> other work; closed/unfiled -> no item)."""
    out = {w: [] for w in WAITS}
    for f in feats:
        by = {}
        for c in f["caps"] + f.get("minor", []):
            if capd[c]["d"]["status"] in ("NOT BUILT", "PARTIAL"):
                w = waits_on(capd[c]["item"], states, needs)
                by.setdefault(w, []).append(PLAIN.get(c, capd[c]["label"]))
        for w, ph in by.items():
            out[w].append((f, ph))
    return {w: v for w, v in out.items() if v}


def asks_open(capd, feats_d):
    out = []
    for a in ASKS:
        cond = a.get("open_if")
        if cond and cond[0] == "cap_missing" and capd[cond[1]]["d"]["status"] in ("PROVEN-LIVE", "BUILT-UNPROVEN"):
            continue
        out.append(a)
    return out[:5]


# ------------------------------------------------------------------------------------------------ the sheet
CSS = r"""<style id="FWSTYLE">
/* FlowWorks designer sheet: the owner's warm dark-brown palette, text >= 16px, one column on a phone. */
:root{--bg:#171310;--panel:#211b16;--panel2:#1c1713;--line:#3a2f24;--ink:#efe7d9;--dim:#b3a892;--accent:#e0803a;
  --link:#f0c08a;--ok:#6fae5a;--warn:#c9a44a;--bad:#c96634;--info:#5390c4}
html,body{font:17px/1.5 ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--ink);overflow-x:hidden;margin:0}
.hrow h1{font-size:21px}.sub{font-size:16px;color:var(--dim)}
.panel{font-size:16px;background:var(--panel2)}.panel h3{font-size:16px}
#posturePanel{display:none}
.crit{font-size:16px;color:var(--dim)}
.btn{font-size:16px;padding:6px 12px;background:#2a221b;border-color:var(--line)}
.btn:hover{background:#352a20}.btn.pri,.btn.on{background:#3a2a1c;border-color:#6b4a2a;color:var(--link)}
.bar{background:#1c1713;border-top-color:var(--line)}
.bar input[type=search],.bar select{font-size:16px;background:#120f0c;border-color:var(--line);min-width:0}
.bar input[type=search]{flex:1 1 220px}
#fmark,#btnGrid,#cell{display:none !important}
kbd{font-size:14px}
.panel h3,.pathbar b{font-size:16px}
.pill{font-size:16px;background:#120f0c;border-color:var(--line)}
.pathbar{font-size:16px;background:var(--panel2)}
.gh{font-size:19px;background:#2a2119;color:var(--accent);padding:10px 18px;border-color:var(--line)}
.gh .ghcount{display:none}.gh .ghbulk button{font-size:16px;padding:4px 10px}
.row{flex-wrap:wrap;gap:14px;padding:16px 18px;border-bottom:1px solid var(--line)}
.row:hover{background:#1f1914}.row.focus{background:#2a2119;box-shadow:inset 4px 0 0 var(--accent)}
.row[style*="color"]{box-shadow:inset 6px 0 0 currentColor}
.label{font-size:19px;color:var(--ink);font-weight:650;line-height:1.35}.label .id{display:none}
.effect{font-size:16px;color:#d9cfbf;margin-top:6px}
.main{flex:1 1 380px}
.ctrl{width:270px;flex:0 0 270px}
.opts button{font-size:16px;padding:9px 6px;background:#241d17;border-color:var(--line);color:var(--ink)}
.opts button.sel{color:#171310}
.note{font-size:16px;background:#120f0c;border-color:#4a3c2c;color:var(--ink);min-height:40px}
.note::placeholder{color:#8a7d68}
.mark{font-size:16px}
.badge{display:inline-block;font-size:16px;font-weight:700;color:#171310;border-radius:999px;padding:3px 12px;
  margin:0 0 6px;letter-spacing:.2px}
.seen{font-size:16px;color:var(--dim);margin-left:8px}
.pics{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
.pic{margin:0;width:230px;max-width:100%;cursor:zoom-in}
.pic img{width:100%;height:150px;object-fit:cover;border-radius:6px;border:1px solid var(--line);display:block;background:#120f0c}
.pic.art img{object-fit:contain;background:#3a3a3a}
.pic figcaption{font-size:16px;color:var(--dim);margin-top:4px;line-height:1.35}
.nopic{font-size:16px;color:#8a7d68;margin-top:8px;font-style:italic}
.missing{font-size:16px;color:#e8c9a0;margin-top:8px}
details.tech{margin-top:10px;font-size:16px;color:var(--dim)}
details.tech summary{cursor:pointer;font-size:16px;color:#8a7d68;width:max-content}
details.tech table{border-collapse:collapse;margin-top:6px;width:100%}
details.tech td{border-top:1px solid var(--line);padding:4px 6px;vertical-align:top;word-break:break-word}
details.tech code{font-size:15px;color:#cdbb9c}
.secfoot{padding:10px 18px 18px;font-size:16px;color:var(--dim);border-bottom:2px solid var(--line);background:#1a1511}
.secfoot b{font-weight:700}
#zoom img{image-rendering:auto;max-width:92vw;max-height:80vh}
#zoom .cap{font-size:16px}
/* the at-a-glance panel: outside the sticky header, so it scrolls away like the top of a document */
#glance{padding:18px;max-width:1200px}
#glance h2{font-size:24px;margin:0 0 6px}
#glance h3{font-size:18px;margin:18px 0 8px;color:var(--accent)}
#glance h4{font-size:16px;margin:12px 0 4px;color:var(--ink)}
#glance p,#glance li{font-size:16px}
#glance a{color:var(--link)}
.gtot{font-size:18px;margin:6px 0 12px}
.legend{font-size:16px;color:var(--dim);margin:6px 0 10px}.legend div{margin:2px 0}
.dot{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.mrow{display:grid;grid-template-columns:minmax(150px,260px) 1fr;gap:10px;align-items:center;margin:5px 0;
  color:inherit;text-decoration:none}
.mrow:hover .mname{text-decoration:underline}
.mname{font-size:16px}
.mbar{display:flex;height:26px;border-radius:5px;overflow:hidden;background:#120f0c;border:1px solid var(--line)}
.mbar i{display:flex;align-items:center;justify-content:center;font-style:normal;font-size:16px;font-weight:700;
  color:#171310;min-width:22px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:22px}
.cols ol,.cols ul{padding-left:22px;margin:4px 0}
.cols li{margin:4px 0}
.waitt{font-size:16px;color:var(--dim)}
@media (max-width:760px){
  .row{flex-direction:column}.ctrl{width:100%;flex:1 1 auto}.main{flex:1 1 auto}
  .pic{width:100%}.pic img{height:190px}
  .mrow{grid-template-columns:1fr}
  #glance{padding:14px 16px}
  .hrow,.bar,.gh,.row,.secfoot{padding-left:16px;padding-right:16px}
  header{position:static}.gh{top:0 !important}   /* a sticky header would cover a phone screen */
  .bar select,.bar .btn{flex:1 1 auto}
}
</style>
"""

RENDER_JS = r"""<script id="RENDER">
window.itemBody = it => {
  const e = window.esc, s = it.fw || {};
  const pics = (s.pics || []).map(p => `<figure class="pic${p[2] ? ' art' : ''}" data-zoom="${e(p[0])}" data-cap="${e(p[1])}">`
    + `<img src="${e(p[0])}" loading="lazy" decoding="async" alt="${e(p[1])}"><figcaption>${e(p[1])}</figcaption></figure>`).join('');
  const badge = s.status ? `<span class="badge" style="background:${e(s.color)}" title="${e(s.means)}">${e(s.label)}</span>`
    + (s.seen ? '<span class="seen">part of it was seen working in the game</span>' : '') : '';
  const pre = s.pre ? `<div class="waitt" style="margin-top:6px">${e(s.pre)}</div>` : '';
  const missing = (s.missing || []).length ? `<div class="missing">Still to build: ${e(s.missing.join('; '))}.</div>` : '';
  const tech = (s.tech || []).map(r => `<tr><td>${e(r[0])}</td><td>${e(r[1])}</td><td><code>${e(r[2])}</code></td></tr>`).join('');
  return `${badge}<div class="effect">${e(it.say || '')}</div>${missing}${pre}`
    + (pics ? `<div class="pics">${pics}</div>` : (s.status ? '<div class="nopic">no picture yet</div>' : ''))
    + (tech ? `<details class="tech"><summary>details</summary><table>${tech}</table></details>` : '');
};
window.itemOptions = it => {
  const want = (it.fw || {}).opts || ['ok', 'wrong', 'unwanted'];
  return want.map(k => OPTS.find(o => o.key === k)).filter(Boolean);
};
</script>
"""

AFTER_JS = r"""<script id="FWAFTER">
"use strict";
/* Plain-language chrome on top of the template, run after every paintCounts (which render() also calls): section
   summary lines at the END of each section, a plain progress counter, no bulk buttons on the asks group, and the
   glance panel's jump links. Hotkeys a row does not offer are swallowed rather than recorded. */
(function () {
  const FW = JSON.parse(document.getElementById('FWDATA').textContent);
  const LBL = FW.labels, COL = FW.colors, ORD = FW.order;
  const mine = it => { const d = decOf(it.id);
    return !!(d && d.decision && (d.decidedAt || isOverride(it.id) || prefillOf(it) == null)); };
  function sectionLine(group) {
    const rows = ITEMS.filter(it => it.group === group && it.fw && it.fw.status);
    if (!rows.length) return '';
    const n = {}; for (const it of rows) n[it.fw.status] = (n[it.fw.status] || 0) + 1;
    const marked = rows.filter(mine).length;
    return ORD.filter(k => n[k]).map(k => `<b style="color:${COL[k]}">${n[k]}</b> ${LBL[k].toLowerCase()}`).join(' · ')
      + ` &nbsp;—&nbsp; you have marked ${marked} of ${rows.length}`;
  }
  function fwAfter() {
    const list = document.getElementById('list');
    for (const f of list.querySelectorAll('.secfoot')) f.remove();
    const heads = [...list.querySelectorAll('.gh')];
    heads.forEach((gh, i) => {
      const name = gh.firstChild ? gh.firstChild.textContent : '';
      if (name === FW.askGroup) for (const b of gh.querySelectorAll('[data-bulk]')) b.remove();
      const line = sectionLine(name);
      if (!line) return;
      let last = gh, n = gh.nextElementSibling;
      while (n && !n.classList.contains('gh')) { last = n; n = n.nextElementSibling; }
      last.insertAdjacentHTML('afterend', `<div class="secfoot">${line}</div>`);
    });
    const total = ITEMS.length, done = ITEMS.filter(mine).length;
    const pre = ITEMS.filter(it => decisionOf(it.id) && !mine(it)).length;
    const notes = ITEMS.filter(it => String((decOf(it.id) || {}).note || '').trim()).length;
    const p = document.getElementById('progress');
    if (p) p.innerHTML = `<b>${done}</b> of ${total} marked by you` + (pre ? ` · ${pre} pre-marked by me` : '')
      + (notes ? ` · ${notes} with a note` : '');
    const g = document.getElementById('gprog');
    if (g) g.textContent = `${done} of ${total} marked by you so far`;
  }
  const orig = window.paintCounts;
  window.paintCounts = function () { orig.apply(this, arguments); try { fwAfter(); } catch (e) { console.error(e); } };
  if (document.querySelector('#list .row')) fwAfter();
  addEventListener('keydown', e => {
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || e.metaKey || e.ctrlKey || e.altKey) return;
    const op = OPTS.find(o => o.hotkey === e.key); if (!op) return;
    const it = shown[focusIdx >= 0 ? focusIdx : 0]; if (!it) return;
    if (!window.itemOptions(it).some(o => o.key === op.key)) { e.stopImmediatePropagation(); e.preventDefault(); }
  }, true);
  document.addEventListener('click', e => {
    const a = e.target.closest('[data-goto]'); if (!a) return;
    e.preventDefault();
    for (const id of ['q', 'fstate', 'fgroup']) { const x = document.getElementById(id); if (x && x.value) { x.value = ''; render(); } }
    const row = document.querySelector(`.row[data-id="${a.dataset.goto}"]`); if (!row) return;
    const hh = document.querySelector('header').offsetHeight + 50;
    scrollTo({ top: row.getBoundingClientRect().top + scrollY - hh, behavior: 'smooth' });
    focusIdx = shown.findIndex(x => x.id === a.dataset.goto); paintFocus(false);
  });
})();
</script>
"""


def _esc(x):
    return html.escape(str(x))


def _cap1(s):
    return s[:1].upper() + s[1:] if s else s


def ensure_art(out_dir):
    """Copy the art candidates the owner is asked to pick between into <out_dir>/shots/ (PNG, alpha kept)."""
    got = {}
    for name, src in ART.items():
        rel = "shots/%s.png" % name
        target = os.path.join(out_dir, rel)
        committed = os.path.join(REVIEW, rel)
        for s in (target, committed, os.path.join(REPO, src)):
            if os.path.exists(s):
                if s != target:
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with open(s, "rb") as a, open(target, "wb") as b:
                        b.write(a.read())
                got[name] = rel
                break
    return got


def glance_html(sec_counts, totals, nfeat, asks, rem, board_rel):
    seg = []
    for key, name in SECTIONS:
        n = sec_counts.get(key, {})
        tot = sum(n.values())
        if not tot:
            continue
        bars = "".join('<i style="flex:%d;background:%s" title="%d %s">%d</i>' % (n[k], F_COLOR[k], n[k], F_LABEL[k].lower(), n[k])
                       for k in F_ORDER if n.get(k))
        first = next(f["id"] for f in FEATURES if f["s"] == key)
        seg.append('<a class="mrow" href="#" data-goto="%s"><span class="mname">%s</span><span class="mbar">%s</span></a>'
                   % (_esc(first), _esc(name.split(" · ", 1)[-1]), bars))
    legend = "".join('<div><i class="dot" style="background:%s"></i><b>%s</b>: %s</div>' % (F_COLOR[k], F_LABEL[k], _esc(F_MEANS[k]))
                     for k in F_ORDER)
    tot_line = " · ".join('<b style="color:%s">%d</b> %s' % (F_COLOR[k], totals.get(k, 0), F_LABEL[k].lower()) for k in F_ORDER)
    ask_li = "".join('<li><a href="#" data-goto="%s"><b>%s</b></a><br><span class="waitt">%s</span></li>'
                     % (_esc(a["id"]), _esc(a["title"]), _esc(a.get("short") or a["say"])) for a in asks)
    rem_html = ""
    for w in WAITS:
        if w not in rem:
            continue
        rem_html += "<h4>%s</h4><ul>" % _esc(WAITS_HEAD[w])
        for f, ph in rem[w]:
            rem_html += '<li>%s <a href="#" data-goto="%s" class="waitt">(%s)</a></li>' % (
                _esc(_cap1("; ".join(ph))) + ".", _esc(f["id"]), _esc(dict(SECTIONS)[f["s"]].split(" · ", 1)[-1]))
        rem_html += "</ul>"
    return (
        '<section id="glance">'
        '<h2>FlowWorks at a glance</h2>'
        '<p class="gtot">%d features: %s</p>'
        '<div>%s</div>'
        '<div class="legend">%s</div>'
        '<p><a href="%s" target="_blank" rel="noopener">Read it as a plain status board, top to bottom (printable)</a>'
        ' &nbsp;·&nbsp; <span id="gprog"></span></p>'
        '<div class="cols"><div><h3>What I need from you</h3><ol>%s</ol>'
        '<p class="waitt">Everything below is yours to mark too: <b>OK</b>, <b>Not right</b> (say why in the note) or '
        "<b>Don't want</b>. Only unbuilt features still on the work list start pre-marked OK.</p></div>"
        '<div><h3>What remains to build</h3>%s</div></div>'
        '</section>'
    ) % (nfeat, tot_line, "".join(seg), legend, _esc(board_rel), ask_li, rem_html or "<p>Nothing: every part is built.</p>")


def board_html(feats_d, sec_counts, totals, asks, rem, stamp):
    """A plain status board that reads top to bottom like a document: no controls, printable."""
    css = CSS.replace('<style id="FWSTYLE">', "").replace("</style>", "") + r"""
body{max-width:980px;margin:0 auto;padding:20px 18px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:22px;margin:28px 0 4px;color:var(--accent);border-bottom:1px solid var(--line);padding-bottom:4px}
.f{margin:14px 0;padding-left:12px;border-left:4px solid var(--line)}
.f .t{font-size:18px;font-weight:650}
.sum{color:var(--dim);font-size:16px;margin:2px 0 8px}
.pics .pic{width:200px}.pics .pic img{height:120px}
@media print{html,body{background:#fff;color:#000}.effect,.sum,.pic figcaption{color:#333}.missing{color:#7a4a10}
  .f{break-inside:avoid}.pic img{border-color:#999}}
"""
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1"><title>FlowWorks status board</title>'
           '<style>%s</style></head><body>' % css]
    out.append("<h1>FlowWorks status board</h1><p class='sum'>Generated %s from the code on disk, the newest live test "
               "result and the work list. The review sheet is where you mark things; this page is for reading.</p>" % _esc(stamp))
    out.append("<p class='gtot'>%d features: %s</p>" % (len(feats_d), " · ".join(
        '<b style="color:%s">%d</b> %s' % (F_COLOR[k], totals.get(k, 0), F_LABEL[k].lower()) for k in F_ORDER)))
    if asks:
        out.append("<h2>What I need from you</h2><ol>%s</ol>" % "".join(
            "<li><b>%s</b>: %s</li>" % (_esc(a["title"]), _esc(a["say"])) for a in asks))
    for key, name in SECTIONS:
        fs = [f for f in feats_d if f["s"] == key]
        if not fs:
            continue
        n = sec_counts.get(key, {})
        out.append("<h2>%s</h2><p class='sum'>%s</p>" % (_esc(name.split(" · ", 1)[-1]), " · ".join(
            '<b style="color:%s">%d</b> %s' % (F_COLOR[k], n[k], F_LABEL[k].lower()) for k in F_ORDER if n.get(k))))
        for f in fs:
            pics = "".join('<figure class="pic%s"><img src="%s" alt=""><figcaption>%s</figcaption></figure>'
                           % (" art" if p[2] else "", _esc(p[0]), _esc(p[1])) for p in f["pics"][:2])
            out.append('<div class="f"><span class="badge" style="background:%s">%s</span>%s<div class="t">%s</div>'
                       '<div class="effect">%s</div>%s%s</div>' % (
                           F_COLOR[f["status"]], F_LABEL[f["status"]],
                           '<span class="seen">part of it was seen working in the game</span>' if f["seen"] else "",
                           _esc(f["title"]), _esc(f["say"]),
                           ('<div class="missing">Still to build: %s.</div>' % _esc("; ".join(f["missing"]))) if f["missing"] else "",
                           ('<div class="pics">%s</div>' % pics) if pics else ""))
    out.append("<h2>What remains to build</h2>")
    for w in WAITS:
        if w in rem:
            out.append("<h3>%s</h3><ul>%s</ul>" % (_esc(WAITS_HEAD[w]), "".join(
                "<li>%s (%s)</li>" % (_esc(_cap1("; ".join(ph))) + ".", _esc(f["title"])) for f, ph in rem[w])))
    out.append("</body></html>")
    return "\n".join(out)


BOARD_NAME = "FlowWorks_status_board.html"
PRE_NOTE = ("Pre-marked OK by me: the missing part is on the work list, so I assumed you still want it. "
            "Mark Don't want if you don't.")


def build(out=DEFAULT_OUT, result=None, states=None, probe_fn=probe, caps=None, write_decisions=True, needs=None,
          feats=None):
    caps = caps if caps is not None else CAPS
    feats = feats if feats is not None else FEATURES
    out = os.path.abspath(out)
    out_dir = os.path.dirname(out)
    os.makedirs(out_dir, exist_ok=True)
    rlabel, rows = latest_result(result)
    item_ids = sorted({c["item"] for c in caps})
    if states is None:
        states = ledger_states(item_ids)
        needs = ledger_needs(item_ids) if needs is None else needs
    needs = needs or {}
    shots = ensure_shots(out_dir)
    shots.update(ensure_art(out_dir))
    must, cannot, walk_state = walk_bars()
    caps_d = [dict(c, d=derive_status(c, rows, probe_fn)) for c in caps]
    capd = {c["id"]: c for c in caps_d}
    counts = {s: sum(1 for c in caps_d if c["d"]["status"] == s) for s in STATUSES}
    rem_items = remains(caps_d, states)
    covered = {b for c in caps for b in c.get("bars", [])}
    uncovered = [b for b in must + cannot if b not in covered]

    def pics_of(names):
        return [(shots[n], SHOT_CAPTIONS.get(n, n), n.startswith("ART_")) for n in names if n in shots]

    feats_d = []
    for f in feats:
        st, seen = feature_status(f, capd)
        missing = [PLAIN.get(c, capd[c]["label"]) for c in f["caps"] + f.get("minor", [])
                   if capd[c]["d"]["status"] in ("NOT BUILT", "PARTIAL")]
        tech = []
        for c in f["caps"] + f.get("minor", []):
            d = capd[c]["d"]
            ev = ["%s (%s)" % (capd[c]["item"], states.get(capd[c]["item"], ("?", ""))[0])]
            ev += ["live test %s: %s" % (r, s) for r, s in d["live"]]
            ev += ["%s %s" % ("✓" if ok else "✗", p) for p, ok in d["probes"]]
            tech.append((PLAIN.get(c, c), "%s · %s" % (c, d["status"]), " · ".join(ev)))
        feats_d.append(dict(f, status=st, seen=seen and st != F_WORKS, missing=missing, tech=tech,
                            pics=pics_of(f.get("shots", []))))
    totals = {k: sum(1 for f in feats_d if f["status"] == k) for k in F_ORDER}
    sec_counts = {}
    for f in feats_d:
        sec_counts.setdefault(f["s"], {}).setdefault(f["status"], 0)
        sec_counts[f["s"]][f["status"]] += 1
    rem = remains_plain(feats, capd, states, needs)
    asks = asks_open(capd, feats_d)
    n_works = totals.get(F_WORKS, 0)
    if n_works and len(asks) < 5:
        asks.append(dict(id=next(f["id"] for f in feats_d if f["status"] == F_WORKS),
                         title="Look at the %d features that work in game, and say if they look right" % n_works,
                         say="A test in the running game proved each one works; only your eyes can say it looks and "
                             "feels right. The pictures on each one are from that test.", kind="pointer"))
    if "unfiled" in rem and len(asks) < 5:
        asks.append(dict(id=rem["unfiled"][0][0]["id"],
                         title=("%d unbuilt parts have no open work item: do you still want them?" % len(rem["unfiled"])
                                if len(rem["unfiled"]) > 1 else "One unbuilt part has no open work item: do you still want it?"),
                         say="Mark the feature Don't want if not; otherwise it gets filed.", kind="pointer"))

    ask_group = "0 · What I need from you"
    items = []
    for a in asks:
        if a.get("kind") == "pointer":
            continue
        items.append(dict(id=a["id"], label=a["title"], group=ask_group, effect=a["say"], say=a["say"],
                          fw=dict(pics=pics_of(a.get("shots", [])),
                                  opts=["pickA", "pickB", "wrong"] if a["kind"] == "pick" else ["ok", "wrong"])))
    sec_name = dict(SECTIONS)
    for f in feats_d:
        waits = {waits_on(capd[c]["item"], states, needs) for c in f["caps"] + f.get("minor", [])
                 if capd[c]["d"]["status"] in ("NOT BUILT", "PARTIAL")}
        planned = bool(waits) and waits <= {"you", "other", "nothing"}
        items.append(dict(id=f["id"], label=f["title"], group=sec_name[f["s"]], effect=(f["title"] + " " + f["say"]).strip(),
                          say=f["say"], prefill="ok" if planned else None,
                          fw=dict(status=f["status"], label=F_LABEL[f["status"]], color=F_COLOR[f["status"]],
                                  means=F_MEANS[f["status"]], seen=f["seen"], missing=f["missing"], tech=f["tech"],
                                  pics=f["pics"], pre=PRE_NOTE if planned else "")))

    brief = (
        "<p><b>What this is:</b> every FlowWorks feature, built or not, in plain words, so you can see what exists, what "
        "works, what doesn't and what remains. Each feature carries <b>one</b> status, worked out from the code on disk and "
        "the newest live test; nobody typed it. The small <i>details</i> toggle on a feature holds the technical evidence.</p>"
        "<p><b>Your buttons:</b> <b>OK</b> · <b>Not right</b> (say why in the note) · <b>Don't want</b> (drop it from the "
        "plan). Keys: <kbd>j</kbd>/<kbd>k</kbd> move, <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> mark, <kbd>n</kbd> note, "
        "<kbd>?</kbd> all keys. Each section has an <b>all ok</b> button. The only rows I pre-marked are unbuilt "
        "features still on the work list (OK = still wanted; each says so). Nothing is removed by this sheet.</p>")
    config = {
        "sheetId": "flowworks_feature_review",
        "title": "FlowWorks: what exists, what works, what remains",
        "subtitle": "%d features · %s" % (len(feats_d), " · ".join("%d %s" % (totals.get(k, 0), F_LABEL[k].lower()) for k in F_ORDER)),
        "briefHtml": brief,
        "criterion": "part of the mod, nothing else. A status says whether a thing exists and passed a live test, never whether it looks right.",
        "invented": [],
        "posture": {"mode": "blacklist",
                    "explain": "Nothing is removed by this sheet; Don't want marks a feature to drop from the plan."},
        "options": [
            {"key": "ok", "label": "OK", "hotkey": "1", "color": F_COLOR[F_WORKS], "counts": "in"},
            {"key": "wrong", "label": "Not right", "hotkey": "2", "color": F_COLOR[F_NOT], "counts": "out", "bulk": False},
            {"key": "unwanted", "label": "Don't want", "hotkey": "3", "color": "#7d7565", "counts": "out", "bulk": False},
            {"key": "pickA", "label": "Pick A", "hotkey": "4", "color": F_COLOR[F_BUILT], "counts": "in", "bulk": False},
            {"key": "pickB", "label": "Pick B", "hotkey": "5", "color": F_COLOR[F_BUILT], "counts": "in", "bulk": False},
        ],
        "groupLabel": "section",
        "media": False,
        "decisionsFile": DEC_NAME,
        "decisionsPath": "", "sheetPath": "",
    }
    fwdata = {"labels": F_LABEL, "colors": F_COLOR, "order": list(F_ORDER), "askGroup": ask_group}
    tpl = open(TEMPLATE, encoding="utf-8").read()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(config, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items, indent=0).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<title>Review sheet</title>", "<title>FlowWorks feature review</title>", 1)
    assert tpl.count("</style>\n</head>") == 1, "template changed: cannot place the FlowWorks style"
    tpl = tpl.replace("</style>\n</head>", "</style>\n" + CSS + "</head>", 1)
    assert tpl.count('<div id="list"></div>') == 1, "template changed: cannot place the glance panel"
    tpl = tpl.replace('<div id="list"></div>', glance_html(sec_counts, totals, len(feats_d), asks, rem, BOARD_NAME)
                      + '\n<div id="list"></div>', 1)
    # the RENDER hook goes in LIVE, after the template's commented example (SKILL.md: a hook inside the comment is inert)
    marker = "-->\n\n<script>\n\"use strict\";"
    assert marker in tpl, "template changed: cannot place the RENDER hook"
    tpl = tpl.replace(marker, "-->\n" + RENDER_JS + "\n<script>\n\"use strict\";", 1)
    tail = "boot();\n</script>"
    assert tpl.count(tail) == 1, "template changed: cannot place the after-hook"
    tpl = tpl.replace(tail, tail + '\n<script id="FWDATA" type="application/json">%s</script>\n%s'
                      % (json.dumps(fwdata).replace("</", "<\\/"), AFTER_JS), 1)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(tpl)
    import datetime
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(out_dir, BOARD_NAME), "w", encoding="utf-8") as fh:
        fh.write(board_html(feats_d, sec_counts, totals, asks, rem, stamp))
    dec = os.path.join(out_dir, DEC_NAME)
    if write_decisions and not os.path.exists(dec):      # never overwrite: once it exists it is the owner's
        with open(dec, "w", encoding="utf-8") as fh:
            json.dump({"posture": "blacklist", "decisions": {},
                       "reviewStatus": {"state": "prefill", "by": None, "at": None,
                                        "evidence": "generated by FlowWorks/human_review.py; nobody has ruled"}}, fh, indent=1)
    return dict(out=out, items=items, counts=counts, remains=rem_items, uncovered=uncovered, result=rlabel, caps=caps_d,
                features=feats_d, totals=totals, remains_plain=rem, asks=asks, board=os.path.join(out_dir, BOARD_NAME))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--result", help="a specific validation_v2 result json (default: the newest)")
    a = ap.parse_args()
    r = build(a.out, a.result)
    print("%d features (%d capabilities underneath) -> %s" % (len(r["features"]), len(r["caps"]), r["out"]))
    print("  " + " · ".join("%d %s" % (r["totals"].get(k, 0), F_LABEL[k]) for k in F_ORDER))
    print("  result: %s" % r["result"])
    for w, v in r["remains_plain"].items():
        print("  %s: %d" % (WAITS_HEAD[w], len(v)))
    if r["uncovered"]:
        print("  bars with no capability: %s" % ", ".join(r["uncovered"]))


if __name__ == "__main__":
    main()
