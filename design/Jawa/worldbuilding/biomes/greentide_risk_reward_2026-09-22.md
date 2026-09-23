# The Greentide as an exchange — audit, progression, and new reward categories

**Date:** 2026-09-22 · **Seat:** design pass for `GREENTIDE_RISK_REWARD_EXCHANGE_1`
**Status:** DRAFT — design only. No def, XML or art authored here.

> Owner's direction, 2026-09-22 (relayed, see the item's provenance note): *"The jungle should be
> filled with really intimidating dangers in terms of plants, beasts, diseases, and insects. That
> should in turn be countered with tremendous food abundance, unique medicines, a seemingly endless
> possibility for Star Wars cuisine ingredients, and… (get creative! come up with more rewards for
> braving this terrible place!)"*

---

## 1. Audit of the danger side

**Method.** Every figure below was parsed off files in this repo on 2026-09-22. There is no game, no
def dump and no decompiler on this machine, so nothing here is live-proven and no vanilla defName
appears that was not read from one of our own files.

🔑 **There are TWO Greentide BiomeDefs and they do not agree.** Both were read in full:

- `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml` — the franchise-free twin, the
  one that will carry the tiles after the terminal repaint.
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml` — **frozen 2026-09-22**, and the def
  the live saved world actually runs on today.

| field | `RM_Greentide` | `RUT_Greentide` (live) |
|---|---|---|
| `animalDensity` | 3.2 | 3.5 |
| `plantDensity` | 0.95 | 0.9 |
| `movementDifficulty` | **1.6** | **1** |
| `forageability` | 0.8 | 1.0 |
| `foragedFood` | `RawBerries` | `RawBerries` |
| `diseaseMtbDays` | 45 | 50 |
| diseases | 6 | **7** |
| `allowFarmingCamps` | *absent* | **true** |
| `wildAnimals` | 7 Core rows | 27 rows |
| `fishTypes` | **absent** | 10 species + rare table |

🔴 **The live def carries `movementDifficulty` 1 — no penalty at all**, against the owner's ruling
that movement is *"extremely difficult"*. The generic twin carries 1.6. This is a real contradiction
between a ruling and the def the world runs on, and it is noted rather than fixed here: `RUT_Greentide`
is frozen and content fixes were ruled to land in `mandrake.rm.greentide` only. ⇒ It belongs to
`GREENTIDE_BIOME_DENSITY_1`, which already owns the movement budget, and that item does not yet
record it.

### 1a. Plants — SUBSTANTIAL, and largely undesigned-but-scoped

| what | state |
|---|---|
| `RM_Greentide`'s `wildPlants` | **6 vanilla temperate rows** (`Plant_TreeOak` 2.0, `Plant_TreePoplar` 1.2, `Plant_Bush` 1.5, `Plant_Grass` 2.0, `Plant_TallGrass` 1.0, `Plant_Berry` 0.6) — the list the owner rejected outright |
| the replacement roster | **21 invented plants, fully designed, nothing authored** — `greentide_tree_roster_2026-09-22.md`. 9 of 21 dangerous by design; 6 rows where reward and hazard are literally the same object |
| hostile mobile plants | `HOSTILE_MOBILE_PLANTS_1` — **concept approved and three of five questions ruled** (waits rooted, one leaf twitches, hostile to anything close, activation propagates between neighbours as a swarm). Nothing authored; the animation mechanism is deliberately unresolved |
| tree fall as a hazard | ✅ **BUILT IN FULL.** `RM_TreeFallUtility` + `RM_CompCrackFall` + `RM_FellableTreeExtension`, three fellers routed through one utility, settings toggle #22 |
| the growth-into-your-doorway hazard | `EXPLOSIVE_PLANT_GROWTH_1` — **open, and NOT built.** Measured by an earlier pass: zero hits in `src/` for a suppression grid. Two shipped mechanics have documented no-op hooks waiting on it (`RM_CompDryFieldEmitter.SuppressPlantGrowth()`, M10's grazing postfix) |

⇒ **The plant axis is the best-covered of the four.** What it lacks is defs, not design.

### 1b. Beasts — the LARGEST existing body of work, and the signature ones are placeholders

`WildAnimals_Greentide.xml` (new 2026-09-22) puts **27 rows** onto `RM_Greentide`, weights summing to
9.318, copied verbatim from the frozen live def. 23 are our own `RSW_` ports of canon creatures, 1 is
ours outright (`RUT_Sytheclaw`), 3 are non-Star-Wars donor rows (`AA_Needlepost`, `AA_BloodShrimp`,
`VFEI2_Swarmling`).

✅ **Four of the biome sheet's six named fauna *sorts* have their mechanics built:**

| sort (sheet §4) | mechanic | state |
|---|---|---|
| the Lungers | `RM_CompAquaticAmbusher` — invisible on deep water, snaps visible, one 1.5× opening bite | ✅ **BUILT** (M7), settings toggle #11 |
| the Gnawers | `RM_JobGiver_GnawTreeBase` / `RM_JobDriver_GnawTreeBase` | ✅ **BUILT** (M6, feller 3) |
| the Shatterers | `fellsTreesBelowHealthFraction` hook inside `HediffComp_PeriodicAreaAttack` | ✅ **BUILT** (M6, feller 2) — **wired to no live creature** |
| the Brakes / grazing | grazing-suppresses-encroachment postfix | ⛔ blocked on `EXPLOSIVE_PLANT_GROWTH_1` |
| the Swingers | — | nothing |
| the Fliers | — | nothing (but the standing flyers-fly rule applies when one is touched) |

🔴 **The two creatures those mechanics were built for do not exist.** MEASURED: the only Gnawer and
Lunger defs in the repo are `RUT_Placeholder_GreentideGnawer` (a recoloured Squirrel) and
`RUT_Placeholder_GreentideLunger` (Alligator's fields copied down), and **neither appears in any
biome's `wildAnimals` or any GenStep** — deliberately, per each pass's own scope. There is no
Shatterer def of any kind. ⇒ So the beast axis reads as rich in the roster and rich in the engine, and
the three signature terrors are unrepresented in both.

### 1c. Diseases — SEVEN, all vanilla, and the project has never authored one

✅ Confirmed exactly as the brief states. `RUT_Greentide` (live) carries seven:
`Disease_Flu` 75, `Disease_Plague` 75, `Disease_Malaria` 75, `Disease_GutWorms` 50,
`Disease_AnimalFlu` 75, `Disease_AnimalPlague` 75, `Disease_OrganDecay` 10. `RM_Greentide` carries the
first six only — **organ decay was added to the live twin and never mirrored to the generic one**, a
small owed fix. `diseaseMtbDays` 50 / 45.

🔴 **And the axis is empty project-wide, not just here.** MEASURED across all of `src/` — every
distinct `<diseaseInc>` value in every one of our ~20 biome defs:

```
26 Disease_Flu        24 Disease_Plague       21 Disease_GutWorms
19 Disease_MuscleParasites   18 Disease_SensoryMechanites   18 Disease_FibrousMechanites
17 Disease_AnimalFlu   16 Disease_AnimalPlague  9 Disease_Malaria
 6 Disease_OrganDecay   4 Disease_SleepingSickness
 2 AB_Disease_SporesAllergy   2 AB_Disease_AnimalSporesAllergy
 1 AB_Disease_ViralAbasia   1 AB_Disease_RavagingIntestinalParasites   1 AB_Disease_BacterialGangrene
```

⇒ **Eleven vanilla incidents and five Alpha Biomes donor incidents. Zero of ours, anywhere.** A
Greentide disease of our own would be the project's first, so the `IncidentDef`/`HediffDef` shape for
one is **UNMEASURED** and must be read off a real example on the Desktop before anything is authored.
This is a bigger step than "add a row" and should be priced that way.

Also relevant: the biome's `Disease_Malaria` is the single most biome-legible vanilla row it carries,
and `Disease_Flu`/`Disease_AnimalFlu` are the two least — they appear on 26 and 17 of our biomes
respectively and therefore say nothing about this place. §5 Q2 builds on that.

### 1d. Insects — UNMEASURED in the brief, and now established: there is NO authored insect threat

This was checked rather than assumed, and the answer is a clean negative.

**What exists** is insect-*flesh* creatures in the roster, all ports of somebody else's canon:

| row | state, read from its own def |
|---|---|
| `RSW_Kinrath` 0.3 | ours (port). `fleshType Insectoid`, `predator true`, `manhunterOnDamageChance` **1.0**, poisonous stinger appendage, own leather `RSW_Leather_Insectine` |
| `RSW_Klorslug` 0.4 | ours (port). Insectoid, `predator true`, `manhunterOnDamageChance` **1.0**, poisonous tail-stinger + circular teeth |
| `RSW_Gelagrub` 0.3 | ours (port). Insectoid, `trainability None`, `manhunterOnDamageChance` 0.1 — a **docile neutroamine producer**, a reward not a threat |
| `RSW_Diggerpede` 0.4 | ours already before the port pass |
| `VFEI2_Swarmling` 0.4 | **donor**, VFE Insectoids 2, behind `MayRequire` |
| `Megaspider` 0.1 | vanilla, on the Core-only generic roster only |

**What does not exist**, MEASURED:

- 🔴 **No insect mechanic of ours at all.** `Hive`, `Infestation`, `InsectJelly` and `HiveDef` return
  zero hits across `src/RimMandrake` outside unrelated map-painting and raid-visibility utilities.
- 🔴 **The Gnawers — the sheet's own signature insect, *"huge insects chewing at the tree bases…
  the food pyramid's floor"* — are a recoloured squirrel placeholder, unwired.** The job driver that
  fells trees for them is built and has nothing to drive.
- No insect-specific hazard: no swarm, no nest, no brood event, no chitin economy beyond the two
  ported leathers.

⇒ 🔑 **The insect axis is the genuinely empty one of the four, and it is empty in a specific way that
matters: the mechanic exists and the creature does not.** Filling it is cheap relative to the others
because `RM_JobGiver_GnawTreeBase`, `RM_GnawTreeBaseExtension` and the whole fall utility are already
shipped and tested-to-compile. The missing piece is a real Gnawer def and art.

### 1e. Environment — the intimidation layer is nearly complete

Not one of his four axes, but it is where most of the *fear* already lives, and it is the most built
part of the whole biome. From `GREENTIDE_MECHANICS_2`, all read from that item and the files it names:

✅ **Shipped:** churnmud mire + item-swallow in full (`RM_MapComponent_TerrainMire`,
`RM_MapComponent_MudSwallow`, `RM_Mired` hediff with three escalating stages) · the silence cue ·
wet-bulb overwhelm as a permanent map condition with a 4-stage hediff and a 3-piece apparel tree ·
the dry-air blower with its decaying dryness grant · the Roil as a permanently-forced weather with its
own overlay class · Breaklight as a rare clearing incident with a glow override · the steam devil
wandering vortex with `RUT_Scald` damage · root causeways at mapgen · the Greatbole with mineable
heartwood, regrowth crush-and-eject, and the toxin sealant that stops it · three-feller tree fall.

⛔ **Not shipped:** `EXPLOSIVE_PLANT_GROWTH_1` in its entirety (so no visible growth, no door
encroachment, no grazing suppression, no bottled extract) · the steam devil has no sprite and does not
meet *"visible from far off"* · vegetation movement cost as distinct from churnmud.

⇒ **Nine of twelve kit mechanics are live.** Anyone treating the Greentide as an unbuilt biome is
wrong by a wide margin, and the one big hole is a single named item.

---

## 2. Audit of the reward side

### 2a. What is already designed or built

| reward | where it lives | state |
|---|---|---|
| **Greenwood** — bulk burnable/buildable wood | `RUT_Greenwood` ThingDef, MarketValue 1.8 / Mass 1.5 (both invented) | ✅ **BUILT**, dropped per-cell by `RM_TreeFallUtility` at a 0.5 chance, stacks 5–15 |
| **True hardwood** | `RUT_Hardwood` + `RUT_GreatboleHeartwood` (mineable, `mineableThing` = hardwood) | ✅ **BUILT** — but the felling route is **broken by a ruling**: the signature giant is the Greatbole and it *cannot be felled*, so §7's *"only from the heart of fallen giants"* has no fallen giant. Open as the roster's Q1 |
| **Sap and resin** | `RM_SapResin` (MarketValue 1.1, from 10 `WoodLog` at a machining table) | ✅ **BUILT** |
| **Toxin sealant** | `RM_ToxinSealant` (MarketValue 2.4, from 4 resin + 1 `Neutroamine`) | ✅ **BUILT**, and it is what makes a Greatbole chamber persist |
| **Chamber shelter** | `RUT_GreatboleCore` / `RUT_GreatboleHeartwood` / `RUT_ToxinSealant` terrain, `RM_MapComponent_LivingRegrowth` | ✅ **BUILT** — you mine a home into a living tree and paint it so it cannot heal shut |
| **Free roads** | `RM_GenStep_RootCauseways` | ✅ **BUILT** |
| **The catch** | `RUT_Greentide`'s `fishTypes`: 10 species (7 ours: `RUT_Zeev`/`Uvva`/`Karrun`/`Dubbol`/`Lozh`/`Saava`/`Tuun`, 3 `RSW_`), `maxFishPopulation` 720, `rareCatchesSetMaker` `RUT_RareGreentideCatches` | ✅ **BUILT on the live twin**; `RM_Greentide` has **neither tag**. `GREENTIDE_EXOTIC_JUNGLE_FISH_1` extends it with invented exotics, catch-item only — the owner ruled *"There is no 'underwater' beast version for a land biome. Just fishable."* |
| **The harvest economy** | the 21-plant roster: a fuel-sap tap, an export timber, a hardwood, forageable roots, a bulk tuber, sugar, containers, roofing, cordage, medicinal spores, acid toxin | **designed, nothing authored.** 19 of 21 rows useful |
| **Neutroamine from livestock** | `RSW_Gelagrub`, already in the roster | ✅ live in the roster, and worth noticing — an insect that pays |

### 2b. What his three named rewards actually have today

1. **Tremendous food abundance** — `forageability` 0.8/1.0 and `foragedFood` `RawBerries`. That is the
   whole of it. 🔴 **The biome's foraged yield is a vanilla berry**, which both
   `GREENTIDE_BIOME_DENSITY_1` and the roster flag and neither will assume away. The roster supplies
   real staples on paper (brakkel fruit, wollick tuber, tumbel gourds, nemmer fruit, sarquin sugar)
   and none exists as a def.
2. **Unique medicines** — 🔴 **nothing.** MEASURED: no medicine def of ours keys to this biome. The
   project's medicine content is `KOTOR_kolto` (an absorbed donor gel, `MedicalPotency` 1.9) and the
   Rot's fungal preparations. The sheet promises *"the most biochemically frantic pharmacopoeia on the
   planet"* and the biome delivers zero of it. **This is the emptiest reward axis.**
3. **A large cuisine-ingredient space** — 🔴 **nothing.** No Greentide meal, no ingredient, no recipe.
   The catch table is the only edible content that exists.

### 2c. The one structural precedent worth copying

`src/RimUtinni/RotSporeKit/Defs/RecipeDefs/RUT_RotSporeKit_LivePrepRecipes.xml` already solves the
problem §4 and the anti-inversion section below both face, and its header says so in its own words:

> *"There is no bulk variant of any of these on purpose — a `bulkRecipeCount` would have quietly
> turned a pilgrimage into a production line."*

Its shape: one dedicated vessel that cannot be substituted, six ingredient units per single product,
the product **dies in 2.5 days and cannot be refrigerated**, and no `unfinishedThingDef` so there is
no stockpilable half-product. ⇒ **That is the template for every high-value Greentide reward.** It is
already shipped, already reviewed, and it is the reason the Rot's rewards did not become a money
printer.

## 3. The exchange as a progression

🔑 **The arc in one sentence: you stop surviving the Greentide and start scheduling it.**

A place that is uniformly lethal-and-generous teaches nothing, because nothing the player learns
changes the transaction. The fix is not to ramp difficulty — it is to make **which rewards are
reachable** a function of what the player has built, while the danger stays roughly flat.

### 3a. The three phases

**Phase 1 — Trespass (roughly the first five visits).**

*It costs:* your pawns' health and your schedule. Two independent movement taxes stack (churnmud's
`pathCost` plus the ruled vegetation cost), the wet-bulb condition ramps on anyone without the right
apparel, and you cannot see the floor — so you cannot see the ambusher rooted on it, and you cannot
tell which mud swallows. Your desert kit is exactly wrong here and you own no other.

*It gives:* only what is lying on the ground. Fallen greenwood by the crawler-load, fruit under leaves,
water. A tuber you can dig. **No clock-goods at all**, because you have no way to get anything
perishable home.

*What you learn:* that this is a second planet needing a second kit. The intended emotional beat is
**recoil** — the owner's own acceptance bar for the density work is *"You look at the map when you
land and decide to go around."*

**Phase 2 — Foothold (visits five to thirty).**

*It costs:* upkeep that never stops. Every blower doorway burns fuel; encroachment grows into doors
faster than you can tend them; a Greatbole chamber heals shut unless the sealant is maintained. 🔑 **A
bigger Greentide presence costs strictly more per day than a smaller one**, which is the negative
feedback the whole design rests on — and it is already shipped in the decaying dryness grant and the
regrowth timers.

*It gives:* the harvest economy proper. Sap into fuel, the export timber, hardwood, roofing, cordage,
containers, the catch. And — if the disease axis is redesigned as §4 R1 proposes — the fevers stop
being pure attrition and start producing **resistant veterans**, which is the moment the exchange
first feels like a bargain rather than a toll.

*What you learn:* routes. Which causeway, which crossing, which grove, which season of the day.

**Phase 3 — Expedition economy (thirty onward).**

*It costs:* logistics. Everything valuable left has a clock on it, so the binding constraint stops
being the harvest and becomes transit: how fast can a crawler reach a buyer before the jar dies.

*It gives:* the high categories — growth extract, live bloodstock, perishable sensory luxuries,
regrown tissue. These are the reasons a clan that already has food goes back.

*What you learn:* that you were never meant to live here. **The Greentide is a destination, not a
home** — which is also the thing that prevents the inversion §4c addresses.

### 3b. What changes and what deliberately does not

| | Phase 1 | Phase 3 |
|---|---|---|
| danger level | high | **the same** |
| your competence | none | high |
| reward *kinds* available | floor-litter only | everything |
| binding constraint | can you survive the walk | can you deliver in time |
| upkeep per day | near zero | high and rising |
| how it feels | trespass | a scheduled trip |

🔴 **Recommendation: do not scale the danger with the player.** A hazard that grows to match you
erases the only reward the player earned by learning, and this project has a standing anti-exponential
concern for the same reason on the money side. The Greentide's difficulty curve should be flat and the
player's should be steep. That is a real design choice and it is §5 Q4.

### 3c. The two hazards that must NOT be softened by progression

- **The swarm chain** (`HOSTILE_MOBILE_PLANTS_1`'s activation propagation). It should remain capable of
  killing a competent colony, because it is the one thing that keeps the floor frightening after the
  player can read everything else. Its bound must be deliberate — an unbounded chain across a map with
  no uncovered squares is a colony-killer, which that item already warns.
- **The tree fall.** It is indiscriminate by design (`RM_TreeFallUtility` damages every Thing in the
  swath including the player's own, deliberately). A player in Phase 3 with a built-out camp has *more*
  to lose to it than a Phase 1 trespasser. That is the correct shape: the hazard doesn't grow, the
  stake does.

## 4. New reward categories

*(in progress)*

## 5. Card-ready questions for the owner

*(in progress)*

## 6. UNMEASURED / needs the Windows machine

*(in progress)*
