# BLUEDESERT_RM_MOD_BUILD_1 — build RM_BlueDesert as its own RimMandrake mod

**the Blue Desert - BLUE_DESERT_LIFE_AUTHORING_1 builds INTO this mod**

Phase A row 7 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/BlueDesert/` does not exist (confirmed: `ls` errors ENOENT) |
| 2 copy content | ⛔ OWED — 100% of the built cast lives in `src/RimUtinni/UtinniPatches/` today (see §6) |
| 3 freeze RUT_ def | ⛔ OWED — `RUT_BlueDesert.xml`'s header (163 lines, read in full) has no freeze sentence; it still reads as the authoring record, not "carrying the world until the terminal paint" |
| 4 retarget | ⛔ OWED — not started; 3 facts files are already stale (§7) and need correcting regardless of this item |
| 5 prove it loads | ⛔ OWED — Windows Desktop only |
| 6 commit/push | ⛔ OWED — with step 5 |
| paint-list append | N/A yet — `infrastructure/state/facts/biome_paint_list.md` row correctly says `PAINT` (RUT_ still carries the world); becomes owed at close |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_BlueDesert.xml`, 163 lines (measured `wc -l`).
`workerClass` = `BiomeWorker_IceSheet` — **vanilla Core type, not a donor** (line 74) — so
**no `RM_BiomeWorker_<X>` is owed**, unlike most other rows. `modExtensions`: **none on the
BiomeDef itself** (grepped, zero hits). Terrain: `Ice` only (`terrainsByFertility` line
125–131, `lakeBeachTerrain`/`mudTerrain` both `Ice`). Weather: `Clear` 100, every other key
(`Fog`,`Rain`,`DryThunderstorm`,`RainyThunderstorm`,`FoggyRain`,`SnowGentle`,`SnowHard`,
`GrayPall`,`Windy`,`Overcast`,`Blizzard`) zeroed (lines 132–145) — sheet's own "Owed" list
names The Haze/ice-sand-drift/ice-fog as still needing an engine-feasibility pass, not yet
WeatherDefs. Diseases: `Disease_Flu` 100, `Disease_Plague` 80 (both vanilla). No `hediffs`/
`gameConditions` block on the BiomeDef itself.

### 3. wildAnimals split

| defName | commonality | prefix/class | verdict |
|---|---|---|---|
| `RM_Vekkit` | 0.8 | ours (`RM_`) | stays in `RM_BlueDesert` |
| `RM_Dorrak` | 0.5 | ours (`RM_`) | stays in `RM_BlueDesert` |
| `RM_Krissek` | 0.35 | ours (`RM_`) | stays in `RM_BlueDesert` |

Zero `RSW_`/`SW_`/`RUT_`/donor rows in the live `<wildAnimals>` block today — the def's own
comment (line 152) names two Star Wars rows the roster ratifies (Vapaad, AA_Thunderbeast per
the roster JSON — the def's comment itself calls both "the roster's two owner-ruled Star Wars
rows") that are **deliberately not wired anywhere yet**. `WildAnimals_BlueDesert.xml`
**does not exist** (checked `src/RimUtinni/UtinniPatches/Patches/` — no such file) — that
patch is net-new work, not a move.

### 4. wildPlants split

| defName | commonality | class | verdict |
|---|---|---|---|
| `RM_Palefloss` | 1.0 | ours | stays in `RM_BlueDesert` |
| `RM_Glassfern` | 0.5 | ours | stays in `RM_BlueDesert` |
| `RM_Chimeglobe` | 0.25 | ours | stays in `RM_BlueDesert` |
| `AB_ToxiGrass` | 0.6 | donor (Alpha Biomes) | stays inline per §7 Q9 (non-Star-Wars donor) |
| `AB_CrystalHorn` | 0.4 | donor (Alpha Biomes) | stays inline per §7 Q9 |
| `PoisonPlantTallGrass` | 0.4 | donor (vanilla-named) | stays inline per §7 Q9 |

⚠️ **Not an owner rejection to act on**: the def's own comment (lines 87–99) flags these
three donor rows as in tension with sheet §6 ban 1 ("no water-based plants") and says that
tension "stays open for the owner" — it is explicitly *not* a ruling to cut them. Do not
evict them on this item's authority.

### 5. Roster vs def diff

Roster fauna NOT wired: `Vapaad` (0.5, Star Wars per def's own comment) and `AA_Thunderbeast`
(0.005 trace, Star Wars per def's own comment) — both belong in
`WildAnimals_BlueDesert.xml` once authored, never in `RM_BlueDesert` (§7 Q11).
Roster flora: all 3 donor rows + 3 new flora are wired (§4) — no gap.
`new_defs` (roster's Swallower/Burner/Picker/flora placeholders) are now real defs:
`RM_Dorrak`/`RM_Krissek`/`RM_Vekkit` (`ThingDefs_Races/RM_BlueDesertFauna.xml`),
`RM_Palefloss`/`RM_Glassfern`/`RM_Chimeglobe` (`ThingDefs_Plants/RM_BlueDesertFlora.xml`),
`RM_ColdWax` (`ThingDefs_Items/RM_ColdWax.xml`). **Art: MEASURED placeholder, not missing
but not real either** — fauna texPaths point at vanilla `Thrumbo`/`Warg`/`Squirrel` art
(grepped, e.g. line 134/276/409); flora texPaths point at `Things/Plant/RM_Palefloss/...`
etc. but **no PNG exists there** (`find` for the three flora + `RM_ColdWax` under any
`Textures/` returned nothing) — missing-texture placeholders in game, per the closed
item's own report. 20 art jobs already queued (`fill_queue.py`, cited in
`BLUE_DESERT_LIFE_AUTHORING_1`) — do not re-queue.

### 6. Content to move into the mod

| file | reason |
|---|---|
| `Defs/BiomeDefs/RUT_BlueDesert.xml` | becomes `RM_BlueDesert` (copy, then freeze the `RUT_` original) |
| `Defs/ThingDefs_Races/RM_BlueDesertFauna.xml` | RM_Dorrak/RM_Krissek/RM_Vekkit — the biome's own fauna |
| `Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml` | the 3 fractal flora |
| `Defs/ThingDefs_Items/RM_ColdWax.xml` | the shared fuel product |
| `Defs/HediffDefs/RM_BlueDesertCharges.xml` | detonation hediffs |
| `Defs/EffecterDefs/RM_KrissekHalo.xml` | halo VFX |
| `Source/BlueDesertLife.cs` | already namespaced `RimMandrake.BlueDesert` — a file move, not a rewrite |
| 6 settings fields in `Source/UtinniPatchesSettings.cs` (`nativeDetonationsEnabled`, `floraChainReactionsEnabled`, `coldWaxWarmReactiveEnabled`, `butaneGutEnabled`, `burnerHaloEnabled`, `warmDetonationThresholdC`) | per-mechanic toggles that belong on the new mod's own settings screen (§6a shape), not the campaign patch mod |

**Stays in Utinni, not moved**: `WildAnimals_BlueDesert.xml` once authored (Star Wars fauna,
§3/§5). **No change needed**: `PlantGrowth/Defs/JawaPlantGrowthSettings.xml`'s
`exemptPlants` already lists `RM_Palefloss`/`RM_Glassfern`/`RM_Chimeglobe` by name (lines
45–47) — it keys off the defName, which does not change on the move, so this cross-mod file
needs no edit.

**C#**: assembly today is `RimMandrake.Utinni.UtinniPatches.dll`
(`src/RimUtinni/UtinniPatches/Source/RimMandrake.Utinni.UtinniPatches.csproj`). ⚠️ That
csproj sets `EnableDefaultCompileItems=false` and lists `BlueDesertLife.cs` explicitly
(line 70) — moving the file means **removing that `<Compile Include>` line** from this
csproj AND adding one to the new mod's own csproj, or it silently drops out of both builds.

### 7. References to `RUT_BlueDesert` across the repo (36 files grepped, read by category)

**(a) Retarget-outright** (target doesn't need to be on the world): `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md` (named explicitly as a step-4 retarget target), `design/Jawa/worldbuilding/biome_flora_rosters.md:60`, `design/Jawa/worldbuilding/explosive_plant_growth_design.md:438`.

**(b) Comment/prose — leave**: `RUT_Desert.xml:9,34` (precedent comment in a different biome's def), `BiomeFlora_Ashkarr.xml:32` (comment inside the "deliberately does NOT patch" block — same shape as Greentide's exemplar), `FishTypesStrip_NoFishBiomes.xml:52`, `BiomeDescriptions_Ashkarr.xml:65-66,110` (the actual `PatchOperationConditional` at that line targets `BiomeGRimond`'s description, not `RUT_BlueDesert` — the mention is a trailing comment; `RM_BlueDesert` will carry its own native `<label>`/`<description>` exactly as `RM_Greentide` does, so **no second op is needed here**), `biome_wildbiomes_evictions.py:69`, `vapor_emitter_review_2026-09-12.md:175` (historical review doc), `rosters_to_cast.py:34` (accurate as written — `gen_cast_patch.py` correctly still skips `RUT_` defs it never claimed; unaffected by Phase A).

**### False statements found elsewhere**
- `infrastructure/state/facts/biome_rosters.md:82` — heading "`RUT_BlueDesert` is empty because its life was never AUTHORED" is **false now**: `BLUE_DESERT_LIFE_AUTHORING_1` closed 2026-09-21 and the def carries `animalDensity` 0.5, `plantDensity` 0.33, 3 wildAnimals, 6 wildPlants rows. BENCH should correct or delete this section.
- `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md:28` — "`<wildAnimals />` is EMPTY" is **false now**, same reason.
- `infrastructure/state/facts/biome_paint_list.md` (RUT_BlueDesert row) — "no `wildAnimals` block found... fauna not yet authored (tracks the open item `BLUE_DESERT_LIFE_AUTHORING_1`)" is **false**: that item is closed (`4299f9262`) and the def now has fauna+flora; the row's "140 lines" is also stale (now 163).
- `src/RimUtinni/UtinniPatches/build_desert_review_sheet.py:8,819` — its own header/output prose ("RUT_BlueDesert was dropped from this pass... it is UNAUTHORED") is a report generator whose claim is now stale for the same reason; low-priority (a report script, not live-read), flagging rather than fixing.

**UNCERTAIN**: `design/Jawa/mods/biome_flora.py` (lines 172, 330, 333, 468) carries a `RUT_BlueDesert` dict entry feeding a flora-patch generator, but `BiomeFlora_Ashkarr.xml`'s own comment says it already excludes `RUT_BlueDesert` (authored in its own def) — did not verify whether this dict entry is dead code or still consumed by another generator step; did not check `src/RimMandrake/Utils/ecosystem_pyramid_check.py:49,53` closely enough to say whether it needs a parallel `RM_BlueDesert` entry now or only at Phase B.

### 8. Mechanics/kit state

No separate kit spec exists for the Blue Desert (`kits/` has no `blue_desert_kit_spec.md` —
it is a standalone biome, §2a). All of its mechanics are **already SHIPPED**, built and
compiling clean in `RimMandrake.Utinni.UtinniPatches.dll` (`BlueDesertLife.cs`): plant/fauna
detonation comps, the krissek halo, the cold-wax warm-reactivity comp, the butane-gut
ingestion doer. Nothing here is unbuilt or blocking step 2 — it is a straight file move.
Deliberately NOT built and NOT owed by this item (per `BLUE_DESERT_LIFE_AUTHORING_1`'s own
carried-forward list): a `RM_ColdWax`→Chemfuel refinery recipe, a real `CompGlower` on the
krissek, corpse warm-reactivity, juvenile blast radius tuning — none of these block the move.

### 9. Dependencies & items building INTO this mod

- `BLUE_DESERT_LIFE_AUTHORING_1` — **CLOSED** 2026-09-21 at `4299f9262` (`rimflow show`
  confirms `done`). It built the entire cast into `UtinniPatches` *because this item was
  unclaimed at the time* (its own "Housing decision" section says so verbatim) — this
  item's step 2 is exactly the move that item deferred. Blocks step 2 by definition.
- `SW_FAUNA_NEVER_IN_RM_TIER_1` — proposed, needs offline. Names the 97 Star Wars rows
  across 12 `RUT_` biomes that must route through Utinni patches; Blue Desert's 2 rows
  (Vapaad, AA_Thunderbeast) are part of that count but currently unwired anywhere — lands
  later (authoring `WildAnimals_BlueDesert.xml`), does not block step 1–4.
- `HELIX_TELLUROX_BUILD_1` — mentions `RUT_BlueDesert` re: `cast_assignment.csv` having zero
  rows for it; unrelated tracking, does not block this item.
- `WORLD_REMAKE_FINAL_STEP_1` — owns the paint list this item must append to at close; lands
  later (Phase B prerequisite), not a step 1–4 blocker.

### 10. Blockers

**None for steps 1–4.** Step 5 (prove it loads) needs the Windows Desktop machine — not a
blocker of starting tomorrow morning, per the brief's own rule that a Desktop-only step
isn't a blocker of steps 1–4.

### 11. Concrete step plan

1. `deploy_custom_mods.py --mod BlueDesert` dry run, then scaffold
   `src/RimMandrake/BlueDesert/About/About.xml`, packageId `mandrake.rm.bluedesert`,
   `loadAfter`: `mandrake.rm.environmentalhazards` (BlueDesertLife.cs's comps follow the
   same idiom as the other kits' `CompProperties`/`ThingComp` pattern used against that
   library elsewhere — verify the exact base classes on the move) — UNMEASURED whether
   `BlueDesertLife.cs` actually subclasses anything from `EnvironmentalHazards` today
   (its classes look self-contained: `ThingComp`/`HediffComp`/`CompEffecter` direct from
   Core) — if confirmed self-contained, `loadAfter` may need only `mandrake.rut.patches`
   reversed (this mod loads BEFORE it, per §3d) and no RimMandrake library dependency.
   `RM_BlueDesertSettings : ModSettings` with a master toggle + the 6 fields from §6, empty
   `Defs/BiomeDefs/`.
2. Copy in: the 6 files listed in §6, editing `RUT_BlueDesert` → `RM_BlueDesert` in the
   BiomeDef's `defName` only (label/description/content unchanged). Move
   `BlueDesertLife.cs` into `src/RimMandrake/BlueDesert/Source/`, namespace already correct
   (`RimMandrake.BlueDesert`) — no rename needed, only the file move + csproj edits (§6).
   Leave `Vapaad`/`AA_Thunderbeast` OUT — author
   `UtinniPatches/Patches/WildAnimals_BlueDesert.xml` as a `PatchOperationAdd` onto
   `RM_BlueDesert`, `MayRequire="mandrake.rsw.swbestiary"`, shaped like
   `WildAnimals_Pyrelands.xml`.
3. Freeze `RUT_BlueDesert.xml` byte-for-byte with the standard header sentence naming
   `mandrake.rm.bluedesert`.
4. Retarget the 3 retarget-outright files in §7(a); fix the 3 false statements in §7 in the
   same pass (correctness outranks seat ownership, CLAUDE.md). No second-op file is needed
   (§7b covers why `BiomeDescriptions_Ashkarr.xml` needs none).
5. Minimal list + `BlueDesert` + `mandrake.rut.patches` + all 5 expansions; `validate_patch.py
   --live --defs` on `WildAnimals_BlueDesert.xml`; quicktest map on a scratch world tile set
   to `RM_BlueDesert`.
6. One commit, explicit paths (the 6 moved files + new mod scaffold + csproj edits + the
   retarget/correction files), message naming that the `RUT_` twin was carrying content that
   belonged in the RimMandrake tier. Append to `WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.bluedesert`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_BlueDesert` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_BlueDesert`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.bluedesert`; do not edit here."* From that moment
   every content fix lands in `RM_BlueDesert` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_BlueDesert` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_BlueDesert` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.bluedesert` exists, deploys, and loads clean carrying `RM_BlueDesert` with its own content and its own
Mod Settings screen; the `RUT_` twin is frozen with its header and unchanged; the Star Wars
fauna ride a Utinni patch rather than the RimMandrake def; one commit, explicit paths, the
message naming what the twin got wrong; and the mod is appended to
`WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## Watch out

- ⛔ **Do not paint, and do not cite a tile count as evidence about this biome.** The planet
  is painted ONCE, at the end. A def of ours carrying 0 tiles is the expected mid-migration
  state, not a defect.
- ⛔ **Do not delete the `RUT_` def.** Deleting a painted def before Phase B destroys the
  save.
- ⚠️ A `<li>` in the wrong place discards the WHOLE def, silently.
