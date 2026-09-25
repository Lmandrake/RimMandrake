# Deepfire — luminous pigment mod (`LuminousPigment`) — design spec

**Status: RULED 2026-09-25 (three §11 cards, 15:42–16:16) — nothing built.** Every ruling cited
is from the ledger item; the one choice still open is §11 Q5, which FOUNDRY starts on its default.
Mod folder `src/RimMandrake/LuminousPigment` · packageId `mandrake.rm.luminouspigment` ·
prefix `RM_` · namespace `RimMandrake.LuminousPigment` · RimMandrake tier (no Star Wars IP).
Authority on rulings: `DEEPFIRE_PIGMENT_MOD_1` (ledger). Research it builds on:
`Transient/pigment_research/` (engine_feasibility, painting_integration, mods_and_games,
real_world_lacquer) — shelf life ~14 days; anything load-bearing is restated here.

## 1 Overview and fantasy

**Deepfire** is a luminous pigment. It carries no colour of its own: mixed into ordinary dye it
makes whatever colour the dye gives *glow* — a dim, steady, coloured light that a wall, a chair, a
statue, a robe or a rifle gives off in the dark. It comes from the oldest life on any planet:
**crowncarpet**, a rainbow bacterial mat that grows on ocean shores (rarely) and carpets the
margins and the floor of a boiling sea (the Scald, in the Utinni campaign — where the great
bottom-walkers lay it down behind them as they pass). A fresh mat dies within a day, and dies at once if chilled, so
the whole economy is a race from shore to press. A colony that masters it lights its halls with
colour instead of fire, raises its art by one grade, dresses its notables in light — and marks
every glowing pawn as a target on a dark night.

What the player gets, in one line each (rulings, `DEEPFIRE_PIGMENT_MOD_1`):

- A rare wild resource (crowncarpet) with a one-day clock and a "do not refrigerate" trap.
- A new powered bench (the Deepfire press: a press and an alchemical setup welded together) that
  refines fresh crowncarpet + a fixative into Deepfire, gated by research discovered on first
  seeing a mat. In the campaign the fixative is **Stillfluid**, the Poison Forest's universal
  preservative, from the Thornwillow.
- The GlowTank: a hydroponics-like culture tank, very low yield, moderate power/space/cost.
- A paint job: Deepfire + dye onto walls, floors, furniture, art, apparel, weapons. Colour from the
  dye; glow from the pigment; up to three coats, later coats only brighten. Worn items are
  lacquered at the press or, with Ideology, at the styling station.
- First coat: +1 quality on art, +beauty on everything else (flat + % of existing, size-scaled);
  floors get glow, per-tile beauty and a room bonus per 10 coated tiles.
- Worn Deepfire = a real moving light around the pawn, and a pawn easier to hit in the dark. It
  is light like any lamp's: darkness precepts and Anomaly's darkness treat the pawn as lit.
- Status: Deepfire-lacquered apparel and furniture run through a sumptuary-reaction engine
  (the "purple engine", named for Tyrian purple) — titled/high-status pawns pleased to wear and
  own it, low-status wearers draw titled pawns' disapproval. Reactions only: no law, no
  confiscation, no incident.
- Gods: every god likes it, the trade/craft trio adores it, Ishko the Unmaskable dislikes it;
  every god but Ishko loves it on his own statue.
- Cuisine: Deepfire dishes give permanent glow-conditions from a list of effect families, at
  most three per pawn; a skilled chef steers which family, an unskilled one rolls — and the
  prestige family (the vermilion) is master chefs only, never a lottery.
- Everything above is a Mod Settings toggle or number (§7).

**What is NOT in it:** curing (dropped — owner, typed: *"Curing sounds good but I'm not sure how to
achieve that since it can be used on so many item types, so best to drop it."*); hue-cycling or
shifting-colour light (disliked — it clashes with the ship's god-mood lighting language,
`ship_distinctive_features.md` §9); specular shine (impossible in the engine,
`engine_feasibility.md` §4); hair/skin dye; a "rainbow" colour of its own.

**Tier and dependencies.** RimMandrake tier: every name here is invented (Q11a), nothing is Star
Wars IP. Hard dependency: Harmony. Soft (reflection, never an assembly reference): FlowWorks
(`mandrake.rm.flowworks`, ocean water for the tank), Ninefold (`mandrake.rm.ninefold`, god
reactions), the Utinni statues mod (`mandrake.rut.utinnistatues`, statue reactions), Dub's Paint
Shop (floor colour grid), Royalty/Ideology (status ranks, styling station). The Scald
(TerminalBiomes, `mandrake.rm.terminalbiomes`) gains a **hard** `modDependencies` + `loadAfter`
on this mod (§2.1). The campaign's Stillfluid recipe is a Utinni patch (§2.3), not a dependency
of this mod.

## 2 The chain: mat → press → GlowTank

### 2.1 What moves out of TerminalBiomes (the Scald)

Today the Scald mod carries the placeholders. Both move here; the Scald keeps only its biome-side
use of them.

**The mat is named crowncarpet everywhere** (owner, typed, 2026-09-25 16:16: *"Crowncarpet"*). The
name *welcome blanket* is retired from every def, label, description, letter and doc — the
renames are listed below and in §2.2, and the design docs that still carry the old name
(`sea_dive_maps_spec.md`, `design/Jawa/worldbuilding/biomes/the_scald.md`,
`sea_catch_rosters_2026-09-24.md`, `fish_bestiary_commission_2026-09-10.md`,
`README_BIOME_GRAMMAR.md`; live XML `RM_TheScald.xml`, `RUT_TheScald.xml`, `RUT_ScaldMargin.xml`,
`RUT_ScaldFish.xml` ×2; `scald_showcase.py`) are corrected in the build step that moves the def.

| Today (TerminalBiomes) | Becomes (LuminousPigment) | The Scald keeps |
|---|---|---|
| `Defs/ThingDefs_Plants/RM_WelcomeBlanket.xml` (plant, label *welcome blanket*, harvests 4 pigment, grows only on terrain tag `RUT_ScaldMarginMat`, `maxGrowthTemperature 90`) | **`RM_Crowncarpet`**, label *crowncarpet*. Description generalised: shore life on any ocean, thickest where the water is hot; in the Scald, laid down by the bottom-walkers. Harvests **`RM_CrowncarpetFresh`** (§2.2), not pigment. `wildTerrainTags` = `RM_CrowncarpetBed` (new) **plus** the existing `RUT_ScaldMarginMat` string (string tag, no cross-reference — harmless when the Scald is absent). | Its `wildPlants` row `<RM_Crowncarpet>` at the Scald's high commonality; the `RUT_ScaldMarginMat` tag on `RUT_ScaldMargin`; the dive-floor harvest and the walker-laid mats in `sea_dive_maps_spec.md` (rename its references). |
| `Defs/ThingDefs_Items/RM_RainbowPigment.xml` (plain resource, MarketValue 3 placeholder) | **`RM_Deepfire`**, label *deepfire* (§2.4). `RM_RainbowPigment` is deleted, not aliased — nothing else references it (MEASURED: only the plant, `scald_showcase.py`, the frozen `RUT_TheScald.xml` twin whose dangling rows already wait on the repaint, and `sea_dive_maps_spec.md`). `scald_showcase.py` gets the new defName. | nothing |
| `Textures/Things/Item/Resource/RM_RainbowPigment/` (procedural placeholder) | replaced by the jar art the review sheet picks (§9) | nothing |

TerminalBiomes `About.xml` gains `<modDependencies>` on `mandrake.rm.luminouspigment` and the
matching `loadAfter`. `deploy_custom_mods.py` needs a unique folder name — `LuminousPigment`
collides with nothing (checked `src/RimMandrake/`). Save-compat: the campaign start save predates
both defs, so the rename costs nothing there; any scratch save holding `RM_RainbowPigment` loses the
stack (acceptable, `rimworld-savegame` skill's "dead name" class).

### 2.2 Crowncarpet and the one-day clock

Three sources, in rising order of yield (card 2: *"rare on any ocean shore standalone, far more
in the Scald"*; Scald floor sitting 2026-09-25 15:19, `SEA_DIVE_MAPS_BUILD_1`: the bottom-walkers
*"as they pass slowly over terrain PRODUCE the bacterial mats that make Deepfire"*):

- **Wild spawn, standalone (any ocean shore, rare):** a `GenStepDef` `RM_GenStep_ShoreMats` runs
  after terrain on any map whose biome is not the Scald: for each `WaterOceanShallow` cell adjacent
  to land, roll `shoreMatChance` (default 0.6%, §7) and plant a cluster of 1–3 `RM_Crowncarpet`.
  A patch adds the `RM_CrowncarpetBed` terrain tag to vanilla `WaterOceanShallow` so the plant may
  live there (the plant already ignores fertility). Regrowth after harvest is the plant's own
  `reproduceMtbDays`/`reproduceRadius` — ⚠️ UNMEASURED whether vanilla reproduction requires the
  plant in the biome's `wildPlants`; FOUNDRY reads `GenPlantReproduction.TryReproduceFrom` before
  relying on it, and the fallback is the GenStep re-seeding a cleared shore on a slow map-component
  timer (`shoreRegrowDays`, default 30). A coastal colony sees a few clusters per map, not a crop.
- **The Scald's shore margin:** the biome's `wildPlants` row carries the density; the
  `RUT_ScaldMarginMat` terrain tag does the placement — unchanged mechanism, moved authority.
- **The Scald's floor (the dive map, `sea_dive_maps_spec.md`):** crowncarpet is **produced by the
  bottom-walkers**. Each walker carries a `RM_CompMatLayer` (defined here, tagged onto the walker's
  PawnKind by the Scald's own patch under `MayRequire="mandrake.rm.luminouspigment"`): every
  `matLayIntervalTicks` (default 2500) while the walker is moving, it spawns one `RM_Crowncarpet`
  on a random cell it has just vacated if the cell carries the `RM_CrowncarpetBed` or
  `RUT_ScaldMarginMat` tag and holds no plant — so a walker's track is a slowly widening rainbow
  trail, and a diver harvests by following one. The floor terrain's `wildPlants` density for
  crowncarpet is **zero**: down there every mat is a walker's leaving, and killing the walkers
  ends the supply. Which walker defs exist, and their AI, is the dive-map spec's work; this mod
  ships only the comp.
- **Harvest:** `harvestTag Standard`, `harvestYield 4` → 4 × `RM_CrowncarpetFresh`,
  `harvestWork 120`, `growDays 3` wild (the mat is a film, not a tree).
- **`RM_CrowncarpetFresh`** — *fresh crowncarpet*. `ResourceBase`, stack 25, Mass 0.2,
  MarketValue 12 (it is a perishable rarity; traders never carry it). It carries
  **`RM_CompMatVitality`**, not `CompRottable`, because vanilla rot *slows* in the cold and the
  ruling is the inverse: *dies if refrigerated*. The comp (`CompTickRare`) keeps `ticksAlive`;
  at `matLifeDays` (default **1.0**, card choice) the stack becomes `RM_CrowncarpetDead` (inert,
  MarketValue 0.5, usable only as fertiliser-less filth-free junk — it exists so the player sees
  what happened rather than a vanished stack). If ambient temperature at the stack's cell is below
  `matChillKillTemp` (default **10 °C**) for one rare tick it dies immediately, with a message the
  first time per game (*"Fresh crowncarpet dies in the cold — refine it, don't refrigerate
  it."*). Inspect string shows *"alive: 14 h left"*. Carried in a caravan/inventory: `MapHeld` is
  null → use the caravan tile's outdoor temperature; the clock still runs.
- **Why a day:** the Scald is the far end of the campaign map and a coastal colony's shore is a
  walk away — one day makes the press a *shore* building and forbids stockpiling, without making a
  harvest party's return trip impossible. `matLifeDays` is a setting.

### 2.3 The Deepfire press

`RM_DeepfirePress` — *deepfire press*. Look: **a press and an alchemical setup welded together**
(owner, typed) — a screw press on one half, retorts and a coil on the other, both on one iron bed.
`WorkTableBase`-derived (`Building_WorkTable`), size **3×1**, `rotatable`, `Graphic_Multi`,
`altitudeLayer Building`, `passability PassThroughOnly`, flammability 0.4, `MaxHitPoints 200`,
`WorkToBuild 3000`, cost **steel 90 + component 3 + wood 30** (an early-industrial bench; it is
the research, not the bill of materials, that gates it), `workSpeedStat` none (the press is slow by
recipe). **Powered only** (card, 15:42): `CompPowerTrader` **150 W** (`pressPower` setting),
`CompFlickable`, `CompBreakdownable`; unpowered it runs no bill — there is no hand-cranked
variant, one def. `designationCategory Production`.

**Gate — Mod Settings, three values (card 1):** `pressGate` = `Research` (default, card choice) /
`Buildable` / `Unbuildable` (rare-lore: the press exists only where the scenario or a quest places
it). Under `Research`:

- `ResearchProjectDef RM_DeepfireRefining` — *Deepfire refining*, cost 800, techLevel Industrial,
  tab Main, prerequisite `Electricity` (the press is powered), `researchViewX/Y` beside Drug
  production. It is **hidden until a mat has been seen.** Discovery:
  `RM_GameComponent_Deepfire.matSeen` is set by `RM_CompMatDiscovery` on `RM_Crowncarpet` — on
  `PostSpawnSetup` and every 250 ticks while spawned, if the cell is unfogged and any player pawn
  is within 20 cells, set the flag, fire a `LetterDef.NeutralEvent` (*"Crowncarpet on the
  shore"*, once per game) and stop ticking. Hiding
  the project: Harmony prefix on `ResearchProjectDef.CanStartNow` returning false while unset,
  plus a postfix on the research tab's draw that skips it — ⚠️ the second hook's target is
  UNMEASURED (FOUNDRY finds where 1.6 filters hidden projects; Anomaly's
  `hiddenPrerequisites`/knowledge-gated projects are the precedent to copy if one fits, and the
  fallback is a visible-but-locked project with a red *"needs a mat sighting"* line in its
  description).
- Under `Buildable` the project is auto-completed at game start; under `Unbuildable` the press's
  `designationCategory` is nulled at startup (the statue-mod pattern, `statue_mods_spec.md` §1.5).

**Recipe `RM_RefineDeepfire`** — *refine deepfire*, `workSkill Crafting`, `workAmount 1800`,
Crafting XP, `skillRequirements` none:

| ingredient | count | why this one |
|---|---|---|
| `RM_CrowncarpetFresh` | 4 | one wild plant's harvest = one batch |
| `Neutroamine` | 1 | the **fixative**: vanilla's universal chemical precursor, trader-only, no colony synthesis without a mod — the one vanilla item that already reads as "the reagent you cannot make", so it puts the exotic-trader pressure the ruling wants on the base game without inventing a chemical |
| `Chemfuel` | 2 | the **solvent**: the extraction bath the mat is pressed in; cheap and colony-made, so the constraint stays on Neutroamine and on the mat's clock, not on fuel |

→ **2 × `RM_Deepfire`**. Two per plant is the rate every number in §3 and §7 is tuned against
(`pressYield` setting). The recipe ignores ingredient quality; product has no quality.

**Campaign (Utinni) variant — patch in `src/RimUtinni/UtinniPatches`, not this mod.** Owner,
typed, 2026-09-25 15:42: *"PoisonForest all the way. It's called Stillfluid, a sort of universal
preservative and fixative. Comes from the Thornwillow, a succulent-like tuberous growth that's
brightly colored, unattractive, and vaguely threatening-looking (very toxic)."*

- **`RUT_Stillfluid`** — *stillfluid*, the fixative. A **universal** preservative and fixative
  (his words), so it is a Poison Forest good in its own right, not a Deepfire-only reagent:
  Deepfire is its first consumer, and other recipes (taxidermy, preserved food, a mounted head)
  may take it later. Item def, ~ `Neutroamine`'s stats, exotic-trader stock; **defined by the
  Poison Forest mod**, not here.
- **`RUT_Thornwillow`** — the source plant: a succulent-like tuberous growth, brightly coloured,
  unattractive, vaguely threatening, **very toxic** (harvesting or eating it is a toxic-buildup
  event; the roster row and its def are the Poison Forest's work). Tapped or harvested for
  Stillfluid at a rate that biome's design sets.
- **`RUT_RefineDeepfireStillfluid`** — the campaign recipe on the press: 4 fresh crowncarpet +
  **1 `RUT_Stillfluid`**, no chemfuel (the fluid is solvent and fixative in one), yield **3**
  Deepfire instead of 2. `PatchOperationAdd` under `MayRequire="mandrake.rm.luminouspigment"` and
  `MayRequire` on the Poison Forest mod. Both recipes stay on the press in the campaign; the
  Stillfluid one is simply better, which is the cross-biome trade pressure the ruling wants — the
  Scald is the far end of the map and the Poison Forest is nowhere near it.

**Bench bills also here:** `RM_LacquerWornItem` is *not* a bill (a bill consumes and re-creates its
input, losing quality, hit points and comps) — worn-item application is a job at the press, §3.4.

### 2.4 Deepfire, the pigment

`RM_Deepfire` — *deepfire*. `ResourceBase`, `thingCategories ResourcesRaw`, stack 50, Mass 0.05,
Flammability 0.3, `DeteriorationRate 0.5`, **MarketValue 90** (a coat on a wall cell costs one; a
Legendary-adjacent quality bump costs two; the number is `deepfireMarketValue` and pricing is the
items pass's to retune). No rot, no clock — refined Deepfire keeps forever, which is the whole
point of racing to the press. It carries a `CompGlower` (`glowRadius 1.5`, colour a pale warm
white `(255,240,200)`, `glowColorOverride` unused): a stack on the floor glows faintly, so the
stockpile itself is the mod's first tell in a dark room (items on the ground are spawned and do
light — `engine_feasibility.md` §1). Traders: `tradeTags RM_Deepfire`, stocked by exotic goods
traders at 0–6 units (`TraderKindDef` patch, `MayRequire` none), never by bulk goods.

### 2.5 The GlowTank

`RM_GlowTank` — *glowtank*. **Hydroponics-like, very low yield, moderate power/resources/space**
(ruling). `thingClass RM_Building_GlowTank : Building_PlantGrower`, size **2×2** (four plant
cells), `fertility 1.0`, cost **steel 120 + component 4 + plasteel 10**, `WorkToBuild 4500`,
`CompPowerTrader 180 W` (a hydroponics basin is 280 W for four cells; the tank is cheaper to run
because it is slower), `CompFlickable`, `CompBreakdownable`, research `RM_DeepfireRefining` +
vanilla `Hydroponics`. `fixedPlantDefToGrow` = **`RM_CrowncarpetCultured`** (same art as the wild
mat, `growDays 12`, `harvestYield 2 × RM_CrowncarpetFresh`, `sowMinSkill 6`,
`fertilitySensitivity 0`). Four cells × 2 fresh mat per 12 days = **8 fresh mat = 2 batches = 4
Deepfire per tank per 12 days**: two coats on a chair a quadrum, which is "very low".

- **Seeding:** the tank must be seeded with a fresh mat before anything grows. `CompRefuelable`
  with `fuelFilter = RM_CrowncarpetFresh`, `fuelCapacity 1`, `fuelConsumptionRate 0`,
  `initialFuelPercent 0`, label *"seed culture"*; `RM_Building_GlowTank.CanAcceptSowNow` returns
  false while unfuelled. The mat's own clock does not run inside the tank (it is alive in culture).
  Losing power for `tankPowerGraceHours` (default 6 h) kills the four plants (vanilla
  hydroponics behaviour) *and* the seed culture, so a blackout costs a mat, not just a crop.
- **Ocean water (FlowWorks present only — card ruling: none needed without it):** when
  `mandrake.rm.flowworks` is loaded, `RM_PlaceWorker_GlowTankWater` requires at least one cell
  orthogonally adjacent to the tank to carry a FlowWorks liquid terrain of `RM_Liquid_SaltWater`
  or `RM_Liquid_BoilingWater` (the two ocean liquids in `RM_LiquidDefRegistry.xml`; brine is
  §11 Q5), and the same check runs each rare tick — dry tank = growth paused, inspect string says
  so. Resolution of "which liquid is on this cell" goes through FlowWorks by reflection
  (`RM_WorldComponent_LiquidTags`/terrain→liquid lookup — the exact accessor is UNMEASURED; the
  binding is soft, one `Type.GetType` with a warn-once, the `NinefoldBandBridge` shape). Without
  FlowWorks the tank needs nothing but power. `tankNeedsOceanWater` is a setting that can turn the
  requirement off even with FlowWorks present.
- Look: a squat glass-and-iron vat, two by two, the culture visible as banded colour inside, a
  dim glow (`CompGlower 2.0`, colour from the culture — static, pale) when seeded and powered.

## 3 Application: painting things with Deepfire

Architecture adopted from `painting_integration.md` §3 (research recommended; card 3 recorded
it): **a separate Deepfire designator + job is the core**, a `CompDeepfire` on every paintable or
colourable thing, colour read live from `thing.DrawColor`, one `MapComponent` owning every
Deepfire light as a proxy glower. No patch on any colour UI is load-bearing; vanilla dye menus,
Character Editor, Self Dyeing and Dub's Paint Shop all end in `Notify_ColorChanged`/`DrawColor`,
so Deepfire hears them for free (MEASURED there, §1–2).

### 3.1 The rule: colour from dye, glow from Deepfire

Deepfire never sets a colour. A thing's glow colour is **whatever it is currently painted**:
`Building.paintColorDef` → `CompColorable` → `ForceColor()` → stuff colour, i.e. `thing.DrawColor`.
An unpainted steel wall glows steel-grey; paint it blue afterwards and the glow turns blue the
same tick (`CompDeepfire.Notify_ColorChanged`). Floors read `TerrainGrid.ColorAt(c)`, and Dub's
Paint Shop floors its `MapComponent_PaintShop.GetColour` by reflection (§8). Normalisation: the
glow colour is the draw colour with its HSV value floored at `glowMinValue` (default 0.45) so a
near-black dye still lights — a very dark dye otherwise never crosses the engine's lit threshold
(`GameGlowLitThreshold` 0.3, `painting_integration.md` §3.3).

### 3.2 Coats and brightness

Up to **three coats** (card 1). `CompDeepfire.coats` ∈ 0..3, Scribed on the thing (survives
minify, haul, equip, caravan). Each coat costs the same again (§3.3). Coats change only the light:

| coats | radius (buildings/items/floor cells) | radius (worn) | intensity (× glow colour) |
|---|---|---|---|
| 1 | 1.5 | 1.5 | 0.45 |
| 2 | 2.0 | 2.0 | 0.70 |
| 3 | 2.5 | 2.5 | 1.00 |

All six numbers are settings (`coatRadius[]`, `coatIntensity[]`). "Dim" is the design: a
three-coat wall reads like a candle, never like a standing lamp (vanilla standing lamp radius
12). Night visibility = ordinary light: the glow grid does not know it is Deepfire, so work
speed, `PsychGlowAt`, Ideology darkness/light precepts, `Hediff_LightExposure` and Anomaly's
unnatural darkness all treat it as any lamp (ruling: *"night visibility = normal lights"*; card,
16:16: **Deepfire light counts as light** for darkness precepts and Anomaly — a Deepfire-lit
pawn is *in light*, is never "swallowed by darkness", and a lit hostile is un-hidden. That is
the meaning of *drives off darkness*; no exemption postfixes).

### 3.3 The designator and job

- **`RM_Designator_Deepfire`** — *apply deepfire* — sits beside vanilla Paint (same
  `DesignationCategoryDef` as `Designator_PaintBuilding`; FOUNDRY reads
  `DesignationCategories.xml` for the category name rather than guessing it). Drag-select like
  paint; valid targets: any spawned `ThingWithComps` carrying `CompDeepfire` with `coats < 3`,
  and any floor cell with a floor terrain (`TerrainDef.layerable`/`IsFloor`) with fewer than
  three coats in the floor grid. It shows the Deepfire cost of the selection in the mouse
  attachment (vanilla `Designator_Paint.DrawMouseAttachments` shape, reading `RM_Deepfire`
  counts instead of `Dye`). **`RM_Designator_RemoveDeepfire`** clears coats (no refund).
- **`RM_DesignationDef Deepfire`** carries nothing but the target; the coat count lives on the
  comp / floor grid, not on the designation.
- **`RM_WorkGiver_ApplyDeepfire`** (`workType Construction` for buildings/floors, `Crafting` for
  items — one WorkGiver, `workType` chosen by target; ⚠️ if a single WorkGiver cannot switch
  work types, ship two) → **`RM_JobDriver_ApplyDeepfire`**: fetch `cost` Deepfire from a
  stockpile (`PaintUtility.FindNearbyDyes` shape, our own def), go to target, `toil` 600 ticks ×
  `WorkSpeedGlobal`, Artistic XP 100 (paint's own skill), then `CompDeepfire.AddCoat(worker)`.
- **Cost per coat** (`RM_Deepfire` units, all settings): wall cell **1** · floor cell **1** ·
  furniture/building 1×1 **2**, larger **2 + 1 per extra cell**, cap 6 · art item **3** · apparel
  **3** · weapon **3**. "Expensive" (ruling) comes from the pigment's price and the press's rate,
  not from an exotic count: a 20-cell wall is 20 Deepfire ≈ five tanks' output for a quadrum.
- **`CompDeepfire`** is injected at startup by code (the Dub's Paint Shop `PaintableDefsInit`
  pattern) into every `ThingWithComps` def that satisfies `building.paintable` ∨ `IsApparel` ∨
  `IsWeapon` ∨ `HasComp(CompColorable)` ∨ `HasComp(CompArt)`, excluding `RM_Deepfire` itself,
  corpses, pawns, minified-thing shells and anything with `RM_DeepfireExcludeExtension`. Not an
  XML patch: the set must follow every other mod's defs, whatever load order.

### 3.4 Worn items — a real moving light, and a target

Apparel and weapons take Deepfire two ways:

1. **On the ground / in a stockpile**: the designator, as any item.
2. **While worn — at the press**: the pawn's own gizmo *"lacquer worn item…"* (drafted or not)
   lists worn apparel and equipped weapons with `coats < 3`; picking one queues
   `RM_JobDriver_LacquerWornItem` — fetch Deepfire, walk to a powered `RM_DeepfirePress`, 1000
   ticks, `AddCoat`. The press is the place because "you take it off at the bench" is the fiction,
   and it gives the press a second life after research.
3. **While worn — at the Ideology styling station** (card, 15:42: both places, not one): the
   station's `Dialog_StylingStation` gets a **per-item Deepfire checkbox** beside each apparel
   row's colour picker, enabled while the colony holds enough `RM_Deepfire` and the item's
   `coats < 3`; confirming the dialog adds the coat to the styling job's work and consumes the
   pigment when the job completes (postfix on `JobDriver_UseStylingStation`'s finish, reading a
   list of ticked items stashed on the job). Ideology absent → path 3 does not exist and nothing
   references the type (`MayRequire`-guarded assembly load or a reflection-resolved dialog patch —
   FOUNDRY picks the one the other Ideology-touching mods here use). Same cost, same `AddCoat`.

When a Deepfire-coated item is worn or equipped (`ThingComp.Notify_Equipped/Unequipped`,
`Notify_WearerDied`), `RM_MapComponent_DeepfireLights` owns **one proxy light per glowing
pawn** (not per item): colour = the brightest coat's colour blended across the pawn's glowing
items, radius = the pawn's highest coat. The proxy moves with the pawn: every `CompTickInterval`
15 ticks compare `pawn.Position` with the proxy's cell; on change `proxy.Position = cell;
glower.ForceRegister(map)`. Never spawn/destroy per step (the Rikiki pattern is the expensive
one; GravTide's map-component shape is the cheap one — `painting_integration.md` §4). Skipped
while the pawn is unspawned (caravan, carried, in a pod). **There is no off switch on a worn
glow** — that is the ruling's trade; a pawn who does not want to glow takes the robe off. **Card 3 owes a quicktest**
for the re-registered-per-cell proxy: build step 1 in §10.

**Easier to hit in the dark** (ruling), both DLC-free:

- Ranged: Harmony postfix on `ShotReport.HitReportFor` — if the target pawn has an active
  Deepfire glow and its surroundings are dark *without our light* (sky glow ≤ 0.35 outdoors, or
  `GroundGlowAt` minus our own contribution < 0.3 indoors), multiply the private
  `factorFromTargetSize` by `glowTargetFactor` (default **1.25**), clamped to vanilla's 0.5–2.
  Shows in the vanilla hit readout under "Target size"; a labelled *"glowing in the dark"* line
  via a `GetTextReadout` postfix. Compatible with Yayo's Combat 3 (MEASURED, it still calls
  `HitReportFor`). Combat Extended is not live and is out of scope.
- Melee: `RM_StatPart_GlowingTarget` on `MeleeDodgeChance` by XML patch — offset
  `−glowDodgePenalty` (default **−0.08**) under the same darkness test; explanation line free.
- Neither applies to a *lit* room: in light, a glowing robe is just a pretty robe.

### 3.5 First coat: quality or beauty

Applied once, on the first coat only (card 1); later coats never touch it. `CompDeepfire.bonusApplied`
is Scribed so removal-and-reapply cannot farm it.

- **Art items** (`CompArt` present — sculptures, the Utinni idols, art-bearing furniture):
  `CompQuality.SetQuality(q + 1, ArtGenerationContext.Colony)`, capped at Legendary (enum max;
  Legendary stays Legendary, and the coat is still charged). The art title/tale is kept as-is
  (`CompArt.InitializeArtInternal` returns early when titled — the ruling is +1 quality, not new
  art). A Masterwork sculpture becoming Legendary through Deepfire is the intended top of the
  line. Stacks split before the bump (`AllowStackWith` needs equal quality).
- **Everything else** — walls, floors excepted (below), furniture, apparel, weapons: `RM_StatPart_Deepfire`
  on `Beauty` (XML `StatDef[defName="Beauty"]/parts` patch) returning
  `beautyFlat × sizeFactor + beautyPct × baseBeauty` where `sizeFactor = min(area, 4)`
  (a 1×1 chair gets the flat once, a 2×2 table twice, capped — "scaled by size", card 1) and
  `baseBeauty` is the stat before our part. Defaults **flat 3, pct 25 %**, both settings. A
  wall (beauty 0) gets +3; a Good-quality steel bed (beauty ~6 with quality) gets +3 + 1.5.
- **Floors — all three** (owner, typed, 16:16: *"All three"*): glow (§3.6), a **per-tile beauty
  bonus**, and a **room bonus per 10 coated tiles**.
  - *Per tile*: floor beauty is `TerrainDef.statBases` read by `BeautyUtility.CellBeauty`, so a
    per-cell value needs a postfix there: `+= floorBeautyPerCell` (default **0.5**) for any cell
    with `floorCoats[c] > 0` — the signature is UNMEASURED; FOUNDRY reads `CellBeauty` and, if it
    is inlined or otherwise unpatchable, postfixes its caller `BeautyUtility.AverageBeautyPerceptible`
    over the visible cells instead. Same first-coat-only rule: the bonus is a function of coated
    or not, never of coat count.
  - *Per room*: `RM_RoomStatPart_DeepfireFloor` added to the `Beauty` `RoomStatDef`'s worker by
    postfix on `RoomStatWorker_Beauty.GetScore`: `+= floorRoomBonusPer10 × floor(coatedCells / 10)`
    (default **+2** per 10 coated cells, cap `floorRoomBonusCap` default **+10**). Shows in the
    room-stats readout as its own line. It counts coated floor cells only — walls are buildings
    and already carry the flat bonus above.

### 3.6 Walls, floors, furniture

- **Walls** are ordinary paintable Buildings — the comp path, cost 1. A long glowing wall is
  many lights; `RM_MapComponent_DeepfireLights` clusters **contiguous same-colour same-coat
  building cells into one proxy per 3×3 block** (average colour, radius = coat radius + 1) — the
  `CombineColorsJob` cost is lights × dirty cells, so a 400-cell hall must not be 400 lights
  (`painting_integration.md` §6). Cluster size `clusterBlock` (default 3) is a setting; 1 = no
  clustering.
- **Floors** have no comps. The map component holds a **per-cell byte grid** `floorCoats[]`
  (`MapExposeUtility`-style Scribe), lit through the same clustering and read by the two beauty
  hooks of §3.5. Postfix
  `TerrainGrid.SetTerrainColor` (recolour → relight; null → keep coats, colour falls back to the
  floor def's colour) and `TerrainGrid.DoTerrainChangedEffects` (floor removed or replaced →
  coats zeroed, no refund). Dub's Paint Shop floors: its colour wins when present (§8).
- **Furniture** is the comp path; minifying carries the comp; uninstall/reinstall relights on
  `PostSpawnSetup`.
- **Lights are never saved.** On map load the component rebuilds every proxy from comps + the
  floor grid + worn items (`FinalizeInit`), exactly as the engine rebuilds `CompGlower`s.

## 4 Status: sumptuary reactions

Ruling: *"lacquered apparel/furniture = status via the same engine as Tyrian purple"*; card 3
chose **sumptuary reactions** — nobles/high-status pawns pleased wearing/owning it, low-status
wearers draw titled pawns' disapproval — and the 15:42 card confirmed **reactions only**. **No
such engine exists yet** (MEASURED 2026-09-25:
`sumptuary`/`tyrian` match nothing under `src/`, `design/` or the live items — the "purple engine"
is the owner's name for the mechanism in `real_world_lacquer.md` §Tyrian purple, and Deepfire is
its first user). So this mod ships the engine as a **reusable, generic** piece in its own
namespace, and a future Tyrian-purple-like good hooks it with one `DefModExtension`.

### 4.1 `RM_SumptuaryEngine` (in `RimMandrake.LuminousPigment.Status`)

- **What counts as a status good:** any worn apparel / equipped weapon whose `CompDeepfire.coats
  > 0`, and any `RM_StatusGoodExtension`-tagged def (the hook for later goods; Deepfire is
  detected by comp, not by extension). A pawn's **display score** = Σ over worn goods of
  `coats` (0–3 each), capped at `displayCap` (default 6). A **room's** display score = Σ coats of
  Deepfire-coated furniture in it (walls/floors count 1 per 10 cells).
- **Rank** (the engine's one judgement, evaluated per pawn, cheapest first): Royalty title
  seniority (`pawn.royalty.MostSeniorTitle`, any title → *titled*) → Ideology role (leader /
  moral guide → *titled*) → otherwise *common*. A colony with neither DLC has no titled pawns;
  `ranklessColoniesEnjoyIt` (default on) then lets every pawn take the wearer's pleasure and
  nobody takes offence — the engine degrades to a plain "nice clothes" thought.
- **Thoughts** (ThoughtDefs, all durations/moods are settings):
  - `RM_WearingDeepfire` — situational, stages by display score 1–2 / 3–4 / 5–6: **+3 / +5 / +8**
    mood for *titled* wearers; for *common* wearers **+1 / +2 / +3** (they like it too — the
    engine is about who else minds).
  - `RM_DeepfireBedroom` — situational, *titled* pawn whose bedroom/throne room has room score ≥ 3:
    **+4**; ≥ 8: **+6**. Royalty's throne-room requirements are untouched.
  - `RM_WearsAboveStation` — **social**, held by *titled* pawns toward any *common* pawn with
    display score ≥ `offenceThreshold` (default 2): opinion **−15**, and a *titled* pawn seeing
    such a pawn (same map, `Notify_Seen`-free: evaluated on the situational-thought tick) gets
    `RM_SawCommonerInDeepfire` mood **−3** (24 h). The commoner feels nothing — Tyrian purple was
    a crime against the *court's* dignity, not the wearer's.
  - Guests, traders, quest lodgers: `RM_ImpressedByDeepfire` — a visiting titled pawn (Empire
    royals, faction leaders) on a map with room score ≥ 8 in any public room gives the colony a
    one-off goodwill **+2** per visit (`goodwillPerImpressedVisit`, cap once per faction per
    quadrum). Cheap, and it makes the paint a diplomatic instrument.
- **No law, no confiscation, no incident** (card, 15:42: reactions only). An Empire demand to
  surrender a commoner's lacquered garment was offered and declined; do not build one.

### 4.2 Why this shape

Thoughts and opinions are the engine's native currency: no new UI, they show in the needs tab
with the reason, and every number is a ThoughtDef stage the settings can scale. The generic
extension means the next status good (a future *porphyry* dye, a Utinni clan-mark) is one XML
tag, not a second engine.

## 5 The gods

Rulings (card 2): **all nine gods like it; the trade/craft trio — Mob'Unloo, Rekko, Zizzik —
adore it; Ishko dislikes it; every god but Ishko loves it on his own statue.**

### 5.1 Mechanism — Ninefold, softly

The god engine already exists: **`mandrake.rm.ninefold`** (`GameComponent_Ninefold.Instance`,
`ApplyDelta(God god, float amount, string reason)`, `EventMagnitude.Small 3 / Medium 8 /
Large 15`, `God` enum `Ishko, Ohm, Oomo, MobUnloo, Rekko, TaBaa, Zizzik, Shkaar, Ozzik` —
MEASURED `src/RimMandrake/Ninefold/Source/`). Deepfire binds to it **by reflection, no assembly
reference** — copy `src/RimMandrake/Aftermath/Source/NinefoldBandBridge.cs` (resolves the type,
`Instance`, `GetBand(God)` with a warn-once on shape change) and add `ApplyDelta`. Ninefold absent
→ every call is a no-op and this whole section is inert. `godsReact` setting gates it too.

### 5.2 The deltas

| event (`reason` string) | delta |
|---|---|
| first coat on any building/floor/item (`deepfire.coat`) | +Small to every god except Ishko; **+Medium** instead for Mob'Unloo, Rekko, Zizzik; **−Small** Ishko |
| second/third coats | nothing (adoration is for the act, not the wattage) |
| a *worn* item's first coat (`deepfire.worn`) | as above, and Ishko **−Medium**: a pawn who cannot be hidden is his particular offence |
| a Deepfire good sold or gifted (`deepfire.sold`, via a small postfix beside Ninefold's own `Patch_TradeCompleted`) | Mob'Unloo **+Medium** per deal containing one |
| a Deepfire dish eaten (§6) | Zizzik **+Small** (the spark), Ozzik **+Small** (pride) |
| a Deepfire coat applied to a **statue of a god** | that god **+Large**; all other gods +Small; Ishko's own idol: Ishko **−Large**, and the coat is allowed (the player may offend him on purpose) |
| a coated god-statue destroyed/deconstructed | that god −Medium (Ninefold's `Patch_BuildingDeconstructed` already covers plain destruction; ours adds the coat's weight) |

Amounts are per-event constants in settings (`godDeltaLike`, `godDeltaAdore`, `godDeltaIshko`,
`godDeltaStatue`), and every delta is rate-limited by Ninefold's own band ladder — Deepfire adds
no loop that could pin a god at Exalted by painting a hundred chairs: coats on the same *def*
after the first ten per game decay to +1 (`godDeltaDiminishAfter`, default 10).

### 5.3 Statues

The Utinni statue mod (`design/RimMandrake/statue_mods_spec.md`, `mandrake.rut.utinnistatues`,
not yet built) will ship one `Building_Art` def per god (`RUT_Idol_Ishko` … `RUT_Idol_Ozzik`).
Deepfire defines **`RM_DeepfireGodExtension { string god; }`** (the god's enum name as a string,
resolved by reflection against Ninefold's `God`); the statue mod tags each idol def with it under
`MayRequire="mandrake.rm.luminouspigment"`. Idols carry `CompArt`, so the first coat also gives
them the +1 quality of §3.5 — a Deepfire-coated Legendary idol of Rekko is the campaign's
high-art ceiling. The flame statues (`mandrake.rm.flamestatues`, spec §2) are paintable
buildings like any other; their own `RM_Comp_WarblingGlow` light and a Deepfire coat coexist
(two different glowers on the map, ours is the proxy, theirs is the comp — no shared
`thingIDNumber`, `painting_integration.md` §3.2).

## 6 Eating it: glow effect families via cuisine

Rulings (card 2, typed): *"body-glow + permanent-condition families … build a list then
normalize; low-skill chefs can't choose the outcome, higher-skill chefs steer toward chosen
families — a general theme for Cuisine."* And: *"They do NOT all need to have 'equal good and
bad.'"* So the list below is **not** balanced per family: some are mostly gifts, some mostly
curses, and the tier ladder is what is normalised.

### 6.1 Where it lives

"RimCuisine" in this project is our own **`mandrake.rsw.cuisine`** (`src/RimStarWars/Cuisine`,
live, `high_cuisine_deep_design.md`) — the galaxy-general cuisine mod, which the design already
names as the home of the chef-as-artist mechanic. Deepfire is RM-tier and must not depend on an
RSW mod, so: **the dishes and the family mechanism ship here** (invented names, Q11a), and the
Cuisine mod later adds its own Deepfire courses (the Ninefold Feast's glowing course) by
`MayRequire`. The **chef-steering mechanism is written as a generic component**
(`RM_CompSkillSteeredOutcome` + `RM_IngestionOutcomeDoer_SteeredFamily`) so Cuisine can reuse it
for any "the chef aims, the roll decides" dish — that is the *general theme for Cuisine* the
ruling asks for; the Cuisine mod's design doc gets a pointer, not a copy.

### 6.2 The dishes

At any stove (`RecipeDef`s, `workSkill Cooking`, `ProcessMeal`-style recipes, Cooking XP):

- **`RM_MealDeepfire`** — *deepfire dish* (any Cooking level): 1 `RM_Deepfire` + fine-meal
  ingredients (0.5 nutrition of meat and veg) → 1 meal, `preferability MealFine`, MarketValue 110.
  Eating it rolls a **random family** (weighted, §6.4) at **tier I** — never the vermilion.
- **`RM_MealDeepfire_<Family>`** — *deepfire dish (eye-glow)* etc., one recipe per family,
  `skillRequirements Cooking ≥ steerMinSkill` (default **10**; the vermilion's recipe **14**,
  `vermilionMinSkill`): same ingredients; eating it lands the **named** family with probability
  `steer(skill)` and otherwise a random other family (a missed vermilion re-rolls among the other
  thirteen — it is never handed out by accident).
  `steer(skill)` = linear from `steerMinSkill` → 50 % up to 20 → 100 % (`steerCurve` setting; a
  level-15 chef lands it 75 % of the time). The chef's skill at cook time is written onto the
  meal by a postfix on `GenRecipe.MakeRecipeProducts` (the `worker` is in scope there —
  `engine_feasibility.md` §2; exact signature FOUNDRY reads) into `RM_CompSkillSteeredOutcome
  { intendedFamily, cookSkill }`, Scribed on the meal.
- Eating the **same family again raises its tier** (I → II → III, permanent); a different family
  adds a second hediff. **Three families per pawn** (card, 16:01; `maxFamiliesPerPawn`, default
  **3**) — beyond that a dish does nothing but taste (the body has no more to give). Animals: no
  effect (`optimalityOffsetFeedingAnimals
  −50`). Nutrient paste never carries it.
- Every dish also gives the vanilla fine-meal taste thought plus `RM_AteDeepfire` (+2, 1 day —
  it tingles).

### 6.3 The families

Each family is one `HediffDef` with **three severity stages = tiers**, permanent (`isBad false`
so it is not tended; `everCurableByItem false`). The ladder is normalised: **tier I** is mild
and mostly cosmetic, **tier II** is where the stat effects bite, **tier III** is life-changing
and glows for real. "Glows" below means the family drives the pawn proxy light of §3.4 at the
stated radius (`RM_MapComponent_DeepfireLights` reads hediffs as well as worn coats); colour is
the family's own, fixed.

| # | family | hediff | what glows | tier I | tier II | tier III | lean |
|---|---|---|---|---|---|---|---|
| 1 | **Skin-glow** (owner: body part glows) | `RM_Glow_Skin` | one limb / torso patch, pale cyan; r 1.0 / 1.5 / 2.5 | Beauty +1; light r 1.0 | Beauty +2; glowing-target rule (§3.4) applies at night | Beauty +3; r 2.5; SocialImpact +10 % (people stare) | **gift** with a combat cost |
| 2 | **Eye-glow** (owner: eyes glow, blindness) | `RM_Glow_Eyes` | the eyes, gold; r 0.5 / 0.8 / 1.2 | Sight −10 %; night-work: no penalty from darkness for this pawn (`StatPart_Glow` exemption — UNMEASURED hook, else Sight only) | Sight −35 % | **blind** (Sight 0 %); the eyes are two coals, r 1.2 | **curse** with one gift |
| 3 | **Cranial glow** (owner: euphoria, major sleep disruption) | `RM_Glow_Cranial` | the skull, dim violet through the scalp; r 0.6 at III only | mood +4; RestFallRate ×1.15 | mood +8; RestFallRate ×1.4; Rest can't exceed 80 % | mood +12 (permanent euphoria); RestFallRate ×1.8; random *"lit dreams"* wake-ups (rest halts at 60 %) | mixed, tilted **gift** for a night-shift colony |
| 4 | **Neural glow** (owner: tremors, speed-up, sleep disruption) | `RM_Glow_Neural` | none visible until III (faint tracery, white) | MoveSpeed +0.1; Manipulation −4 % | MoveSpeed +0.25; Manipulation −10 %; RestFallRate ×1.25 | MoveSpeed +0.4; Manipulation −20 % (tremor); RestFallRate ×1.5; ShootingAccuracy −5 % | **mixed** |
| 5 | **Mouth-glow** (owner: ugliness, haggling buff) | `RM_Glow_Mouth` | the mouth, teeth and tongue, orange; r 0.5 / 0.7 / 1.0 | Beauty −1; NegotiationAbility +10 % | Beauty −2; NegotiationAbility +25 %; TradePriceImprovement +5 % | Beauty −3 (a lantern jaw); NegotiationAbility +40 %; TradePriceImprovement +10 %; SocialImpact +15 % | **gift** for a trader, curse for anyone else |
| 6 | **Body-products glow** (owner: ugliness, negative mood) | `RM_Glow_Products` | the pawn's filth: vomit, blood filth, and toilets (Dubs) glow — `RM_Glow` variants of the filth defs spawned in place of the vanilla ones (postfix `FilthMaker.TryMakeFilth` when the source pawn has the hediff) | Beauty −1; mood −2 (*"my leavings glow"*) | Beauty −2; mood −5; blood filth glows r 1.0 (a wounded pawn leaves a trail) | Beauty −3; mood −8; the pawn's *corpse* glows | pure **curse** — the joke family, kept because the owner named it |
| 7 | **Blood-glow** | `RM_Glow_Blood` | open wounds and bleeding, red; r 0.8 at any bleeding wound | MedicalTendQuality received +10 % (the surgeon sees everything) | +20 %; BleedRate ×1.15 | +30 %; BleedRate ×1.4; bleeding pawn lights r 1.5 | mixed, **gift** at I, dangerous at III |
| 8 | **Marrow-glow** | `RM_Glow_Marrow` | none visible; the bones are alight | ImmunityGainSpeed +10 %; HungerRate ×1.1 | +25 %; HungerRate ×1.25 | +45 % (shrugs off plague); HungerRate ×1.5; ComfyTemperatureMin +5 °C (runs hot) | **gift** paid in food |
| 9 | **Hair-glow** | `RM_Glow_Hair` | hair/fur, colour = hair colour; r 0.8 / 1.2 / 1.8 | Beauty +1 | Beauty +2; glowing-target rule applies | Beauty +2; r 1.8; the hair is a beacon: glowing-target factor ×1.5 instead of ×1.25 | cosmetic **gift**, combat curse |
| 10 | **Gut-glow** (the lantern belly) | `RM_Glow_Gut` | the belly, green, visible through clothes at III; r 0.6 | FoodPoisoningChance ×0.5 | immune to food poisoning; HungerRate ×1.15; Beauty −1 | immune; eats *anything* (`RM_Glow_Gut` III sets `foodType` acceptance like a Biotech robust-digestion gene — ⚠️ mechanism UNMEASURED, fallback: no ill effects from raw/rotten food thoughts); HungerRate ×1.3; Beauty −2 | **gift** for a scavenger |
| 11 | **Nerve-glow** (bright nerves) | `RM_Glow_Nerves` | none | PainFactor ×1.15; Consciousness +3 % | PainFactor ×1.35; Consciousness +6 %; MentalBreakThreshold +3 % | PainFactor ×1.6 (every scratch is a scream); Consciousness +10 %; WorkSpeedGlobal +5 % | **curse** with sharp gifts |
| 12 | **Pulse-glow** (the heart) | `RM_Glow_Pulse` | the whole pawn, dim, **pulsing at the heart rate** — reuse `RM_Comp_WarblingGlow`'s value-pulse parameters (`valuePulseFraction`, `primaryPeriodTicks`) on the proxy glower; hue fixed, no hue warble (the shifting-colour veto) | BloodPumping +5 %; r 0.8 pulsing | BloodPumping +12 %; MoveSpeed +0.05; r 1.2 | BloodPumping +20 %; heart attack chance ×2 (`HediffGiver_Random` on the hediff); r 1.8, the pulse visible across a dark room | **mixed**, the showpiece |
| 13 | **Lung-glow** (ember breath) | `RM_Glow_Lungs` | breath flecks in cold air, amber (a `CompFleckEmitterLongTerm` on the hediff's comp, `Fleck_RadialSparks` scaled down, `engine_feasibility.md` §3) | Talking +10 % | Talking +20 %; Breathing −8 % | Talking +30 %; Breathing −20 %; ToxicResistance +20 % (the fire cooks the air) | **mixed** |
| 14 | **Whole-body glow** (the vermilion) | `RM_Glow_Whole` | everything, the pawn's skin colour; r 1.5 / 2.5 / 3.5 | Beauty +3; glowing-target rule; mood +2 | Beauty +5; r 2.5; SocialImpact +15 %; RestFallRate ×1.2 | Beauty +8; r 3.5 (a walking lamp); factor ×1.5; RestFallRate ×1.4; **cannot be hidden** — Ishko −Medium on reaching III | the **prestige** family; **master chefs only** (card, 16:01): its steered recipe needs Cooking 14 and it is **never rolled at random** — weight 0 in the plain dish and excluded from every steered miss |

Fourteen families. Owner examples are 1–6 verbatim; 7–14 extend them along the same axes
(where it glows → what it costs → what it buys). Every stat in the table is a `HediffStage`
field or a `StatOffset`/`StatFactor` on the stage; the two flagged UNMEASURED cells (eye-glow's
darkness exemption, gut-glow III's diet) have XML-only fallbacks.

### 6.4 Random-roll weights and normalisation

The unsteered dish rolls with weights: families 1–6 (the owner's) **12 each**, 7–13 **6
each**, 14 **0** (the vermilion is steered-only — card, 16:01; the slider for it is fixed at 0
and not shown). A steered miss re-rolls with the intended family and the vermilion excluded.
Normalisation is
by tier, not by family: every tier I is ≤ ±1 Beauty / ≤ ±10 % on one stat and a light of ≤ r 1.0;
every tier II adds a second axis; every tier III is the family's full character. The
good/bad lean column is deliberate and unequal (ruling).

### 6.5 Chef steering as a general Cuisine theme

The comp/doer pair is family-agnostic: `RM_CompSkillSteeredOutcome` holds `intendedOutcome
(string)`, `cookSkill (int)`; `RM_IngestionOutcomeDoer_SteeredFamily` takes an `outcomes` list
of `{ key, hediff, weight, minSkillToSteer }` in XML and a `steerCurve` `SimpleCurve`. Cuisine's
later dishes (a diplomacy meal that lands the *intended* thought only from a skilled chef, a
feast course that is one of three flavours) reuse it as-is. Recorded here so the Cuisine doc's
next sitting can point at it rather than redesign it.

## 7 Mod Settings

Every-mod rule (`MOD_OPTIONS_RETROFIT_1`): `RM_LuminousPigmentMod : Mod` +
`RM_LuminousPigmentSettings : ModSettings`, `Scribe_Values` with defaults = the numbers in this
spec, real gates at the comp/map-component/patch level (never a stub), all-off = a mod that
loads and does nothing. Precedent shape: `src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs`.
Worldgen-affecting settings say so in their label. Grouped as the screen shows them:

**Chain**
| key | default | range | affects |
|---|---|---|---|
| `shoreMatsEnabled` | on | — | GenStep on non-Scald ocean maps *(new maps only — labelled)* |
| `shoreMatChance` | 0.006 | 0–0.05 | per shore cell *(new maps only)* |
| `shoreRegrowDays` | 30 | 0 (off)–120 | re-seed timer if vanilla reproduction proves absent |
| `matLifeDays` | 1.0 | 0.25–5 | fresh-mat clock |
| `matChillKillTemp` | 10 °C | −20–20 | dies below this |
| `pressGate` | Research | Research / Buildable / Unbuildable | §2.3 |
| `pressResearchCost` | 800 | 200–3000 | applied at startup to the project def |
| `pressYield` | 2 | 1–6 | Deepfire per batch (the Stillfluid recipe adds 1) |
| `pressWorkAmount` | 1800 | 600–6000 | |
| `pressPower` | 150 W | 50–600 | the press is powered only; 0 is not offered |
| `deepfireMarketValue` | 90 | 10–500 | applied at startup |
| `deepfireStackGlows` | on | — | the `CompGlower` on the pigment stack |
| `glowTankEnabled` | on | — | building in the menu |
| `tankGrowDays` | 12 | 4–40 | cultured mat |
| `tankYield` | 2 | 1–6 | fresh mat per plant |
| `tankPower` | 180 W | 0–600 | |
| `tankNeedsOceanWater` | on (only shown with FlowWorks) | — | §2.5 |
| `tankPowerGraceHours` | 6 | 0–48 | |

**Painting**
| key | default | range | affects |
|---|---|---|---|
| `paintingEnabled` | on | — | designators + WorkGiver; off = existing coats keep glowing, no new ones |
| `maxCoats` | 3 | 1–3 | card 1 ruled three; the slider cannot exceed it |
| `coatRadius` ×3 | 1.5 / 2.0 / 2.5 | 0.5–6 | |
| `coatIntensity` ×3 | 0.45 / 0.70 / 1.00 | 0.1–1 | |
| `glowMinValue` | 0.45 | 0–1 | dark-dye floor |
| `costWallCell` / `costFloorCell` / `costFurnitureBase` / `costFurniturePerExtraCell` / `costFurnitureCap` / `costArt` / `costApparel` / `costWeapon` | 1 / 1 / 2 / 1 / 6 / 3 / 3 / 3 | 0–20 | |
| `clusterBlock` | 3 | 1–5 | 1 = one light per cell/thing |
| `floorsPaintable` / `wallsPaintable` / `furniturePaintable` / `apparelPaintable` / `weaponsPaintable` | on | — | target classes |
| `wornLightEnabled` | on | — | the moving proxy; off = worn items glow only on the ground |
| `stylingStationLacquer` | on (only shown with Ideology) | — | the styling-station checkbox, §3.4 |
| `wornLightTickInterval` | 15 | 5–60 | cell-change poll |
| `glowTargetFactor` | 1.25 | 1–2 | ranged, in the dark |
| `glowDodgePenalty` | 0.08 | 0–0.3 | melee, in the dark |
| `combatPenaltiesEnabled` | on | — | both hooks |
| `artQualityBump` | on | — | §3.5 |
| `beautyFlat` / `beautyPct` / `beautySizeCap` | 3 / 0.25 / 4 | 0–20 / 0–1 / 1–9 | |
| `floorBeautyPerCell` | 0.5 | 0–5 | per coated floor cell, §3.5 |
| `floorRoomBonusPer10` / `floorRoomBonusCap` | 2 / 10 | 0–10 / 0–50 | room beauty per 10 coated cells, §3.5 |

**Status (the purple engine)**
| key | default | affects |
|---|---|---|
| `statusEnabled` | on | the whole engine |
| `displayCap` | 6 | |
| `offenceThreshold` | 2 | commoner display score that offends |
| `moodScale` | 1.0 (0–3) | multiplies every thought stage |
| `opinionAboveStation` | −15 | |
| `ranklessColoniesEnjoyIt` | on | no-DLC behaviour |
| `goodwillPerImpressedVisit` | 2 (0–10) | |

**Gods** (only shown with Ninefold loaded)
| key | default |
|---|---|
| `godsReact` | on |
| `godDeltaLike` / `godDeltaAdore` / `godDeltaIshko` / `godDeltaStatue` | 3 / 8 / −3 / 15 |
| `godDeltaDiminishAfter` | 10 coats per def |
| `ishkoIdolPaintable` | on (off = the designator refuses his idol) |

**Cuisine**
| key | default | affects |
|---|---|---|
| `cuisineEnabled` | on | all recipes hidden when off; existing hediffs stay |
| `steerMinSkill` | 10 | steered recipes' `skillRequirements` |
| `vermilionMinSkill` | 14 (10–20) | the whole-body family's recipe |
| `steerCurve` | 50 % at `steerMinSkill` → 100 % at 20 | two points |
| `maxFamiliesPerPawn` | 3 (1–14) | card ruled three |
| `familyEnabled[14]` | all on | a disabled family is neither rolled nor steerable |
| `familyWeight[13]` | 12×6, 6×7 | random-roll weights; the vermilion has none (steered-only, no slider) |
| `hediffGlowEnabled` | on | families' lights (off = stats only) |
| `effectScale` | 1.0 (0.25–2) | multiplies every stat offset/factor delta on every stage |

## 8 Compatibility

Live mods named in `painting_integration.md` §2 (MEASURED against `ModsConfig.xml` there;
re-checked 2026-09-25 against `infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml`, 627 active — `void.charactereditor`, `dubwise.dubspaintshop`,
`avilmask.selfdyeing`, `gravtide.mod`, `juanlopez2008.lightsout`, `temeez.floorlights2`,
`mlie.yayoscombat3` all present):

| mod | what Deepfire does | risk |
|---|---|---|
| **Vanilla paint / floor paint / styling station / Character Editor / Self Dyeing** | nothing — colour changes reach `CompDeepfire.Notify_ColorChanged` (things) or the `SetTerrainColor` postfix (floors); glow follows | none; the one gap is a mod that writes `CompColorable.color` by reflection without `Notify_ColorChanged` — the map component re-reads every proxy's colour on a slow 2500-tick sweep as a backstop |
| **Dub's Paint Shop** | things: free, as above. **Floors:** `RM_DubsPaintShopBridge` resolves `MapComponent_PaintShop` + `GetColour(IntVec3)` by reflection; when it returns a colour that cell's glow uses it instead of `TerrainGrid.ColorAt`; when DPS repaints (its own `SetColour` — postfixed by name, soft) the cell is relit. Its second colour (`PaintTo2`) is ignored | DPS ships only a DLL; method names are from the metadata dump and are re-verified at startup with a warn-once. Adding a Deepfire option inside `Dialog_BobRoss` is declined (transpiler on closed code) |
| **GravTide** (worn-apparel lights via its own `MapComponent_WornLights`) | tested together: a pawn wearing a GravTide lamp *and* a Deepfire robe has two lights (two different proxies, no shared id). No code binding | brightness stacking looks odd but is correct; `LightsOut`-style dousing is theirs |
| **LightsOut** | should ignore our proxies (no `CompFlickable`, no power). ⚠️ UNMEASURED — its target filter is checked in step 10 of §10; if it touches them, exclude by def name in its settings or postfix its filter | low |
| **Floor Lights 2** | unrelated; its lamps are buildings and remain paintable (glow + Deepfire glow) | none |
| **Yayo's Combat 3** | compatible: it still calls `ShotReport.HitReportFor` and rolls on a chance that includes `factorFromTargetSize` (MEASURED) | none |
| **Realistic Darkness** | makes "outdoors dark" common → the combat rule fires more; intended | none |
| **Royalty / Ideology** | rank source for §4; the styling-station checkbox (§3.4); darkness precepts and `Hediff_LightExposure` treat a glowing pawn as *in light* (MEASURED consequence, `painting_integration.md` §4; **ruled intended**, card 16:16) | none — Deepfire light is light |
| **Anomaly** | `SilhouetteUtility`/unnatural darkness: a Deepfire-lit hostile is un-hidden; a lit colonist is not "swallowed by darkness" (ruled intended, same card) | none |
| **Combat Extended** | not live; replaces `ShotReport` — out of scope, no guard needed beyond the postfix's null checks | — |
| **Ninefold / FlowWorks / Utinni statues / Cuisine** | soft bindings (§2.5, §5, §6.1), each a warn-once reflection with a no-op fallback | none |
| **Our own glowers** (`RM_Comp_WarblingGlow` on flame statues and gaslight lamps) | coexist; ours is a proxy, theirs a comp on the thing | none |

Save-compat: adds defs, one comp injected by code (absent comps deserialise as empty — the
injection runs before `Scribe` loads), one map component, one game component. Removing the mod
from a save: coats vanish, hediffs log the usual missing-def warning, nothing crashes.

## 9 Art needed

Checked first (rule of 2026-09-20): `infrastructure/artpipe/done/`, `_artsrc/`,
`registry.jsonl`, `art_status.json` and `Transient/*.decisions.json` for `pigment`, `blanket`,
`press`, `tank`, `deepfire`, `lacquer`, `dye`. Found and reusable:

| existing | state | reuse |
|---|---|---|
| `_artsrc/scald2_rainbowpigment_a/b/c` (three 512² jar renders, `SCALD_ART_UPGRADE_WAVE_1`, status ok, **no decisions file rules on them**) | finished, unruled | candidates for **the `RM_Deepfire` item icon** — go on the review sheet below, not picked by an agent |
| `_artsrc/rutwelcomeblanket_v1` (256², rainbow concentric mat, status ok; the artifact keeps its old name) | finished, unruled | candidate for **`RM_Crowncarpet` / `RM_CrowncarpetCultured`** plant graphic — on the sheet |
| `deeps_glowbulb_v2`, `glowstool`, `glowingagarilux`, `rutglower` | other subjects | none |

**Ruled (card, 16:16): the art goes to a review sheet** (`review-sheets` skill, one
`Transient/deepfire_art_*.html` + `.decisions.json`) holding **the three jars, the existing mat
render, and fresh variants** — two more jar variants (one pearl-white with a rainbow sheen, since
the pigment supplies glow rather than colour; one single glowing jar) and two more mat variants
generated with `rutwelcomeblanket_v1` as a style note (⚠️ never as `reference=`, that triggers
reskin-validate). The owner picks the jar and the mat set there; whatever he keeps is wired,
whatever he cuts is not regenerated. `Graphic_Random` on the plant wants 2–3 kept variants.

Owed (queue via `fill_queue.py` under `DEEPFIRE_PIGMENT_MOD_1`; the sheet's variants first, the
rest with it; sizes per `art-downscale-legibility` memory — 256 for 1×1, 512 for larger
footprints):

1. `RM_CrowncarpetFresh` — item: a folded, dripping rainbow sheet on a rack, 256².
2. `RM_CrowncarpetDead` — the same, grey and slumped, 256².
3. `RM_DeepfirePress` — 3×1 bench, `Graphic_Multi` (north/east/south; west mirrors): **a
   screw press and an alchemical retort/coil setup welded onto one iron bed**, a power cable
   or motor housing visible (it is powered), painterly (the art lawset), 768×256 south,
   matching sides.
4. `RM_GlowTank` — 2×2, `Graphic_Multi`, glass-and-iron vat with banded culture visible, two
   states if cheap (empty / seeded) — else one and the glow does the telling. 512².
5. Designator icons: *apply deepfire* (a brush with a glowing tip), *remove deepfire* — 64².
6. `RM_MealDeepfire` — a fine-meal plate with a faint glow line; 256². The steered variants
   reuse it with `Graphic_MealVariants` colour tints per family.
7. Research icon (optional; vanilla tab needs none).
8. Hediff icons: none (vanilla hediffs draw none).
9. Glowing filth variants (family 6): the vanilla filth textures with a `CompGlower` — no art.

Nothing here needs a canon reference (invented content); the art brief for every piece is the
one line above plus the `generating-rimworld-sprites` skill.

## 10 Build steps for FOUNDRY, with proofs

Ordered so every step ships something provable and the riskiest engine bet is first. Each proof
is a quicktest (`rimworld-debug-testing`) on the minimal list + this mod (+ the named soft
dependency where the step needs it); ALL five expansions stay on (owner ruling 2026-09-19).
Nothing here needs a cold load until step 12.

| # | build | proof |
|---|---|---|
| 1 | **Proxy-glower quicktest** (card 3's owed test): `RM_MapComponent_DeepfireLights` + `RM_DeepfireLight` proxy def + dev `[Tool]` in JawaBench (`rimbridge-companion`) `deepfire/light_test` that registers an unspawned proxy at a cell, moves it every 15 ticks along a path, and reads `map.glowGrid.GroundGlowAt` at the old and new cells | bridge: glow at the new cell > 0.3 and at the old cell = 0 within one frame of the move, for 50 moves, no log errors. **If the unspawned proxy does not light, switch the proxy to a spawned invisible 1×1 Thing (`drawerType None`, `selectable false`) and re-run** — `painting_integration.md` §6 names both shapes; decide here, before anything depends on it |
| 2 | Defs: `RM_Deepfire`, `RM_CrowncarpetFresh`/`Dead` + `RM_CompMatVitality`, `RM_Crowncarpet` (moved from TerminalBiomes, §2.1 — every *welcome blanket* string and `RM_WelcomeBlanket` reference in the files §2.1 lists renamed in the same commit), `RM_CrowncarpetBed` tag patch, `RM_GenStep_ShoreMats`, `RM_CompMatLayer` (the walker comp, §2.2; its PawnKind patch is the dive-map build's); TerminalBiomes dependency + `wildPlants` rename; delete `RM_RainbowPigment` | `validate_patch.py --live --defs`; `refresh.py` then `measure count ThingDef` shows the four new defs and zero `RM_RainbowPigment`/`RM_WelcomeBlanket`; `grep -ril "welcome blanket"` over `src/` and `design/` returns only `_artsrc` paths and this spec's §2.1 rename note; quicktest on a coastal temperate map: mats on the shore (count via `jawa/list_things`), harvest one, fresh mat's inspect string counts down, `set_temperature` the stockpile to 0 °C → stack becomes dead mat within one rare tick; a test pawn given `RM_CompMatLayer` walked 40 cells over tagged terrain leaves mats behind it |
| 3 | `RM_DeepfirePress` (powered), `RM_DeepfireRefining` + discovery (`RM_CompMatDiscovery`, `RM_GameComponent_Deepfire`), `RM_RefineDeepfire`, `pressGate` setting; the Utinni `RUT_RefineDeepfireStillfluid` patch (recipe only — `RUT_Stillfluid` and `RUT_Thornwillow` are the Poison Forest's defs, and the patch is `MayRequire`-guarded on that mod) | quicktest: project not startable before a pawn nears a mat, startable after (letter fires once); complete it via dev, build the press, unpowered press runs no bill, powered bill runs with 4 mat + 1 neutroamine + 2 chemfuel → 2 Deepfire; the Deepfire stack glows (`GroundGlowAt` > 0 at its cell) |
| 4 | `RM_GlowTank` + `RM_Building_GlowTank` + `RM_CrowncarpetCultured`; FlowWorks PlaceWorker/water check | quicktest without FlowWorks: unseeded tank refuses sowing, seeded tank grows, harvest yields 2 fresh mat per plant; power cut 6 h kills culture. With FlowWorks: placement refused away from a salt/boiling canal cell, accepted beside one |
| 5 | `CompDeepfire` injection + `RM_Designator_Deepfire`/`Remove` + designation/WorkGiver/JobDriver + coats → proxies (things) | quicktest: designate a steel wall segment, a wooden chair and a sculpture; pawn fetches Deepfire, applies; `GroundGlowAt` beside each > 0 with the thing's draw colour; paint the wall blue with vanilla paint → glow turns blue (read `GlowGrid` colour at the cell); three coats raise radius; fourth refused; remove → 0. Minify the chair, reinstall → still glowing. Save/load → still glowing |
| 6 | Floors: floor grid, `SetTerrainColor` / `DoTerrainChangedEffects` postfixes, clustering, the `CellBeauty` and `RoomStatWorker_Beauty` hooks (§3.5) | quicktest: paint a 6×6 floor, Deepfire it → glow, one proxy per 3×3 block (dev overlay lists 4 proxies); vanilla-paint the floor red → red glow; remove the floor → grid zero, no light; a room's Beauty readout rises by 36 × 0.5 per-cell plus the +6 room line (3 × 10 coated cells) and drops back on removal |
| 7 | First-coat bonus: quality bump + `RM_StatPart_Deepfire` on Beauty | quicktest: Normal sculpture → Good after one coat, unchanged after the second; Legendary stays Legendary; chair Beauty stat card shows the part line with the right number; remove + reapply does not re-bump |
| 8 | Worn items: `Notify_Equipped` path, per-pawn proxy, gizmo + `RM_JobDriver_LacquerWornItem`; the Ideology styling-station checkbox; combat hooks | quicktest at night on an unlit map: pawn in a coated parka walks 30 cells — `GroundGlowAt(pawn.Position)` > 0.3 every 15 ticks along the path (bridge poll, not screenshots); hit-chance readout on a shooter targeting the pawn shows the *glowing in the dark* line and a larger chance than against an uncoated twin (`spawn-many-for-bridge-tests`: 20 pairs, compare `HitReportFor` numbers directly, no live shooting needed); melee dodge stat card shows the offset; with Ideology, a styling job with the box ticked consumes 3 Deepfire and the worn item reads `coats 1` |
| 9 | Status engine + thoughts | quicktest with Royalty: titled pawn wearing 2 coats shows `RM_WearingDeepfire` stage 1; a commoner with 2 coats → titled pawn's opinion −15 and the −3 mood; no DLC → only the wearer's thought |
| 10 | Ninefold bridge + deltas; `RM_DeepfireGodExtension`; LightsOut check | quicktest with Ninefold: `GetSatiation` before/after one coat shows +3 on eight gods, +8 on the trio, −3 Ishko; a tagged test idol def → +15 on its god. With LightsOut: proxies survive an empty room being "switched off" |
| 11 | Cuisine: 15 recipes, 14 hediffs, comp + doer, filth variants, pulse reuse of `RM_Comp_WarblingGlow` params | quicktest: level-3 chef cooks the plain dish → random family at tier I (40 pawns, all 13 rollable families appear, the vermilion **never**, weights roughly right); level-20 chef cooks *eye-glow* → 20/20 land it; the vermilion recipe is absent from a level-13 chef's bill list and present at 14; second helping → tier II; fourth family refused; a tier-III skin-glow pawn lights its cell; pulse-glow's light value oscillates (read `GlowGrid` twice 100 ticks apart) |
| 12 | Mod Settings screen, every key in §7 wired; About.xml, `.csproj` with every `.cs` in `<Compile Include>` (the `EnableDefaultCompileItems false` trap); art wired; `validation.py` | build clean; all-off quicktest: nothing spawns, nothing paints, no errors; **cold load on the full list** (`COLD_LOAD_RUN_SHEET_*`) with the Player.log strings for each def written before launch (`rimworld-load-round`) |

Flight of any kind: none — nothing here flies. Bridge holds per step, released after each.

## 11 Open questions for the owner

One remains; FOUNDRY starts on its default. (Q1–Q4 and Q6–Q12 were ruled on the three cards of
2026-09-25 15:42–16:16 and are folded into the sections above — the numbering is kept so the
ledger notes still resolve.)

- **Q5 — GlowTank water when FlowWorks is present.** (a) salt or boiling water (**default**,
  §2.5); (b) brine also (the Grey Sea's liquid); (c) any water at all.
