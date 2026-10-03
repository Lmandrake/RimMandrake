# RimMandrake: Greentide — validation walk
subject: src/RimMandrake/Greentide  (packageId `mandrake.rm.greentide`)
deps: `mandrake.rm.creaturebehaviors`, `mandrake.rm.environmentalhazards` (modDependencies). Fold-aware: folded into `mandrake.rm.biomes`, active under the composed name 'RimMandrake: Baroque Biomes' (Biomes.compose.json).
list: a tier carrying Greentide (or the composed biomes mod) + Creature Behaviors + Environmental Hazards, all five DLCs, plain open map (the suite builds its own churnmud / Concrete / sealed site)
status-hint: GREENTIDE_STANDALONE_MOD_1 (+ DENSITY_SETTINGS_1, FRENZY_DISEASE_1, FEVER_SPECIALISTS_1) — churnmud mire and swallow, toxin sealant, the Frenzy disease and dose, density settings. Script: `src/RimMandrake/Greentide/validation.py` (plan `northstar_plan.py`), first script GREENTIDE_FIRST_SCRIPT_1. NEVER RUN LIVE.

Sources: `About/About.xml`, `Source/RM_GreentideMod.cs` (16 settings), `RM_MapComponent_TerrainMire.cs`, `RM_MapComponent_MudSwallow.cs`, `RM_IngestionOutcomeDoer_FrenzyDose.cs`, `RM_HediffComp_MarksFeverSurvivor.cs`, `RM_GreentideDensityApplier.cs`, `Defs/`.

## must be true
- Every def the mod ships (biome, terrains, hediffs, plants and tree roster, items, races, recipes, jobs, designation, incident, sounds) resolves in the running game; a nonexistent control reads absent so the probe can say no. → defs_resolve.shipped_defs_resolve, defs_resolve.control_absent_def_reads_absent
- Every Mod Settings field the C# declares round-trips (write alt, read back, write default, read back). → flip_mireEnabled.mireEnabled_round_trips (and one `flip_<field>` chain per declared field, generated from the settings class)
- A run leaves every setting at its shipped default. → settings_restored.all_settings_at_shipped_defaults
- Churnmud is a mire: a pawn standing on `RM_GreentideChurnmud` gains `RM_Mired`; one on Concrete or on `RM_ChurnmudSealed` does not (carrying no mire extension IS the sealant's safety). → mire.mire_applies_on_churnmud, mire.mire_skips_concrete_and_sealed_floor
- The master switch `mireEnabled` off stops the mire. → mire.mire_master_switch_off
- Past the stuck threshold only another pawn can pull a mired pawn out (`RM_FreeMired`). → UNCOVERED: a ~6000-tick random climb plus a second pawn's job; needs a seeded severity and a job order (named item to file: GREENTIDE_MIRE_SEED_1); chain mire_escalation records UNMEASURED
- A loose item left on churnmud for its dwell time is swallowed, even in a stockpile; items on safe or sealed ground stay. → swallow.swallow_buries_on_churnmud_only
- `buriedCacheEnabled` off swallows nothing. → swallow.buried_cache_switch_off_keeps_items
- The dig-out job restores a buried item and nothing is ever destroyed. → swallow.dig_out_job_restores_the_buried_item (UNMEASURED when the order shape is unproven)
- A frenzy dose gives the `RM_Frenzy` hediff. → frenzy_dose.dose_gives_frenzy
- The master switch `frenzyEnabled` off: a dose gives nothing. → frenzy_dose.frenzy_master_switch_off_gives_none
- A colonist carrying `RM_FeverMark` wastes the dose while `feverMarkGrantsImmunity` is on. → frenzy_dose.fever_mark_gates_the_dose
- Surviving the tended Frenzy through the collapse stage earns the permanent `RM_FeverMark`. → UNCOVERED: days of game time and a tending pawn; needs a seeded hediff at the collapse stage (named item to file: GREENTIDE_FRENZY_SEED_1); chain frenzy_dose.fever_mark_earned_by_surviving_the_coma records UNMEASURED
- The ambient Frenzy incident fires only when `frenzyEnabled` is on and skips FeverMark colonists. → UNCOVERED: a dry-run fire_incident reports success=False with canFireNow=False, so it is no instrument; chain frenzy_dose.ambient_frenzy_incident records UNMEASURED
- The live `RM_Greentide` BiomeDef carries the Mod Settings `plantDensity` and `movementDifficulty` (applied at load by the density applier). → density_applier.biome_carries_the_settings_density
- The mire can be opted into a non-Greentide biome's freshly generated map (`crossBiomeEnabled`, worldgen-affecting). → UNCOVERED: needs a map generated fresh with the toggle on; chain cross_biome_churnmud records UNMEASURED
- The stench grenade's smoke radius follows `stenchGrenadeRadiusMultiplier`. → UNCOVERED: no reader for the smoke cloud; chain stench_grenade records UNMEASURED
- `canopySwarmEnabled` gates the Krannock's wild spawning. → UNCOVERED: a deliberate no-op until the Krannock is rostered at the biome's own review sitting; chain canopy_swarm records UNMEASURED
- The seek-shade AI and the silence cue live in the shared Creature Behaviors assembly. → UNCOVERED: owned by the CreatureBehaviors script, not this mod's code
- The jungle's look, audio and ambience. → UNCOVERED: visual and audio, judge pass or owner

## anti-guessing notes
RULED OUT: "a drafted colonist wanders off the mud" — drafted pawns hold their cell; the mire and swallow chains draft the subjects (the GelatinousSlime pattern).
RULED OUT: "the swallow fires at exactly 2500 ticks" — the scan runs every 250 ticks and first-sight starts the dwell clock, so the wait is 3200 (2500 + a scan + margin); `static_checks` fails if swallowTicks outgrows it.
RULED OUT: "a failed dig-out order proves the dig-out job is broken" — the ordered_job target shape for a designation cell is unproven; a non-return is UNMEASURED, never FAIL.
RULED OUT: "reading RM_Greentide's tile count says whether the biome works" — a biome with zero tiles is the expected mid-migration state (CLAUDE.md); no check here reads tiles.
RULED OUT: "the density applier runs when a setting is written through the bridge" — it runs at startup, on load and on WriteSettings only; the check reads the live def against the current settings, never a changed one.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
