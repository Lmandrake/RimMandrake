# Pyrelands site load error — 2026-10-01

Evidence: `Player.log` copy (10:09) and `NS_Pyrelands_site_1_46a3a8544c79.rws` (10:04:40) plus its
`_attempt1` / `_attempt2` siblings, all in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves`.
Engine reads are from RimSage (decompiled 1.6). The log hit "Reached max messages limit" at line ~21424,
so everything after the first map's spawn spam is invisible.

There are **three separate defects**. Only the first is in our content.

## 1. OURS, fixed: RUT_Barbslinger carried TWO `CompProperties_TurretGun`

- This is the first error of the load (log ~1639–1650): `Tried to register the same load ID twice … /currentTarget/thing`,
  `Cannot register … RUT_BarbslingerTailGun95357 … Id already used`, and `Could not get load ID … parent=RUT_Barbslinger95356`.
- Mechanism (RimSage `CompTurretGun.PostExposeData`): it scribes **fixed labels**: `gun` (Deep),
  `currentTarget`, `burstCooldownTicksLeft`, `burstWarmupTicksLeft` and `fireAtWill`. With two comps,
  the save writes **two `<gun>` nodes into one pawn node**. MEASURED: every Barbslinger in the .rws has
  two, for example TailGun95357 and TailGun95358. On load **both comps read the first node**, so the IDs
  collide. A thing can never round-trip two vanilla turret comps.
- Damage: it is load-ID noise, and the two comps share one deep-loaded gun. It does **not** dispose a map,
  so it is not what broke the pathgrid.
- Fix: one comp, and the tail gun's verb gets `burstShotCount 2` / `ticksBetweenBurstShots 12` (one needle
  per tail, so the "two venomous missiles" brief still holds). The def header was corrected in place.
  File: `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsPortedFauna.xml`. Not deployed.
- Old saves keep the doubled `<gun>` nodes. Regenerate the fixture after deploying; do not reuse it.

## 2. NOT OURS: the PathGrid / GlowGrid NRE cascade (the "Error while loading a map")

- `Exception spawning loaded thing Luciferium3121 … PathGrid.WalkableFast` is followed by the same failure
  for every thing, and `GlowGrid+GlowPool.Take` NREs on plants. All of it is inside `Map.FinalizeLoading`
  of **map 0**: the debug-game colony (tile 110257, parent WorldObject_29, Faction_17). It is **not** the
  Pyrelands site map. MEASURED: Luciferium3121 sits inside map 0's span of the .rws.
- `PathGrid.pathGrid` and `GlowPool.pool` are NativeArrays that only `Dispose()` nulls. So map 0 had been
  **disposed but was still in `Game.maps`**. `DeinitAndRemoveMap` removes the map from that list, so it
  did not do this. The thing that disposes maps without removing them is `Game.Dispose()`.
  `GameDataSaveLoader.LoadGame` (RimSage) calls `Current.Game?.Dispose()` right after queueing an
  **async** load. A second LoadGame arriving while the first is between `Scribe_Collections(maps)` and
  `maps.FinalizeLoading` disposes the game that is still being loaded. That matches this signature exactly.
- Evidence of double loads: the log shows `Loading game from file NS_Pyrelands_site_1…` **twice back to
  back with no new game between them**, at lines 1243→1299 and 1443→1502. The 1618 load's twin would fall
  after the message cap. `northstar_site.reload_fixture` sends `rimworld/load_game` once, and neither
  `rimdrive.Session.call` nor `TimedTransport` retries. The second call therefore came from outside this
  script: another driver or window, a manual re-send, or RimBridge itself. **INFERRED, not measured.**
- `TRANSPILER Kikohi.PipeSystem` is just on the `Thing.SpawnSetup` stack. The NRE fires in
  `PathGrid.WalkableFast` on a disposed array, so PipeSystem is a bystander.
- Workaround for the recipe (`src/RimMandrake/Pyrelands/northstar_site.py`, `reload_fixture`):
  1. `rimworld/go_to_main_menu`, then poll for `Entry`.
  2. Make exactly ONE `rimworld/load_game`.
  3. Poll `Playing` + `get_game_info.status == game_loaded`, never re-send.
  4. Assert one `Loading game from file <name>` line per reload in `Player.log`.

  traps.md already records that a load from a settled Entry works. Not changed here, because the
  duplicate's source is unproven.

## 3. GENERATION PATH, already fixed upstream: factionless MapParent

- `_attempt1` and `_attempt2` have the tile-3,0 Settlement saved with `<faction>null</faction>`. On load,
  `Settlement '' had null faction on load - destroying` → `MapParent.Destroy` → `DeinitAndRemoveMap`, and
  the site map is gone (log 1264–1284, with the GlowGrid NRE in `TerrainGrid` PostLoadInit following from it).
- The current .rws has that Settlement on `Faction_17`, so whoever edited `jawa/world_tile_map_generate`
  between attempts fixed it.
- Side note: every attempt generated at **tile 3,0**, whatever centre was chosen. That is the existing
  `TILEGEN_SILENT_REUSE_1` probe's territory.
- Also seen: `Error in WorldGenStep` NRE in `IdeoFoundation_Deity.GenerateTextSymbols` during faction
  generation on this 20-mod tier. It happens on every fresh quicktest world. It was not investigated here.
