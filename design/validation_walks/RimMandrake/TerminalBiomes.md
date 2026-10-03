# RimMandrake: Terminal Biomes — validation walk
subject: src/RimMandrake/TerminalBiomes  (packageId `mandrake.rm.terminalbiomes`)
deps: `mandrake.rm.luminouspigment`, `mandrake.rm.divinginteraction`, `mandrake.rm.environmentalhazards`, `mandrake.rm.flowworks`, `brrainz.harmony` (modDependencies). Fold-aware: folded into `mandrake.rm.biomes`, active under the composed name 'RimMandrake: Baroque Biomes' (Biomes.compose.json entry TerminalBiomes); the composed mod's script covers it only through these lines.
list: a tier carrying the composed biomes mod (or Terminal Biomes and its dependencies), all five DLCs, plain open map (the suite builds its own terrain row, vat site and Hesuun site)
status-hint: the four terminal biomes' shared kit — the Chill (propane sea floor), the Scald (steam), the Twilight Sea and the Grey Sea; this script grew from the 2026-10-03 Chill/Scald def checks. Script: `src/RimMandrake/TerminalBiomes/validation.py`, first script TERMINAL_BIOMES_FIRST_SCRIPT_1. NEVER RUN LIVE.

Sources: `About/About.xml`, `Source/RM_TerminalBiomesMod.cs` (38 settings: 36 bool/float/int/string and 2 enum), `Source/RM_Building_CryoGrower.cs`, `Source/RM_Comp_WaxProcession.cs`, `Source/RM_TerminalBiomes.csproj`, `Defs/` (BiomeDefs, TerrainDefs, ThingDefs_*, incidents, game conditions).

## must be true
- Every def the mod ships resolves in the running game; a nonexistent control reads absent so the probe can say no. → defs_resolve.shipped_defs_resolve, defs_resolve.control_absent_def_reads_absent
- Every Mod Settings field the C# declares round-trips (write alt, read back, write default, read back); one chain per field is generated from the settings class (`flip_masterEnabled`, `flip_scaldEnabled`, `flip_chillEnabled`, … the two enum fields degrade to UNMEASURED if the setter cannot take an enum name). → flip_masterEnabled.masterEnabled_round_trips
- Every settings field is Scribed, has a window control and every source file is in the csproj. → settings_wiring.every_field_scribed_exposed_and_compiled
- A run leaves every setting at its shipped default. → settings_restored.all_settings_at_shipped_defaults
- Every Chill native creature is comfortable below the -110 C floor (ComfyTemperatureMin at or under -150 with a Max above it), in source and in the running game. → natives_tolerate_floor.natives_comfy_min_below_floor_in_source, natives_tolerate_floor.natives_comfy_min_below_floor_live
- The Chill's wildAnimals roster is exactly the floor natives, with the off-floor species absent (Q1a), parsed as XML (no `<li>`). → floor_roster_trimmed.chill_roster_is_the_floor_natives
- The Chill's fishTypes are all free-tier items and every catch has a living floor resident. → catch_free_tier.chill_catch_is_free_tier_and_alive_on_the_floor
- The Scald's saal is labelled saal in both creature and catch, and the ekkel carries its simmerlace origin lore. → saal_one_name.creature_and_catch_both_labelled_saal, saal_one_name.ekkel_carries_simmerlace_lore
- Every biome that ships a wildAnimals roster has `animalDensity` above zero in the running game (the engine gate: zero density spawns nothing). → biome_animal_density.rostered_biomes_have_density_above_zero
- Each of the 15 biome terrains can be painted onto a cell and read back as itself. → terrains_paint.control_vanilla_terrain_reads_back, terrains_paint.every_biome_terrain_paints_and_reads_back
- The cryoponics vat runs its own class: its inspect line names the cryogenic bath and a vanilla grower's does not. → cryoponics_vat.vat_reports_a_cryogenic_bath_line
- A powered bath reads running, and the toggle off reads offline. → UNCOVERED: no bridge tool wires a power net on a bland map; chain cryoponics_vat.powered_bath_runs_and_toggle_off_goes_offline records UNMEASURED
- The wax-procession giant (RM_Hesuun) is untameable, cold-tolerant, rostered, carries the procession comp, and its sheet and flesh defs exist. → wax_procession.wax_giant_wired_in_source
- Killing a Hesuun colony spoils into hydrocarbon flesh (12 per carried sheet). → wax_procession.killed_colony_spoils_into_hydrocarbon_flesh
- A walking colony extrudes a dead filter sheet at its first pause after 90000 ticks of walking. → UNCOVERED: a 90000-tick walk and no tool seeds the countdown; chain wax_procession.sheet_extruded_at_a_pause_after_the_walk records UNMEASURED
- The Scald's steam sky (steam-lock weather pulse and vent flash) runs only while `scaldS1SteamSkyEnabled` is on. → UNCOVERED: a Scald map and a read of the running condition; chain scald_steam_sky.steam_lock_pulses_weather_and_flash records UNMEASURED
- The steam catch condenses steam into a resource while `scaldS2SteamCatchEnabled` is on. → UNCOVERED: a Scald map with a vent and ticks of steam; no condenser-stock reader; chain scald_steam_catch.condenser_collects_steam records UNMEASURED
- Scald vent fields scatter at map generation while `scaldS4VentFieldsEnabled` is on. → UNCOVERED: worldgen-affecting; needs a fresh Scald map; chain scald_vent_fields.vents_scatter_and_erupt records UNMEASURED
- The sail-walker incident and sail scatter run while `scaldS5SailWalkerEnabled` is on. → UNCOVERED: a Scald map and incident; chain scald_sail_walker.walker_surfaces_and_sails_scatter records UNMEASURED
- Scald wrecks scatter and yield salvage while `scaldS6WreckSalvageEnabled` is on. → UNCOVERED: a fresh Scald map; chain scald_wreck_salvage.wrecks_scatter_and_yield_salvage records UNMEASURED
- Steam exposure inflicts `RUT_ScaldExposure` on an unprotected pawn while `scaldS7SteamExposureEnabled` is on. → UNCOVERED: a Scald map under steam; chain scald_steam_exposure.steam_carrier_inflicts_scald_exposure records UNMEASURED
- The Suulk arrival incident and Vaulisk lure run while `suulkEnabled` is on. → UNCOVERED: the Twilight sea-floor map; chain twilight_suulk.suulk_arrival_and_vaulisk_lure records UNMEASURED
- The Twilight channel current carries pawns and the chosen sink outcome applies while `channelCurrentEnabled` is on. → UNCOVERED: a generated Twilight map with channels; chain twilight_channel_current.current_carries_pawns_and_sink_outcome_applies records UNMEASURED
- Veil panes strike and the deck accumulates while `twilightPaneStrikeEnabled` is on. → UNCOVERED: a Twilight map with panes and the gravship launch gate; chain twilight_pane_strike.veil_pane_falls_and_deck_accumulates records UNMEASURED
- A gravship parked on the Grey floor rimes (~1 day), salts its outer doors shut (~2.5 days, chip-free from either side) and grows hull crust that blocks launch until chipped (from day 5, whole hull by ~15), faster in salt snow and beside brine; off removes every constraint. → grey_hull_crust.ladder_rime_door_crust_gate (UNMEASURED without a parked gravship on an RM_GreySea map)
- The well ledger drifts and the sun sphere cultures while `twilightWellDriftEnabled` is on. → UNCOVERED: days of Twilight map time; chain twilight_well_drift.well_ledger_drifts_and_sun_sphere_cultures records UNMEASURED
- Twilight cages are passable beneath while `twilightCagesPassableBeneath` is on. → UNCOVERED: the applier writes passability only from the settings-window frame, never from a bridge setter; chain twilight_cages_passable.cage_passability_follows_the_setting records UNMEASURED
- A Scald mechanic can be opted into another biome's new maps (`crossBiomeEnabled`). → UNCOVERED: worldgen-affecting and inert: reserved for a future pass, nothing to read; chain cross_biome.scald_mechanics_outside_the_scald records UNMEASURED
- The biomes' look, sound and feel (steam, salt snow, light economy, the Twilight sun sphere). → UNCOVERED: visual and audio, judge pass or owner

## anti-guessing notes
RULED OUT: "the first live run reported zero chains because the mod has nothing to check" — the chains held no `t.component(...)`, and a chain records results only through components; every check now runs inside one (2026-10-03).
RULED OUT: "a BiomeDef with zero tiles is a defect" — expected mid-migration state (CLAUDE.md, repaint once at the end); no check here reads tile counts, and the ChillCrater biome has no roster by design.
RULED OUT: "`<li>` rows count the roster" — wildAnimals and fishTypes are read as XML elements (node name = species, text = commonality).
RULED OUT: "a failed enum set proves the enum toggle is dead" — the bridge setter's enum-name shape is unproven, so it is UNMEASURED, never FAIL.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
