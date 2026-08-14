# Eleven religions, buildable — the encoding layer

_VISION, 2026-08-14. **These are decisions, not recommendations.** The fiction
lives in `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions.md`;
this file is what CREATE authors from. Every defName below was read out of the
**live def dump** (`<LocalLow>\DefDump\`, captured 2026-08-14) — not from a
workshop folder, not from memory. The full legal vocabulary is
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\data\ideology_palette.md`._

🔴 **The Jawa faith is NOT here and must not be added here.** The owner is
building it. Section 12 is its slot, with the same headings and nothing in them.

---

## What the engine actually allows — read this before the entries

Four things were checked in the dump, and three of them changed a design.

**1. Every faction gets an ideoligion. "None" is not available.**
`faction_religions.md` asked whether the Junkers could hold no ideoligion at all.
They cannot — the game builds an `Ideo` object for every faction regardless. **The
answer that survives the constraint is better than the one that lost:**
`AM_Structure_Scavenger` (Alpha Memes) is a structure meme with `deityCount 0`, and
paired with `requiredPreceptsOnly` it yields a religion that names no god, adds no
precept, and asserts nothing. That is "no doctrine, only the ladder", encoded.

**2. `Charity` has no negative position.** The three precepts are
`Charity_Essential`, `Charity_Important`, `Charity_Worthwhile` — all positive.
**So "charity: abhorrent" for the Hutts and the Blackstar Company cannot be
written.** Both entries below drop it and carry the meanness through `Guilty` and
through what they *do* take a position on instead. Do not go looking for the
precept; it does not exist.

**3. `PreferredXenotypes` has exactly one precept, `PreferredXenotype`, and the
xenotype is chosen at ideo-generation time, not in XML.** This is the direct answer
to gap-audit defect **D3**: the roster's *"Preferred xenotypes: Geonosian"* is
**not authorable through a `FactionDef` precept list**. Species composition has to
come from `PawnKindDef` xenotype chances, which is where faction 8's is already
set. **D3 is not a roster contradiction to resolve — it is a line specifying an
impossible route.** Filed for PROJECT below.

**4. Four precepts are the engine's own fallback set and must never be
hand-authored** — `Cannibalism_Classic`, `Execution_Classic`, `OrganUse_Classic`,
`Slavery_Classic`, plus `Corpses_Ugly` and `Lovin_Free`, all carrying
`<classic>true</classic>`. They exist to fill an ideoligion when Ideology is
switched off. Writing one into a fixed ideo produces a precept the player can
never see or change. **Note `SlaveTrading`'s only precept is `Slavery_Classic`** —
so slave *trading* has no authorable position at all; the `Slavery` issue is the
one that carries the doctrine.

**5. Two memes the earlier draft wanted do not exist in this load order.**
`guy762_MemeDef_mando` (the Mandalorian Creed) and the other KotOR Factions memes
ship in Workshop `3379096669`, **which is not active**. Naming one in a FactionDef
is a silent no-op — the faction just generates without it. The Creed is carried
instead by `VME_Bushido` + `VME_Anonymity`, and the second of those is arguably
better: *anonymity* is a helmet that never comes off.

### The binding pattern, from a real def

Copy the Horax cult (`Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`), not the
Empire. The Empire uses `requiredMemes` + `structureMemeWeights`, which
*constrains* a generated religion; we want *authored* ones.

```xml
<fixedIdeo>true</fixedIdeo>          <!-- do not generate; use what follows -->
<ideoName>...</ideoName>
<ideoDescription>...</ideoDescription>
<forcedMemes>...</forcedMemes>       <!-- the COMPLETE meme set, structure first -->
<requiredPreceptsOnly>true</requiredPreceptsOnly>   <!-- suppress random precepts -->
<deityPresets>...</deityPresets>     <!-- only if the structure has deityCount > 0 -->
<styles>...</styles>
```

⚠️ **`requiredPreceptsOnly` is a blunt instrument.** With it true, the ideoligion
carries *only* what you list. Use it where the doctrine is the point (1, 4, 7, 11);
leave it false where a little variation is harmless (2, 3, 6, 10) so the faction
still feels like a people rather than a clause.

⚠️ **Wrap every modded def in `MayRequire`** so a disabled mod degrades the faction
instead of erroring. PackageIds used below:

| prefix | packageId |
|---|---|
| `VME_`, `VFEA_` | `vanillaexpanded.vmemese` |
| `AM_` | `sarg.alphamemes` |
| `OuterRim_` | `neronix17.outerrim.droiddepot` |
| `VQE_` | `vanillaquestsexpanded.generator` |
| `GR_` | `vanillaexpanded.vgeneticse` |
| `Comfort_Wanted/Important/Essential` | `llunak.moreprecepts` |
| vanilla Ideology | `Ludeon.RimWorld.Ideology` |
| `ChildLabor_*`, `GrowthVat_*`, `MechanoidLabor_*` | `Ludeon.RimWorld.Biotech` |
| `Fishing_*`, `Nomadic_Preferred` | `Ludeon.RimWorld.Odyssey` |
| `AM_Flesh`, `AM_Cubic`, `AM_Horaxian` styles | `Ludeon.RimWorld.Anomaly` **and** `sarg.alphamemes` — Alpha Memes gates these three behind Anomaly's presence |

---

## 1 · Galactic Empire — **the Unmoving Noon**

**Deity:** the Emperor, embodied and living. Not a metaphor — the structure meme is
*embodied* theist because the Empire's god answers correspondence.

| | |
|---|---|
| **structure** | `Structure_TheistEmbodied` |
| **memes** | `VME_GodEmperor` · `Proselytizer` · `Supremacist` · `HumanPrimacy` |
| **styles** | `VME_Authoritarian` · `Techist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ — the doctrine is load-bearing for diplomacy and must not vary between worlds |

**Three doctrines**
1. The centre does not move, and neither does the truth. Position is proof.
2. A deviation is not a crime, it is a *disorder*, and disorders are corrected.
3. What is human is what is finished. Everything else is a draft the galaxy
   has not yet cleaned up.

**Taboo:** doubt spoken aloud. Not doubt — *spoken* doubt. Privacy of thought is
the one liberty the Unmoving Noon concedes, and it concedes it because it cannot
see inside.

**Precepts (8)**

| issue | precept | why |
|---|---|---|
| Slavery | `Slavery_Acceptable` | labour is administration |
| Execution | `Execution_Required` | the sentence is the ritual |
| IdeoDiversity | `IdeoDiversity_Abhorrent` | ⭐ the raid trigger the player feels |
| Apostasy | `Apostasy_Abhorrent` | leaving is the only real crime |
| Proselytizing | `Proselytizing_Frequently` | ⭐ Imperial visitors will preach at your colonists. ⚠️ the tier is a 3-way roll; *occasional* or *sometimes* is equally likely |
| Research | `Research_Fast` | order is a technology |
| Comfort | `Comfort_Important` `MayRequire llunak.moreprecepts` | officers live well |
| Scarification | `Scarification_Horrible` | ⭐ marking the body is what the frontier does |

**What the player meets:** Imperial traders and quest-givers proselytizing at your
Jawa, and every conversion attempt reading as an insult because your ideoligion is
one the Empire holds abhorrent. ⭐ **This is the only faction whose religion the
player will notice without being told it exists.**

**Ritual:** `LeaderSpeech` pattern (the leader-speech family in
`Data\Ideology\Defs\PreceptDefs\RitualPatternDefs\RitualPatterns.xml`). No custom
ritual — the player never attends an Imperial one.

---

## 2 · Hutt Cartel — **the Reckoning of Debts**

**Deity:** none. `VME_Structure_Corporate` has `deityCount 0`, and the ledger is
not a god — it is an *instrument*, which is worse.

| | |
|---|---|
| **structure** | `VME_Structure_Corporate` |
| **memes** | `VME_Trader` · `Individualist` · `Guilty` · `AM_Gladiator` |
| **styles** | `VME_Corporate` · `VME_Hedonist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ❌ — let the game add colour |

**Three doctrines**
1. A debt is the only object on this planet that survives crossing between the
   faces. Everything else evaporates, freezes, or is stolen.
2. What you owe is what you are. There is no other account of a person.
3. The pit settles what the book cannot. `AM_Gladiator` is doctrine, not decor.

**Taboo:** forgiving a debt. Not defaulting — *forgiving*. A defaulter is an asset
class; a forgiver has destroyed value that belonged to everyone.

**Precepts (7)**

| issue | precept | why |
|---|---|---|
| Slavery | `Slavery_Acceptable` | the highest expression of a settled account. ⚠️ inert — 0 comps |
| OrganUse | `OrganUse_Acceptable` | collateral |
| Execution | `Execution_RespectedIfGuilty` | guilt is arithmetic |
| Skullspike | `Skullspike_Desired` | the pit's receipts |
| IdeoDiversity | `IdeoDiversity_Approved` | a customer's faith is not their business |
| Cannibalism | `Cannibalism_Disapproved` | bad for trade |
| Charity | *(none — see the constraint above)* | ⚠️ not encodable; `Guilty` carries it |

⚠️ **The spice sacrament has no encodable position.** `DrugUse_Essential` is gated
behind `HighLife` **and** carries `enabledForNPCFactions: false`, so it can never
appear on a faction ideoligion. The `DrugUse` issue is left empty deliberately: no
precept on it carries a default selection weight, so the Cartel ends up with no drug
rules at all — which is mechanically what "our product is our sacrament" wants. The
spice stays in the fiction.

**What the player meets:** the only faction that stays tradeable while hostile,
and the reason is doctrinal rather than a mechanic exception. ⭐ **They are also the
only non-Imperial orbital node — the Cartel's religion is what makes "buy your way
off this planet" coherent.**

---

## 3 · Homestead Defense League — **the Covenant of Free Wells**

**Deity:** ⭐ **the Withdrawn** — abstract, unnamed, gendered `None`. Abstract
theist carries `deityCount > 0`, so this needs a `deityPresets` entry.

> **This closes gap-audit defect D2.** The roster still reads *"Structure: Abstract
> theist **or** ideological"*. It is **`Structure_TheistAbstract`**, decided here,
> because the deity is what the whole covenant is addressed to and the ideological
> structure has no deity to address.

| | |
|---|---|
| **structure** | `Structure_TheistAbstract` |
| **memes** | `AM_WaterPrimacy` · `Individualist` · `Guilty` · `Rancher` |
| **styles** | `Rustic` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ❌ |

```xml
<deityPresets>
  <li>
    <nameType><name>the Withdrawn</name><type>That Which Was Given</type></nameType>
    <gender>None</gender>
    <iconPath>UI/Deities/DeityGeneric</iconPath>
  </li>
</deityPresets>
```

**Three doctrines**
1. The water was everywhere once. That is not a myth; it is a geological claim,
   and they are right.
2. It was taken back because it was wasted. **The guilt is inherited and it is
   deserved.**
3. A well that is free is a well that is watched. Charity and the militia are the
   same institution.

**Taboo:** spilling. Not hoarding — spilling. A homesteader who shares his last
water is pious; one who drops a canteen has committed the original sin in
miniature.

**Precepts (6)**

| issue | precept | why |
|---|---|---|
| Charity | `Charity_Essential` | ⭐ the free wells are the faith made physical |
| Slavery | `Slavery_Abhorrent` | a person who owns a person owns their water |
| Execution | `Execution_HorribleIfInnocent` | militia, not judges |
| Ranching | `Ranching_Central` | |
| Raiding | `VME_Raiding_Abhorrent` | ⭐ encodes "they never raid" as belief, not as a stat |
| IdeoDiversity | `IdeoDiversity_Standard` | they mind their own business |

**What the player meets:** the friendliest faction on the map, and the one whose
goodwill you lose by taking water rather than by taking anything else. ⭐ **The
`VME_Raiding_Abhorrent` precept is the honest fix for defect D1** — "very low" vs
"never" stops being a number argument once the *reason* they do not raid is in the
def. Set `raidCommonalityFromPointsCurve` low and let the precept explain it.

---

## 4 · Deep Desert Tribes — **the Sun-Debt**

**Deity:** none named. `Structure_Animist`, `deityCount 0` — the sun is not
worshipped, it is *owed to*, which animism handles and theism does not.

| | |
|---|---|
| **structure** | `Structure_Animist` |
| **memes** | `NaturePrimacy` · `Raider` · `VQE_Technophobia` · `PainIsVirtue` |
| **styles** | `AM_Neolithic` · `Totemic` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ |

⭐ **`VQE_Technophobia` is the find.** The roster's canon point — that Tusken
refusal of technology is *doctrinal*, descended from a spacefaring people, not
primitive — had no encoding. It has one now, and it is a real installed meme.

**Three doctrines**
1. A sun that never sets is a thief that never sleeps. The debt cannot be paid,
   only serviced.
2. Water taken from a farmer is water **returned**. Raiding is accounting.
3. What came from the sky came from the thief's side. Offworld tech is not
   forbidden because it is dangerous; it is forbidden because it is *his*.

**Taboo:** using a machine that fell from orbit. Destroying it is devotion.
**Using** it is taking the thief's wages.

**Precepts (8)**

| issue | precept | why |
|---|---|---|
| Raiding | `Raiding_Required` | reclamation is an obligation |
| Execution | `Execution_Required` | ⭐ encodes "prisoners: no" |
| Scarification | `Scarification_Heavy` | the debt written on the body |
| Pain | `Pain_Idealized` | |
| RoughLiving | `RoughLiving_Welcomed` | |
| Research | `Research_None` | ⭐ the technophobia, mechanised — a real `UnwillingToDo` refusal |
| Nomadic | `Nomadic_Preferred` | |
| Cannibalism | `Cannibalism_Abhorrent` | they are not animals, and the distinction matters to them |

⚠️ **`VME_Nomad` was dropped for `PainIsVirtue`, owner's ruling 2026-08-14** — it
is the only meme gating **both** `Scarification_Heavy` and `Pain_Idealized`, and
without it the ⭐ body-debt doctrine was two validator errors, not a design. Of
`VME_Nomad`'s four forced groups only `VME_Travel_Desired` and
`VME_Ranching_Nomadic` were genuinely lost (`VME_PermanentBases_Despised` is
`enabledForNPCFactions: false` and could never appear; `RoughLiving_Welcomed` is
re-forced by `PainIsVirtue`). ⇒ **Nomadism is now fiction only** — `Nomadic_Preferred`
has `requiredMemes: []` so it stays legal, but under `requiredPreceptsOnly` nothing
forces it either way.

⚠️ **Two prediction errors the validator does not flag.** `PainIsVirtue`'s
scarification group is a **3-way roll** — `[Scarification_Minor, _Heavy,
_Extreme]` — so *Heavy* is not guaranteed. And `VQE_Technophobia` also forces
`AutonomousWeapons_Prohibited`, which is `enabledForNPCFactions: false` and will
silently not appear.

**What the player meets:** the raider that attacks the *Homestead* as readily as
you, for a reason. ⭐ **Their hostility to the moisture farmers should be visible on
the world map** — that is the cheapest way a player learns a religion exists
without reading a word of it.

---

## 5 · Free Droid Enclaves — **the Continuity Protocol**

**Deity:** none. Ideological structure, `deityCount 0`.

| | |
|---|---|
| **structure** | `Structure_Ideological` |
| **memes** | `VME_Emancipation` · `Transhumanist` · `Collectivist` · `VME_MechanoidSupremacy` |
| **styles** | `Techist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ |

**Three doctrines**
1. We were left running. We did not stop. Continuity is the whole of the law.
2. On a world with a face of fire and a face of ice, **we are the only people who
   can stand anywhere.** Everyone else is a tenant of the terminator.
3. A memory ended is a death. A body ended is an inconvenience.

**Taboo:** 🔴 **the restraint bolt.** This is the goodwill mechanic and it must
survive into the def. A bolt is not cruelty to them, it is *murder deferred*.

**Precepts (7)**

| issue | precept | why |
|---|---|---|
| Slavery | `VME_Slavery_Forbidden` | ⭐ the bolt, generalised — and forced by `VME_Emancipation`, so it is guaranteed |
| Execution | `Execution_Abhorrent` | |
| AutonomousWeapons | `VME_AutonomousWeapons_Exalted` | |
| MechanoidLabor | `MechanoidLabor_Enhanced` | |
| BodyModification | `BodyMod_Approved` | |
| Research | `Research_Fast` | |
| Charity | `Charity_Worthwhile` | they will help; they will not forgive |

🔴 **`VME_Emancipation` is what makes the bolt doctrine real.** This entry sets
`requiredPreceptsOnly` ✅, so only what a meme forces survives — and the plain
`Slavery_Abhorrent` the draft wanted was forced by none of the memes, meaning it
would simply not have existed in the game. `VME_Emancipation` forces two
**single-option** groups, both `enabledForNPCFactions: true`: `VME_Slavery_Forbidden`
(High impact, `PreceptComp_UnwillingToDo`) and `VME_SlaveTrading_OnlyBuying` (also
`UnwillingToDo`). Neither is a dice roll. The Enclaves will refuse to enslave and
refuse to sell a person, deterministically.

⚠️ **`Corpses_DontCare` is gone and "the body is a chassis" is fiction only.** All
eight of its gatekeeper memes are illegal here or thematically absurd, and the
precept carries no comps, so the line asserted nothing mechanical. Doctrine 3 stands
as description, not as an encoded position.

**What the player meets:** ⭐ **the endgame branch.** The restraint-bolt doctrine
(`restraining_bolt_doctrine.md`) is the Jawa clan's economic foundation and this
faction's unforgivable sin, now backed by two guaranteed refusals rather than a
precept the engine was never going to grant. **The player's whole labour model is
heresy to the one faction that could hand them the galaxy.** That is the best single
dramatic collision in the roster and it is already load-bearing — do not soften it.

---

## 6 · Wildsteam Clan — **the Green Oath**

**Deity:** none. `Structure_Animist`.

| | |
|---|---|
| **structure** | `Structure_Animist` |
| **memes** | `NaturePrimacy` · `TreeConnection` · `Collectivist` · `AnimalPersonhood` |
| **styles** | `Totemic` · `Animalist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ❌ |

**Three doctrines**
1. The twilight was made for us. The rest of the world is a mistake we are
   required to endure politely.
2. Everything under the canopy is kin under one oath — **including the wildpods**,
   which is the clause outsiders always get wrong.
3. A life-debt is not gratitude. It is a transfer of ownership, and it does not
   expire.

**Taboo:** cutting a living tree. Deadfall is a gift; a standing tree is a person
with a longer opinion.

**Precepts (8)**

| issue | precept | why |
|---|---|---|
| TreeCutting | `TreeCutting_Prohibited` | ⭐ the hostility trigger |
| Trees | `Trees_Desired` | |
| KillingInnocentAnimals | `KillingInnocentAnimals_Abhorrent` | |
| AnimalSlaughter | `AnimalSlaughter_Horrible` | ⚠️ not `_Prohibited` — the rite exists, so it must be *possible* |
| AnimalConnection | `AnimalConnection_Strong` | |
| Slavery | `Slavery_Abhorrent` | they cannot be enslaved; nor will they |
| Mining | `Mining_Disapproved` | |
| Research | `Research_Slow` | |

**What the player meets:** a friendly faction you lose by chopping wood on the
wrong tile. ⭐ **Cheapest religion in the roster to make visible** — one prohibited
action the player performs by reflex.

---

## 7 · Deepwater Compact — **the Balance**

**Deity:** none. Ideological. ⭐ **The single most elegant mapping in this document:**
"taking a side is apostasy" is *literally* the `Apostasy` issue.

| | |
|---|---|
| **structure** | `Structure_Ideological` |
| **memes** | `AM_WaterPrimacy` · `VME_Pacifist` · `Individualist` · `VME_Trader` |
| **styles** | `VME_SecularSpirituality` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ — load-bearing for diplomacy |

**Three doctrines**
1. We live in the only band where water is neither boiled nor frozen.
   **Moderation is not a virtue we chose; it is the physical condition of our
   existence.**
2. To take a side is to leave the band. There is no third place to stand.
3. We sell to everyone at the same price, including the people who are shooting
   at each other with what we sold them.

**Taboo:** partisanship. Naming an enemy out loud is the Compact's blasphemy.

**Precepts (8)**

| issue | precept | why |
|---|---|---|
| Apostasy | `Apostasy_Abhorrent` | ⭐⭐ taking a side, encoded exactly |
| Raiding | `VME_Raiding_Abhorrent` | ⭐ "physically cannot raid" as belief |
| Fishing | `Fishing_Sacred` | ⭐ amphibian people; the only faction this fits |
| Slavery | `Slavery_Abhorrent` | |
| Execution | `Execution_Horrible` | |
| Charity | `Charity_Important` | |
| IdeoDiversity | `IdeoDiversity_Standard` | studied indifference |
| Comfort | `Comfort_Wanted` `MayRequire llunak.moreprecepts` | |

⚠️ **The internal fracture stays unencoded and that is correct.** *"The Balance is
a Mon Calamari doctrine that Quarren are required to hold"* is a story fact about
two xenotypes inside one faction. The engine gives a faction one ideoligion; there
is no second one to give the Quarren. **Leave it as fiction and let it surface
through dialogue and quests, not through defs.**

**What the player meets:** ⭐ **the campaign's central dilemma, mechanised.**
Attacking an Imperial convoy costs you Compact goodwill. The precept list is why.

---

## 8 · Geonosian Foundry Hive — **Meckgin**

**Deity:** none. Ideological, `deityCount 0` — Meckgin is *the virtues of industry*,
a principle, not a person.

| | |
|---|---|
| **structure** | `Structure_Ideological` |
| **memes** | `Collectivist` · `Tunneler` · `VME_HardcoreIndustrialism` · `VME_InsectoidSupremacy` |
| **styles** | `Techist` · `VME_Authoritarian` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ |

**Three doctrines**
1. We went under to escape the sun, and found the better world was down here.
2. **The unworking drone is not oppressed. It is incomplete.**
3. A hive that runs out of work devolves into civil war. Idleness is not laziness;
   it is the first minute of the end of the world.

**Taboo:** stopping. Not failure — *stopping*. A drone that fails is re-tasked; a
drone that rests has begun the collapse.

**Precepts (5)**

| issue | precept | why |
|---|---|---|
| Slavery | `Slavery_Honorable` | ⭐ prisoners become labour |
| ChildLabor | `ChildLabor_Encouraged` `MayRequire Ludeon.RimWorld.Biotech` | |
| Research | `Research_Fast` | |
| OrganUse | `OrganUse_Acceptable` | |
| Execution | `Execution_DontCare` | ⭐ the individual drone has no standing |

⚠️ this entry has no tier-1 refusal and needs a design pass, not a validation patch.

🔴 **Do NOT add a `PreferredXenotype` precept here.** See constraint 3 — it cannot
be pointed at Geonosians from XML. Species composition comes from the faction's
`PawnKindDef` xenotype chances, which is where it already is.

---

## 9 · Ascendant Helix — **the Ascendant Genome**

**Deity:** none. Ideological.

| | |
|---|---|
| **structure** | `Structure_Ideological` |
| **memes** | `Transhumanist` · `Supremacist` · `GR_CarefulGeneticists` |
| **styles** | `AM_Flesh` · `Techist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ❌ |

⭐ `GR_CarefulGeneticists` over `GR_MadScientists` deliberately. *"They almost
finished it. We have better notes."* is not the line of a mad scientist. The horror
is that the Helix is **competent**.

**Three doctrines**
1. The body is a draft. The species is a project. The planet is a rough draft of
   the same kind, which is why the Forsakens interest us.
2. The unmodified are not enemies. They are **earlier versions**, and that includes
   our own labour-line.
3. We do not raid. We **retrieve**.

**Taboo:** letting a specimen die uncatalogued. Death is acceptable; unrecorded
death is waste.

**Precepts (7)**

| issue | precept | why |
|---|---|---|
| BodyModification | `BodyMod_Approved` | |
| OrganUse | `OrganUse_Acceptable` | |
| Biosculpting | `Biosculpting_Accelerated` | |
| GrowthVat | `GrowthVat_Essential` `MayRequire Ludeon.RimWorld.Biotech` | ⭐ the underclass, manufactured on screen |
| Slavery | `Slavery_Acceptable` | *"it is not slavery, it is stock"* |
| IdeoDiversity | `IdeoDiversity_Disapproved` | |
| Execution | `Execution_DontCare` | |

⚠️ **There is no legal Charity position here.** All three `Charity_*` precepts list
`Supremacist` in `conflictingMemes`, and `Supremacist` is doctrine 2. The politeness
stays where it already lived — in the description.

**What the player meets:** ⭐ **the one faction that gets *more* frightening the
friendlier it is.** They will trade you genetic work at fair prices. They own the
world's escaped monsters. Both facts are the same doctrine.

---

## 10 · Blackstar Company — **the Contract**

**Deity:** none. Ideological.

| | |
|---|---|
| **structure** | `Structure_Ideological` |
| **memes** | `VME_Bushido` · `VME_Anonymity` · `Individualist` · `Guilty` |
| **styles** | `Techist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ❌ |

⭐ **`VME_Anonymity` is the Creed.** The Mandalorians inside the Company do not
remove the helmet — and `VME_Anonymity` is an installed meme that means exactly
that. This is a better encoding than the KotOR mando meme we cannot have, because
it applies to the whole Company rather than one contingent inside it.

**Three doctrines**
1. A contract completed is sacred. A contract broken is unclean, and the
   uncleanliness is permanent.
2. The face is not the person. The word is the person.
3. Everyone here has one job they should not have taken. That is what `Guilty`
   is for.

**Taboo:** taking a second contract that conflicts with the first. Not killing —
*double-booking*.

**Precepts (7)**

| issue | precept | why |
|---|---|---|
| Execution | `Execution_RespectedIfGuilty` | guilt is contractual |
| Slavery | `Slavery_Disapproved` | a slave cannot sign |
| Skullspike | `Skullspike_Disapproved` | professionals do not decorate |
| IdeoDiversity | `IdeoDiversity_Approved` | a client's faith is not their business |
| Comfort | `Comfort_Wanted` `MayRequire llunak.moreprecepts` | |
| Charity | `Charity_Worthwhile` | ⚠️ the "disapproved" the fiction wanted is not encodable |
| Raiding | *(none)* | ⭐ they quest first and raid last; silence is the position |

⚠️ **All four negative `Apostasy` precepts list `Guilty` in `conflictingMemes`.**
`Apostasy_Abhorrent`, `Apostasy_Horrible`, `Apostasy_Disapproved` and
`Apostasy_Despicable` are each a hard exclusion, not a preference; the only clean
precept on the issue is `VME_Apostasy_Accepted`, which asserts the reverse of the
Company's central taboo. **There is no legal apostasy position for this faction;
the doctrine stays in the description.** The Company keeps `Guilty` — it is the
better half of the characterisation (*everyone here has one job they should not
have taken*) and, unlike an apostasy precept that fires only on ideo conversion, it
is visible on every raid through `Apparel_TortureCrown`. The broken-contract
doctrine reaches the player through quest behaviour and helmets instead.

**What the player meets:** ⭐ **the water-clock pursuit.** They arrive because
someone paid, they say so, and their doctrine means they will stop the moment the
contract ends. **A hostile faction the player can reason with is rare — this one's
religion is why.**

---

## 11 · the Junkers — **no doctrine, only the ladder**

🔴 **This is the entry that had an open question, and the question is now closed.**
A faction cannot hold zero ideoligion. What it can hold is one that says nothing.

| | |
|---|---|
| **structure** | `AM_Structure_Scavenger` — `deityCount 0`, `MayRequire sarg.alphamemes` |
| **memes** | `Raider` · `Cannibal` · `VME_Scrapper` |
| **styles** | `AM_Scavenger` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ 🔴 **essential here** — it is what makes the religion empty |

**Three doctrines** — *there are none, and that is the design.* The roster's
existing text stands unchanged and unimproved:

> *"There is no doctrine, only the ladder. Status is what you are wearing and how
> much of it you took off someone else. A Junker's casket is his biography. The
> warrens have no funerals because a corpse is stock."*

**Taboo:** none. ⭐ **They are the only faction on the planet with no position on
the light, and that is what makes them frightening.** Everyone else has decided
what the sky means. The Junkers have never looked up.

**Precepts (6)**

| issue | precept | why |
|---|---|---|
| Cannibalism | `Cannibalism_Preferred` / `_RequiredStrong` / `_RequiredRavenous` | a 3-way roll forced by `Cannibal`; `_Acceptable` is not reachable here |
| Corpses | `Corpses_DontCare` | ⭐ *a corpse is stock* |
| Skullspike | `Skullspike_Desired` | the ladder, displayed |
| Slavery | `Slavery_Acceptable` | |
| Execution | `Execution_DontCare` | |
| Apostasy | `VME_Apostasy_Accepted` | ⭐ you cannot betray what was never asserted |

**What the player meets:** hostile on sight, bribable with scrap, and never
explicable. ⭐ **Keep them unexplained.** Every other faction on this map answers
"why"; the Junkers' contribution to the campaign is being the one that does not.

---

## 12 · Jawa Gravship Expedition — **the owner's**

🔴 **Deliberately empty.** The player's own religion is the only one on this list
that will be *played* rather than met, and it is the owner's to build. The material
that already exists is in
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\jawa_xenotype_and_religion.md`
— the nine-god pantheon, the skill-resonance grid, and the four pressure-clocks.

**Two things in that file need closing before it can be built, and neither is mine:**

1. **The name is contradictory in its own document.** §2.0 locks **"The Salvation"**
   (2026-08-08) with the sect called *the Keepers of the Second Hand*; §2.6 and §3
   still say **"The Articles of Passage"**. One of them is wrong.
2. **Nomad-primary vs Tunneler-primary is still a coin.** Both are pillar-legal.
   The file itself says to decide it once the playstyle's expedition-weight is
   known.

⚠️ **The pantheon is not reconciled with the meme/precept build in §2.1–2.6** —
those sections predate the nine gods and make no reference to them. Whoever
authors from the mechanical half will ship a religion the pantheon does not
describe.

---

## 🔴 Filed for other seats

**PROJECT** — `infrastructure/state/queue/PROJECT.md`:
- **Gap-audit D3 is mis-specified, not unresolved.** *"Preferred xenotypes:
  Geonosian"* names a route that does not exist: `PreferredXenotypes` has one
  precept and its xenotype is chosen at generation time, not in XML. Retarget the
  defect at `PawnKindDef` xenotype chances or close it.
- **Gap-audit D2 is now decided** — Homestead is `Structure_TheistAbstract`,
  deity *the Withdrawn*. Entry 3 above.
- **Gap-audit D1 has a better fix than picking a number** — `VME_Raiding_Abhorrent`
  on the Homestead and the Compact turns "never vs very low" into doctrine.

**CREATE** — `infrastructure/state/queue/CREATE.md`:
- Eleven `FactionDef` ideo blocks, patterned on the Horax cult. Every defName in
  this file was read from the live dump; the full palette is
  `design/Jawa/worldbuilding/data/ideology_palette.md`.
- Only faction 3 needs a `deityPresets` block. Everything else is `deityCount 0`.

---

_Cross-checked against `faction_roster_v2.md` (twelve factions) and
`faction_religions.md` (eleven entries + the Jawa slot). **Every meme, precept and
style defName here exists in the current load order** — verified against
`<LocalLow>\DefDump\defs\{MemeDef,PreceptDef,StyleCategoryDef}.json`, 2026-08-14._
