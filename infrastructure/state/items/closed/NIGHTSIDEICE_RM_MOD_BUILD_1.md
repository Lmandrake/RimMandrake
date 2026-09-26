# NIGHTSIDEICE_RM_MOD_BUILD_1 — build RM_NightsideIce as its own RimMandrake mod

**the Nightside Ice - thin by design, but a Lantern Deeps host surface**

Phase A row 5 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

🔑 **Correction to the readiness grade:** `Transient/biome_design_readiness_2026-09-23.md:44,91`
grades this biome **DESIGN-PASS-OWED** solely because `rosters/nightside_ice.json` has **0**
flora rows. That is wrong. The sheet's own words: §6 *"No photosynthesis and no
photosynthetic tissue of any kind"* / *"No lush flora of the ordinary kind"*
(`design/Jawa/worldbuilding/biomes/nightside_ice.md:252,267`), and the roster itself
records it as a ruling, not a gap: `"flora_purged": [{"def": "ALL", "reason": "flora list
ships empty by law: §6 — no photosynthesis or photosynthetic tissue of any kind..."}]`
(`rosters/nightside_ice.json:148-152`). Zero flora is the FROZEN ruling
(`BIOME_FREEZE_FABLE_REVIEW_1`), not owed design work. The def matches: no `<wildPlants>`
element exists in `RUT_NightsideIce.xml` at all. **This item is design-complete on flora;
nothing is owed there.** (Filed under False statements below too, since the readiness doc
is someone else's file.)

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/NightsideIce/` exists (MEASURED: `ls src/RimMandrake \| grep -i night` → empty) |
| 2 copy content | ⛔ OWED — only `RUT_NightsideIce.xml` (185 lines) exists; no `RM_NightsideIce` def, no `RM_BiomeWorker_*`, no Utinni fauna patch |
| 3 freeze the twin | ⛔ OWED — current header (`RUT_NightsideIce.xml:4-68`) is the 2026-09-07 authoring note, not the "carrying the world until terminal paint" freeze notice §5 step 3 requires |
| 4 retarget | ⚠️ PARTIAL — measured, nothing written yet. 1 live PatchOperation needs a second op (§7 below); ~10 doc/tooling refs are retarget-outright; the rest of ~90 repo hits are comments/prose or out-of-scope paint/history artifacts |
| 5 prove it loads | ⛔ Windows Desktop only |
| 6 commit/push | ⛔ owed with step 5 |
| paint-list append | ⛔ OWED, bundled with step 6 — `infrastructure/state/facts/biome_paint_list.md:35` currently lists only `RUT_NightsideIce` (pre-migration state, correct as-is); appending `RM_NightsideIce` is step 6's job |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml`, **185 lines** (MEASURED
`wc -l`; `infrastructure/state/facts/biome_paint_list.md:35` says 173 — stale, pre-dates the
2026-09-21 `RSW_CaveLemming` addition; flagged below).

- `workerClass` = `BiomeWorker_IceSheet` (line 74) — **vanilla Core class, not a donor type.**
  No `RM_BiomeWorker_<X>` is owed (unlike Greentide's donor worker).
- No `<modExtensions>` block anywhere in the file — nothing to attribute to a shared mod.
- Terrain: `terrainsByFertility` → `Ice` only (−999..999); `lakeBeachTerrain`/`mudTerrain` = `Ice`.
- Weather: `baseWeatherCommonalities` — `Clear` 100, every other entry (Fog, Rain,
  DryThunderstorm, RainyThunderstorm, FoggyRain, SnowGentle, SnowHard, GrayPall[Anomaly],
  Windy[Odyssey], Overcast[Odyssey], Blizzard[Odyssey]) = 0.
- Disease: `Disease_Flu` 100, `Disease_Plague` 80, `Disease_OrganDecay` 10 (line 99-112).
- `wildPlants`: **element absent entirely** — matches roster's `flora: []` (see above).
- `coastalWildAnimals`/`allowedPackAnimals`: both empty (`<... />`, lines 181-182).

### 3. wildAnimals split

8 rows (lines 153-179), all donor or RimStarWars-tier — **zero vanilla, zero `RM_` rows.**

| defName | commonality | prefix | verdict |
|---|---|---|---|
| `AA_BoulderMit` | 0.004 | `AA_` (Alpha Animals, `sarg.alphaanimals`) | **stays in `RM_NightsideIce`** — §3b: "non-Star-Wars fauna... stay in the RimMandrake def" |
| `AA_SummitCrab` | 0.004 | `AA_` | stays |
| `AA_RedGoo` | 0.003 | `AA_` | stays |
| `AA_Terramorph` | 0.003 | `AA_` | stays |
| `AA_Slurrypede` | 0.002 | `AA_` | stays |
| `AA_TetraSlug` | 0.002 | `AA_` | stays |
| `AA_ShockGoat` | 0.03 | `AA_` | stays |
| `RSW_CaveLemming` | 0.03 | `RSW_` (`mandrake.rsw.swbestiary`) | **→ Utinni patch** `WildAnimals_NightsideIce.xml` onto `RM_NightsideIce`, `MayRequire="mandrake.rsw.swbestiary"` |

`WildAnimals_NightsideIce.xml` **does not exist yet** (MEASURED: `ls
src/RimUtinni/UtinniPatches/Patches/WildAnimals_*.xml` → CrackedLands, Greentide, Pyrelands
only). Only 1 of 8 rows needs it — architecture §3b overrides the generic item text's "every
`RSW_`/`SW_`/`RUT_` entry stays out": that rule is about the Star Wars/campaign layer, and
Alpha Animals' `AA_` donor fauna is neither — 7 of 8 rows are franchise-free and belong in
the RimMandrake def directly, same as Greentide's vanilla rows.

### 4. wildPlants split

**Both sides are 0, correctly.** No table — `<wildPlants>` is absent from the def, and the
roster's `flora` array is `[]` with an explicit purge ruling (`flora_purged`, quoted above).
No plant is barred by a specific owner ruling here because none was ever proposed; the ban
is categorical (§6, "no photosynthesis ... of any kind").

### 5. Roster vs def diff

Roster `fauna` = 10 rows; def `wildAnimals` = 8. **2 roster rows deliberately unwired:**
`Tauntaun` and `Wampa` (both "visitor" band, commonality 0.03 each) — the def's own comment
(`RUT_NightsideIce.xml:159-167`) says they're left out on purpose: both are LARGE
(bodySize 1.0 / 6) and adding them would push the ecosystem-pyramid ratio the wrong way,
already strained by `RSW_CaveLemming`'s deliberate 2026-09-21 override. Not a gap.
**0 def rows outside the roster** — all 8 trace to a roster row.

Per-def source/art (donor rows are a 3rd-party mod's own art, not ours to check):

| def | source | art |
|---|---|---|
| 6× `AA_*` imports + `AA_ShockGoat` | donor mod `sarg.alphaanimals` | not ours — UNMEASURED/out of scope |
| `RSW_CaveLemming` | ours, RimStarWars tier | ✅ present: `src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/CaveLemming/CaveLemming_south.png` (real file, checked `_south`, not `_southm`) |
| `Tauntaun`, `Wampa` (unwired) | donor, not in `src/` (grepped, no hit) | UNMEASURED — unwired, out of scope |

### 6. Content to move into the mod

This biome has **no kit spec** (`kits/nightside_ice_kit_spec.md` does not exist) and **no
absorbed `mandrake.rut.*` kit mod** — it is the thinnest row in §2a. Content to move:

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml` → `git mv` + rename to
  `src/RimMandrake/NightsideIce/Defs/BiomeDefs/RM_NightsideIce.xml`, defName `RM_NightsideIce`.
  That is the **entire content payload** — one file.
- New, not moved: `About/About.xml` (`mandrake.rm.nightsideice`), a minimal
  `RM_NightsideIceSettings : ModSettings` (Master toggle only — no kit mechanics exist to
  gate, §6a), and its own `Assemblies/RimMandrake.NightsideIce.dll` + `.csproj`.

Stays in Utinni (Star Wars / campaign / doctrine, correctly):
- `RSW_CaveLemming` row → new `WildAnimals_NightsideIce.xml` patch (above).
- `AncientDangerGenSteps_AmbientDoctrine.xml` — doctrine patch, needs a **second op** (§7).
- `BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`, `FishTypesStrip_NoFishBiomes.xml`
  — comment-only for this biome (§7), nothing to move.

### 7. References to `RUT_NightsideIce` across the repo

`grep -rl` found **~90 hits** across the repo (design docs, world/ paint-history scripts,
closed items, dashboards, handoffs, review artifacts). Reading each: **1 live patch
operation, ~10 retarget-outright doc/tooling refs, and the rest are comments, prose,
frozen/closed history, or paint-pass artifacts out of this item's scope** (governed by
`BIOME_PAINT_ONCE_AT_THE_END_1`).

**(b) needs a second op** — must keep working on the live world (still 100% `RUT_` tiles):
- `src/RimUtinni/UtinniPatches/Patches/AncientDangerGenSteps_AmbientDoctrine.xml:174-183` —
  a real `PatchOperationConditional`/`PatchOperationAdd` pair on
  `BiomeDef[defName="RUT_NightsideIce"]/preventGenSteps` (ancient-danger deny). Per §5 step 4
  this is exactly the "doctrine patch" class that gets a second `RM_NightsideIce` op now.
- **The Lantern Deeps allowlist (the addendum's question, answered):** it keys on
  **biome defName membership, not a temperature test at runtime** — confirmed in code, not
  just the sheet's stated intent. `LanternDeepsSettings.IsEntranceBiome` checks
  `entranceBiomeSet.Contains(biome.defName)` against the default array
  `UtinniDefaultEntranceBiomes = {"BiomeGRimond", "RUT_NightsideIce", "RUT_PropaneLake"}`
  (`src/RimUtinni/LanternDeeps/Source/LanternDeepsMod.cs:52-59`), and
  `LanternDeeps/validation.py:83`'s `QUALIFYING_BIOMES = {"BiomeGRimond",
  "RUT_NightsideIce", "RUT_PropaneLake"}` mirrors it. Architecture §4e already flags this
  exact gap: *"Its allowlist checks name `RUT_NightsideIce`... and must follow §2's renames
  — but note the FROZEN sheet says the host test is temperature, so a biome allowlist in the
  code is already a departure."* **Not a step-1–4 blocker for THIS item** — the array only
  needs `RM_NightsideIce` ADDED alongside `RUT_NightsideIce` (both must resolve while the
  world still carries `RUT_` tiles and the Deeps mod hasn't moved tier yet), and that edit
  lands in `LanternDeepsMod.cs`/`validation.py`, i.e. **`LANTERNDEEPS_RM_MOD_BUILD_1`'s file**,
  not this one — flag it there, don't fix it here.

**(a) retarget-outright** (target need not be on the world): `biome_flora_rosters.md:29`,
`biomes/_def_bindings_2026-09-09.md:26,123`, `biomes/README_BIOME_GRAMMAR.md:134`,
`design/Jawa/mods/biome_flora.py:316,335` (`PLANTLESS` set), `design/Jawa/fauna/
rosters_to_cast.py:35`, `infrastructure/state/facts/biome_rosters.md:67`.

**(c) comment/prose — leave**, same shape as Greentide's cleared five:
`BiomeDescriptions_Ashkarr.xml:65` ("NOT PORTED" list, prose only),
`BiomeNames_Ashkarr.xml:6` (explanatory prose, no defName touched — file is LABEL ONLY by
design), `FishTypesStrip_NoFishBiomes.xml:51` (prose: "already ship `fishTypes` empty"),
6 sibling `RUT_*BiomeDefs/*.xml` files citing `RUT_NightsideIce` only as a precedent comment
(`RUT_BlueDesert.xml`, `RUT_ExtremeDesert.xml`, `RUT_GreySea.xml`, `RUT_PropaneLake.xml`,
`RUT_TheScald.xml`, `RUT_TwilightSea.xml`, `RUT_FuelSnows.xml`, `Jawa_BackgroundWater.xml`,
`RUT_ScaldWater.xml`), `design/RimMandrake/biome_mod_architecture.md` itself (this spec).
Validation walks (`design/validation_walks/RimUtinni/UtinniPatches.md`,
`.../LanternDeeps.md`) assert `RUT_NightsideIce` currently exists and loads — true today,
becomes stale only once the world is repainted (Phase B), not this item's concern.
`canon.yml:153,306,677` and `world/**` scripts are tile-count/paint-history artifacts,
out of scope per `BIOME_PAINT_ONCE_AT_THE_END_1`.

### 8. Mechanics/kit state

No kit spec exists for this biome and no mechanic is shipped or owed by this item: grepped
`src/RimMandrake`, `src/RimUtinni`, `src/RimStarWars` for "tunneler", "one-move",
"landform catalyst", "catalytic sheet" — **zero hits** outside the sheet/roster/def's own
prose. The roster's `new_defs` (the one-move animal, the tunnelers, icy insects, landform
catalysts) are **all unbuilt**, filed nowhere as their own item yet, and this item's Phase A
move must not wait on them — the sheet's `## Owed` list already scopes them out as separate
authoring work.

### 9. Dependencies & items building into this mod

| item | `rimflow show` | relation |
|---|---|---|
| `BIOME_MOD_SPLIT_EXECUTION_1` | doing, BLOCKED on 10 owner Qs (row 5 is not one of them) | parent — governs the whole wave, not a step 1-4 blocker for this row |
| `ECOSYSTEM_PYRAMID_LAW_1` | proposed | names `RUT_NightsideIce`'s 16.7%→68.8% pyramid math as a worked example; lands later, doesn't block |
| `ROSTER_DEAD_BMT_NAMES_SWEEP_1` | proposed, but body says "✅ DONE 2026-09-23 — zero `BMT_` rows remain in any roster" | already resolved for this biome (`RSW_CaveLemming` wired, was the last one) |
| `HELIX_TELLUROX_BUILD_1` | doing, BLOCKED | names `HorrorWastes` (a different nightside biome) and lists `RUT_NightsideIce` only as a sibling entrance-biome example — no relation to this build |
| `BIOME_SPECIFIC_FAUNA_LAW_1` | proposed | 52-species multi-home audit; evictions are STOPPED (owner ruling) — nothing actionable against this roster now |
| `BIOME_WORLD_SWITCH_WAVE_1` | doing | the tile-repaint wave (Phase B), not this item's scope |

### 10. Blockers

**None for steps 1-4.** Step 5 (prove it loads) is Desktop-only, not a blocker of starting
tomorrow morning. The Lantern Deeps allowlist gap (§7) is real but belongs to
`LANTERNDEEPS_RM_MOD_BUILD_1`, not this item, and is inert either way while `RM_NightsideIce`
carries 0 tiles.

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/NightsideIce/About/About.xml`, packageId
   `mandrake.rm.nightsideice`. `loadAfter`: **none of §2d's shared libraries are referenced**
   (no modExtension, no comp on this def) — loadAfter only the RimWorld base + expansions
   used (`Ludeon.RimWorld.Odyssey`, `Ludeon.RimWorld.Anomaly` for the gated weather keys).
   `RM_NightsideIceSettings : ModSettings` with a **Master toggle only** (no per-mechanic
   section — no kit exists). Empty `Defs/BiomeDefs/`. `deploy_custom_mods.py --mod
   NightsideIce` dry run, then `--apply`.
2. **Copy content**: `git mv` `RUT_NightsideIce.xml` content into
   `src/RimMandrake/NightsideIce/Defs/BiomeDefs/RM_NightsideIce.xml`, defName
   `RM_NightsideIce`, drop the `RSW_CaveLemming` row (moves to the patch below), keep all
   7 `AA_*` rows in place. Create
   `src/RimUtinni/UtinniPatches/Patches/WildAnimals_NightsideIce.xml`: one
   `PatchOperationAdd` of `RSW_CaveLemming` (0.03) onto
   `/Defs/BiomeDef[defName="RM_NightsideIce"]/wildAnimals`,
   `MayRequire="mandrake.rsw.swbestiary"`, shape from `WildAnimals_Pyrelands.xml`.
   `workerClass` stays `BiomeWorker_IceSheet` (vanilla Core) — no `RM_BiomeWorker_<X>` needed.
3. **Freeze** `RUT_NightsideIce.xml`: byte-for-byte, one new header line — *"carrying the
   world until the terminal paint; content lives in `mandrake.rm.nightsideice`; do not edit
   here."*
4. **Retarget now**: the 10 doc/tooling refs in §7(a). **Second op now**: add a twin
   `PatchOperationConditional` block to `AncientDangerGenSteps_AmbientDoctrine.xml` targeting
   `RM_NightsideIce` beside the existing `RUT_NightsideIce` block. **Flag, don't fix**: file
   a one-line note on `LANTERNDEEPS_RM_MOD_BUILD_1` that its allowlist (`LanternDeepsMod.cs:59`,
   `validation.py:83`) needs `RM_NightsideIce` added alongside `RUT_NightsideIce`.
5. **Prove it loads**: minimal list + `NightsideIce` + `mandrake.rut.patches` + all five
   expansions; quicktest map with landing tile set to `RM_NightsideIce`; confirm
   `RSW_CaveLemming` actually lands via post-load def dump, not just a clean
   `validate_patch.py` run.
6. **Commit/push**: one commit, explicit paths, message naming that the readiness doc's
   flora-owed grade was wrong (see correction above). Append `mandrake.rm.nightsideice` /
   `RM_NightsideIce` to `infrastructure/state/facts/biome_paint_list.md` and
   `WORLD_REMAKE_FINAL_STEP_1`'s paint list.

### False statements found elsewhere

- `Transient/biome_design_readiness_2026-09-23.md:44,91` — grades NightsideIce
  DESIGN-PASS-OWED on "flora roster empty". Wrong: §6 of `nightside_ice.md` (lines 252, 267)
  bans all photosynthetic flora categorically, and the roster's own `flora_purged` entry
  (`rosters/nightside_ice.json:148-152`) records the empty list as the ruling, not a gap.
  This biome is flora-complete; nothing is owed there. (BENCH to correct the doc.)
- `src/RimMandrake/FlowWorks/Defs/ManyWaters/ThingDefs/RM_ColoredWaterBottles.xml:41` cites
  `src/RimStarWars/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml` — wrong path/tier; the
  real file is `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml`. Low-stakes
  (a citation in an explanatory comment, not a live reference), but wrong.
- `infrastructure/state/facts/biome_paint_list.md:35` states the def is "173 lines" — MEASURED
  now at **185 lines** (`wc -l`), stale since the 2026-09-21 `RSW_CaveLemming` addition.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.nightsideice`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_NightsideIce` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_NightsideIce`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.nightsideice`; do not edit here."* From that moment
   every content fix lands in `RM_NightsideIce` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_NightsideIce` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_NightsideIce` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.nightsideice` exists, deploys, and loads clean carrying `RM_NightsideIce` with its own content and its own
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
