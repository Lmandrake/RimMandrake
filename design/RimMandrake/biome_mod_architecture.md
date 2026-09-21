# Biome mod architecture — one RimMandrake mod per converted biome

_Design spec, 2026-09-20. Implements the owner ruling of the same day. Status: DRAFT for owner review; builds nothing._

## 1. The ruling and the amendment

**Owner, 2026-09-20, verbatim:** *"please make sure that each of our actively converted
biomes is its own mod at the RimMandrake level. Lanterndeep, two deserts, pyrelands, the
rot, etc. only Star Wars creatures become patches applies from the utinni scenario layer."*

**BENCH's amendment, same day, load-bearing.** "Its own mod at the RimMandrake level" had
been built four times to mean *a BiomeDef with a `workerClass` that scores tiles and places
itself*. On Ash'karr that can never put a biome on the map: there is no worldgen, the world
is hand-painted and frozen (CLAUDE.md, owner 2026-08-15). `RM_FE_Pyrelands` is the proof —
self-contained, well built, and nothing of its own has ever placed it on the planet.
Whether the Pyrelands tiles carry it today or the relabelled donor grassland is a
live-read question (`PYRELANDS_WRONG_BIOME_DEF_1`; `GRASSLANDS_TILES_CSV_STALE_1` is open
on that row), and either answer proves the point: **the tiles carry whatever the paint
says, never what the worker scores.**

MEASURED this pass against the decompiled engine (RimSage, `BiomeDef.cs` line 188 and
`WorldGenStep_Terrain.cs` line 298): `BiomeDef.Worker.GetScore` is called from
`WorldGenStep_Terrain` and nowhere else. A `workerClass` is therefore **inert on a frozen
world** — it neither helps nor hurts Ash'karr. It is still worth shipping in a RimMandrake
mod because that mod is meant to be playable on a *generated* planet by anyone; it is just
not the mechanism that lands the biome on OUR planet.

So the rule this spec implements, stated for a cold reader:

1. **The RimMandrake mod owns the biome**: the `BiomeDef` and every piece of content that
   makes the biome what it is — terrain, plants, weather, game conditions, hediffs, the
   mechanics kit (C#), the non-Star-Wars fauna, the art for all of that, and a real Mod
   Settings screen. It names no franchise and no campaign. It works on any planet.
2. **The Utinni layer paints that def onto the frozen world's tiles and patches the Star
   Wars creatures in.** It also carries the campaign label for the biome ("the Deep
   Desert", "the Dune Sea"), the campaign description, and any wiring that names Ash'karr,
   a faction, a settlement, a quest or a tile.
3. **The def the world carries must BE the RimMandrake def.** Never a `RUT_` twin of it,
   never a donor def relabelled to look like it. `RUT_Greentide` beside `RM_Greentide` is
   the failure mode; one of every such pair dies.

What this is not: it is not a worldgen feature, it does not build alternative planets, and
it does not change how the one map is authored. It changes *which defName* the hand-painted
tiles carry and *which mod folder* the biome's content lives in.

Related rulings this spec rides on, all already recorded:
- `WORLD_REMAKE_FINAL_STEP_1` — a repaint is expected, a zero-tile owned def is not a
  defect, the repaint needs a paint list. This spec's §2 table IS that paint list.
- `BIOME_WORLD_SWITCH_WAVE_1` (closed, DONE live 2026-09-12) — 17,667 tiles were repainted
  donor→`RUT_` in one bridge session with `world/biome_world_switch_apply.py`. A repaint
  is a proven operation; the terminal `RUT_`→`RM_` paint is the same operation again,
  **once** (owner, same day: *"we will do the painting once and for all"*).
- `MOD_OPTIONS_RETROFIT_1` — every mod ships settings; biome-kit mechanics are enable-able
  in other biomes without the biome (§6).
- `design/NAMING_SCHEME_PLAN.md` — `mandrake.rm.<modname>`, `RM_` defNames, namespace
  `RimMandrake.<Mod>`; "Jawa" and every other lore word is label text only.

## 2. The mapping table — all 27 world biomes

The `tiles (record)` column is from `world/ASHKARR_WORLDMAP_tiles.csv`, a RECORD exported
from the savegame on 2026-09-12 (its own freeze stamp: *"a RECORD of the planet, not a
rival to it"*); a live read on 2026-09-19 already disagrees with it on the Pyrelands row.
The column says which defs the record carries — i.e. what the paint list must cover — and
nothing else: no tile count schedules, gates or defers any work in this spec. Current defs are read from
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml` (26 files) and the four existing
RimMandrake mods. Sheet = the frozen definition sheet under
`design/Jawa/worldbuilding/biomes/`. Every target name marked **PROPOSED** is a name this
spec invents and the owner has not seen; the rest already exist in the repo.

**The grouping rule.** The owner said *each* converted biome is its own mod, so standalone
is the default and a kit needs a reason. The only reason accepted here is: **two painted
defs are one place under one frozen sheet, and the sheet describes them as one system.**
That is true exactly twice. Every other pairing considered (the two deserts; Nightside Ice
+ Blue Desert; Poison Forest + Contagion) failed it — separate sheets, separate identities,
and in the deserts' case the owner named them separately in the ruling.

### 2a. Standalone mods — 23 biomes, 23 mods

| # | painted def today | tiles (record) | campaign label (stays in Utinni) | sheet | target mod folder `src/RimMandrake/` | packageId | BiomeDef defName | status |
|---|---|---:|---|---|---|---|---|---|
| 1 | `RUT_ExtremeDesert` | 3969 | the Deep Desert / the Dune Sea | `dune_sea.md` + `deep_desert.md` (one merged roster, R22) | `DeepDesert` | `mandrake.rm.deepdesert` | `RM_DeepDesert` | PROPOSED — owner-named standalone |
| 2 | `RUT_Desert` | 2390 | the Desert | `desert.md` | `ShadowDesert` | `mandrake.rm.shadowdesert` | `RM_ShadowDesert` | PROPOSED — owner-named standalone; name from the sheet's identity ("life is a sprint between islands of shade"); §7 Q2 |
| 3 | `RUT_TheRot` | 2204 | the Rot | `the_rot.md`, `kits/rot_kit_spec.md` | `TheRot` | `mandrake.rm.therot` | `RM_TheRot` | PROPOSED — owner-named standalone; absorbs `mandrake.rut.rotsporekit` (151 files, biome mechanics, not campaign) |
| 4 | `RUT_Wasteland` | 1853 | the Wasteland | `wasteland.md` | `Wasteland` | `mandrake.rm.wasteland` | `RM_Wasteland` | PROPOSED; owns the `RUT_WastelandBrine*` terrain family |
| 5 | `RUT_NightsideIce` | 1506 | the Nightside Ice | `nightside_ice.md` | `NightsideIce` | `mandrake.rm.nightsideice` | `RM_NightsideIce` | PROPOSED; thin (no plants by design) but it is a Lantern Deeps host surface |
| 6 | `RUT_ForsakenCrags` | 1135 | the Forsaken Crags | `forsaken_crags.md` | `ForsakenCrags` | `mandrake.rm.forsakencrags` | `RM_ForsakenCrags` | PROPOSED |
| 7 | `RUT_BlueDesert` | 1029 | the Blue Desert | `the_blue_desert.md` | `BlueDesert` | `mandrake.rm.bluedesert` | `RM_BlueDesert` | PROPOSED; `BLUE_DESERT_LIFE_AUTHORING_1` builds INTO this mod, not into UtinniPatches |
| 8 | `RUT_CrackedLands` | 970 | the Cracked Lands | `the_cracked_lands.md` | `FloodedCanyon` (EXISTS) | `mandrake.rm.floodedcanyon` | `RM_FloodedCanyon` | twin pair, §4; §7 Q4 |
| 9 | `RUT_AridShrubland` | 628 | the arid shrubland | `arid_shrubland.md` | `FogShrubland` | `mandrake.rm.fogshrubland` | `RM_FogShrubland` | PROPOSED — "arid shrubland" is a vanilla biome label; the sheet's identity is the fog-fed fuzz |
| 10 | `RUT_PoisonForest` | 546 | the Poison Forest | `poison_forest.md` | `PoisonForest` | `mandrake.rm.poisonforest` | `RM_PoisonForest` | PROPOSED |
| 11 | `RUT_TheScald` | 312 | the Scald | `the_scald.md`, `kits/scald_kit_spec.md` | `TerminalBiomes` | `mandrake.rm.terminalbiomes` | `RM_TheScald` | 🔴 RULED 2026-09-21 §7 Q1 — moves OUT of its own mod into the four-biome `TerminalBiomes` mod, independently toggleable. A sea biome (impassable) with a kit. |
| 12 | `RUT_RustCathedral` | 236 | the Rust Cathedral | `the_rust_cathedral.md`, `kits/rust_cathedral_kit_spec.md` | `RustCathedral` | `mandrake.rm.rustcathedral` | `RM_RustCathedral` | PROPOSED; absorbs `mandrake.rut.rustcathedralhum` / `...roaches` / `...walls` |
| 13 | `RUT_Greentide` | 235 | the Greentide | `the_greentide.md`, `kits/greentide_kit_spec.md` | `Greentide` (EXISTS) | `mandrake.rm.greentide` | `RM_Greentide` | twin pair, §4 |
| 14 | `RUT_WeepingStones` | 223 | the Weeping Stones | `weeping_stones.md` | `WeepingStones` | `mandrake.rm.weepingstones` | `RM_WeepingStones` | PROPOSED |
| 15 | `ZBiome_Grasslands` (DONOR, More Vanilla Biomes) | 222 | the Pyrelands | `the_pyrelands.md` | `Pyrelands` (EXISTS) | `mandrake.rm.pyrelands` | `RM_FE_Pyrelands` today; §7 Q3 asks for `RM_Pyrelands` | twin pair, §4; absorbs `mandrake.rut.pyrelandsmechanics` |
| 16 | `RUT_Contagion` | 179 | the Contagion | `the_contagion.md` | `Contagion` | `mandrake.rm.contagion` | `RM_Contagion` | PROPOSED |
| 17 | `RUT_Webwork` | 161 | the Webwork | `the_webwork.md`, `kits/webwork_kit_spec.md` | `Webwork` | `mandrake.rm.webwork` | `RM_Webwork` | PROPOSED |
| 18 | `RUT_Slime` | 96 | the Slime | `the_slime.md`, `the_slime_gene_lists.md` | `GelatinousSlime` (EXISTS) | `mandrake.rm.gelatinousslime` | `RM_GelatinousSlime` | twin pair, §4; `TITANOSLIME_SLIME_BIOME_1` builds here |
| 19 | `RUT_Miasma` | 93 | the Miasma | `the_miasma.md`, `kits/miasma_kit_spec.md` | `Miasma` | `mandrake.rm.miasma` | `RM_Miasma` | PROPOSED |
| 20 | `RUT_Scarlands` | 90 | the Scarlands | `the_scarlands.md`, `kits/scarlands_kit_spec.md` | `Scarlands` | `mandrake.rm.scarlands` | `RM_Scarlands` | PROPOSED; absorbs `mandrake.rut.scarlandsladder`; ⚠️ its worker is vanilla `RimWorld.BiomeWorker_Scarlands`, i.e. the label collides with a vanilla 1.6 biome — §7 Q5 |
| 21 | `RUT_TheForge` | 44 | the Forge | `the_forge.md`, `kits/forge_kit_spec.md` | `TheForge` | `mandrake.rm.theforge` | `RM_TheForge` | PROPOSED |
| 22 | `RUT_FeverWood` | 43 | the Fever Wood | `the_fever_wood.md`, `kits/fever_wood_kit_spec.md` | `FeverWood` | `mandrake.rm.feverwood` | `RM_FeverWood` | PROPOSED |
| 23 | `RUT_Sump` | 41 | the Sump | `the_sump.md`, `kits/sump_kit_spec.md` | `TheSump` | `mandrake.rm.thesump` | `RM_TheSump` | PROPOSED |

### 2b. Kits — 4 biomes, 2 mods

| # | painted defs today | tiles (record) | sheet (one sheet, one system) | target mod folder | packageId | BiomeDef defNames | why one mod |
|---|---|---:|---|---|---|---|---|
| 24 | `RUT_PropaneLake` | 57 | the Propane Lake | `the_propane_lakes.md` (`_def_bindings_2026-09-09.md`) | `TerminalBiomes` | `mandrake.rm.terminalbiomes` | `RM_PropaneLake` | 🔴 RULED 2026-09-21 §7 Q1 — an ocean biome made of propane, its own biome, shipping in the four-biome `TerminalBiomes` mod with a Mod Settings toggle. ⛔ `RUT_Umbra` is NOT a biome (it is a REGION) and has left this list. |
| 25–26 | `RUT_TwilightSea` + `RUT_GreySea` | 607 + 472 | the Twilight Sea, the Grey Sea | `terminator_sea.md` (surface), `the_twilight_deep.md` / `the_grey_deep.md` (floors) | `TerminalBiomes` | `mandrake.rm.terminalbiomes` | `RM_TwilightSea`, `RM_GreySea` | 🔴 RULED 2026-09-21 §7 Q1 — two of the four biomes in the shared `TerminalBiomes` mod, each independently toggleable. |

**Totals: 27 painted defs → 25 mods (23 standalone + 2 kits).** Four of the 25 mod folders
already exist; 21 are new.

### 2c. Not a worldmap biome, still owner-named: the Lantern Deeps

`the_lantern_deeps.md` (FROZEN 2026-09-07): *"Not a worldmap biome (owner: 'that was a
mistake') — an injected underground layer beneath any nightside map"* at ≤ −40 °C. No surface tile carries it, by
design. MEASURED this pass: it already has its
own def — `RUT_LanternDeeps` in `src/RimUtinni/LanternDeeps/Defs/Biomes/RUT_LanternDeeps.xml`
(178 lines), used by name in `Source/DeepFloraPlanter.cs` and `Source/GenStep_LanternstoneRock.cs`
as the pocket map's biome; `CAVERNS_PARITY_BUILD_1` (DONE and deployed 2026-09-19) replaced
the donor `BMT_CrystalCaverns` cave def and its log check recorded that def absent.
`BMT_CrystalCaverns` itself is **UNMEASURED** in the 618-mod def dump (BENCH, 2026-09-20) —
the donor is not in the current load and this spec asserts nothing about it.

| today | target mod folder | packageId | defName | shape |
|---|---|---|---|---|
| `mandrake.rut.lanterndeeps` (`RUT_LanternDeeps`, 117 files) | `LanternDeeps` | `mandrake.rm.lanterndeeps` | `RM_LanternDeeps` | An **injection layer**, not a painted biome: entrance buildings, the pocket-map generator, the layer's own BiomeDef, flora, darkness mechanic, settings. Its host test is TEMPERATURE, not a biome list — that is what makes it RimMandrake-tier. The one Star Wars piece inside it, `Patches/RUT_LanternDeepGateKotorStygium.xml`, stays in Utinni. PROPOSED; §7 Q6 |

**Total with the Deeps: 26 RimMandrake biome mods.**

### 2d. Shared RimMandrake libraries these mods depend on (unchanged by this spec)

`mandrake.rm.environmentalhazards` (the comp/gas/hediff toolkit the kits share, 40+ C#
files), `mandrake.rm.creaturebehaviors`, `mandrake.rm.flowworks` (FloodedCanyon's flood),
`mandrake.rm.weathersuite`. A biome mod depends on these; nothing in them names a biome.
The `RUT_`-referencing extension classes already used inside the biome defs
(`RimMandrake.EnvironmentalHazards.BiomeGlowMultiplierExtension`,
`RimMandrake.CreatureBehaviors.RM_FrontCreepExtension`) are already RimMandrake-tier and
need no move.

## 3. The RimMandrake / Utinni boundary

### 3a. The test

Ask, of each file, def, patch or C# class: **would it make sense, unchanged, on a
randomly generated planet with no Star Wars mod and no Ash'karr loaded?**

- **Yes → RimMandrake.** The biome def, its terrain, plants, weather, game conditions,
  hediffs, mechanics, Mod Settings, and every creature whose own def lives in a
  RimMandrake mod, in vanilla, or in a donor mod referenced with `MayRequire`.
- **No → Utinni.** Anything that names a Star Wars creature or species, a faction, a
  settlement, a landmark, a quest, a tile id, the campaign's word for a thing, or Ash'karr
  itself.

A second, sharper form of the same test, for the borderline case: **if the RimMandrake mod
were uploaded on its own, would this line make the reviewer ask "what is a Kreetle?"** If
it would, the line is a patch.

### 3b. What stays in Utinni, concretely

| Utinni responsibility | where it lives today | what changes |
|---|---|---|
| **Painting the def onto the world** | `world/biome_world_switch_apply.py` (bridge `world_tile_set` + one `world_commit`), the CANONICAL re-save, `world/ASHKARR_WORLDMAP_tiles.csv` + `.frozen.json` re-export | The `MAP` list becomes `RUT_X → RM_X` per §2; the CSV is the paint list's record |
| **Star Wars fauna** | inline in each `RUT_*.xml` `<wildAnimals>` with `MayRequire="mandrake.rsw.swbestiary"` — MEASURED this pass: 102 `RSW_` + 4 `SW_` entries across the 26 defs (RUT_Desert alone carries 50) | Leave the RimMandrake def; land in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as `PatchOperationAdd` onto `/Defs/BiomeDef[defName="RM_X"]/wildAnimals`, same `MayRequire`. `WildAnimals_Pyrelands.xml` is the existing shape |
| **Non-Star-Wars fauna** | the same blocks: 102 vanilla, 90 `AA_` (Alpha Animals, `MayRequire="sarg.alphaanimals"`), 6 `VFEI2_`, 8 `GR_`, etc. | **Stay in the RimMandrake def.** The ruling says *only* Star Wars creatures become patches. Donor retirement (`DONOR_DEFS_PORT_TO_OURS_1`) is a separate stream and is not sped up or slowed by this spec |
| **Campaign labels and descriptions** | `Patches/BiomeNames_Ashkarr.xml`, `Patches/BiomeDescriptions_Ashkarr.xml` | Retarget xpaths at the `RM_` names. The RimMandrake def carries a generic label ("deep desert"); "the Dune Sea" is Tatooine and stays here |
| **Campaign creature defs** (`RUT_FurnaceBeast`, `RUT_Emberscythe`, `RUT_FireHawk`, …) and their `wildAnimals` entries (3 `RUT_` entries measured) | `UtinniPatches/Defs/ThingDefs_Races` | Unchanged, patched in like Star Wars fauna. ⚠️ If one of these is not Star Wars and not campaign-specific it is really a RimMandrake creature misfiled — decide per creature at the move, never in bulk |
| **Doctrine / ambient patches** keyed by biome (`AncientDangerGenSteps_AmbientDoctrine.xml`, `MechClusterBiomes_AmbientDoctrine.xml`, `AnimalTolerances_Ashkarr.xml`, `BiomeCastEvictions_WildBiomes.xml`, `AnimalBiomeDuplicates_*.xml`) | `UtinniPatches/Patches` | Retarget at `RM_` names. `gen_cast_patch.py`'s output regenerates against the new names |
| **World-specific content**: landmarks (`IshkoDarkLandmarks`), settlements, factions, scenario, the Kotor stygium gate on the Deeps | their own `mandrake.rut.*` mods | Unchanged |
| **Trade and economy hooks** (`mandrake.rut.fungalsoiltrade`, trader kinds) | own mods | Unchanged — traders are campaign wiring |

### 3c. Two things that look like Utinni content and are not

- **The mechanics kits.** `mandrake.rut.rotsporekit`, `mandrake.rut.rustcathedralhum`,
  `...roaches`, `...walls`, `mandrake.rut.scarlandsladder` and `mandrake.rut.pyrelandsmechanics`
  are biome mechanics filed at the wrong tier. A spore that rots food, a wall that hums, a
  roach that eats deck plate — none of it needs Star Wars. They fold into their biome's
  RimMandrake mod (§2 table). ⚠️ UNMEASURED whether any of them contains a Star Wars
  reference internally; the move is the moment to check, file by file.
- **The flora.** `mandrake.rut.ashkarrflora` (35 files) is per-biome plant content named
  for the planet. Plants are what a biome IS; the RimMandrake def's `wildPlants` must
  point at defs the same mod ships. §7 Q8 asks the owner whether it splits into the biome
  mods (this spec's recommendation) or stays a campaign pack.

### 3d. The load-order consequence

Every `mandrake.rm.<biome>` mod loads before `mandrake.rut.patches`; the Utinni patches
`loadAfter` every biome mod they touch. A `PatchOperationAdd` onto a def that has not
loaded yet matches nothing and logs nothing (CLAUDE.md) — so the Utinni fauna patches
must be validated with `validate_patch.py --live --defs`, never trusted on a clean log.

## 4. Resolving the four existing orphan mods

Rule applied to every pair: **the RimMandrake mod survives, the RimMandrake defName
survives, and the `RUT_` def's CONTENT is merged into it — then the `RUT_` def is
deleted**, not kept as a stub, not annotated as superseded (CLAUDE.md: inaccurate or dead
material is deleted, git is the provenance). The one thing that is *not* deleted early is
the painted def, for the reason §5's hazard gives — deletion is Phase B step 4.

Active-list state, MEASURED from `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
(618 active, parsed): `mandrake.rm.greentide` and `mandrake.rm.pyrelands` are active;
`mandrake.rm.floodedcanyon` and `mandrake.rm.gelatinousslime` are **not** in that snapshot.
Whether their folders sit in the live Mods directory is UNMEASURED here.

### 4a. Greentide — `RM_Greentide` (123 lines) vs `RUT_Greentide` (287 lines)

- **Survivor:** `mandrake.rm.greentide`, defName `RM_Greentide`, its C# kit
  (`RM_GreentideMod.cs`, churnmud, mired, dig-out, sealant) and its settings screen.
- **Merged in:** the body of `RUT_Greentide.xml` — the sheet-derived terrain ladder,
  plant list, weather table and the two `modExtensions` — replaces the 123-line placeholder
  body of `Defs/BiomeDefs/RM_Greentide_Biome.xml`. Its 27 `wildAnimals` split: 22 vanilla
  + 2 `AA_` + 1 `VFEI2_` stay inline; the 1 `RSW_` and 1 `RUT_` entry go to
  `WildAnimals_Greentide.xml` in Utinni.
- **Deleted:** `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml`, at Phase B step 4.
- Why this way round and not the other: `GREENTIDE_STANDALONE_MOD_1` (closed) already
  ruled the mod RimMandrake-tier on the owner's card; the `RUT_` twin was authored by
  `BIOME_OWNERSHIP_WAVE_1` two days earlier to get the tiles off the donor and never
  reconciled. The content is the `RUT_` file's; the home is the `RM_` mod's.

### 4b. Slime — `RM_GelatinousSlime` (192 lines + 30 defs of kit) vs `RUT_Slime` (105 lines)

- **Survivor:** `mandrake.rm.gelatinousslime`, `RM_GelatinousSlime`. This one is the
  opposite shape to Greentide: the RimMandrake mod is the richer article (slime terrain
  ladder, compressor, gene archive, antidote, four plants, `SlimeMod.cs` settings) and the
  `RUT_` twin is thin.
- **Merged in:** anything `RUT_Slime.xml` carries that the RimMandrake def lacks — compare
  the terrain-by-fertility and weather tables at the move; its 9 fauna entries (7 `AA_`,
  2 `GR_`) stay inline, none is Star Wars.
- **Deleted:** `RUT_Slime.xml`, at Phase B step 4.
- **Retargets:** `TITANOSLIME_SLIME_BIOME_1` says "for `RUT_Slime`"; the Titanoslime is
  not Star Wars, so it is a RimMandrake creature and it is built inside this mod.
  `SLIME_GENE_ARCHIVE_BUILD_1` and `SLIME_STREAM_ROWS_1` likewise land here.

### 4c. Pyrelands — `RM_FE_Pyrelands` (322 lines) vs `ZBiome_Grasslands` (donor def)

- **Survivor:** `mandrake.rm.pyrelands`. The loser is not ours: `ZBiome_Grasslands` is a
  More Vanilla Biomes def and is not deleted, it is simply no longer painted.
- **Deleted from Utinni** the moment the repaint lands: every op targeting
  `ZBiome_Grasslands` — the one op in `WildAnimals_Pyrelands.xml`, all of
  `AshStorms_Pyrelands.xml` (a cosmetic storm bolted onto a donor's intact weather table),
  the `AncientDangerGenSteps_AmbientDoctrine.xml` and `AnimalBiomeDuplicates_*.xml` ops on
  it. They were only ever compensating for the wrong def being on the tiles.
- **Absorbed:** `mandrake.rut.pyrelandsmechanics` (31 files, "biome-aware of BOTH
  defNames") folds into the RimMandrake mod and keys on one name.
- **Two grammar defects to fix at the same move**, both MEASURED in
  `Defs/BiomeDefs/Pyrelands.xml`: the worker is
  `RimMandrake.StarWars.FireEcology.BiomeWorker_Pyrelands` — a `.StarWars.` namespace
  inside a RimMandrake mod — and the `RM_FE_` infix ("FireEcology") on all 22 of its defs
  is a project-name fossil. Renaming to `RM_Pyrelands` before the terminal paint costs a handful of Utinni
  xpath retargets; after it, a save. §7 Q3.
- Which def the live Pyrelands tiles carry today is UNMEASURED here
  (`PYRELANDS_WORLD_SWITCH_1` is closed; `GRASSLANDS_TILES_CSV_STALE_1` is open on exactly
  that row) and it does not matter: Phase B step 1 reads it live and paints the
  RimMandrake def either way.

### 4d. Flooded Canyon — `RM_FloodedCanyon` (109 lines) vs `RUT_CrackedLands` (122 lines)

BENCH's brief listed this mod as an orphan with no twin. It has one. `FLOOD_CANYON_BIOME_1`
(closed) and the mod's own `About.xml` describe it as *"canyons that get periodically
flooded … the Cracked Lands chime mechanic, generalized"*, and `the_cracked_lands.md` is the
sheet for *"canyon country … clay pans split into polygons … then, rarely and without
warning, the water comes down"*. Same place, two defs.

- **Survivor:** `mandrake.rm.floodedcanyon`, `RM_FloodedCanyon` (depends on
  `mandrake.rm.flowworks` for the flood itself — correct, the flood is FlowWorks' liquid).
- **Merged in:** `RUT_CrackedLands.xml`'s terrain, plants, weather; its 10 fauna entries
  split 5 vanilla + 2 `AA_` inline, 3 `RSW_` to `WildAnimals_CrackedLands.xml`.
- **Label:** "the Cracked Lands" is the campaign's name and lives in
  `BiomeNames_Ashkarr.xml`; the RimMandrake label is "flooded canyon".
- **Deleted:** `RUT_CrackedLands.xml` at Phase B step 4.
- This is the one pairing where the owner has not yet said the two are the same thing.
  §7 Q4 asks; until he answers, nothing in §5 runs for this biome.

### 4e. Not a twin — the Lantern Deeps

`RUT_LanternDeeps` has no `RM_` counterpart; the whole `mandrake.rut.lanterndeeps` mod
changes tier (§2c). Nothing is deleted; the Kotor stygium gate patch is carved out into
`UtinniPatches/Patches` and the rest is `git mv`'d to `src/RimMandrake/LanternDeeps` with
its packageId, namespace and defNames renamed. Its allowlist checks name
`RUT_NightsideIce` and `RUT_PropaneLake` (`About.xml` line 35, `validation.py` line 83)
and must follow §2's renames — but note the FROZEN sheet says the host test is
temperature, so a biome allowlist in the code is already a departure to look at while
there.

## 5. Migration sequence

**Owner, 2026-09-20, verbatim:** *"Don't worry about worldmap painting. Once we have all
the biomes in mods we will do the painting once and for all."*

So the sequence has two phases and the second happens once. **Phase A builds every
RimMandrake biome mod; nothing in it touches the world.** **Phase B paints the world once,
then deletes the `RUT_` defs.** No biome's migration is gated on its tiles, and no tile
count decides what is done first.

### Phase A — build all 26 mods (per biome, no world contact)

1. **Scaffold the RimMandrake mod** (new folders only; the four existing ones skip this):
   `About/About.xml` with `mandrake.rm.<name>`, `loadAfter` on the shared libraries §2d
   names, a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`. A deployed biome mod that
   the world does not yet carry is the expected state (`WORLD_REMAKE_FINAL_STEP_1`).
2. **Copy the content into the RimMandrake mod** — the `BiomeDef` as `RM_X`, its terrain,
   plant, weather, condition and hediff defs, textures, the kit C# under namespace
   `RimMandrake.<Mod>`, and the absorbed `mandrake.rut.*` kit mods (§3c). Every
   `RSW_`/`SW_`/`RUT_` creature entry in `<wildAnimals>` is left out of `RM_X` and written
   into `UtinniPatches/Patches/WildAnimals_<Biome>.xml` targeting `RM_X`. Every donor-class
   `workerClass` (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`,
   `BiomeWorker_CypreJungle`) becomes the mod's own `RM_BiomeWorker_<X>` — a donor type in
   `workerClass` is a hard dependency the RimMandrake tier may not assume (inert on
   Ash'karr either way, §1).
3. **Freeze the `RUT_X` def, do not delete it.** It is what the player's world carries
   until Phase B, so it stays byte-for-byte as it is, with one header comment: *"carrying
   the world until the terminal paint; content lives in `mandrake.rm.<name>`; do not edit
   here."* From this moment every content fix for the biome lands in `RM_X` only.
   ⚠️ This is a deliberate, bounded duplication and the one exception to "delete, never
   supersede": the copy exists because deleting the painted def before Phase B destroys
   the save (see the hazard below), and it is scheduled for deletion at Phase B step 4.
   `.claude/hooks/queue_lint.py`-style WARN on any edit under
   `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/` would enforce it; that is a tooling
   item, not this spec.
4. **Retarget what can be retargeted now** — references whose target does not need to be
   on the world: kit specs, `_def_bindings_*.md`, queue items, `validation.py`
   `QUALIFYING_BIOMES`, the kit C# string constants. References that must keep working on
   the live world (`BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`, doctrine
   patches, `race/wildBiomes` on animal defs, `gen_cast_patch.py` output) get a **second**
   op for `RM_X` beside the `RUT_X` one, so both defs behave identically until Phase B.
5. **Prove `RM_X` loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   all five expansions (`rimworld-load-round`; every test list carries every expansion,
   owner 2026-09-19). Zero new Config errors; `validate_patch.py --live --defs` on the new
   Utinni fauna patch (an unmatched `PatchOperationAdd` is silent). A quicktest map on a
   scratch world whose landing tile is set to `RM_X` through `jawa/world_*` at
   `Page_SelectStartingSite` (`rimworld-world-editing`) — never the canonical save.
6. **Commit and push**, explicit paths, one commit per biome, the message naming the twin
   that was wrong. Item per biome: `<BIOME>_RM_MOD_BUILD_1`. Append the mod and its
   `RM_X` to the paint list on `WORLD_REMAKE_FINAL_STEP_1` as each one closes.

**Order within Phase A:** the four existing mods first (Greentide, Slime, Pyrelands;
Flooded Canyon once §7 Q4 is answered), because their twins are the double-maintenance
costing now; then the rest in whatever order the kit work is already moving. The Lantern
Deeps (§2c) is a tier move with no `RUT_` twin — it does its steps 1, 2, 4, 5, 6 and skips
3.

### Phase B — paint once, then delete (one sitting, once)

Runs when the paint list on `WORLD_REMAKE_FINAL_STEP_1` has all 26 rows closed. It may be
the world remake's last step or its own bridge sitting; either way it happens once.

1. **Repaint the whole planet** with `world/biome_world_switch_apply.py` and a `MAP` of
   every `RUT_X → RM_X` pair (plus `ZBiome_Grasslands → RM_Pyrelands` if a live read shows
   the Pyrelands tiles still carry the donor — read it then, do not assume it): batches,
   getter read-back, one `world_commit`. Biome before links (a repaint over a river hides
   it, `rimbridge/references/world-authoring.md`).
2. **CANONICAL re-save** with the Saves-folder backup and the stat-after check — a NEW
   file appeared and no existing file changed size; `rimworld/save_game` has written the
   wrong slot before. Re-export `world/ASHKARR_WORLDMAP_tiles.csv` and re-stamp
   `.frozen.json` in the same commit. The CSV is a record of the planet, never a rival to
   it: after this step it records `RM_` names.
3. **Verify by live read**, not by CSV: `jawa/world_tile_export`, zero tiles carry any
   `RUT_` biome or `ZBiome_Grasslands`, 21,872 of 21,872 tiles carry an `RM_` biome. Say
   the count.
4. **🔴 Delete the `RUT_` biome defs** — `git rm` all 26 files under
   `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml`, and every duplicate `RUT_X` op
   left by Phase A step 4, and every `ZBiome_Grasslands` op (§4c). Only now.
5. **Full-list cold load** (~15 min on ~600 mods) and load the re-saved canonical save:
   zero `Could not load reference to`, zero new Config errors. The pocket-map biome
   (`RM_LanternDeeps`) is exercised by entering a Deep in play.
6. Commit and push; close `WORLD_REMAKE_FINAL_STEP_1`'s paint list.

### 🔴 The hazard — where it bites and why the order above is the cure

The frozen save stores biomes as `tileBiomeDeflate`, a DEFLATE grid of **2-byte def
shortHashes**, not names; a pocket map stores its biome the same way. A biome defName that
no longer exists resolves to nothing — `Could not load reference to`, the Scribe error no
mod change fixes (`rimworld-savegame` skill) — and **every tile carrying that hash is lost
on load.** It bites at **Phase B step 4**, and only there: deleting a `RUT_` def while any
live save still carries its hash. Phase A step 3 (freeze, don't delete) and the B1→B2→B4
order exist for this reason and no other. A repaint through the bridge writes the new
hashes correctly; only the old save files carry the old ones, and after B2 no live save
does. Archived `world/*.rws` copies keep old hashes and are history, not live articles.

### What the sequence deliberately does NOT do

- It does not repaint per biome, and it does not use any tile count to schedule work.
- It does not migrate colony state, placed things or research — `WORLD_REMAKE_FINAL_STEP_1`
  says those regenerate.

## 6. Mod Settings and feature gating

Owner, 2026-09-12 (`MOD_OPTIONS_RETROFIT_1`): every mod ships a real settings screen —
on/off per major feature, tuning where a number is the experience, defaults = shipped
behaviour, all-off degrades gracefully, and **biome-kit mechanics are feature-gated so they
can be enabled in other biomes WITHOUT the biome.**

### 6a. What every biome mod's screen carries

MEASURED reference implementations already in the repo: `RM_GreentideMod.cs`
(`crossBiomeEnabled` / `crossBiomeEverywhere` / `crossBiomeBiomeList` /
`crossBiomeCoverage`, with `RM_MapComponent_CrossBiomeChurnmud` honouring them),
`SlimeMod.cs` (`SlimeSettings`), `RM_PyrelandsMod.cs` (`RM_PyrelandsSettings`),
`LanternDeepsMod.cs` (`LanternDeepsSettings` — per-entrance toggles and rates, darkness
sensitivity), `RM_EnvironmentalHazardsMod.cs` (`RM_EnvironmentalHazardsSettings`). The
Greentide shape is the template; the others conform to it.

| section | contents | default |
|---|---|---|
| Master | the mod on/off (the biome def still loads; the mechanics stop) | on |
| Per mechanic | one toggle per mechanic the kit spec names (churnmud, wet-bulb, the Roil, ash fall, the hum, the ladder …) | on |
| Tuning | the one or two numbers that ARE the experience per mechanic (coverage, severity, rate) | shipped value |
| **Cross-biome** | `enabled` · `everywhere` · a biome-defName allowlist · coverage — lets the mechanics run on maps whose biome is not this mod's | off |
| Map-gen note | any toggle that only takes effect on a NEW map is labelled so in the UI (the campaign is a frozen world; nothing here regenerates the planet) | — |

For a two-biome kit (§2b) the screen has one master and a per-biome section for the
mechanics that belong to one of the two.

### 6b. How gating shapes the split — three consequences

1. **A mechanic is gated at the comp / MapComponent / patch level, never at the def.** The
   mechanics never test `map.Biome == RM_X` directly; they test a settings-derived
   predicate *"does this mechanic run on this map?"* whose default answer is "yes on
   `RM_X`, no elsewhere". That is what makes the cross-biome allowlist possible, and it is
   also what makes the biome def itself a plain data file the Utinni layer can paint
   without owning any behaviour. `PatchOperationSettingGate.cs` (already in
   `UtinniPatches/Source`) is the XML-side form of the same idea.
2. **This decides what is "the biome" and what is "the kit".** Everything that only
   makes sense on this terrain — the terrain ladder, the plant list, the weather table —
   is the biome and lives in the def. Everything that could plausibly run on someone
   else's map — a fog that bites, a mud that swallows, a spore that rots stock — is the
   kit and lives behind a toggle. A biome mod is exactly one def plus one kit plus one
   screen; the split in §2 follows because a kit spec (`kits/*.md`) exists per biome, not
   per family.
3. **The Utinni layer gets no settings of its own for biomes.** Painting is not a
   setting, and Star Wars fauna patches are content, not options. If the campaign ever
   wants a kit mechanic somewhere other than its home biome (the Deeps' darkness on the
   Nightside Ice surface, say), that is a shipped DEFAULT written into the RimMandrake
   mod's settings by the Utinni scenario, not a `RUT_` copy of the mechanic.

### 6c. What "all-off degrades gracefully" means for a biome mod specifically

With every toggle off the biome still loads, generates, and plays as terrain + plants +
weather with no scripted hazard — a normal RimWorld biome. No NRE, no orphaned def, no
missing texture: the def never references a comp that a toggle can remove, because toggles
remove behaviour, not defs. This is the bar `MOD_OPTIONS_RETROFIT_1`'s verify line sets
("toggling a feature off provably disables it live or at next map-gen, say which"), and
each biome mod's `validation.py` states which of the two it is per toggle.

## 7. Owner rulings, and what is still open

🔴 **Ruled 2026-09-21 (BENCH question cards). These are decisions, not recommendations.**

**Q1 — the two kits: RE-SCOPED by his answer, verbatim.**

> *"Umbra is a region not a biome. The Propane Lake is an ocean-biome made of propane,
> definitely its own biome. Propane, Grey, Twilight, and Scald biomes can all share one
> mod with options to enable/disable each of these biomes in a spawned game... or Utinni
> scenario simply uses a painted world."*

⇒ **Umbra is NOT a biome** and leaves the biome row list entirely — it is a region, and
belongs with the planet's named regions. ⇒ The **Propane Lake is its own biome**, an ocean
biome made of propane. ⇒ **Propane + Grey + Twilight + Scald ship as ONE mod carrying four
biomes**, each with a Mod Settings toggle to enable or disable it in a generated game
(per the standing "every mod ships superb Mod Settings" ruling). The Utinni scenario is
unaffected either way because it uses the painted world.
⛔ The spec's original `mandrake.rm.propanelakes` / `mandrake.rm.terminalseas` pairing is
dead — do not build it.

**Q2 — names for the two deserts and the shrubland: DRAFTS OWED HIM.** He ruled *"bring me
a drafted list"*; the drafts are at `Transient/biome_name_drafts_2026-09-21.md` awaiting
his pick. Nothing depending on a name starts until he picks.

**Q3 — rename `RM_FE_Pyrelands` → `RM_Pyrelands`: YES, NOW.** Ruled. Item:
`PYRELANDS_DEFNAME_RENAME_1`.

**Q4 — is `RM_FloodedCanyon` the Cracked Lands? YES, same place.** `RUT_CrackedLands`
merges into the RimMandrake mod under the campaign label "the Cracked Lands". One biome,
one mod. The Cracked Lands does NOT get its own row.

**Q5 — "Scarlands" collides with vanilla: RENAME OURS.** Not the DLC's label, not keeping
the name. Item: `SCARLANDS_RENAME_OURS_1`; replacement drafts are in
`Transient/biome_name_drafts_2026-09-21.md` awaiting his pick.

**Q8 — `mandrake.rut.ashkarrflora`: DISSOLVE IT.** Each plant moves into the RimMandrake
mod of the biome whose `wildPlants` lists it, renamed `RM_`. Every biome mod ships with its
own signature plants. The campaign flora pack does not survive the split.

**Q9 — donor fauna inline in RimMandrake defs: ACCEPTABLE, leave them inline.** The `AA_`,
`VFEI2_`, `GR_` and other donor entries stay in the `RM_` defs with their `MayRequire`;
`DONOR_DEFS_PORT_TO_OURS_1` removes them over time. No extra work at the split.

**Q6 — the Lantern Deeps' def and tier: MOVE IT UP.** The whole mod becomes
`mandrake.rm.lanterndeeps` with the def renamed `RM_LanternDeeps`; only the Kotor stygium
gate patch carves back out to Utinni. (Q6b — allowlist vs temperature test — was already
settled by a closed item and was never his to answer.)

**Q7 — the two-def window: ADD A WARN HOOK.** For the duration between the split and the
final paint, a hook WARNs on any edit under `UtinniPatches/Defs/BiomeDefs/`. Not a hard
block — an emergency correction to a frozen def must stay possible. ⚠️ Note for whoever
builds it: a WARN hook's output goes to the OWNER's screen, not to an agent's — an agent
never sees it fire, so the hook is a guard for him, not a check an agent can rely on.

**Q10 — the seven misfiled creatures: ALL SEVEN MOVE TO RIMMANDRAKE.** `RUT_FurnaceBeast`,
`RUT_FireHawk`, `RUT_Emberscythe`, `RUT_FireWasp`, `RUT_Flamefang`, `RUT_Barbslinger` and
`RUT_Sytheclaw` each move into their biome's RimMandrake mod, renamed `RM_`. One sweep, not
a per-creature call. None has a canon-library entry and each is a campaign-original
re-authoring, so none of them is Star Wars content.

### Nothing is open

🔴 **All ten questions in this section are RULED as of 2026-09-21.** Q2 and Q5 await only
his pick from `Transient/biome_name_drafts_2026-09-21.md`; every other row can start.
