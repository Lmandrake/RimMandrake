<!-- status: reconciliation record — the OFFLINE half of LIQUID_BIOMES_MAP_1 only.
     The live/paint half (world tiles, the propane lake's exact subset, the
     owner-reviewed worldview.py render, the savegame re-freeze) is NOT done
     here and is not this document's job to rule on. -->

# LIQUID_BIOMES_MAP_1 — def reconciliation, 2026-09-06

FOUNDRY, offline half only. `python3 src/RimMandrake/rimflow/cli.py show LIQUID_BIOMES_MAP_1`
asks: which existing sea defs are the boiling ocean and the two brine seas, what each
needs to become a distinct liquid biome def, and (optionally) a distinct def for the
propane lake. This is that reconciliation, plus the four new defs it produced.

## 0. The four seas, matched to real defNames and real tiles

MEASURED against `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 data rows,
sha256:b38fd68569237c96) via `~/.claude/skills/measuring-large-artifacts`, and against
the live def dump (`defs.sqlite`, mods=596/cec112bad2152f47, captured=2026-09-05T14:41:26Z
— 2 mods behind the live 598-mod `ModsConfig.xml`; close enough for def-shape
reconciliation, NOT close enough to trust for a paint pass without a fresh capture).

| item's name | design doc | region (CSV) | tiles | biome today | new def authored |
|---|---|---|---|---|---|
| **boiling ocean** | *(no biome sheet — see §2)* | `Scald` | 312, water=1 on all 312 | `Lake` (vanilla) | `RUT_TheScald` |
| **brine sea 1** | `terminator_sea.md` — Twilight Sea (θ91, bearing 170, moldy) | `Twilight Sea` | 852 total; 442 `Ocean` + 171 `SeaIce` + 239 land shore | `Ocean` (vanilla) | `RUT_TwilightSea` |
| **brine sea 2** | `terminator_sea.md` — Grey Sea (θ92, bearing 8, salt-encrusted, shrinking) | `Grey Sea` | 617 total; 381 `Ocean` + 91 `SeaIce` + 145 land shore | `Ocean` (vanilla) | `RUT_GreySea` |
| **propane lake** | `the_propane_lakes.md` | `Umbra` | 802 total (`AB_PropaneLakes` 558, `BMT_CrystalCaverns` 244); **water=0 on all 802** | *(no water tile exists yet)* | `RUT_PropaneLake` (unpainted) |

The "the three seas" phrase the item and `README_BIOME_GRAMMAR.md`/`tile_augmentation_matrix.md`
use resolves to **the Scald, the Twilight Sea and the Grey Sea** — confirmed by
`tile_augmentation_matrix.md:85` ("the three seas (`Lake`/Ocean: the Scald, Twilight,
Gray)") and `hiding_the_gravship.md:303` ("1,780 water tiles, three seas... The Scald
(312 tiles..."). The propane lake is a fourth, separate body the item adds on top —
it is not one of "the three seas."

## 1. The engine facts this reconciliation rests on

- **`BiomeDef.waterDeepTerrain` / `waterShallowTerrain` / `oceanDeepTerrain` /
  `oceanShallowTerrain` / `waterMovingShallowTerrain` / `waterMovingChestDeepTerrain`**
  are real fields (`Source/RimWorld/BiomeDef.cs:119-127`, confirmed via
  `mcp__rimsage__read_csharp_symbol`), consumed per-tile by `MapGenUtility.cs`
  (`map.BiomeAt(cell).waterDeepTerrain ?? TerrainDefOf.WaterDeep`, etc.) — this is how a
  biome gets its own water look, and it is a BiomeDef-level override, not a per-tile one.
- **`waterBodyType` lives on the TerrainDef, not the BiomeDef** (`Verse.WaterBodyType`:
  `None` / `Freshwater` / `Saltwater` / `Other`, enumerated via ilprobe). There is no
  engine tier for "hypersaline" beyond `Saltwater` — vanilla `WaterOceanDeep`/
  `WaterOceanShallow` already carry it, so the terminator seas' brine chemistry is
  already expressed at the only granularity the engine has.
- 🔴 **`Lake` and `Ocean` (`Core/Defs/BiomeDefs/Biomes_Water.xml`) carry no `Name="..."`
  attribute on their own `<BiomeDef>` tag.** Verified by direct read of the file, the
  same trap `RUT_NightsideIce.xml` already found for `IceSheet`. `ParentName="Lake"` or
  `ParentName="Ocean"` would silently fail to resolve — every new def below restates the
  vanilla shape directly instead of inheriting it.
- Both `Ocean` and `Lake` are otherwise almost field-empty (`isWaterBiome`,
  `canBuildBase false`, `impassable true`, `isBackgroundBiome true`, a `workerClass`, a
  `texture` — nothing else) — matching `the_seas.md`'s own finding that "the seas are
  faunaless: `Ocean` and `Lake` have empty `wildAnimals`."
- **`WaterDeepBase` / `WaterChestDeepBase` / `WaterShallowBase`** (`Core/Defs/TerrainDefs/
  Terrain_Water.xml:41,73,103`) **do** carry `Name="..."` — `ParentName` against them is
  safe, and is how every new terrain def below is built.

## 2. The boiling ocean = the Scald — and it has no biome sheet

The Scald (crater lake, `ASHKARR_WORLD_DEFINITION.md`'s Sea table: centre (35,185),
radius 10.5, ruled −30 m / live-measured −350 m, "a terminal pan" with eight rivers
ending in it and none leaving) sits in the Anvil substellar band (arc 0-30, +70→+58 °C)
— "the hottest lake in the hottest place." `terminator_sea.md` §2 uses it only as a
comparison foil for the terminator seas' own definition ("Why the terminator's coast is
salt and the Scald's coast is jungle") — it does not define the Scald's own roster,
weather or hard bans.

**No file under `design/Jawa/worldbuilding/biomes/` is a Scald biome sheet.** Checked:
no `the_scald.md`, no `the_anvil.md`. `README_BIOME_GRAMMAR.md`'s table row
(`terminator_sea.md | the three seas | ✅ done`) overclaims for the Scald specifically —
worth a line-fix once a real Scald sheet exists, not done in this pass (a table caption
is not a ruling to make unilaterally, and the fix is one line once someone owns it).

⇒ **This is why `RUT_TheScald.xml`'s `wildAnimals`/`coastalWildAnimals` ship empty**: there
is no owner-reviewed sheet to draw a roster from, and inventing lore for a whole named
sea is exactly the kind of call `biomes-sheets-are-a-conversation-loop` reserves for the
owner sitting with BENCH, one biome at a time — not a FOUNDRY judgment call.

### The boiling-lift mechanic — reconciled against `REGROWTH_BOILING_LIFT_SPEC.md`

The item's own words point at this spec ("the boiling-lift spec's scald water"). Its
ruling (R-B3, 2026-08-15) was **route (b): author six `Jawa_ScaldWater*` TerrainDefs in
`src/Jawa/Jawa_Patches` — never built.** Confirmed this pass: `measure get` against the
live dump finds zero defs named `Jawa_ScaldWater*` (`UNMEASURED`, exit 2, not `MEASURED 0`
— the type IS in the dump's 529-complete coverage, so this is a real absence, not a
capture gap). `src/Jawa/Jawa_Patches` itself no longer exists — the mod split
2026-09-04 (`JAWA_PATCHES_SPLIT_1`) into `mandrake.rut.patches` (UtinniPatches) and
siblings, and the spec was never carried forward.

⇒ **Authored this pass**, renamed under the tier grammar (new authorship takes the new
prefix directly rather than waiting on `NAMING_SCHEME_EXECUTION_1`, which only covers
migrating OLD names) and rehomed to the live mod:
`src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldWater.xml` — six terrain defs
(`RUT_ScaldWaterDeep/Shallow/OceanDeep/OceanShallow/MovingShallow/MovingChestDeep`),
R-B4a's values verbatim: cyan glow `(2,154,229)`/radius 2, burn 1/300t (shallow+moving) /
2/240t (deep+chestdeep), `traversedThought HotSpring`, `avoidWander true`, `dbh_water` tag
(`dubwise.dubsbadhygiene.thirst`/`.lite` confirmed ACTIVE in the live `ModsConfig.xml` this
pass — R-H1's water-is-currency economy depends on this tag). `waterBodyType` left at the
inherited `Freshwater` default on the non-ocean variants — **no design doc calls the
Scald basin itself saline**, unlike the two terminator seas, so this was NOT changed
unilaterally; flagged here as an open question rather than decided.

**`RUT_TheScald.xml`** (new `BiomeDef`, `isWaterBiome true`, shape restated from vanilla
`Lake`) wires `waterDeepTerrain`/`waterShallowTerrain`/`waterMovingShallowTerrain`/
`waterMovingChestDeepTerrain` to the four matching `RUT_ScaldWater*` terrains. **Why a new
BiomeDef and not a patch to vanilla `Lake` in place**: `Lake` is not the Scald alone — the
same CSV shows a second region, `Damp` (10 tiles), also painted `biome=Lake`. Patching
`Lake` globally would boil that lake too, which nothing asks for.

## 3. The two brine seas = Twilight Sea + Grey Sea — already fully defined, never implemented

`terminator_sea.md` (owner-ratified, 2026-09-05) is thorough and settled: both seas
hypersaline, terminal, no outflow; each sea endemic and alone ("every large organism in a
terminator sea exists in that sea and nowhere else in the universe"); hard bans on lush
flora, herds/flocks, high species count, freshwater life. **None of that is implemented
anywhere** — both seas currently paint plain vanilla `Ocean` (823 tiles total, splitting
exactly 442/381 between the two regions with nothing left over — confirmed against the
CSV, so patching vanilla `Ocean` in place would not leak onto a third region the way
`Lake` would).

**Authored this pass**: `RUT_TwilightSea.xml` and `RUT_GreySea.xml` — both restate
`Ocean`'s vanilla shape (same `Name=` trap as `Lake`). **Water terrain deliberately left
unchanged** — vanilla `WaterOceanDeep`/`WaterOceanShallow`'s `waterBodyType Saltwater` is
already the engine's full expression of "hypersaline" (§1); no new TerrainDef is
warranted here the way the Scald needed one, because there is no distinct *mechanic* to
carry, only a distinct *identity* (so the two seas can hold different, non-shared
faunas per the sheet's "endemic and alone" ban on repeats). A visually distinct "dull
steel and bone, never blue" water texture (`terminator_sea.md` §9) is real, wanted, and
NOT done here — it is art work, not a def reconciliation.

`wildAnimals`/`coastalWildAnimals` on both: empty, same reasoning as the Scald. The sheet
names roster SHAPE ("a single mat/film organism per sea... one or two enormous, ancient,
solitary brine animals per sea, endemic to it") but no defNames — that is
`SEAS_WATERLINE_PASS_1` / `SW_SEA_MONSTERS_ART_1` territory (`the_seas.md`'s own
sequencing), a separate item this reconciliation does not fold in.

`SeaIce` tiles inside both regions (171 Twilight, 91 Grey) are frozen margin, not liquid
— out of this item's scope by its own title.

## 4. The propane lake — a bigger gap than "which def," and a real donor asset to reuse

**Finding, not previously written down anywhere in the design docs checked**:
`AB_PropaneLakes` (Alpha Biomes, `sarg.alphabiomes`) is a **land** biome —
`canBuildBase true`, `isWaterBiome false`, `impassable false` (read off the live dump this
pass). Its "liquid propane lake" is a **local-map terrain patch**, generated by its own
`terrainPatchMakers` (perlin fertility 0.76-999 → `AB_PropaneLake`; 0.56-0.76 →
`AB_SolidPropane`) — every one of the 558 Umbra tiles painted `AB_PropaneLakes` today
already generates a working lake-and-crust patch on any colony built there. That is a
real, shipped feature and this item does not touch it.

What `the_propane_lakes.md` §0 actually measured as missing is different and bigger: a
**world-map water tile** — `Umbra` reads `water=0` on all 802 of its tiles (confirmed
this pass, both `AB_PropaneLakes`' 558 and `BMT_CrystalCaverns`' 244). A tile that shows
blue on the planet view the way the Scald and the two brine seas already do needs an
`isWaterBiome` BiomeDef, the way `Ocean`/`Lake` are — `AB_PropaneLakes` cannot become one
without losing everything that makes it settleable.

**Authored this pass (unpainted)**: `RUT_PropaneLake.xml` — `isWaterBiome true`, shape
restated from `Ocean`/`Lake` (same `Name=` trap). **Reuses the donor's own terrain rather
than inventing new ones** — `waterDeepTerrain -> AB_PropaneLake` (liquid centre,
`waterBodyType None` — correctly NOT drinkable by DBH or anything else, matching
"propane, not water"), `waterShallowTerrain -> AB_SolidPropane` (frozen margin crust,
`Standable`) — physically the right pairing for a phase-line lake (R-H6b: propane
liquefies at −42 °C, so the cold shallow edge freezes while the deep centre stays
liquid). `wildAnimals`/`fishTypes` left empty: the sheet's V-wake creature has no
PawnKindDef yet (checked the live dump — nothing named anything resembling "V-wake"),
and `AB_PropaneLakes`' own donor `fishTypes` (`VCEF_PropaneBag`, `VCEF_AbyssalEel`, etc.)
belong to the land biome's local-map fishing zones, a different gameplay surface —
copying them here would be a content decision, not an engine reconciliation.

🔴 **`RUT_PropaneLake` is authored but not wired to any tile.** Painting it — and picking
which subset of the 332 arc≥165 `AB_PropaneLakes` tiles becomes "the lake proper" — is
explicitly owner-gated by render (`the_propane_lakes.md`'s own Owed list; the item text)
and is NOT decided here.

## What remains owed (all of it explicitly out of this pass's scope)

- **The render + the paint** — `worldview.py`, owner review, then `jawa/world_tile_set`
  (or equivalent) onto the Scald's existing 312 tiles (biome swap `Lake` →
  `RUT_TheScald`), the Twilight Sea's 442 (`Ocean` → `RUT_TwilightSea`), the Grey Sea's
  381 (`Ocean` → `RUT_GreySea`), and — separately, gated on its own render decision —
  whichever propane-lake tile subset the owner rules.
- **A Scald biome sheet** (`the_scald.md` or similar), owner conversation, the same shape
  `terminator_sea.md`/`nightside_ice.md` already have — needed before `RUT_TheScald`'s
  `wildAnimals`, `diseases`, `baseWeatherCommonalities`, `settleWarning` etc. can be
  filled in for real.
- **`README_BIOME_GRAMMAR.md`'s "the three seas ✅ done" line** — overclaims for the
  Scald; a one-line fix once the sheet above exists (superseding-doc discipline: not
  touched here because the underlying gap it should point at doesn't have an owner yet).
- **Fish/fauna for all four** — `SEAS_WATERLINE_PASS_1`'s repatriation cast (KwazelMaw,
  Mott, Dianoga, Dragonsnake, Fambaa, Fanback, Blixus) needs assigning per sea by name,
  not just "Lake/coastal biomes" as a class; the terminator seas' own endemic giants and
  the propane lake's V-wake creature need PawnKindDefs authored and normalized
  (`SW_SEA_MONSTERS_ART_1`'s sequencing).
- **Art**: a distinct terminator-sea water texture ("dull steel and bone, never blue");
  a dedicated propane-lake world-map icon distinguishing it from the surrounding
  `AB_PropaneLakes` land tiles (currently reuses the donor's own `Biomes/AB_PropaneLakes`
  as a placeholder).
- **The ancient war lab** beneath the propane lake, and the crater-transformation map
  permanence — `ANCIENT_WAR_LAB_1`, unrelated to this item beyond needing the lake's
  tile set to "leave it a home" (the item's own text).
- **Savegame re-freeze** — standing procedure, only relevant once the live paint happens.
- **`dbh_water` verification** — R-B4a's own caveat, restated: verify the tag against
  Dubs Bad Hygiene's own reader before relying on it in play.

## Files this pass produced

- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldWater.xml`
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheScald.xml`
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TwilightSea.xml`
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_GreySea.xml`
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PropaneLake.xml`
- This document.

All five validate clean: `python3 skills/rimworld-modding/scripts/validate_patch.py
<files> --defs ... --live ...` → `OK TOTAL - 5 file(s), 0 error(s), 0 warning(s)`. None
of the five defNames collided with anything in the live dump (`measure get` on each:
`UNMEASURED` = free, not a capture gap — `coverage` confirms 529 def types complete).
