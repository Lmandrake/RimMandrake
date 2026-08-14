# The Unearned — begging as heresy, ownership as mercy

_VISION, 2026-08-14. **These are decisions, not recommendations.** CREATE authors
from this file and should not have to invent a defName, a field or an event.
Companion to `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`;
it closes that file's entry-2 and entry-10 `Charity` gaps. Every defName below was
read from the **live def dump** (`<LocalLow>\DefDump\defs\`, captured
2026-08-14T08:20:26Z, game 1.6.4871 rev591), from vanilla XML on disk, or from an
installed mod's own XML — each is cited at the point of use._

🔴 **The file keeps the name `precept_the_unearned.md`.** "The Unearned" survives
as the doctrine's name because it is the only phrasing that carries **both** halves
of the owner's brief in one word — the beggar's unearned share *and* the free
market's premise that a share must be earned. "Mendicancy" names only the beggar;
"the Outstretched Hand" names only the gesture. No rename.

---

## 🔴 The three answers you need before reading further

**1 · The refusal hook is LEGAL.** `CharityRefused_Beggars` is a real
`HistoryEventDef` and the beggar quest records it on the turn-away path. The
"delight on refusal" half is authorable exactly as the owner asked. Evidence in §2.

**2 · But "declining a beggar quest" is not a thing the game has.** The beggar
quest is `<autoAccept>true</autoAccept>` — there is **no accept/decline button.**
Refusal is behavioural: you let the timer run out and they walk off empty-handed.
This is *better* than what was asked for, because the delight then fires off a
choice the player makes on the map rather than a dialog they click through.

**3 · 🔴 A `FactionDef` CANNOT list precepts, so this needs a new `MemeDef`.**
`Assembly-CSharp.dll` exposes exactly seven ideo fields on `FactionDef` —
`ideoName`, `fixedIdeo`, `forcedMemes`, `requiredMemes`, `deityPresets`,
`structureMemeWeights`, `requiredPreceptsOnly`. There is **no** `forcedPrecepts`,
no `requiredPrecepts`, no precept list of any kind. `IdeoPresetDef` is memes-only
too. **The only way to guarantee a precept on any ideoligion is a meme that forces
it via `requireOne`.** So the deliverable is a meme *and* an issue *and* a precept,
not a precept alone. `faction_religions_spec.md` entry 5 already discovered this
from the other end; this is the same constraint stated as a rule.

> Verified: `strings -a "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll"`,
> exact-match on each candidate field name, 2026-08-14.

---

## 🔴 The visibility problem, stated honestly and near the top

`faction_religions_spec.md` is disciplined around **"NPC religion rarely surfaces
in play"**, which is still an *unmeasured premise* (its red block; the `jawa/ideo_of`
`otherOnMap` counter is built but unfired). This spec inherits that uncertainty and
does not pretend otherwise.

**The two bindings are not equal, and the owner's "delight" lives in exactly one of
them.**

| binding | what it does | does the owner feel it? |
|---|---|---|
| **(a) NPC — Hutt Cartel** | Hutt pawns carry the precept. Their moods move on events *on their own maps*, which the player never loads. On **our** map a Hutt visitor's mood is invisible unless clicked. | **Barely. It is fiction and colour.** |
| **(b) Player-available — an `IdeoPresetDef` + the meme in the ideoligion editor** | A colonist of this faith gets a **positive** mood memory when the beggars leave empty-handed, and a bigger one when they are taken. Refusing becomes a real decision with a real payoff, felt at the keyboard. | **Yes. This is the whole delight.** |

⇒ **Spec once, ship both. Build (b) first.** (a) costs one line in a `FactionDef`
once (b)'s defs exist, so there is no reason to skip it — but if only one ships,
ship (b).

⚠️ **Do NOT assign this to the Jawa faith.** Section 12 of
`faction_religions_spec.md` is the owner's and is deliberately empty. Making the
meme *available* to the player's ideoligion is the deliverable; **choosing** it is
the owner's. Note that `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\jawa_xenotype_and_religion.md`
§"One does not beg!" (owner, 2026-08-07) already asks for this doctrine on the Jawa
— which is precisely why (b) must exist. This file gives the owner the parts; it
does not fit them.

---

## 1 · Which faction — **the Hutt Cartel (2), the Reckoning of Debts**

**Decided. Blackstar Company is the weaker variant, specified in §7.**

| | Hutt Cartel (2) | Blackstar Company (10) |
|---|---|---|
| taboo already on file | **forgiving a debt** | double-booking a contract |
| the doctrine restated | a beggar asks to be forgiven a debt he never contracted — the taboo made flesh | a beggar has nothing to sign with |
| free-market memes already assigned | `VME_Structure_Corporate` · `VME_Trader` · `Individualist` — **all three, already** | `Individualist` only |
| existing `Charity` line in the spec | *"(none — see the constraint above)"* — **an acknowledged hole this fills** | `Charity_Worthwhile` — ⚠️ **the fiction wanted "disapproved"; the spec says so** |
| slavery position | `Slavery_Acceptable` | `Slavery_Disapproved` — *"a slave cannot sign"* |

**Why the Hutts win, in one line each:**

1. **Their fiction already asserts it and their encoding already failed to.**
   `faction_religions.md` entry 2 says *"charity: **abhorrent**"*;
   `faction_religions_spec.md` constraint 2 says it "cannot be written". This is
   the thing that could not be written.
2. **They already hold every meme the free-market half needs.** Zero new
   worldbuilding, zero new memes for that half — see §5.
3. **It is the only doctrine that makes their slavery position *mean* something.**
   `Slavery_Acceptable` is flagged in the spec as *"⚠️ inert — 0 comps"*, and that
   flag is correct: the dump shows `Slavery_Acceptable` with `comps: []`,
   `associatedMemes: []`, `conflictingMemes: []`. The Cartel's central practice
   currently generates no mood, no development points and no refusal. **The Unearned
   is what gives the Cartel a slavery doctrine with a body.**
4. **Blackstar's slavery position contradicts it.** *A slave cannot sign* is a good
   line and it is the opposite of *those who cannot take care of themselves should
   be owned*. Putting both on one faction would be incoherent.

---

## 2 · Does refusing a beggar fire something? — **YES. Question closed.**

### The events, verbatim

> `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Ideology\Defs\PreceptDefs\Precepts_Charity.xml`, read 2026-08-14
> ```xml
> <HistoryEventDef><defName>CharityRefused_Beggars</defName>
>   <label>beggars refused</label></HistoryEventDef>
> <HistoryEventDef><defName>CharityRefused_Beggars_Betrayed</defName>
>   <label>beggars betrayed</label></HistoryEventDef>
> <HistoryEventDef><defName>CharityFulfilled_Beggars</defName>
>   <label>beggars helped</label></HistoryEventDef>
> ```

### 🔴 The live beggar quest is NOT the vanilla one

**Better Beggars (Continued)** (`mlie.betterbeggars`, WS `3006899215`, **active** —
`ModsConfig.xml` line 71) `PatchOperationReplace`s the storyteller's
`GiveQuest_Beggars` with its own. The quest that actually fires in this campaign is
one of:

| defName | source file | note |
|---|---|---|
| `Beggars_WantThing_Vanilla` | `...\294100\3006899215\1.6\Defs\QuestScriptDefs\Script_Beggars_Vanilla.xml` | the everyday one |
| `Beggars_WantThing_Drugs` | `...\Script_Beggars_Drugs.xml` | 60-day on-cycle |
| `Beggars_Chased` | `...\Script_Beggars_Chased.xml` | `baseChance 1.0`, `minRefireDays 30` |
| `Beggars_DelayedReward` | `...\Script_Beggars_DelayedReward.xml` | `defaultHidden true` |

**Naming vanilla `Beggars` in any patch would target a quest the storyteller no
longer hands out.** Better Beggars ships no `HistoryEventDef`, no `IssueDef`, no
`PreceptDef`, no `ThoughtDef` — it re-records the **stock** events, so a comp
written against `CharityRefused_Beggars` covers stock *and* all three modded
variants unchanged.

> `...\3006899215\1.6\Assemblies\BetterBeggars.dll`, `strings -a`, and the mod's
> published source (`QuestNode_Root_Beggars_WantThing_Vanilla.cs`):
> ```csharp
> quest.Delay(60000, delegate {
>     quest.Leave(pawns, null, false, false);
>     quest.RecordHistoryEvent(HistoryEventDefOf.CharityRefused_Beggars);
> ```
> The `RecordHistoryEvent` sits **outside** the `AnyColonistWithCharityPrecept`
> filter — the event fires whether or not anyone approves of charity.

### The event map

| player action | event raised | confidence |
|---|---|---|
| beggars time out and leave with nothing | `CharityRefused_Beggars` | **VERIFIED** (source above) |
| beggars given what they asked for | `CharityFulfilled_Beggars` | **VERIFIED** |
| beggars harmed / attacked | `CharityRefused_Beggars_Betrayed` | **VERIFIED** |
| beggars **arrested** (→ enslaved) | `CharityRefused_Beggars_Betrayed` | ⚠️ **UNVERIFIED — see below** |

### ⚠️ The one open question in this spec

**Does *arresting* a beggar raise `CharityRefused_Beggars_Betrayed`, or only
killing one?** The assembly carries both signals — `beggars.Arrested` and
`beggars.Killed` (`strings -a -el`) — and Better Beggars carries a distinct
`BeggarArrested_BadThought` branch, so an arrest is plainly tracked. But the quest
letter reads *"[travelers] have been **harmed**"*, and I did not read the arrest
branch's `RecordHistoryEvent` call. **Do not assert the arrest→Betrayed link.**
Filed for BRIDGE in §9 as a two-minute live measurement.

**Design consequence if it comes back negative:** §4's arrest reward loses its
beggar-specific event and falls back to the generic `EnslavedPrisonerNotPreviouslyEnslaved`.
The doctrine still works; it just stops distinguishing *this* slave from any other.
**Nothing else in the spec changes.** The turn-away half — the owner's primary ask —
is unaffected either way.

### ⚠️ A second, narrower trap

On the **`Beggars_Chased`** variant only, the mod wraps the betrayal record inside
the filter:

```csharp
quest.AnyColonistWithCharityPrecept(delegate {
    quest.RecordHistoryEvent(HistoryEventDefOf.CharityRefused_Beggars_Betrayed); }, ...)
```

`QuestPart_Filter_AnyColonistWithCharityPrecept` is a **vanilla** class
(present in `Assembly-CSharp.dll`). A colony that holds **The Unearned and no
`Charity_*` precept** has nobody who approves of charity — so on that one variant
the Betrayed event is **skipped entirely**. The turn-away path on the other two
variants is unaffected. Mitigation: none needed for v1; note it so nobody debugs it
twice.

---

## 3 · Is there an issue to hang this on? — **No. A new `IssueDef` is required.**

**Confirmed against the live dump — 220 `IssueDef`s across 21 mods:**

| queried | result |
|---|---|
| `Beggars` · `Alms` · `Begging` · `Mendicancy` | **ABSENT — all four** |
| `Ownership` · `Property` · `Wealth` · `Debt` · `Contract` · `Market` | **ABSENT — all six** |
| `Charity` | exists, Ideology, `allowMultiplePrecepts: false` |
| `Slavery` | exists, Ideology, 8 positions |
| `Trade` (mlie) · `VME_Trading` · `VME_TradingPrice` | exist |
| `GarryFlowers_Slave_Opinion` / `_Relations` / `_Gatherings` | exist, More Slavery Stuff |

**`Charity` has no negative position — re-confirmed two independent ways.**
(i) exactly three precepts carry `issue: Charity` in all 685 dumped precepts;
(ii) `approvesOfCharity: true` is set on exactly those three and on nothing else in
the build. There is no `Charity_Contemptible`, and `approvesOfCharity: false` is the
C# default on the other 682 precepts — so **setting it false asserts nothing.**

⇒ **A custom `IssueDef` is the honest answer, and it is a clean one.** The issue is
`Jawa_Begging`, and it is *not* the negative pole of `Charity` — it is a different
question. `Charity` asks *do we help?*; `Jawa_Begging` asks *what is a person who
asks?* An ideoligion may hold both and be coherently vile.

⚠️ **`Charity`'s `conflictingMemes` in the live game are `[Supremacist,
PainIsVirtue, Trader]` — three, not the two in the vanilla XML.** *Precepts and
Memes (Continued)* patches `Trader` in. **The dump wins over vanilla XML, again**
(same trap as the `Horaxian` → `AM_Horaxian` style swap already in
`infrastructure/state/queue/VISION.md`). Practical effect: the mlie `Trader` meme
already hard-excludes all charity — it is the closest thing the build has to an
anti-charity statement, and it is a *meme exclusion*, not a precept.

---

## 4 · Enslaving a beggar — **not distinguishable at the def level. Say so.**

The only enslavement events in the build are `EnslavedPrisoner` and
`EnslavedPrisonerNotPreviouslyEnslaved`
(`...\Data\Ideology\Defs\PreceptDefs\Precepts_Slavery.xml`, lines 12 and 17), plus
`SoldSlave`. **None carries the victim's provenance.** Enslaving a beggar fires
exactly what enslaving a raider fires.

**So the honest answer is: the precept can only reward slavery in general — with
one exception, and the exception is the whole design.**

`CharityRefused_Beggars_Betrayed` **is** beggar-specific, and it fires on the path
that *begins* an enslavement (harm → down → arrest → convert). So the doctrine gets
its beggar-specific delight from the **taking**, and its general delight from the
**owning**, and the two stack in the same afternoon:

| moment | event | who feels it | comp |
|---|---|---|---|
| the beggars are turned away | `CharityRefused_Beggars` | everyone of this ideo | `PreceptComp_KnowsMemoryThought` |
| the beggars are taken | `CharityRefused_Beggars_Betrayed` ⚠️*(arrest link unverified)* | everyone of this ideo | `PreceptComp_KnowsMemoryThought` |
| the prisoner becomes property | `EnslavedPrisonerNotPreviouslyEnslaved` | the doer, then everyone | comes from the **`Slavery`** precept, not this one |
| we gave in and paid them | `CharityFulfilled_Beggars` | everyone — **a penalty** | `PreceptComp_KnowsMemoryThought` |

⚠️ **Do not put an enslavement comp on this precept.** `Slavery` is a separate issue
with `allowMultiplePrecepts: false`, and the slavery precepts already own those
events. Duplicating them stacks two memories for one act.

---

## 5 · The free-market half — **reuse. Author nothing.**

**Checked all 136 `MemeDef`s.** No meme in this build carries free-market,
libertarian or anti-charity doctrine as such. But three installed memes carry it
between them, and **the Hutt Cartel already has all three**:

| defName | source | what it contributes | forces |
|---|---|---|---|
| `VME_Structure_Corporate` | `vanillaexpanded.vmemese` | the theology: *"No Gods or Kings should be worshipped, only man and his unslakable desire for wealth. Colonies should be managed like companies."* `deityCount 0` | nothing — payload is `Apparel_CollarShirt` + the `VME_Corporate` style |
| `VME_Trader` | `vanillaexpanded.vmemese` | *"With wealth comes power, generating profit is an important part of life."* | `VME_TradingPrice_Improved` · `VME_Trading_Required` · `VME_Expectations_High`, **all three**, plus ritual `VME_TradingFairPrecept` |
| `Individualist` | `ludeon.rimworld.ideology` | *"Each person is a free individual… Nobody should be made to conform."* | nothing; `modExtensions` → preferred trait `Recluse` |

⇒ **The free-market half is already shipped and already assigned.** The new meme
carries **only** the doctrine that was missing. That is the correct scope.

**Optional, cheap, and recommended for the player build (b):** add `Trader`
(`mlie.preceptsandmemes`) — it forces `TradingRespected`/`TradingHonored`
(`TradePriceImprovement +0.10/+0.20` against `WorkSpeedGlobal −0.09/−0.18`, a real
tradeoff), carries `agreeableTraits: [Greedy]`, and **already conflicts with every
`Charity_*` precept**, which enforces the doctrine's negative half for free.
⚠️ `Trader` has `exclusionTags: [TraderRaider]` — it cannot sit with `Raider`.
Irrelevant for the Hutts; relevant if the owner ever wants this on a raider faith.

> ⚠️ **A `strings -a` miss worth knowing.** `agreeableTraits` returns **zero** exact
> matches in `Assembly-CSharp.dll` while `disagreeableTraits` returns one — because
> .NET's `#Strings` metadata heap **shares suffixes**, so the shorter name has no
> record of its own. It is a real vanilla `MemeDef` field; the dump shows it
> populated on `Trader`. **An absent `strings` reading is not an absent field.**
> Same family as the ascii/unicode lesson, different mechanism.

---

## 6 · The defs to author — Hutt Cartel binding

**Mod:** `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\` (`mandrake.jawa.patches`).
**Prefix:** `Jawa_`, matching `Jawa_TheClaim`, `Jawa_SaltCrust`, `Jawa_GroundHulk`.
**File:** `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Defs\PreceptDefs\Precepts_TheUnearned.xml`

⚠️ **`MayRequire`, exactly twice.** Every def referenced below is vanilla Core or
Ideology **except the two `conflictingMemes` entries in §6.2**, which come from
mods. A `conflictingMemes` entry naming an absent def is a cross-reference error at
load, so those two `<li>`s carry a per-element guard:

```xml
<li MayRequire="vanillaexpanded.vmemese">VME_Egalitarian</li>
<li MayRequire="mlie.preceptsandmemes">Altruism</li>
```

Everything else is unguarded. `MayRequire Ludeon.RimWorld.Ideology` on the file as
a whole is correct and sufficient — the mod is otherwise Ideology-free.

🔴 **Icons: reuse, do not commission.** Vanilla textures live in AssetBundles and
`Data\...\Textures\` does not exist on disk, so a bespoke `iconPath` needs art we
would have to ship. *More Slavery Stuff* proves the reuse route works — its three
issues all point at `UI/Issues/Slavery`. Use `UI/Issues/Charity` for the issue and
`UI/Memes/Trader` for the meme. **Zero art cost.** Revisit only if the owner wants
a distinct symbol.

### 6.1 The issue

```xml
<IssueDef>
  <defName>Jawa_Begging</defName>
  <label>begging</label>
  <iconPath>UI/Issues/Charity</iconPath>
</IssueDef>
```

Field shape verified against vanilla `<IssueDef><defName>Charity</defName>…` and
against all three `GarryFlowers_Slave_*` issues. `allowMultiplePrecepts` defaults
false, which is what we want.

### 6.2 The precept — `Jawa_Begging_Contemptible`

```xml
<PreceptDef>
  <defName>Jawa_Begging_Contemptible</defName>
  <issue>Jawa_Begging</issue>
  <label>contemptible</label>
  <description>One who begs has thrown away his hands. He has no claim on what
    another earned, and no standing to make one. To turn him away is
    housekeeping; to put him to work is mercy.</description>
  <impact>High</impact>
  <displayOrderInIssue>0</displayOrderInIssue>
  <displayOrderInImpact>1000</displayOrderInImpact>
  <defaultSelectionWeight>0</defaultSelectionWeight>
  <associatedMemes>
    <li>Individualist</li>
    <li>Supremacist</li>
  </associatedMemes>
  <conflictingMemes>
    <li MayRequire="vanillaexpanded.vmemese">VME_Egalitarian</li>
    <li MayRequire="mlie.preceptsandmemes">Altruism</li>
  </conflictingMemes>
  <comps>
    <li Class="PreceptComp_KnowsMemoryThought">
      <eventDef>CharityRefused_Beggars</eventDef>
      <thought>Jawa_BeggarsRefused_Contemptible</thought>
      <description>Beggars sent away</description>
    </li>
    <li Class="PreceptComp_KnowsMemoryThought">
      <eventDef>CharityRefused_Beggars_Betrayed</eventDef>
      <thought>Jawa_BeggarsTaken_Contemptible</thought>
      <removesThought>Jawa_BeggarsRefused_Contemptible</removesThought>
      <description>Beggars taken</description>
    </li>
    <li Class="PreceptComp_KnowsMemoryThought">
      <eventDef>CharityFulfilled_Beggars</eventDef>
      <thought>Jawa_BeggarsPaid_Contemptible</thought>
      <description>Gave alms to beggars</description>
    </li>
    <li Class="PreceptComp_DevelopmentPoints">
      <eventDef>CharityRefused_Beggars</eventDef>
      <eventLabel>sent beggars away</eventLabel>
      <points>2</points>
    </li>
  </comps>
</PreceptDef>
```

**Every field above is attested.** `PreceptComp_KnowsMemoryThought`,
`PreceptComp_DevelopmentPoints`, `removesThought`, `description`, `eventLabel`,
`points`, `displayOrderInIssue`, `displayOrderInImpact`, `defaultSelectionWeight`,
`associatedMemes`, `conflictingMemes`, `impact` — all read from
`Precepts_Charity.xml` (`Charity_Essential`, lines 128–216) and
`Precepts_Slavery.xml` (`Slavery_Honorable`, lines 179–243), 2026-08-14.

⚠️ **`defaultSelectionWeight: 0` is mandatory.** A non-zero weight leaks the
precept into randomly generated ideoligions across the whole world. Every one of
*More Slavery Stuff*'s nine precepts sets it to 0 for the same reason.

⚠️ **`PreceptComp_KnowsMemoryThought`, not `PreceptComp_SelfTookMemoryThought`.**
Nobody "does" a refusal — it is a colony-level event with no doer. Vanilla's three
`Charity_*` precepts use `KnowsMemoryThought` for every `CharityRefused_*` binding
and never `SelfTook`. Copy that, or the thought lands on nobody.

**The comp vocabulary.** `Assembly-CSharp.dll` declares **16** whole-line
`PreceptComp` types — 1 abstract base and 15 subclasses. Twelve more are added by
mods, **all but one active** (Alpha Memes 2, VE Memes 3, More Precepts 3, VVE 3,
AP Hunting 1; `Xenomorphtype.PreceptComp_WitnessedAction` is on disk but not in
`ModsConfig.xml`). ⚠️ `PreceptComp_Apparel` and `PreceptComp_Thought` are used in no
XML anywhere and appear to be abstract bases — **do not put them in `Class=`**.
`PreceptComp_GoodwillSituation` has zero usages on this machine and its child
element is **UNVERIFIED**.

The four that matter here — *uses counted across vanilla `Data\` XML only*, not the
whole build:

| class | vanilla uses | what it needs | use it for |
|---|---|---|---|
| `PreceptComp_KnowsMemoryThought` | 188 | `eventDef` + `thought`; optional `description`, `removesThought`, `onlyForNonSlaves`, `doerMustBeMyIdeo` | **everyone reacts to a thing that happened** ← ours |
| `PreceptComp_SituationalThought` | 151 | `thought` + optional `description` / `thoughtStageDescriptions` / `tooltipShowMoodRange`; **no event** | a standing condition (e.g. "slaves in colony") |
| `PreceptComp_SelfTookMemoryThought` | 99 | `eventDef` + `thought`; optional `description`, `onlyForNonSlaves` | the pawn who performed the act |
| `PreceptComp_DevelopmentPoints` | 21 | `eventDef` + `points`; optional `eventLabel` | ideoligion development on the player's ideo |

`eventDef` and `thought` are present on **100%** of the uses of the comps that take
them — treat both as required. Everything else is optional.

🔴 **`eventDefs` (plural) does not exist** — zero occurrences in vanilla XML, zero
across all 1,246 workshop mods, and no string in the assembly's `#Strings` heap
*ends* in `eventDefs` (the suffix test, which is the one that counts — see the
`agreeableTraits` note in §5). **To react to N events you write N `<li>` entries.**

`PreceptComp_UnwillingToDo` (31 vanilla uses) also takes a singular `eventDef` —
**it is the wrong tool here**, because there is no "gave alms" event a pawn performs
that it could refuse.

⭐ **Worth knowing for later, not used here:**
`VanillaMemesExpanded.PreceptComp_DisableIncident` (active) can switch an incident
off from a precept — note its child element is a **capital-I `<Incident>`**. The
Unearned wants *more* beggars, not fewer, so we do not use it; but it is the tool if
the owner ever wants a faith that never sees them.

### 6.3 The thoughts

```xml
<ThoughtDef Abstract="True" Name="Jawa_UnearnedThoughtBase">
  <durationDays>8</durationDays>
</ThoughtDef>

<ThoughtDef ParentName="Jawa_UnearnedThoughtBase">
  <defName>Jawa_BeggarsRefused_Contemptible</defName>
  <stages>
    <li>
      <label>sent the beggars away</label>
      <description>They came with their hands out and left with them empty.
        The ledger is clean and the world is in order.</description>
      <baseMoodEffect>6</baseMoodEffect>
    </li>
  </stages>
</ThoughtDef>

<ThoughtDef ParentName="Jawa_UnearnedThoughtBase">
  <defName>Jawa_BeggarsTaken_Contemptible</defName>
  <stages>
    <li>
      <label>beggars properly owned</label>
      <description>They could not keep themselves. Now someone else will,
        and they will earn it. Nothing has been wasted.</description>
      <baseMoodEffect>10</baseMoodEffect>
    </li>
  </stages>
</ThoughtDef>

<ThoughtDef ParentName="Jawa_UnearnedThoughtBase">
  <defName>Jawa_BeggarsPaid_Contemptible</defName>
  <stages>
    <li>
      <label>gave alms</label>
      <description>We paid someone for nothing. Whatever we bought,
        it was not worth what it cost us.</description>
      <baseMoodEffect>-8</baseMoodEffect>
    </li>
  </stages>
</ThoughtDef>
```

`durationDays 8` and the `stages`/`baseMoodEffect` shape are copied from vanilla's
`CharityBase` and `CharityRefused_Essential_Beggars` (`-8`, same file). **The
magnitudes are deliberately the mirror of vanilla's charity numbers**, so a
colonist who holds The Unearned feels about refusing exactly what a
`Charity_Essential` colonist feels, inverted. `+10` on the taking is one step above
that: the doctrine's peak.

### 6.4 The meme — `Jawa_Meme_TheUnearned`

```xml
<MemeDef>
  <defName>Jawa_Meme_TheUnearned</defName>
  <label>the unearned</label>
  <description>A share must be earned. One who asks for what he did not earn has
    confessed he cannot keep himself, and one who cannot keep himself is better
    kept by someone who can.</description>
  <category>Normal</category>
  <impact>2</impact>
  <iconPath>UI/Memes/Trader</iconPath>
  <requireOne>
    <li><li>Jawa_Begging_Contemptible</li></li>
  </requireOne>
  <exclusionTags>
    <li>Jawa_Mendicancy</li>
  </exclusionTags>
</MemeDef>
```

⚠️ **`requireOne` is a list-of-lists** — outer entries are ANDed, inner entries are
ORed. Verified against `VME_Trader`
(`requireOne: [[VME_TradingPrice_Improved], [VME_Trading_Required], [VME_Expectations_High]]`,
all three forced) and `Trader` (`requireOne: [[TradingRespected, TradingHonored]]`,
one of two). One group with one member = "always exactly this precept". **Neither
`requiredPrecepts` nor `addedPrecepts` exists on `MemeDef`;** do not write them.

⚠️ **`impact: 2` is an integer in this build, not a string.** All 136 dumped memes
use 0–3, with 0 reserved for the 35 structure memes.

⚠️ **The meme forces the precept but does not override `conflictingMemes`.** Keep
`VME_Egalitarian` and `Altruism` off any ideoligion that takes this. Neither is on
the Hutts.

### 6.5 The FactionDef change

One line, in whichever file CREATE lands the eleven ideo blocks in:

```xml
<forcedMemes>
  <li>VME_Structure_Corporate</li>
  <li>VME_Trader</li>
  <li>Individualist</li>
  <li>Guilty</li>
  <li>AM_Gladiator</li>
  <li>Jawa_Meme_TheUnearned</li>   <!-- new -->
</forcedMemes>
```

⚠️ **Entry 2 in `faction_religions_spec.md` sets `requiredPreceptsOnly` ❌ (false)**
— deliberately, "let the game add colour". That is still right: `requireOne` forces
our precept regardless of that flag. **Do not flip it to true** to "make sure" —
that would strip the Cartel's incidental precepts and is a different decision.

⇒ **Update `faction_religions_spec.md` entry 2's precept table**: the row
`| Charity | *(none — see the constraint above)* | ⚠️ not encodable; Guilty carries it |`
becomes
`| Jawa_Begging | Jawa_Begging_Contemptible | ⭐ the ledger applied to persons; forced by Jawa_Meme_TheUnearned |`.
That edit is **not** made by this file — it is queued in §9.

---

## 7 · Blackstar Company — the weaker variant, and it is genuinely weaker

**Ship it only if the owner asks.** A second position on the same issue:

```xml
<PreceptDef>
  <defName>Jawa_Begging_Distasteful</defName>
  <issue>Jawa_Begging</issue>
  <label>distasteful</label>
  <description>A man who begs has nothing to offer and nothing to sign.
    We do not despise him. We simply have no business with him.</description>
  <impact>Low</impact>
  <displayOrderInIssue>10</displayOrderInIssue>
  <defaultSelectionWeight>0</defaultSelectionWeight>
  <comps>
    <li Class="PreceptComp_KnowsMemoryThought">
      <eventDef>CharityFulfilled_Beggars</eventDef>
      <thought>Jawa_BeggarsPaid_Distasteful</thought>
      <description>Gave alms to beggars</description>
    </li>
  </comps>
</PreceptDef>
```

`Jawa_BeggarsPaid_Distasteful`: one stage, `baseMoodEffect -3`.

**Why weaker, honestly:** it carries **no delight**, only a small penalty for
giving in — because Blackstar holds `Slavery_Disapproved` (*"a slave cannot sign"*)
and rewarding the taking would contradict their own contract doctrine. It fixes the
spec's flagged *"⚠️ the 'disapproved' the fiction wanted is not encodable"* on entry
10 and does nothing else. **It needs its own meme to be forced** onto an NPC
faction, per §"three answers" point 3 — which is a whole meme for one −3 mood. **My
recommendation: skip it, and give Blackstar the note in prose instead.**

---

## 8 · Does the player notice, and does it change the campaign?

**For the NPC binding (a): barely, and I will not pretend otherwise.** A Hutt
pawn's mood memory about beggars refused on a map the player never visits is
invisible. The one place it could surface is a Hutt visitor standing in your colony
while a beggar quest runs — a coincidence, not a mechanic. **Its value is that the
Cartel's dossier stops containing a line the engine contradicts**, which matters to
the eleven-religion set's internal honesty and to nothing else. If `jawa/ideo_of`
comes back `otherOnMap ≈ 0`, this binding is decoration, exactly as the spec's red
block predicts.

**For the player binding (b): yes, and it is the good kind of change.** RimWorld's
beggar quest is normally a small tax you either pay or eat a mood hit for. Under The
Unearned it inverts into a *recurring free reward for cruelty*: every beggar event
becomes +6 colony-wide for doing nothing, +10 and a prisoner for doing something
worse, and −8 if you go soft. With **Better Beggars** already tuning frequency
upward and adding a drugs variant and a chased variant, that is not a rare
occurrence — it is a rhythm. **The player stops reading "beggars arrive" as a bill
and starts reading it as a delivery.** That is a real change in how the campaign
plays, it is entirely diegetic, and it is the owner's stated design intent from
2026-08-07 finally having a mechanism.

⚠️ **Balance note, flagged not solved.** +6 colony-wide on a repeating quest with no
cost is strong. If it proves too strong, cut `Jawa_BeggarsRefused_Contemptible` to
`+4` and leave the taking at `+10` — the doctrine reads the same and the free money
shrinks. Do not fix this before it is seen once.

---

## 9 · Filed for other seats

**BRIDGE** — the one measurement this spec needs, ~2 min on any live map:
- **Does arresting a beggar raise `CharityRefused_Beggars_Betrayed`?** Run a beggar
  quest, arrest one, read the history. Both `beggars.Arrested` and `beggars.Killed`
  signals exist; which raises the event is unread. §2 explains what changes either
  way — the answer is not blocking, only clarifying.
- Standing ask, unchanged: `jawa/ideo_of` **`otherOnMap`**. This spec's binding (a)
  is worth exactly what that number says it is.

**CREATE** — `infrastructure/state/queue/CREATE.md`, `[v2]`:
- Author `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Defs\PreceptDefs\Precepts_TheUnearned.xml`
  from §6. Every defName, field and value is in this file; nothing needs inventing.
  Reuse `UI/Issues/Charity` and `UI/Memes/Trader` — **no art required.**
- Add `Jawa_Meme_TheUnearned` to the Hutt Cartel's `forcedMemes` when the eleven
  ideo blocks are written (§6.5). Do not flip `requiredPreceptsOnly`.
- 🔴 **Never target the vanilla `Beggars` QuestScriptDef.** Better Beggars replaces
  it in the storyteller; the live quests are `Beggars_WantThing_Vanilla`,
  `Beggars_WantThing_Drugs`, `Beggars_Chased`, `Beggars_DelayedReward` (§2).

**VISION (me)** — after CREATE lands the defs:
- Update `faction_religions_spec.md` entry 2's precept table per §6.5, and soften
  its constraint 2 from *"cannot be written"* to *"cannot be written **as a Charity
  precept**"* — which is what is actually true.
- Entry 10's `Charity_Worthwhile` row keeps its ⚠️; §7 explains why I am not
  spending a meme on it.

---

_Sources, all read 2026-08-14: live def dump `<LocalLow>\DefDump\defs\{PreceptDef,
MemeDef,IssueDef,HistoryEventDef,QuestScriptDef,IncidentDef}.json` (game 1.6.4871
rev591) · `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Ideology\Defs\PreceptDefs\{Precepts_Charity,Precepts_Slavery}.xml`
· `...\Data\Ideology\Defs\QuestScriptDefs\Script_Beggars.xml` ·
`...\Managed\Assembly-CSharp.dll` (`strings -a` and `strings -a -el`) ·
`...\workshop\content\294100\3006899215\` (Better Beggars, `mlie.betterbeggars`, active) ·
`...\workshop\content\294100\2896845138\` (More Slavery Stuff, `garryflowers.moreslaverystuff`, active) ·
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\data\ideology_palette.md`._

⚠️ **"More Slavery Stuff (Continued)" WS `3530586159` is NOT installed** — a grep of
all 1246 workshop `About.xml` files matches only the original `2896845138`. Several
design docs cite `3530586159` as adopted. **Filed as `[?]` for PROJECT:** the
`GarryFlowers_` defs this campaign relies on all come from the original, which is
active, so nothing is broken — but the ID in the docs is wrong.
