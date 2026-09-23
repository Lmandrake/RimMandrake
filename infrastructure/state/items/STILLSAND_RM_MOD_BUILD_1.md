# STILLSAND_RM_MOD_BUILD_1 — build RM_Stillsand as its own RimMandrake mod

**the Stillsand (extreme desert; campaign label "the Dune Sea" stays a Utinni patch)**

Phase A row 1 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

Not a twin (§4 doesn't apply — row 1 is "PROPOSED — owner-named standalone", no existing
`RM_Stillsand` folder). `src/RimMandrake/Stillsand` does not exist (checked, `ls` → no such
path). This is a from-scratch Phase A build, nothing pre-done.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/Stillsand`, no `mandrake.rm.stillsand` anywhere |
| 2 copy content | ⛔ OWED — nothing copied |
| 3 freeze RUT def | ⛔ OWED — `RUT_ExtremeDesert.xml` header (lines 4–57) is authoring provenance only, no freeze notice |
| 4 retarget | ⛔ OWED — nothing to retarget onto yet (mod doesn't exist) |
| 5 prove it loads | ⛔ OWED, Desktop-only anyway |
| 6 commit/push | ⛔ OWED |
| paint-list append | ⛔ OWED — `infrastructure/state/facts/biome_paint_list.md:29` lists `RUT_ExtremeDesert` owned by `mandrake.rut.patches`, no `RM_Stillsand` row yet |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ExtremeDesert.xml`, **214 lines** (`wc -l`).
`workerClass` = `RimWorld.BiomeWorker_ExtremeDesert` — namespace `RimWorld.`, i.e. **vanilla
Core**, not one of step 2's donor namespaces (`AlphaBiomes.*`/`VanillaBiomes.*`/
`BiomesPlus.*`/`ReGrowthCore.*`) → **no `RM_BiomeWorker_<X>` owed**, can be reused as-is.
`modExtensions`: **none** (parsed, `ET.find` returns `None`). `gameConditions`: **none**.
Terrain: `terrainsByFertility` one row, `Sand` (-999..999); `lakeBeachTerrain`/`mudTerrain`/
`riverbankTerrain` all `Sand`. Weather (`baseWeatherCommonalities`): `Clear` 95,
`DryThunderstorm` 1, `Fog`/`Rain`/`RainyThunderstorm`/`FoggyRain`/`SnowGentle`/`SnowHard` 0,
`Sandstorm` (Odyssey) 4. Diseases: 9 entries (`Disease_Flu` 100, `Disease_Plague` 80,
`Disease_GutWorms` 40, `Disease_MuscleParasites` 40, `Disease_FibrousMechanites` 30,
`Disease_SensoryMechanites` 30, `Disease_AnimalFlu` 100, `Disease_AnimalPlague` 80,
`Disease_OrganDecay` 10). `allowRoads` false (named ban, dune_sea.md SS6), `allowRivers`
false, `allowFarmingCamps` false. `allowedPackAnimals`: 5 `RSW_` entries (Bantha/Ronto/Eopie/
Jamel/Falumpaset), all `MayRequire="mandrake.rsw.swbestiary"` — Star Wars, → Utinni patch.
No bespoke kit spec exists for this biome (`design/Jawa/worldbuilding/biomes/kits/` has no
`dune_sea`/`deep_desert` file, unlike the Rot/Scald/etc.) — this build is BiomeDef + flora +
fauna only, no separate mechanics kit mod to absorb.

### 3. wildAnimals split — 14 rows (`len(list(wa))`, parsed)

| defName | commonality | prefix | verdict |
|---|---:|---|---|
| RSW_Spineroller | 0.3 | RSW_ | → Utinni patch (Star Wars) |
| RSW_Kreetle | 0.2 | RSW_ | → Utinni patch |
| RSW_WarWyrm | 0.2 | RSW_ | → Utinni patch |
| RSW_KraytDragon | 0.15 | RSW_ | → Utinni patch |
| RSW_Stareling | 0.15 | RSW_ | → Utinni patch |
| RSW_GraniteSlug | 0.1 | RSW_ | → Utinni patch |
| RSW_Scurrier | 0.1 | RSW_ | → Utinni patch |
| RSW_Gizka | 0.01 | RSW_ | → Utinni patch |
| RSW_GreaterKraytDragon | 0.001 | RSW_ | → Utinni patch |
| RSW_Voltmaw | 0.0005 | RSW_ | → Utinni patch |
| RSW_TruffleMole | 0.5 | RSW_ | → Utinni patch |
| RSW_SandLion | 0.5 | RSW_ | → Utinni patch |
| RSW_Drazzik | 0.05 | RSW_ | → Utinni patch (see ⚠️ below — name may be wrong tier) |
| JOE_Cephalope | 0.5 | JOE_ | **stays in `RM_Stillsand`** — donor non-Star-Wars, Q9 acceptable inline |

**13 of 14 rows go to Utinni**; 1 (`JOE_Cephalope`) stays. `WildAnimals_Stillsand.xml`
**does not exist yet** (checked, no file under `UtinniPatches/Patches/`).

⚠️ **`JOE_Cephalope`'s own ThingDef is NOT in a RimMandrake mod today** — it was absorbed
into `src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
(Utinni-tier), per the def's own `AA_JOE_DESERT_PORT_BATCH_1` comment. An `RM_Stillsand`
`wildAnimals` row referencing it inline would make a RimMandrake mod depend on Utinni
content — backwards per §1. **Flagging, not deciding**: either the absorbed def moves to a
RimMandrake-tier file (§2d shared library or into `RM_Stillsand` itself) before step 2, or
this row also routes through a patch. UNCERTAIN which BENCH prefers.

⚠️ **`RSW_Drazzik`** (drum-lure predator, `RM_CompDrumLure`/`RM_CompProperties_DrumLure` C#
already live in `src/RimMandrake/CreatureBehaviors/Source/`, §2d shared library) is an
**invented** biome-signature predator, not canon Star Wars — its ThingDef
(`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Drazzik.xml`) sits in the `RSW_` tier
today. Per §7 Q11a (invented ≠ IP), this may belong RimMandrake-side instead of behind a
Utinni patch. Not decided here.

### 4. wildPlants split — 3 rows (`len(list(wp))`, parsed) — exact roster match

| defName | commonality | prefix | verdict |
|---|---:|---|---|
| RSW_Plant_Bloddle | 0.05 | RSW_ | → Utinni patch — genuine SW canon (Tatooine bloddle, SWAC donor) |
| RSW_LightPipeNub | 0.1 | RSW_ | ⚠️ see below |
| RSW_Ollim | 0.01 | RSW_ | ⚠️ see below |

🔴 **Same Q11a issue as Drazzik, sharper here.** `RSW_LightPipeNub` and `RSW_Ollim` are
`EXTREME_DESERT_SIGNATURE_FLORA_1`'s own invented signature flora — *"the biome's own
named signature flora"* per the def's header comment, final names picked by owner ruling on
that same item, not Star Wars canon. They are authored in
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_ExtremeDesertSignatureFlora.xml` under the
`RSW_` prefix and `mandrake.rsw.swbestiary` mod, which per §7 Q11a should never have housed
them — invented content is RimMandrake-tier by the ruling, prefix notwithstanding. **These
two are strong candidates to author directly into `RM_Stillsand`'s own `wildPlants`
(renamed off `RSW_`) rather than routed through a Utinni patch onto Star Wars content that
isn't Star Wars.** Flagging for BENCH/owner naming, not deciding or renaming here.

No owner-rejected rows found in this def's `wildPlants` (`AB_GiantStikehr` was already
removed 2026-09-20, cited in the def's own comment — not restated as new).

### 5. Roster vs def diff

Roster JSON (`dune_sea_deep_desert.json`, authored 2026-09-09, **pre-port**: fauna rows use
donor/pre-rename names — `GraniteSlug`, `AA_Needleroll`, `AA_Eyeling`, `Kreetle`, `Gizka`,
`Scurrier`, `KraytDragon`, `GreaterKraytDragon`, `WarWyrm`, `AA_BoulderMit`, `AA_TetraSlug`,
`AA_Dunealisk`, `AA_SpinedGow`, `AA_SandLion`, `RSW_TruffleMole`, `JOE_Cephalope`.
`DESERT_FAMILY_PORT_EXECUTION_1` (state: **proposed**, defs 96/109 done per its own doc)
replaced these with `RSW_` names — the def today carries the **post-port** names.

| roster row (pre-port name) | maps to (in def today) | status |
|---|---|---|
| GraniteSlug | RSW_GraniteSlug | ✅ wired (commonality matches) |
| AA_Needleroll | RSW_Spineroller | ✅ wired ("needleroll" in def comment) |
| AA_Eyeling | RSW_Stareling (?) | ⚠️ UNCERTAIN — commonality (0.15) + grain-scale band match, "ikee" comment plausible, but the rename is **not confirmed** against a `<!-- donor -> RSW_X -->` source comment (didn't locate one in time) |
| Kreetle | RSW_Kreetle | ✅ wired |
| Gizka | RSW_Gizka | ✅ wired |
| Scurrier | RSW_Scurrier | ✅ wired |
| KraytDragon | RSW_KraytDragon | ✅ wired |
| GreaterKraytDragon | RSW_GreaterKraytDragon | ✅ wired |
| WarWyrm | RSW_WarWyrm | ✅ wired |
| AA_TetraSlug | RSW_Voltmaw | ✅ wired ("tetra slug" comment) |
| AA_SandLion | RSW_SandLion | ✅ wired ("vekka" comment) |
| RSW_TruffleMole | RSW_TruffleMole | ✅ wired |
| JOE_Cephalope | JOE_Cephalope | ✅ wired (see Utinni-tier flag above) |
| AA_BoulderMit | RSW_Stoneback | ⛔ **evicted, cited**: `STONEBACK_DEFNAME_COLLISION_1`/`BIOME_SPECIFIC_FAUNA_LAW_1` — bokka given one home (the Long Shade); not a gap |
| AA_Dunealisk | — | ⛔ **evicted, cited**: def's own `WYYYSCHOKK_FERALISK_MERGE_1` comment — Alpha Animals '-lisk' clade retired by Cherry Picker cut |
| **AA_SpinedGow** | — | 🔴 **UNWIRED** — roster names it for this biome ("extreme desert", 0.15, plated-grazer) but the live def carries it only on `RUT_Scarlands.xml:167` (0.15, unrelated placement), never here |

**1 roster fauna row confirmed unwired** (`AA_SpinedGow`). Flora: **0 unwired**, exact
match (§4 table above). Def rows not in roster: `RSW_Drazzik` (built 2026-09-20 by
`DRUM_LURE_PREDATOR_BUILD_1`, after the roster's authoring date — not a gap, newer content).
Art existence for individual roster/def rows: **UNMEASURED** — not checked file-by-file in
the time available (see UNCERTAIN in the return line).

### 6. Content to move into the mod

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ExtremeDesert.xml` → becomes `RM_Stillsand`
  (minus the 13 RSW_ wildAnimals rows), reason: it's the biome's own def, §3a test passes.
- `RSW_LightPipeNub`/`RSW_Ollim` (`src/RimStarWars/SWBestiary/Defs/DesertPort/
  RSW_ExtremeDesertSignatureFlora.xml`) — candidate move per §4 above (flagged, not decided).
- `RM_CompDrumLure`/`RM_CompProperties_DrumLure`/`RM_DrumLure_Hediffs.xml` — **already** in
  `mandrake.rm.creaturebehaviors` (§2d shared library), nothing to move.
- **Stays in Utinni** (Star Wars IP or campaign wiring, §3a "no" branch): every `RSW_`
  wildAnimals row (§3 table), `RSW_Plant_Bloddle` (genuine canon), `BiomeNames_Ashkarr.xml`/
  `BiomeDescriptions_Ashkarr.xml` (campaign label "the Dune Sea"/"the Stillsand" text),
  `Absorbed_Cephaloids_Defs.xml` (unless relocated per the flag above).
- No absorbed `mandrake.rut.*` kit mod exists for this biome (unlike the Rot's
  `rotsporekit`) — nothing else to fold in.
- C#: no bespoke Stillsand C# exists yet; the only mechanic (drum-lure) is already correctly
  filed under the shared `CreatureBehaviors` assembly/namespace `RimMandrake.CreatureBehaviors`,
  csproj `RM_CreatureBehaviors.csproj` (⚠️ lists every `<Compile Include>` explicitly per
  CLAUDE.md — not this item's concern since nothing new is being added there).

### 7. References to `RUT_ExtremeDesert` across the repo

`rg -l "RUT_ExtremeDesert"` inside `src/`, `design/`, `infrastructure/`, `Transient/`
returns ~60 hits. Live-code and design-data hits, read:

- **(a) Retarget outright** (target need not be on the world): `design/Jawa/fauna/
  cast_assignment.csv:155-185` (roster provenance record), `design/Jawa/fauna/
  biome_name_migration.py:39` (name-map dict), `src/RimUtinni/UtinniPatches/
  build_desert_review_sheet.py` (review-sheet generator, several refs) — none of these
  need to stay working on the live world.
- **(b) Needs a SECOND op for `RM_Stillsand`** (must keep working on the live world):
  `src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml:36` (comment inside its "does
  NOT patch" block, naming `RUT_ExtremeDesert` as one of the biomes with its own authored
  flora — **read it, this line is prose not an op**, so it may only need updating text, not
  a second xpath), `Patches/BiomeDescriptions_Ashkarr.xml:230` (an `<Operation>` targeting
  the label/description — this one **is** a real op needing the second-target treatment).
- **(c) Comment/prose — leave**: `RUT_Umbra.xml:77`, `RUT_FuelSnows.xml:90` (both a stray
  cross-reference inside their own no-roads comment, not an op) — do not retarget a comment.
- Everything else in the ~60 hits is `infrastructure/state/items/*` (live+closed items —
  see §9 below for the live ones), `infrastructure/state/handoffs/*`, `infrastructure/
  state/facts/*`, and `Transient/*` — historical/derived, not code to retarget.

### 8. Mechanics/kit state

No kit spec exists for this biome (checked `design/Jawa/worldbuilding/biomes/kits/` —
no `dune_sea`/`deep_desert` file). The one bespoke mechanic tied to this biome,
`RM_CompDrumLure` (`DRUM_LURE_PREDATOR_BUILD_1`), is **already SHIPPED** in the
`mandrake.rm.creaturebehaviors` shared library (§2d) — nothing to wait on, nothing to move.
Unbuilt per the def's own header comment: the sarlacc (its own item, not this one), the
megafauna filter-feeder giant + its shade-commensal micro-fauna (roster `new_defs` rows,
NOT this pass's scope per the def comment), any world repaint. **None of these block
steps 1–4.**

### 9. Dependencies & items building INTO this mod

| item | `rimflow show` state | blocks step 2? |
|---|---|---|
| `DESERT_FAMILY_PORT_EXECUTION_1` | proposed — defs 96/109 done, 12 need owner, art mostly unqueued | no — def today already carries post-port `RSW_` names; only `AA_SpinedGow`'s placement is unresolved (§5) |
| `EXTREME_DESERT_SIGNATURE_FLORA_1` | doing — flora already wired (§4); ⚠️ rimflow warns its file may be stale vs a citing commit | no — content already landed in the def |
| `FALL_LINE_ARRIVAL_MECHANISM_1` | proposed — owns the droids/Rat/Scavrat/WompRat/Mynock/fuelmite disposition, none of which are in this def's `wildAnimals` today | no — those rows are already excluded here |
| `BIOME_SPECIFIC_FAUNA_LAW_1` | proposed — multi-home adjudication, review-sheet-scoped per CLAUDE.md, not a sweep | no — not scoped to force changes here before a Stillsand sitting |
| `DESERT_PORT_PLACEHOLDER_ART_1` | doing — 4 fauna + 1 plant art in this biome still donor-textured | no — art gap, not a load-time blocker |
| `ECOSYSTEM_PYRAMID_LAW_1` | proposed — cites this biome's 77.0% small:large ratio | no — informational |
| `DUPLICATE_CANON_DEFNAME_PAIRS_1` | proposed — gizka/kreetle multi-defName collision, names this biome | no — pre-existing, doesn't block the move |

### 10. Blockers

**None for starting step 1 tomorrow morning.** Two UNCERTAIN items worth a BENCH decision
before step 2 lands wildAnimals (not hard blockers, just avoid doing the wrong thing twice):
(a) where `JOE_Cephalope`'s ThingDef should live before `RM_Stillsand` references it inline;
(b) whether `RSW_LightPipeNub`/`RSW_Ollim`/`RSW_Drazzik` move to RimMandrake tier now (Q11a)
or stay `RSW_`+patched for this pass. Step 5 is Desktop-only, not a blocker of 1–4.

### 11. Concrete step plan

1. **Scaffold**: `src/RimMandrake/Stillsand/About/About.xml`, packageId `mandrake.rm.stillsand`,
   `loadAfter`: `mandrake.rm.creaturebehaviors` (drum-lure comp/hediffs — cited §8), no other
   §2d library is referenced by this def (no EnvironmentalHazards/FlowWorks/WeatherSuite
   content found in it). `RM_StillsandSettings : ModSettings` with a master toggle (§6a);
   since there's no kit, the settings screen is thin (master + cross-biome section only —
   there is no per-mechanic toggle to add unless the Drazzik predator counts as one).
   `Defs/BiomeDefs/` empty dir. `deploy_custom_mods.py --mod Stillsand` dry run, then `--apply`.
2. **Copy content**: `RUT_ExtremeDesert.xml` → `Defs/BiomeDefs/RM_Stillsand_Biome.xml`,
   defName `RM_Stillsand`, minus the 13 `RSW_` wildAnimals rows (§3), keeping `JOE_Cephalope`
   inline pending the §10(a) call. Write `src/RimUtinni/UtinniPatches/Patches/
   WildAnimals_Stillsand.xml` (shape = `WildAnimals_Pyrelands.xml`) as a `PatchOperationAdd`
   of the 13 rows onto `/Defs/BiomeDef[defName="RM_Stillsand"]/wildAnimals`, plus
   `RSW_Plant_Bloddle` onto `wildPlants`, each `MayRequire="mandrake.rsw.swbestiary"`.
   Resolve §10(b) before deciding whether `RSW_LightPipeNub`/`RSW_Ollim` go into the patch
   or straight into the `RM_` def.
3. **Freeze**: add the standard header comment to `RUT_ExtremeDesert.xml` in place, byte-for-
   byte otherwise.
4. **Retarget**: fix `Patches/BiomeFlora_Ashkarr.xml:36`'s prose and add the second op on
   `Patches/BiomeDescriptions_Ashkarr.xml:230` for `RM_Stillsand`; retarget `cast_assignment.csv`
   and `biome_name_migration.py` (offline records, no live-world requirement).
5. **Prove it loads**: minimal list + `Stillsand` + `mandrake.rut.patches` + all five
   expansions, scratch-world landing tile `RM_Stillsand`. Desktop-only.
6. **Commit/push**: one commit, explicit paths, message naming that `RUT_ExtremeDesert`
   was the donor-fauna-inline predecessor; append `mandrake.rm.stillsand` / `RM_Stillsand`
   to `infrastructure/state/facts/biome_paint_list.md`.

### False statements found elsewhere

None found and confirmed in the time available (a candidate — `BiomeFlora_Ashkarr.xml:36`'s
comment will become stale prose once the split lands, but it is not false *today* — leaving
it as a §7(b) retarget item, not a correction here).

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.stillsand`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Stillsand` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Stillsand`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.stillsand`; do not edit here."* From that moment
   every content fix lands in `RM_Stillsand` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Stillsand` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Stillsand` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.stillsand` exists, deploys, and loads clean carrying `RM_Stillsand` with its own content and its own
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
