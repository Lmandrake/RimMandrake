# DESIGN — what makes a religion interesting

_Expands `SKILL.md` §2. Every number here was counted from the live def dump
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\`
(all mods resolved, captured 2026-08-14, game 1.6.4871 rev591) or from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Ideology\Defs\`.
Vocabulary: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\data\ideology_palette.md`.
Corpus of eleven worked religions:
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`._

**Population, 2026-08-14:** 136 memes (35 structure, 101 normal) · 685 precepts
across 220 issues · 283 `HistoryEventDef`s, 206 of them hooked by at least one
precept.

---

## 1. The design loop

Memes are the only thing XML sets (`SKILL.md` §1). Precepts arrive as a
*consequence*. So the loop runs meme-first and the precept table is written last,
as a prediction you then check.

| # | step | what you actually do | the file you read |
|---|---|---|---|
| 1 | **Structure** | Pick one. It fixes deity count and the worship room noun before you write a word of fiction. | §4 below |
| 2 | **Impact budget** | Pick 2–4 normal memes whose `impact` sums into the band you want. | §2, and `references/authoring.md` for the engine cap |
| 3 | **Read the consequences** | For each meme, read its `requireOne`. Every group forces one precept. Write them down — that is most of your doctrine, already decided. | `MemeDef.json` |
| 4 | **Check reachability** | Any precept you *wanted* that carries `requiredMemes` is unreachable unless step 2 took one of those memes. 163 of 685 precepts are gated this way, by 85 distinct gatekeeper memes. | `PreceptDef.json` |
| 5 | **Friction test** | Score the result by §3. If nothing lands in tier A or B, the religion is decoration — go back to step 2. | §3 below |

🔴 **Step 3 is where designs die.** A meme with seven `requireOne` groups has
already written seven precepts for you; `Transhumanist` forces
`SleepAccelerator_Preferred`, `NeuralSupercharge_Preferred`,
`Biosculpting_Accelerated`, `AgeReversal_Demanded`,
`NutrientPasteEating_DontMind`, `BodyMod_Approved` and
`VQE_ARCGenerators_Exalted`. Listing `BodyMod_Approved` in your spec adds
nothing; it was never optional.

**Measured spread of `requireOne`:** 99 of 136 memes carry one; 314 groups in
total; **251 of them (80%) hold exactly one precept** and are therefore
deterministic. 63 hold 2–4 and are a *dice roll* — see §2.4.

**Impact bands, measured against the 46 shipped `IdeoPresetDef`s** (which is the
only place the game itself declares what "strong" means):

| category | presets | total meme impact | meme count |
|---|---|---|---|
| `Mild` | 9 | 1–4 | 1–3 |
| `Strong` | 23 | 3–7 | 1–5 |
| `Intense` | 14 | 5–10 | 2–5 |

Impact 0 for all 35 structure memes; normal memes are 1–3 (27 at 1, 50 at 2, 24
at 3). **Nothing in the shipped corpus exceeds 10 or 5 memes.** A design asking
for six memes is outside everything Ludeon and the expansion authors shipped.

---

## 2. Which memes change play, and which change a tooltip

### 2.1 How this was classified

Every `MemeDef` was read for two things:

1. **Its own mechanical fields** — the ones that add or remove something the
   player can click. Present-and-non-default counts across all 136 memes:
   `consumableBuildings` 23 · `requiredRituals` 23 · `addDesignators` 12 ·
   `styleItemTags` 16 · `thingStyleCategories` 38 · `preferredWeaponClasses` 5 ·
   `startingResearchProjects` 4 · `requireAnyRitualSeat` 5 ·
   `apparelRequirements` 2 · `preventApparelRequirements` 1 ·
   `addDesignatorGroups` 2 · `veneratedAnimalsCountOffset` 2.
2. **Whether its `requireOne` guarantees a refusal** — a group counts only if
   *every* option in it carries a `PreceptComp_UnwillingToDo` family comp. A
   mixed group is a gamble, not a guarantee, so it does not qualify.

Tiers are exclusive and sum to 136.

### 2.2 Tier 1 — forced refusal (20 memes)

**These are the interesting ones.** Taking the meme guarantees a precept that
makes a colonist *refuse the job*, naming a concrete `HistoryEventDef`.

| meme | impact | forces refusal of | source |
|---|---|---|---|
| `AnimalPersonhood` | 3 | `KilledInnocentAnimal` (hunting) | Ideology |
| `FleshPurity` | 2 | `IngestedDrug` | Ideology |
| `HumanPrimacy` | 2 | `Bonded` (animal bonding) | Ideology |
| `Pacifism` | 3 | `ExecutedPrisoner`, `SoldSlave` | Ideology: More Precepts |
| `Altruism` | 2 | `SoldSlave` | Precepts and Memes (Continued) |
| `AM_NonViolence` | 3 | `SoldSlave`, `ExecutedPrisoner`, `KilledInnocentAnimal` | Alpha Memes |
| `AM_Monastic` | 3 | drug ingestion **and** `SharedBed` | Alpha Memes |
| `AM_VampireHunting` | 2 | `PropagateBloodfeederGene`, `AM_BuildingDeathrestCasket` | Alpha Memes |
| `AM_Iconoclast` | 2 | `AM_BuildingReliquary` | Alpha Memes |
| `AM_Deforestation` | 3 | `AM_PruneGauranlenTree` | Alpha Memes |
| `AM_BiologicalDefilers` | 2 | `Bonded` | Alpha Memes |
| `VME_Pacifist` | 3 | `SoldSlave`, `ExecutedPrisoner` | VME |
| `VME_Emancipation` | 1 | `EnslavedPrisoner`, `SoldSlave` | VME |
| `VME_Egalitarian` | 1 | `SoldSlave` | VME |
| `VFEA_Isolationist` | 3 | `VFEA_RecruitAttempt`, both directions | VME |
| `VQE_Technophobia` | 2 | `BuiltAutomatedTurret`, `Researching` | VQE Generator |
| `HAR_Xenophobia` | 1 | alien romance | Humanoid Alien Races |
| `GR_CarefulGeneticists` | 1 | `BuiltAutomatedTurret` | Vanilla Genetics Expanded |
| `GR_MadScientists` | 1 | `BuiltAutomatedTurret` | Vanilla Genetics Expanded |
| `VVE_Roadragers` | 3 | boarding air and sea vehicles | Vanilla Vehicles Expanded |

⚠️ **`TreeCutting_Prohibited` is not on this list, and `SKILL.md` §2 rule 1 still
names it correctly.** No meme *forces* it — `TreeCutting` has three precepts
(`Prohibited`/`Horrible`/`Disapproved`) and no meme's `requireOne` guarantees the
Prohibited one. It is the best single precept in the game and you get it by
**listing it directly in a `disallowedPrecepts`-shaped design and taking it in the
in-game editor**, not by picking a meme. Same for `Mining_Prohibited`.

### 2.3 Tier 2 — adds a building, designator, or gear rule (33 memes)

Changes what is on the architect menu or what the pawns carry; does **not**
guarantee a refusal.

| what it adds | memes |
|---|---|
| **new buildings on the architect menu** (`addDesignators`) | `Transhumanist` (`SleepAccelerator`, `NeuralSupercharger`, `WallMountableSleepAccelerator`, transhumanist floors) · `PainIsVirtue` (four slab beds) · `HighLife` (`Autobong`, mindbend carpet) · `Tunneler` (`FungalGravel`) · `AM_TeaPrimacy` (`AM_TeaCeremonyTable`) · `AM_WaterPrimacy` (`AM_BaptismalFont`) · `AM_BiologicalReconstructors` (`AM_AnimalDatabase`) · `AM_Iconoclast`¹ (`AM_RelicSmashingAltar`) · `VME_MechanoidSupremacy` (`VME_MechanoidEffigy`) · `AM_Structure_Corsair` · `VME_Structure_ChthonianCult` |
| **free research at game start** | `Tunneler` → `Stonecutting` · `TreeConnection` → `TreeSowing` · `Bloodfeeding` → `Deathrest` · `BMT_CavernDweller` |
| **forces headgear** | `Guilty`, `PainIsVirtue` → `Apparel_TortureCrown` |
| **cancels all apparel demands** | `Nudism` (`preventApparelRequirements: true`) |
| **weapon class** | `Transhumanist` / `VME_MechanoidSupremacy` (noble Ultratech) · `NaturePrimacy` (noble Neolithic) · `AM_Sharpshooter` (LongShots) · `AM_Gladiator` (Melee) |
| **`consumableBuildings` only** — the weakest thing in this tier | `Supremacist`, `Loyalist`, `Collectivist`, `Individualist`, `Raider`, `Rancher`, `Cannibal` (`CannibalPlatter`), `FleshPurity`¹, `VME_Gestalt`, `VME_FireWorship`, `AP_HuntingMeme`, `AM_Epicurean`, `Structure_Ideological`, `Structure_OriginChristian/Hindu/Buddhist` |

¹ also in tier 1; listed here for the building.

🔴 **`consumableBuildings` names only a building a ritual *may consume*.** A meme
whose entire mechanical footprint is `consumableBuildings: [Effigy]` has changed
the game less than one tier-1 precept.

### 2.4 Tier 3 — gates a ritual (16 memes)

`requiredRituals` forces a `Precept_Ritual` (and often its building) into the
ideoligion. `requireAnyRitualSeat` forces a seat type into the worship room.

`Blindsight` (`BlindingCeremony`) · `AM_Madness` · `AM_BiologicalCorruptors`
(`AM_OcularWarping`) · `AM_Cowboys` · `VFEP_PirateMeme` · `VME_ViolentConversion`
· `VME_Astrology` · `VME_Fleshcrafters` · `VME_HolyDiseases` · `VME_Trader` ·
`VME_Bushido` · `VME_BloodCourt` · `VME_InsectoidSupremacy` ·
`VME_Structure_Bacchanalianism` · `Structure_OriginIslamic` (`KneelSheet`) ·
`AM_Structure_Jewish`.

Rituals are **strong for the player and near-invisible on an NPC** — see §5.

### 2.5 Tier 4 — mood and opinion only (67 memes)

**Half the installed vocabulary.** These carry no building, no designator, no
guaranteed refusal. Includes **26 of the 35 structure memes** and, among normals:
`MaleSupremacy`, `FemaleSupremacy`, `Proselytizer`, `Darkness`, `Inhuman`,
`Ritualist`, `Shipborn`, `Nomadism`, `Necrolatry`, `Trader`, `VME_Vegan`,
`VME_Scrapper`, `VME_Nomad`, `VME_Royal`, `AM_Sadist`, `AM_Artist`, `VVE_*`.

⚠️ **Tier 4 is not "does nothing" — it is "does nothing you can point at in the
XML".** `Darkness` forces `Darklight_Preferred` + `DarknessCombat_Preferred` +
`Eclipse_Beautiful`, which reshapes an entire base's lighting. `VME_Vegan` forces
`VME_MeatEating_Abhorrent_Strict`, a permanent mood hit on the single most
frequent action in the game. **The tier tells you where the effect lives, not how
big it is.** Read the forced precepts before dismissing a tier-4 meme.

### 2.6 The `requireOne` gamble

63 of 314 groups hold more than one option, and the generator picks one. `VME_Vegan`
forces the group
`[AnimalSlaughter_Prohibited, AnimalSlaughter_Horrible, AnimalSlaughter_Disapproved]`
— **one of those is a work refusal and two are a mood hit, and you do not choose
which.** `AnimalPersonhood` has the same shape on `KillingInnocentAnimals`.

⇒ **If the design depends on the refusal, the meme is not enough.** Name the
precept in the spec, take it in the editor or via the faction's precept
constraints, and say in the document that the meme alone does not guarantee it.

---

## 3. The friction ranking

**Belief is only visible through friction, and friction is the hooked event
firing.** Rank precepts by how often a normal colony triggers the
`HistoryEventDef` they name. The event names and the comp types below are
measured; the *rate class* is judgement, stated as such.

**Three severities of hook, measured across 685 precepts:**

| hook | precepts | what the player sees |
|---|---|---|
| `PreceptComp_UnwillingToDo` family | **74** (10.8%) | the job is refused; a red "will not do" on the work menu |
| `PreceptComp_SituationalThought` | 345 comps | a **permanent** mood line while the condition holds |
| `SelfTookMemoryThought` / `KnowsMemoryThought` | 234 / 298 comps | a decaying mood hit on the actor, and on everyone who hears |
| no comps and no mechanical field | **135** (19.7%) | **nothing** — see §3.3 |

### 3.1 Tier A — fires several times per pawn per day

| action | event | precepts that hook it |
|---|---|---|
| eating a meal | `AteMeat` / `AteNonMeat` | `MeatEating_Abhorrent/Horrible/Disapproved`, `VME_MeatEating_Abhorrent_Strict`, `MeatEating_NonMeat_Abhorrent/Horrible/Disapproved`, `AP_MeatEating_Honorable` |
| eating human meat | `AteHumanMeat` | `Cannibalism_Abhorrent/Horrible/Disapproved/Preferred/RequiredStrong/RequiredRavenous` |
| eating paste | `AteNutrientPaste` | `NutrientPasteEating_Disgusting` (**the default**), `NutrientPasteEating_DontMind`, `AM_NutrientPasteEating_Preferred/Forbidden` |
| being dressed | continuous situational | the 14 `Nudity_Male_*` / `Nudity_Female_*` precepts |
| being in a role without its kit | continuous situational | `IdeoRoleApparelRequirementNotMet` — reused by **30** role precepts |

**Anything hooking food or clothing is tier A.** Every pawn eats twice a day and
is dressed all day. This is why `Cannibal` and `VME_Vegan` are felt from hour one
and `MarriageName_AlwaysMans` is not.

### 3.2 Tier B — fires many times per colony-day, hardest in the first season

| action | event | the precept that stops it |
|---|---|---|
| cutting a tree | `CutTree` | **`TreeCutting_Prohibited`** (refusal) · `_Horrible` · `_Disapproved` |
| mining | `Mined` | **`Mining_Prohibited`** (refusal; `enabledForNPCFactions: false`) · `_Horrible` · `_Disapproved` |
| slaughtering | `SlaughteredAnimal` | **`AnimalSlaughter_Prohibited`** (refusal) · `_Horrible` · `_Disapproved` · `AM_AnimalSlaughter_Desired` |
| a body on the ground | `ObservedLayingCorpse` / `…Rotting` | `Corpses_Ugly` (**the default**), `Corpses_DontCare`, `AM_Corpses_Sublime`, `VME_Death_Troubling` |
| fishing | `SlaughteredFish` | `Fishing_Prohibited` (refusal) |
| building a trap | `BuiltTrap` | `Traps_Prohibited` (refusal; NPC-disabled) |
| researching at all | `Researching` | `Research_None` (refusal) |

🔴 **`TreeCutting_Prohibited` is the benchmark and it earns it three ways:** a
refusal, plus **two** `KnowsMemoryThought`s (`CutTree_Know_Prohibited` and
`CutTree_Know_Prohibited_Mood`), so the whole colony reacts when a *visitor* fells
a tree. Cutting a tree is turn-one reflex play. The player meets the religion
before they read it.

### 3.3 Tier C — weekly, or once per prisoner

`ExecutedPrisoner` · `EnslavedPrisoner` · `SoldSlave` (**the most-hooked event in
the game: 22 precept comps reference it**) · `HarvestedOrgan` ·
`PerformedHarmfulSurgery` · `Raided` · `InnocentPrisonerDied` ·
`TakingFromDowned_DownedStripped` · `InvolvedInPsychicRitual` ·
`CharityFulfilled_*` (six variants).

### 3.4 Tier D — a handful per campaign; near-invisible

`GotMarried_TookMansName` / `…WomansName` / `…KeptName` and all the
`GotMarried_SpouseCount_*` and `TookLover_LoverCount_*` gendered refusals (62
`UnwillingToDo_Gendered` comps in total) · `GotBlinded` · `GotScarified` ·
`ChangedIdeo` · `Nomadism_AbandonedSettlement` · `BecomeNonPreferredXenotype`.

⇒ **A design whose distinctive content is entirely `MarriageName_*` and
`SpouseCount_*` has spent its whole budget in tier D.** The precepts are real and
they will validate; the player will finish a 100-hour campaign without one firing.

### 3.5 The null precept, and why it is not always waste

**135 precepts (19.7%) have no comps and no mechanical field** — `Corpses_DontCare`,
`Execution_DontCare`, `Cannibalism_Acceptable`, `Lovin_Free`,
`NutrientPasteEating_DontMind`, `Research_Normal`, `Alcohol_Neutral`,
`Nudity_*_NoRules`, `OrganUse_Acceptable`, `AM_Creep_DontCare`, and so on.

They are not inert. **Their function is to occupy the issue slot so the punitive
default cannot.** 68 precepts carry `defaultSelectionWeight > 0`; `Corpses_Ugly`
and `NutrientPasteEating_Disgusting` are two of them, and they are what a colony
gets if the issue is left open.

⇒ **A "don't care" precept in a design table is a *removal*, not a doctrine.**
Write it as "we suppress `Corpses_Ugly`", so the reviewer can see what it buys.
And check `requiredMemes` first — see §7.

---

## 4. Structure memes and what each commits you to

**35 are live** (9 vanilla Ideology, 13 Alpha Memes, 13 VME). Exactly one per
ideoligion. All have `impact: 0`, so the structure is free against the budget —
**it is the one decision that costs nothing and constrains the most.**

The nine vanilla:

| structure | `deityCount` | worship room | design consequence |
|---|---|---|---|
| `Structure_Animist` | 0–0 | temple | **No deity may be named.** A `deityPresets` block here is a silent failure. Spirits in things; the fiction has to carry itself without a face. |
| `Structure_Ideological` | 0–0 | sanctuary | No gods, a *grand narrative*. Adds `SacrificialFlag`. The natural home for machine, corporate and political faiths. |
| `Structure_Archist` | 0–0 | shrine | No named deity, but archotechs are the object. The Horax cult's structure (`…\Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`). |
| `Structure_TheistAbstract` | **1–4** | temple | Formless, omnipresent gods. The only structure with a *range* wider than one besides Embodied — you may name 1, 2, 3 or 4. |
| `Structure_TheistEmbodied` | **2–4** | pantheon | Gods that walk. **Minimum two** — a design with one god cannot use this. |
| `Structure_OriginChristian` | 1–1 | church | Exactly one deity. Forces `ChristmasTree` + a `CelebrationTree` ritual and requires a pew-class seat (`Pew`, `TST_*`). |
| `Structure_OriginIslamic` | 1–1 | mosque | Exactly one. Requires a `KneelSheet` seat. Carries `exclusionTags: [AM_Ascetic]`. |
| `Structure_OriginHindu` | **4–4** | shrine | **Exactly four deities — not three, not five.** Adds `IncenseShrine`, requires a kneel seat. |
| `Structure_OriginBuddhist` | **0–0** | pagoda | Despite the label, **no deity may be named.** Adds `IncenseShrine`, requires a `KneelPillow`. |

**The rule that catches people:** `deityCount` is an `IntRange` with a hard
minimum as well as a maximum. `Structure_TheistEmbodied` at 2–4 rejects a
one-god pantheon; `Structure_OriginHindu` and `AM_Structure_Kemetism` and
`AM_Structure_Neolithic` and `VME_Structure_ChthonianCult` are all **4–4**, not
"up to 4".

**Modded zero-deity structures**, for a faction that must name no god:
`AM_Structure_Scavenger` · `_Atheist` · `_Corsair` · `_Alienism` · `_Jainism` ·
`_SteampunkRevival` · `VME_Structure_Agnosticism` · `_Authoritarianism` ·
`_Bacchanalianism` · `_Eschatologism` · `_Esotericism` · `_Omnism` ·
`_SecularSpirituality` · `_Serketist` · `_Shintaoism`. The 1–1s are
`AM_Structure_Cubicism`, `_FleshCult`, `_Horaxian`, `_Jewish`, `_Sikhism`,
`VME_Structure_Corporate`, `_CultOfPersonality`, `_Pantheism`; the 4–4s are
`AM_Structure_Kemetism`, `_Neolithic`, `VME_Structure_ChthonianCult`.

⚠️ **26 of the 35 structures are tier 4 — mood and worship-room noun only.** The
nine that do more: `Structure_Ideological`, `Structure_OriginChristian`,
`Structure_OriginHindu`, `Structure_OriginBuddhist`, `Structure_OriginIslamic`,
`AM_Structure_Corsair`, `AM_Structure_Jewish`, `VME_Structure_ChthonianCult`,
`VME_Structure_Bacchanalianism`. **So the structure choice is mostly a fiction and
a deity budget, not a mechanic.** Spend the design effort on step 2.

⚠️ **A structure meme is not always in `<memes>`.** Only **17 of the 46
`IdeoPresetDef`s** name one; the other 29 leave the player to pick. A `FactionDef`
`forcedMemes` block **must** include it — the Horax cult lists
`Structure_Archist` first.

---

## 5. NPC religion versus the player's

**An NPC ideoligion is a costume and a conversion payload.** Almost everything a
precept does needs a colonist to do it, and NPC pawns do not live on your map.

| route the player meets it | what actually gets through | worth designing? |
|---|---|---|
| **A raid arrives** | `styleItemTags` (16 memes carry them: `Cannibal` → `TattooFaceCannibal`, `Inhuman` → `Cultist`, `FleshPurity` → tribal beards, `AnimalPersonhood` → tribal tattoos), `thingStyleCategories` (38 memes), `preferredWeaponClasses` (5 memes), `apparelRequirements` (2 — `Apparel_TortureCrown` from `Guilty` and `PainIsVirtue`) | 🔴 **Yes.** This is the single highest-value NPC design surface, because it is the only one that fires without the player doing anything. |
| **You capture / recruit one of them** | Their whole precept set arrives with the pawn, plus their certainty and `convertPowerFactor`. Every tier-A and tier-B precept above becomes your problem. | ✅ Yes — and this is where a tier-1 refusal on *your* reflex play (mining, tree-cutting, slaughter) is worth more than any mood modifier. |
| **The Ideos tab / faction info** | `ideoName`, `ideoDescription`, deity names, symbol, colour | ✅ Cheap and it is the whole of the fiction the player can read. |
| **Rituals** | ❌ NPC factions do not perform rituals on your map. | ❌ **No.** A tier-3 ritual meme on an NPC buys you a name in a tooltip. |
| **Diplomacy / trade prices** | ❌ No `PreceptDef` field affects faction goodwill or trade. Checked: the full field set has nothing diplomatic. | ❌ No. "They hate you for your religion" is not encodable in the ideo. |
| **Their settlement's look** | *Unverified* — `styles`/`thingStyleCategories` plausibly reach generated bases, but this was not measured. Do not spend on it. | ⚠️ |

🔴 **52 precepts carry `enabledForNPCFactions: false` and cannot appear in a
faction religion at all** — every `Violence_*` (8), every `Nomadism_*` (3),
`DrugUse_Essential`, `Comfort_Essential`, `Alcohol_Essential/Wanted`,
`Mining_Prohibited`, `Traps_Prohibited`, `AutonomousWeapons_Prohibited`,
`GR_AutonomousWeapons_Scorned`, `VME_MeatEating_Abhorrent_Strict`,
`VME_LeatherApparel_Abhorrent/Disliked`, `VME_PermanentBases_*`, `Elderly_Revered`,
`Elderly_Abhorred`, `Compassion_All`, all `DrugPossession_*`, and the whole
`RomanceOnTheRim_*` family. **Note what that costs:** a pacifist NPC faction
cannot hold `Violence_Pacifism`, and a vegan one cannot hold the strict
meat-eating precept. Carry the doctrine with a meme instead (`VME_Pacifist`,
`AM_NonViolence`) and say so in the document.

### What this means for the eleven

**Design an NPC religion outward-in.** Decide first what a raid *looks like* and
what a defector *refuses to do*, and let the rest be flavour text. Doctrine that
only a colonist could enact is fiction — write it, mark it as fiction, and do not
count it toward interest.

---

## 6. Worked example — faction 5, the Continuity Protocol

`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`
lines 290–328. `SKILL.md` §2 rule 3 names it the best entry in the roster.
Running the §1 loop over it as written:

**Step 1 — structure.** `Structure_Ideological`. `deityCount 0–0`, worship room
"sanctuary", adds `SacrificialFlag`. ✅ Correct: the spec says "Deity: none", and
a `deityPresets` block here would be a silent failure. Free against the budget.

**Step 2 — impact budget.** Spec names four normal memes. Measured:

| meme | impact | exclusionTags |
|---|---|---|
| `OuterRim_DroidPrimacy` | 🔴 **does not exist** | — |
| `Transhumanist` | 2 | `FleshAugmentation`, `NecrolatryTranshumanist`, `VQE_Technophobia_Transhumanist`, `VME_EldersOrTranshumanist` |
| `Collectivist` | 1 | `Individualism`, `VME_CollectivistVsEgalitarian` |
| `VME_MechanoidSupremacy` | 2 | `Primacy`, `VQE_Technophobia_MechSupremacy` |

🔴 **`OuterRim_DroidPrimacy` is in neither the live dump nor
`ideology_palette.md`.** No `MemeDef` or `PreceptDef` in this load order contains
`OuterRim` or `Droid`. Naming it in a `FactionDef` is the exact silent no-op
`SKILL.md` §4 warns about — the faction generates without it and nobody is told.
The remaining three are legal: **no exclusionTag overlap**, total impact **5**,
which lands at the bottom of the `Intense` band (5–10). There is room for a
fourth meme, and the design needs one to replace the missing droid meme.

**Step 3 — read the consequences.** `requireOne` across those three memes forces
**nine** precepts:

- `Transhumanist` → `SleepAccelerator_Preferred`, `NeuralSupercharge_Preferred`,
  `Biosculpting_Accelerated` (`biosculpterPodCycleSpeedFactor: 2` — a real ×2),
  `AgeReversal_Demanded`, `NutrientPasteEating_DontMind`, `BodyMod_Approved`,
  `VQE_ARCGenerators_Exalted`
- `Collectivist` → `WorkDrive_Tripled` (`abilityStatFactors`: the moral guide's
  `WorkDrive` ability lasts ×3)
- `VME_MechanoidSupremacy` → `VME_Mechanoids_Exalted`

⇒ **`BodyMod_Approved` in the spec's 8-precept table is redundant** — it is
already forced. And `NutrientPasteEating_DontMind` arrives free, suppressing the
default `NutrientPasteEating_Disgusting`; that is a real gain the spec does not
claim.

**Step 4 — reachability.** Checking the eight listed precepts against
`requiredMemes` and `conflictingMemes`:

| precept | verdict |
|---|---|
| `Slavery_Abhorrent` | ✅ `conflictingMemes: [Raider]` — not taken. Legal. |
| `Execution_Abhorrent` | ✅ `conflictingMemes: [PainIsVirtue]` — not taken. Legal. |
| `VME_AutonomousWeapons_Exalted` | ✅ legal (`MayRequire` vmemese) |
| `MechanoidLabor_Enhanced` | ✅ legal (`MayRequire` Biotech) |
| `BodyMod_Approved` | ✅ but redundant — forced by `Transhumanist` |
| `Corpses_DontCare` | 🔴 **unreachable.** `requiredMemes: [PainIsVirtue, Cannibal, Supremacist, Raider, Inhuman, Necrolatry, VME_BloodCourt, VME_Fleshcrafters]` — this ideoligion holds **none** of them. `Corpses_Ugly` (`classic`, `defaultSelectionWeight: 1`) takes the slot instead. |
| `Research_Fast` | ✅ legal |
| `Charity_Worthwhile` | ✅ `conflictingMemes: [Supremacist, PainIsVirtue, Trader]` — none taken. Legal. |

**Two defects, both silent.** The `Corpses_DontCare` failure is the costlier one,
because it carries the spec's own ⭐ note — *"the body is a chassis"* — and it is
precisely the doctrine that will not exist.

🔴 **And the obvious fix does not work.** "Take one of the eight gatekeeper memes"
sounds cheap until each is checked against the three memes already held *and*
against the design's own doctrine:

| gatekeeper | verdict |
|---|---|
| `Necrolatry` | ❌ `exclusionTags` has `NecrolatryTranshumanist`; so does `Transhumanist`. Illegal. |
| `VME_Fleshcrafters` | ❌ `exclusionTags` has `FleshAugmentation`; so does `Transhumanist`. Illegal (`SKILL.md` §6 names this pair). |
| `Inhuman` | ❌ `factionWhitelist: [HoraxCult]` — unavailable to any other faction. |
| `Raider` | ❌ `Slavery_Abhorrent` lists `conflictingMemes: [Raider]`. |
| `Supremacist` | ❌ forces `[Slavery_Acceptable, Slavery_Honorable, …]` **and** `[Execution_Required, …_RespectedIfGuilty, …_DontCare]`. Kills both of the design's tier-1 refusals. |
| `Cannibal` | ❌ forces the same Execution group; kills `Execution_Abhorrent`. |
| `PainIsVirtue` | ❌ `conflictingMemes` on both `Execution_Abhorrent` and `Charity_Worthwhile`. |
| `VME_BloodCourt` | ⚠️ **the only legal one.** Impact 3 → total 8, still `Intense`, no tag clash, forces `Corpses_DontCare` outright. Also drags in `VME_Leader_BestFighter`, `VME_Death_DontCare`, `Apostasy_Abhorrent`, `VME_Scars_Honorable` — a duelling blood-cult, on a droid enclave. |

⇒ **`Corpses_DontCare` is effectively unreachable for this design. Drop it.** This
is the loop's step 4 earning its place: the check is cheap, the alternative is a
game load spent discovering that pawns still flinch at bodies.

**Step 5 — friction.** Score the doctrine that survives:

| precept | tier | why |
|---|---|---|
| `Slavery_Abhorrent` | 🔴 **tier 1 refusal, tier C rate** | `SoldSlave` + `EnslavedPrisoner`. **This is the whole design.** The Jawa clan's restraint-bolt economy is this faction's murder. |
| `NutrientPasteEating_DontMind` | tier A | suppresses a mood hit that fires at every meal |
| `Execution_Abhorrent` | tier 1 refusal, tier C | |
| `Biosculpting_Accelerated` | mechanical, tier C | real ×2 |
| `WorkDrive_Tripled` | mechanical, tier C | |
| `MechanoidLabor_Enhanced`, `Research_Fast`, `AgeReversal_Demanded`, `VME_Mechanoids_Exalted`, `SleepAccelerator_Preferred`, `NeuralSupercharge_Preferred`, `VQE_ARCGenerators_Exalted`, `Charity_Worthwhile` | tier 4 / mood | flavour |

**Verdict.** One tier-1 refusal aimed straight at the player's labour model, one
free tier-A suppression, two real stat effects, and a long mood tail. `SKILL.md`
§2 rule 3 is right that this is the best entry — **and the reason is exactly rule
1**: the collision is a *refusal*, not a modifier, and it is aimed at something
the player does by reflex on every prisoner. Drop `Corpses_DontCare`, replace the
non-existent droid meme, and it ships.

---

## 7. The checks to run before you call a design done

1. Does at least one precept hit **§3 tier A or B** *and* carry a §2 tier-1
   refusal? If not, the religion is decoration.
2. Does the design table list a precept with `requiredMemes` the meme set does
   not satisfy? (The faction-5 trap. 163 precepts are gated.)
3. Does it list a precept a meme already forces? Cut it — it is noise in a review.
4. For an NPC: is any of it `enabledForNPCFactions: false`? (52 precepts.)
5. Does it depend on a multi-option `requireOne` group landing a particular way?
   (63 groups are gambles.) Say so.
6. **Name-blind test** (`SKILL.md` §2 rule 4): strip the names from two
   neighbouring factions and hand a player the precept lists. If they cannot tell
   which is which, one of them is decoration. The test is passable *only* on §2
   tier-1/2 content — two tier-4 religions always look alike, because they are.
7. Run `python3 src/RimMandrake/Utils/validate_ideoligion.py <spec>` before
   anything reaches XML (`SKILL.md` §4).
