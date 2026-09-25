# FEVERWOOD_RM_MOD_BUILD_1 — build RM_FeverWood as its own RimMandrake mod

**the Fever Wood**

Phase A row 22 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

**Row 22, standalone (not a twin, not a kit-pair).** No `RM_FeverWood` anything exists yet
— `src/RimMandrake/FeverWood/` is absent from `src/RimMandrake/` (35 folders listed,
FeverWood not among them). This is a from-scratch build, not a merge.

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/FeverWood/` folder, no `mandrake.rm.feverwood` About.xml anywhere in `src/` |
| 2 copy content | ⛔ OWED — `RM_FeverWood` BiomeDef does not exist; only the painted `RUT_FeverWood` (232 lines) |
| 3 freeze twin | ⛔ OWED — `RUT_FeverWood.xml`'s header (lines 1–40) is provenance/mechanics prose only, no "carrying the world until the terminal paint" freeze comment |
| 4 retarget | ⛔ OWED — nothing retargeted yet (nothing to retarget *to* until step 1 exists); candidate list below |
| 5 prove it loads | ⛔ Desktop-only, blocked on steps 1–2 |
| 6 commit/push | ⛔ OWED — nothing built yet |
| paint-list append | ✅ DONE — row present, `infrastructure/state/facts/biome_paint_list.md:30` |

### The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml`, 232 lines.
`workerClass` = `ReGrowthCore.UniversalBiomeWorker` — **donor type**, owed
`RM_BiomeWorker_FeverWood`. `modExtensions`: 3 `<li>`, all already RM_-tier
(`MayRequire="mandrake.rm.environmentalhazards"`): `RM_LivingBoleBiomeExtension`,
`RM_MirrorPoolBiomeExtension`, `RM_RootCausewayBiomeExtension` — none need porting,
only re-pointing at `RM_FeverWood`. `terrainsByFertility`: `Soil` (−999..0.9),
`SoilRich` (0.9..999) — both vanilla, by name. `diseases` (7, all vanilla names):
`Disease_Flu` 70, `Disease_Plague` 50, `Disease_Malaria` 140, `Disease_GutWorms` 75,
`Disease_MuscleParasites` 50, `Disease_AnimalFlu` 70, `Disease_AnimalPlague` 100.
`baseWeatherCommonalities` (vanilla weather names only): `Clear` 30, `Fog` 10, `Rain` 0,
`DryThunderstorm` 1, `RainyThunderstorm` 0, `FoggyRain` 0, `SnowGentle` 0, `SnowHard` 0,
`Overcast` (MayRequire Odyssey) 2.

### wildAnimals split — MEASURED via `xml.etree.ElementTree`, 11 rows (shorthand `<DefName>commonality</DefName>` form, not `<li>`)

| defName | commonality | MayRequire | verdict |
|---|---:|---|---|
| `RSW_GlowSlug` | 0.5 | `mandrake.rsw.swbestiary` | → Utinni patch (our own SW tier) |
| `Urusai` | 0.5 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon, Q11) |
| `VFEI2_Megathrips` | 0.5 | `oskarpotocki.vfe.insectoid2` | **stays in `RM_` def** — non-SW donor, Q9 |
| `Gelagrub` | 0.4 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon) |
| `Nuna` | 0.4 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon) |
| `Convor` | 0.3 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon) |
| `LongtailGorg` | 0.3 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon) |
| `Whisperbird` | 0.3 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon) |
| `RSW_JewelBeetle` | 0.2 | `mandrake.rsw.swbestiary` | → Utinni patch |
| `RSW_AcidSlug` | 0.05 | `mandrake.rsw.swbestiary` | → Utinni patch |
| `Fambaa` | 0.02 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon) |

**10 of 11 rows go to Utinni; 1 stays** (`VFEI2_Megathrips`). `WildAnimals_FeverWood.xml`
does **not exist** — only `WildAnimals_CrackedLands.xml`, `WildAnimals_Greentide.xml`,
`WildAnimals_Pyrelands.xml` do (`ls src/RimUtinni/UtinniPatches/Patches/`). `RSW_GlowSlug`/
`RSW_JewelBeetle`/`RSW_AcidSlug` were renamed from dead `BMT_` names by
`MIASMA_FEVERWOOD_GREENTIDE_BMT_1` (BENCH, 2026-09-21) — that half is already live in
this def, confirmed by this parse.

### wildPlants split — MEASURED, 7 rows

| defName | commonality | MayRequire | verdict |
|---|---:|---|---|
| `Plant_HydenockTree_Wild` | 1.5 | `mlie.starwarsanimalcollection` | → Utinni patch (hydenock is Q11a's own canon example) |
| `AB_KeeningCordax` | 1.2 | `sarg.alphabiomes` | **stays in `RM_` def** — non-SW donor |
| `RUT_GiantLeaf` | 0.8 | none | **our own invented content, currently `RUT_`-prefixed** — rename to `RM_`-tier per Q11a (not SW canon) and move the def (see below) |
| `Plant_JoganTree_Wild` | 0.6 | `mlie.starwarsanimalcollection` | → Utinni patch (jogan is Q11a's own canon example) |
| `AB_Iashiphus` | 0.5 | `sarg.alphabiomes` | **stays in `RM_` def** |
| `AB_Gomphoeria` | 0.4 | `sarg.alphabiomes` | **stays in `RM_` def** |
| `Plant_Chakroot_Wild` | 0.4 | `mlie.starwarsanimalcollection` | → Utinni patch (chak-root is Q11a's own canon example) |

No owner-rejected rows here (no vanilla-Earth filler present — all 7 are alien/donor
names; nothing to flag as an invented rejection).

### Roster vs def diff

Roster (`rosters/the_fever_wood.json`): 12 `fauna` rows, 7 `flora` rows.
- **Flora: fully wired.** All 7 roster flora rows match the def's 7 `wildPlants` rows
  1:1 (same defNames). 0 unwired either direction.
- **Fauna: 1 roster row unwired.** All 11 def `wildAnimals` rows appear in the roster's
  12 `fauna` rows; the extra roster row, **`AA_SmallButterfly`** (commonality 0.5, `sarg.alphaanimals`
  donor per its `AA_` prefix), is **not** in the def's `wildAnimals` at all — its own roster
  note says "PLACED: the_greentide + the_fever_wood" but it was never added to this XML.
- Ownership: `RSW_GlowSlug`/`RSW_JewelBeetle`/`RSW_AcidSlug` are ours (RimStarWars tier,
  `src/RimStarWars/SWBestiary/`); every other fauna row (`Urusai`, `VFEI2_Megathrips`,
  `Gelagrub`, `Nuna`, `Convor`, `LongtailGorg`, `Whisperbird`, `Fambaa`, `AA_SmallButterfly`)
  is a donor name, no port exists (`DONOR_DEFS_PORT_TO_OURS_1`, long-term, out of scope here).
  Flora: `AB_KeeningCordax`/`AB_Iashiphus`/`AB_Gomphoeria` are `sarg.alphabiomes` donor names,
  `Plant_HydenockTree_Wild`/`Plant_JoganTree_Wild`/`Plant_Chakroot_Wild` are `mlie` donor
  names; `RUT_GiantLeaf` is ours (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_CavernsFlora.xml`),
  art present and MEASURED (`texPath Things/Plant/GiantLeaf` →
  `src/RimUtinni/UtinniPatches/Textures/Things/Plant/GiantLeaf/GiantLeaf_a.png` exists on disk).
  UNMEASURED: art presence for the donor-named rows (their textures live in their own donor
  mods, not checked here).

### Content to move into the mod

Every file under `src/RimUtinni/**` naming Fever Wood content (via `grep -rl "RUT_FeverWood"`,
each hit read):

- `Defs/IncidentDefs/RUT_FeverWood_MirrorBreak.xml` (F2) — biome-generic mechanic, moves
- `Defs/MapGeneration/RUT_FeverWood_ScatterPoolsGenStep.xml` (F1) + its
  `Patches/RUT_FeverWood_ScatterPoolsGenStep_Register.xml` — moves; the Register patch needs
  a **second op** for `RM_FeverWood` (step 4) since it targets the BiomeDef by name
- `Defs/TerrainDefs/RUT_Boughway.xml` (F6), `RUT_FeverWoodMirrorPool.xml` (F1),
  `RUT_StiltPlatform.xml` (F5) — move
- `Defs/TerrainDefs/RUT_RootCauseway.xml` — **UNCERTAIN**: the kit spec's own header says
  it's "reused verbatim from the sibling kit" (Greentide) — check whether `RUT_Greentide`'s
  own causeway also targets this exact def before moving it; if shared across two biome mods
  it cannot simply move into one
- `Defs/ThingDefs_Buildings/RUT_FeverTrunkCore.xml`, `RUT_FeverTrunkHeartwood.xml` (F7) +
  their texture `Textures/Things/Building/RUT_FeverTrunkHeartwood/RUT_FeverTrunkHeartwood.png` — move
- `Defs/ThingDefs_Items/RUT_FeverWood_MirrorList.xml` (F3) — move
- `Defs/ThingDefs_Plants/RUT_CavernsFlora.xml` — **only the `RUT_GiantLeaf` row** moves
  (rename `RM_GiantLeaf`); the rest of that file serves other biomes (Lantern Deeps cave
  flora roster names 13 species from this pack) and stays
- **C#, all 8 F1–F9 spike classes** currently live in
  `src/RimMandrake/EnvironmentalHazards/Source/` under namespace `RimMandrake.EnvironmentalHazards`,
  assembly `mandrake.rm.environmentalhazards` (csproj `EnableDefaultCompileItems=false`,
  each file individually `<Compile Include>`d — confirmed present for all 8):
  `RUT_MapComponent_TheTenant.cs`, `RUT_IncidentWorker_MirrorBreak.cs`,
  `RM_CompUseEffect_RevealHazards.cs`, `RUT_TenantEmergenceSpawner.cs`,
  `RM_CompGatherableCalmGated.cs`, `RUT_HaulPawnAndExit.cs`, plus `RM_LurkingWaterExtension.cs`/
  `RM_TenantTruceExtension.cs`. The kit spec's own text says packaging (RM_ shared-lib home vs
  Fever Wood mod) is **FOUNDRY's call, not yet made** — this ticket is that call. The `RM_`-named
  classes (generic, content-blind) fit the §2d shared-library posture and can stay; the
  `RUT_`-named ones are Fever-Wood-specific and are candidates to move with the content.
- **Stays in Utinni, correctly:** `Patches/BiomeDescriptions_Ashkarr.xml:199-206` — its
  Operation targets the **donor** def `COMIGO_GreaterSwamp_Tropical`, not `RUT_FeverWood`;
  the `RUT_FeverWood` on line 206 is a trailing comment. `RM_FeverWood` will carry the same
  description natively (already native in `RUT_FeverWood.xml:46`) — nothing to patch.
  `Patches/BiomeFlora_Ashkarr.xml:37` — `RUT_FeverWood` is named inside that file's own
  "biomes this file deliberately does NOT patch" list (7 plants, authored in its own def) —
  correct, leave.

### `RUT_FeverWood` references across the repo

`grep -rl "RUT_FeverWood"` (excluding `Transient/`), each hit read:

- **Retarget-outright now** (target doesn't need to be on the world):
  `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md:46,119`,
  `design/Jawa/worldbuilding/biome_flora_rosters.md:156`,
  `design/Jawa/mods/biome_flora.py:166` (flora-generation source table).
- **Leave — Phase B / painting tooling, untouched until the terminal paint:**
  `design/Jawa/fauna/biome_name_migration.py:37` (donor→`RUT_FeverWood` map),
  `world/biome_world_switch_apply.py`, `infrastructure/state/facts/biome_paint_list.md:30`.
- **Leave — comment/prose only**, confirmed by reading each: `RM_CompUseEffect_RevealHazards.cs:25`,
  `RM_GenStep_ScatterPools.cs:8`, `RM_MirrorPoolBiomeExtension.cs:8,28,32,36` (all header/field-doc
  comments, no string literal used at runtime), `RSW_ScrapNestBird.xml:24` (comment, `wildBiomes`
  donor metadata a BiomeDef never reads), `BiomeDescriptions_Ashkarr.xml`, `BiomeFlora_Ashkarr.xml`
  (both above), plus every item file's own prose (`FEVER_WOOD_MECHANICS_1`,
  `MIASMA_FEVERWOOD_GREENTIDE_BMT_1`, `FORGE_MECHANICS_1`, `SCALD_MECHANICS_1`,
  `SW_FAUNA_NEVER_IN_RM_TIER_1`, `ECOSYSTEM_PYRAMID_LAW_1`, `DUPLICATE_CANON_DEFNAME_PAIRS_1`,
  `BIOME_WORLD_SWITCH_WAVE_1`, closed items) — same shape as the Greentide exemplar, do not
  retarget a comment or another item's prose.
- `design/RimMandrake/biome_mod_architecture.md` — the governing spec itself, correct as-is.
- `gen_cast_patch.py` (`design/Jawa/fauna/gen_cast_patch.py`) — **zero occurrences of
  "FeverWood"**, MEASURED — nothing owed there, same finding as the Greentide exemplar.

### Mechanics/kit state — `FEVER_WOOD_MECHANICS_1` (doing)

6 of 9 mechanics have a real, compiling spike/build, all inside `mandrake.rm.environmentalhazards`
(not yet in any Fever Wood mod):
- **F1 Tenant** (aquifer entity) — ships: `RUT_MapComponent_TheTenant` + terrain wired
  (`RUT_FeverWoodMirrorPool.xml` carries `RM_LurkingWaterExtension`).
- **F2 evidence/mirror-break** — ships (thin): `RUT_IncidentWorker_MirrorBreak`; **silence-cue
  reuse not wired** (`RM_MapComponent_SilenceCue` has no public trigger entry point yet — owed).
- **F3 mirror list intel** — ships (minimal): `RM_CompUseEffect_RevealHazards`; trader-kind XML
  and the overlay draw call are **not done**.
- **F4 deep thing** — gate/seam only: `RUT_TenantEmergenceSpawner` exists, referenced by
  nothing (ban §6.1 holds by construction); `RUT_TenantEmergedMass`, `RUT_TenantTentacle`,
  and all art are **NOT built** — confirmed absent by `grep -rl` across `src/`.
- **F5 ground refusal/stilts** — ships: `RUT_StiltPlatform.xml`, no C# needed.
- **F6 boughway network** — ships (static): `RUT_Boughway.xml` + `RM_GenStep_RootCauseways`
  multi-pass (unblocked 2026-09-14 by `GREENTIDE_MECHANICS_2`'s M9/M12 landing — the C# classes
  now exist and compile, confirmed present in `src/`).
- **F7 bore-caves/Fever Trunk** — ships: `RUT_FeverTrunkHeartwood`/`RUT_FeverTrunkCore` on the
  Greatbole (`RM_LivingBoleBiomeExtension`) class, no new C#.
- **F8 thornbugs** — comp only: `RM_CompGatherableCalmGated` compiles and is wired to the real
  engine gate (`Active`, not `Gathered()`); **content NOT built** — no `RUT_Thornbug`
  PawnKindDef, no `RUT_ThornbugNectar` ThingDef exist anywhere in `src/` (confirmed by `grep -rl`).
- **F9 two-front war** — driver only: `RUT_HaulPawnAndExit` JobDriver compiles; **NOT built**:
  `RUT_AntSwarm`/`RUT_FeraliskBrood` FactionDefs, LordJob/LordToil wiring, the victim-finder,
  the raid-back QuestScriptDef — confirmed absent by `grep -rl`.

⇒ **What moves now**: the 6 spiked/shipped mechanics' XML + their compiling C#, repackaged per
the "content to move" section above. 🔑 **Wave-1 scope RULED — decision taken by question card,
2026-09-24 (BENCH sitting):** wave 1 is the split **plus F8's content defs plus F9's war wiring**
— thornbug creature + nectar, the two raider species (`RM_Kurreth` ant-swarm, `RM_Skreth` brood
predator — names proposed, not yet ratified), factions, lord wiring, raid-back quest. Only
**F4's dormant creature content stays unbuilt by design**. Cast source:
`design/Jawa/worldbuilding/biomes/fever_wood_rm_cast_proposal_2026-09-24.md` (pending owner
ratification of names/rosters). `FEVERWOOD_ANT_HIVE_DUNGEON_1`
(proposed) additionally reserves the ants' hive-as-dungeon behaviour for a later pass reusing
`RM_CompPlantAlarm`'s propagation pattern — also not a blocker here.

### Dependencies & items building into this mod

| item | `rimflow show` | blocks step 2? |
|---|---|---|
| `FEVER_WOOD_MECHANICS_1` (doing) | C# kit, 6/9 mechanics spiked, lands in this mod per the packaging call above | No — lands alongside/after, per "content to move" |
| `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` (proposed, but its FeverWood body confirms DONE) | roster `BMT_`→`RSW_` renames already live in `RUT_FeverWood.xml` (confirmed by this pass's own parse) | No |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` (proposed) | names `RUT_FeverWood` at 7/11 SW rows to route to Utinni | No — this ticket's step 2 already does that split |
| `FEVERWOOD_ANT_HIVE_DUNGEON_1` (proposed) | ant hives as reactive dungeons, reuses `RM_CompPlantAlarm` pattern, ordered after the wasp swarm build | No — later mechanics wave |
| `ECOSYSTEM_PYRAMID_LAW_1` (proposed, needs deploy) | FeverWood passing at 80.7% small/large ratio | No — informational |
| `BIOME_WORLD_SWITCH_WAVE_1` (doing, needs bridge) | Phase B tile-switch wave, names `RUT_FeverWood` among 23 biomes owed the paint | No — Phase B only |
| `DUPLICATE_CANON_DEFNAME_PAIRS_1` (proposed) | `Nuna` occupies FeverWood + 4 other biomes under two defNames | No — multi-home review, not a build blocker |

### Blockers

**None for steps 1–4.** Step 5 (prove it loads) is Desktop-only, as always. The one
UNCERTAIN item (`RUT_RootCauseway.xml` possibly shared with Greentide) needs a one-file
check before step 2's move, not before scaffolding starts.

### Concrete step plan

1. **Scaffold** `src/RimMandrake/FeverWood/About/About.xml`, packageId `mandrake.rm.feverwood`,
   `loadAfter`: `mandrake.rm.environmentalhazards` (hard dep — 3 modExtensions),
   `mandrake.rm.creaturebehaviors` (transitive, silence-cue reuse). `RM_FeverWoodSettings :
   ModSettings` with a master toggle + one toggle per F1/F2/F3/F5/F6/F7/F8/F9 mechanic present
   (F4 excluded — dormant, no toggle needed per §6c). Empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod FeverWood` dry run, then `--apply`.
2. **Copy content**: `RM_FeverWood` BiomeDef (defName renamed, `workerClass` →
   `RimMandrake.FeverWood.RM_BiomeWorker_FeverWood` new class replacing donor
   `ReGrowthCore.UniversalBiomeWorker`), terrain/disease/weather tables unchanged, the 3
   `modExtensions` re-pointed at `RM_FeverWood` (classes unchanged, already RM_-tier), 1
   `wildAnimals` row (`VFEI2_Megathrips`) kept inline, 3 `wildPlants` rows kept inline
   (`AB_KeeningCordax`, `AB_Iashiphus`, `AB_Gomphoeria`), `RUT_GiantLeaf` renamed
   `RM_GiantLeaf` and moved from `RUT_CavernsFlora.xml` into this mod with its texture.
   Write `src/RimUtinni/UtinniPatches/Patches/WildAnimals_FeverWood.xml` (new file, shape of
   `WildAnimals_Pyrelands.xml`) carrying the 10 routed rows (`RSW_GlowSlug`, `Urusai`,
   `Gelagrub`, `Nuna`, `Convor`, `LongtailGorg`, `Whisperbird`, `RSW_JewelBeetle`,
   `RSW_AcidSlug`, `Fambaa`) plus a second write for the 3 SW plant rows
   (`Plant_HydenockTree_Wild`, `Plant_JoganTree_Wild`, `Plant_Chakroot_Wild`) as
   `PatchOperationAdd` onto `RM_FeverWood`'s `wildPlants`. Move the 6-mechanic content list
   from "Content to move" above; verify `RUT_RootCauseway.xml` sharing before moving it.
3. **Freeze** `RUT_FeverWood.xml` byte-for-byte, add the standard one-line header comment.
4. **Retarget now**: `_def_bindings_2026-09-09.md`, `biome_flora_rosters.md`, `biome_flora.py`.
   Second-op: `RUT_FeverWood_ScatterPoolsGenStep_Register.xml` gets a twin targeting
   `RM_FeverWood` alongside its existing `RUT_FeverWood` op.
5. **Prove it loads**: minimal list + `FeverWood` + `mandrake.rut.patches` +
   `mandrake.rm.environmentalhazards` + `mandrake.rm.creaturebehaviors` + all five expansions.
6. **Commit and push**, message naming that the donor `workerClass` and the inline SW fauna
   are what the twin got wrong.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.feverwood`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_FeverWood` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_FeverWood`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.feverwood`; do not edit here."* From that moment
   every content fix lands in `RM_FeverWood` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_FeverWood` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_FeverWood` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.feverwood` exists, deploys, and loads clean carrying `RM_FeverWood` with its own content and its own
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
