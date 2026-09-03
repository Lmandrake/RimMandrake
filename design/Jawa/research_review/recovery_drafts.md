<!-- status: PROPOSAL — RESEARCH_TREE_NORMALIZATION_1 recovery pass, Fable design agent,
     2026-09-03, on the owner's directive: "Anything thrown out we'll see if we can't draft a
     version of it that can bring back the core gameplay into the scenario without the non-canon
     weirdness." Companion to twelve_trees_proposal.md, whose §2 already carries recover lines for
     its OWN 30 new cuts; this doc covers the 84 EARLIER cuts that had none.
     Nothing here is ruled. Nothing here re-litigates a cut. -->

# Recovery drafts — the 84 earlier cuts

> 🔴 **A CUT REMOVES A `ResearchProjectDef` AND NOTHING ELSE** — owner,
> 2026-09-03: *"I did not cut the anomaly content. I only cut the players
> ability to research that tech tree."* Every ThingDef, PawnKindDef, building,
> creature and piece of map content stays in the game for the campaign's own
> repurposing. Where this document reads as though cut content is gone, it is
> wrong and this line governs. `research_tree_taxonomy.md` migration rule 5.


**Scope.** The 114 ruled research cuts split 30 / 84. The v2 proposal gave a
recover line to its 30 NEW cuts. These are the other **84**, from
`restructured_model_v2.json` (`fate2 == "cut"`, empty `recover`):

| bucket | rows | the ruling that cut them |
|---|---|---|
| Anomaly | 42 | owner 2026-09-03 — repurposed content, not a player tree |
| Royalty | 19 | canon `royalty.dead_ruled` |
| Dungeon Pack (Continued) | 10 | map/dungeon locations, 0 unlocks |
| Big & Small | 5 | owner 2026-09-03 — out |
| measured dead | 8 | `research_tree_prep.md` §1 |

**The question asked of each row is not "should it come back."** The cuts are
ruled. The question is: *what core gameplay did the row carry, and can that
gameplay re-enter the campaign stripped of the non-canon weirdness?* Verdicts:

- **RECOVER** — real gameplay worth re-entering, with a route.
- **LOOT-ONLY** — the item should exist as salvage or trade; it needs no research row.
- **DEAD** — nothing worth recovering, or the gameplay is already carried elsewhere.

Every mechanism claim is marked **[VERIFIED]** (the def or engine source was
read this sitting) or **[HYPOTHESIS]** (design assertion, not yet checked).

## Index

| # | cluster | verdict | rows |
|---|---|---|---|
| 1 | The bioferrite economy and the containment mechanic | **RECOVER** | 6 |
| 2 | Bioferrite ignition weapons — the flame family | **RECOVER** | 1 |
| 3 | Clean industrial gear misfiled in the Anomaly tab | **RECOVER** | 2 |
| 4 | Bioferrite-and-shard utility structures | **RECOVER** | 5 |
| 5 | The serum bench — injectable combat chem | **RECOVER** | 4 |
| 6 | The psychic ritual chain | **DEAD** | 15 |
| 7 | The ghoul chain | **DEAD** | 4 |
| 8 | Entity-derived exotica (deadlife, revenant spine, lances, void art) | **DEAD** | 5 |
| 9 | Cataphract armor | **RECOVER** | 1 |
| 10 | The two cheap force multipliers (jump pack, gunlink) | **RECOVER** | 2 |
| 11 | The specialist implant chain | **RECOVER** | 11 |
| 12 | The instrument chain → The Rites | **RECOVER** | 3 |
| 13 | Court finery | **LOOT-ONLY** | 2 |
| 14 | Dungeon Pack's ten places | **DEAD** | 10 |
| 15 | Gene tools and animal size serums | **RECOVER** | 3 |
| 16 | Mad science field testing (growth/shrink rays) | **DEAD** | 1 |
| 17 | Android conversion | **DEAD** | 1 |
| 18 | The eight measured-dead rows | **DEAD** | 8 |

**Totals: 38 rows RECOVER · 2 LOOT-ONLY · 44 DEAD · 84 accounted.**

---

# A. The Anomaly bucket — 42 rows

## 1. The bioferrite economy and the containment mechanic — RECOVER (6 rows)

`BioferriteExtraction` · `BioferriteHarvesting` · `BioferriteShaping` ·
`BioferriteGenerator` · `EntityContainment` · `Electroharvester`

**What the gameplay is.** One economy, not six rows. You take a live monster,
you keep it alive in a cage, and the cage pays: it yields a *material* and it
yields *power*. Everything downstream in this bucket is fed by it.

- `Bioferrite` is a **stuff** (categories Metallic + Bioferrite), sharp-armor
  1.1, cold-insulation 2.5, sharp-damage ×1.3, a ×2 MaxHitPoints factor, and
  `commonality 0` / `allowedInStuffGeneration false` — so it never appears by
  accident, only by harvest. It is also a fuel. **[VERIFIED — ThingDef Bioferrite]**
- `BioferriteHarvester` is `CompProperties_Facility` at range 5.1 with
  `ContainmentStrength -15`; its description states it draws biomass from an
  entity held on an adjacent holding platform. `Electroharvester` is the same
  shape at `-25`, producing **2,000 W** from a held entity
  (`basePowerConsumption -2000`). `BioferriteGenerator` burns 6 bioferrite/s
  for **4,000 W**. **[VERIFIED — the four ThingDefs]**
- `EntityContainment` unlocks `HoldingPlatform` (Steel 40), `ElectricInhibitor`
  (+10 ContainmentStrength) and `ShardInhibitor` (+20). `BioferritePlate` is a
  **TerrainDef floor** worth +15 ContainmentStrength. **[VERIFIED]**

This is the loop: *bigger beast → more bioferrite and more power → but harder
to hold*, with containment strength as the whole tension. That is excellent,
non-weird, and it is exactly the register of a clan that scavenges a desert.

**The draft.** *"The Pit."* A captured sarlacc, chained and tapped. The
harvester becomes a **sap-tap**; the electroharvester becomes a **nerve-tap**;
bioferrite becomes **beast-metal** — the fibrous plate the clan renders out of
a living thing that will not stop growing it. The generator burns beast-metal
for current, and the psychic-drone malus reads as the thing screaming.

**Route — and how this relates to `ANOMALY_EXCEPTION_ACCESS_1`.** That item is
the hard gate and it rules the *access*; this cluster only argues the *worth*.
Its criterion 2 is explicit — the route must not reintroduce a research row —
so **none of these six rows returns as a row.** What this draft adds is a
recommendation between its three options:

> **Take (b), the Memory-Core revelation, and grant this cluster's five
> buildings + the Bioferrite stuff as one event package.** Option (a)'s
> class-item grant works but hands the player a functioning industry on day one
> with no discovery, and option (c) throws away the single best resource loop
> in the entire 84. The economy is worth an event author.

**Not recovered inside this cluster:** `BioferriteExtraction`'s cultist
unlocks (`Apparel_CultistMask`, `NerveSpiker`) are Horaxian ritual register —
LOOT-ONLY at best. `BX_BloodletterBlade` appears in the dump's unlock cache but
**RimSage has no def by that name** — see UNKNOWN at the end.

## 2. Bioferrite ignition weapons — the flame family — RECOVER (1 row)

`BioferriteIgnition`

**What the gameplay is.** A flamethrower family: `Gun_Incinerator` (heavy
arc-spray, Steel 75 / Components 6 / Bioferrite 30) and `Gun_HellcatRifle`
(assault rifle with a flame charge, Steel 60 / Bioferrite 20 / Components 7),
both crafted at the `BioferriteShaper`. **[VERIFIED — costLists and recipeUsers]**
Only the *fuel* is exotic; the weapons themselves are ordinary industrial guns
that throw fire.

**The draft.** Into **Blasterworks** (things that kill by HEAT), T2, as the
clan's crude bottom rung *below* the blaster spine: a scavenged igniter that
sprays burning beast-metal. That is a genuinely good position — the tree
currently starts at blasters with nothing beneath them.

**Route.** Reflavor label/description only; keep the defs and the
`BioferriteShaper` as their bench. **Gated on cluster 1** — no beast-metal, no
charge. If the owner takes option (c) on `ANOMALY_EXCEPTION_ACCESS_1`, patch
both costLists to `Chemfuel` and the family stands alone. **[HYPOTHESIS — the
costList patch is trivially expressible but has not been written or tested]**

## 3. Clean industrial gear misfiled in the Anomaly tab — RECOVER (2 rows)

`SecurityDoor` (700) · `TurretPack` (1,400)

**These two carry no weirdness whatsoever.** They are in the Anomaly tab only
because the DLC shipped them there.

- `SecurityDoor`: Plasteel 50 + ComponentIndustrial 2, `designationCategory
  Structure`, 800 HP, airtight, `isSupportDoor`, powered open ×4. Zero
  anomaly ingredients. **[VERIFIED]**
- `Apparel_PackTurret`: Steel 70 + ComponentIndustrial 2, made at
  `TableMachining`, one-use deployable battery turret at range 22.9. Zero
  anomaly ingredients. **[VERIFIED]**

**The draft.** Straight re-home, no reflavor and no new def:
`SecurityDoor` → **Powder & Slug** (which already owns blast doors), T1 at its
shipped 700. `TurretPack` → **Powder & Slug**, T1 at 1,400 — a thrown turret is
the most Jawa item in the DLC.

**Route.** Move the rows out of the cut list into the tab assignment. This is
the cheapest recovery in the document and the one with no argument against it.

## 4. Bioferrite-and-shard utility structures — RECOVER (5 rows)

`AtmosphericHeater` · `SleepSuppressor` · `FrenzyInducer` · `ProximityDetector`
· `DisruptorFlares`

**What the gameplay is.** Five colony-utility devices with real, distinct
effects and a shared ingredient bill:

| row | cost to build | what it does |
|---|---|---|
| `ProximityDetector` | Components 1 + Bioferrite 15 | perimeter alarm, sees the invisible |
| `DisruptorFlares` | Components 1 + Bioferrite 30 | belt pack, stuns what a bullet does not |
| `FrenzyInducer` | **Shard 1** + Bioferrite 100 | work-speed field, guaranteed mental breaks |
| `SleepSuppressor` | **Shard 1** + Bioferrite 100 + Steel 25 | removes the need for sleep in radius, at a mood cost |
| `AtmosphericHeater` | **Shard 2** + Bioferrite 150 + Steel 150 + Comp. 8 | raises outdoor temperature map-wide |

**[VERIFIED — all five costLists; `Shard` has no `recipeMaker` and no vendor
route, i.e. it is itself an entity/event drop]**

**The draft.** *Shard-work* — the clan's name for a device built around a
scavenged fragment nobody understands. This is precisely the campaign's
existing "salvaged archotech" register and needs no invention:

- `ProximityDetector` → **Scavenger**, T1 — a perimeter of listening stakes.
- `DisruptorFlares` → **The Strange Schools**, T2 — a stun flare, adjacent to
  the ion/EMP branch it already resembles.
- `SleepSuppressor` and `FrenzyInducer` → **The Reach**, T3 — the trap tab is
  exactly right: both are pure "work your people to death" temptations with a
  mood price already priced in. No reflavor needed at all; they read as Ozzik.
- `AtmosphericHeater` → **DEAD on this planet as shipped, RECOVER inverted.**
  Ash'karr is a desert; a map-wide *heater* is a liability. The gameplay worth
  keeping is *map-wide climate machine*, and the campaign wants the sign
  flipped. **[HYPOTHESIS — a cooler-variant `RUT_` def reusing
  `CompProperties_TempControl`-style behaviour has NOT been checked against the
  building's C# class, which may hardcode the heating direction.]**

**Route.** The first four are reflavor-in-place; only the heater needs a new
`RUT_` def. All five are **gated on cluster 1** for bioferrite, and the three
Shard-costed ones additionally need a Shard source, which only entity content
provides. If `ANOMALY_EXCEPTION_ACCESS_1` lands on option (c), this cluster
drops to the two cheap ones with a costList patch.

## 5. The serum bench — injectable combat chem — RECOVER (4 rows)

`SerumSynthesis` · `MetalbloodSerum` · `MindNumbSerum` · `JuggernautSerum`

**What the gameplay is.** A drug bench that makes **short-duration combat
buffs** — damage resistance, break immunity, a strength burst — as consumables
rather than permanent implants. The campaign's drug economy (The Refinery) has
nothing in this slot; every current buff is worn or installed.

- `SerumCentrifuge`: Shard 1 + Components 2 + Bioferrite 80 + Steel 100.
- `MetalbloodSerum`: **Meat_Twisted 10** + Bioferrite 20 → damage resistance,
  fire vulnerability.
- `JuggernautSerum`: **Meat_Twisted 20** + Bioferrite 10 → strength/speed.
- `MindNumbSerum`: **Neutroamine 2** + Bioferrite 30 → suppresses breaks.
  *This one needs no monster meat at all.*
**[VERIFIED — four costLists; `Meat_Twisted` has no recipe and no vendor route]**

**The draft.** *Gland-draughts.* The clan renders the beast in the pit and
distils what comes out: a rust-coloured draught that hardens you, a black one
that makes you not care. Into **The Refinery**, T2 (`SerumSynthesis` +
`MindNumbSerum`) and T3 (the two meat-fed serums), sitting beside the existing
drug chain. The register is already right — a scavenger clan drinking what it
scraped out of a monster is not weird, it is the setting.

**Route.** Reflavor in place. `MindNumbSerum` survives on bioferrite +
neutroamine alone. For the other two, **[HYPOTHESIS]** a costList patch
swapping `Meat_Twisted` for ordinary `Meat_Raw` would free the whole bench from
entity content at the price of the flavour — worth putting to the owner as a
choice rather than deciding here.

## 6. The psychic ritual chain — DEAD (15 rows)

`BasicPsychicRituals` · `AdvancedPsychicRituals` · `SummonAnimals` ·
`SummonShamblers` · `SummonFleshbeastsPlayer` · `SummonPitGate` ·
`SkipAbductionPlayer` · `Chronophagy` · `Psychophagy` · `Philophagy` ·
`DeathRefusal` · `PleasurePulse` · `NeurosisPulse` · `BloodRain` · `Brainwipe`

**Dead, and the reason is structural rather than tonal.** These fifteen rows
unlock `PsychicRitualDef`s that run on a `PsychicRitualSpot` and are paid for
in entity-derived invocation costs; the mechanic is the monolith, the void, and
stealing years or skills out of a bound prisoner. There is no version of
"psychophagy" that is not the weirdness.

**One pointer, not a recovery.** The campaign already has the *good* half of
this idea in a Jawa register and a different mechanism: the **The Rites** tree
(twelve_trees_proposal §5) builds ritual power on vanilla Ideology
`RitualOutcomeComp`s, XML-only, with no void anywhere. If the owner ever wants
"call the beasts to us" — the one genuinely attractive verb in this list
(`SummonAnimals`) on a desert world — it belongs there as a beast-calling rite,
authored fresh. **Do not resurrect these rows to get it.**

## 7. The ghoul chain — DEAD (4 rows)

`GhoulInfusion` · `GhoulEnhancements` · `GhoulResurrection` · `BlissLobotomy`

**What it carried:** a disposable melee super-soldier made by destroying a
prisoner's mind, upgradeable with bioferrite prosthetics and resurrectable
after death. **[VERIFIED — `GhoulPlating`, `AdrenalHeart` and `MetalbloodHeart`
all carry `techHediffsTags: Ghoul` and state they can only be installed on a
ghoul; `GhoulResurrectionSerum` needs a ghoul corpse.]**

**Dead because the clan already has this unit and it is a droid.** An
expendable melee body that fights without fear and gets rebuilt after it dies
is the entire promise of **Droidsmith** and **The Waking Mind** — two trees, 56
rows, already in the roster. Recovering ghouls would duplicate that gameplay in
a register (lobotomising people) the owner named as out. The four rows die and
nothing is lost.

## 8. Entity-derived exotica — DEAD (5 rows)

`DeadlifeDust` · `RevenantInvisibility` · `InsanityWeaponry` ·
`MutationWeaponry` · `VoidSculptures`

Five one-off items, each dead for its own one line:

- `DeadlifeDust` — a shell that animates corpses into shamblers. The mechanic
  *is* necromancy; there is no reflavor that keeps the verb.
- `RevenantInvisibility` — a personal cloak, and genuinely good gameplay — but
  `RevenantVertebrae` costs `RevenantSpine 1` + `Shard 2`, an entity-only drop
  chain **[VERIFIED]**, and the campaign already carries a cloak school in
  **The Strange Schools**. Covered elsewhere; the row adds nothing.
- `InsanityWeaponry` / `MutationWeaponry` — psychic lances and pulsers.
  Single-use mind weapons; the payload is the weirdness. (The one attractive
  verb, stampeding a herd at the enemy, exists in vanilla outside this row.)
- `VoidSculptures` — a Bioferrite-50 art piece that boosts *psychic ritual*
  quality and meditation focus **[VERIFIED]**. Its only mechanical customer is
  cluster 6, which is dead. Beast-metal sculpture as *art* survives free: the
  material is a stuff, and any `TableSculpting` recipe can use it once
  cluster 1 lands.

---

# B. The Royalty bucket — 19 rows

**The canon ruling is `royalty.dead_ruled`, and the sitting's default is
"Royalty unlocks loot-only."** That default is right for the court and wrong
for the workshop: eleven of these nineteen rows are ordinary industrial
prosthetics hanging off `MicroelectronicsBasics` and `Bionics`, and three more
are pieces of kit with no imperial mechanic in them at all. **No row in this
bucket requires a royal title, a favour, or a permit — checked on the defs and
on the prereq graph. [VERIFIED]** What was ruled dead is the *Empire*, not the
plasteel.

## 9. Cataphract armor — RECOVER (1 row)

`CataphractArmor` (6,000; prereqs `ReconArmor`, `PoweredArmor`, `AdvancedFabrication`)

`Apparel_ArmorCataphract`: Sharp 1.2 / Blunt 0.5 / Heat 0.6, MoveSpeed −0.5,
Cold insulation 70, 75,000 work, ComponentSpacer 6 + Plasteel 150 + Uranium 50
at the `FabricationBench`, Crafting 8. No title, no permit. **[VERIFIED]**

**The draft.** *The heavy shell.* Into **The Shell**, T4 at its shipped 6,000 —
the top of the armor ladder the tree already climbs, and mechanically the only
thing in the campaign above power armor. Reflavor the description off "imperial
cataphracts" onto salvaged siege plate; the mod stack's variants
(`BMT_Apparel_ArmorChitinphract`, the phoenix/prestige skins) come with it and
need a keep/cut pass of their own at manifest draft.

**Route.** Reflavor in place, no new def. This is the single strongest
individual recovery in the 84.

## 10. The two cheap force multipliers — RECOVER (2 rows)

`JumpPack` (2,000; prereq `TransportPod`) · `Gunlink` (2,000; prereq `Fabrication`)

- `Apparel_PackJump`: **techLevel Industrial**, Plasteel 30 + Components 3 +
  **Chemfuel 100**, made at `TableMachining`, `JumpRange` 23.9, reloadable with
  **Chemfuel** — 5 charges, 20 chemfuel each. **[VERIFIED]**
- `Apparel_Gunlink`: ComponentSpacer 1 + Plasteel 10, **+3
  `ShootingAccuracyPawn`**, zero armor, 1 kg. **[VERIFIED]**

**The draft.** The jump pack is the most on-register item in the entire Royalty
DLC for this campaign: an **industrial-tech chemfuel rocket harness** that lets
a small pawn cross a dune or a wall. The clan already refines chemfuel. Into
**The Workshop**, T2 at 2,000, hanging off the existing fuel chain rather than
`TransportPod`. Call it a *dune-hop rig*.

The gunlink is a **targeting monocle**: a cheap head-slot optic that buys
accuracy and nothing else. Into **Powder & Slug**, T2 at 2,000, as the marksman
branch's first real upgrade. Reflavor to a scavenged targeting lens.

**Route.** Both reflavor-in-place. The jump pack's prereq wants re-pointing off
`TransportPod` onto the chemfuel chain at manifest draft.

## 11. The specialist implant chain — RECOVER (11 rows)

`BrainWiring` · `SpecializedLimbs` · `CompactWeaponry` · `VenomSynthesis` ·
`ArtificialMetabolism` · `NeuralComputation` · `SkinHardening` ·
`HealingFactors` · `FleshShaping` · `MolecularAnalysis` · `CircadianInfluence`

**All eleven cost 2,000 and all eleven descend from `MicroelectronicsBasics` or
`Bionics` — core vanilla, not Royalty. [VERIFIED — prereq graph]** They unlock
about thirty implants: drill arms and field hands (work speed), power claws and
elbow blades (melee), venom fangs, stoneskin and armorskin glands, coagulators
and healing enhancers, nuclear and detoxifier stomachs, learning assistants and
neurocalculators, circadian half-cyclers, joywires and painstoppers. Spot-check:
`PowerClaw` is Steel 40 + ComponentIndustrial 8, **techLevel Industrial**, no
title requirement, `techHediffsTags: Advanced`. **[VERIFIED]**

**What the gameplay is.** This is the *mid* rung of the body ladder — the space
between a peg leg and an archotech arm — and the campaign currently has a hole
there. **The Reach** is 16 rows and jumps almost straight to archotech. These
eleven fill it, and they fill it with exactly the right flavour: parts bolted
onto people by a clan that bolts parts onto everything.

**The draft.** *Grafts.* Fold eleven flat 2,000-cost rows into a **four-row
ladder inside The Reach**, since the flat pricing is a wall rather than a
ladder (the same defect §6.9 of the proposal names for Droid Depot):

| new tier | rows folded in | cost | reads as |
|---|---|---|---|
| T1 | `BrainWiring`, `CircadianInfluence` | 1,400 | wire-work: sleep, pain, mood |
| T2 | `SpecializedLimbs`, `CompactWeaponry` | 2,200 | hands that dig and hands that cut |
| T2 | `FleshShaping`, `MolecularAnalysis`, `ArtificialMetabolism` | 2,600 | guts: eat anything, survive anything |
| T3 | `SkinHardening`, `HealingFactors`, `NeuralComputation`, `VenomSynthesis` | 3,400 | the good stuff: skin, blood, mind, venom |

**Route.** Merge, not cut — and merges re-point the loser's unlocks onto the
survivor **before** the loser dies (taxonomy §5.4). Four survivors, seven
merged away, thirty-odd implants preserved. Reflavor the descriptions off
imperial surgeons onto clan bone-setters. Zero new defs.
**[HYPOTHESIS — the merge targets above are a design proposal; which of the
eleven defNames survives as the carrier should be decided at manifest draft,
since some mods' C# may check specific research keys.]**

## 12. The instrument chain → The Rites — RECOVER (3 rows)

`Harp` (500) · `Harpsichord` (500) · `Piano` (2,000)

**This is the cluster the owner is least likely to expect and the mechanism is
real.** `RitualOutcomeComp_NumPlayedDrums` counts *any*
`Building_MusicalInstrument` being played in the ritual room — not drums
specifically — and `RitualBehaviorWorker_PartyDanceDrums` and
`CompRitualEffect_Drum` do the same test. **[VERIFIED — RimWorld source, three
files]** `Harp` is `thingClass Building_MusicalInstrument`, `joyKind
HighCulture`, `instrumentRange 12`, WoodLog 150, buildable at a crafting spot
or smithy. **[VERIFIED]**

So the Royalty instrument chain is **already the mechanism The Rites needs**.
The proposal's §5 T2 row — *God-Speaker Array: "speaker masts + vox/drum
stations; big-congregation quality"* — is describing this chain without knowing
it exists.

**The draft.** Reflavor all three into clan instruments and hang them under
**The Rites**: a **hull-drum** (T0, beaten sheet from a wreck), a **wire-harp**
(T1, tensioned salvage cable), and a **vox-organ** (T2, a scavenged pipe bank).
Each is a `Building_MusicalInstrument`, so each measurably raises ritual outcome
quality *and* gives HighCulture joy, with no new C# and no new comps.

**Route.** Reflavor label/description/texture and re-cost to 400 / 1,200 /
2,600 to sit on the Rites ladder. **One real problem: `Harp` costs WoodLog 150
and Ash'karr is a desert** — patch the costList to steel or salvage.
**[HYPOTHESIS — the costList patch is standard, but the re-textures are
art work that has not been scoped.]**

## 13. Court finery — LOOT-ONLY (2 rows)

`NobleApparel` (400) · `RoyalApparel` (400)

Berets, corsets, ruffled shirts, top hats, coronets, crowns and royal robes.
The gameplay these carry is *high-value trade goods and a mood/impressiveness
bump from wearing something fine* — and neither needs a research row. The
canon default is exactly right here: **the items stay in the world as loot and
as trade stock**, they turn up in caravan inventories and on dead nobles, and a
Jawa who finds a crown sells it. Nothing to recover; nothing to mourn.

---

# C. Dungeon Pack — 10 rows

## 14. Dungeon Pack's ten places — DEAD (10 rows)

`DP_RGiveThrumboValley` · `DP_RGivePirateBay` · `DP_RGiveArea52` ·
`DP_RGiveMaze` · `DP_RGiveSunCult` · `DP_RGiveArea50` · `DP_RGiveNinja` ·
`DP_RGivePrivate` · `DP_RGiveExcavation` · `DP_RGiveGrandWalls`

Ten rows costing 500–10,000, **all with zero unlocks**; each one's entire
function is to place a dungeon on the world map. They are dead on the principle
the campaign has already ruled from the other side (twelve_trees_proposal §4):

> **Research must never unlock a place. Places unlock RESEARCH** — the Memory
> Core reveal, a vault's schematics, a hulk's salvaged prototype. That is
> research-as-revelation, and it is already canon.

Nothing here recovers, and the *content* — the dungeons themselves — is not
what was cut. If the owner wants Area 52 on Ash'karr it is a worldmap and quest
question, authored where landmarks are authored, and it can then hand the clan
a research reveal on arrival. The rows die; the ninja temple need not.

---

# D. Big & Small — 5 rows

## 15. Gene tools and animal size serums — RECOVER, as a pointer (3 rows)

`BS_GeneScience` (250) · `BS_ArchiteGeneScience` (250) · `BS_AnimalGrowthSerums` (250)

The first two unlock xenogerm-creation tooling (`BS_CreateXenogerm`,
`BS_GeneGeneIntegrator`, `BS_GeneDicombobulator`, the archite variants); the
third unlocks `BS_Giant_Serum` and `BS_Shrink_Serum`, which change an animal's
size.

**This is the same gameplay the v2 proposal already gave a recover line to** —
the six cut VGE `GR_*` genetics rows, whose line reads: *"the creature-crafting
gameplay could return v2 as an Oomo-sanctioned beast-breeding rite — hatchery,
not laboratory."* These three rows attach to that line rather than getting
their own; the lab register is out, the *breeding* is the recovery.

**The draft.** If the beast-breeding rite is ever authored, `BS_AnimalGrowthSerums`
is its most useful single input — a draught that grows a pack beast is a
hatchery verb, not a laboratory one, and it needs no gene mechanics at all.
The two xenogerm rows come only if the rite turns out to need real gene
plumbing underneath. **[HYPOTHESIS — the beast-breeding rite is unauthored;
nothing here is scoped or costed.]**

**Route.** Deferred to the v2 rite. No row returns now.

## 16. Mad science field testing — DEAD (1 row)

`BS_MadScienceField` (500) — unlocks `BMad_GrowthRay`, `BMad_ShrinkRay` and
their turret versions. A shrink ray is a comedy register on a Star Wars desert
world, and the gameplay underneath (an enemy debuff at range) is served by the
ion/EMP and sonic branches of **The Strange Schools** without the joke. Dead.

## 17. Android conversion — DEAD (1 row)

`BS_AndroidConversion` (1,337; prereq `Bionics`) — **zero unlocks measured**,
and turning a colonist into an android is the exact ground **The Waking Mind**
owns as the campaign's Ohm/Oomo flashpoint, authored deliberately. A second,
mod-native route to the same idea would undercut it. Dead. (The cost, 1,337, is
the author's joke and is itself a tell.)

---

# E. The eight measured-dead rows

## 18. Measured dead — DEAD (8 rows)

`VAE_SterileAttire` · `VWE_MakeshiftWeapons` · `VFEP_SweatFermentation` ·
`WallStuff` · `MatterToEnergyConversion` · `guy762_ResearchKotOR_revan` ·
`guy762_ResearchKotOR_exile` · `MM_Research_Repulsor`

These are genuinely dead and were measured so in `research_tree_prep.md` §1.
Three sub-reasons, and one caveat worth stating:

- **Author-flagged dead (4).** `WallStuff` and `MatterToEnergyConversion` both
  carry the description *"No Longer needed, just left for now so it doesn't
  cause errors."* The two KotOR hero rows are priced 100,000,000 and marked
  unobtainable by their author.
- **Zero unlocks, mod-wide (1).** `MM_Research_Repulsor` — the whole mod tree
  was grepped; nothing anywhere names it as a prerequisite.
- **All unlocks already cut (3).** `VAE_SterileAttire` (3 items),
  `VWE_MakeshiftWeapons` (6 guns), `VFEP_SweatFermentation` (1 rumsuit) — their
  items were removed by Cherry Picker in an earlier curation pass, so the rows
  now unlock nothing.

⚠️ **The caveat.** That last three are dead *because of a separate ruling*, not
on their own merits — makeshift guns and lab clothing are perfectly ordinary
gameplay. If the owner ever restores those items, the rows come back with them
automatically. They are not recoveries; they are dependents.

---

# Out of scope, asked for anyway — Deathrest

`Deathrest` is one of the v2 proposal's **own 30 cuts**, not one of these 84, so
it is absent from the roster below and from every count in this document. It
already carries a recover line — *"v2 'long-sleep cradle' ship structure if the
dormancy gameplay is ever wanted."* The owner asked whether that gameplay can
survive as something Jawa. **The honest answer is: not by reflavor, and the
existing recover line is optimistic.**

The gameplay is genuinely attractive — a pawn sleeps for days in a chamber and
wakes with real, lasting bonuses, scaled by how many accessory buildings you
built and bound to that chamber. It is a *build-an-installation-and-invest*
loop, which is very much this campaign's idiom.

But the whole mechanic lives on the gene. `Gene_Deathrest` owns
`deathrestCapacity`, `boundBuildings`, `BindTo`, `ApplyDeathrestBuildingBonuses`
and `DeathrestEfficiency`; the buildings are inert `CompDeathrestBindable`
facilities that a `Gene_Deathrest` reaches out and binds. **[VERIFIED —
`RimWorld/Gene_Deathrest.cs`, and `GeneDefs_Sanguophage.xml:174`]** No gene, no
capacity, no binding, no bonuses. So:

- **Reflavoring the buildings recovers nothing** — a "long-sleep cradle" with no
  gene to bind it is furniture.
- **Recovering it for real means giving Jawa (or one clan role) the `Deathrest`
  gene**, which is a xenotype decision with campaign-wide consequences —
  sunlight sensitivity is a separate gene, but deathrest exhaustion and the
  multi-day coma are not optional once the gene is on a pawn.
- **A third route** would be a new `RUT_` sleep-chamber with its own small C#
  granting a temporary hediff on a long stay — the *feel* of the loop with none
  of the gene. That is new-mechanism work, not recovery.

Recommendation: leave the cut, and **amend the v2 recover line to say "needs the
Deathrest gene or new C# — not a reflavor"**, so nobody later reads it as cheap.

# What this pass could not settle

1. **`BX_BloodletterBlade`** appears in `BioferriteExtraction`'s unlock cache in
   `restructured_model_v2.json`, but **RimSage has no def under that name** and
   no source hit. Either a mod def outside RimSage's index or a stale cache
   entry. It changes nothing in cluster 1's verdict; flagged so nobody treats
   the unlock list as measured.
2. **The `AtmosphericHeater` inversion** (cluster 4) assumes a cooler variant
   can reuse the building's behaviour. Its C# class was not read; the heating
   direction may be hardcoded.
3. **The implant merge carriers** (cluster 11) are a design proposal. Some mods'
   C# checks specific research defNames; which of the eleven survives as the
   carrier must be checked before the merge, not after.
4. **Every Anomaly recovery is downstream of `ANOMALY_EXCEPTION_ACCESS_1`.**
   Clusters 1, 2, 4 and 5 — 16 of the 18 recovered Anomaly rows — need
   bioferrite, and three devices additionally need `Shard`, which has no craft
   and no vendor route. Only cluster 3 (2 rows) stands with the exception
   dropped. If the owner takes option (c) there, this document's Anomaly
   recovery shrinks from 18 rows to 2 plus whatever survives a costList patch.

---

# Appendix — the authoritative row→cluster roster

This block is the coverage contract, machine-checked by
`check_recovery_coverage.py`: every one of the 84 defNames appears exactly once
here, and the per-cluster counts match the Index table above. (defNames also
appear in the prose, and several collide with ThingDef names of the same
string — the prose is not the roster; this is.)

```roster
1  RECOVER    BioferriteExtraction BioferriteHarvesting BioferriteShaping BioferriteGenerator EntityContainment Electroharvester
2  RECOVER    BioferriteIgnition
3  RECOVER    SecurityDoor TurretPack
4  RECOVER    AtmosphericHeater SleepSuppressor FrenzyInducer ProximityDetector DisruptorFlares
5  RECOVER    SerumSynthesis MetalbloodSerum MindNumbSerum JuggernautSerum
6  DEAD       BasicPsychicRituals AdvancedPsychicRituals SummonAnimals SummonShamblers SummonFleshbeastsPlayer SummonPitGate SkipAbductionPlayer Chronophagy Psychophagy Philophagy DeathRefusal PleasurePulse NeurosisPulse BloodRain Brainwipe
7  DEAD       GhoulInfusion GhoulEnhancements GhoulResurrection BlissLobotomy
8  DEAD       DeadlifeDust RevenantInvisibility InsanityWeaponry MutationWeaponry VoidSculptures
9  RECOVER    CataphractArmor
10 RECOVER    JumpPack Gunlink
11 RECOVER    BrainWiring SpecializedLimbs CompactWeaponry VenomSynthesis ArtificialMetabolism NeuralComputation SkinHardening HealingFactors FleshShaping MolecularAnalysis CircadianInfluence
12 RECOVER    Harp Harpsichord Piano
13 LOOT-ONLY  NobleApparel RoyalApparel
14 DEAD       DP_RGiveThrumboValley DP_RGivePirateBay DP_RGiveArea52 DP_RGiveMaze DP_RGiveSunCult DP_RGiveArea50 DP_RGiveNinja DP_RGivePrivate DP_RGiveExcavation DP_RGiveGrandWalls
15 RECOVER    BS_GeneScience BS_ArchiteGeneScience BS_AnimalGrowthSerums
16 DEAD       BS_MadScienceField
17 DEAD       BS_AndroidConversion
18 DEAD       VAE_SterileAttire VWE_MakeshiftWeapons VFEP_SweatFermentation WallStuff MatterToEnergyConversion guy762_ResearchKotOR_revan guy762_ResearchKotOR_exile MM_Research_Repulsor
```
