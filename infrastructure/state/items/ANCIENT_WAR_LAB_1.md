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

## build spec (FOUNDRY, 2026-09-08 — consolidated, follows the `dungeons_arc_spec.md`
pattern already used for `ASSAILANT_DUNGEON_BUILD_1`/`VAULT_DUNGEON_BUILD_1`)

**Technical route — confirmed, same pipeline as the vault/Assailant dungeons**: KCSG
via `jawa/kcsg_place` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchKcsgTools.cs`),
authored as `KCSG.StructureLayoutDef`/`KCSG.SymbolDef` XML, `RUT_` tier. No new
placement C# needed for the dungeon itself — only the ignition→crater world-tile
mutation needs new code, split out below.

**Layout — three bands**, matching `wasteland.md` §10's reconciliation (live,
contained specimens; never resident weapon-fauna):
1. **Approach (shielding intact)** — ancient Rakatan hull/shielding material, powered,
   dark but not breached; the submerged entry point.
2. **Lab interior** — `AA_Slurrypede` (confirmed live in the biome cast, prisoner-feeder
   bio-mechanoid) working its pens; lab guardians (mechanoid/ancient — reuse the vault
   type-① Forsaken Arsenal garrison roster, e.g. `Mech_Lancer`/`Mech_Centurion` per
   `RUT_Symbol_MechLancer`/`RUT_Symbol_MechCenturion` in
   `src/RimUtinni/VaultDungeons/Defs/SymbolDefs_Vaults.xml`; confirm final roster
   against `MECHANOID_BIOME_PRESENCE_REVIEW_1` at hand-finish rather than inventing a
   new one).
3. **Core** — the containment cells holding live, trapped Assailant specimens (never
   roaming; hard ban #8 in `the_propane_lakes.md` §6) plus the study records
   (terminal/archive prop — exact defName HELD, confirm at hand-finish; the payoff is
   informational/reveal-beat, not loot-ladder).

**Content palette still open** (do not invent — confirm at build time, same discipline
as the Assailant dungeon's held items): exact shielding wall/terrain defNames, the
study-records prop, and the frozen/live-Assailant containment prop. `AA_Slurrypede`'s
`PawnKindDef` name is assumed identical to its ThingDef (`AA_Slurrypede`) per Alpha
Animals convention — confirm before the real `SymbolDef` is written.

**Illustrative skeleton** — proves the grid format against this dungeon's specific
palette (not shippable, no wall/props defNames committed yet):
```xml
<Defs>
  <KCSG.StructureLayoutDef>
    <defName>RUT_WarLab_ApproachBand_Skeleton</defName>
    <spawnConduits>false</spawnConduits>
    <layouts>
      <li>
        <li>Wall,Wall,Wall,Wall,Wall,Wall,Wall,Wall</li>
        <li>Wall,.,.,.,.,.,.,Wall</li>
        <li>Wall,.,RUT_Symbol_MechLancer,.,.,.,.,Wall</li>
        <li>Wall,.,.,.,.,.,.,Wall</li>
        <li>Wall,.,.,.,.,AA_Slurrypede,.,Wall</li>
        <li>Wall,.,.,.,.,.,.,Wall</li>
        <li>Wall,Wall,Wall,Wall,Wall,Wall,Wall,Wall</li>
      </li>
    </layouts>
  </KCSG.StructureLayoutDef>
</Defs>
```
`Wall` is a vanilla placeholder standing in for the still-unconfirmed shielding
material; `AA_Slurrypede` used as a bare-thing placeholder pending the same
`KCSG.SymbolDef`+`pawnKindDef` indirection the vaults use for live pawns (§3.9 of
`dungeons_arc_spec.md` — never a bare ThingDef for a pawn in the real build).

**Ending split (per the existing SCOPED note above)**: the ignition→crater world-tile
mutation is filed as its own item, `WAR_LAB_CRATER_HOOK_1` — new companion C# (a
`QuestPart`/`CompDestroyed`/`GameComponent` hook calling the same `PrimaryBiome`-write
+ cache-regenerate sequence `jawa/world_tile_set`/`jawa/world_commit` already prove —
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs`), blocked
on `LIQUID_BIOMES_MAP_1` freezing the propane lake's exact tile footprint. Do not
build the crater hook against an unfrozen footprint.

## criteria
- [ ] Three-band layout authored as `KCSG.StructureLayoutDef`(s) with real (not
  placeholder) shielding/prop defNames, proven on a quicktest by LOOKING
  (`take_screenshot`) per the vault quicktest-proven bar (`dungeons_arc_spec.md` §3.7).
- [ ] `AA_Slurrypede` present as lab fauna via a `KCSG.SymbolDef`+`pawnKindDef`
  (never a bare ThingDef for a live pawn).
- [ ] Lab guardians read as mechanoid/ancient, never Assailant-flesh material (hard
  ban #8, `the_propane_lakes.md` §6) — no Assailant fauna roams; live specimens exist
  only as sealed containment props/props-with-pawn, never a spawned hostile faction.
- [ ] Reachable only via the submerged route (ship lowered into fuel) — no ordinary
  overland entrance.
- [ ] Ignition/crater ending is NOT built here — tracked separately in
  `WAR_LAB_CRATER_HOOK_1`, blocked on `LIQUID_BIOMES_MAP_1`.

## Watch out
🔶 Same discipline as the sibling dungeons in `dungeons_arc_spec.md`: this stays
`doing`, not closed, until the real (non-placeholder) content palette is confirmed and
the site can be committed to the world (needs `LIQUID_BIOMES_MAP_1`'s propane-lake
footprint frozen first). Do not close on a solo placeholder-content pass.

## verify
Lab placed and reachable via the submerged route in a test map; ignition triggers
produce the crater state; the crater persists across save/load; screenshots for the
owner.
