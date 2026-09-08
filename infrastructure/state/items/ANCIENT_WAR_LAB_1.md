# ANCIENT_WAR_LAB_1 — the war lab beneath the propane lake, over the Impact Site

Owner rulings 2026-09-06 (`the_propane_lakes.md` §3 "The machine" and §8).

## spec
- **What it is**: the Rakatan-era war lab where the Assailants were first contained and
  studied — built AFTER the weapon was deployed and active, never part of the
  terramanufacture plan; directly over the **Impact Site** where the first infection
  occurred. Mutual learning, mutual destruction: every study taught the weapon.
- **Where**: beneath the propane lake's surface under Umbra (`LIQUID_BIOMES_MAP_1` places
  the lake; this item places the lab within it). Reached by the ruled submerged
  adventure (the ship lowered into fuel) — great care against ignition from spacecraft
  interaction or anything extremely hot.
- **The dungeon**: shielding intact; lab fauna (the Slurrypede as prisoner-feeder);
  mechanoid/ancient guardians; the study records (what they learned, what it learned).
  Scene-composition skill applies; KCSG or the dungeon items' method.
- ⭐ **The ending**: plentiful ways to permanently change the map — ignition (thruster,
  dropped reactor core per wasteland §10 option 4, deliberate charge) turns the lake into
  **a massive fresh crater and a ripped-open lab, shielding intact**. This is a permanent
  map change on a frozen world: needs its own engine design (map/world mutation, save
  implications, the propane-lake tiles → crater tiles).
- ⭐ **RECONCILED (owner ruling, 2026-09-07)**: confirmed — this lab IS the wasteland
  §10 "sealed research station holding active Assailants". Owner, verbatim: *"The War
  Lab refers to the antipodal site beneath the propane lake on the night side, that's
  where the live assailants being studied trapped in the frozen wastes will happen."*
  The Assailants here are **live but contained/trapped specimens under study** — this
  reads as compatible with `the_propane_lakes.md` hard ban #8 ("study subject, never
  resident weapon-fauna"): live and dangerous if released, but never ambient roaming
  wildlife on the biome map. `wasteland.md` §10 point 4 is updated to point here by
  name instead of re-describing a second station.
- ⛔ **NOT the same as** `SCALD_DARK_TOWER_1` (filed 2026-09-07, same sitting): the
  owner's "nearby lab concept" from earlier drafts was reborn as a **separate** dungeon
  — the dark tower at the Scald, the Rakatan's ground-based high command with control
  systems for the Rust Cathedral, holding *ocular warped* Assailants that pressed their
  way in from outside. Similar theme, different site, different item — do not merge.
- Naming per the tier grammar (`RUT_`/`RSW_`).
- ⭐ **SCOPED (research, 2026-09-07)**: the world-tile mutation is real and achievable
  — `Tile.PrimaryBiome` has a public setter, `Tile.ExposeData()` Scribes biome/
  elevation/etc. as plain values with no special-casing blocking a runtime write
  from surviving save/load (confirmed via decompiled `Source/RimWorld/Planet/Tile.cs`).
  Vanilla itself never rewrites a tile's biome mid-campaign (the only runtime
  per-tile-mutation precedent is `pollution`, a plain float via
  `WorldPollutionUtility.PolluteWorldAtTile`) — no config flip exists for this.
  This project's own `jawa/world_tile_set` + `jawa/world_commit` bridge tools
  (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs`)
  already prove the correct call sequence (`PrimaryBiome` write, then regenerate
  `WorldDrawLayer_Terrain/_Hills/_Landmarks/_Roads/_Rivers`, `FastTileFinder`,
  `WorldPathGrid`, `WorldReachability` caches) — but that tool is driven externally
  over the bridge RPC and **cannot fire itself from an in-game trigger**. Building
  this needs new companion-mod C# (a `QuestPart`/`CompDestroyed`/`GameComponent`
  hook on the ignition event) calling that SAME sequence in-process — new
  authoring work, not a config task, but low-risk since the sequence is already
  validated. Recommend splitting scope: local-map spectacle (fire, terrain swap,
  roof breach) for the 95% of player-visible payoff using routine, well-precedented
  map-damage machinery; the real world-tile mutation only for the permanent
  worldmap scar itself, likely a small tile count (propane lake's exact footprint
  still owed by `LIQUID_BIOMES_MAP_1`). Do not fake the worldmap side only — that
  leaves a permanent discrepancy between what the map shows and what a save holds.

## verify
Lab placed and reachable via the submerged route in a test map; ignition triggers
produce the crater state; the crater persists across save/load; screenshots for the
owner.
