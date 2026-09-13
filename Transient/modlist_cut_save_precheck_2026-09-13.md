# Modlist-cut save precheck — CANONICAL_ASHKARR_START_2026-09-12.rws

Read-only precheck. Question: does the canonical start save hold placed
content (things/pawns/terrain/world objects/components) referencing defNames
from any of 8 mods proposed for deactivation? A cut of a mod whose defs (or
whose C# component classes) are referenced in the save produces load damage
(`Could not resolve cross-reference` / a null Def field / a GameComponent
whose Class can't be found).

## Instrument note — the named `defs.sqlite` was empty

The task named `/mnt/d/Luke/dev/Rimworld/defs.sqlite` as the attribution
source. That file exists but is **0 bytes** (untracked, `ls -la` confirms,
re-checked 3x) — not usable. The real, current def-attribution DB lives at
the DefDump root, not the repo:

```
/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite
```

`dump_projection.sqlite_path()` in `src/RimMandrake/Utils/dump_projection.py`
confirms this is the ruling location (`DUMP_STORAGE_LAYOUT_RULING_1`: the db
lives at the DefDump root, outside any capture). Its provenance:

```
captured_utc        2026-09-12T22:49:15Z
mod_count           594
game_version        1.6.4871 rev591
modlist_fingerprint d4f85d2a9d785594
defs_total          79522
```

The save itself declares `gameVersion 1.6.4871 rev591` and 594 `<modIds>`
entries — same version, same count as the DB's provenance. Used this DB in
place of the empty repo-root file; the repo-root `defs.sqlite` should
probably be regenerated or removed (out of scope for this precheck — read
only, no writes made).

## Method

Per packageId: pulled all defNames (all def types, TerrainDef held out
separately) from `defs` where `package_id = <pkg>`. Built fixed-string grep
patterns per defName — `<def>NAME</def>` and `Def>NAME<` (the second form
catches `<thingDef>`, `<kindDef>`, `<hediffDef>`, `<raceDef>`, etc. — any
element whose tag ends `...Def>`). Ran one `grep -o -F -f <patterns>` per
package against the save, aggregated counts. Zero-def (code-only) packages
were checked for their C# namespace via `grep -o 'Class="[^"]*"' | sort -u`
against the save, since a GameComponent/MapComponent/WorldComponent can be
scribed by Class with no defName at all. Save was never read into context —
grepped only, per-match spot-checks used `grep -n -B/-A` on exact fixed
strings to distinguish a genuine `<thing>`/`<pawn>`/component reference from
an unrelated `<li>NAME</li>` storage-filter membership line (RimWorld
stockpile/outfit filters enumerate almost every ThingDef the game knows,
allowed or not — a naive substring match on those would over-report). No
grid was decoded.

## Results

### 1. `xmb.ancienturbanruins.mo` — **DIRTY**
- Defs in dump: 911 (735 ThingDef, 14 PawnKindDef, 4 TerrainDef, + 34 other types)
- Save hits: 279 of 907 non-terrain defNames matched, e.g.:
  - `AM_DamagedEmptyShelves` — confirmed placed `<thing Class="...">` on map 0
    at save line 463535, **and** referenced in a blueprint/records list
    (`<thingDef>AM_DamagedEmptyShelves</thingDef>`, line 83498)
  - dozens more (`AM_Wall_Atlas_*`, `AM_Counter_Atlas_*`, `AM_FrontDesk*`, …)
- Class= hits: none needed (defName evidence alone is decisive)
- TerrainDef: 4 defNames (`TERRAIN_UNCHECKED` — compressed grid, not grepped)
- Verdict: **DIRTY**

### 2. `meteores.ancienturbanruinsalldeconstructible.aurad` — **CLEAN**
- Defs in dump: 0 (**ZERO_DEFS** — confirmed: patch-only mod, no `Assemblies/`
  folder on disk at its Workshop path (3361061429); it only reweights the
  `xmb.ancienturbanruins.mo` deconstruct flags via PatchOperation, adds
  nothing of its own)
- Save hits: none possible (no defNames to test)
- Class= hits: none (`meteores`/`aurad` tokens absent from the save's
  `Class="..."` set)
- Verdict: **CLEAN** — nothing in the save can reference this mod; cutting it
  only reverts the deconstructible-flag patch on the parent mod's defs

### 3. `meteores.ancienturbanruinsvanillaloot.aurvl` — **CLEAN**
- Defs in dump: 0 (**ZERO_DEFS** — same shape as #2: no `Assemblies/` at its
  Workshop path 3446989523, patch-only mod depending on
  `xmb.ancienturbanruins.mo` + aurad)
- Save hits: none possible
- Class= hits: none (`meteores`/`aurvl` absent)
- Verdict: **CLEAN**

### 4a. `hailuan.customquestframework` — **DIRTY**
- Defs in dump: 160 (88 ThingDef, 14 PawnModDef, 6 WorldObjectDef, 3 TerrainDef, + others)
- Save hits: 17 of 157 non-terrain defNames, e.g.:
  - `CQF_CryptosleepCasket`, `QE_Cabinet`, `QE_TreasureChest`, `QE_Crate`,
    `QE_Bookshelf`, `QE_Sarcophagus`, `QF_MiracleWall`, `QE_Sign` — all
    present as `<thingDef>NAME</thingDef>` blueprint/record entries
    (spot-checked `QE_Cabinet` at line 70424)
- Class= hits: **`QuestEditor_Library.MapComponent_CQFLord`** — a scribed
  MapComponent from this mod's own C# namespace (also
  `GameComponent_ComplexDuty`, `GameComponent_Editor`,
  `GameComponent_LevelSchedule`, `GameComponent_QuestBook`,
  `MainMapWorldComponent`, `MapComponent_CustomMapData` — all
  `QuestEditor_Library.*`)
- TerrainDef: 3 defNames (`TERRAIN_UNCHECKED`)
- Verdict: **DIRTY** — both defName references and live scribed components

### 4b. `hailuan.customquestframeworkai` — **CLEAN**
- Defs in dump: 8, all UI/registration-only types never scribed
  (PawnColumnDef ×3, ThinkTreeDef ×2, PawnTableDef, MainButtonDef,
  KeyBindingDef)
- Save hits: 0 of 8
- Class= hits: none — every `QuestEditor_Library.*`/`Quest*` class found in
  the save (see #4a) belongs to the base `customquestframework` mod; no
  AI-specific class or "Level AI" token appears
- Verdict: **CLEAN**

### 5a. `kilokio.rimai.framework` — **CLEAN**
- Defs in dump: 0 (**ZERO_DEFS** — genuine framework/API mod; ships
  `RimAI.Framework.dll`, `RimAI.Framework.Contracts.dll`,
  `000_Newtonsoft.Json.dll` but defines no Defs)
- Save hits: none possible
- Class= hits: none — searched the save's full `Class="..."` set for
  `RimAI.Framework`: **zero** hits (only `RimAI.Core.*` classes are scribed,
  see 5b)
- Verdict: **CLEAN** as far as the save goes — cutting it would still break
  `kilokio.rimai.core`'s *function* (a load-order/dependency concern, not a
  save cross-reference concern) since Core depends on Framework's DLL

### 5b. `kilokio.rimai.core` — **DIRTY**
- Defs in dump: 33 (22 ThingDef, 5 ResearchProjectDef, 3 ThoughtDef, + others)
- Save hits: 7 of 33 defNames — `RimAI_AIServer_Lv1A/Lv2A/Lv3A`,
  `RimAI_AITerminalA`, `RimAI_GWAntennaA` (all as `<thingDef>` blueprint/record
  entries, spot-checked `RimAI_AIServer_Lv1A` at line 85760), plus 2
  Techprint defNames
- Class= hits: **`RimAI.Core.Source.Infrastructure.Scheduler.SchedulerGameComponent`**
  and **`RimAI.Core.Source.Modules.Persistence.PersistenceManager`** — two
  live scribed GameComponents
- Verdict: **DIRTY**

### 6. `mlie.jurassicrimworlddinosaursonly` — **DIRTY**
- Defs in dump: 912 (534 ThingDef, 228 SoundDef, 131 PawnKindDef, + others; no TerrainDef)
- Save hits: 93 of 912 defNames, e.g. `DinoChitin` (confirmed: 5× placed
  `<thing Class="ThingWithComps"><def>DinoChitin</def><id>DinoChitin6512xx</id><map>0</map>`,
  lines 349697/349719/349767/349807/349896), plus egg defNames, leathers,
  `DinoChitinStrong`
- Verdict: **DIRTY** — actual placed Things on map 0, not just filter-list noise

### 7. `mlie.beastsoftherim` — **DIRTY**
- Defs in dump: 102 (83 ThingDef, 19 PawnKindDef; no TerrainDef)
- Save hits: 35 of 102 defNames — egg defNames (`EggWormFertilized`, etc.),
  numerous `Leather_<Beast>` materials (`Leather_Bardelot`, `Leather_Toraton`,
  `Leather_Megasquid`, …) present as `<thingDef>` blueprint/record entries
- Verdict: **DIRTY**

### 8a. `redmattis.bigsmall` (Races) — **DIRTY**
- Defs in dump: 62 (48 PawnKindDef, 6 FactionDef, 4 ThingDef, + others)
- Save hits: 2 of 62 — `BS_BarbarianArmor`, `VFEM_Bow_HeavyCrossbow` (both
  confirmed `redmattis.bigsmall`-owned ThingDefs in the dump, not a name
  collision with another mod), present as `<thingDef>` blueprint/record entries
- Verdict: **DIRTY**

### 8b. `redmattis.bigsmall.core` (Genes & More) — **DIRTY**
- Defs in dump: 779 (371 GeneDef, 71 ThingDef, 63 XenotypeIconDef,
  56 HediffDef, + many others)
- Save hits: 71 of 779 defNames, and this one is the sharpest hit in the
  whole set: **`BS_LargeFrame` is attached to a live pawn** —
  ```
  176515  <li>
  176516    <def>BS_LargeFrame</def>
  176517    <pawn>Thing_Human51546</pawn>
  ```
  (a gene on a colonist/pawn's genepack list, ×8 total occurrences of that
  defName across the save) plus `BS_Diet_Carnivore`, `BS_SmallFrame`,
  `BS_EarlyMaturity`, `BS_AlienAppearanceTolerance_Default`,
  `HalfJotunFrame`, `BMad_ShrinkRay`, `BS_OgreBody`, `BS_VerySlowAging`,
  `BS_WomanInBlue`, and 60 more
- Verdict: **DIRTY** — a pawn genuinely carries this mod's gene right now

## Verdict summary table

| packageId | def count | verdict | key evidence |
|---|---|---|---|
| xmb.ancienturbanruins.mo | 911 | DIRTY | `AM_DamagedEmptyShelves` placed thing + blueprint record |
| meteores.ancienturbanruinsalldeconstructible.aurad | 0 | CLEAN | ZERO_DEFS, no Assemblies, no Class= tokens |
| meteores.ancienturbanruinsvanillaloot.aurvl | 0 | CLEAN | ZERO_DEFS, no Assemblies, no Class= tokens |
| hailuan.customquestframework | 160 | DIRTY | `QE_Cabinet` etc. + live `MapComponent_CQFLord` |
| hailuan.customquestframeworkai | 8 | CLEAN | 0/8 hits, no distinct Class= token |
| kilokio.rimai.framework | 0 | CLEAN | ZERO_DEFS, no `RimAI.Framework.*` Class= hits |
| kilokio.rimai.core | 33 | DIRTY | `RimAI_AIServer_Lv1A` etc. + live `SchedulerGameComponent`/`PersistenceManager` |
| mlie.jurassicrimworlddinosaursonly | 912 | DIRTY | `DinoChitin` ×5 placed Things on map 0 |
| mlie.beastsoftherim | 102 | DIRTY | multiple `Leather_<Beast>`/egg defNames present |
| redmattis.bigsmall | 62 | DIRTY | `BS_BarbarianArmor`, `VFEM_Bow_HeavyCrossbow` present |
| redmattis.bigsmall.core | 779 | DIRTY | `BS_LargeFrame` gene on live pawn `Thing_Human51546` |

## Unmeasured / not checked

- **Terrain**: `xmb.ancienturbanruins.mo` (4 TerrainDefs) and
  `hailuan.customquestframework` (3 TerrainDefs) — terrain lives in
  compressed map grids, not grepped. `TERRAIN_UNCHECKED`. Given both mods
  are already DIRTY on other grounds, this doesn't change either verdict,
  but if either mod is kept-terrain-only-cut, run `savemap.py` before
  trusting a terrain-specific cut.
- The repo-root `/mnt/d/Luke/dev/Rimworld/defs.sqlite` is empty (0 bytes) —
  flagging for whoever owns it; not touched here.
- No git actions taken; no writes to the save, its folder, the ledger, or
  the queue files.
