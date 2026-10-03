# RimUtinni: Assailant Salvage — validation walk
subject: src/RimMandrake/AssailantSalvage  (dev source folder, own About.xml packageId `mandrake.rut.assailantsalvage`)
deps: `Ludeon.RimWorld` only; no C#, no Mod Settings; not wired into any map generation (ASSAILANT_DUNGEON_BUILD_1 is separate)
status-hint: CRYPTOFORGE_HARVEST_RETIRE_1 step 1 — 22 owned RUT_ ThingDef replacements for the Cryptoforge salvage props (airlocks, shielded turret and autocannon, landmine, terminals, floor heater, black box, wargaming table, blueprints bench, cryptosleep pod, ruined hospital bed), same stats as the donor, owned defNames; script = `src/RimMandrake/AssailantSalvage/validation.py`, never run live yet

Sources: `About/About.xml`, the three `Defs/ThingDefs/RUT_*.xml` files (their header comments name each donor def and its stats), `design/Jawa/art/SALVAGE_PALETTE.md`.

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`.
- Every owned ThingDef the mod ships resolves in the running game (none is discarded for an unresolvable class or comp), and a nonexistent def reads absent. → defs_resolve.defs_resolve, defs_resolve.probe_can_say_absent
- The live thingClass, fillPercent and size of each def are what the XML declares (the donor's stats were carried over unchanged, and nothing overrides them). → defs_resolve.fields_match_xml
- The mod ships no Mod Settings and no C#. → settings_roundtrip.no_settings_declared (UNMEASURED by design: nothing to round-trip; the static check fails if a Source folder or assembly appears)
- Every placeable prop spawns on a map and is found again, and its inspect string reads without error. → spawn_all.every_placeable_prop_spawns, spawn_all.spawned_props_inspect_clean
- The ancient landmine springs under a pawn who does not know it (mine gone, the pawn hurt or dead); a mine off the path stays. → landmine.hostile_pawn_springs_player_landmine
- Every texture path the defs name resolves in the running game (no magenta). → textures.textures_resolve
- The shielded turret and the spacer autocannon fire at hostiles. → UNCOVERED: needs power, ownership and a raid (owner/FOUNDRY live round) → unproven_behaviours.turrets_fire_when_hostile_in_range
- The floor heater warms its room and glows when powered. → UNCOVERED: needs a sealed powered room and a control room → unproven_behaviours.floor_heater_heats_and_glows_when_powered
- The ancient airlock opens for pawns and holds a room's pressure line. → UNCOVERED: door open state has no reader → unproven_behaviours.airlock_opens_for_pawns
- The ruined hospital bed, frozen pod, wargaming table and blueprints bench do what their donors did. → UNCOVERED: need pawns and bills → unproven_behaviours.bed_pod_table_functions

## the walk
1. [B] Tier: smallest list loading `mandrake.rut.assailantsalvage` plus the bridge, all five DLCs; quicktest map 150 cells or larger.
2. [B] Run the suite through modcheck / `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod AssailantSalvage` (no plan file yet; the suite is the script).
3. [L] Player.log has no cross-reference or Config error naming a `RUT_Ancient*`, `RUT_Jammed*`, `RUT_Forced*`, `RUT_Busted*` or `RUT_Crypto*` def.
Offline: `python3 src/RimMandrake/AssailantSalvage/validation.py` (static checks, no game).

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. No owner-ruled experience bars yet; the functional lines above are agent-owned.

## anti-guessing notes
- UNPROVEN live shapes (first run settles them; each reads UNMEASURED, never PASS, when absent): `get_defs fields="thingClass,fillPercent,size"` returning scalar field values; `jawa/set_thing_props faction="PlayerColony"` accepted for a landmine; a hostile `Colonist` ordered with `order_pawn` actually stepping on the mine; `jawa/texture_audit filter="RUT_Ancient"` returning `missing[]`.
- RULED OUT: "a colonist can test the landmine" — `Building_Trap.KnowsOfTrap` is true for any pawn of a faction not hostile to the trap's owner, and a known trap springs at 0.4%, so the test uses a HOSTILE pawn and a player-owned mine.
- Texture count: the mod's own `Textures/` holds only 8 files while the defs name ~25 paths; many may be owed art. The live `texture_audit` component is the judge (a missing path is a MOD finding), not the file listing.
