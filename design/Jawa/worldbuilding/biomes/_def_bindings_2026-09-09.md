# Biome/def binding table — work-packet prep for the fauna/flora assignment pass

_Regenerated 2026-09-20 from `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles,
27 distinct painted biomes), parsed with Python's `csv` module; the `def` and
`tiles` columns are that parse and the `wildAnimals owner` column is a parse of
every `BiomeDef` in `src/**/Defs/**/*.xml` plus every `<xpath>` in the patch
files. The sheet and §10 columns are unchanged human knowledge from the
2026-09-09 compilation._

⚠️ **The painted CSV is ONE instrument.** A live world read is the confirming
instrument and has not been run. `GRASSLANDS_TILES_CSV_STALE_1` is open against
this very CSV on `ZBiome_Grasslands` — that is the one row it bites.

🔑 **Every painted biome has exactly one row and every row carries painted
ground**; the tile column sums to 21,872.

## 1. Def → sheet → §10 → wildAnimals owner

| def | tiles | sheet | §10 "Bestiary sorts"? | wildAnimals owner |
|---|---:|---|---|---|
| `RUT_Desert` | 2390 | `desert.md` | no (§10 = "Implementation", not bestiary) | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Desert.xml` |
| `RUT_ExtremeDesert` | 3969 | `dune_sea.md` + `deep_desert.md` (ONE merged roster, R22) | no (neither sheet) | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ExtremeDesert.xml` |
| `RUT_Umbra` | 2531 | `the_propane_lakes.md` (the antistellar cap the sheet names "Umbra") | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml` |
| `RM_TheRot` | 2204 | `the_rot.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RM_TheRot.xml` |
| `RUT_Wasteland` | 1853 | `wasteland.md` | no (§10 = "Campaign hooks") | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Wasteland.xml` |
| `RUT_NightsideIce` | 1506 | `nightside_ice.md` | no (§10 = "The door — occupied") | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml`, FROZEN 2026-09-24 (`NIGHTSIDEICE_RM_MOD_BUILD_1`) — carries the world until Phase B's repaint; content lives in `src/RimMandrake/NightsideIce/Defs/BiomeDefs/RM_NightsideIce.xml` (`mandrake.rm.nightsideice`) now |
| `RUT_ForsakenCrags` | 1135 | `forsaken_crags.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ForsakenCrags.xml` |
| `RUT_BlueDesert` | 1029 | `the_blue_desert.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_BlueDesert.xml` — 3 `wildAnimals` + 6 `wildPlants` rows since `BLUE_DESERT_LIFE_AUTHORING_1` (done 2026-09-21; re-read 2026-09-23) |
| `RUT_CrackedLands` | 970 | `the_cracked_lands.md` | **YES** — §10 "The bestiary sorts — a fauna divided by TIME, not space" | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_CrackedLands.xml` |
| `RUT_AridShrubland` | 628 | `arid_shrubland.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml` |
| `RM_TwilightSea` | 607 | `terminator_sea.md` (surface); `the_twilight_deep.md` (bottom) — **both claim it, see flag below** | no on either | own def file: `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml` |
| `RUT_PoisonForest` | 546 | `poison_forest.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PoisonForest.xml` |
| `RM_GreySea` | 472 | `terminator_sea.md` (surface); `the_grey_deep.md` (bottom) — **both claim it, see flag below** | no on either | own def file: `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml` |
| `RM_TheScald` | 312 | `the_scald.md` | no | own def file: `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml` |
| `RUT_RustCathedral` | 236 | `the_rust_cathedral.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml` |
| `RUT_Greentide` | 235 | `the_greentide.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml` |
| `RUT_WeepingStones` | 223 | `weeping_stones.md` | **YES** — §10 "The bestiary — who comes to the water" (bestiary-content, titled slightly differently than "sorts" but is the enrichment-pass §10) | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_WeepingStones.xml` |
| `ZBiome_Grasslands` | 222 | `the_pyrelands.md` | no | **donor mod only — no local override.** Our only local ops on it REMOVE duplicates (`AnimalBiomeDuplicates_Fix.xml`, `ZZZ_BiomeWildAnimalDuplicates_Generated.xml`). 🔴 `WildAnimals_Pyrelands.xml` wires the ruled roster into `RM_FE_Pyrelands` (0 painted tiles), not here — `PYRELANDS_WRONG_BIOME_DEF_1` |
| `RUT_Contagion` | 179 | `the_contagion.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Contagion.xml` |
| `RUT_Webwork` | 161 | `the_webwork.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Webwork.xml` |
| `RUT_Slime` | 96 | `the_slime.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml` |
| `RUT_Miasma` | 93 | `the_miasma.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` |
| `RUT_Scarlands` | 90 | `the_scarlands.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml` |
| `RM_PropaneLake` | 57 | `the_propane_lakes.md` (the lake proper; `RUT_Umbra` is the cap it sits under) | no | own def file: `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_PropaneLake.xml` — 3 `wildAnimals` + 6 `wildPlants` rows since `BLUE_DESERT_LIFE_AUTHORING_1` (done 2026-09-21; re-read 2026-09-23) |
| `RUT_TheForge` | 44 | `the_forge.md` — one sheet, one massif | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml` |
| `RUT_FeverWood` | 43 | `the_fever_wood.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml` |
| `RUT_Sump` | 41 | `the_sump.md` | no | own def file: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Sump.xml` |

**§10 tally: 2 of the 27 painted defs sit under a sheet with an enriched bestiary
§10** (`RUT_CrackedLands`/the_cracked_lands.md, `RUT_WeepingStones`/weeping_stones.md —
the two "worked examples" `README_BIOME_GRAMMAR.md` itself names for the
enrichment pass). Every other sheet's numbered §10, where one exists at all
(`desert.md`, `nightside_ice.md`, `wasteland.md`, `wreck_fields.md`), is a
differently-purposed section, not a bestiary.

**wildAnimals ownership, MEASURED 2026-09-20.** 26 of the 27 painted defs
declare `wildAnimals` directly in their own
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/<def>.xml`; no patch file
wholesale-replaces any of them. `ZBiome_Grasslands` is the sole donor def and
has no local override. Two of the 26 declare an EMPTY `<wildAnimals />` —
`RUT_BlueDesert` (1,029 tiles) and `RM_PropaneLake` (57) — so 1,086 painted
tiles currently have no cast.

🔑 **How each row's def was established.** The row's SHEET was looked up in
`README_BIOME_GRAMMAR.md`'s progress table, which states the owner-given biome
NAME for that sheet; that name was matched against the live def's `<label>`
(`the_rot.md` → "the Rot" → `RM_TheRot`; `the_cracked_lands.md` → "the Cracked
Lands" → `RUT_CrackedLands`; `the_blue_desert.md` → "Blue Desert" →
`RUT_BlueDesert`). Tile-count identity corroborated but never decided. Per-row
working: `Transient/biome_bindings_regen_20260920.md`.

## 2. Flags

- **RM_TwilightSea and RM_GreySea are each claimed by two sheets.** `terminator_sea.md`
  defines the surface/open-water ecology for both seas; `the_twilight_deep.md` and
  `the_grey_deep.md` each define that same def's SEA-BOTTOM ecology (design done,
  🔵 implementation deferred to the diving mods per `README_BIOME_GRAMMAR.md`'s own
  progress table). This reads as intentional layering (surface sheet + bottom sheet
  per sea), not a collision — but it means the def's `wildAnimals` roster is not
  fully specified by any ONE sheet; the assignment pass needs both per sea.
- **fall_line.md, the_lantern_deeps.md, wreck_fields.md, assailant_weapon_remnants.md**
  are deliberately unbound to any painted def (injection layers / dissolved-and-
  reabsorbed / not-a-biome rulings) — not gaps, per the task's own framing.
- No sheet was found naming zero def or two sheets colliding on one def other than
  the twilight/grey-sea case above.

## 3. The five standing questions

**1. Offline def dump — plants.** `src/RimMandrake/Utils/refresh.py`'s `D_DUMP`
resolves (via `game_paths.newest_capture()`) to
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon
Studios/DefDump/captures/<latest-id>/` (currently `2026-09-09T01-54-07Z`,
CONFIRMED to exist on disk). There is **no `PlantDef.json`** — RimWorld plants are
`ThingDef` rows (`thingClass`/`category=Plant`) living inside `defs/ThingDef.json`,
which is **385 MB** (CONFIRMED via `du -h`, not opened whole per the
measuring-large-artifacts rule). `manifest.json.defCounts.ThingDef = 25,812`
(CONFIRMED) — that is ALL ThingDefs, not plants specifically; a plant-only count
needs a real instrument (`measure`), which is **not installed/on PATH in this
environment** (`which measure` → not found) — **UNMEASURED**. A `defs.sqlite`
derived index sits beside the dump (`DefDump/defs.sqlite`, tables
`defs`/`def_flags`/`def_tags`) but I did not validate its plant-filter query
against a known answer, so any count from it would be UNCERTAIN, not CONFIRMED —
not used here. **The actual usable plant candidate pool already exists**, separate
from the dump: `design/Jawa/mods/plant_pool.csv`, **670 lines = 669 plant rows**
(CONFIRMED via `wc -l`), columns include defName/label/mod/growDays/temp
tolerances/sowTags/texPath; it is the `POOL` constant read by
`design/Jawa/mods/biome_flora.py`. This is the pool the assignment pass should use.

**2. `creature_register_rows.json`.** Path:
`design/Jawa/worldbuilding/review/creature_register_rows.json`. Structure is
`{"meta": {...14 keys}, "rows": [...]}`. **`len(rows) == 1165`** (CONFIRMED by
`json.load` + `len()`) — matches `_assignment_prep.md`'s stated "1,165 rows,
595-mod dump 2026-09-05, calibration PASSED" claim exactly.

**3. `biome_flora.py` FAMILIES.** Yes — it is a **two-level** dict (MEASURED
2026-09-20 via `ast.literal_eval` of the module's AST): **5** top-level
narrative-category keys, holding **20** distinct BiomeDef defName keys, all of
them painted `RUT_*`/`ZBiome_Grasslands` defs: `RUT_AridShrubland,
RUT_Contagion, RUT_CrackedLands, RUT_Desert, RUT_ExtremeDesert, RUT_FeverWood,
RUT_ForsakenCrags, RUT_Greentide, RUT_Miasma, RUT_PoisonForest, RUT_Scarlands,
RUT_Slime, RUT_Sump, RUT_TheForge, RM_TheRot, RUT_Umbra, RUT_Wasteland,
RUT_Webwork, RUT_WeepingStones, ZBiome_Grasslands`. The other **7** painted
defs are in the module's own `PLANTLESS` set on purpose — `RUT_NightsideIce,
RUT_BlueDesert, RUT_RustCathedral, RM_TwilightSea, RM_GreySea, RM_TheScald,
RM_PropaneLake`. 20 + 7 = 27: **there is no flora gap.** ⚠️ FOUNDRY was
mid-edit on this file when it was measured, so re-measure before acting on the
weights; the key SET is what matters here. (`PLANTLESS` also now carries
`RM_NightsideIce` — `NIGHTSIDEICE_RM_MOD_BUILD_1`'s new standalone mod's own
defName, 0 tiles, not one of the 27 painted defs — so the 7/20/27 counts above
are unaffected.)

**4. De-dup union machinery (`BIOME_DUPLICATES_STILL_LIVE_1`).** Generated file:
`src/RimUtinni/UtinniPatches/Patches/AnimalBiomeDuplicates_Generated.xml`
(header: "GENERATED - do not hand-edit. Regenerate with `biome_animal_conflicts.py`,
flag `xml`"). Generator script: **`src/RimMandrake/Utils/biome_animal_conflicts.py`**
(CONFIRMED, `grep -rl` hit). It fixes the double-registration bug where an animal
listed by both a biome's `wildAnimals` and its own `race.wildBiomes` throws in
`BiomeDef.CommonalityOfAnimal()`'s dictionary Add — always removing the ANIMAL
side. Companion hand-written file (still correct, not superseded):
`AnimalBiomeDuplicates_Fix.xml` in the same directory.

**5. `EARTH_FAUNA_EXCLUDED.txt`.** Path: `design/Jawa/fauna/EARTH_FAUNA_EXCLUDED.txt`.
**129 total lines / 85 non-blank/non-comment content lines** (CONFIRMED via `wc -l`
and a `^[A-Za-z]` count). ⚠️ Its own header is a live caveat, not just data: "KNOWN
GAP … RETEXTURES OF BANNED ANIMALS ARE NOT BANNED" — the list is Core/Odyssey
defNames only; reskinned Earth animals under mod-prefixed defNames (its own cited
examples: `GRimTortoise`, `GRimCobra`) pass straight through it. Relevant to this
packet: any def-bindings-driven cast pass should NOT treat this file as a complete
denylist (matches the `defname-denylists-miss-retextures` lesson already on file).
