# The Cauldron (shipping as Poison Forest) — bedazzle review, 2026-09-28

Movement 1–2 of the bedazzle ritual (`BAROQUE_BEDAZZLE_PROGRAM_1`). Biome lives under TWO
names: shipping mod `PoisonForest`, owner-typed ruling 2026-09-27 renames it **The Cauldron**
(rename executed at this sitting, censused below — NOT executed by this review).

## What's there

**Item:** CAULDRON_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 5)
**Author:** DESIGN subagent (Fable), movement 1–2 pass. Sources read this pass:
`src/RimMandrake/PoisonForest/` (all defs + C#), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PoisonForest.xml`, both Utinni patches,
`rosters/poison_forest.json`, the frozen sheet `poison_forest.md`,
`noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md` Batch 4a,
artpipe `registry.jsonl`/`done/`/`_artsrc/`.

### BiomeDef(s)

Two, deliberately (twin architecture, `biome_mod_architecture.md` §5):

- **`RM_PoisonForest`** — label already reads **"the Cauldron"** (the label was renamed
  ahead of the defName; the defName, folder, packageId etc. are the rename census below).
  `src/RimMandrake/PoisonForest/Defs/BiomeDefs/RM_PoisonForest.xml`. Ships in
  `mandrake.rm.poisonforest` ("RimMandrake: Poison Forest"), built 2026-09-25
  (`POISONFOREST_RM_MOD_BUILD_1`). animalDensity 0.8, plantDensity 0.5, Fog-dominated
  weather, 8 vanilla diseases, own worker `RM_BiomeWorker_PoisonForest`.
- **`RUT_PoisonForest`** — the frozen campaign twin (byte-frozen, serves the live world).
  Same content plus the 5 Star Wars rows inline. Not this sitting's to edit except via the
  ruled rename ticket (live-tile/savegame check gates any defName change).

⚠️ Disclosed in About.xml and real: the RM mod is **NOT donor-free** — the worldmap
texture (`Biomes/PoisonForest`, BiomesPlus) and 7 Alpha Biomes wildPlants rows carry no
MayRequire.

### Flora roster (def + patch-added, merged)

No Utinni flora patch exists for this biome — flora is all inline on the RM def
(shorthand `<DefName>commonality</DefName>` form, parsed as such):

| def | comm | provenance |
|---|---|---|
| `RM_TwistingThornwood` | 0.6 | OURS — dup of RUT_ original (also serves RUT_CrackedLands), tree, WoodLog |
| `RM_TreeMartyr` | 0.5 | OURS — dup, "weeping" yucca-form tree, WoodLog |
| `RM_DarkCrust` (vein moss) | 0.25 | OURS — black/purple/red phototroph film, the sheet §4 underclass made real |
| `AB_CrystalFlower` | 0.5 | Alpha Biomes donor, no MayRequire |
| `AB_BloodBouquet` | 0.4 | donor |
| `AB_RavenNettle` | 0.4 | donor |
| `AB_GiantAgariTox` | 0.3 | donor tree |
| `AB_RedBugloss` | 0.3 | donor |
| `AB_KeeningCordax` | 0.2 | donor tree |
| `AB_GiantToxicFlower` | 0.08 | donor (owner move 2026-09-20, wasteland → here) |

Note: both owned trees still yield plain `WoodLog` — the sheet's §7 "old trunks assay
richer than the rock" (bio-accumulated metal, the biome's stated reason to exist) has no
def expression anywhere. See scorecard mark 3 and slate candidate B.

### Fauna roster (def + patch-added, merged)

RM def inline (14 rows) — parsed from the element form, not `<li>`:

| def | comm | note |
|---|---|---|
| `RM_Suush` | 0.2 | OURS — floating shot-detonating drifter, built 2026-09-26 with real art (`SUUSH_CAULDRON_DRIFTER_1`, closed) |
| `GR_Beetlefleet` | 0.7 | VGE chimera, pops on death |
| `AA_InfectedAerofleet` | 0.5 | Alpha Animals |
| `AA_OcularJelly` | 0.5 | eye-heavy signature |
| `AM_Dryad_Corruptor/Ocular/Tumorous` | 0.4×3 | Alpha Memes; wild-function still UNMEASURED per roster confidence block |
| `Visceral` | 0.35 | Horrors, sealed insectoid |
| `AA_BedBug` | 0.3 | paralysing ambusher |
| `AA_CrystalMit` | 0.15 | crystal-fan match |
| `AA_GiantCrownedSilkie` | 0.15 | silhouette eye-test still owed (roster note) |
| `AA_DecayDrake` | 0.1 | |
| `AA_Helixien` | 0.1 | GIANT band, spd 0.6 gas-form decayer |
| `AA_Wildpod` | 0.05 | GIANT band, venomous |

Patch-added (`UtinniPatches/Patches/WildAnimals_PoisonForest.xml`, one
PatchOperationConditional op targeting `Defs/BiomeDef[defName="RM_PoisonForest"]/wildAnimals`,
gated `mandrake.rsw.swbestiary` — read from the op's own xpath+value):
`RSW_Neebray` 0.8 · `RSW_Mynock` 0.2 · `RSW_GraniteSlug` 0.15 (the sheet's only legal
herbivore — mineral-rasper) · `RSW_Screecher` 0.35 (**multi-homed ON PURPOSE** — owner
2026-09-22, migrates here↔Wasteland to lay; do not "fix") · `RSW_VentStalker` 0.25
(OURS — the sheet's §4 signature "eyeless vibration-sensing ambusher", built via
Kinrath-body reuse, `COMMISSION_LEDGER_CLEANUP_1`).

**Campaign cast: 19 wired species; RM-standalone cast without any donor present: 1
(the Suush).** See roster gaps.

**Roster-vs-wiring gap (adjudicate at the sitting, no action taken):**
`rosters/poison_forest.json` carries 7 owner-ruled "round2 move mapping" imports that are
wired NOWHERE (neither twin nor patch): `Lylek` (apex 0.05), `AA_Plasmorph`, `AA_LuciferBug`,
`AA_Radyak`, `AA_RipperHound`, `Skalder` (huge-grazer 0.08), `Silooth`. Two internal
contradictions inside the roster itself: `AA_RipperHound` is BOTH evicted (ban 9, spd 5.5
MEASURED) and imported; `Skalder` is a huge-GRAZER import into a biome whose frozen sheet
§6 hard-bans open grazing body plans ("there is nothing to graze"). These look like
homeless-disposition rows that predate the freeze discipline — the sitting should rule
wire-or-strike per row rather than anyone bulk-wiring them.

### Terrain

`RM_PoisonSoil` (fertility 0.85, pathCost 3) and `RM_PoisonSoilRich` (fertility 1.2) —
net-new owned TerrainDefs replacing the twin's phantom BiomesPlus terrains; reuse vanilla
Soil/SoilRich textures, zero terrain art of their own. Marsh for lake beach/mud,
vanilla Riverbank. No unique visible ground yet — the "mineral rings and beaded
condensate" of the sheet is unexpressed.

### Weather

Live block on both defs: **Fog 90 · DryThunderstorm 1 · everything else 0.** That is a
donor placeholder wearing a ruled biome's clothes. The four weathers were **RULED and
ratified by owner card 2026-09-12** (sheet §4b): **scatter-dusk** (the standing state) ·
⭐ **vent bloom** (venting surge, toxic buildup outdoors, the signature hazard) ·
**vapour bank** (chemical fog) · **dewfall** (the only "precipitation"; every wet surface
is a dosed surface). Def work explicitly unblocked since 2026-09-12 and **zero WeatherDefs
exist in `src/`** (checked this pass). This is the single largest ruled-unbuilt gap.

### Mechanics / C#

`RM_PoisonForestBiome.cs` — worldgen worker + ranges extension only.
`RM_PoisonForestMod.cs` — Mod Settings, one rarity slider; its own header states it
plainly: *"No mechanics kit exists for this biome yet."*
Creature-level mechanics that DO exist: the Suush's `CompProperties_Explosive`
(startWickOnDamageTaken Bullet/Bomb, ToxGas post-explosion, explodeOnKilled) + core-1.6
flight fields; the VentStalker's dormant-ambush pair (CanBeDormant/WakeUpDormant).
Utinni side: the toxic-prized-meat chain IS built — `PoisonForest_ToxicPrizedMeat.xml`
points Neebray/RSW_Screecher/Visceral/AA_Helixien at 4 hand-authored `RUT_*Meat` defs
(`RUT_PoisonForestPrizedMeats.xml`).

### Art status per cast member

From `artpipe/registry.jsonl` + `done/` + `_artsrc/` (checked before any re-queue,
per the standing rule):

| subject | status |
|---|---|
| Suush (3 facings, `cauldron_suush_*`) | **DONE + validated + deployed** into the mod |
| RM_TwistingThornwood (`twistingthornwood_v1`) | done/validated; mod ships `_a`+`_b` PNGs |
| RM_TreeMartyr (`martyr_v1`) | done/validated; mod ships `_a`+`_b` |
| RM_DarkCrust (`rutdarkcrust_v1` in `_artsrc/`+`done/`) | done; deployed as `RM_DarkCrust_a` |
| AB_* flora ×7 (`crystalflower_v1`, `bloodbouquet_v1`, `ravennettle_v1`, `redbugloss_v1`, `keeningcordax_v1`, `giantagaritox_v1`, `gianttoxicflower_v1`) | **all generated+validated** — replacement art already exists for every donor flora row, unwired |
| RSW_VentStalker | rides Kinrath's generated art (`kinrath_v1`/`canon_kinrath_v1` confirmed real) — retint, deliberate |
| RSW_Screecher / Neebray / Mynock / GraniteSlug / Skalder | own art in SWBestiary / `desert_swaca_*` jobs done |
| Donor fauna (AA_/AM_/GR_/Visceral) | donor mods' own art; none of ours queued |

⛔ Nothing in this table may be re-queued at movement 4. The validated AB_-replacement
flora set is the interesting find: **the divergence art for the donor flora already
exists** and is sitting unused — wiring it to owned defs is a build ticket, not an art ask.

## Nine-mark scorecard

PENDING

## Roster gaps

PENDING

## Rename census (PoisonForest → Cauldron)

PENDING

## Candidate mechanics slate

PENDING
