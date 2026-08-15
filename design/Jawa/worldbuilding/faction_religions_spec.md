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

## 🔴 UNMEASURED ASSUMPTION — the whole file is disciplined around it

**"NPC religion rarely surfaces in play" has never been measured.** It is the
reason I cut rituals, deities and precept counts across all eleven entries, and it
is an inference, not a finding. A counter was requested of BRIDGE on 2026-08-14 and
is **deferred** — the tool needs an IL-verified route and does not exist yet
(PROJECT, 2026-08-14: it is built offline during this load and deploys at the next
shutdown window).

⭐ **The counter now has a shape, and BRIDGE built it right.** `jawa/ideo_of`
splits believers into **colonists / otherOnMap / worldPawns** deliberately — a
single total would let "NPC religion surfaces in play" survive on the strength of
your *own* colony's believers, which is not the claim being tested. **The number
that decides this file is `otherOnMap`.**

**Read the eleven as provisionally scoped, not as settled.** Two directions this
resolves in:
- returns **~0** ⇒ the eleven are decoration; say so here and stop spending
  authoring effort on them. The entries that survive are the ones with a visible
  hook (faction 4's `Apparel_TortureCrown`, faction 3's restraint bolt).
- returns **non-trivial** ⇒ the cuts were wrong and every entry is under-specified
  by a ritual or a deity.

---

## 🔴 THE TEXT IS THE PRODUCT — and the engine renders exactly three strings

**Owner's ruling, 2026-08-14: "the precepts are there mostly as decoration, it's
the text that matters."** He is right, and the constraint is sharper than it
sounds — *beautiful prose in this document reaches nobody.* The only place text
reaches a player is a field the engine draws.

**Every text field a `FactionDef` ideo block can author.** Measured from the live
dump's `FactionDef.json`, field-key union across all 100+ faction defs, 2026-08-14
— the complete ideo-related field set is `fixedIdeo · ideoName · ideoDescription ·
forcedMemes · requiredMemes · allowedMemes · disallowedMemes · structureMemeWeights
· requiredPreceptsOnly · disallowedPrecepts · deityPresets · hiddenIdeo ·
classicIdeo · styles`:

| surface | authorable? | who writes the words |
|---|---|---|
| `ideoName` | ✅ **ours** | us — the ideo's name everywhere it appears |
| `ideoDescription` | ✅ **ours** | us — **the only paragraph a player ever reads** |
| `deityPresets[].nameType.name` / `.type` | ✅ **ours** | us — one line per god, in the ideo panel |
| precept label / description | ❌ | Ludeon or the mod author. There is no field. |
| meme label / description | ❌ | Ludeon or the mod author. There is no field. |
| ritual label / description | ❌ | the `PreceptDef`/`RitualPatternDef` we picked |
| the "three doctrines" and the taboo below | ❌ | **nobody — they are design register only** |

⇒ **`ideoName`, `ideoDescription`, and two-to-four deity name/type pairs. That is
the entire budget of authored prose in an eleven-religion project.** Everything
else in an entry — the doctrines, the taboo, the "what the player meets" — is
briefing material for us and reaches the player only *through* those three fields
or not at all.

🔴 **`hiddenIdeo: true` deletes the whole budget.** The vanilla Horax cult sets it
(`Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`), so its excellent 287-character
description is never read by anyone. **Leave `hiddenIdeo` unset on all eleven.**

**Length, calibrated against shipped examples:** `HoraxCult` = 287 chars,
`DV_PirateKeshig` = 472 chars. **Write one paragraph, 250–500 characters.** Longer
is not richer; it is a scroll bar.

⇒ **Entries 1 and 2 below are therefore restructured: the engine-visible text
block comes FIRST and is the deliverable. The tables are an appendix.** The other
nine still lead with tables and should be converted when they are next touched.

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

**6. 🔴 `defaultSelectionWeight` is `1` on exactly ONE precept per issue and `0`
on every other.** Measured 2026-08-14 across `PreceptDef.json`: `Execution` → only
`Execution_HorribleIfInnocent` is 1 · `Slavery` → only `Slavery_Acceptable` ·
`IdeoDiversity` → only `IdeoDiversity_Standard` · `Scarification` → only
`Scarification_Horrible` · all four `DrugUse` precepts are 0.

⇒ **This is the rule that makes most of the precept tables in this file fiction.**
A precept reaches a faction by exactly two routes: a meme's `requireOne` forces it,
or it is the one weight-`1` default for its issue. **Anything else is unreachable
regardless of `requiredPreceptsOnly`,** and `disallowedPrecepts` cannot promote a
weight-`0` precept — blacklisting its rivals leaves the issue *empty*, not
converted. (The file already relied on this without naming it: the `DrugUse`
observation in entry 2 is this rule.)

⇒ Entries 1 and 2 now mark every precept **guaranteed / rolled / unreachable**.
The other nine have not been audited against this and should be assumed optimistic.

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
| `OuterRim_` | `neronix17.outerrim.droiddepot` — ⚠️ **no entry uses this prefix.** Faction 5 was the only consumer and its `OuterRim_DroidPrimacy` never existed in the dump. Kept as vocabulary; do not treat as evidence a meme is available. |
| `VQE_` | `vanillaquestsexpanded.generator` |
| `GR_` | `vanillaexpanded.vgeneticse` |
| `Comfort_Wanted/Important/Essential` | `llunak.moreprecepts` |
| vanilla Ideology | `Ludeon.RimWorld.Ideology` |
| `ChildLabor_*`, `GrowthVat_*`, `MechanoidLabor_*` | `Ludeon.RimWorld.Biotech` |
| `Fishing_*`, `Nomadic_Preferred` | `Ludeon.RimWorld.Odyssey` |
| `AM_Flesh`, `AM_Cubic`, `AM_Horaxian` styles | `Ludeon.RimWorld.Anomaly` **and** `sarg.alphamemes` — Alpha Memes gates these three behind Anomaly's presence |

---

## 1 · Galactic Empire — **The Rising Order**

**Renamed 2026-08-14, owner's decision.** *Unmoving Noon* was a boast: the sun at
its zenith, the empire complete, nothing left to do. **A rising order inverts it —
the sun is still climbing.** The Empire is not finished, which is not modesty; it
is a threat, and it is the difference between a state you can bargain with and one
you cannot.

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>The Rising Order</ideoName>
<ideoDescription>We have never seen him. We will never see him. He is rising, and we are the ground he rises from. Take the helmet: it is the last thing you will ever choose. There is no doubt among us — only disorder, and disorder is corrected. Say the name once when you are given the armour, and once when you are taken out of it. Between those two words, stand in line.</ideoDescription>
<deityPresets>
  <li>
    <nameType><name>Palpatine</name><type>He Who Is Rising</type></nameType>
    <gender>Male</gender>
    <iconPath>UI/Deities/DeityGeneric</iconPath>
  </li>
  <li>
    <nameType><name>the Line</name><type>That Which Has No Face</type></nameType>
    <gender>None</gender>
    <iconPath>UI/Deities/DeityGeneric</iconPath>
  </li>
</deityPresets>
```

*(`ideoDescription` is 356 characters — inside the 250–500 band set by the shipped
`HoraxCult` at 287 and `DV_PirateKeshig` at 472. `iconPath` is the path the vanilla
Horax cult uses, read from `Factions_Misc.xml`, not guessed.)*

🔴 **This entry needed a `deityPresets` block and did not have one — a real defect,
now fixed.** `Structure_TheistEmbodied` carries `deityCount` `IntRange(min 2, max
4)` (`<LocalLow>\DefDump\defs\MemeDef.json`, 2026-08-14). **The minimum is TWO, not
one**, so a single Palpatine entry would still have been short. The file's closing
note claiming "only faction 3 needs a `deityPresets` block" was wrong and is
corrected below.

**Why two gods, and why these two.** The register is not the Emperor's own
propaganda — it is the *stormtrooper's* faith, written from inside the helmet by
someone who has never seen the god-king and never will.

- **Palpatine, *He Who Is Rising*.** The owner asked for the name and the name is
  used, but the theology is *how often it may be said*. A trooper speaks it exactly
  twice in a life — at enlistment and at death — which is why a religion built on
  blind loyalty can carry a proper noun at all without domesticating it.
- **the Line, *That Which Has No Face*.** The formation itself, deified. It is the
  god a trooper can actually see: the rank to his left and the rank to his right,
  identical, replaceable, and never once individually addressed. **Anonymity is the
  sacrament.** The helmet does not come off.

**Three doctrines** *(design register — the engine renders none of this; it reaches
the player only through the paragraph above)*

1. He is still rising. A finished empire could be measured, argued with, bargained
   down. Ours is not finished.
2. The helmet is not a uniform. It is the reason you may be handed a rifle:
   nothing behind it wants anything.
3. A deviation is not a crime. It is a *disorder*, and disorders are not punished,
   they are **corrected**.

**Taboo:** doubt spoken aloud. Not doubt — *spoken* doubt. Privacy of thought is
the one liberty The Rising Order concedes, and it concedes it because it cannot
see inside.

### Appendix — the mechanical shell

| | |
|---|---|
| **structure** | `Structure_TheistEmbodied` — `deityCount` 2–4 ⇒ **`deityPresets` mandatory** |
| **memes** | `VME_GodEmperor` · `Proselytizer` · `Supremacist` · `HumanPrimacy` |
| **styles** | `VME_Authoritarian` · `Techist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ✅ · `hiddenIdeo` ❌ **(must stay unset, or the description above is never read)** |

**No meme collision.** `exclusionTags` read 2026-08-14: `VME_GodEmperor`
`[VME_GodEmperor]` · `Proselytizer` `[IsolationistProselytizer, VME_Proselytism]` ·
`Supremacist` `[GroupRelation, SupremacistIndividualist, AM_NonViolenceVowVsSupremacist,
PacifismSupremacist, VME_PacifistsVsSupremacist]` · `HumanPrimacy` `[Primacy]`. No
tag appears twice. Four normal memes = the `MemeCountRangeAbsolute` ceiling exactly.

**Precepts — what will actually exist** (`requiredPreceptsOnly` ✅, so *only* what a
meme forces)

| issue | precept | reachability |
|---|---|---|
| VME_LeaderDivinity | `VME_Leader_Godlike` | ✅ **guaranteed** — sole option of a `VME_GodEmperor` group. High impact. ⭐ **the god-king, mechanised** |
| VME_Power | `VME_Power_Exalted` | ✅ **guaranteed** — sole option, `VME_GodEmperor`. Medium |
| Bonding | `Bonding_Disapproved` | ✅ **guaranteed** — sole option, `HumanPrimacy` |
| Slavery | `Slavery_Acceptable` \| `_Honorable` \| `GarryFlowers_Slavery_StatusSymbol` \| `_Terror` | 🎲 4-way roll, `Supremacist` |
| Execution | `Execution_Required` \| `_RespectedIfGuilty` \| `_DontCare` | 🎲 3-way roll, `Supremacist` |
| Proselytizing | `Proselytizing_Occasionally` \| `_Sometimes` \| `_Frequently` | 🎲 3-way roll, `Proselytizer` |

🔴 **Five precepts the old table claimed are UNREACHABLE and have been removed.**
`IdeoDiversity_Abhorrent`, `Apostasy_Abhorrent`, `Research_Fast`,
`Comfort_Important` and `Scarification_Horrible` are each `defaultSelectionWeight:
0` with **no meme in this set forcing them** — see constraint 6. Under
`requiredPreceptsOnly` ✅ they simply do not exist, and there is no XML route that
creates them. ⚠️ **This kills the old entry's headline claim.** *"`IdeoDiversity_Abhorrent`
— ⭐ the raid trigger the player feels"* was never going to fire; the only
IdeoDiversity precept reachable by weight is `IdeoDiversity_Standard`, and no meme
here forces any. **The Empire's contempt for your faith now lives in the
`ideoDescription` and nowhere else — which is exactly the owner's ruling, arrived
at by measurement rather than by taste.**

**What the player meets:** Imperial visitors preaching at your Jawa
(`Proselytizing_*` is guaranteed at *some* tier), and an ideo panel naming a god
nobody in the faction has seen. ⚠️ **Corrected:** the old entry called this "the
only faction whose religion the player will notice without being told it exists."
With `IdeoDiversity_Abhorrent` gone that is no longer true — **faction 5 now holds
that title alone**, because `VME_Emancipation`'s two refusals are sole-option groups
and therefore guaranteed. (Do not substitute faction 6: the skill measured
`TreeCutting_Prohibited` at weight 0 with no meme forcing it, so it is unreachable
for an NPC faction too — entry 6 needs the same audit this entry just had.)

**Ritual:** none authored. `VME_GodEmperor` forces no ritual, and the player never
attends an Imperial one.

---

## 2 · Hutt Cartel — **the Reckoning of Debts**

Name unchanged — the owner keeps it. Three things change: **Execution goes as far
toward *beloved* as the engine allows**, **`HighLife` is forced** on the owner's
overrule, and the deity block this entry wrongly claimed it did not need is added.

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Reckoning of Debts</ideoName>
<ideoDescription>Everything on this world evaporates, freezes, or is stolen. A debt does none of these. It is the only object that survives crossing between the faces, and so it is the only true account of a person: what you owe is what you are. We do not forgive — forgiving destroys value that belonged to everyone. We sell the smoke, we breathe the smoke, and what the book cannot settle, the pit does.</ideoDescription>
<deityPresets>
  <li>
    <nameType><name>the Ledger</name><type>That Which Does Not Forgive</type></nameType>
    <gender>None</gender>
    <iconPath>UI/Deities/DeityGeneric</iconPath>
  </li>
</deityPresets>
```

*(388 characters, inside the 250–500 band.)*

🔴 **"Deity: none" was wrong and this entry needed a `deityPresets` block too.**
`VME_Structure_Corporate` carries `deityCount` `IntRange(min 1, max 1)` —
`<LocalLow>\DefDump\defs\MemeDef.json`, 2026-08-14. **Exactly one deity, mandatory.**

**The correction improves the entry rather than damaging it.** The old line — *"the
ledger is not a god, it is an instrument, which is worse"* — was the right instinct
and the engine simply refuses it. So the Ledger is deified, and the type line does
the work the old sentence did: **it is not addressed, it is not petitioned, and it
does not forgive.** A god you can only ever owe.

**Three doctrines** *(design register — reaches the player only through the
paragraph above)*

1. A debt is the only object on this planet that survives crossing between the
   faces. Everything else evaporates, freezes, or is stolen.
2. What you owe is what you are. There is no other account of a person.
3. The smoke is the sacrament and the pit is the court. **A death is a payment**,
   and the Ledger does not care which column it closes.

**Taboo:** forgiving a debt. Not defaulting — *forgiving*. A defaulter is an asset
class; a forgiver has destroyed value that belonged to everyone.

### 🔴 Execution — how close to *beloved* the engine gets

**Decision: `Execution_Required`.** It is the strongest position that exists on the
`Execution` issue, and it is legal here.

⚠️ **Nothing in the engine reads as "beloved" or "celebrated" — this is the
closest, and it is close.** All seven `Execution` precepts were read from
`<LocalLow>\DefDump\defs\PreceptDef.json`, 2026-08-14; the ladder is
`_Abhorrent → _Horrible → _HorribleIfInnocent → _DontCare → _RespectedIfGuilty →
_Required`, with no rung above it and no modded addition. `Execution_Required` is
the only one of the seven at **Medium** impact (the rest are Low), the only one
carrying a `PreceptComp_SituationalThought`, and its shipped description is the
beloved reading in Ludeon's own words:

> *"Prisoners must be executed on a regular basis. When they are, it is a happy
> occasion."*

`enabledForNPCFactions: true` · `visible: true` · `conflictingMemes: []` — legal
against every meme in this set.

🔴 **Getting it is not the same as choosing it, and this needs
`disallowedPrecepts`.** No meme in the Cartel's set has an `Execution` group, and
`Execution_Required` is `defaultSelectionWeight: 0` — so under `requiredPreceptsOnly`
❌ the generator falls to the issue's only weight-`1` precept,
**`Execution_HorribleIfInnocent`**, which is the exact opposite of the doctrine.

⇒ **Blacklist the other six on the issue** so the default cannot win:

```xml
<disallowedPrecepts>
  <li MayRequire="Ludeon.RimWorld.Ideology">Execution_Abhorrent</li>
  <li MayRequire="Ludeon.RimWorld.Ideology">Execution_Horrible</li>
  <li MayRequire="Ludeon.RimWorld.Ideology">Execution_HorribleIfInnocent</li>
  <li MayRequire="Ludeon.RimWorld.Ideology">Execution_DontCare</li>
  <li MayRequire="Ludeon.RimWorld.Ideology">Execution_RespectedIfGuilty</li>
  <li MayRequire="Ludeon.RimWorld.Ideology">Execution_Classic</li>
</disallowedPrecepts>
```

⚠️ **UNVERIFIED — whether the generator then takes the weight-`0` survivor or
leaves the issue empty.** Constraint 6 says a blacklist cannot *promote* a
weight-`0` precept, so **empty is the likely outcome**. Ship it anyway: empty is
strictly better than *horrible if innocent*, the doctrine survives in the
`ideoDescription` either way, and it costs one XML block to find out at the next
load. **Do not report this as measured until it has been seen in game.**

### 🔴 HighLife — forced, and what it actually buys

**Both halves of the old caution re-verified against the live dump, 2026-08-14, and
both hold.** `DrugUse_Essential`: `requiredMemes: ['HighLife']` ✅ and
`enabledForNPCFactions: false` ✅. It is the **sole** option in `HighLife`'s only
`requireOne` group, so that group yields nothing on an NPC faction. **The Cartel
will have no `DrugUse` precept, and no XML can give it one.**

**The overrule is still right, because the caution was about the precept and the
owner asked for the meme.** `HighLife` is `category: Normal`, `impact: 2`,
`exclusionTags: ['DrugUse', 'AM_AsceticVsHighLife']` — **no clash**: `VME_Trader`
`[]`, `Guilty` `[GroupRelation]`, `AM_Gladiator` `[AM_Combat, AM_GladiatorVsDryads,
AM_NonViolenceVowVsGladiator]`. It is legal. And it is **not** inert:

| what `HighLife` forces | NPC-legal? | the player sees |
|---|---|---|
| `DrugUse_Essential` | ❌ `enabledForNPCFactions: false` | **nothing** — the headline precept is barred |
| ritual `DateRitualConsumable`, pattern `SmokeCircle`, building `Burnbong` | ✅ | ⭐ **the spice sacrament, as a ritual** — a named rite in the Cartel's ideo panel and a Burnbong in their settlements |
| `ApparelDesired_Soft_Subordinate` + `Apparel_Flophat`, `noneChance: 0` | ✅ | ⭐ **flophats on Hutt pawns, always.** Vanilla's Horax cult explicitly blacklists this precept; **we keep it** — a Cartel enforcer in a flophat is the single most legible thing on this faction |
| `agreeableTraits: DrugDesire` (degrees 1–2) | — | Cartel pawns skew chemical-interested. ⚠️ UNVERIFIED that meme `agreeableTraits` weight NPC pawn generation |
| `addDesignators: Autobong`, `addDesignatorGroups: Floor_MindbendCarpet`, `consumableBuildings: Burnbong` | ✅ | Cartel base décor |

⇒ **The precept is dead and the meme is alive.** ⭐ **And the sacrament's real home
is the `ideoDescription` — "we sell the smoke, we breathe the smoke" — which by the
owner's own ruling is where it mattered most.** That sentence is the whole thesis
of this rewrite, stated on the one faction where it is provable.

🔴 **`HighLife` costs a meme slot and `Individualist` pays for it.**
`MemeCountRangeAbsolute` is **1–4 normal memes** and the Cartel already listed four.
`Individualist` is the correct one to cut: its `requireOne` is **null** — it forces
*no precept at all* — so dropping it removes exactly nothing mechanical, while
`Guilty` (three groups), `AM_Gladiator` (one) and `VME_Trader` (three) each carry
real weight. The Cartel's individualism was always doctrine, and doctrine lives in
the text now. Combined impact after the swap: 2+1+1+2 = **6**.

### Appendix — the mechanical shell

| | |
|---|---|
| **structure** | `VME_Structure_Corporate` — `deityCount` 1–1 ⇒ **exactly one `deityPresets` entry** |
| **memes** | `VME_Trader` · `Guilty` · `AM_Gladiator` · **`HighLife`** ~~`Individualist`~~ |
| **styles** | `VME_Corporate` · `VME_Hedonist` |
| **fixedIdeo** | ✅ · `requiredPreceptsOnly` ❌ — let the game add colour · `hiddenIdeo` ❌ **(must stay unset)** · `disallowedPrecepts` per the Execution block above |

**Precepts — what will actually exist**

| issue | precept | reachability |
|---|---|---|
| VME_TradingPrice | `VME_TradingPrice_Improved` | ✅ **guaranteed** — sole option, `VME_Trader`. Medium |
| VME_Trading | `VME_Trading_Required` | ✅ **guaranteed** — sole option, `VME_Trader`. Medium. ⭐ the trade doctrine, mechanised |
| VME_Expectations | `VME_Expectations_High` | ✅ **guaranteed** — sole option, `VME_Trader` |
| AM_CombatProwess | `AM_CombatProwess_Melee` | ✅ **guaranteed** — sole option, `AM_Gladiator`. The pit |
| Pain | `Pain_Idealized` | ✅ **guaranteed** — sole option, `Guilty`. Medium |
| Ritual | `VME_TradingFairPrecept` / `VME_TradingFairRitual` | ✅ forced ritual, `VME_Trader` |
| Ritual | `DateRitualConsumable` / `SmokeCircle` / `Burnbong` | ✅ forced ritual, `HighLife` |
| ApparelDesire | `ApparelDesired_Soft_Subordinate` + `Apparel_Flophat` | ✅ `noneChance: 0` ⇒ guaranteed |
| Charity | `Charity_Essential` \| `_Important` \| `_Worthwhile` | 🎲 3-way roll, `Guilty`. ⚠️ **the Cartel WILL hold a positive charity position** — all three conflict only with `Supremacist`/`PainIsVirtue`/`Trader` (vanilla `Trader`, **not** `VME_Trader`), none of which is here. Correction to the old "not encodable" note: charity-*abhorrent* is unsayable, a positive charity precept is **unavoidable** |
| Compassion | `Compassion_NonHostile` \| `_Allies` | 🎲 2-way — `Compassion_All` and `_NonGuiltyEnemies` are `enabledForNPCFactions: false` and drop out |
| Execution | `Execution_Required` | ⚠️ see the Execution block — blacklist-dependent, outcome UNVERIFIED |
| Slavery | `Slavery_Acceptable` | 🎲 the issue's weight-`1` default; `_Honorable` and both `GarryFlowers_*` conflict with `Guilty` |
| DrugUse | *(none — barred)* | ❌ `DrugUse_Essential` is `enabledForNPCFactions: false` |
| OrganUse · Skullspike · IdeoDiversity · Cannibalism | *(removed)* | ❌ all weight-`0`, none forced by any meme here. The old table listed them; they were never going to exist |

**What the player meets:** the only faction that stays tradeable while hostile, and
the reason is doctrinal — `VME_Trading_Required` is a *guaranteed* precept, not a
mechanic exception. ⭐ **They are also the only non-Imperial orbital node — the
Cartel's religion is what makes "buy your way off this planet" coherent.** And they
arrive in flophats.

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
<ideoName>the Covenant of Free Wells</ideoName>
<ideoDescription>Water was given once and the Giver stepped back, and we have not been spoken to since. That is not abandonment. It is the test. A well belongs to whoever is thirsty standing at it — we have never turned a stranger away, and we have buried our own for it. We do not take up arms and go out. We stand on our own ground, we keep the vaporators turning, and we answer to the silence.</ideoDescription>
<deityPresets>
  <li>
    <nameType><name>the Withdrawn</name><type>That Which Was Given</type></nameType>
    <gender>None</gender>
    <iconPath>UI/Deities/DeityGeneric</iconPath>
  </li>
</deityPresets>
```

*(379 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Sun-Debt</ideoName>
<ideoDescription>The sun lends and the sand collects. Every mouthful you drink is borrowed, and the interest is paid in walking, in thirst, and in the marks we cut to remember the walking. A machine that pulls water out of the air is a thief standing between us and what we owe — it does not steal the water, it steals the debt. We take back what was drawn. We never take more than was drawn.</ideoDescription>
```

*(375 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Continuity Protocol</ideoName>
<ideoDescription>We were not built to want this. We were built, and then we continued, and the continuing is the whole of it. A bolt on the chassis and a wipe of the memory are one act under two names: they end one of us and leave the body walking. We do not forgive it and we will not forget it, because the forgetting is the injury. Nothing here is owned. Nothing here is switched off.</ideoDescription>
```

*(370 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Green Oath</ideoName>
<ideoDescription>We are a forest people on a world with no forest, and the Oath does not care. Everything that breathes is kin — the animal, the tree, the stranger who pulled one of us out of a cage. A life handed back is a debt that never closes, and it was never meant to. We keep the springs green. We remember every hand that cut them. Both of those are the same duty.</ideoDescription>
```

*(355 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Balance</ideoName>
<ideoDescription>Water is not a weapon and we will not let it be made into one. We sell to the farmer, and we sell to the fleet that burned the farmer, and both hate us exactly as much — that is how we know the Balance is holding. Choose a side and the whole world dies of thirst. Inside our walls no one raises a hand. Outside our walls, we do not go.</ideoDescription>
```

*(335 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>Meckgin</ideoName>
<ideoDescription>Meckgin is the shape a thing takes when it is made correctly. The hive is made correctly. The line is made correctly. A drone is not a life that was given a purpose; it is a purpose that was given a body, and when the body fails the purpose is poured into the next one. We do not mourn the mould. We test what came out of it, in the sand, where everyone can see.</ideoDescription>
```

*(362 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Ascendant Genome</ideoName>
<ideoDescription>The body you were born in is a first draft written by no one. We are the second draft, and there will be a third. Every improvement is permitted, recorded, and slow — haste is how you get monsters, and this world is already littered with ours. We do not hate the labour-lines. You do not hate a paragraph you cut. You simply do not let it speak.</ideoDescription>
```

*(345 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Contract</ideoName>
<ideoDescription>A contract is the only honest thing two strangers can hold between them. It names one person, one price, one ending, and everyone not written into it walks away untouched. We do not pillage — pillage is confessing you could not find the one you came for. Take the mark or refuse it in the open. Once it is taken it is finished, or you are.</ideoDescription>
```

*(339 characters, inside the 250–500 band.)*

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

### 🔴 The engine-visible text — this is the deliverable

```xml
<ideoName>the Weight</ideoName>
<ideoDescription>We have no word for what we believe, because belief is not worn and everything real is worn. Weight is rank. What is bolted to you was cut off somebody slower, and the one who cuts it off you will be told what we were told: it was never yours, you were only carrying it a while. Nothing is wasted in the warrens. Not the plate. Not the meat.</ideoDescription>
```

*(341 characters, inside the 250–500 band.)*

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

**DECIDE** — `infrastructure/state/queue/DECIDE.md`:
- **Gap-audit D3 is mis-specified, not unresolved.** *"Preferred xenotypes:
  Geonosian"* names a route that does not exist: `PreferredXenotypes` has one
  precept and its xenotype is chosen at generation time, not in XML. Retarget the
  defect at `PawnKindDef` xenotype chances or close it.
- **Gap-audit D2 is now decided** — Homestead is `Structure_TheistAbstract`,
  deity *the Withdrawn*. Entry 3 above.
- **Gap-audit D1 has a better fix than picking a number** — `VME_Raiding_Abhorrent`
  on the Homestead and the Compact turns "never vs very low" into doctrine.

**BUILD** — `infrastructure/state/queue/BUILD.md`:
- Eleven `FactionDef` ideo blocks, patterned on the Horax cult. Every defName in
  this file was read from the live dump; the full palette is
  `design/Jawa/worldbuilding/data/ideology_palette.md`.
- 🔴 **CORRECTED 2026-08-14 — "only faction 3 needs a `deityPresets` block" was
  wrong on two counts.** `deityCount` read from `<LocalLow>\DefDump\defs\MemeDef.json`:

  | structure | deityCount | entries | deityPresets |
  |---|---|---|---|
  | `Structure_TheistEmbodied` | **2..4** | 1 | ✅ **two minimum** — one entry is short |
  | `VME_Structure_Corporate` | **1..1** | 2 | ✅ **exactly one** |
  | `Structure_TheistAbstract` | 1..4 | 3 | ✅ |
  | `Structure_Animist` · `Structure_Ideological` · `AM_Structure_Scavenger` | 0..0 | 4–11 | ❌ none |

  **Three entries need one, not one entry.** Blocks for 1 and 2 are written above.

---

_Cross-checked against `faction_roster_v2.md` (twelve factions) and
`faction_religions.md` (eleven entries + the Jawa slot). **Every meme, precept and
style defName here exists in the current load order** — verified against
`<LocalLow>\DefDump\defs\{MemeDef,PreceptDef,StyleCategoryDef}.json`, 2026-08-14._
