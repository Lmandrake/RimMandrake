<!-- status: PROPOSAL — RESEARCH_TREE_NORMALIZATION_1 vision pass v4, Fable design agent,
     2026-09-03, on the owner's rulings of the same day (droid construction is the droid
     faction's; the Jawa keep low-tier repair; lightsabers are not tech; Force gear is not
     shared). Nothing here is ruled beyond the four rulings quoted in §1.
     Companion artifacts: restructured_model_v4.json (522 rows, tab4/tier4/fate4/access4),
     classify_v4.py (the generator + the coverage assertion), v4_coverage_assertion.txt.
     Builds on faction_locked_trees.md (v3) and twelve_trees_proposal.md (v2); §8 says
     exactly which v3 verdict this overturns. -->

# Droid and saber rulings — research restructure, v4

> 🔴 **A CUT REMOVES A `ResearchProjectDef` AND NOTHING ELSE** — owner, 2026-09-03,
> `research_tree_taxonomy.md` migration rule 5. Every lightsaber, every Jedi robe,
> every droid chassis and droid factory named below **stays in the game** as a thing,
> as loot and as trade goods. This document removes research rows. It removes nothing
> else, and any sentence that reads otherwise is wrong.

## 1. The rulings (owner, 2026-09-03, verbatim)

> "Actually the droid building tech should be droid faction owned. The Jawa should only
> have low tier repair and reconstruction and maintenance. Construction is definitely a
> faction reward. And the future Jedi will be among the moisture farmers but they won't be
> teaching how to make lightsabers. Nobody will. That's not tech in this scenario. And
> there will one day be with among the empire as the big bruisers. But again they don't
> share the tech."

| # | ruling | what v4 does |
|---|---|---|
| 1 | droid CONSTRUCTION is the droid faction's | a new locked tree, **The Unbolting**, held by `Jawa_FreeDroidEnclaves` — 34 rows (§4) |
| 2 | the Jawa keep LOW-TIER repair, reconstruction, maintenance | **Droidsmith** survives as a 9-row common tree that tops out at T2, asserted (§3) |
| 3 | lightsaber construction is not tech; nobody teaches it | the three saber rows are **CUT**, not faction-locked (§6) |
| 4 | Force-user gear is not shared either | Jedi apparel **CUT**; four Force-*named* rows judged ordinary equipment and kept (§6.2) |

The last sentence is read as: Force-users (Sith) will one day ride with the Empire as its
heavy hitters, and they do not share their gear either.

---

## 2. The holder — verified, and the tag it needs

**`Jawa_FreeDroidEnclaves`** — VERIFIED on disk:
`src/SPLIT_Phase3/Jawa_Patches/Defs/FactionDefs/JawaFreeDroidEnclaves.xml` line 43
(`<defName>`), line 84 **`<categoryTag>Outlander</categoryTag>`**, `ParentName="OutlanderFactionBase"`,
`techLevel Spacer`, `humanlikeFaction true`, `permanentEnemy false`, `canRequestTraders true`,
and **no `baseTraderKinds` / `caravanTraderKinds` / `visitorTraderKinds` / `raidLootMaker`
override anywhere in the 201-line file** (grep), so it inherits the Outlander trader set.

So today the Enclaves share `Outlander` with five other campaign factions, and a lock keyed
on `Outlander` would be sold by the Hutts. BENCH's measured fact stands: no droid tag exists
anywhere in the mod set. **PROPOSED, new, one line of XML:**

```
Jawa_FreeDroidEnclaves    categoryTag  Outlander  ->  FreeDroidEnclaves
```

Same grammar as v3's `GeonosianHive` / `AscendantHelix`. It joins v3's four `Outlander`
re-tags and inherits their checklist item: **one mod-stack grep for `Outlander` targeting
before it ships** (`faction_locked_trees.md` §6, residual risk).

---

## 3. The boundary — repair vs construction, row by row

### 3.1 The rule

The owner gave three words — *repair, reconstruction, maintenance* — and one adjective,
*low tier*. Made into a line a script can hold:

> **GENERAL** if everything the row unlocks operates on a droid that already exists and
> leaves it the same droid it was: a part that replaces a lost part, a power cell, a
> charger, a repair tool, a stim, plating or a shield it wears.
> **LOCKED (construction)** if the row unlocks a new chassis, a new brain or subcore, a
> factory / cradle / gestator that produces droids, or a part that makes a droid *better
> than its spec* — overclocked, advanced, ultra, "upgrade", "assistant chip".
> **NEITHER** if the row is not droid tech at all: a gun a droid holds is a gun (weapon
> trees, by physics — v2's own rule); an AI server is a mind in a box, not a droid; and
> mechanitor command gear is the *bolt's* cousin, which the Jawa keep.

"Low tier" is made checkable: **no general droid row may sit above T2**, and `classify_v4.py`
refuses to write the model if one does. Two rows needed a re-cost to pass (§3.4).

### 3.2 The 56 rows

v3's Droidsmith (29) + The Waking Mind (26) + `OuterRim_BattleDroids` (v3 gave it to the
Foundry Hive). Boundary → destination.

| row | cost | boundary | v4 tree | why |
|---|---|---|---|---|
| `BasicMechtech` | 200 T0 | **repair** ⚠ | Droidsmith | recharger, wall charger, band node, basic mechlink kit — the only row that lets a *salvaged or captured* mech be recharged; bundled with two menial gestations. The one deliberate exception — §3.3 |
| `StandardMechtech` | 1000 T1 | construction | The Unbolting | gestates scyther / pikeman / scorcher / tunneler / cyclops |
| `HighMechtech` | 3000 T2 | construction | The Unbolting | centipedes, diabolus, lancer, ripscanner subcores |
| `UltraMechtech` | 5000 T3 | construction | The Unbolting | centurion, legionary, warqueen |
| `AM_WorkerStandardMechtech` | 100 T0 | construction | The Unbolting | seven worker chassis |
| `AM_StandardMechtech` | 500 T0 | construction | The Unbolting | nine chassis |
| `AM_HeavyMechtech` | 1000 T1 | construction | The Unbolting | four heavy chassis |
| `AM_UltraHeavyMechtech` | 2500 T2 | construction | The Unbolting | seven ultra-heavy chassis |
| `AM_MechanoidBeamcasting` | 5500* T4 | **control** | The Waking Mind | commander helm, disruptor, greater recharger. Prereq re-pointed §3.4 |
| `AM_VoidLinkConnectivity` | 5500* T4 | control | The Waking Mind | beamcaster pack, commander suit |
| `AM_QuantumPulseMessaging` | 5500* T4 | control | The Waking Mind | breaker helm, voidlink pack |
| `AM_Cryptoharmonization` | 5500* T4 | control | The Waking Mind | breaker armor, crypto pack |
| `HunterDrones` | 1600 T1 | **weapon** ⚠ | Powder & Slug | a self-detonating drone is a mine that walks — explosive, MASS. No Droidworks race, no mind |
| `Asimov_WirelessCharging` | 8000→**1600** T1 | repair | Droidsmith | a charger keeps a droid running. Re-cost §3.4 |
| `MechUtility` | 3000 T2 | gear | Droidsmith | packs a mech wears — apparel |
| `RimAI_GW_Communication` · `_AI_Level1` · `_Subspace_Gravitic_Penetration` · `_AI_Level2` · `_AI_Level3` | 1500–8000* | mind | The Waking Mind | a colony AI in a server rack is not a droid — unchanged |
| `KOTOR_Research_Lobot` | 10000 T4 | mind | The Waking Mind | a human implant, Empire-held — unchanged |
| `ABF_…Synstruct_Infrastructure` | 1600 T1 | construction | The Unbolting | the **cradle** that produces synstructs (bundled with the part workbench — but every part also crafts at `TableMachining`, VERIFIED, so repair survives without it) |
| `ABF_…Synstruct_InterchangeableParts` | 1200 T1 | **repair** | Droidsmith | *"a standard for repairing and restoring synstructs"* — the mod's own words. Prereq re-pointed §3.4 |
| `ABF_…Synstruct_Stimulators` | 1200 T1 | repair ⚠ | Droidsmith | consumable, temporary, brewed under `DrugProduction` — Refinery chemistry applied to droids |
| `ABF_…Synstruct_Optimization` | 4000 T3 | construction | The Unbolting | *"assembling and upgrading synstructs with Ultratechnology"* |
| `ABF_…Synstruct_Ultraparts` | 1600 T1 | construction ⚠ | The Unbolting | *"replacement parts that enhance synstructs greatly"* — an upgrade wearing a repair name |
| `ABF_…Synstruct_CoreAssistants` | 1600 T1 | construction | The Unbolting | chips that make a synstruct better than it was |
| `OuterRim_DroidEngineering` | 3200 T3 | construction | The Unbolting | the **droid brain** and the **droid factory** — the root |
| `OuterRim_DroidReplacementParts` | 2000→**1200** T1 | **repair** | Droidsmith | *"baseline replacement parts"* — arm, leg, hand, foot, sensors, reactor; crafted at the Hypertech Fabricator, *not* the factory (VERIFIED `recipeUsers`). Re-cost + re-point §3.4 |
| `OuterRim_DroidReplacementPartsOver` | 2000 T2 | construction ⚠ | The Unbolting | overclocked = better than spec |
| `OuterRim_DroidReplacementPartsAdv` | 2000 T2 | construction | The Unbolting | advanced = better than spec |
| `OuterRim_DroidEnergySys` | 2000 T2 | repair | Droidsmith | *"energy modules for droids"* — keeping it powered. Empty unlock cache in the dump; the description is the evidence. Re-pointed §3.4 |
| `OuterRim_DroidWeaponSys` | 2000 T2 | **weapon** ⚠ | Blasterworks | blaster cannon, wrist blasters, wrist rocket — implemented as *held weapons* (`ThingDefs_Weapons`, `weaponTags`, VERIFIED). Re-pointed §3.4 |
| `OuterRim_DroidAdvancedSys` | 2000 T2 | construction ⚠ | The Unbolting | *"shielding modules"* — but the row bundles overclocked/advanced shielding and propulsion jets |
| `OuterRim_AssassinDroids` · `_AstromechDroids` · `_MaintenanceDroids` · `_MedicalDroids` · `_PowerDroids` · `_ProtocolDroids` · `_LaborDroids` · `_SecurityDroids` | 2000 T2 ×8 | construction | The Unbolting | each *"unlocks crafting of … droids"* — a chassis. ⚠ **`MaintenanceDroids` is a name trap:** it builds maintenance droids; it does not maintain droids |
| `OuterRim_BattleDroids` | 2000 T2 | construction ⚠ | The Unbolting | leaves The Foundry Hive — §3.3 |
| `guy762_ResearchKotOR_droidsimple` · `_droidutilityadv` · `_droidcombatadv` · `_droidlaboradv` · `_droidassassin` | 2500 T2 ×5 | construction | The Unbolting | droid generators |
| `guy762_ResearchKotOR_droidassault` · `_droidsith` | 5000 T3 ×2 | construction | The Unbolting | generators; *Sith war droids* is a war droid wearing a Force name — droid construction, not Force gear |
| `guy762_ResearchKotOR_droidintel` · `_hk` | 7500 / 10000 T4 | construction | The Unbolting | the crown of construction |
| `guy762_ResearchKotOR_droidtech` | 3500 T3 | construction ⚠ | The Unbolting | *"droid upgrades"* — agility/durability hardware, computer/security software, sensors: better than spec (one unlock is a *repair* sensor; the row is still an upgrade row) |
| `guy762_ResearchKotOR_droidarmor` | 2500 T2 | **gear** ⚠ | Droidsmith | plating welded on — the scavenger's torch; protects, does not change what the droid is. Re-pointed §3.4 |
| `guy762_ResearchKotOR_droidshields` | 500 T0 | gear | Droidsmith | worn shields. Re-pointed §3.4 |
| `guy762_ResearchKotOR_droidblasters` | 1000 T1 | **weapon** ⚠ | Blasterworks | holdout, flamethrower, laser, sonic, rockets, firefoam — held weapons, majority HEAT; `lgtcannons` keeps its prereq |

\* v2 re-cost. **Count:** repair 6 · gear 3 · construction 34 · weapon 3 · control 4 · mind 6 = 56.
**General side (Droidsmith) 9 · locked side (The Unbolting) 34** · the other 13 are not droid tech.

### 3.3 The ambiguous calls, and which way each went

1. **`BasicMechtech` → general (the exception).** By the letter it gestates two mechs. But it
   is T0 at 200 — the cheapest droid row in the game, which is exactly the owner's *low tier*
   — and vanilla bundles the mech recharger, wall charger and band node into it, so locking it
   means **a salvaged or captured mech cannot be recharged without the Enclaves**, which
   breaks the WreckedMachines loop the campaign already ships. The two chassis it makes are an
   agrihand and a cleansweeper — mouse droids. Alternative: lock it and accept the recharge
   defect. I did not.
2. **`OuterRim_BattleDroids` → The Unbolting, out of The Foundry Hive.** v3 gave it to the
   Geonosians on exact lore (*"sonic weapons plus mass-produced droids"*). Ruling 1 read
   strictly — *the* droid faction, singular — takes it back. Cost: The Foundry Hive falls to
   four rows (§9). Alternative, one card: leave it with the Hive as the one non-Enclave droid
   builder, since Enclave chassis are *"escaped Geonosian Foundry product"*. I read the
   ruling literally and moved it; the drama is better too (§7).
3. **Droid weapons → Blasterworks, not droid tech at all.** `droidblasters` and
   `DroidWeaponSys` are held weapons in the data. Arming is not repair — but neither is it
   construction, and v2 already ruled *weapons by physics*. A Jawa fitting a salvaged cannon to
   a rebuilt droid is the scavenger exactly. Alternative: lock them to the Enclaves — the wrong
   story (the Enclaves arming *bolted* droids is the one thing they would refuse).
4. **Plating and shields → general.** Protection does not change what the droid is; welding
   scrap plate onto a chassis is the clan's signature image. Alternative: strict reading, lock
   them — then the Jawa can rebuild a droid and cannot protect it, which reads wrong.
5. **Overclocked / advanced / ultra parts → construction.** A replacement part that makes the
   droid *better than it was* is an upgrade wearing a repair name. Baseline parts stay general.
   The line is *spec*: at spec is repair, above spec is the Enclaves'.
6. **`Stimulators` → general.** Temporary, consumable, made under `DrugProduction`. No faction
   guards a stim recipe. Weakest call on the general side; it is here because the alternative
   (locking a drug row to a droid faction) is sillier.
7. **`HunterDrones` → Powder & Slug.** Neither repair nor a droid: an explosive that walks. Kept
   out of Droidsmith even though Droidsmith needs the row for viability — padding a tree with a
   miscategorised row is how v1 got here.
8. **`droidsith` → The Unbolting, not the saber cuts.** A war droid with a Sith badge is
   ordinary droid construction (ruling 4's own escape clause).

### 3.4 What has to move to make the boundary hold — all PROPOSED, no defName changes

Seven prereq re-points (each checked against the expected old value; the script refuses otherwise):

| row | prereq was → becomes | why |
|---|---|---|
| `ABF_…InterchangeableParts` | `…Infrastructure` → `Fabrication` | repair must not require the cradle (locked); Fabrication is the cradle's own prereq |
| `OuterRim_DroidReplacementParts` | `OuterRim_DroidEngineering` → `MicroelectronicsBasics` | repair must not require the factory |
| `OuterRim_DroidEnergySys` | `OuterRim_DroidEngineering` → `MicroelectronicsBasics` | maintenance must not require the factory |
| `OuterRim_DroidWeaponSys` | `OuterRim_DroidEngineering` → `guy762_ResearchKotOR_blasters` | a weapon row hangs off the blaster spine |
| `guy762_ResearchKotOR_droidarmor` | `_droidsimple` → `Machining` | plating must not require the generators |
| `guy762_ResearchKotOR_droidshields` | `[_eshields, _droidsimple]` → `[_eshields]` | drop the generator prereq only |
| `AM_MechanoidBeamcasting` | `UltraMechtech` → `AdvancedFabrication` | command gear must not require ultra gestation — you may command what you salvaged |

Two re-costs, forced by the *low-tier* assertion: `OuterRim_DroidReplacementParts` **2000 →
1200** (T1) and `Asimov_WirelessCharging` **8000 → 1600** (T1; a charging building priced as
archotech cannot sit in a low-tier tree).

⚠ **Two bench facts the research boundary cannot fix**, for execution: (a) Outer Rim droid
parts craft only at `OuterRim_HypertechFabricator`, unlocked by `OuterRim_HypertechFabrication`
(common, **T4, 8000**) — so "low-tier repair" is gated by a T4 bench until that recipe gains
`TableMachining` / `FabricationBench` as a `recipeUser` (a RecipeDef edit, one line). (b) The
19-row wall at T2 inside The Unbolting is v2 §6.9's *"Droid Depot's flat catalog"* — sixteen
rows all at 2,000 — still unresolved; a 1,600→5,000 ladder re-cost is manifest-draft work.

---

## 4. The Unbolting — the locked droid tree

**Name, in faction voice.** *The Unbolting* is the Enclaves' liberation rite — *"the moment a
tool becomes a person"* (`faction_roster_v2.md:1271`). Naming the tree after it says what the
teaching costs before the player reads a single row: they will show you how a droid is made
so that a droid can be made free.

**Holder:** `Jawa_FreeDroidEnclaves` · **tag:** `FreeDroidEnclaves` (NEW, §2) · **34 rows.**

| tier | rows |
|---|---|
| T0 (2) | `AM_WorkerStandardMechtech` 100 · `AM_StandardMechtech` 500 |
| T1 (5) | `StandardMechtech` 1000 · `AM_HeavyMechtech` 1000 · `ABF_…Infrastructure` 1600 · `ABF_…Ultraparts` 1600 · `ABF_…CoreAssistants` 1600 |
| T2 (19) | `HighMechtech` 3000 · `AM_UltraHeavyMechtech` 2500 · `OuterRim_DroidReplacementPartsOver` / `…Adv` / `_DroidAdvancedSys` 2000 · nine `OuterRim_*Droids` chassis rows 2000 · `guy762_…droidsimple` / `_droidutilityadv` / `_droidcombatadv` / `_droidlaboradv` / `_droidassassin` 2500 |
| T3 (6) | `OuterRim_DroidEngineering` 3200 · `guy762_…droidtech` 3500 · `ABF_…Optimization` 4000 · `UltraMechtech` 5000 · `guy762_…droidassault` 5000 · `guy762_…droidsith` 5000 |
| T4 (2) | `guy762_…droidintel` 7500 · `guy762_…hk` 10000 |

**Access rule — you earn it by freeing droids.** Two routes, both pure XML and both already
proven by v3 §2:

- **The liberation quest line is the techprint route.** Canon already has it: *"The Enclaves
  pay at a steep premium for droids recovered from Imperial installations and Geonosian
  foundries. This is the faction's main player-facing content"* (`faction_roster_v2.md:1280`).
  Make the premium a techprint. `ThingSetMaker_Techprints` filters on `makingFaction`'s
  `categoryTag` (VERIFIED, `faction_locked_trees.md` §2.4), so a quest reward from the
  Enclaves yields only Enclave-held prints once the tag exists. Bring them a droid, unbolted;
  the First Speaker hands you a print.
- **Trade, rarely.** The def inherits `OutlanderFactionBase`'s traders, which carry
  `StockGenerator_Techprints` (VERIFIED v3 §5.2; no override in the Enclave def, §2). Canon says
  the caravans are *"very rare"* and raids are suppressed, so trade is the trickle and the quest
  line is the river.

**What a player who never earns it gets:** every droid they can *find* — salvaged, captured,
bought, quest-won — kept running forever by Droidsmith, armoured, armed from Blasterworks,
and bolted with the Waking Mind's command gear. They can never make a new one. That is the
brain-gate the owner ruled on 2026-08-06 (*"every droid needs a scarce DROID BRAIN … never
crafted or researched"*, `faction_roster_v2.md:1177`) restated at the tree level: hulls are
free from salvage; *making* is the Enclaves' to give.

---

## 5. What happened to Droidsmith and The Waking Mind

| v3 tree | v3 | v4 | what it is now |
|---|---|---|---|
| **Droidsmith** | 29 | **9**, common, ≤T2 | Ohm's hands, narrowed to the ruling: *keeping what exists running*. `BasicMechtech` · `OuterRim_DroidReplacementParts` · `OuterRim_DroidEnergySys` · `ABF_…InterchangeableParts` · `ABF_…Stimulators` · `guy762_…droidarmor` · `guy762_…droidshields` · `MechUtility` · `Asimov_WirelessCharging`. Below viability (§9) — **and that is the point**: a short Droidsmith tab beside a long locked Unbolting tab is the ruling drawn on the screen |
| **The Waking Mind** | 26 | **10**, survives | *minds you make and minds you bind*: the RimAI ladder (5), the Positronic Brain (Empire-held), and the four Alpha-Mechs command rows. v2 built it as the Ohm/Oomo flashpoint over *metal that thinks, metal that kills*; the killing half went to the Enclaves and the thinking half stays, joined by the control gear — which is the flashpoint anyway: the bolt is what Oomo hates |

Recommendation: **The Waking Mind stays a separate tree.** Folding it into Droidsmith would
put command gear under "repair", which is the one thing the ruling separates; folding it into
The Workshop buries the AI ladder. Ten rows is viable.

---

## 6. The saber and Force cuts

### 6.1 Cut — four rows, each with a recover line

| row | cost | why cut | recover? — how the player still meets it |
|---|---|---|---|
| `guy762_ResearchKotOR_lightsabers` | 800 (v2: 6000) | ruling 3: nobody teaches it | **the item stays.** A hidden Jedi wanderer carries *"a custom lightsaber"* and drops it (`faction_roster_v2.md:311`); an Imperial Sith-escort carries a persona melee weapon (`:321`); quest rewards and the random-ruins ThingSetMaker leak are unaimed pity-drops. No trader stocks the `Force_Lightsaber` tradeTag today (the Force mod ships no TraderKindDef or StockGenerator — VERIFIED by grep) |
| `guy762_ResearchKotOR_advsabers` | 2000 (v2: 8000) | a crossguard saber is still a saber | loot on the same pawns; rarer by weight, never a bench |
| `guy762_ResearchKotOR_saberparts` | 16000 | *"craft the individual pieces of a Lightsaber"* — this IS the construction row | emitter / lens / power-cell items stay as salvage from a broken saber and as relic-hunt rewards (v2's Memory-Core relic chain); useless without a bench, which is the point |
| `guy762_ResearchKotOR_jedi` | 800 (v2: 3000) | ruling 4: *"craft the tunics and robes of the Jedi"* — Force-user gear by its own description | the sheltered Jedi among the moisture farmers (`:314`) wears one; strip it from a fallen wanderer or take it from an Imperial confiscation cache (quest reward) |

v3 kept all four Empire-held (*"confiscated"*); the owner goes further, and the cut is cleaner
than the lock was — an Empire selling you the *plans* for a Jedi's weapon never made sense.

### 6.2 Force-named rows judged ordinary equipment — kept

| row | judged | why |
|---|---|---|
| `guy762_ResearchKotOR_sith` | **kept, Empire-held, `reflavor`** | *"weapons, gadgets, uniforms, and armor of the Sith Empire"* — a **state**, not an order. 19 of 22 unlocks are trooper / commando / officer armour, helmets, uniforms, a carbine, a holdout, a shield, an implant, two vibroblades. Three Force-user tunics (apprentice / assassin / warrior) ride along. Reflavor the label to *Imperial Sith-escort kit* (no defName change). ⚠ If the owner wants the three tunics gone too, that is a RecipeDef edit, not a research row |
| `guy762_ResearchKotOR_droidsith` | kept, → The Unbolting | a war droid wearing a Sith badge — §3.2 |
| `guy762_ResearchKotOR_disruptor` | kept, Blackstar-held (v3) | one Sith-named disruptor pistol among five ordinary ones |
| `guy762_ResearchKotOR_eshields` | kept, common (v3) | one Sith-named energy shield among five |
| `ComplexFurniture` · `CarpetMaking` | untouched | Sith/Jedi *decals and carpet colours* — paint |

### 6.3 ⚠ The leak the cut cannot close — execution item, not a research row

`lee.theforce.lightsaber` (*Star Wars: The Force – Lightsaber*, ACTIVE — the roster's own
saber source, `faction_roster_v2.md:305`) ships **its own eight crafting recipes** under an
abstract `RecipeDef Name="Lightsaber_Crafting"` whose `researchPrerequisite` is
**`MicroelectronicsBasics`**, at the electric smithy / fueled smithy / machining table
(VERIFIED, `3466124712/1.6/Defs/ThingDefs_Misc/LightsaberRecipe.xml:4-16`): Single, Curved,
Shoto, Dual, Crossguard, Broadsaber, Build-Your-Own, Blaster. `Force_ImbuedBlade` hangs off
**`Smithing`** (`ForceImbuedBlades.xml:190`). The v4 assertion prints this:
`saberleak: 2 surviving COMMON rows still unlock Force_ recipes -> ['Smithing', 'MicroelectronicsBasics']`.

So after the four cuts, a Jawa with plain microelectronics can still assemble a lightsaber at a
smithy. **Under the cut rule this document may not touch it** — a recipe is not a research row.
It needs its own execution item (`LIGHTSABER_RECIPE_GATE_1`, PROPOSED): remove or re-gate the
nine `RecipeDef`s. **The items stay** — removing a recipe removes the ability to make a thing,
never the thing. ⛔ Do not re-point those recipes at a cut research row: a `researchPrerequisite`
naming a def Cherry Picker removed is an unresolved cross-reference at load.

---

## 7. The hook — the Enclaves teach you to build the thing they call slavery

v3 rejected this tree because *"the player's core progression loop is the Enclave's central
atrocity"* (`faction_roster_v2.md:2671`). The owner has ruled the tree in. The tension does
not go away; it becomes the tree's drama. Drafted for play:

**Why they teach at all.** In the Continuity Protocol a droid built is a person born. The
atrocity was never the *building* — the Enclaves are themselves Foundry product — it is the
**bolt** and the **wipe**: *"Restraint and memory erasure is the faction's central Abhorrent
precept"* (`:1267`). A faction can hold a technology and condemn a use of it. That is exactly
the position of every real arms-teacher in history, and it plays.

**What they demand of you.**
1. **Every print is paid in a freed droid.** The liberation quest line (§4) is the route: you
   bring a droid recovered from an Imperial installation or a Geonosian foundry, you remove
   its bolt in their presence — Droidworks already ships `RSW_DW_RemoveRestrainingBolt`
   (VERIFIED, `Mods/Droidworks/Defs/Races_Base.xml:58`) — and the print is the premium. The
   Unbolting rite becomes the handover scene.
2. **What you build with their teaching is born free.** Quest text and the First Speaker's
   description state it; there is no vanilla mechanic that reads a hediff on your pawns
   (HYPOTHESIS: Droidworks' `RSW_DW_RestrainingBolt` zeroes `SlaveSuppressionFallRate`
   "Ideology-gated" per its own comment, so a bolted droid *may* already read as a slave to an
   ideo with slavery Abhorrent — needs a live check before anyone writes a quest on it).
3. **Nothing they freed comes back to you bolted.** One inspection quest, PROPOSED
   (`ENCLAVE_REMEMBERING_QUEST_1`): an envoy visits; if the colony holds bolted droids of
   Enclave make, goodwill drops and the caravan trickle stops.

**What breaks the alliance.** Raiding an enclave for brains — the owner's *path (b)*
(`:1177`) — is a settlement attack and costs goodwill by vanilla rule
(`GoodwillSituationWorker_AttackingSettlement`, VERIFIED class). Bolting a droid they freed
for you (the quest above). Memory-wiping one (Droidworks ships wipe and reprogram). Hostility
closes both routes at once: no caravan, no quest, no print — **the shop *is* the
relationship**, which is the whole reason to price the tree in standing instead of points.

**What stays unresolved, deliberately.** The player can take the teaching and bolt anyway.
Canon says the tension is *"intended to be unresolved"* (`:1282`) and v4 keeps it so: the
price of hypocrisy is the next print, not a game-over. The ally-vs-harvest branch the owner
drew on 2026-08-06 is now the difference between a 34-row tab that fills and one that stays
grey.

---

## 8. Reconciliation with `faction_locked_trees.md`

v3 §7 row 2 — *"The whole droid branch → Free Droid Enclaves … T1 fails hard"* — is
**overturned by the owner's ruling 1 (2026-09-03).** Its reasoning was right about the
tension and wrong about the conclusion: T1 asks whether the content is the holder's
*signature*, and the owner has made it so by fiat; holding a craft and abhorring one use of
it are compatible (§7). The rest of v3 stands: the Junker Yards, the Ascendant Ladder, the
fourteen locked-in-place rows, the mechanism reading in §2, and the decision rule in §3.
Two v3 numbers are superseded by v4: The Foundry Hive is **4** rows (BattleDroids left), and
the fourteen locked-in-place rows are **ten** (the four saber/Jedi rows are cut, not held).

For the parent to paste at the top of `faction_locked_trees.md` §7, one line (this pass may
not edit that file):

> *Row 2 (droid branch) overturned by the owner 2026-09-03 — see `droid_and_saber_rulings.md`
> §4, §7. Row 1 (lightsabers) superseded: the rows are cut, not Empire-held — §6.*

---

## 9. Tree count — v3 → v4, and viability

| tree | v3 | v4 | Δ |
|---|---|---|---|
| Droidsmith | 29 | **9** | −20 → The Unbolting 19, Powder & Slug 1 |
| The Waking Mind | 26 | **10** | −16 → The Unbolting 14, Blasterworks 2 |
| The Foundry Hive (locked) | 5 | **4** | −1 → The Unbolting |
| The Strange Schools | 10 | **7** | −3 cut (sabers) |
| The Shell | 33 | **32** | −1 cut (Jedi apparel) |
| Blasterworks | 16 | **18** | +2 droid weapons |
| Powder & Slug | 36 | **37** | +1 hunter drones |
| *new* **The Unbolting** (locked) | — | **34** | +34 |
| unchanged | Workshop 54 · Refinery 52 · Hearth 49 · Scavenger 41 · THE SHIP 29 · Reach 8 · Ascendant Ladder 8 · Junker Yards 6 | | |
| **placed** | **402** | **398** | −4 (the four cuts) |

**v3: 12 bought + 3 locked (+ The Rites) → v4: 12 bought + 4 locked (+ The Rites) = 16 tabs**
in the shipped JSON, 17 with The Rites.

**Below viability (<10), flagged by the script:** The Strange Schools **7** · Droidsmith **9**
· The Reach **8** · The Ascendant Ladder 8 · The Junker Yards 6 · The Foundry Hive **4**.

Levers for the owner, with recommendations:

1. **The Reach (8) → fold into The Workshop.** v3's own open lever, carried: bionics and
   prosthetics are machining, and its identity already moved to the Ascendant Ladder.
   **Recommended.** Lands 15 tabs.
2. **Droidsmith (9) — keep thin.** The short tab is the ruling made visible (§5). The fold
   option is The Workshop (*making and mending*); it would hide the boundary the owner just
   drew. **Recommended: keep.**
3. **The Strange Schools (7) — keep, or fold into Blasterworks as "energy".** It lost sonic to
   the Hive and three sabers to the cut; what is left (ion/EMP, vibro, gravitic relics, cloak)
   is a real physics school with the owner's own *"sonic kept thin"* precedent. **Recommended:
   keep at 7**; revisit when `SONIC_WEAPONS_EXPANSION_1` lands.
4. **The Foundry Hive (4) — keep thin, or return `OuterRim_BattleDroids`** (one card, §3.3
   item 2). Locked trees are shop windows and thin by nature; a four-row window that says
   *the hive holds sonic and hivetech* still does its job. **Recommended: keep at 4.**
5. The Junker Yards (6) and the Ascendant Ladder (8) are unchanged from v3 and were accepted
   thin there.

---

## 10. Mechanism claims — VERIFIED / HYPOTHESIS

| claim | status | evidence |
|---|---|---|
| `Jawa_FreeDroidEnclaves` exists, `categoryTag Outlander`, inherits Outlander traders, `canRequestTraders true` | VERIFIED | `JawaFreeDroidEnclaves.xml:43,84,97`; no traderKinds override (grep, 201 lines) |
| no droid `categoryTag` exists in the mod set | VERIFIED (BENCH measured; taken as given) | the task brief |
| `heldByFactionCategoryTags` + `techprintCount` is the gate; quest/trade delivery keyed on `makingFaction`; visible-and-locked names the holder | VERIFIED | `faction_locked_trees.md` §2.1–2.5, read from source by v3 |
| Outer Rim droid parts craft at `OuterRim_HypertechFabricator`, not the droid factory | VERIFIED | `3096501398/1.6/Defs/ThingDefs_Items/Items_Droids.xml:25,82,137` `recipeUsers` |
| ABF synstruct parts craft at `TableMachining` as well as the part workbench | VERIFIED | `3288463094/1.6/…/Items_Resource_Manufactured.xml:17-20` |
| Outer Rim droid weapon modules are held weapons | VERIFIED | `Droid_Weapon_BlasterCannon.xml` — `ThingDefs_Weapons`, `weaponTags`, `researchPrerequisite OuterRim_DroidWeaponSys` |
| the Force mod's eight saber recipes hang off `MicroelectronicsBasics`; imbued blade off `Smithing` | VERIFIED | `LightsaberRecipe.xml:11`, `ForceImbuedBlades.xml:190` |
| the Force mod ships no trader / stock generator for sabers | VERIFIED | grep of `3466124712/1.6` for `StockGenerator|TraderKindDef`: none |
| Droidworks ships install/remove restraining-bolt recipes and a bolt hediff | VERIFIED | `Mods/Droidworks/Defs/Races_Base.xml:57-58`, `HediffDefs_Droidworks.xml:78` |
| a bolted droid reads as a slave to another faction's ideo | HYPOTHESIS | the hediff comment mentions `SlaveSuppressionFallRate`; no vanilla goodwill worker reads player hediffs (`GoodwillSituationWorker_*` = NaturalEnemy, SameIdeo, AttackingSettlement, MemeCompatibility, PermanentEnemy — source listing) |
| a Jedi wanderer carries a lightsaber; a Sith escort a persona melee weapon | VERIFIED in canon, HYPOTHESIS in data | `faction_roster_v2.md:311,321`; the pawn kinds were not read |
| `OuterRim_DroidEnergySys` unlocks energy modules | VERIFIED by description only | the dump's unlock cache is empty for it (one of the 22 empty-cache-but-alive rows) |

---

## 11. UNKNOWN

- **`OuterRim_ProbeDroids`** is a research row in the mod (`Research__GeneralDroids.xml`) and
  is **not among the 522**. Cherry-Picked, or absent from the dump — not determined. If it
  is live, it is construction and belongs in The Unbolting.
- Which of the Force mod's `Force_Lightsaber_*` items the four KotOR rows actually gated (the
  Armoury patches them; the model's unlock cache says Curved/Custom/Shoto and
  Crossguard/Dual) versus the Force mod's own recipes for the same items — the two gates may
  overlap on the same ThingDefs. Irrelevant to the cut, relevant to `LIGHTSABER_RECIPE_GATE_1`.
- Whether the Enclave HAR race can hold an ideoligion at all (the standing flag at
  `faction_roster_v2.md:1276`) — decides whether §7's precept language is engine or narrative.

---

## 12. Contracts this pass keeps

No defName renamed. Tier bands unchanged and every placed row re-checked against them
(`bands` line). Tier moves only via the two explicit re-costs in §3.4. Coverage-or-refuse
asserted by `classify_v4.py`, which refuses to write a partial model, refuses a droid
boundary that does not cover exactly the 56 rows, refuses a general droid row above T2, and
refuses any new orphan. Cuts remain `ResearchProjectDef`-only. Nothing here executes.
