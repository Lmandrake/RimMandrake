# The plant economy bar (2026-11-01)

Item `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE`, filed from the owner's EC1 answer, 2026-10-16: *"(1) but we need to
renormalize EVERYTHING anyway"* (`design/RimMandrake/explosive_growth_rulings_2026-10-16.md`, round 4). Its done-when
(2026-10-29): every plant def in our RM/RUT/RSW mods has growth and yield matching the water rule, and a census shows
0 off-rule. The bar below is an agent decision (delegated: tuning numbers, `delegation_policy.md`); every number in it
is measured from the base game, and loosening it is a change to this file and the census together.

## 1. What is runtime and what is a def number

The water rule is code, not def numbers. It lives in ExplosiveGrowth and is not re-tuned here:

| rule (owner) | where it runs |
|---|---|
| ×0.1 dry, ×10 wet and lit for dry natives (C6, light ruling) | `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs` `RM_RateSettings` (dryWet 10, dryDry 0.1) |
| wet natives ×4 at home (C1) | same, `wetNative` 4 |
| trees: water buys days of life, burst at a water-driven death (tree burst Q1, Q5/Q6, Q11) | `RM_TreeLife.cs`, `RM_TopResolver.cs` |
| a self-fruiting crop's full harvest uses up the water on its cell (EC3) | `RM_TopResolver.cs` → `RM_WetSources.Consume` |
| wood at tree rate (EC1) | superseded by the tree burst rulings, 2026-10-17 (`tree_burst_design_2026-10-17.md` §2: `treeRatio` retired; a tree is drawn 3.0+, not a fungus) |

The def numbers those rules multiply (`growDays`, `harvestYield`, the product's worth) are this item. **Decision: they sit
at vanilla parity at ×1.** The water makes the swing, so the numbers it multiplies must be ordinary: a watered dry native
then out-produces a vanilla crop by exactly its ×10, paid for in water and pawn hours (the bench design pass, *"×10 shrinks
land and calendar time, not work per meal"*), and never by a def fault that ×10 magnifies (the pass's example:
`RM_SicklyGlowMushroom`, 25 logs in 2 days, about 43 logs per cell per day watered).

## 2. The bar

Measured per grow day at ×1, from the plant's own `growDays` and `harvestYield` and its product's `MarketValue` and
`Nutrition`. Base-game reference values are from the 2026-10-26 def dump (`ludeon.*` packages):

| rule | bar | base game it is drawn from |
|---|---|---|
| **E1** value | harvest silver per grow day ≤ **4.0** | ordinary maximum `Plant_TreeCocoa` 3.75; crops 1.0-2.2 |
| **E2** nutrition | harvest nutrition per grow day ≤ **0.135** | maximum `Plant_Ambrosia` 0.133, `Plant_Haygrass` 0.129; rice 0.100 |
| **E3** wood only from trees | a harvest of `WoodLog` or any `Woody` stuff only from a plant drawn 3.0+ that is not on the roster's `<notTrees>` (`RM_Greatbole` exempt, its own mechanic) | tree burst Q2 *"SIZE 3.0+ ONLY"*, Q3 *"stop giving wood"*, the tree tiers sheet *"Not a tree, does not make wood."* |
| **E4** wood rate | logs per grow day ≤ **3.0** | `Plant_SaguaroCactus` and `Plant_TreePolux` 3.0; oak 1.5 |

A product with no `MarketValue` is **unmeasured**, and unmeasured fails the census like off-rule (a worth of 0 is a defect,
not a pass). Fungi drawn 3.0+ may keep a fungal log harvest (Q9 gives them no tree rules, not no harvest).

**Allowances** (in the census, each with its reason):
- `RM_AmbrosyxFungus` (E1): the exact twin of vanilla `Plant_Ambrosia` (4 × 15 silver in 6 days), a vanilla special.
- `RM_FE_Plant_ScorchFruit` (E1, E2): never sown and in no biome's `wildPlants`; Pyrelands' fire hook spawns it only on a
  burning cell (`src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs`). Its 5 fruit are the reward of one fire.

Non-wood trees' burst logs (tree burst Q12) stay on the Mod Setting default, 10 logs once at the end of a life of
hundreds of days, far under E4; no per-tree `burstLogs` is set.

## 3. What changed (2026-11-01)

Every edited def carries an XML comment naming this item, the rule and the old number. In short:

- **Yield cut to the bar (E1/E2/E4)**, growth left as it was: `RM_Arpeau` 20→13, `RM_BloomCrop` 14→6, `RM_CorriskTree` and
  `RSW_Plant_HydenockTree_Wild` 30→15 dye, `RM_Crimmelroot` and `RSW_Plant_Chakroot_Wild` 11→8, `RM_Crowncarpet` 4→1,
  `RM_CrystalHorn`, `RM_Iashiphus`, `RM_GlowberryBush`, `RM_SugarFamewort` 10→8, `RM_Dewgourd` 14→7,
  `RM_FloatstoneGarden` 35→1, `RM_FrostLeaf` 20→8, `RM_GargantuanLithops` 10→6 steel, `RM_HalfAlienTree` 25→15,
  `RM_LumbrelTree` and `RSW_Plant_JoganTree_Wild` 40→15, `RM_MangroveTree` 50→42, `RM_MoonlessStripesPlant` 16→7,
  `RM_Salvessa` and `RSW_Plant_Nysyllin_Wild` 10→4, `RM_Slimecasia`, `RM_SlimyFern` 10→8, `RM_TentacularPlant` 15→13,
  `RM_Thrannagourd` and `RSW_Plant_HubbaGourd_Wild` 2→1, `RM_YearningFruit` 10→7.
- **Growth slowed (E2, already 1 per harvest)**: `RM_Glasmaw` and `RSW_Plant_TookeTrap_Wild` 3→7.5 grow days (one root
  is a whole 1.0 nutrition).
- **No more wood under 3.0 (E3)**, completing the tree burst build's T6: the five fungi or mushrooms among them
  (`RM_FlakespireFungus`, `RM_GreenArpeau`, `RM_Skulltop`, `RM_NogtylMarsh`, `RM_SicklyGlowMushroom`, the last
  being the pass's 25-logs-in-2-days fungus) now yield vanilla `RawFungus` within E2; `RM_MangrovePalm` and the six
  `RM_Plant_*Cactus` drop nothing, T6's pattern.
- **Products given a worth**: `RM_ColdWax` and `RM_QeshraRoe` had no `MarketValue`; now 1.5.

The 15 defs T6 stripped of wood on 2026-10-17 stay harvest-free: Q3 says only *"stop giving wood"*, and this item adds
no new product for them.

## 4. The instrument

`python3 src/RimMandrake/Utils/plant_economy_census.py --check` reads every XML under `src/RimMandrake`,
`src/RimStarWars`, `src/RimUtinni`, applies our patches to the raw XML first and then resolves inheritance against the
base game's `Data/*/Defs` (the game's own order), evaluates a `Conditional` on our defs and takes only its branch, and
ends `N plant defs (...): 0 off-rule, 0 unmeasured`. Any patch op it cannot evaluate that touches a number it reads
(a `FindMod` branch, an `@Name` selector, a whole-`<plant>` Replace, a Remove, a product's `MarketValue`) turns the
plants it names, their children and the plants harvesting it UNMEASURED; with no readable name, or a roster patch, the
whole census is. `--check` also refuses a tree of under 300 plants, unparsable XML or a missing tier folder. Its
selftest, `src/RimMandrake/Utils/selftest_plant_economy_census.py`, proves on a fixture tree of 30 plant defs that each rule
fires and each of those paths reads as it should (mutation-probed), then runs the live census. Two independent GPT
reviews (2026-11-01) found 12 and then 8 defects, all fixed or listed as limits in the census's docstring. Limits: it
reads XML, not the loaded game, so a donor mod's patch on our plant or a C# change to a def is outside it; on
2026-11-01 it saw 394 plant defs against 385 in the 2026-10-26 dump.
