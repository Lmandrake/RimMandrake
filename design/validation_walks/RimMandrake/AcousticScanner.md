# RimMandrake: Acoustic Scanner — validation walk
subject: src/RimMandrake/AcousticScanner  (packageId `mandrake.rm.acousticscanner`)
deps: `Ludeon.RimWorld.Odyssey` (BasicGravtech, substructure, GravEngine); the biome payloads are patches in the biome mods (Cracked Lands, Stillsand, Utinni Cracked Lands), FindMod-guarded on `RimMandrake: Acoustic Scanner`
status-hint: GRAVSHIP_ACOUSTIC_SCANNER_1 — a ship-mounted acoustic sounder: research, build on substructure, fire a powered pulse from a landed gravship, get a banded temporary overlay and a letter; payload per biome by def extension; script = `src/RimMandrake/AcousticScanner/validation.py`, never run live yet

Sources: `About/About.xml`, `Source/RM_Building_AcousticSounder.cs`, `RM_AcousticBanding.cs`, `RM_AcousticPayloadExtension.cs`, `RM_AcousticScannerMod.cs`, `Defs/`, `Languages/English/Keyed`, the three payload patches.

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`.
- The sounder building and the acoustic sounding research resolve in the running game, the sounder is gated by that research and the research follows BasicGravtech; a nonexistent def reads absent. → defs_resolve.defs_resolve, defs_resolve.probe_can_say_absent, defs_resolve.research_gate
- The settings class and the payload extension class are loaded. → defs_resolve.classes_loaded
- All seven Mod Settings fields (enabled, requireLandedShip, cooldownHours, overlayHours, bandSize, rangeCells, pulseEffects) read their shipped defaults, write, read back and restore; a nonexistent field fails loudly. → settings_roundtrip.enabled_roundtrip
- A sounder with no power refuses and says so. → sounder_gating.unpowered_refuses
- A powered sounder not on a landed gravship (no grav engine on the map) refuses with the substructure line. → sounder_gating.off_the_ship_refuses
- A powered sounder on substructure with a grav engine on the map is ready. → sounder_gating.ready_on_landed_ship
- With `enabled` off every sounder refuses ("switched off"); restored, it is ready again. → sounder_gating.master_off_refuses
- With `requireLandedShip` off a sounder with no engine is ready. → sounder_gating.require_ship_off_relaxes
- Firing the pulse starts the cooldown (inspect says "Transducer settling") and sends the "Sounding reading" letter. → pulse.pulse_starts_cooldown_and_sends_letter
- A reading is always banded, never exact: band side never below 7 cells whatever the settings file says. → pulse.banded_overlay_never_exact (the floor itself is a static check; the overlay drawing is UNMEASURED: no reader for the unsaved map component)
- What a pulse hears depends on the biome through its payload extension; a biome without one reads "nothing unusual". → UNCOVERED: needs a map whose biome is RM_FloodedCanyon, RM_Stillsand or RUT_CrackedLands with its targets; follow-up ACOUSTIC_SCANNER_BIOME_SITE_1 → pulse.biome_payload_reads (UNMEASURED)
- Pulse effects (dust, thump, camera shake) fire when `pulseEffects` is on. → UNCOVERED: visual/audio, no state read; the setting round-trips → settings_roundtrip.pulseEffects_roundtrip
- Cooldown, overlay duration and range settings change pulse timing and reach. → UNCOVERED: cooldownHours and rangeCells are read/write only here; a 24 h cooldown and a payload-biome map exceed the cheap site → settings_roundtrip.cooldownHours_roundtrip

## the walk
1. [B] Tier: smallest list loading the mod (bridge + Odyssey + `mandrake.rm.acousticscanner`), quicktest map 150 cells or larger.
2. [B] `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod AcousticScanner --plan <plan>` (suite via modcheck). No plan file exists yet; the modcheck suite is the script.
3. [L] Player.log has no cross-reference or Config error naming an `RM_Acoustic*` def.
Offline: `python3 src/RimMandrake/AcousticScanner/validation.py` (static checks, no game).

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. No owner-ruled experience bars yet; the functional lines above are agent-owned.

## anti-guessing notes
- UNPROVEN live shapes (first run settles them; each reads UNMEASURED, never PASS, when absent): `jawa/set_substructure_batch action="add"` on an open map cell; `jawa/spawn_batch` accepting `GravEngine` and the 3x3 sounder; `jawa/power_net thing=<id> forcePowerOn=True` powering a sounder with no net; the `click_cell` + `list_selected_gizmos` + `execute_gizmo` route (needs god mode off the pad's selection); `jawa/letter_list` rows carrying the letter label.
- RULED OUT: "the engine must be on the substructure" — `OnLandedShip` only needs a `GravEngine` anywhere on the map and the sounder's own 9 cells on substructure foundation.
