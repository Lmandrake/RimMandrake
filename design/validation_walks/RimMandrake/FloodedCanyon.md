# RimMandrake: Flooded Canyon — validation walk
subject: src/RimMandrake/FloodedCanyon  (packageId `mandrake.rm.floodedcanyon`)
deps: `brrainz.harmony`, `mandrake.rm.flowworks` (modDependencies); `mandrake.rm.explosivegrowth` is an optional companion found by reflection (the soak does nothing without it). Fold-aware: if this biome is folded into `mandrake.rm.biomes` it is active under the composed name 'RimMandrake: Baroque Biomes'.
list: a tier carrying FlowWorks + FloodedCanyon + ExplosiveGrowth, all five DLCs, plain open biome map (the suite arms `featureInOtherBiomes` itself)
status-hint: FLOOD_CANYON_BIOME_1 / CRACKEDLANDS_MECHANICS_BUILD_1 — a canyon biome whose map floods on a clock: herald beats, chimes, a wall of water that soaks the ground, recedes to soil, leaves a feast and salvage and re-cuts fossil seams. Script: `src/RimMandrake/FloodedCanyon/validation.py` (plan `northstar_plan.py`), first script FLOODED_CANYON_FIRST_SCRIPT_1. NEVER RUN LIVE.

Sources: `About/About.xml`, `Source/RM_FloodedCanyonMod.cs` (25 settings), `RM_MapComponent_CanyonFlood.cs`, `RM_MapComponent_RecedeAftermath.cs`, `RM_FossilStrata.cs`, `Source/Debug/RM_FloodedCanyonDebugActions.cs` (the state surface), `Defs/`.

## must be true
- Every def the mod ships (biome, game condition, weather, sounds, creatures, hediff, fossil seams and display, wax suit, plant, genstep) resolves in the running game; a nonexistent control reads absent so the probe can say no. → defs_resolve.shipped_defs_resolve, defs_resolve.control_absent_def_reads_absent
- Every Mod Settings field the C# declares round-trips (write alt, read back, write default, read back). → flip_biomeRarityFactor.biomeRarityFactor_round_trips (and one `flip_<field>` chain per declared field, generated from the settings class)
- A run leaves every setting at its shipped default. → settings_restored.all_settings_at_shipped_defaults
- Off a canyon biome and with `featureInOtherBiomes` off, the flood cycle is inert. → feature_gate_off.cycle_inert_on_plain_map
- On (feature on), Arm brings the warning through to a standing flood on a non-empty footprint, and Recede clears the footprint, stamps the recede and schedules the next flood. → flood_cycle.arm_reaches_standing_flood, flood_cycle.recede_clears_footprint_and_reschedules
- The master switch `floodCycleEnabled` off stops the cycle. → master_switch_off.master_off_refuses_flood
- Five beats before water: Herald, then Warned (chimes), then Flooding, and the tarruq go silent; with `fiveBeatsEnabled` off there is no Herald and no hush. → warning_sequence_five_beats.herald_then_chime_then_wall, warning_sequence_five_beats.five_beats_off_skips_herald
- Every cell the flood wets is handed to Explosive Plant Growth as soaked; `growthCouplingEnabled` off hands none. → soak_coupling.flood_soaks_cells_via_explosive_growth
- The recede scatters floodline salvage; `floodlineSalvageEnabled` off scatters none. → recede_salvage.salvage_scattered_only_when_enabled
- The recede hatches the irqit carpet; `recedeFeastEnabled` off hatches none. → recede_feast.irqit_cohort_only_when_enabled
- The recede re-cuts fresh fossil seams along the wetted wall; `floodRecutSeamsEnabled` off cuts none. → recede_seams.recede_recuts_seams_only_when_enabled
- A pawn caught in the wall takes one light non-fatal hit; `floodDamageEnabled` off spares it. → UNCOVERED: the footprint is a map-wide BFS from a random seed, so a pawn cannot be placed under it; needs a seed control (named item to file: FLOODED_CANYON_PROBE_SEED_1); chain flood_damage_light_and_nonfatal records UNMEASURED
- A dug FlowWorks channel, pit or superdeep cell inside the footprint is filled by the flood, not erased, and is emptied again at recede. → UNCOVERED: needs FlowWorks excavation plus an F-level read and a seeded footprint (CANYON_FLOOD_ERASES_CANALS_1 is the engine side); chain excavated_cells_survive records UNMEASURED
- Peakstorm Light pulls the next flood forward (0.6 roll once per cycle). → UNCOVERED: statistical single roll, needs a seeded RNG; chain peakstorm_pulls_flood_forward records UNMEASURED
- The flood wakes the muttavaq (water reaching its pan) and at the dry it digs in. → UNCOVERED: needs a muttavaq on a flooded pan cell and a seeded footprint; chain muttavaq_wakes_and_digs_in records UNMEASURED
- The recede brings a flier migrant group on a biome that rosters flight-capable animals (`recedeMigrantsEnabled`). → UNCOVERED: a plain biome has none, needs an RM_FloodedCanyon map; chain recede_migrants records UNMEASURED
- The chime and herald audio and the water look. → UNCOVERED: audio and visual, judge pass or owner
- Ledges of Mercy: at the warning a trained animal runs for the nearest refuge ledge and reaches it; the flood never takes a ledge cell; `ledgeRefugeEnabled` off sends nobody. → ledge_refuge.trained_animal_runs_for_ledge, ledge_refuge.refuge_off_sends_nobody
- A neutral humanlike visitor runs for a ledge at the warning. → UNCOVERED: the suite's spawn_pawn makes only player or hostile pawns; chain ledge_refuge_neutral_visitor records UNMEASURED
- The staged chimes toll from the nearest chime-line anchor (`chimeAnchorsEnabled`). → UNCOVERED: no anchor def exists until the owner rules the ledge/chime-line physical form; chain chime_anchors_used records UNMEASURED

## anti-guessing notes
RULED OUT: "read the debug line with `jawa/drain_log contains=`" — it returns a stale first message (skills/rimbridge/references/map-authoring.md); the suite reads each action's own `effects.logs`.
RULED OUT: "an action that logged nothing did nothing" — RimWorld stops all logging at 10,000 messages; `_act` records UNMEASURED, never PASS or FAIL.
RULED OUT: "the flood runs on any map" — `Active` needs the canyon biome or `featureInOtherBiomes`; the chains arm the setting and `feature_gate_off` is the control.
RULED OUT: "the phases take game hours to play" — `DebugArmFloodSoon` sets nextFloodTick to now+1, so Herald, Warned and Flooding play inside ~3 ticks; the sequence chain polls once per tick.
RULED OUT: "a seam count of zero after recede means the recut is broken" — the recut only replaces natural non-resource rock touching the footprint; no such face on a site is UNMEASURED, not FAIL.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
