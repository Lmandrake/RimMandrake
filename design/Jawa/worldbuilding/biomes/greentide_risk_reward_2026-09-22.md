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

**The invention frame.** His three named rewards are treated as the floor. The question driving
everything below is not *"what else grows here"* — that is the roster's job and it is done — but
**what would a desert scavenger clan find priceless in a place that is violently, excessively
alive?** The answer that generates new categories rather than new items is: on a dead planet, the
scarce things are not materials. They are **living processes**. Water can be hauled. A metabolism
cannot. The Greentide is the only place on Ashkarr where biology is running fast enough to be
*used as machinery*, and every category below is a different way of renting that machinery.

🔑 **The organising test, applied to every candidate:** does it change what the colony can **do**,
or only what it has in store? A category that only adds stock is a resource, and the biome already
has enough of those. Eight of the ten below change a capability; the two that are stock
(R2 medicines, R3 cuisine) are his own named asks and are shaped so that they cannot be stockpiled.

⚠️ **All names below are placeholders for the concept, not proposals.** Nothing here names any
franchise; the invented words are there so a category can be discussed, and the naming pass owns
them. Nothing here is a def, and no vanilla defName appears that was not already read off a file
in §1–2.

### R1 — Immunological capital: the fevers make *qualified people*

**What it is.** Surviving a Greentide fever leaves a permanent, visible, *valuable* mark: a pawn who
has had the jungle's signature sickness and lived carries lifelong resistance to it, and that
resistance is a **job qualification**. Only a marked pawn can safely lead a deep expedition, hold a
forward camp through a wet season, or work a live-preparation vessel without dosing themselves.
Unmarked pawns can still go — they just get sick, and the marked ones don't.

**What it costs.** The fever itself: real downtime, real deaths, and a nursing burden on the colony
that is *worse* than the expedition it enables. You cannot buy the mark, you cannot rush it, and a
pawn who dies of it takes the investment with them. Deliberately, the first three or four Greentide
trips are net-negative in labour for exactly this reason.

**Why only here.** The desert's hazards are physical — heat, thirst, sand, raiders. None of them
leave an adaptation behind, because you do not adapt to dehydration; you just fail at it. A fever
is the only hazard on the planet that *teaches the body something*, and the Greentide is the only
place with one. ⇒ This is the category that turns §1c's seven diseases from a tax into the biome's
single best reward, without authoring one new hazard.

🔑 **This is why it is R1 and why it is cheapest.** The hazard is already shipped — seven disease
rows are live on the biome today. What is missing is the *other half of the transaction*, and that
half is one hediff and one qualification check. §3a's Phase 2 beat ("the exchange first feels like a
bargain") is this and nothing else.

⚠️ Whether a vanilla disease's recovery already leaves a durable immunity record a mod can read, and
whether a work-capability gate of this shape exists, are both **UNMEASURED — confirm on the Windows
machine.** See §6.

### R2 — A pharmacopoeia priced in *hours*, not silver

**What it is.** His "unique medicines", built on the one axis nothing in the desert can compete on:
**potency that decays.** Greentide preparations are the best medicine on the planet for the first
few hours after they are made and worthless by the next day. Three distinct grades, not one item:

1. **Field preparations** — made *inside* the biome from a plant harvested minutes earlier, used on
   the spot. Better than anything in the colony's stores. Cannot be carried home at all.
2. **Sealed preparations** — the same material stabilised with the shipped toxin sealant route
   (`RM_ToxinSealant` already exists), surviving a crawler ride at a real potency loss. This is the
   tradeable grade and the only one a buyer ever sees.
3. **Live cultures** — a maintained, feeding thing rather than an item: it keeps producing while it
   is fed, and dies the moment the colony stops. Capability, not stock.

**What it costs.** A dedicated vessel that cannot be substituted, several ingredient units per single
output, and a clock. The precedent is already shipped and already reviewed — §2c's Rot live-prep
recipes, whose own header explains why there is deliberately no bulk variant. Every reward in this
section inherits that shape.

**Why only here.** A pharmacopoeia requires an arms race, and an arms race requires crowding. Nine
of the roster's 21 plants are dangerous *to each other* as much as to you; the desert's flora is
sparse enough that nothing there needs a chemical weapon. ⇒ The medicine is good **because** the
place is hostile — the same molecules are the hazard and the cure, which §1a already notes is
literally true of six roster rows.

### R3 — Cuisine as a combinatorial SYSTEM, never a recipe list

🔴 **"Seemingly endless" must come from few ingredients recombining. A long list of hand-authored
dishes is filler and would fail his ask while appearing to satisfy it.** The design below produces
an unbounded dish space from a small fixed vocabulary, and the authoring cost does not grow with
the number of dishes.

**The system in four parts.**

1. **Every Greentide edible carries one value on each of three small axes** — a *savour* (roughly
   six values: bitter-green, resin-smoke, sour-acid, sweet-sap, fat-flesh, mineral-brine), a
   *texture* (three: pulp, crisp, gel), and a *volatility* (three: stable, fades, turns hostile when
   stale). Every roster plant, every catch row and every meat already in the biome gets tagged.
   That is the whole authoring burden: a few dozen tags, no new dishes.
2. **A dish is a slot pattern, not a recipe.** One small family of cook jobs — say a three-slot and
   a five-slot — accepts *any* legal combination. The dish's identity, name and thought are
   **derived at cook time** from the multiset of savours and textures present. Six savours in three
   slots is already 56 distinct dishes from one authored recipe; adding one ingredient adds dishes
   for free.
3. **The colony has a palate memory, and it is the engine.** A savour combination eaten recently is
   worth less; a genuinely new one is worth much more. ⇒ **The demand for novelty is what keeps
   sending the player back into the jungle after food stopped being a problem** — the reward is not
   the calories, it is the *variety*, and variety is the one thing a warehouse cannot hold.
4. **Volatility is the brake.** The best savours are on the volatile ingredients, so the best dishes
   can only be cooked near where the ingredients grew. A colony cooking from storage eats
   competently and never eats well.

**What it costs.** Cooks, a kitchen near the frontier rather than at home, and trips whose whole
purpose is an ingredient you have not tasted yet. Nothing about it is stockpilable, by construction.

**Why only here.** A palate needs contrast, and contrast needs a biome with more than four edible
things in it. The desert supplies roughly one savour. ⇒ This is the category that most directly
delivers the *feel* he asked for — a cuisine culture that seems bottomless — and it does it with
about thirty tags and two recipes.

⚠️ Whether a cooked meal can carry its ingredient set forward at all (so a dish's identity can be
derived from what went in) is the single mechanism this rests on, and it is **UNMEASURED — confirm
on the Windows machine.** If it cannot, the fallback is a fixed set of derived *dish classes* chosen
at cook time, which loses the free-scaling property and should be priced as a much weaker version.

### R4 — Regrowth: the only place a lost limb comes back

**What it is.** The biome's defining property is growth that cannot be stopped — it is already
shipped as a hazard in the Greatbole's regrowth crush-and-eject and the encroachment that heals a
chamber shut. **Turn that same property on a body.** A pawn who has lost a hand, an eye, a lung or
a leg is put through a procedure that can only be performed inside the biome, in a living chamber,
over days — and grows the part back. Not a prosthetic. The original tissue.

**What it costs.** Time in the worst place on the planet: the patient is immobile, in a chamber that
is actively trying to close on them, needing continuous upkeep and a guard, for days. The procedure
is unreliable and its failure mode is *more* growth, not less — an overgrowth condition that has to
be cut back and leaves the pawn worse than the amputation did. And it consumes the perishable top
grade of R2, so it competes directly with treating anyone else.

**Why only here.** Nothing in the desert grows. That is the entire setting premise, and this is its
strongest possible inversion: the clan's scarred, patched, mechanically-repaired people learn there
is one place they can be made whole, and it is the place that will kill them. ⇒ **This is the
category with the most emotional weight of anything in this document,** and it is the one a player
tells someone else about.

⛔ **Do not let it become the colony's prosthetics industry.** It is per-pawn, in-place, and the
product is never an item — there is nothing to stockpile, ship or sell, and no bulk route can exist
because the patient is the vessel. That property is what makes it safe to make this good.

⚠️ Whether a mod can add a body part back to a living pawn, and what it takes, is **UNMEASURED —
confirm on the Windows machine.**

### R5 — Live bloodstock: genetic capital for a world with no animals

**What it is.** Not meat, not leather — a **living, breeding animal brought out alive.** The biome
carries 27 roster rows against a planet whose other regions carry a handful; this is the only place
with a gene pool. What you take home is a herd: draft power, pack capacity, milk, wool-analogues,
guard animals, and — the real prize — the ability to *breed more* without coming back.

**What it costs.** Capture, containment and transit of something that fought you, through churnmud
and a wet-bulb condition, without killing it. A crawler carrying a live cage carries little else.
And most of the cast cannot survive the desert at all, so the first generations die at home, which
is the price of finding the two or three lineages that can.

**Why only here.** A desert scavenger clan's animals are inherited, not acquired; a clan that can
found a *new* line has changed its own future. ⇒ Note this category is half-shipped already and
unremarked: `RSW_Gelagrub` in the live roster is a docile neutroamine producer (§1d), i.e. an
insect that pays rent. That is the proof of concept for the whole category.

### R6 — Domestication: carrying the jungle home as a desert cultivar

**What it is.** A long, failure-prone programme that takes a Greentide plant and produces a strain
that will grow **at the home base**, in sand, under the desert sun. The output is not a crop — it is
a *cultivar*, a permanent unlock, and it is deliberately a shadow of the original: a sixth of the
yield, none of the volatile savours, none of the medicinal fraction.

**What it costs.** Years of in-fiction time, repeated expeditions for fresh stock because each
attempt consumes it, and a research burden. And the yield is bad on purpose.

**Why only here.** There is nothing else on the planet worth domesticating.

🔑 **This category exists for a structural reason, not a flavour one: it is the anti-relocation
valve.** See §4c — the way you stop a player moving into the jungle is to let the jungle's value
move to them instead, badly. A player who can grow a weak jungle staple in the desert has a reason
to *stay* in the desert, and still has every reason to visit.

### R7 — The living laboratory: research that exists nowhere else on the planet

**What it is.** A **field station**, not a bench: research that can only be progressed by pawns
physically inside the biome, working on things that are alive and uncooperative. The unlocks it
gates are the ones that make everything else in this section usable — the vessels of R2, the
procedure of R4, the containment of R5, the cultivar programme of R6 — plus a tier of biology and
chemistry the desert simply has no specimens for.

**What it costs.** Your best researcher, in the worst place, for a long time, at risk. A field
station is a permanent upkeep line (§3a Phase 2's shipped negative feedback applies directly) and it
does not progress while nobody is standing in it.

**Why only here.** Knowledge is the purest "changes what you can do rather than what you have," and
a dead planet is a place with nothing left to learn. ⇒ **R7 is the spine the other categories hang
off**, which is an argument for building it early and an argument against building it first: it is
worthless until there is something on the far side of it.

### R8 — Concealment biology: the jungle teaches you not to be found

**What it is.** The place is full of things that survive by not being seen, and two of them are
already shipped as hazards — the aquatic ambusher that is invisible on deep water, and the silence
cue. **Harvest that.** Scent-masking preparations that stop a predator or a manhunting animal
committing to you; a resin that kills the noise a working colony makes; dyes and coatings that read
as vegetation.

**What it costs.** These are made from the hazards themselves, so obtaining them means engaging the
things you are trying to hide from, and they are worn or applied — consumed, on a clock, per pawn
per trip.

**Why only here.** Desert survival is about endurance and water; *nothing hides in an open desert*,
so no desert biology has ever needed to. ⇒ This is the category that changes **combat and hunting**,
a domain none of the others touch, and it is the one that most directly rewards the player for
understanding the biome's own bestiary.

### R9 — Grown construction: a structure you plant instead of haul

**What it is.** The Greatbole chamber (shipped) proves the idea — you mine a home into a living tree
and paint it so it cannot heal shut. **Generalise it.** Living walls that thicken over days and
repair themselves; root causeways the player can *extend* rather than merely find at mapgen (the
gen-step is already shipped); a canopy that roofs an area by growing over it.

**What it costs.** Time instead of materials, and maintenance forever. A grown structure is never
finished: it keeps growing, and an untended one closes your own doorway — which is `EXPLOSIVE_PLANT_
GROWTH_1`'s hazard reused verbatim as this category's cost. It works only where the biome's growth
rate applies, so it cannot be exported (unlike R6, deliberately).

**Why only here.** A scavenger clan's buildings are salvage, bolted together. Something *grown* is
the strongest visual statement the biome can make about what it is.

### R10 — Reputation: becoming the only source of things that cannot be shipped far

**What it is.** A trade identity rather than a trade good. Because the top grades of R2 and R3 die
in hours, **nobody who is not local can supply them** — so a clan holding the Greentide holds a
monopoly that distance itself enforces. The payoff is social: buyers who come to you, standing
orders, a faction attitude that improves because you are the only supplier, and visitors of kinds
the desert never sees.

**What it costs.** Being findable. Everything that makes you a destination makes you a target, and a
known route is a route a raid can use.

**Why only here.** ⇒ This is the category that converts the perishability constraint — the main
*brake* on every other reward — into a reward in its own right, which is the most elegant move
available and costs almost nothing to build once R2 and R3 exist.

### 4b. Ranking, and what I would build first

Ranked by **(owner's stated intent) × (payoff per unit of build) ÷ (mechanism risk)**, with the
audit's own finding that the hazard half of several of these is *already shipped* weighing heavily.

| # | category | build cost | rests on a mechanism we have | verdict |
|---|---|---|---|---|
| **1** | **R1 immunological capital** | **low** | hazard already live (7 disease rows) | **build first** |
| **2** | **R3 cuisine system** | low–medium | needs one ingredient-memory mechanism | **build second** |
| **3** | **R2 pharmacopoeia** | medium | ✅ live-prep template + sealant shipped | build third |
| 4 | R10 reputation | low | free once R2/R3 exist | ride along with R2 |
| 5 | R4 regrowth | high | regrowth hazard shipped; surgery side unknown | the marquee, build later |
| 6 | R7 living laboratory | medium | none | needed before 5, 6, 8 go deep |
| 7 | R5 live bloodstock | medium | roster + a live producer already exist | good, not urgent |
| 8 | R8 concealment | medium | ambusher + silence cue shipped | strongest combat-side option |
| 9 | R6 domestication | high | none | structurally important, slow payoff |
| 10 | R9 grown construction | high | chamber + causeways shipped | best spectacle, worst cost |

🔑 **Build R1 first, and it is not close.** Three reasons, all from §1:

1. **The hazard is already paid for.** Seven disease rows are live on the biome today and currently
   deliver nothing but attrition. R1 is the only category on this list that adds a *reward* by
   completing a transaction that already exists, rather than by authoring a new hazard and a new
   reward together.
2. **It fixes the emptiest axis without touching it.** §2b found the "unique medicines" axis at
   literally zero and the disease axis at seven-borrowed-rows. R1 converts the second into the
   payoff for the first, and §1c's warning stands: authoring a disease of ours would be this
   project's first ever and is a much bigger step than it looks.
3. **It is the moment §3a's Phase 2 turns.** Without R1, Phase 2 is upkeep with no compensating
   gain, and the progression in §3 does not actually have a hinge.

**Then R3**, because it is the ask most at risk of being answered badly — a hundred meal defs would
look like a lot of work and deliver none of what he asked for — and because its whole cost is tags.

**R4 is the one to protect.** It is the best idea in this document and the easiest to spoil by
building it early, small, and safe. It should arrive as an event the player has heard rumours of,
not as a research tab entry.

### 4c. Why this does not make the jungle the best place to live

🔴 **The named risk: `allowFarmingCamps` is `true` on the live def (§1), `forageability` is 1.0, and
the roster is full of staples. Abundance + farming + rich forage is exactly the recipe for the
hazard biome becoming the optimal home base** — which would destroy both the desert premise and
every reward above, since all of them are priced as expedition goods. Seven defences, five of which
are already shipped:

1. **The value is capability, and capability lands at home.** R1 marks a *pawn*, R6 produces a
   *cultivar*, R7 unlocks *research*, R4 repairs a *body*. All four are carried out in the colonist
   and spent at the base. ⇒ Moving in gains the player nothing they do not already get by visiting.
2. **Everything else has a clock.** R2 and R3's top grades die in hours by construction, so a
   settlement here cannot accumulate — it can only consume, exactly as a camp does.
3. **No bulk route, on anything.** §2c's shipped precedent, verbatim in its own header: no
   `bulkRecipeCount`, one dedicated vessel, no stockpilable half-product. Applied to every category
   above without exception.
4. **Upkeep is superlinear in presence, and this is already built.** Blower fuel, the decaying
   dryness grant, chamber sealant, regrowth timers (§3a). A permanent settlement pays all of them
   every day, forever, at a scale a three-day camp never does. 🔑 This is the single strongest lever
   and it needed no new work.
5. **Flatten market value on the top categories, on purpose.** Precedent: this project already
   flattened a creature's market value to stop a money printer. Apply it here — the medicine and the
   cuisine should be worth **using** and barely worth selling. R10 supplies the *social* payoff that
   would otherwise have to be silver.
6. **The abundance is calories and nothing else.** It is starch, fruit, sap and fish. It carries no
   metal, no components, no stone worth the haul, no cloth-analogue at scale, and it cannot hold a
   stable temperature. ⇒ **A colony that lives here eats magnificently and cannot build anything.**
   That is the correct shape for "tremendous food abundance" that does not invert the game.
7. **Farming here is worse than farming at home, and the reason is already an open item.**
   Encroachment out-grows a tended plot (`EXPLOSIVE_PLANT_GROWTH_1`), and the fertility favours
   jungle plants over anything the clan knows how to sow. ⇒ A farming camp should feed *itself* and
   never export. That is a tuning stance, not new code, and it makes the live `allowFarmingCamps`
   flag safe rather than dangerous.

🔑 **And the framing that makes all seven coherent, already stated in §3a Phase 3: the Greentide is a
destination, not a home.** Every defence above is a way of saying that in mechanics. ⛔ If a future
pass finds itself adding a storable, sellable, bulk-producible Greentide good, it is undoing this
section — and R6 is the sanctioned release valve for that pressure.

## 5. Card-ready questions for the owner

**How to read these.** Seven cards, each with exactly three options, each option saying what it buys
**and** what it costs. No internal names or identifiers appear below — they are written to be read
cold. **Q1 is the widest and is his explicit ask.** ⇒ And per how he prefers to work: any of these
can be answered by *refining* an option rather than picking one, and "none of these — here is a
fourth" is a valid answer on every card.

### Q1 — Which new payoff do we build first? *(the widest card)*

*Why you are being asked:* the jungle now has ten distinct kinds of reward designed, which is far
more than can be built at once. They are not variations — each one changes a different thing about
the colony, and whichever comes first sets what the jungle *means* for a long time. All three of
your named rewards are covered in every option; this is about what goes in beside them.

- **A. The sickness pays you back — survivors become your specialists.**
  A colonist who catches one of the jungle's fevers and lives is permanently marked by it, and that
  mark is a qualification: only marked people can lead a deep trip, hold a forward camp through the
  wet, or handle the fresh medicines without dosing themselves. Nobody else can be made into one, and
  it cannot be bought.
  *Buys:* the jungle's illnesses stop being pure punishment and become the thing that builds your
  expedition crew — and it costs almost nothing to build, because the illnesses are already in the
  game today. It is also the moment the whole place starts feeling like a bargain instead of a toll.
  *Costs:* the payoff is invisible for the first several trips, and it is paid for in dead
  colonists. Some players will read early deaths as the biome being unfair rather than as tuition.

- **B. The jungle can give a body part back.**
  Someone who lost a hand, an eye, a lung or a leg is put through a days-long procedure that only
  works inside the jungle, in a chamber cut into a living tree — and grows the real part back. Not a
  prosthetic. It can fail, and when it fails it fails by growing *too much*.
  *Buys:* the most memorable thing in the whole biome, and the sharpest possible statement of the
  setting — on a planet where nothing grows, there is exactly one place your people can be made
  whole, and it is the place that kills them. This is the option players tell each other about.
  *Costs:* the most expensive of the three to build and the one most likely to hit a wall in the
  game's own limits. It also risks turning the jungle into a hospital run, which is a much smaller
  idea than the one above.

- **C. The jungle teaches you not to be found.**
  Harvest the biology of the things that ambush you: scent-maskers that stop a predator or an enraged
  animal committing to you, resins that quiet a working camp, coatings that read as vegetation.
  Consumed per person, per trip.
  *Buys:* the only option that changes **fighting and hunting**, which nothing else in the biome
  touches — so it broadens what the jungle is for rather than deepening what it already is. It also
  directly rewards a player for learning the local bestiary.
  *Costs:* the least emotional of the three, and it makes the player stronger *everywhere*, not just
  here — which slightly dilutes the jungle's identity as a place with its own rules.

### Q2 — Do we write our own jungle diseases, or take some away?

*Why you are being asked:* the jungle currently carries **seven** illnesses and all seven are the base
game's. Two of them appear on more than twenty of our other regions, so they say nothing about this
place. Writing one of our own would be the first disease this project has ever authored, which is a
bigger job than it sounds. And more illness is not the same as more fear — a place that just keeps
making people sick becomes tedious rather than frightening.

- **A. Replace, don't add. Cut the two generic fevers, write one jungle disease of ours.**
  *Buys:* the count stays at six, so the tedium does not rise, but the jungle gains one illness that
  is unmistakably *its* — a name and a progression a player will come to dread specifically. The two
  removed are the two that could have come from anywhere.
  *Costs:* one genuinely new piece of engineering, done for the first time, with the risk that comes
  with a first. And removing anything from the region the saved world already runs on is delicate.

- **B. Keep all seven as they are, and spend the effort on the payoff instead.**
  *Buys:* zero risk, zero new work on the danger side, and everything saved goes into Q1's reward —
  which is where the biome is actually empty. Seven illnesses already deliver the attrition you
  wanted.
  *Costs:* the jungle's sickness never becomes *characterful*. It will always be the same fevers the
  player has met in six other places, just more often.

- **C. Keep seven, but give two of them a jungle-specific twist rather than replacing them.**
  *Buys:* a middle path — the same illnesses behave differently here (faster onset, a different
  progression, a different cure route) so the place feels distinct without a new disease being
  written or anything being taken out of the live world.
  *Costs:* the least legible option. A player may never notice that a familiar illness is behaving
  differently, in which case the work bought nothing.

### Q3 — Are the insects their own kind of threat, or just more animals?

*Why you are being asked:* of the four dangers you named, insects turned out to be the genuinely
empty one — and empty in a lucky way. The machinery for a huge insect that chews trees down is
**already built and working**; it just has nothing to drive, because the creature itself is a
placeholder squirrel standing in until someone makes it. So the cheap option here is unusually cheap.

- **A. Yes — insects are their own layer, and they work on the *forest*, not on you.**
  They chew the tree bases, they bring giants down, they are why the canopy is dangerous overhead.
  They are not primarily out to eat your people.
  *Buys:* the cheapest real danger available, because the falling-tree machinery is already shipped
  and tested. It also gives the jungle a genuinely different *kind* of fear — the ground is safe and
  the sky is not — which nothing else in the biome does.
  *Costs:* needs one new creature and its art before any of it is visible. Until that exists, this
  option shows the player nothing.

- **B. No — fold them into the animal cast and move on.**
  The jungle already has twenty-seven animals, several of them insect-fleshed, venomous and prone to
  turning on you.
  *Buys:* nothing new to build, and the danger is arguably already sufficient. Effort goes to the
  reward side instead.
  *Costs:* one of your four named dangers stays a label rather than a thing, and a piece of working
  machinery stays unused.

- **C. Yes, and go further — a nest you can find, rob, and regret disturbing.**
  Insects become a *place* on the map as well as a creature: a structure with something worth taking
  inside it.
  *Buys:* the strongest version — a danger that is also one of the rewards, which is the pattern the
  rest of the biome already follows.
  *Costs:* by far the most work of the three, and the nest-and-swarm idea is the sort of thing that
  either lands hard or becomes an annoyance that ends colonies without a story.

### Q4 — Does the jungle get harder as the player gets better?

*Why you are being asked:* this decides whether learning the jungle is a real reward or a treadmill,
and it has to be decided before the payoffs are tuned, because it changes what they are compensating
for.

- **A. No. The danger stays flat; the player gets better.** *(recommended)*
  The jungle is exactly as lethal on trip fifty as on trip one — what changes is that the player
  now knows where to walk, what to wear, and when to leave.
  *Buys:* competence is the reward, and it is permanent. A player who learned this place *keeps* what
  they learned, which is the strongest possible reason to come back. It is also the honest version of
  the arc you already have.
  *Costs:* a very good player will eventually find the jungle routine. The fear fades even though the
  place hasn't changed.

- **B. Yes — the jungle answers back as you get stronger.**
  *Buys:* the place never stops being frightening, at any point in a long game.
  *Costs:* it erases the only thing the player earned by learning, and it is the same shape as the
  runaway-growth problem you have deliberately stamped out elsewhere. Most players read it as the
  game cheating.

- **C. Flat danger, but the *stakes* rise on their own.**
  Nothing about the hazards changes — but a player with a built-out camp simply has more standing in
  the path of a falling tree than a trespasser with a backpack did.
  *Buys:* the fear comes back late in the game without the game ever cheating, because it is the
  player's own investment that is at risk. This already happens naturally with the falling trees.
  *Costs:* punishes the players who committed most to the place, which can read as a penalty for
  playing along.

### Q5 — Where does the "endless cuisine" feeling actually come from?

*Why you are being asked:* "seemingly endless" cannot be built by writing endless dishes — that way
lies hundreds of near-identical recipes, which is a lot of work that reads as padding. It has to come
out of a small number of ingredients combining. The question is what the player is combining *for*.

- **A. Novelty. The colony remembers what it has eaten, and rewards you for surprising it.**
  A handful of ingredients, each carrying a flavour; a dish is any legal combination and gets its name
  and its effect from what went in. A combination eaten recently is worth less; a new one is worth
  much more.
  *Buys:* genuinely bottomless from about thirty pieces of authoring, and — the real prize — it keeps
  sending the player into the jungle *after food has stopped being a problem*. The reward is variety,
  and variety is the one thing a warehouse cannot hold.
  *Costs:* asks the player to keep notes, and a player who does not engage just eats the same thing
  and sees a mild penalty they may not understand.

- **B. Discovery. Certain combinations are secretly special, and finding them is the game.**
  Most combinations are ordinary; a hidden few are extraordinary, and a cook learns them.
  *Buys:* the strongest feeling of *cuisine* specifically — a clan with recipes, traditions, a
  culinary reputation. Very satisfying when a player finds one.
  *Costs:* finite by definition. Once the good combinations are known — and they will be shared
  within a week of release — the space stops being endless and becomes a checklist.

- **C. Freshness. What you can cook depends on how recently it was picked.**
  The best flavours only exist on ingredients that are still fresh, so the best dishes can only be
  cooked near where they grew.
  *Buys:* the tightest fit with the rest of the biome, and it does the most to stop the jungle
  becoming somewhere to live — a kitchen at home can never cook well.
  *Costs:* the most logistically fussy of the three, and the option most likely to feel like an
  errand rather than a cuisine.

*(These three are not exclusive — A is the engine, C is the brake, and B can be layered on later.
That combination is the recommendation if you want one.)*

### Q6 — How hard is the clock on the valuable things?

*Why you are being asked:* everything good the jungle produces is currently designed to spoil, which
is the main thing stopping the place becoming a factory. How hard that clock bites is a taste
question, and it is the difference between "a tense delivery run" and "an annoying timer".

- **A. Hard. The best grade cannot leave the jungle at all.**
  *Buys:* the strongest guarantee that nothing here becomes an industry, and it makes the forward camp
  matter enormously. The good stuff is used where it is made.
  *Costs:* players who like trading and stockpiling get nothing from the biome's best content, and
  some will find it simply withholding.

- **B. Medium. The best grade travels for a couple of days and loses potency as it goes.**
  *Buys:* a real delivery game — a reason to build routes, fast transport and a sealing workshop —
  while still forbidding a warehouse.
  *Costs:* more moving parts, and the loss-over-time rule needs to be visible or it feels arbitrary.

- **C. Soft. It spoils, but slowly, and a good workshop can preserve most of it.**
  *Buys:* the friendliest option, and the one that most rewards infrastructure. The jungle's payoff
  becomes something a player can plan a whole colony around.
  *Costs:* the weakest brake by a wide margin, and the most likely to end with the jungle as the best
  place to live — which is the failure this whole design is guarding against.

### Q7 — How far does the regrowth go? *(only if Q1 lands on B, or later)*

*Why you are being asked:* growing a limb back is the strongest idea in the pass and the easiest to
spoil by making it too clean. How far it goes is a tone question about your setting, not a mechanical
one.

- **A. Repair only. Lost parts come back as they were.**
  *Buys:* a clean, humane, extremely desirable payoff that needs no explanation.
  *Costs:* the least distinctive, and it quietly competes with prosthetics rather than saying
  something new.

- **B. Repair, imperfectly. What grows back works, and is visibly not quite the same.**
  *Buys:* the setting's voice — a clan of scavengers whose bodies are patched with jungle. Much more
  memorable than A, and the imperfection is what makes it feel like a bargain rather than a cure.
  *Costs:* needs art and description work to land, and some players will resent a permanent blemish
  on a rescued colonist.

- **C. Repair, and sometimes more than you asked for.**
  The failure mode is overgrowth — something keeps growing and has to be cut back.
  *Buys:* the most frightening and most thematically exact version: the jungle's defining property is
  growth that will not stop, and this is that property applied to a person.
  *Costs:* body horror, which is a deliberate tonal choice and yours alone to make. It also risks
  players never using the procedure at all, which wastes the best idea in the biome.

## 6. UNMEASURED / needs the Windows machine

**Nothing below was established on this machine, and nothing below should be treated as a finding.**
There is no running game, no def dump and no decompiler here, so every mechanism question the design
above rests on is listed rather than answered. ⛔ No vanilla or third-party defName appears that was
not read off a file in this repo.

### 6a. Mechanism questions the ranked build order depends on

| # | question | which reward it gates | why it matters |
|---|---|---|---|
| U1 | When a pawn recovers from a vanilla disease, is there any durable, mod-readable record that they had it — and is there a hook at recovery a mod can attach a permanent immunity to? | **R1, ranked #1** | If there is no recovery hook, R1 needs its own disease to hang off, which merges it with Q2 option A and changes its cost from *low* to *medium* |
| U2 | Is there a mechanism that gates a job, a work type or a caravan role on a pawn carrying a given condition? | **R1** | R1's "qualification" half. A mood/efficiency penalty on unmarked pawns is the fallback if a hard gate does not exist |
| U3 | Can a cooked meal carry its ingredient set forward in a form readable when it is eaten? | **R3, ranked #2** | The entire free-scaling property of the cuisine system. If not, the fallback in §4 R3 applies and R3 drops several places |
| U4 | Does the base game already track recently-eaten food variety, and if so can it be extended rather than duplicated? | **R3** | The palate memory should ride an existing system if one exists — Q5 option A is much cheaper if it does |
| U5 | Can a region's foraged yield be more than one item — a table, or a weighted set? | R3, and his "food abundance" | The biome's forage is a single berry row today (§2b). If the field takes only one def, "tremendous abundance" has to be delivered by plants and the catch, not by forage |
| U6 | Can a mod restore a **missing body part** to a living pawn, and what is the route? | **R4, the marquee** | R4 does not exist if this is impossible. This is the single highest-value measurement in the list |
| U7 | What is the actual shape of a disease incident plus its condition — read off a real working example? | Q2 option A | §1c established this project has never authored one. It must be read, not inferred |
| U8 | Can a research project be made to progress only while a pawn is working in a given region? | R7 | The field-station idea. A conventional bench with a region-gated *unlock* is the fallback |
| U9 | Is predator and enraged-animal target selection reachable by a mod? | R8 | R8's scent-masking. If not, R8 degrades to a stealth/mood effect and loses most of its point |
| U10 | Can a wall-like building regrow or self-repair on a timer? | R9 | R9's living walls. The chamber precedent suggests yes but the chamber is terrain, not a building |
| U11 | Can faction attitude respond to a colony being the sole supplier of something? | R10 | R10's whole payoff is social rather than monetary |
| U12 | Can a plant be made cultivable only after a research unlock, with a different yield than its wild form? | R6 | The cultivar programme, and §4c's release valve |

### 6b. Live-state facts this pass could not check

- 🔴 **Which of the two Greentide region definitions the live saved world is actually running today**,
  and whether the movement-cost contradiction recorded in §1 still stands in the live file. §1 read
  both files on disk; it did not read the game.
- **Whether the seventh illness (organ decay) is present on the generic twin yet.** §1c read it as
  present on the live twin only, from the files. That is a disk read, not a live read.
- **Whether the biome's farming-camp permission behaves as §4c assumes** — that a camp can feed itself
  without becoming an export base. The seven defences in §4c are a design stance; none of them has
  been observed in play.
- **Whether the twenty-seven-row animal roster actually spawns at the stated weights** on the live
  map, which bears on R5's premise that this region holds the planet's gene pool.

### 6c. Explicitly out of scope here, and where it belongs

- **Tile counts and where this biome appears on the planet.** Not touched, by standing ruling — the
  planet is painted once, at the end, after every biome is its own mod.
- **The movement-cost contradiction.** Noted in §1, belongs to the density item, and is not fixed
  here.
- **Mod Settings.** Per the standing rule, every category in §4 needs its own toggle and the extreme
  tunings need sliders. That is spec work for whichever item builds each category, not a measurement,
  and it is recorded here so it is not forgotten: **ten categories means ten feature gates.**
- **Names.** Every invented word in §4 is a placeholder for a concept. The naming pass owns them, and
  nothing in §4 names any franchise.
