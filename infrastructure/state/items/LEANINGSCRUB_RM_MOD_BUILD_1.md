# LEANINGSCRUB_RM_MOD_BUILD_1 — build RM_LeaningScrub as its own RimMandrake mod

**the Leaning Scrub (was arid shrubland, a vanilla label)**

Phase A row 9 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

1. **Step table**

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/LeaningScrub/` folder exists (MEASURED: `find` returns nothing); mod not scaffolded |
| 2 copy content | ⛔ OWED — `RM_LeaningScrub` does not exist anywhere in the repo (0 hits for the string) |
| 3 freeze the twin | ⛔ OWED — `RUT_AridShrubland.xml` carries no freeze header, still the live authoring target |
| 4 retarget | ⛔ OWED — see §7 table below; most refs are comments (Greentide shape), a handful are real |
| 5 prove it loads | ⛔ OWED — Desktop-only, no mod exists yet to test |
| 6 commit/push | ⛔ OWED |
| paint-list append | ⚠️ PARTIAL — `infrastructure/state/facts/biome_paint_list.md:24` carries a generic `RUT_AridShrubland` row (status `PAINT`, 628 tiles); no `RM_LeaningScrub` row exists yet and `WORLD_REMAKE_FINAL_STEP_1.md` names neither (grep: 0 hits) |
2. **The def today**

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml`, 213 lines (MEASURED,
`wc -l`; the header comment's own claim of 628 tiles is the tiles record, not cited as a
build signal). `workerClass` = `RimWorld.BiomeWorker_AridShrubland` — this is **vanilla
Core**, not a donor mod class (unlike the `AlphaBiomes.*`/`VanillaBiomes.*`/`BiomesPlus.*`
cases step 2 warns about), so `RM_LeaningScrub` can keep referencing it directly; no
`RM_BiomeWorker_LeaningScrub` is owed. **No `<modExtensions>` block** (MEASURED, absent).
Terrain: vanilla `Sand`/`Soil`/`SoilRich` only, no custom TerrainDef. Weather: 10 vanilla/DLC
entries (`Clear`, `Fog`, `DryThunderstorm`, `SnowGentle`, `SnowHard`, `Rain`,
`RainyThunderstorm`, `FoggyRain`, `GrayPall` [Anomaly], `Overcast` [Odyssey]) — no custom
WeatherDef exists for the sheet's own Stall/Gale (confirmed absent, `find` on
`src/RimUtinni` for `*Stall*`/`*Gale*` returns nothing). Diseases: 9 vanilla `Disease_*`
only. No hediff defs, no game-condition defs authored for this biome.
3. **wildAnimals split** — MEASURED by parsing `<wildAnimals>` (shorthand `<Tag>commonality</Tag>`
   form, `len(list(node))` = **45** rows, not `grep -c`). 40 carry `MayRequire` naming a Star
   Wars source → Utinni per §7 Q11 (which forbids donor SW names too, not just `RSW_`); 5 stay.
   `WildAnimals_LeaningScrub.xml` does not exist yet (0 hits).

| defName | comm | MayRequire | verdict |
|---|---|---|---|
| FrilledGorg, Gorg, Iriaz, LongtailGorg, Eopie, Kreetle, Lothcat, Mudhorn, Ronto, Scurrier, Sketto, Igitz, Urusai, Kybuck, Massiff, Bantha, Pufferpig, Anooba, Corinathoth, Gizka, Nuna, Worrt, Grank, Qormot, Strill, Cannok, Whisperbird, Pikobis, Convor, Skalder, Vulptex, FeralNerf, Porg, Voorpak, KowakianMonkeyLizard (35 rows, 1.0→0.01) | as authored | `mlie.starwarsanimalcollection` | → Utinni `WildAnimals_LeaningScrub.xml` (donor SW name, Q11 bars it inline even without an `RSW_` prefix) |
| RSW_ShrublandGiant 0.35, RSW_TunnelSnake 0.5, RSW_ScrapNestBird 0.45, RSW_ImperialToad 0.7, RSW_MossBeetle 0.3 (5 rows) | as authored | `mandrake.rsw.swbestiary` | → Utinni `WildAnimals_LeaningScrub.xml` (ours, but still Star Wars — Q11 bars `RSW_` too) |
| Terrorworm 0.7 | — | `mlie.horrors` | stays `RM_LeaningScrub` (non-SW donor, Q9) |
| AA_Cactipine 0.25, AA_Needlepost 0.1, AA_Wildpawn 0.1, AA_Wildpod 0.025 (4 rows) | as authored | `sarg.alphaanimals` | stays `RM_LeaningScrub` (non-SW donor, Q9) |

⚠️ `SW_FAUNA_NEVER_IN_RM_TIER_1.md:64` cites **35/45** for this biome (measured 2026-09-22)
— narrower than the 40/45 measured here today. The 5-row gap is exactly the
`mandrake.rsw.swbestiary` set; either that item's count predates them or undercounted —
flagged, not resolved (see False statements below).
4. **wildPlants split** — MEASURED, `len(list(node))` = **11** rows, all non-Star-Wars (no
   `RSW_`/`SW_` plant in this biome) — nothing here goes to a Utinni fauna-style patch;
   flora is a §3c/Q8 question (dissolve `mandrake.rut.ashkarrflora`), not a Star Wars one.

| defName | comm | MayRequire | verdict |
|---|---|---|---|
| `RUT_Fuzz` | 0.9 | `mandrake.rut.ashkarrflora` | → `RM_LeaningScrub` (ours; move the ThingDef out of AshkarrFlora, §3c/Q8) |
| `RG_Plant_AridGrass` | 0.5 | — | stays `RM_LeaningScrub` (donor, ReGrowth; not owner-rejected — no ruling found) |
| `Plant_Brambles` | 0.3 | — | stays `RM_LeaningScrub` (vanilla; not rejected) |
| `RUT_Grellbush` | 0.3 | `mandrake.rut.ashkarrflora` | → `RM_LeaningScrub` (ours, replaces vanilla `Plant_Bush`, `DESERT_FAMILY_PORT_EXECUTION_1` DONE) |
| `RUT_Grellspine` | 0.3 | `mandrake.rut.ashkarrflora` | → `RM_LeaningScrub` (ours, replaces Biotech `Plant_Ripthorn`, DONE) |
| `RUT_WildHealroot` | 0.25 | `mandrake.rut.ashkarrflora` | → `RM_LeaningScrub` (ours, replaces vanilla `Plant_HealrootWild`, DONE; label "wild healroot" kept per owner ruling) |
| `Plant_Nysyllin_Wild` | 0.22 | — | stays `RM_LeaningScrub` (vanilla-adjacent SW herb name, not IP per Q11a — not rejected) |
| `RG_Plant_CreepStern` | 0.2 | — | stays `RM_LeaningScrub` (donor, not rejected) |
| `RG_Plant_CrimsonCushion` | 0.2 | — | stays `RM_LeaningScrub` (donor, not rejected) |
| `RG_Plant_Dervish` | 0.2 | — | stays `RM_LeaningScrub` (donor, not rejected) |
| `RM_VenomvineThicket` | 0.15 | `mandrake.rm.environmentalhazards` | stays inline — already `RM_`-tier, lives in the §2d shared lib `EnvironmentalHazards`, no move |

No owner-rejected row found in this list (no "vanilla temperate filler" analog here — that
was Greentide's jungle-tree finding, not this biome's).
5. **Roster vs def diff** — MEASURED by set-diff of `rosters/arid_shrubland.json` (`fauna`+`flora`
   arrays, authored 2026-09-09) against the live def's parsed `wildAnimals`/`wildPlants`.

   **Roster fauna NOT in def (1/41):** `VAEWaste_Hydra` (action `import`, comm 0.5, "venomvine
   patch predator") never landed. UNMEASURED whether it exists anywhere in `src/`.

   **Def fauna NOT in roster (5/45, all post-2026-09-09):** `RSW_ShrublandGiant`,
   `RSW_TunnelSnake`, `RSW_ScrapNestBird` (`COMMISSION_LEDGER_CLEANUP_1`/
   `SHRUBLAND_SCRAPNEST_BIRDS_1`, 2026-09-20) + `Skalder`, `AA_Wildpawn` (pre-existing, just
   absent from the roster snapshot) — roster is stale here, not the def.

   **Roster flora NOT in def (3/11):** `Plant_Bush`/`Plant_HealrootWild`/`Plant_Ripthorn` —
   **not missing, RENAMED.** `DESERT_FAMILY_PORT_EXECUTION_1` replaced these with our own
   `RUT_Grellbush`/`RUT_WildHealroot`/`RUT_Grellspine` at the same commonalities (confirmed
   live). The roster JSON is stale on the name; the def is correct — a roster-doc fix, not a
   build gap.

   **Art presence** (`_south.png`, never `_southm.png`):
   - `RUT_Fuzz`, `RUT_Grellbush`, `RUT_Grellspine`, `RUT_WildHealroot` — **MEASURED MISSING**
     (0 PNGs under `AshkarrFlora/Textures` or `artpipe/done`); each has a queued, undelivered
     job in `infrastructure/artpipe/pending/` (`rutfuzz_v1.json`, `rut_grellbush.json`,
     `rut_grellspine.json`, `rut_wildhealroot.json`).
   - `RUT_SweetlineTree` — art **present** (`Textures/Things/Plant/RUT_SweetlineTree/*.png`,
     4 variants A–D), but 🔴 **the def is not wired into `RUT_AridShrubland.xml`'s `wildPlants`
     at all** (0 references anywhere in `src/` besides its own ThingDef file and a BetterTrees
     immunity patch) — the sweetline tree, a named §4 landmark feature, does not currently spawn.
     Not a tile-count finding; this is the def simply never being added to the biome's plant list.
   - `RM_VenomvineThicket` — **UNMEASURED** this pass (shared-lib def, not re-checked).
   - The 40 Star Wars fauna rows' art is donor/shared texture folders (`swanimals/Fambaa/*`,
     `swanimals/Klorslug/*` etc.) — out of scope, Utinni-tier, not checked.
6. **Content to move into the mod**

Moves in (franchise-free, per §3a's test):
- `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_Fuzz.xml` — the fuzz ThingDef
- `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AridShrublandVanillaReplacements.xml`
  — `RUT_Grellbush`/`RUT_Grellspine`/`RUT_WildHealroot` ThingDefs
- `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AshkarrFlora_Plants.xml` —
  `RUT_SweetlineTree` only (1 def in this file; MEASURED via `grep -c "<ThingDef"` = 1)
- `src/RimUtinni/AshkarrFlora/Patches/BetterTrees_SweetlineTree_Immunity.xml` (rides with the tree)
- Corresponding `Textures/Things/Plant/RUT_Fuzz*`, `RUT_Grellbush*`, `RUT_Grellspine*`,
  `RUT_WildHealroot*` (none exist yet — see §5) and `RUT_SweetlineTree/*.png` (4 files, exist)
- No C# to move — `mandrake.rut.ashkarrflora` ships **zero `.cs` files** (MEASURED, `find`)

Stays out (Utinni/campaign or shared-lib, per §3a):
- `RUT_AridShrubland.xml` itself — frozen in place at step 3, not deleted
- All 40 Star Wars `wildAnimals` rows and their patch file (new, Utinni-tier)
- `RM_VenomvineThicket` + `RM_CompBodySizeBarrier` — already `RimMandrake.EnvironmentalHazards`,
  a §2d shared library; no move, no rename
- `RM_ParentalEnrageExtension`/`RM_CompParentalEnrage`/`RM_MentalState_ParentalEnrage` —
  already `RimMandrake.CreatureBehaviors`, a §2d shared library, wired onto `RSW_ShrublandGiant`
  (a Utinni-tier creature def) — the mechanic is generic and RimMandrake-tier already
- `src/RimUtinni/UtinniPatches/Patches/BiomeNames_Ashkarr.xml` /
  `BiomeDescriptions_Ashkarr.xml` — target vanilla `AridShrubland`, not our def (see §7)
- `src/RimUtinni/UtinniPatches/build_desert_review_sheet.py` — a Transient review-sheet
  generator, not live wiring; low priority to retarget
7. **References to `RUT_AridShrubland` across the repo** — `grep -rl` (excluding
`infrastructure/state/items/`, `.git/`) then read each hit. Most are comments, exactly the
Greentide shape:

| file | classification |
|---|---|
| `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ScrapNestBird.xml` (3 refs), `RSW_TunnelSnake.xml` (1) | (c) comment/prose — leave |
| `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AridShrublandVanillaReplacements.xml`, `RUT_Fuzz.xml` | (c) header comments — leave (these two files themselves are moving, §6) |
| `src/RimUtinni/UtinniPatches/About/About.xml:71` | (c) comment on a `<li>` dependency line — leave |
| `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml` | the def itself — freeze header owed, step 3 |
| `src/RimUtinni/UtinniPatches/Patches/BiomeDescriptions_Ashkarr.xml:258-263`, `BiomeNames_Ashkarr.xml:214-223` | **(c) comment only** — READ the actual `<Operation>`: both target `defName="AridShrubland"` (**vanilla** Core biome), not `RUT_AridShrubland`; "RUT_AridShrubland" appears only in the trailing `<!-- -->` comment. No retarget — `RM_LeaningScrub` will carry its own native label/description like `RM_Greentide` does |
| `src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml:31` | (c) comment, inside that file's own "biomes this file deliberately does NOT patch" exclusion block — same shape as Greentide's exact case, leave |
| `src/RimUtinni/UtinniPatches/build_desert_review_sheet.py` (6 refs) | (a) retarget-outright candidate, low priority — a Transient report generator, not live wiring |
| `world/biome_world_switch_apply.py`, `world/ASHKARR_WORLDMAP_tiles.csv` | Phase B only, per spec — do not touch now |
| `design/Jawa/fauna/biome_name_migration.py`, `design/Jawa/mods/biome_flora.py`, `design/Jawa/worldbuilding/biome_flora_rosters.md`, `_def_bindings_2026-09-09.md`, `fall_line.md`, `sweetline_guardian_spec.md`, `infrastructure/state/facts/biome_paint_list.md`, `biome_rosters.md` | (a) retarget-outright candidates, target need not be on the world — not read line-by-line this pass, UNMEASURED which need a second op vs a straight rename |

**No `PatchOperationAdd`/`Remove` in `UtinniPatches/Patches/*` targets `RUT_AridShrubland`
directly today** (no doctrine/ambient patch keyed to it found in this search) — UNMEASURED
whether `AncientDangerGenSteps_AmbientDoctrine.xml` etc. (§3b's named examples) touch it;
not read this pass.
8. **Mechanics/kit state** — no `kits/*.md` spec exists for this biome (row 9's table cites only
`arid_shrubland.md`, unlike Rot/Scald/Rust Cathedral etc.), so its "kit" is smaller and mostly
shared-library:

| mechanic | state | ships in |
|---|---|---|
| Venomvine body-size passability barrier | ✅ SHIPPED | `mandrake.rm.environmentalhazards` (`RM_CompBodySizeBarrier`) — shared lib, moves with nothing |
| Parental enrage (giant young) | ✅ SHIPPED, wired onto `RSW_ShrublandGiant` | `mandrake.rm.creaturebehaviors` — shared lib |
| Tree-guardian generic species (owner ruled 2b) | ⛔ UNBUILT | new build, lands into `RM_LeaningScrub` later — `SHRUBLAND_TREE_GUARDIAN_1` |
| Stall/Gale wind WeatherDefs + AI hooks | ⛔ UNBUILT | no WeatherDef exists (MEASURED absent); names are locked (`ARIDSHRUBLAND_SHIPPING_NAMES_1`) but nothing to port yet |
| Vaporator desertification (V-blight) | ⛔ UNBUILT | sheet's own "Owed", not started |
| Canopy-concealment vs colony visibility stat | ⛔ UNBUILT | engine feasibility pass not run (sheet's own Owed) |

**Nothing here blocks steps 1–4**: the two shipped mechanics are already in shared
RimMandrake libraries and need no move; the four unbuilt ones simply have nowhere to land
yet and are not waited on.
9. **Dependencies & items building into this mod** — found by grepping item filenames/bodies
for `AridShrubland`/`LeaningScrub` (19 hits, `rimflow show` run on each):

| item | `rimflow show` state | blocks step 2? |
|---|---|---|
| `ARIDSHRUBLAND_SHIPPING_NAMES_1` | proposed — 4/5 names ruled (thunderstep, yanker, venomvine stands, Stall/Gale stand); only **#1 the fuzz** still open, owner said wait for a BENCH item | NO — item itself says the rename is cheap and doesn't need to block anything |
| `SHRUBLAND_TREE_GUARDIAN_1` | proposed — ruled (b) generic guardian species, now a build, unbuilt | NO — lands later |
| `OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` | body shows ✅ DONE 2026-09-21 — `mandrake.rut.ashkarrflora` is ACTIVE (619→620 activeMods), so `RUT_Fuzz` now spawns; only load-proof is outstanding | NO — already resolved |
| `DESERT_FAMILY_PORT_EXECUTION_1` | proposed — this biome's 3 rows (Grellbush/Grellspine/WildHealroot) are DONE per its own body | NO |
| `TREE_GRAPHICS_OWNERSHIP_1` | doing, **BLOCKED** — owner pick on 14 sweetline-tree art candidates still pending | NO for steps 1-4, but the sweetline tree isn't even wired into `wildPlants` yet regardless (§5) |
| `COMMISSION_LEDGER_CLEANUP_1` | doing — owns the art jobs (`rutfuzz_v1` etc.) queued in `infrastructure/artpipe/pending/` | NO |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | proposed — is literally this item's step 2/4 for all 12 biomes at once; this item's §3 table above already does that work for this biome specifically | overlaps, doesn't block |
| `BIOME_SPECIFIC_FAUNA_LAW_1` / `DUPLICATE_CANON_DEFNAME_PAIRS_1` | proposed — multi-home review sheets naming gizka/kreetle/nuna/worrt (also in this roster) | NO — review-sheet judgement work, explicitly not a rule sweep (owner ruling) |
| `ROSTER_DEAD_BMT_NAMES_SWEEP_1` | proposed — asks whether `BMT_Stoneback` should wire into this biome too (currently only `RUT_Desert`) | NO — a per-species decision, not filed against this biome's def |
| `BIOME_MOD_SPLIT_EXECUTION_1` (parent) | ⚠️ its `rimflow show` summary line still reads "BLOCKED on 10 owner questions" — **STALE**, all 11 are RULED per `biome_mod_architecture.md` §7 "Nothing is open" (2026-09-22) | see False statements below |
10. **Blockers** — **none for steps 1–4.** Step 5 (prove it loads) is Desktop-only, not a
blocker of starting. The fuzz's still-open name (#1 of `ARIDSHRUBLAND_SHIPPING_NAMES_1`) does
not block the build — the item itself says the rename is cheap and independent. Missing art
for 4 of 11 wildPlants rows (§5) does not block the def/mod move; it blocks nothing but the
visual — those rows already spawn as vanilla stand-ins today via the flammability-adjustment
patch and will keep doing so, magenta or not, once moved.
11. **Concrete step plan**

1. **Scaffold** `src/RimMandrake/LeaningScrub/About/About.xml`, packageId
   `mandrake.rm.leaningscrub`, `loadAfter` = [`mandrake.rm.environmentalhazards`] (the only
   confirmed cross-mod reference — `RM_VenomvineThicket`; `mandrake.rm.weathersuite`'s tie to
   this biome, if any, is UNMEASURED and campaign-side per its own About.xml, not asserted
   here). `RM_LeaningScrubSettings : ModSettings`, master toggle + venomvine-passability
   toggle (only shipped mechanic that's a real behaviour switch). Empty
   `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/`. `deploy_custom_mods.py --mod LeaningScrub`
   dry run, then `--apply`.
2. **Copy content**: `RM_LeaningScrub` BiomeDef (defName `RM_LeaningScrub`, keep
   `workerClass RimWorld.BiomeWorker_AridShrubland` as-is — vanilla Core, no wrapper owed),
   the 5 non-SW `wildAnimals` rows (Terrorworm, AA_Cactipine, AA_Needlepost, AA_Wildpawn,
   AA_Wildpod), all 11 `wildPlants` rows including moving `RUT_Fuzz.xml`,
   `RUT_AridShrublandVanillaReplacements.xml` (3 defs) and `RUT_SweetlineTree` (from
   `RUT_AshkarrFlora_Plants.xml`, extracting just that one def) plus their Textures folders
   into `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/` and
   `Textures/Things/Plant/`. Write `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LeaningScrub.xml`
   as a `PatchOperationAdd` of the 40 SW rows (35 `MayRequire="mlie.starwarsanimalcollection"`
   + 5 `MayRequire="mandrake.rsw.swbestiary"`) onto `/Defs/BiomeDef[defName="RM_LeaningScrub"]/wildAnimals`,
   shaped like `WildAnimals_Pyrelands.xml`. Native `<label>`/`<description>` on `RM_LeaningScrub`
   from `arid_shrubland.md` §1 (franchise-free — it already is).
3. **Freeze** `RUT_AridShrubland.xml`: one header line, *"carrying the world until the
   terminal paint; content lives in mandrake.rm.leaningscrub; do not edit here."*
4. **Retarget**: none of the found refs need a second `RM_` op today (§7 — the label/description
   ops target vanilla `AridShrubland`, not ours). Optionally repoint
   `build_desert_review_sheet.py`'s `BIOME_DEFS_DIR` entry — cosmetic, not required.
5. **Prove it loads** — Desktop only, minimal list + `mandrake.rm.leaningscrub` +
   `mandrake.rm.environmentalhazards` + `mandrake.rut.patches` + all five expansions;
   quicktest on a scratch world tile set to `RM_LeaningScrub`.
6. **Commit/push**, explicit paths, message naming that `RUT_AridShrubland` carried Star Wars
   fauna inline (the twin's defect). Append `RM_LeaningScrub` to
   `infrastructure/state/facts/biome_paint_list.md` next to the existing `RUT_AridShrubland` row.

### ⚠️ Uncertain / not fully verified this pass
- Whether any `UtinniPatches/Patches/*` doctrine file (`AncientDangerGenSteps_AmbientDoctrine.xml`
  etc.) keys off `RUT_AridShrubland` — not searched.
- `VAEWaste_Hydra` (roster fauna row, action `import`) — whereabouts in `src/` UNMEASURED.
- Whether `RM_VenomvineThicket`'s art exists — not checked this pass.
- The 35-vs-40 SW-fauna-row discrepancy against `SW_FAUNA_NEVER_IN_RM_TIER_1`'s own count (§3).

### False statements found elsewhere
- `infrastructure/state/items/BIOME_MOD_SPLIT_EXECUTION_1.md`'s ledger summary line (via
  `rimflow show`) reads *"BLOCKED on 10 owner questions in its section 7"* — this is stale.
  `design/RimMandrake/biome_mod_architecture.md` §7 states all eleven questions are RULED
  (Q1–Q10 on 2026-09-21, Q11 on 2026-09-22) under its own heading "Nothing is open." Whether
  this is the ledger's `file` text (immutable) or the item file's own body text drifting
  from the spec was not determined this pass — worth a look, but it's the parent item, not
  this one, so not corrected here per the brief's file-only-your-item-file rule.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.leaningscrub`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_LeaningScrub` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_LeaningScrub`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.leaningscrub`; do not edit here."* From that moment
   every content fix lands in `RM_LeaningScrub` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_LeaningScrub` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_LeaningScrub` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.leaningscrub` exists, deploys, and loads clean carrying `RM_LeaningScrub` with its own content and its own
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
