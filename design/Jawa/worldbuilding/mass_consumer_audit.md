# Mass / bodySize consumer audit — the complete blast radius

**Status: AUDIT COMPLETE, 2026-09-05.** Answers the owner's instruction in
`creature_normalization_doctrine.md` §"Everything else that reacts to mass":
*"Armor and pit trap activation mass and anything else that reacts to damage and
mass."* This doc is the COMPLETE, verified consumer list. It documents only —
no def or generator was edited.

Every row is tagged **MEASURED** (read in the decompiled 1.6 source or the Core
def XML, with file:line) or **INFERRED** (a judgement built on those).

Source roots: the decompiled tree behind `mcp__rimsage__*` (`Source/Verse`,
`Source/RimWorld`) and `Defs/Core/**` as shipped.
Companion docs: `creature_normalization_doctrine.md` (the rulebook),
`creature_size_model.md` (what the engine does with `bodySize` vs `drawSize`).

---

## 0. The one-paragraph answer

`bodySize` is read in **~45 distinct engine places**. Only **five** of them go
through the `Mass` *stat*; the other forty read `Pawn.BodySize` directly. Mass
itself is a thin wrapper — `StatDefOf.Mass` base 1 × `StatPart_BodySize`
(`val *= bodySize`) — so **"renormalizing bodySize" and "moving Mass" are the
same act**, and every `StatDefOf.Mass` consumer in the game (all of them item-
and caravan-logistics) moves with it.

🔴 **The dangerous consumers are not the smooth multiplications — they are the
~20 hard numeric thresholds and the two non-linear curves.** A smooth `×
bodySize` scales predictably and can be reasoned about; a threshold flips a
behaviour on or off the moment a creature crosses it, silently, with no log
line and no error. §5 is the danger list.

---

## 1. Consumers of the **Mass stat** (`StatDefOf.Mass`)

**MEASURED.** `Mass` is defined in `Defs/Core/Stats/Stats_Basics_General.xml`
with `defaultBaseValue` 1 and `<li Class="StatPart_BodySize"/>`
(`Source/RimWorld/StatPart_BodySize.cs:5-28`, `val *= bodySize`;
`PawnOrCorpseStatUtility` supplies `pawn.BodySize` for a live pawn and
`race.baseBodySize` for a def-only request). So for any creature,
**`Mass (kg) = bodySize × 1.0`** — which is exactly why the doctrine's
`bodySize = kg / 70` anchor makes Mass literal at last.

| # | consumer | source | formula / threshold | changes under renorm? |
|---|---|---|---|---|
| 1 | **Corpse Mass** | `ThingDefGenerator_Corpses.cs:163` — `SetStatBaseValue(Mass, pawnDef.statBases.GetStatOffsetFromList(Mass))` | corpse def gets the race's Mass **offset**, generated at load | **YES** — corpse hauling/caravan weight moves with the creature |
| 2 | **Pawn carry / encumbrance** | `MassUtility.cs:22-34` | `IsOverEncumbered` when `GearAndInventoryMass / Capacity > 1`; `Capacity = BodySize × 35` (`:85`) | **YES** — a pack animal's usefulness is linear in bodySize |
| 3 | **Caravan mass usage/capacity** | `CollectionsMassCalculator.cs:40,48,70,78` | sums `GetStatValue(Mass)` over pawns + items | **YES** — a caravan of renormalized animals weighs itself differently |
| 4 | **Caravan forage cap** | `Planet/Caravan_ForageTracker.cs:74` | `FloorToInt((MassCapacity − MassUsage) / foodMass)` | **YES**, indirectly |
| 5 | **Load-transporter / trade / gift UI** | `Dialog_LoadTransporters.cs:557`, `Dialog_Trade.cs:119`, `TransferableComparer_Mass.cs:7`, `FactionGiftUtility.cs:113`, `CaravanThingsTabUtility.cs:125,132`, `TransferableOneWayWidget.cs:757`, `FloatMenuOptionProvider_LoadCaravan.cs:45,62,77` | display + sorting on Mass | **YES** (cosmetic + capacity) |
| 6 | **Quest/loot generators gated on max mass** | `ThingSetMakerUtility.cs:140,147,161,203,209`; `ThingSetMakerByTotalStatUtility.cs:196-341`; `ThingSetMaker_StackCount/Count/Sum` | `GetStatValueAbstract(Mass) <= maxMass` — **a hard threshold** | **only if a live animal is ever a ThingSetMaker candidate.** INFERRED: normally items only; a modded "reward: an animal" set maker would be affected |
| 7 | **Caravan-demand quest weighting** | `IncidentWorker_CaravanDemand.cs:212` | `Pow(MarketValue / Mass, 2)` | **YES** if an animal is demandable |
| 8 | **Raid loot distribution** | `RaidLootDistributor.cs:66-67` | budget `= 10 × Max(1, recipient.BodySize) − massGiven`; item `Mass` spent against it | **YES** — note the `Max(1, …)` floor: everything below bodySize 1 already behaves identically |

⚠️ **MEASURED, and important:** there is **no combat, damage, armour, trap,
stagger or predation code anywhere that reads the `Mass` stat.** Every combat-
adjacent size effect reads `Pawn.BodySize` directly. Mass is purely a logistics
number.

---

## 2. Direct readers of `Pawn.BodySize` / `RaceProperties.baseBodySize`

`Pawn.BodySize => ageTracker.CurLifeStage.bodySizeFactor × RaceProps.baseBodySize`
(**MEASURED**, `Source/Verse/Pawn.cs:2499`).

### 2a. Smooth multipliers — scale predictably, no cliff

| consumer | source | formula | effect of renorm |
|---|---|---|---|
| **MeatAmount** | `Stats_Pawns_General.xml:322-368` base **140**, `StatPart_BodySize` | see §3 — **non-linear postProcessCurve** | 🔴 see §3, this is not smooth |
| **LeatherAmount** | `Stats_Pawns_General.xml:370-397` base **0** (per-race), same parts | same curve | 🔴 see §3 |
| **CarryingCapacity** | `Stats_Pawns_General.xml`, base **75**, `StatPart_BodySize` | `75 × bodySize` | linear; hauling animals collapse at the small end |
| **MaxNutrition** | `Stats_Basics_General.xml`, base 1, `StatPart_BodySize` | `1 × bodySize` | linear |
| **Nutrition** (creature/corpse as food) | `Stats_Basics_General.xml:284-293`, `StatPart_BodySize` | `base × bodySize` | linear — a renormalized rat feeds almost nobody |
| **Caravan mass capacity** | `MassUtility.cs:10,85` — `MassCapacityPerBodySize = 35` | `BodySize × 35` | linear |
| **Food tank size** | `Need_Food.cs:77` | `MaxLevel = BodySize × CurLifeStage.foodMaxFactor` | linear — **time between meals**, not hunger rate (`Need_Food.cs:216` has no bodySize) |
| **Foraged nutrition/day** | `StatWorker_ForagedNutritionPerDay.cs:8,19,35` | `BodySize × 0.6` | linear |
| **Ranged hit chance vs target** | `ShotReport.cs:129`; `ShootTuning.cs:89,91` | `factorFromTargetSize = BodySize`, **clamped 0.1–2.0** | **saturating** — see §5 |
| **Stray-bullet interception** | `Projectile.cs:367,534` | `0.4f` / `0.5f × Clamp(BodySize, 0.1, 2)` | saturating, same clamp |
| **Pen / pasture load** | `AnimalPenBalanceCalculator.cs:46-62` | sums `BodySize` per district; better pen if `densityA × 1.2 < densityB` | **YES** — grazing pressure re-sorts entirely |
| **Caravan visibility** | `Planet/CaravanVisibilityCalculator.cs:13-26,56` | curve on **Σ bodySize**: `(0,0) (1,0.2) (6,1) (12,1.12)` | **YES** — see §5, curve saturates at 12 |
| **Rot stink volume** | `GasUtility.cs:14,96` — `RotStinkPerBodySize = 52` | gas amount `∝ corpse.InnerPawn.BodySize` | linear |
| **Blood filth on execution** | `ExecutionUtility.cs:19,24` | `Max(RoundRandom(BodySize × bloodPerWeight[=8]), 1)` | linear, floored at 1 |
| **Blood filth while bleeding** | `Pawn_HealthTracker.cs:1221-1223` | `chance = BleedRateTotal × BodySize × (standing ? 0.004 : 0.0004)` | linear. ⚠️ **this is filth drop chance, NOT the bleed rate itself** — see §6 |
| **Drug effect strength** | `AddictionUtility.cs:73,93-95`; `CompDrug.cs:42,88`; `IngestionOutcomeDoer_OffsetNeed.cs:21`, `IngestionOutcomeDoer_GiveHediff.cs:14,22` | `effect /= BodySize`; overdose `= overdoseSeverityOffset / BodySize` | **YES, inverse** — a renormalized small animal overdoses on a crumb |
| **Safe dose interval (UI)** | `DrugStatsUtility.cs:138-154,240` | `… / bodySizeFactor` | display only |
| **Heat pushed into the room** | `Pawn.cs:2792` | `0.3 × BodySize × 4.1667 × (humanlike ? 1 : 0.6)` | linear — barn temperature |
| **Bioferrite production (Anomaly)** | `CompProducesBioferrite.cs:30,41` | `BodySize × rate` | linear |
| **Hemogen from a victim (Biotech)** | `SanguophageUtility.cs:172` | `gain × victim.BodySize × …` | linear |
| **Toxic pack / gas dosing** | `CompToxPack.cs:28` | sums `pawn.BodySize` | linear |
| **Footprints / water ripples** | `PawnFootprintMaker.cs:49,59` (`√BodySize`), `PawnWaterRippleMaker.cs:35` (`Clamp(BodySize,0.5,2)×0.6`) | cosmetic | cosmetic only |
| **Selection ring size** | `TargetHighlighter.cs:67` | `bodySizeFactor × drawSize.y` | reads the LIFE-STAGE factor, not baseBodySize — unaffected by renorm of `baseBodySize`, see `creature_size_model.md` §1 |
| **Mote/head attach offset** | `MoteAttached.cs:51-53` | `animalHeadOffsets × BodySize` | cosmetic |
| **Inverse-bodySize hediff severity** | `Pawn_HealthTracker.cs:417-419`; `DamageDefAdditionalHediff.cs:17` | if `victimSeverityScalingByInvBodySize`: `severity *= 1 / BodySize` | 🔴 **inverse** — a renormalized rat gets a ~43× severity multiplier where it used to get 5× |
| **Devourer digest time (Anomaly)** | `CompDevourer.cs:244`, `CompProperties_Devourer.cs:24` | `bodySizeDigestTimeCurve.Evaluate(BodySize) × 60` | curve-dependent |
| **Nerve stun duration** | `DamageWorker_Nerve.cs:15-30` | curve `(0.01,3) (1,2) (2,2) (4,1)` sec × 2 × quality | **YES** — see §5 |
| **Herd-migration group size** | `IncidentWorker_HerdMigration.cs:15,116` | `Max(roll, CeilToInt(4 / baseBodySize))` — `MinTotalBodySize = 4` | 🔴 **YES, explosively** — see §5 |
| **Farm-animals-wander-in count** | `IncidentWorker_FarmAnimalsWanderIn.cs:13,58` | `Clamp(RoundRandom(2.5 / baseBodySize), 2, 10)`; chance curve on animal-bodySize-per-capita | clamped 2–10, so it saturates |
| **Ritual "farm animals wander in"** | `RitualAttachableOutcomeEffectWorker_FarmAnimalsWanderIn.cs:8,10,18` | `totalBodySize = 2` (positive) / `3` (best) | fixed budget ÷ bodySize → same explosive count as above |
| **Animal disease incident scaling** | `IncidentWorker_DiseaseAnimal.cs:28` | sums `v.BodySize` over candidates | **YES** |
| **Electroharvester power (Anomaly)** | `CompPowerPlantElectroharvester.cs:24` | `RoundToInt(HeldPawn.BodySize × … × 0.1)` | linear |
| **Wildlife/animals tab sort order** | `PawnTable_Wildlife.cs:13`, `PawnTable_Animals.cs:13` | orders by `baseBodySize` | cosmetic |
| **Quest node `GetBodySize`** | `QuestGen/QuestNode_GetBodySize.cs:14,21` | writes `baseBodySize` into a slate var | **YES** for any quest that reads it |

### 2b. `bodySize` provably does NOT drive (MEASURED by absence)

Re-verified against the full-source `BodySize` sweep for this pass; agrees with
`creature_size_model.md` §1:

- **Health / hit points** — `RaceProperties.baseHealthScale`, a separate field.
- **Melee damage or melee hit chance** — melee comes wholly from `tools`
  (`power`, `cooldownTime`). `bodySize` appears in no melee verb or damage worker.
- **Armour of any kind** — see §4.
- **Move speed**, **hunger *rate***, **pain/downed thresholds**, **combat power**.
- **Fence containment.** `RaceProperties.FenceBlocked => Roamer`
  (`RaceProperties.cs:386-388`) — 🔴 **a bool, with no size term at all.** The
  doctrine's "pen escape" worry does not exist as a size mechanic; only pen
  *density* (`AnimalPenBalanceCalculator`) is size-driven.
- **Wild-animal spawn density.** `PawnKindDef.ecoSystemWeight` is a
  hand-authored field; `WildAnimalSpawner.cs` reads it, never `bodySize`.
- **The renderer.** No draw path reads `baseBodySize` (`creature_size_model.md` §1).

---

## 3. YIELDS — what auto-scales and what does not

🔴 **This is the single most consequential section for the pass, and the answer
is NOT the simple "meat scales linearly" the doctrine assumes.**

| yield | auto-scaled by bodySize? | formula | base / per-def value | interval |
|---|---|---|---|---|
| **Meat** | **YES** | `140 × bodySize` × coverage × slaughter(0.66 if not carefully slaughtered) × difficulty × malnutrition-curve(1→0.4), **then a `postProcessCurve`** | base **140** (`Stats_Pawns_General.xml:322`) | per butcher |
| **Leather** | **YES** | same chain minus malnutrition | base **0**, per-race `statBases` override | per butcher |
| **Milk** (`CompMilkable`) | **NO — FLAT** | `RoundRandom(Props.milkAmount × fullness)` | `milkAmount`, flat int per def | `milkIntervalDays`, flat |
| **Wool** (`CompShearable`) | **NO — FLAT** | `RoundRandom(Props.woolAmount × fullness)` | `woolAmount`, flat int per def | `shearIntervalDays`, flat |
| **Eggs** (`CompEggLayer`) | **NO — FLAT** | `stackCount = eggCountRange.RandomInRange` | `eggCountRange`, flat IntRange | `eggLayIntervalDays`, flat |
| **Non-pawn `butcherProducts`** (mechanoids, some specials) | **NO — FLAT** | `RoundRandom(count × efficiency) × butcherYieldFactor` | flat `ThingDefCountClass` list | per butcher |

Sources: `RimWorld/StatPart_BodySize.cs:5-28`; `Verse/Pawn.cs:4233-4260`
(`ButcherProducts` — meat only if `RaceProps.meatDef != null`, leather only if
`RaceProps.leatherDef != null`); `Verse/Thing.cs:1937-1954`;
`CompProperties_Milkable.cs:5-19` + `CompMilkable.cs:5-50`;
`CompProperties_Shearable.cs:5-17` + `CompShearable.cs:5-46`;
`CompProperties_EggLayer.cs:6-42` + `CompEggLayer.cs:7-185`.

**Interval note (MEASURED):** the fill *rate* of milk/wool/eggs is multiplied by
`PawnUtility.BodyResourceGrowthSpeed` (`PawnUtility.cs:341-344`) — which is
`needs.food.CurCategory.HungerMultiplier()`, i.e. **hunger state, not bodySize**.
So no part of milk/wool/egg production touches size. ⇒ **All three must be set
explicitly per creature. Nothing will fall out.**

### 🔴 3a. The meat/leather `postProcessCurve` — a non-linearity nobody flagged

**MEASURED**, `Stats_Pawns_General.xml:363-370` and `:388-395`, identical on both
stats:

```
(0,0)  (5,14)  (40,40)  (100000,100000)
```

⇒ Below a raw value of **5** the game **inflates** the yield by up to **2.8×**
(the segment 0→5 maps onto 0→14). Between 5 and 40 it *compresses* (slope 0.74).
Above 40 it is 1:1. So meat yield is **piecewise-linear with a kink at raw 5 and
raw 40**, i.e. at **bodySize ≈ 0.036 and bodySize ≈ 0.286**.

**Worked example (INFERRED from the MEASURED curve):** a rat at today's
`bodySize` 0.20 → raw `140 × 0.2 = 28` → post-curve **≈ 31 meat**. Renormalized
to a real 0.32 kg rat (`bodySize` 0.0046) → raw 0.64 → post-curve **≈ 1.8 meat**.
A **17× cut**, not the 43× the linear reading would predict — the curve absorbs
some of it, which makes the error *harder to notice*, not smaller.

⚠️ Both kinks sit in exactly the region renormalization dumps the entire small-
animal population into. Any yield table computed as "old_meat × (new_bs/old_bs)"
will be **wrong for every creature under `bodySize` 0.286**.

---

## 4. ARMOUR — how it is actually sourced today

**MEASURED, and the answer is: nothing size-derived touches it, at all.**

- `ArmorRating_Sharp` / `_Blunt` / `_Heat` are defined in
  `Defs/Core/Stats/Stats_Apparel.xml` (abstract `ArmorRatingBase` at `:36`,
  the three at `:56/:83/:110`). `defaultBaseValue = 0`, `minValue 0`,
  `maxValue 2`. Their **only** StatPart is `StatPart_Stuff` (material/quality) —
  **no `StatPart_BodySize`, no mass part, no size part**.
- An animal's armour therefore comes from **plain `statBases` hand-authored on
  its ThingDef** (or an abstract parent). `AnimalThingBase`
  (`Races_Animal_Base.xml:49`) declares **no** ArmorRating, so armour is opt-in
  per species and **defaults to 0**.
- `ArmorUtility.GetPostArmorDamage` / `ApplyArmor`
  (`Source/Verse/ArmorUtility.cs:16-90`): apparel first, then the pawn's own
  `GetStatValue(armorRatingStat)`. `ApplyArmor` computes
  `num = Max(armorRating − armorPenetration, 0)`, then rolls `Rand.Value` against
  `num/2` (full deflect) and `num` (halve + convert sharp→blunt).
  **No bodySize or Mass term anywhere in that math.** The only size-adjacent
  branch is `metalArmor = RaceProps.IsMechanoid`, which changes only the
  deflect *sound/mote*, not the magnitude.
- There is **no `StatWorker_ArmorRating` class** — armour uses the default worker.

**Vanilla per-animal spread (MEASURED, `statBases`):**

| animal | Sharp | Blunt | Heat |
|---|---|---|---|
| Rat, Muffalo, Elephant, Rhinoceros, Megasloth, and most mammals | *(absent → 0)* | 0 | 0 |
| Tortoise (`Races_Animal_MiscGroup.xml:354`) | 0.50 | 0.35 | — |
| Thrumbo (`Races_Animal_MiscGroup.xml:15`) | 0.60 | 0.40 | 0.30 |
| Megascarab (`Races_Animal_Insect.xml:62`) | 0.72 | 0.18 | — |
| Megaspider (`Races_Animal_Insect.xml:320`) | 0.27 | 0.18 | — |
| Spelopede (`Races_Animal_Insect.xml:191`) | 0.18 | 0.18 | — |
| MechCentipede (`Races_Mechanoid.xml:71`) | 0.72 | 0.22 | — |
| Mech walker (Lancer/Scyther, `Races_Mechanoid.xml:276`) | 0.40 | 0.20 | — |

⇒ **MEASURED: vanilla armour has zero correlation with size.** A 4.0-bodySize
Elephant has none; a tortoise has 0.50. It is entirely an authored, lore-driven
per-def choice.

⇒ **INFERRED, and this is good news for the doctrine:** the doctrine's
integument-class table is **not overriding an engine behaviour** — it is filling
a vacuum. There is nothing to fight. We are free to author armour by integument
type with no engine term to cancel out. **`maxValue = 2` is the hard ceiling**
(200% armour); the "rhino at whale size is impervious" result must be reached at
or below 2.0, or by health, not by an armour number the engine will clamp away.

---

## 5. 🔴 THE DANGER LIST — every hard numeric threshold

These are the ones that flip a behaviour rather than scale it. Ordered by how
badly renormalization breaks them. All **MEASURED**.

| # | threshold | number | source | what changes when a creature crosses it |
|---|---|---|---|---|
| **1** | `TrainableDef.minBodySize` — **Haul** | **0.40** | `Defs/Core/TrainableDefs/Trainables.xml:74`; enforced `Pawn_TrainingTracker.cs:128,137,152` | Below it, the animal **cannot be trained to haul at all**. 🔴 Under `kg/70`, a 30 kg dog is 0.43 (*just* passes); a 4 kg cat is 0.057, a 20 kg husky-equivalent 0.29 — **most trained haulers stop qualifying**. Muffalo (500 kg → 7.1) still fine. This silently guts animal labour. |
| **2** | `TrainableDef.minBodySize` — **Rescue** | **0.65** | `Trainables.xml:54` | Same, for rescue. Under renorm only ≥45 kg animals qualify — plausible in-fiction, catastrophic if unintended. |
| **3** | `RaceProperties.maxPreyBodySize` | **0.25 – 3.0** vanilla (cat 0.25, fox 0.35, cougar/panther 1.0, wolf/warg 2.3, bear 3.0); modded set reaches **20** (`SeaBeasts_Sando.xml:66`) | `RaceProperties.cs:96`; enforced `FoodUtility.cs:781` | A predator refuses prey **above** this. 🔴 Renorm collapses prey bodySize far faster than these authored caps, so **every predator becomes eligible to hunt nearly everything, including colonists (human = 1.0 < 2.3)**. The `Sando` cap of 20 becomes "eats anything under 1.4 tonnes." **This must be renormalized in lockstep or predation goes feral.** |
| **4** | Predator/prey **win** ratio | `preyPower × BodySize ≥ predatorPower × BodySize` → refuse | `FoodUtility.cs:791-795` (plus a `combatPower > 2× predator` gate at `:787`) | bodySize appears on **both** sides, so the *ratio* is what matters — but `combatPower` is hand-authored and does NOT move with renorm, so the product shifts. **INFERRED: second-order, but it does move.** |
| **5** | **Ranged hit-chance clamp** | **0.1 – 2.0** | `ShootTuning.cs:89,91`; `ShotReport.cs:129`; `Projectile.cs:367,534` | Target-size factor saturates. 🔴 Under renorm **almost every animal pins to the 0.1 floor** (anything under 7 kg) and every large one pins to the 2.0 ceiling (anything over 140 kg). **The whole middle of the curve — where the mechanic is interesting — empties out.** Not a break, but a total loss of resolution. |
| **6** | `bed_maxBodySize` | **0.25** (crib/bassinet, `Buildings_Furniture.xml:176,214`), **0.55** (`Buildings_Furniture.xml:547`), default **9999** | `BuildingProperties.cs:178`; enforced `RestUtility.cs:426`, `CompAssignableToPawn_Bed.cs:77`, `CompAssignableToPawn_DeathrestCasket.cs:34`, `Pawn_AgeTracker.cs:604` (**unassigns a bed on growth**), `Building_Bed.cs:86`, `RoomRoleWorker_Nursery.cs:22,55` | Below/above → cannot use that bed; **an already-owned bed is silently un-assigned when a pawn grows past it**. These are compared against `bodySizeFactor` in some call sites and `BodySize` in others — mixing life-stage factor with absolute size. Renormalizing humanlikes (ruling 4) can move colonists across the nursery/crib line. |
| **7** | **Meat/leather `postProcessCurve` kinks** | raw **5** and raw **40** → `bodySize` **0.036** and **0.286** | `Stats_Pawns_General.xml:363-370, 388-395` | Yield is piecewise-linear, **not** proportional. Below 0.036 the game inflates by up to 2.8×. **Any yield recomputed by ratio is wrong for every creature under bodySize 0.286.** See §3a. |
| **8** | **Bullet stagger immunity** | `BodySize <= bullet.stoppingPower + 0.001` → **staggered** | `StaggerHandler.cs:49`; `RaceProperties.bulletStaggerIgnoreBodySize` (`:160`); vanilla `stoppingPower` values **0.5 / 1.0 / 1.5 / 2.0 / 2.5 / 3.0** (`Damages_Misc.xml:55,73,125`; `RangedIndustrial.xml`, `RangedNeolithic.xml`, `Weapons_Breach.xml:73`) | 🔴 **Inverted by renorm.** Today only sub-1.5-bodySize animals stagger; after renorm **every animal under ~210 kg (bodySize 3.0) is staggered by a breach shotgun, and everything under 70 kg is staggered by an ordinary rifle.** Small animals become permanently stun-locked by gunfire. This is the most invisible break in the list. |
| **9** | **Herd migration** min total | **4.0** total bodySize | `IncidentWorker_HerdMigration.cs:15,116` — `Max(roll, CeilToInt(4 / baseBodySize))` | 🔴 **Explosive.** A renormalized 0.32 kg rat gives `ceil(4 / 0.0046)` = **870 animals in one migration**. Nothing clamps it. **This will hang or crash a map.** Compare the wander-in incident, which *is* clamped 2–10. |
| **10** | **Farm animals wander in** | budget **2.5** (`:13`), ritual **2.0 / 3.0** | `IncidentWorker_FarmAnimalsWanderIn.cs:13,58`; `RitualAttachableOutcomeEffectWorker_FarmAnimalsWanderIn.cs:8,10,18` | `Clamp(RoundRandom(2.5 / baseBodySize), 2, 10)` — **clamped**, so it saturates at 10 rather than exploding. Safe, but the reward becomes "always 10 of the smallest thing." |
| **11** | **Cell sharing** | **1.5**, and a size ratio of **3.57** | `PawnUtility.cs:603-617` | Two pawns may share a cell only if **both** are under 1.5 **and** their size ratio exceeds 3.57. Under renorm nearly every animal drops under 1.5, so sharing becomes governed entirely by the ratio test — a large behavioural change in crowded pens/raids. |
| **12** | **"Large corpse" storage filter** | **0.75** | `SpecialThingFilterWorker_CorpsesLarge.cs:7,13,27,44` | A corpse is "large" at ≥0.75. 🔴 Under renorm, **almost nothing is a large corpse** (needs ≥52 kg), so stockpile filters authored around it silently stop matching. |
| **13** | **Meat texture selection** | **0.7** | `ThingDefGenerator_Meat.cs:105` | `baseBodySize < 0.7` → `Meat_Small` sprite, else `Meat_Big`. Cosmetic, but **every meat item in the game changes icon** under renorm. |
| **14** | **Snow-trampling** | **0.9** | `Pawn_PathFollower.cs:651` | `BodySize > 0.9` → clears 0.001 snow depth per cell. Under renorm only ≥63 kg animals clear snow. Minor, but visible. |
| **15** | **Anomaly / Biotech ability size gates** | Teleport **3.5** (`CompProperties_AbilityTeleport.cs:9`), ConsumeLeap **2.0** (`CompProperties_ConsumeLeap.cs:5`), Psychic Slaughter **2.5** (`CompAbilityEffect_PsychicSlaughter.cs:71`), Biomutation Lance **2.5** (`Verb_CastTargetEffectBiomutationLance.cs:20`), Fleshbeast **0.75 / 3.5** (`FleshbeastUtility.cs:53,233,237`), EmergeFromWater **1.5** (`PawnsArrivalModeWorker_EmergeFromWater.cs:69`) | enforced at those lines | 🔴 **All of these become "always allowed."** Every gate authored as "too big to teleport / consume / slaughter" fails open once real-mass numbers put nearly all animals under 1.0. |
| **16** | **Ideoligion animal-per-capita thoughts** | stages at **1, 2, 4, 6, 8** total bodySize per colonist | `ThoughtWorker_Precept_AnimalBodySizePerCapita.cs:32,45,50,84-87`; `ThoughtWorker_VeneratedAnimalOnMapOrCaravan.cs:32,42-45`; `PawnUtility.cs:1363-1411` | 🔴 Sums **BodySize across the colony's animals**. Under renorm the sum collapses; an "animal husbandry" ideoligion becomes permanently unsatisfiable unless the colony keeps literal tonnes of livestock. |
| **17** | **Caravan visibility curve** | `(0,0) (1,0.2) (6,1) (12,1.12)` on Σ bodySize | `Planet/CaravanVisibilityCalculator.cs:13-26` | Renorm collapses Σ bodySize for animal caravans → **caravans become nearly invisible**, changing ambush frequency. The curve saturates at 12, so pack-animal caravans of large beasts are unaffected. |
| **18** | **Nerve stun duration curve** | `(0.01,3) (1,2) (2,2) (4,1)` seconds | `DamageWorker_Nerve.cs:15-30` | **Inverted**: smaller = longer stun. Renorm pushes almost every animal to the 0.01 end → **max 3 s stun on nearly everything.** |
| **19** | **Ritual animal role** | `minBodySize` **0.75** (`Ritual_Behaviors.xml:526`) | `RitualRoleAnimal.cs:7,22-26` | Under renorm, only ≥52 kg animals can fill the role; smaller ones are rejected with a UI message. |
| **20** | **Raid loot budget floor** | `Max(1, BodySize)` | `RaidLootDistributor.cs:66` | Everything below bodySize 1 already behaves identically — renorm just moves more raiders under the floor. Benign. |
| **21** | **Pack-animal capacity gate** | `CanEverCarryAnything` → `RaceProps.packAnimal` bool | `MassUtility.cs:97-104` | Not a size threshold — a bool. Capacity is then `BodySize × 35`, so a renormalized pack animal's usefulness moves linearly. |
| **22** | **`ThinkNode_ConditionalBodySize`** | `min` / `max`, per-def | `ThinkNode_ConditionalBodySize.cs:14-17` | Any AI think-tree branch authored on a size window. **Vanilla usage not enumerated in this pass — UNCERTAIN, see §6.** |

---

## 6. 🔴 Corrections to the doctrine's existing list

The doctrine's §"Everything else that reacts to mass" list is **substantially
right but wrong in three places**, all MEASURED:

1. **"Pit-trap activation mass and anything else gated on Mass crossing a
   threshold" — THIS DOES NOT EXIST IN THE ENGINE.**
   `Building_Trap.SpringChance` (`Building_Trap.cs:116-141`) is the complete
   activation formula: `immuneToTraps` → 0; else a knower factor
   (same-faction **0.005**, wild animal **0.2** × `trapPeacefulWildAnimalsSpringChanceFactor`,
   factionless human **0.3**, other **0**); × `TrapSpringChance` (building stat)
   × `PawnTrapSpringChance` (pawn stat, `Stats_Pawns_Combat.xml:348-359`,
   `defaultBaseValue 1`, **no StatParts at all**). `Building_TrapReleaseEntity`
   overrides it to a flat **0**.
   **There is no mass term, no bodySize term, and no weight threshold in any of
   RimWorld's four trap classes** (`Building_TrapDamager`,
   `Building_TrapExplosive`, `Building_TrapReleaseHunter`,
   `Building_TrapReleaseWasp` — `Buildings_Security.xml` Core:137,186 and
   Odyssey:11,76). A grep of the deployed mod set for `minMass` / `massThreshold`
   / `activationMass` returns nothing.
   ⇒ **INFERRED: the owner is describing a mechanism he WANTS, not one that
   exists.** "Pit trap activation mass" is a **feature request**, not an audit
   finding. Treat it as new design work, and say so rather than "renormalizing"
   a number that isn't there.
   ⚠️ **Floor, not a census:** this grep covered the **75 deployed mod folders**
   (minimal list + our own mods), not the owner's full ~595-mod list. A mod not
   currently deployed could add one. **UNMEASURED for the full set.**

2. **"Pen space/load" is right; "pen escape" is not a size mechanic.**
   `RaceProperties.FenceBlocked => Roamer` (`RaceProperties.cs:386-388`) — a
   plain bool. Pen *density* balancing (`AnimalPenBalanceCalculator.cs:46-62`)
   is genuinely bodySize-driven; fence containment is not.

3. **"Bleed rate" is wrong.** `Pawn_HealthTracker.cs:1221` multiplies
   `BleedRateTotal × BodySize` to get a **blood-filth drop chance** — the bleed
   rate itself (`hediffSet.BleedRateTotal`) has no bodySize term. Renormalizing
   changes how much blood is on the floor, not how fast anything bleeds out.

**Also inconsistent inside the doctrine itself:** §"The whale test" still says
the result *"falls out of armour ∝ length together with health ∝ mass"* — but
the owner's own correction two paragraphs above replaced `armour ∝ length` with
integument-class-dominant. §4 above confirms the engine has **no** size term in
armour at all, so the surviving `∝ length` sentence should be struck.

**Everything else in the doctrine's list is CONFIRMED**: MeatAmount /
LeatherAmount carry `StatPart_BodySize` ✅ · CarryingCapacity ✅ · `MassUtility`
caravan capacity ✅ · trainability gates ✅ · predation thresholds ✅ · ranged
hit-chance clamped 0.1–2.0 ✅ · bullet-stagger immunity ✅ · Nutrition,
MaxNutrition, food-tank size ✅ · milk/eggs/wool needing explicit values ✅
(and now proven: **they are flat, nothing at all falls out**).

---

## 7. UNCERTAIN / not measured in this pass

- **`ThinkNode_ConditionalBodySize` vanilla usages.** The class exists
  (`ThinkNode_ConditionalBodySize.cs:14-17`) with `min`/`max`. I did not
  enumerate which vanilla or modded think trees instantiate it or with what
  bounds. **UNMEASURED — worth a targeted def sweep before applying.**
- **`CompProperties_Devourer.bodySizeDigestTimeCurve`** default points not read;
  only that it is evaluated on `BodySize`.
- **Modded C# consumers.** The decompiled tree is **vanilla only**. Any of the
  595 mods may Harmony-patch a bodySize consumer or add its own threshold. A
  live check (or a decompile sweep of mod assemblies) is the only way to close
  this, and it is the same blind spot `creature_size_model.md` §6 already names
  for the draw path.
- **Hediff / body-part armour offsets** for Anomaly entities were not
  exhaustively read; none surfaced in the size/mass StatPart search.
- **Full-mod-set threshold grep.** Only the 75 deployed folders were grepped
  (§6.1). The full ~595-mod list is **UNMEASURED**.
- **Whether any modded animal declares an `ArmorRating_Heat`** beyond the vanilla
  Thrumbo — not enumerated.

---

## 8. BIGGEST RISK — the one most likely to break unnoticed

🔴 **Bullet stagger immunity** (`StaggerHandler.cs:49`, danger-list #8), with
**herd migration** (#9) as the loudest and **trainability gates** (#1/#2) as the
most player-visible.

Stagger wins the "unnoticed" category because it has **no UI, no stat readout,
no log line, and no error**. `BodySize <= bullet.stoppingPower` is a silent
comparison against a weapon field nobody will think to look at. Today the
threshold separates small game (staggers) from large beasts (does not) — exactly
the design intent. After renormalization **every animal under 70 kg is staggered
by an ordinary rifle round and everything under 210 kg by a breach shotgun**,
which means most wildlife is permanently stun-locked the moment anyone opens
fire. It will read as "combat feels weird / animals don't close distance
anymore" many sessions later, and it will be attributed to anything but this.

Herd migration (#9) is more *severe* — an unclamped `4 / bodySize` spawning ~870
rats will hang a map — but it fails **loudly** on first occurrence, so it will be
caught. Trainability (#1/#2) fails loudly too, at the training UI.

**Mitigation for #8, if wanted:** `RaceProperties.bulletStaggerIgnoreBodySize`
(`RaceProperties.cs:160`) is a per-race opt-out that already exists — a cheap
explicit setting, exactly the "set deliberately, don't let it fall out" the
owner asked for.
