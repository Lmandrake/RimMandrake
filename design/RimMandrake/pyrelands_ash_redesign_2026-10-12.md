# Pyrelands ground: deep ash everywhere, and the burn feeds the field (2026-10-12)

Item: `PYRE_ASH_REDESIGN_BURN_FEEDS_THE_FIELD` (replaces `ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP`).
Build item for FOUNDRY: `PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED`.

## The ruling

Owner, 2026-10-12, verbatim: *"the Pyrelands have burned for milennia, so most places should
already have deep ash. Very little should be otherwise. But the ash should be QUITE fertile with
water added, so it shouldn't be "dead ash" in the sense of lack of fertility. I'm not certain in the
Pyrelands watching the transformation of soil to ash is really a mechanic we need? ... this feels
like a mechanic intended to turn non-Pyreland into Pyreland."*

He then picked this by card (*Ash: what should Pyrelands ground do? → Deep ash everywhere +
fresh-burn bonus*). It means:

- most ground starts as deep ash;
- the ash is fertile when it is watered;
- a new burn leaves a short fertility bonus that rain fades, so burning on purpose pays;
- the soil → trace → light → heavy → deep ladder is removed.

Every number below is **PROVISIONAL**. Each one is a Mod Setting and gets tuned in a walk.

## 1. Terrain set after the change

| def | role | fertility (XML) | flammable | burnedDef | pathCost | Beauty |
|---|---|---|---|---|---|---|
| `RM_FE_Ash_Deep` | **the Pyrelands ground** | 0.40 (dry) | no (0) | none | 2 | 0 |
| `RM_FE_Ground_Soil` | rare unburned pocket | 0.70 (unchanged) | yes | **`RM_FE_Ash_Deep`** | unchanged | unchanged |
| `RM_FE_Ground_SoilRich` | the ring around standing water | 1.40 (unchanged) | yes | **`RM_FE_Ash_Deep`** | unchanged | unchanged |
| `RM_FE_Ground_Sand` | lake beach | 0.05 (unchanged) | yes | **`RM_FE_Ash_Deep`** | unchanged | unchanged |
| `RM_FE_Ground_Gravel` | gravel / rocky margin | 0.28 (unchanged) | yes | **`RM_FE_Ash_Deep`** | unchanged | unchanged |
| `RM_FE_FirebreakLine` | unchanged | 0 | no | none | — | — |

The changes to deep ash:

- Its description loses "dead … nothing grows through it". New text: *"Ash laid down by a thousand
  years of burning, fine and black. Dry, it feeds little; watered, it grows almost anything."*
- `pathCost` drops from 16 to 2 and `Beauty` from -10 to 0. It is now the ordinary ground of a
  whole biome. A walking penalty and a mood penalty on every cell would punish standing in the
  biome at all. The drag a fresh fall puts on a walker stays with the loose-ash filth
  (`RM_FE_Filth_LooseAsh`), which is unchanged.

**Retired:** `RM_FE_Ash_Trace`, `RM_FE_Ash_Light` and `RM_FE_Ash_Heavy`. A burn is now ONE step:
an unburned pocket goes straight to deep ash. Deep ash is not flammable, so `Fire.TryBurnFloor`
has nothing left to escalate. That makes the one-fire-goes-deep cascade measured in
`ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP` structurally impossible.

Removing the rungs has a side effect worth having. The four "burnedDef is flammable" config
errors that `ScorchableGround.xml` and `AshLadder.xml` call expected **disappear**, because the
burn target is no longer flammable. So:

- the allowlist entries for them in the log-clean bar are retired;
- the `⛔ DO NOT "FIX" THIS` comment in `ScorchableGround.xml` is deleted.

## 2. How the biome paints deep ash

Everything happens in `BiomeDefs/Pyrelands.xml`. Mapgen stays XML.

- **`terrainsByFertility`:** `RM_FE_Ground_Gravel` for fertility noise below 0.10, and
  `RM_FE_Ash_Deep` for everything above 0.10. Sand and Soil leave this list.
- **Patchmaker 1** (the old "burn scars" patchmaker, whose comment says *"Deep ash is
  deliberately absent"*) is **replaced** by an "unburned pocket" patchmaker:
  - `RM_FE_Ground_Soil` for noise 0.88–0.96;
  - `RM_FE_Ground_Gravel` for noise 0.96 and up.
- **Patchmaker 2** (standing water with its `SoilRich` / `Mud` ring) is unchanged.
- `lakeBeachTerrain` (Sand) and `gravelTerrain` (Gravel) are unchanged.

**Target:** deep ash is at least 85% of open land cells (not rock, not water) on a fresh map.
This is PROVISIONAL and is read by bar `pyre_ground_deep_ash` below.

Players never generate a world: the planet is painted once at the end. That does not affect
this change, because this is per-map terrain laid at landing, not planet painting.

## 3. Dry and watered fertility

### What "watered" means

The Pyrelands has no ordinary rain (biome ban #2). Black Rain is *"non-hydrating"*
(`design/Jawa/proposals/fire_ecology_deep_design.md`). So water arrives only on purpose, or from
standing water.

The project already has an irrigation rule, so this design reuses it. That rule lives in
`src/RimMandrake/ExplosiveGrowth/Source/RM_SoakSources.cs`. FlowWorks' own header names it
(*"irrigation wants a per-cell soak map"*). The rule:

- A **FlowWorks dug cell holding a qualifying fresh fluid waters itself and its 8 neighbours.**
- Natural liquid reads as SUPERDEEP with depth-grid 0 and is **not** irrigation.

Pyrelands reads FlowWorks the same reflection-soft way. FlowWorks is not a dependency; when it
is absent, this route is silent. The builder lifts the cell rule into one shared helper that both
mods call, rather than copying it.

A second route covers natural water: a deep-ash cell **within 2 cells of any water terrain**
(including `Mud` and riverbank) counts as watered. That gives a river or lake a green margin
without painting it.

Black Rain does **not** water the ground; it fades the burn bonus (§4).

### Numbers (PROVISIONAL)

| ground state | fertility |
|---|---|
| deep ash, dry | **0.40** — sparse crops; fine for wild embergrass (`fertilityMin` 0.08) |
| deep ash, watered | **1.40** — equal to rich soil: "QUITE fertile" |
| either, plus a fresh-burn bonus | **+0.50** at the moment of the burn, fading to 0 (§4) |
| hard cap | 2.0 |

### Mechanism

1. The XML `fertility` of `RM_FE_Ash_Deep` is the dry value, 0.40. If the patch is off or fails,
   vanilla reads a sane value.
2. A `RM_AshFieldExtension` (DefModExtension) on `RM_FE_Ash_Deep` carries `wateredFertility`.
   It lives in data, so another biome can opt its own ground in.
3. A Harmony **postfix on `FertilityGrid.CalculateFertilityAt`**:
   - Vanilla computes fertility fresh on every call and never caches it
     (`Source/RimWorld/FertilityGrid.cs:44`, RimSage). Vanilla returns an edifice override first,
     then terrain fertility, then the Biotech pollution cap.
   - The postfix acts only when the cell's terrain carries the extension and no edifice overrides
     it. It then returns the watered value or the dry value, plus the burn bonus, capped.
   - Plant growth (`Plant.GrowthRateFactor_Fertility`), sowing and the fertility overlay all read
     this one method, so every reader agrees.
4. The watered state lives in an unsaved per-map `BoolGrid`, rebuilt by a sliced sweep: 8 passes,
   the same cadence as `RM_SoakSources`. Each irrigated cell stays watered for one day after its
   last read, matching the soak's day.
5. When the grid changes, the fertility overlay drawer is marked dirty.

**Readable sign.** The inspect pane of a deep-ash cell shows `watered` and `fresh burn +0.32
(3 days)`. Nothing changes fertility silently.

## 4. Fresh-burn bonus

**How it is stored.** A per-cell `int` grid of "last burned tick" (saved; 62,500 ints on a
250×250 map) plus one per-map rain accumulator `R` (saved; a float). Both live in a new
`MapComponent_PyrelandsAshField`. It may fold into `MapComponent_BurnLine`, which already pays for
a Pyrelands map check, a tick gate and a save block.

**How a burn is stamped.** `Patch_FireTick_AshAndScorchFruit` already postfixes
`Fire.TickInterval` on every ground fire. It writes `burnTick[cell] = now` and
`rainAtBurn[cell] = R`. That needs a second grid, or both values packed into one long.

🔴 **Its terrain gate must widen.** `IsScorchableGround` admits only `RM_FE_Ground_*`. Once the
map is nearly all `RM_FE_Ash_Deep`, the existing ash-dusting and scorch-fruit rolls (and this
stamp) would stop on 85% of the biome. The gate becomes "is Pyrelands ground", i.e. starts with
`RM_FE_`, excluding the firebreak. This is the one regression the build must test for.

**Duration.** The bonus falls linearly from +0.50 to 0 over **6 days** (PROVISIONAL), counted
from the last fire tick on the cell. A cell burned again restarts at full.

**Rain fade.** Every 250 ticks, `R += curWeather.rainRate × hours`. In this biome that is
effectively only Black Rain. The bonus is:

`base × max(0, 1 − age/duration − (R − rainAtBurn)/rainBudget)`

with `rainBudget` = **12 rain-hours at rainRate 1** (PROVISIONAL). So a long Black Rain strips a
scar's bonus. This is O(1) per query and needs no sweep.

Accepted simplification: roofs are ignored for the fade. A fresh burn under a roof is rare;
this is documented in the class comment.

**Why burning is now the player's tool.** Firing a field just before sowing gives about six days
of +0.5 on top of whatever water gives. Players time burns between Black Rains.

## 5. Mod Settings

The new settings, added to `RM_PyrelandsSettings` under one "Ash field" section:

| setting | default | when off / meaning |
|---|---|---|
| `ashWaterFertilityEnabled` | true | off: deep ash is dry fertility everywhere |
| `ashDryFertility` | 0.40 | tuning |
| `ashWateredFertility` | 1.40 | tuning |
| `ashNaturalWaterRadius` | 2 | 0 = only irrigation waters |
| `freshBurnBonusEnabled` | true | off: no bonus, no stamping |
| `freshBurnBonus` | 0.50 | tuning |
| `freshBurnDays` | 6 | tuning |
| `rainFadesBurnBonus` | true | off: the bonus fades by time only |
| `rainFadeBudgetHours` | 12 | tuning |

- With everything off, deep ash reads its XML 0.40 and the rest of the mod is untouched.
- None of these affect worldgen. The mapgen painting is XML, not a toggle.
- `ashDryFertility` is written to the def at startup, so vanilla readers agree with it.

## 6. What is retired, and what replaces it

**Defs and code**

- `Defs/TerrainDefs/AshLadder.xml`:
  - Trace, Light and Heavy are deleted.
  - Deep stays, with the stats in §1 and the extension.
  - The file is renamed to `AshField.xml`, and its header comment (the ladder, the "burnedDef is
    flammable" warning, the driesTo note) is rewritten to describe this design.
- `ScorchableGround.xml`: every `burnedDef` points to `RM_FE_Ash_Deep`, and the expected-warning
  comment is deleted.
- `BiomeDefs/Pyrelands.xml`: the painting in §2. Fix the plant-density comment that cites "light
  ash (0.25)" and "deep ash stay bare", and the fertility-ignored comment that cites "the ash
  ladder's fertility rungs".
- `EmberGrass.xml`: delete the header lines 15–16 and 50–53, which say it "stops at heavy ash
  (0.05) and deep ash (0.0)".
- `RM_FireEcoKernel.RuinScorchRung` (heavy footprint, light rim): the ruin sweep lays deep ash
  plus loose-ash filth on the footprint. That cell is usually deep ash already, so the filth is
  the visible scorch. Fix `FireEcologyHook.cs:482/524`, which reads Light/Heavy.
- `RM_Ullai.xml:95–98` graze-terrain list and `Patches/RM_AcousticPayload_Pyrelands.xml:46–47`:
  drop the retired rungs.
- `MapComponent_BurnLine.cs:55` says *"Ash terrain never reverts (AshLadder.xml), so terrain
  alone cannot say which black is fresh"*. Correct it to point at the new burn-tick grid. The
  ullai "graze where it burned two days ago" may read that grid in place of the hourly centre
  sample (optional; keep the behaviour).
- `Filth_LooseAsh.xml`, `preflight_pyrelands.py`, `SelfTest/Fuzz/PyrelandsFuzz.cs`,
  `Utils/harvest_log.py`, `Utils/northstar_driver/bars.py` (line 141) and
  `Utils/modcheck/required_checks.json` (the `FireEcology` and Pyrelands entries): every
  reference to the rungs or the ladder goes.

**Harness (`src/RimMandrake/Pyrelands/validation.py`)**

- Chain `ground_ash_ladder` is deleted. It is replaced by:
  - `ground_deep_ash`: a mapgen census;
  - `ash_fertility_watered`: a fertility read on a dry cell and on a cell next to a filled
    FlowWorks channel (or a cell next to `WaterShallow` when FlowWorks is absent);
  - `fresh_burn_bonus`: fertility read before a burn, right after it, at +3 days, and after a
    forced `RM_FE_BlackRain`.
- These are **state reads of `FertilityAt`**. Eyes are not the instrument here.
- `embergrass_regrow`:
  - the cohort is pre-laid to `RM_FE_Ash_Deep`, the real ground, not `SOIL`;
  - delete the comment "past 7500 the floor burns to RM_FE_Ash_Deep (fertility 0) so nothing
    could regrow".
- The `ash_timeline.py` probe from the old item is retired.

**North-star bars.** Bars under `## north star` are the owner's and hash-bound, so this design
**proposes** wording and does not edit them.

`design/validation_walks/RimMandrake/Pyrelands.md`:

- **Retire** `pyre_ground_ash_ladder`.
- **Propose:**
  - `pyre_ground_deep_ash` — *"a fresh Pyrelands map is almost all deep ash; only small pockets
    of unburned soil and gravel remain, and standing water is ringed with richer ground."*
  - `pyre_ash_fertile_when_watered` — *"a crop on deep ash beside a watered channel grows clearly
    faster than the same crop on dry ash."*
  - `pyre_fresh_burn_feeds_the_field` — *"ground that has just burned grows noticeably faster
    for a few days, and a black rain washes that advantage away early."*
- **Amend** `pyre_grass_chokes_ground`: "unburned soil is carpeted" becomes "open ground is
  carpeted". Its census currently excludes `RM_FE_Ash_Deep` as unplantable, which becomes false.

`design/validation_walks/RimStarWars/FireEcology.md`:

- **Retire** `fireeco_burn_leaves_ash_ladder` and `fireeco_ash_gradient_follows_fire` (a
  trace-to-heavy gradient).

Both files are then re-validated on his word.

## 7. Save compatibility

Players receive a savegame holding the world. Colony maps are generated at landing, so no player
save ever holds a ladder rung. Only our own keeper and review saves can.

The build keeps `RM_FE_Ash_Trace/Light/Heavy` for **one cycle** as hidden legacy aliases:

- each has the same stats as deep ash, appears in no mapgen and no designator;
- `MapComponent_PyrelandsAshField.FinalizeInit` re-lays any of them to `RM_FE_Ash_Deep` on load.

Terrain saves by shortHash, so a deleted def would lose those cells with a load error rather than
convert. The aliases are deleted once the Saves folder has been loaded through once.

The new per-cell grids default to "never burned" on a save that lacks them.

## 8. Embergrass regrowth on the new ground

- Wild spawning ignores local fertility (`wildPlantsCareAboutLocalFertility` false), so the fuel
  bed repopulates deep ash at full density, as the owner's "choked with grass" ruling wants.
- Plant growth after spawning does read fertility, so:
  - a dry scar regrows at the 0.40 rate;
  - a fresh scar regrows at about 0.90 for the first days, so the fuel bed comes back fastest
    right after a burn;
  - a watered scar regrows fastest of all.
- The old failure (grass refused on fertility-0 deep ash, 400/400 in the 2026-10-12c run) cannot
  happen: 0.40 is far above `fertilityMin` 0.08.
- The regrow thresholds the trial plan cites (25% by day 3, 60% by day 7) against the measured
  34% / 59.8% will be **re-asked once this lands**, per the owner's card note. The row stays
  CALIBRATING until then.

## 9. Docs corrected in this change

- `design/Jawa/proposals/fire_ecology_deep_design.md`: the "Ash accumulation —
  trace/light/heavy/deep" paragraph and the Black Rain slurry step.
- `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md`:
  - the terrain line;
  - bar 3;
  - bar 4's plantable-cell definition;
  - the `ash_ladder_escalation` retirement note.
- `design/RimMandrake/watcher_creatures_pitch.md`: the ttekku terrain becomes `RM_FE_Ash_Deep`.

The north-star bars and the code comments are left to the owner's re-validation and to the build
respectively (§6).
