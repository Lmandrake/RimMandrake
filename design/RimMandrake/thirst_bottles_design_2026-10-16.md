# Thirst and bottles in FlowWorks, compatible with Dubs Bad Hygiene Lite (design, 2026-10-16)

Item: `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY`. Owner, 2026-10-16: *"We should have our own bottles and
thirst, but if Dubs Lite is loaded be compatible with it. Not require it, but not conflict either."*

This replaces the DBH-gated `src/RimMandrake/FlowWorks/Patches/RM_ColoredWaterBottles_Patch.xml` approach.
It supersedes `LIQUID_THIRST_CHAIN_1`'s line "with DBH absent, bottles are plain ingestibles with a hydration
thought". The carried-water job (explosive growth HW1/D8, `explosive_growth_ruled_spec_2026-10-16.md` §3, §8)
uses these containers.

## 0. What already exists (searched first)

| thing | where | state |
|---|---|---|
| bottle/bucket/barrel chain: empty, filled, dirty, wash, tank | `Defs/LiquidTypes/ThingDefs/RM_LiquidBottles{,_Base}.xml`, `Source/LiquidTypes/*Bottle*`, `Building_LiquidTank.cs` | built; live fill FAILED 2026-09-25 (`LIQUID_BOTTLE_LOOP_1`), cause not isolated |
| `thirstQuality` ladder (Distilled/Potable/Fouled/Toxic) | `LiquidDef.cs:119`; registry rows: FreshWater=Potable, SaltWater=Fouled, Brine=Fouled, ToxicWater=Toxic | data only; nothing reads it for thirst |
| ingest hook on filled bottles | `IngestionOutcomeDoer_BottleResidue` (leaves dirty/empty, need-agnostic) | built |
| litres (bottle 1.5 L, bucket 15 L, barrel 208 L; decilitre ints) | `liquid_litres_2026-10-16.md` | ruled |
| four container styles (Scrapper/Industrial/Modern/Futuristic) | `liquid_containers_four_styles_2026-10-16.md` | ruled |
| 5 DBH-only coloured bottles `RM_WaterBottle_{Rust,Verdigris,Amber,Violet,Chalk}` | `Patches/RM_ColoredWaterBottles_Patch.xml` (gated on `ResourceBasedMom` existing) | **to delete** |
| `dbh_water` tag on coloured-water terrains | `Patches/LiquidTypes/RM_DBH_WaterTerrainTag.xml` (FindMod on Lite / full DBH) | keep |
| any `NeedDef` for thirst of our own | none in `src/` (MEASURED grep `<NeedDef`, 2026-10-16) | to build |

**DBH facts (MEASURED from workshop files, 2026-10-16):**
- Lite = `Dubwise.DubsBadHygiene.Lite` (2570319432); add-on `Dubwise.DubsBadHygiene.Thirst` (2582878800) ships
  **no Defs**, only About + textures: it is a presence flag. Full DBH = `Dubwise.DubsBadHygiene` (836308268).
- The need is `NeedDef DBHThirst`, `Class="DubsBadHygiene.Needy"`, `needClass DubsBadHygiene.Need_Thirst`,
  `baseLevel 0.8`, `onlyIfCausedByHediff true` (so DBH grants it by its own code), body/race/hediff `Exemptions`
  lists (`Lite 1.6/Defs/NeedDefs/Needs_Misc.xml:53`). Full DBH defines the same defName.
- Hediff `DBHDehydration`, jobs `DBHDrinkFromGround/FromBasin/PackWaterBottle/StockpileWaterBottles/
  AdministerFluids`, think node `DubsBadHygiene.ThinkNode_ConditionalThirst` + `JobGiver_DrinkWater`.
  Every thirst def carries a `DBHThirst="true"` attribute (DBH drops them when thirst is off; mechanism UNMEASURED).
- A drinkable is any ThingDef with `DubsBadHygiene.WaterExt` {`water`, `UseForWashing`, `SeekForThirst`}
  (`DBH_WaterBottle`, `Items_Resource_Stuff.xml:108`). DBH settings strings include `ThirstNeed`,
  `PetsGetThirst`, `ThirstRateD`, `ThirstRequiresRestart` (BadHygiene.dll strings). How DBH reads `water` on
  ingest is UNMEASURED (no outcome doer in the XML, so it is C#).

## 1. Core decision: ONE need, chosen at startup; ours steps aside when DBH thirst is live

**Rule:** if DBH thirst is live, `DBHThirst` is the only thirst need and ours is never added. Otherwise
`RM_Thirst` is the only one. Our bottles satisfy whichever need is live.

**Mechanism (C# detection + one Harmony postfix; defs always load):**
1. `RM_ThirstProvider` (`[StaticConstructorOnStartup]`) resolves `Mode` once:
   `Dbh` if `DefDatabase<NeedDef>.GetNamedSilentFail("DBHThirst") != null` **and**
   (`ModsConfig.IsActive("Dubwise.DubsBadHygiene.Thirst")` or `ModsConfig.IsActive("Dubwise.DubsBadHygiene")`);
   else `Own`. The result goes to the log once: `[FlowWorks] thirst provider: Own|Dbh (reason)`.
2. A Harmony postfix on `Pawn_NeedsTracker.ShouldHaveNeed(NeedDef)` returns false for `RM_Thirst` when
   `Mode == Dbh` or the setting is off (the 1.6 signature must be confirmed with RimSage before writing). Vanilla
   `AddOrRemoveNeedsAsAppropriate` then removes ours from loaded pawns, so a save survives adding or removing DBH
   in either direction with no dangling def.
3. Bottles get DBH's drinkable marker **as data**: a FindMod-gated patch
   (`Patches/LiquidTypes/RM_DBH_BottleWaterExt.xml`, mods = `Dubs Bad Hygiene Lite`, `Dubs Bad Hygiene`) adds
   `DubsBadHygiene.WaterExt` (`water 1`, `UseForWashing false`, `SeekForThirst true`) to every drinkable
   `RM_Bottle_*`. The generator emits it, one `PatchOperationAdd` per def, never a top-level `MayRequire`.

**Why we step aside rather than take over DBH's need:**
- DBH's need has callers we cannot see or keep up with: drink-from-ground, basins, administer-fluids,
  caravans, RimHUD (*"DONT CHANGE NAMES WILL BREAK RIMHUD"*). Taking it over means Harmony into a closed DLL
  that changes with every update. Stepping aside is one boolean on our side.
- A player who loads DBH chose DBH's thirst model, so we fit into it. Without DBH they get ours.
- Removing our NeedDef by XML patch was rejected. It breaks saves (Scribe "Could not load reference"), breaks
  DefOf, and still leaves the hediff, thoughts and jobs to remove.
- Corner case: DBH loaded with its own thirst turned off in DBH settings. `DBHThirst` may still load with no pawn
  holding it. Then there is no thirst at all, which is DBH's choice. Detection is ±1 load from measured, so
  step 1 of the build checks it live (§7).

## 2. The need `RM_Thirst` (Own mode)

| field | value | reason |
|---|---|---|
| defName / class | `RM_Thirst` / `RimMandrake.FlowWorks.Thirst.Need_RM_Thirst` | naming scheme |
| range, start | 0–1, spawn at 0.8 | matches DBH baseLevel so the bar reads the same |
| base fall | 1.0 → 0 in **1.25 days** (0.8/day) at 1×; a 1.5 L bottle restores **0.5** (3 L/day) | real ~2.5–3 L/day |
| heat factor | ×(1 + 0.05 per °C above the pawn's `ComfyTemperatureMax`), cap ×3 | *"One kind of heat"*: reads vanilla ambient temperature, so it is never a new heat |
| other factors | ×1.3 while doing hard labour (mining, construction, hauling), ×0.5 asleep | the desert should bite |
| frozen when | `Need.IsFrozen` (cryptosleep, deathrest, caravan off-map handled in §5) | vanilla |
| thresholds | Thirsty < 0.3 · Parched < 0.1 · Empty 0 | the drink think-node starts at < 0.3 |

**Mood:** `RM_Thought_Thirsty` −4, `RM_Thought_Parched` −10, `RM_Thought_Dehydrated` −18 (a `ThoughtWorker`
on need level, the same shape as vanilla Hungry). There is **no positive thought** for plain water.
`RM_Thought_DrankDistilled` +2 for 0.5 day.

**Health:** `RM_Dehydration` (HediffDef). Severity +0.30/day while the need is 0, −0.6/day while it is above 0.3.
Lethal at 1.0, which is about 3.3 days at zero. Stages: 0.0 trivial (Consciousness −5%) · 0.2 minor (−10%,
Moving −5%) · 0.4 moderate (−20%, Moving −10%) · 0.6 severe (−30%, Moving −20%) · 0.8 extreme (−45%,
Moving −40%). This mirrors DBH's stage shape so play feels the same in both modes. A pawn never disappears without
a readable sign: the hediff names the cause.

**Who gets it:** humanlike pawns with Metabolism or BloodPumping, by default. Exempt: mechanoids, droids
(`src/RimStarWars/Droidworks` has its own needs), anomaly entities, and any race or gene carrying
`RM_ThirstExemptExtension` (data, so a race mod opts out by patch). Animals are **off** by default, setting
`animalsGetThirst` (DBH's `PetsGetThirst` default is UNMEASURED). With it on, wild animals drink from terrain
only and never touch bottles.

## 3. Drinking

| source | how | quality |
|---|---|---|
| filled bottle `RM_Bottle_<Liquid>` | vanilla `Ingest` job (bottles keep `NeverForNutrition`, so food search never picks them); the new `IngestionOutcomeDoer_RM_Hydrate` raises `RM_Thirst` by `litres / 3.0` | the row's `thirstQuality` |
| fresh-water terrain edge | `JobDriver_RM_DrinkFromTerrain` (stand adjacent, 300 ticks, +0.5); debits litres like a bottle fill (`TryDebitTerrain`) | the terrain's LiquidDef row |
| `RM_LiquidTank` holding a drinkable liquid | `JobDriver_RM_DrinkFromTank`, 1.5 L per drink | the tank's row |
| bucket / barrel | **not drunk directly** (items are consumed whole). The existing tank/fill jobs decant them to bottles | n/a |

`JobGiver_RM_Drink`, in a ThinkTreeDef inserted at `Humanlike_PostDuty` (DBH uses the same tag, MEASURED), picks
the best reachable source by quality, then distance: Distilled > Potable > Fouled > Toxic. Toxic is only taken
when the pawn is Parched, like vanilla's desperate-food rule. Pawns pack 2 bottles into inventory on a caravan or
long job (`JobGiver_RM_PackBottles`, like DBH's PackWaterBottle).

**Quality effects** live in the outcome doer, the same in both modes because they are about the liquid, not
the need:
- Distilled: hydrate ×1.0, +2 mood.
- Potable: ×1.0.
- Fouled (salt water, brine, ash-fouled rain water): ×0.7, 20% chance of vanilla `FoodPoisoning`.
- Toxic: ×0.5, `ToxicBuildup` +0.12.
The coloured waters (rust/verdigris/amber/violet/chalk) become ordinary registry rows, Potable by default.

**The "use" chain is unchanged:** the residue doer still leaves `RM_BottleDirty` (or an empty, if the dirty stage
is off). Style and Stuff carry through `MakeContainer`.

## 4. The bottles

- No new container family. The bottle/bucket/barrel defs stay the single item set, generated from registry rows
  by `Tools/generate_liquid_suite.py`. A row with `thirstQuality` gets an `<ingestible>` block on its **bottle**
  (buckets and barrels lose any ingestible block they have; today `RM_LiquidBottles.xml` has 17 `ingestible`
  hits, so the generator must be checked).
- Coloured waters: five new registry rows, `RM_Liquid_{Rust,Verdigris,Amber,Violet,Chalk}Water`. Each adopts
  its `RM_Water_<colour>` terrain (Defs/ManyWaters) as its suite, `thirstQuality Potable`, `color` = today's
  patch tints. They emit `RM_{Bottle,Bucket,Barrel}_<Colour>Water` on the Industrial (or styled) sprite with the
  liquid colour on the mask window. They load with DBH absent; that is the point of the item.
- DBH mode adds only `WaterExt` to drinkable bottles (§1.3). There is **no** `DubsBadHygiene.CompContamination`
  on ours: our `thirstQuality` already says how clean the water is, and two contamination systems on one item
  would double-count.
- Litres: bottle 1.5 L (Stuff multiplier per the litres ruling), bucket 15 L, barrel 208 L.

## 5. Caravans, prisoners, patients

- **Caravan:** a `WorldComponent` tick (every 2500 ticks) lets a caravan pawn below 0.3 drink the best bottle in
  caravan inventory. Caravan forming shows `RM_Thirst` days-of-water next to food (a Harmony postfix on the
  caravan needs readout; build step 6, may be cut to a tooltip).
- **Patients/prisoners:** `WorkGiver_RM_AdministerWater` (Doctor and Warden, humanlikes only), the same shape as
  DBH's AdministerFluids. It carries a bottle to a downed or imprisoned pawn below 0.3.

## 6. Mod Settings (FlowWorks `RimMandrakeFlowWorksSettings`, new section "Thirst")

| setting | default (shipped) | off/edge behaviour |
|---|---|---|
| `thirstEnabled` | **on** | off: no `RM_Thirst` on anyone; bottles still drink (quality effects stay) |
| `thirstProvider` (read-only label) | shows `Own` / `Dbh` + reason | informational; there is no switch, so two needs can never be forced |
| `thirstRateMultiplier` | 1.0 (0.25–3) | tuning |
| `thirstHeatScaling` | on | off: flat rate |
| `animalsGetThirst` | off | on: animals drink from terrain only |
| `drinkFromTerrain` | on | off: bottles and tanks only (the hard scavenger mode) |
| `waterQualityEffects` | on | off: every drinkable is treated as Potable |
| `dbhBottleBridge` | on | off: no `WaterExt` patch, so DBH pawns ignore our bottles (escape hatch for a DBH update). Label: needs restart |

All off leaves FlowWorks whole: bottles are plain items that fill, wash and trade. The existing
`bottleLoopEnabled` / `bottleDirtyStageEnabled` / `tankLoopEnabled` are unchanged.

## 7. Files: replaced, deleted, new

| path (under `src/RimMandrake/FlowWorks/`) | action |
|---|---|
| `Patches/RM_ColoredWaterBottles_Patch.xml` | **DELETE**. Its 5 `RM_WaterBottle_*` defs come back as the generated `RM_Bottle_<Colour>Water`. Saves that hold the old defs lose those stacks (log line `Could not load reference`); accepted for a dev save, see OQ-4 |
| `Patches/LiquidTypes/RM_DBH_WaterTerrainTag.xml` | keep (lets DBH's drink-from-ground see the coloured waters) |
| `Patches/LiquidTypes/RM_DBH_BottleWaterExt.xml` | NEW, generated, FindMod-gated |
| `Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml` | +5 coloured-water rows |
| `Defs/Thirst/{RM_Thirst_Need,RM_Dehydration,RM_Thirst_Thoughts,RM_Thirst_Jobs,RM_Thirst_ThinkTree}.xml` | NEW |
| `Source/Thirst/{Need_RM_Thirst,RM_ThirstProvider,RM_Patch_ShouldHaveNeed,IngestionOutcomeDoer_RM_Hydrate,JobGiver_RM_Drink,JobDriver_RM_DrinkFromTerrain,JobDriver_RM_DrinkFromTank,WorkGiver_RM_AdministerWater,RM_ThirstCaravan,RM_ThirstExemptExtension}.cs` | NEW |
| `Tools/generate_liquid_suite.py` | emits the ingestible only on bottles, the hydrate doer, and the WaterExt patch |
| `About/About.xml` | add `Dubwise.DubsBadHygiene.Thirst` and `Dubwise.DubsBadHygiene` to `loadAfter` (Lite is already there) |
| comments in `RM_BottledLiquidExtension.cs`, `IngestionOutcomeDoer_BottleResidue.cs`, `RM_LiquidBottles_Base.xml` that say "DBH registration is LIQUID_THIRST_CHAIN_1" | repoint at this doc in the same change |
| `infrastructure/state/items/LIQUID_THIRST_CHAIN_1.md` | its "register as DBH drinkables / plain ingestible with hydration thought" spec is superseded; the crude→household still chain survives (BENCH ledger note owed, not done here) |

## 8. Build plan (ordered; each step ends green in the script before the next)

0. **Unblock the fill.** `LIQUID_BOTTLE_LOOP_1`'s live fill failed (2026-09-25). Thirst without a working fill
   is untestable. Read `RM_LiquidBottleUtility.LiquidAt(WaterShallow)` on a fresh log first.
1. `RM_ThirstProvider` plus its log line. Confirm the `ShouldHaveNeed` signature via RimSage. Live check on
   three lists: no DBH (Own), Lite+Thirst (Dbh), Lite without Thirst (Own, and confirm `DBHThirst` is absent
   or inert).
2. NeedDef, hediff, thoughts, `Need_RM_Thirst` (fall, heat, hard labour) and the postfix.
3. Generator: coloured-water rows, bottle-only ingestibles, `IngestionOutcomeDoer_RM_Hydrate`, quality effects.
   Delete `RM_ColoredWaterBottles_Patch.xml` in the same commit.
4. `JobGiver_RM_Drink` + think tree, terrain and tank drink drivers.
5. DBH bridge patch (`WaterExt`), generated.
6. Administer-water work giver, caravan drinking, pack-bottles.
7. Mod Settings section and `thirstProvider` label.
8. HW1 carried water (explosive-growth D8) consumes `RM_Bucket_FreshWater` first, then a bottle. It goes
   through `MakeContainer`, so dirty/empty comes back the same way.

## 9. First functional script (ships with step 1; `debug_process.md` §2)

Joins FlowWorks' family script `src/RimMandrake/FlowWorks/validation.py` as a `thirst` chain. Every line is
sourced from this doc, so the script is not a guess.

| # | check | instrument | pass bar |
|---|---|---|---|
| T1 | the provider line names the right mode for the loaded list | Player.log grep `thirst provider:` + parsed ModsConfig | Own without DBH thirst, Dbh with it |
| T2 | **exactly one** thirst need per colonist | bridge pawn needs read: count of `RM_Thirst` + `DBHThirst` | == 1 on every free colonist (== 0 when `thirstEnabled` is off and Own) |
| T3 | Own: the need falls | read level, advance 0.25 day at 20 °C | drop within 0.2 ± 0.03 × multiplier |
| T4 | a drinkable bottle satisfies the live need | set need 0.2, give `RM_Bottle_FreshWater`, order Ingest | level rises ≥ 0.45 (Own) / DBH need rises (Dbh); a dirty bottle appears |
| T5 | quality | drink `RM_Bottle_SaltWater` ×10 on test pawns | hydrate ×0.7; FoodPoisoning in 1–4 of 10 |
| T6 | dehydration is readable and lethal | need held at 0, advance 1 day | `RM_Dehydration` ≈ 0.30 ± 0.03 |
| T7 | DBH absent: no errors | Player.log first exception since load | none naming `DubsBadHygiene`, `RM_Thirst`, `RM_Bottle_` |
| T8 | coloured bottles exist without DBH | def read `RM_Bottle_RustWater` | present, ingestible, Potable |

Informative false theory to record if met: "the pawn has no thirst" when T1 says Dbh may mean DBH's own thirst
setting is off, not our bug.

## 10. Open questions for the owner (question-card candidates)

**OQ-1. When Dubs thirst is on, whose thirst runs?**
(a) Dubs' thirst runs and ours steps aside; our bottles count for it. One switch on our side, nothing breaks
when Dubs updates. *(recommended)*
(b) Ours runs and Dubs' is disabled. Same feel everywhere, but we must patch inside Dubs and it can break on
any Dubs update.
(c) The player picks in Mod Settings. Most flexible, but one wrong pick can give two thirst bars.

**OQ-2. Can pawns drink straight from a pond or river?**
(a) Yes, slower than a bottle, using that water's quality. *(recommended)*
(b) No, bottles and tanks only. Real scavenger pressure, but harsh early game.
(c) Yes, but only with the setting on, default off.

**OQ-3. How fast does thirst bite on this desert world?**
(a) Empty in about 1¼ days, faster in heat (×3 at most). Death about 3 days after empty. *(recommended)*
(b) The same as hunger (about 2 days to empty), no heat effect. Gentler.
(c) Harsh: empty in 1 day, heat up to ×4.

**OQ-4. The five coloured Dubs-only bottles get new names. Old saves lose those stacks. Fine?**
(a) Yes, a dev-save cost only. *(recommended)*
(b) Keep the old names for the five so saves keep them. That leaves five odd defs forever.

**OQ-5. Do animals get thirsty?**
(a) No (default off, switch available). *(recommended)*
(b) Yes, and they drink from terrain only.
(c) Only tamed animals.
