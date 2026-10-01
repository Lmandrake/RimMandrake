# The Carbon Garden — hydrocarbon flora vetting (Blue Desert)

`BLUEDESERT_GPT_ENRICHMENT_1` §3. Owner, typed on the card (2026-09-30): *"Only hydrocarbon
plants please."* Source pitch: the GPT enrichment consult, §5 "The Carbon Garden"
(`Transient/bedazzle_gpt_enrich_2026-09-30/bluedesert.md`, advice only). This is also the Blue
Desert's first contribution to `BEDAZZLE_FLORA_EXPANSION_1` (the owner's "Need more plant-like
members of this biome"): that item has produced no Blue Desert pitch list yet, so these rows are
its Blue Desert list, and its sitting for this biome is this page.

**Status: NO DEF SHIPS YET.** The item's own gate: new names collision-swept (done, §2), art
commissioned (rows written, §4, not queued), and art to an owner review sheet **before any def
ships**. The draft stats in §3 are the def work waiting on that sheet.

## 1. What "hydrocarbon plant" has to mean here

From `the_blue_desert.md` §3 and the hard bans (§6):

- Body: hydrocarbon plumbing, butane/pentane stores, methane exchange; transparent, fractal gas
  exchange instead of leaves; **small**. Stable only in the cold.
- Ban 1: no water metabolism. Ban 2: never sowable (no `sowTags`). Ban 3: **no warm-safe
  hydrocarbon organics**, and that covers the plant's PRODUCE too: anything it yields must carry
  the warm-detonation behaviour (the `RM_ColdWax` pattern: `CompTemperatureRuinable` +
  `RM_CompRuinedDetonator` + `CompExplosive`).
- Mechanically: `RimMandrake.BlueDesert.CompProperties_PlantCharge` (the charge comp every native
  plant carries), `completelyIgnoreFertility`, sub-zero growth band, `growMinGlow 0`,
  `dieIfNoSunlight false`, butane-gut `outcomeDoers` for foreign grazers, MaxHitPoints ≤ 40 so a
  blast chains.

## 2. The three candidates, vetted

| candidate | hydrocarbon-bodied? | verdict | what changes |
|---|---|---|---|
| **milelace** | Yes: a creeping mat of transparent charge filament, palefloss's lineage spread flat. | **KEEP, reshaped** | Its pitched product, an "insulating frost-fibre", would be a warm-safe hydrocarbon organic unless it detonates warm (ban 3). Recommended: it yields `RM_ColdWax` like the rest of the flora, and no new fibre item. (If the owner wants the fibre, it must ship on the cold-wax comps, meaning a cold-store packing material that is never worn or carried indoors.) "Stitches fresh drifts" = it re-seeds onto new ice-sand drift cells when `RM_IceSandDrift` ends: small C#, riding the drift-end hook `RM_MapComponent_MurrekDrifts` already has. |
| **Ninefold Censer** | Yes: a closed many-lobed cup that opens after Haze and exhales its own hydrocarbon vapour. The most hydrocarbon of the three. | **KEEP, RENAMED** | **Name collides:** `Ninefold` is already our mod `mandrake.rm.ninefold` (`src/RimMandrake/Ninefold`). Proposed name **hazebell** (`RM_Hazebell`), sweep-clear (§2a). Opening on Haze = small C#: a plant comp that swaps to an "open" graphic and emits a breath fleck while the `RM_Haze` weather is active or for a day after it. |
| **longglass** | Only if its "frost" is Haze precipitate (hydrocarbon rime), not water frost, and only if it is not a second glassfern. | **KEEP, reshaped** | Its frost becomes the Haze's own rime, which settles only on new growth (graphic: fresh tips go frosted). "Turns toward the wind" is an **engine limit**: RimWorld plants have no facing and only the shared wind-sway shader. Recommended instead: it grows LEANING the prevailing way (baked into the art), sways with vanilla wind. Distinct from glassfern by being a spire (branching upward, knee-high) rather than a fern frond. |

None is dropped: all three are hydrocarbon-bodied once reshaped. Owner questions are in §5.

### 2a. Collision sweep (2026-09-30)

Swept every `.xml`/`.md`/`.csv` under this repo's `src/` and `design/`, the game's `Data/`
(Core + all DLC), the local `Mods/` folder and the Steam workshop folder, for `milelace`,
`longglass`, `hazebell`, `censer` and `frostfibre`. Sanity probes `palefloss` and `thrumbo` in the
same pass. Files read: repo `src/` 2,098, repo `design/` 781, local `Mods/` 2,025, workshop
71,170, game `Data/` 1,672. Probes found: `palefloss` (repo src 7, design 5, Mods 6) and
`thrumbo` (in all five roots, 712 files total), so the sweep could see.

- `milelace`, `longglass`, `hazebell`, `frostfibre` / `frost-fibre` / `frost fibre`: **0 hits
  anywhere.** Clear.
- `censer`: 2 hits, both in our design docs. `Alien_Bestiary.md` names the Mechalope's IN-6
  variant **"Censer"**, and `tile_augmentation_matrix.md` uses the word in passing. That is a
  second reason, beside `mandrake.rm.ninefold`, not to ship "Ninefold Censer".

## 3. Draft defs (NOT shipped — wait for the art sheet)

All three: `ParentName="PlantBase"`, the palefloss plant block (`completelyIgnoreFertility`,
`fertilityMin 0`, growth band -90/-60/-20/-1 °C, `growMinGlow 0`, `growOptimalGlow 0`,
`dieIfNoSunlight false`, `dieIfLeafless false`, `neverBlightable`), no `sowTags`,
`harvestedThingDef RM_ColdWax`, `Flammability 0.05`, the `RM_IngestionOutcomeDoer_ButaneGut`
outcome doer, and `CompProperties_PlantCharge`. INVENTED numbers below, on the existing flora's
scale (palefloss 20 HP / r1.1, glassfern r1.9).

| def | label | MaxHP | growDays | harvestYield | visualSize | charge radius / dmg | wild commonality (proposed) | C# |
|---|---|---|---|---|---|---|---|---|
| `RM_Milelace` | milelace | 15 | 5 | 1 | 0.4–0.6, `Graphic_Random` mats | 1.1 / 30 | 0.35 | drift re-seed (optional) |
| `RM_Hazebell` | hazebell | 25 | 9 | 3 | 0.3–0.45 | 1.4 / 40 | 0.12 | Haze-open graphic + breath fleck |
| `RM_Longglass` | longglass | 30 | 12 | 2 | 0.45–0.65 | 1.9 / 40 | 0.15 | none |

Roster rows land on `RM_BlueDesert`'s `<wildPlants>` in the shorthand element form
(`<RM_Milelace>0.35</RM_Milelace>`), never `<li>`.

## 4. Art commission

Rows written to `infrastructure/artpipe/art_lists/bluedesert_gpt_enrichment.csv` (not queued: the
daemon only takes jobs `fill_queue.py` puts in `pending/`). Checked first: no existing art for
any of these subjects. A walk of all 3,734 files under `infrastructure/artpipe/` found 0 hits for
milelace, longglass, hazebell or censer (probe: `palefloss` 8 hits). Seven rows: the three plants
(hazebell twice, closed and open) plus the three non-flora textures the same item's built parts
need (cold rack, meltwater can, ablation silhouette). The rime road reuses vanilla's Ice texture,
tinted, so it needs none.

## 5. Owner questions for the sitting

1. Milelace's fibre: drop it (yields cold wax) or keep it as a warm-reactive cold-store material?
2. Hazebell as the censer's new name, or another?
3. Longglass: leaning-with-the-wind art in place of turning, acceptable?
