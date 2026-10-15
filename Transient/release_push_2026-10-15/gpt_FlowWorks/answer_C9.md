Eight findings below. This slice supports XML/data-contract findings; it does **not** establish a Scribe, session-static, or cache-invalidation defect.

Paths are relative to `src/RimMandrake/FlowWorks/`. I use exact XML quotations instead of uncertain line numbers. Checks below are proposed, not executed.

**F1 — HIGH — Player-accessible chemfuel is disconnected from the detonating canal fluid**

- **Where:** `Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml`, `RM_Liquid_Chemfuel`: `<bottle>Chemfuel</bottle>` with no `canalFluid`. Likewise `Patches/LiquidTypes/RM_LiquidDef_AstrofuelAdoption.xml`, `RM_Liquid_Astrofuel`: `<bottle>VGE_Astrofuel</bottle>` with no `canalFluid`. Meanwhile `Defs/Canals/FluidDefs/FlowWorks_PitFluids.xml` defines both corresponding FluidDefs with `<fireKind>Detonation</fireKind>`.
- **What happens:** The item/tank identities have no declared connection to their canal identities. The supplied pit-fluid header explicitly identifies `canalFluid` as the connection that lets a registered liquid feed a cut. The detonating canal forms therefore exist separately from the fuels players acquire. Propane has the broader gap: its registry row supplies terrain and containers, but no `canalFluid` or corresponding FluidDef appears here.
- **Repro:** Put ordinary chemfuel into a tank and pump it into an empty excavation. Repeat with adopted astrofuel; try drawing from a propane pond.
- **Suggested check — offline def dump:** Assert the resolved `canalFluid` for these three LiquidDefs. Then check that each intended fuel has an identity-preserving tank → canal → tank route. Whether the current reader refuses or substitutes another fluid requires the omitted C#.
- **Confidence:** **High** for the missing connections; **medium** for the precise player-facing failure.

**F2 — HIGH — Conversion recipes explicitly budget unexplained liquid loss**

- **Where:** `Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml`. Examples:
  - Salt-water distillation: `<inputUnits>2</inputUnits>` / `<outputUnits>1</outputUnits>`.
  - Toxic-water filtering: `<inputUnits>3</inputUnits>` / `<outputUnits>1</outputUnits>`.
  - Brine distillation: `<inputUnits>4</inputUnits>` / `<outputUnits>1</outputUnits>`.
- **What happens:** Executing these declared ratios removes more liquid stock than it produces. These rows declare no reject stream or other destination for the difference. The drip-filter description even says it “wastes most of what it is given.” Under the brief’s conservation law, that is a design mismatch: conversion inefficiency is not the sanctioned canal-fill overflow.
- **Repro:** Feed a drip filter 30 units of toxic water. Its declared conversion yields ten fresh-water units, leaving twenty units unaccounted for.
- **Suggested check — offline Python/SelfTest:** Enumerate conversion rows and require every input unit to appear in product, retained intermediate stock, or an explicitly accounted output. Check `CompLiquidConverter` before concluding that its implementation lacks an additional accounting mechanism.
- **Confidence:** **High** for the declared deficit; **medium** for runtime destruction because the converter implementation is absent.

**F3 — HIGH — Tar still requests the cooling-to-glass behavior the owner reversed**

- **Where:** `Defs/Canals/FluidDefs/FlowWorks_Fluids.xml`, `RM_Fluid_Tar`:
  ```xml
  <coolsToGlassEdge>RM_TarGlass</coolsToGlassEdge>
  ```
  This conflicts with supplied ruling #6 in `gss_flowworks_rulings_2026-10-11.md`, including its explicit resolution: “no edge inside channels.”
- **What happens:** The shipped fluid data still requests conversion of a tar flood edge into solid terrain. If its reader remains active, a player’s liquid tar defense can acquire solid glass edges despite the reversal. Whether stock is also lost cannot be established here.
- **Repro:** Release tar along a dug channel with the cooling path enabled; inspect the advancing/receding edge.
- **Suggested check — offline:** Assert that `RM_Fluid_Tar.coolsToGlassEdge` is absent, or inspect its reader and prove that it cannot solidify tar inside excavations. A resolved-def read alone can confirm the stale instruction.
- **Confidence:** **High** for the design/data conflict; **medium** for execution.

**F4 — HIGH — Acid terrain advertises itself to DBH as usable water**

- **Where:** `Defs/LiquidTypes/TerrainDefs/RM_AcidWater.xml`, both `RM_AcidShallow` and `RM_AcidDeep`:
  ```xml
  <li>dbh_water</li>
  ```
  The same defs declare `<pH>2</pH>` and AcidBurn damage.
- **What happens:** The generated terrain carries DBH’s water-source tag despite being corrosive acid. This contradicts the potable-only policy documented in `RM_DBH_FreshWaterDrinkables.xml`. The bottle gate does not protect terrain consumers: acid is independently advertised through the terrain tag.
- **Repro:** With DBH active, give pawns access to an acid shore and remove ordinary water sources; inspect their washing/drinking source choices.
- **Suggested check — offline first:** Query resolved terrains carrying `dbh_water` and cross-check their liquid’s `thirstQuality`, pH and contact damage. Then cheaply inspect DBH’s actual source eligibility for `RM_AcidShallow`; the DBH consumer implementation is outside this input.
- **Confidence:** **High** for incorrect tagging; **medium** for the specific DBH action it enables.

**F5 — MEDIUM — DBH counts every fresh-water bucket as five units despite material-scaled contents**

- **Where:** `Patches/LiquidTypes/RM_DBH_FreshWaterDrinkables.xml`, `RM_Bucket_FreshWater`:
  ```xml
  <water>5</water>
  ```
  `Defs/LiquidTypes/ThingDefs/RM_LiquidBottles_Base.xml`, bucket material rules:
  ```xml
  <li><material>Metal</material><capacityFactor>1.2</capacityFactor><holdsHot>true</holdsHot><holdsAcid>false</holdsAcid></li>
  <li><material>Leather</material><capacityFactor>0.8</capacityFactor><holdsHot>false</holdsHot><holdsAcid>false</holdsAcid></li>
  ```
- **What happens:** A metal bucket contains six units and a leather bucket four, but both expose a fixed DBH water value of five. Drinking/washing therefore values different actual quantities identically. Leather over-credits one unit; metal under-credits one.
- **Repro:** Fill one wooden, steel and leather bucket from measured tank stock, then use each through DBH.
- **Suggested check — offline:** Compare `RM_ContainerMaterialMath.ScaledUnits(5, factor)` against the resolved `WaterExt.water` for every allowed bucket material. A cheap live follow-up measures thirst/washing credit per consumed bucket.
- **Confidence:** **High** for the mismatch; DBH-side material adjustment, if any, needs checking.

**F6 — MEDIUM — Compatibility silently disappears with full Dubs Bad Hygiene**

- **Where:** Both `Patches/LiquidTypes/RM_DBH_FreshWaterDrinkables.xml` and `RM_DBH_WaterTerrainTag.xml` gate solely on:
  ```xml
  <li>Dubs Bad Hygiene Lite</li>
  ```
  All five definitions in `Defs/ManyWaters/ThingDefs/RM_ColoredWaterBottles.xml` likewise require:
  ```xml
  MayRequire="Dubwise.DubsBadHygiene.Lite"
  ```
- **What happens:** Full DBH does not satisfy these gates. Fresh FlowWorks containers lose the supplied drinkable registration, colored-water terrain tagging is skipped, and the colored DBH bottles are not loaded. Full DBH identifies itself as `Dubs Bad Hygiene`, package `Dubwise.DubsBadHygiene`, and includes thirst. [DBH’s own metadata](https://github.com/Dubwise56/Dubs-Bad-Hygiene/blob/master/About/About.xml)
- **Repro:** Load FlowWorks with full DBH and no Lite package; compare resolved fresh-container extensions against the Lite configuration.
- **Suggested check — offline patch fixture:** Run three configurations: neither DBH variant, Lite, and full. Require equivalent intended integration for the latter two.
- **Confidence:** **High**.

**F7 — HIGH — Plain water is a calorie source, including toxic and saline water**

- **Where:** `Defs/LiquidTypes/ThingDefs/RM_LiquidBottles.xml`. Fresh, salt, toxic and brine bottles/buckets all receive:
  ```xml
  <Nutrition>0.05</Nutrition>
  ```
  or:
  ```xml
  <Nutrition>0.25</Nutrition>
  ```
  together with `<preferability>DesperateOnlyForHumanlikes</preferability>`.
- **What happens:** These are nutrition-giving ingestibles. A starving colonist can obtain food nutrition from water: twenty bottles represent one nutrition unit. Toxic/saline classifications do not remove the positive Nutrition stat. The only wired custom outcome doer is `IngestionOutcomeDoer_BottleResidue`; its absent implementation prevents a conclusion about additional poisoning, but does not negate the declared calories. Vanilla’s `ThingDef.IsNutritionGivingIngestible` explicitly tests cached nutrition. [1.6 implementation](https://github.com/32bitx64bit/RW-Decompiled-1.6/blob/main/Verse/ThingDef.cs)
- **Repro:** Leave a hungry colonist without food but with bottled fresh water; inspect food-need change after ingestion. Repeat with toxic water.
- **Suggested check — offline resolved-def assertion:** Require zero nutritional value for plain-water containers unless feeding pawns with water is an explicit design decision.
- **Confidence:** **High**.

**F8 — MEDIUM — Hazardous canal fills retain recreational-water eligibility**

- **Where:** `Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml`. Oil, poison and fuel tiers include:
  ```xml
  <li>Water</li>
  ```
  plus freshwater tags, and their superdeep tiers explicitly declare `<passability>Standable</passability>`. None carries the exclusion used by `Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml`:
  ```xml
  <li Class="RimMandrake.FlowWorks.ManyWaters.RM_NoRecreationalSwimExtension" />
  ```
- **What happens:** The supplied DeepSand documentation identifies the vanilla `JoyGiver_GoSwimming.TryGiveJob` eligibility path as water plus standability. The hazardous fills satisfy that same classification without the marker that excludes DeepSand. Poison is particularly concerning because its harm is declared on the FluidDef, while its terrain does not declare `<dangerous>true</dangerous>`. Vanilla `TerrainDef.IsWater` is simply the `Water` tag check. [1.6 implementation](https://github.com/32bitx64bit/RW-Decompiled-1.6/blob/main/Verse/TerrainDef.cs)
- **Repro:** Provide an accessible shallow poison/oil canal as the nearby swimming opportunity for a recreation-seeking colonist.
- **Suggested check — cheap live query:** Request swimming-job eligibility on those cells. First inspect the omitted swimming postfix for a broader hazardous-liquid veto; the XML supplies none.
- **Confidence:** **Medium**; an additional C# exclusion could prevent the outcome.

## Outside this slice

The following implementations are needed to confirm the bounded runtime consequences above:

- `FluidDef`, `LiquidDef`, `RM_FluidIdentity` and pump/transfer readers: missing mappings, defaults and fallback identity.
- `CompLiquidConverter` / `RM_ConversionMath`: reject-stream accounting.
- The reader of `coolsToGlassEdge`.
- `RM_ContainerMaterials`, `IngestionOutcomeDoer_BottleResidue`, the swimming postfix, and DBH’s water consumers.

Save/load, earlier-save reloads, static collection lifetime, map removal, path-cache invalidation, Harmony targets and tick costs require the actual component/patch implementations named in the csproj. Their inclusion in the project proves compilation intent, not correct lifetime behavior.

No supplied file block appeared truncated. The ledger explicitly says its item heads are truncated; generated terrain families were intentionally omitted.