# RIVER_STEAM_ANIMATION_1 — animated steam rising from Pyrelands rivers

Owner, verbatim (2026-09-02): *"could we add animated steam rising from the
river? That is an amazing idea, file a ticket on that alone!"*

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-09-02.

## spec

Pure ambience feature, no gameplay effect, no new art. `mandrake.rut.riversteam`
(RimUtinni tier — this names Ash'karr's Pyrelands specifically, per
`NAMING_SCHEME_PLAN.md`'s tier test).

`MapComponent_RiverSteam` (`src/RimUtinni/RiverSteam/Source/RiverSteamHook.cs`):
- MapComponent subclasses are auto-instantiated per map by `Map.FillComponents()`
  (`Verse/Map.cs:710`) — no Harmony patch or XML registration needed, confirmed
  by reading the real vanilla source, not assumed.
- Gates on `map.Biome.defName == "ZBiome_Grasslands"` — the Pyrelands' actual
  BiomeDef, per `ASHKARR_WORLD_DEFINITION.md`'s biome table ("stormy savanna").
  Every other biome's rivers stay silent.
- River cells found via `TerrainDef.IsRiver` (`HasTag("River")`) — the exact
  test `RimWorld.SeasonalFlood` already uses for the same purpose
  (`Source/RimWorld/SeasonalFlood.cs:63`), cached once at `FinalizeInit()`.
- Every 90–260 ticks (randomized), one river cell is picked and — if not
  fogged — thrown a puff of vanilla's own **`Steam` FleckDef**
  (`Defs/Ideology/Effects/Fleck_Visual.xml`, `ParentName="FleckBase_Thrown"`,
  `texPath=Things/Mote/Smoke`) via `FleckMaker.GetDataStatic` + a slight
  upward drift (`velocityAngle` 60–120°, `velocitySpeed` 0.15–0.3). No new
  texture, no heat push (unlike `IntermittentSteamSprayer`, which this
  deliberately does NOT reuse — that class pushes 40 heat/interval, which is
  a real geyser gameplay mechanic, not ambience).

## verify

- `dotnet build RiverSteamHook.csproj -c Release` — clean (0/0), confirmed.
- Deploy clean, file-copy only (`deploy_custom_mods.py --mod RiverSteam --apply`).
- Live-observed: load a save/quicktest with a Pyrelands-biome map open, confirm
  steam puffs appear near river cells at a reasonable, non-spammy rate, and
  that a NON-Pyrelands map's rivers stay silent (the biome gate holds).

## criteria

Steam visibly rises from river cells on a live Pyrelands map at an ambient,
non-distracting cadence; no gameplay stat/mechanic is touched; other biomes'
rivers are unaffected.

## 2026-09-02 — offline build (FOUNDRY)

Built and deployed as above. `ZBiome_Grasslands` is a third-party mod's
BiomeDef (`RimSage` only indexes vanilla source, so its exact schema wasn't
independently re-verified here — the defName itself is sourced from
`ASHKARR_WORLD_DEFINITION.md`'s own biome table, not guessed). Not enabled
in `ModsConfig.xml`, no restart — live-quicktest-observed steam-on-Pyrelands
(and silence-elsewhere) is owed to a future bridge session. Left `doing`.
