# Species traits over aptitudes — design draft (2026-10-09)

Item: `SPECIES_TRAITS_OVER_APTITUDES_1` · **DESIGN DRAFT for owner review. Nothing built, no def changed.**
Written by a BENCH design helper overnight; every engine claim below was checked against the
decompiled 1.6 source (RimSage) tonight unless marked otherwise.

## 1. The ask, and what is already ruled

Your words (2026-09-20): *"we should consider deeply making better traits that might do a better job
of capturing these fine points and nuances than pluses to skills."*

Already ruled, so this draft does not reopen it:

- **A species unit REPLACES the aptitude it was a surrogate for** — never both. Aptitudes that are
  genuinely about skill stay.
- **Reach decides the unit:** true of ALL members → a **gene**; true of most/many → a **trait**.
- **Gungan keeps `poor intellectual`** ("half joke and half rebuke").
- **Appearance is gated** — Bothan fur as a *mechanic* is in scope; fur as a *render* is not.
- **New tonight (UNSUBSTANTIATED_SPECIES_ABILITIES_1, R5):** you kept the Echani melee package as
  *"game stand-in for culture"*. That is a gene carrying culture. It sits in mild tension with the
  reach test (culture is rarely universal), so it is put back to you as a card question (§6 Q4) rather
  than assumed either way.

## 2. What we already ship (survey)

**The scale, MEASURED tonight** from the generated
`D:\Luke\dev\RimMandrake\src\RimStarWars\StarWarsRaces\Defs\XenotypeDefs\RimMandrakeXenotypes.xml`:
**69 xenotypes, 47 carry aptitude genes, 137 aptitude genes in all.** (That file is generator
output from `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\gen_races_mod.py`; tonight's R1–R11
removals are queued there and may not be in this count yet.)

Reusable pieces, by where they live:

| piece | where | why it matters here |
|---|---|---|
| `RSW_statgene_*` (8: psyharmonize, amphibious, compliant, force, fourthroats, metabolismcheat, predator, senses), `RSW_lifespan_*`, `RSW_WaterBreathing`, `RSW_SandVoiceGene` | `src\RimStarWars\StarWarsRaces\Defs\GeneDefs\SW_Genes.xml`, `RSW_Aquatic.xml` | we already author species-specific behaviour genes in XML; the pattern exists |
| `RSW_Jawa_Skittish` | `...\GeneDefs\Jawa_Skittish.xml` | precedent for **reshaping a blunt donor gene into the species truth** (kept terror ×1.5, dropped fainting, repriced metabolism +2→+1) |
| `RM_Submissive`, `RM_Amorous` TraitDefs | `...\Defs\TraitDefs\RM_TwilekTropeTraits.xml` | precedent for the **reach test run in reverse**: a Twi'lek trope moved from a species gene to an individually-rolled trait |
| `Gene_ForcesHediff` + `RM_ForcedConditionExtension` | `src\RimMandrake\GelatinousSlime\Source\GeneConditions.cs` | a generic "gene puts a permanent hediff on the pawn" class, chosen in XML. A hediff can carry stages, capMods and comps — so it is a carrier for anything a gene field cannot reach |
| `RM_HediffComp_ShadeDrivenSeverity`, `RM_HediffComp_EnvironmentalExposure` | `src\RimMandrake\CreatureBehaviors\Source\`, `src\RimMandrake\EnvironmentalHazards\Source\` | working examples of **severity driven by the pawn's situation** |
| `ThoughtWorker_IkeeNearby` + `IkeeToleranceExtension` | `src\RimStarWars\SWBestiary\Source\JawaIkee\` | a working **"something nearby changes my mood, and which xenotypes react is a list in XML"** thought — the closest existing shape to a hive-kin thought |
| `Need_Power`, `RSW_Need_ToxinDependence` | `src\RimStarWars\Droidworks\Source\`, `src\RimStarWars\SWBestiary\Source\BeastMechanics\` | we already ship custom Needs |
| 12 custom `StatPart`s | across `src\` | situational stat modifiers are familiar ground |
| RUT precepts (HolyFlame, TheReturn, FungusEating, NineFaults, JoiningWater) | `src\RimUtinni\...` | we already author Ideology content |

⚠️ **`StarWarsRaces` has no C# assembly of its own.** Its only code is borrowed from donor frameworks
(VEF, BigAndSmall, BetterPrerequisites, TabulaRasa). Any approach needing new C# needs either a new
small assembly for that mod or hosting in an existing RSW assembly. A new assembly would also give the
mod a Mod Settings screen, which it currently cannot have (`MOD_OPTIONS_RETROFIT_1`).

## 3. Engine machinery available (RimSage-checked 2026-10-09)

| mechanism | what it gives | cost |
|---|---|---|
| `GeneDef.conditionalStatAffecters` | a gene's stat bonus/penalty that applies **only while a condition holds**. `StatWorker` does read it from genes (and from precepts). Base class is tiny: `statFactors`, `statOffsets`, `Label`, `Applies(StatRequest)` | vanilla ships only 6 conditions (InSunlight, Clothed, Unclothed, Child, InSpace, NotInSpace). A new condition is **one small C# class, no Harmony** |
| `GeneDef.forcedTraits` / `suppressedTraits` | a gene can **force a trait** onto every bearer, or block one | XML only |
| `GeneDef.enablesNeeds` / `disablesNeeds` | a gene can **add a Need** to the needs tab | XML for the hook; the Need itself is C# |
| `ThoughtDef.requiredGenes` / `nullifyingGenes` | a mood thought only bearers of a gene feel (or are immune to) | XML only, if a vanilla ThoughtWorker fits; otherwise one ThoughtWorker class |
| `Precept_Xenotype`, `ThoughtWorker_Precept_PreferredXenotype_Social`, `ThoughtWorker_Precept_ColonyXenotypeMakeup` | Ideology already knows about xenotype preference and colony make-up | XML |
| Royalty / Anomaly | nothing here that fits better than the above. Psylink is already how our psychic genes work. | — (said so rather than forced in) |

**UNMEASURED:** whether a trait can be rolled at a per-species *chance* ("most but not all") without
C#. `GeneDef.forcedTraits` gives it to all bearers; backstories can force traits. A chance-per-species
roll was not verified tonight — treat it as possibly needing a small generation hook.

## 4. The candidate list — the item says this list IS the decision

Species whose truth does not fit a skill axis, with the aptitude that looks like its surrogate.
Confidence is mine, from the canon library (`D:\Luke\dev\RimMandrake\design\RimStarWars\canon_references\`);
**you rule the list, not me.**

| species | the truth no number holds | current surrogate aptitude(s) | reach → unit | confidence |
|---|---|---|---|---|
| **Geonosian** | caste hive under a queen; "Geonosian hive-mind" is its listed language/distinction | `Terrible_Social` (insular hive-mind). Construction/Crafting Remarkable look like real skill (droid foundries) — keep | all → gene | high (your own case) |
| **Bothan** | mood-sensitive fur (Wrendui) that *"betrayed them when … duplicitous"* — Legends, your source | `Strong_Social` partly (spies/politicians) | all → gene | high (your own case) |
| **Abednedo** | underground-dwelling ancestry; sourced linguists | `Strong_Construction` (already softened per your ruling) | culture/history → trait, or nothing | medium — your softened aptitude may already be enough |
| **Cerean** | binary brain | `Strong_Intellectual` | all → gene | medium |
| **Zeltron**, **Falleen** | pheromones that work on others | `Strong_Social` | all → gene | medium |
| **Echani** | combat as communication; matriarchal caste culture | melee package (kept tonight as culture) | culture → your call (Q4) | depends on Q4 |
| **Jawa** | clan-trader scavengers | `Strong_Social` (haggling) | culture → trait | low — may be genuine skill |
| Gungan | — | `Poor_Intellectual` **stays by ruling** | — | excluded |

⇒ **The honest size is 3 certain + 3–5 possible.** That is a small build, not a programme — if the
list holds.

## 5. Approaches — each answers a different question

### A. Situational genes — *"when and where is this species different?"*
A gene's bonus or penalty that switches on with circumstance, via a few new
`ConditionalStatAffecter` conditions: **NearKin** (N others of my xenotype within R cells), **MoodBand**
(my mood above/below a threshold), **UnderRoofOrRock** (overhead mountain).

- **Geonosian** — "Hive-minded": work speed and research speed up while 2+ Geonosians are near, down
  when alone. Replaces `Terrible_Social`. The inspect panel shows *"Hive-minded (near kin)"* on the stat.
- **Bothan** — "Wrendui fur": negotiation and trade price improve while content, worsen while
  stressed (the fur gives a nervous Bothan away). Replaces part of `Strong_Social`.
- **Abednedo** — "Tunnel-born": small mining/construction speed bonus under overhead rock — the "light
  nod" — and the flat `Strong_Construction` goes.
- **Cerean** — "Binary brain": research speed + a small consciousness-linked bonus; `Strong_Intellectual` goes.

*Machinery:* 3–4 condition classes (~150 lines total) + XML genes; regenerate via `gen_races_mod.py`.
*Build cost:* small — one assembly, one evening plus a quicktest.
*Risks:* NearKin scans the map on every stat request — must cache per pawn (~every 250 ticks) or it
costs frame time. Needs a home assembly (§2 ⚠️).
*Balance:* each swap must be priced against the aptitude it removes, and the xenotype's metabolism
total repriced (the Skittish precedent). A lone Geonosian should be weaker, not crippled.

### B. Needs and feelings — *"what does this species need, and how does it feel?"*
Species character as mood: a gene adds a Need or gene-gated thoughts.

- **Geonosian** — a "Hive" need that fills near kin and drains alone; empty → a mood penalty and a
  `Gene_ForcesHediff`-carried "cut off from the hive" hediff (consciousness cap). Strongest expression
  of *"need to group think"*.
- **Bothan** — a social opinion thought on *others*: "I can read X's fur" — slight trust when the
  Bothan is calm, distrust when stressed.
- **Abednedo** — a mood thought "comfortable underground" (`ThoughtDef.requiredGenes`, XML only).
- **Zeltron/Falleen** — opinion thought on others near them (pheromones), stronger at close range.

*Machinery:* one Need class, 2–3 ThoughtWorkers (the Ikee thought is the template), XML genes.
*Build cost:* medium — a Need needs UI, save-safety and tuning.
*Risks:* mood is RimWorld's strongest lever; a Hive need makes a 1-Geonosian colony a misery engine and
can cascade into breaks. Needs are always on screen — noticeable, which is the point, and also noise.
*Balance:* hard to price in metabolism (vanilla prices needs inconsistently); the most playtesting.

### C. Culture, not genome — *"is this belief and upbringing rather than biology?"*
Species culture carried by an ideoligion and traits, per the reach test's "most but not all" branch.

- **Geonosian** — a faction ideoligion meme/precept "Hive conformity": approves obedience to the
  leader role, dislikes individualism. Uses existing Ideology roles for the queen.
- **Abednedo** — a trait "Linguist" (social learning, negotiation) rolled on most Abednedo.
- **Echani** — melee moves from genes into an "Echani discipline" precept/trait.
- **Bothan** — the *Spynet* culture as a precept; ⚠️ **the fur cannot be expressed here** — it is biology.

*Machinery:* mostly XML; a per-species trait chance may need a small hook (UNMEASURED, §3).
*Build cost:* low–medium.
*Risks:* a converted colonist loses their species culture — which may be right, or may read as the
species vanishing. Precepts bind ideoligion members, not species, so a Bothan in a human ideo has no Spynet.
*Balance:* easiest — precepts and traits are already tuned engine units.

## 6. Recommendation

**A, situational genes** — because it is the only approach that replaces each surrogate aptitude
one-for-one with something the player can see on the stat tooltip, at small cost, without adding a
mood burden. B's XML-only half (`requiredGenes` thoughts) can ride on top for one or two species if
you want them to *feel* it, and C stays the right home for anything you rule is culture.

## 7. Questions for you (card-ready, plain language)

1. **Is the list right?** Geonosian, Bothan and Abednedo for sure; also Cerean (binary brain),
   Zeltron/Falleen (pheromones), Echani, Jawa — which of these should get a species trait at all?
2. **Geonosians apart from their hive:** should they get *better when together*, *worse when alone*,
   or both?
3. **Bothan fur betrays mood — who does it affect?** Their own dealing (trade and negotiation), how
   others feel about them (opinion), or both?
4. **Culture in genes:** you kept the Echani melee as a stand-in for culture. Is that the rule for all
   species (culture may live in genes), or should culture go to traits/ideoligion and genes stay biology?
5. **Cost:** OK to give the Star Wars races mod its own small code library? It is needed for approach
   A or B, and it also gives that mod a settings screen with on/off per species trait.
