---
name: rimworld-quests
description: Design, author, validate and debug RimWorld quests. A quest is a QuestScriptDef whose node tree runs ONCE at offer time and leaves QuestParts that talk only by signal string, so most quest bugs are silent - a renamed storeAs kills every inSignal on it, one unresolvable [symbol] blanks the whole description rather than degrading, and a def with no firing route loads clean and never occurs. Covers the prose spec that makes a quest worth playing and how each part of it maps onto def fields, the ~300 QuestNode vocabulary and the 30 Util_ sub-scripts, slate vars and $ syntax, rule packs and grammar suffixes, the four ways a quest gets offered, when a custom C# node is genuinely needed, and an offline validator calibrated against all 151 shipped quests. Use for any QuestScriptDef, QuestNode, quest reward, quest text, quest that never fires or never completes, or a request to design a quest at all.
---

# RimWorld quests

Quest bugs do not throw. They blank a description, or leave a branch that never
arms, or produce a def that loads, appears in the def dump, and simply never
occurs. Every check in `scripts/validate_quest.py` exists because one of those
cost somebody a 20-30 minute game load.

## 0. Which job are you on

| you want to | read |
|---|---|
| decide whether this quest is worth building | §1 spec, §2 stakes — write the spec *before* the def |
| write the def | §3 shape · §4 slate · §5 text · §6 signals |
| make it actually appear in a game | §7 firing routes |
| find out why it broke | §8 validator, then `references/mod_patterns.md` §6 failure table |
| decide XML vs C# | §9 |
| know what a node/field/suffix really does | `references/vanilla_corpus.md` — the full inventory |

🔴 **Never guess a node class, a field or a signal suffix.** There are ~300
`QuestNode_*` types and the near-misses are real (`QuestNode_GetSitePartDefsByTagsAndFaction`
vs `QuestNode_GetDefaultSitePartsParams`). Copy names out of a shipped def; the
validator checks every one against `Assembly-CSharp.dll`.

---

## 1. The model, which reorganises everything else

A quest is **generated once, at offer time.** The node tree runs, fills a
**slate** (a string→object dict of generation-time variables), and appends
**`QuestPart`** objects to the live quest. Then the tree is gone. Only the
`QuestParts` tick during play, and they talk to each other **only by signal
string**.

```
QuestScriptDef                     <- the def you author
 ├─ root = QuestNode_Sequence      <- tree, runs ONCE at generation
 │    ├─ QuestNode_GetMap          <- writes slate var  map
 │    ├─ QuestNode_Delay           <- EMITS a QuestPart that ticks in play
 │    └─ QuestNode_End             <- EMITS QuestPart_QuestEnd
 ├─ questNameRules / questDescriptionRules   <- grammar, resolved at the end
 └─ root-level fields                        <- when/whether it may be offered
```

Three consequences you will otherwise learn the expensive way:

- **You never name a `QuestPart` in XML.** All 249 of them are built from C# in
  `QuestNode.RunInt()`. A new `QuestPart` requires a C# `QuestNode` to emit it.
- **Success and failure are structural, not computed.** There is no evaluation
  step. You place one `QuestNode_End` per terminal branch, hard-code its
  `<outcome>`, and whichever signal arrives first wins.
- **Nothing declares a contract.** A node reads `map`, `asker`, `rewardValue`
  because that is the conventional name, not because anything enforces it. Read
  the consumer before you name a variable.

---

## 2. Write the spec before the def

A def is the second half of the work. The first half is six lines of prose, and
every line has a field it lands on. Fill this in first; if a row is blank the
quest is not ready to build.

| the spec line | the question it answers | where it lands in the def |
|---|---|---|
| **The ask** | what does the colony have to *do* | the node tree - the site, the pawns, the timer |
| **The reason** | why does the colony care, *without mentioning the reward* | `questDescriptionRules` - first sentence |
| **The choice** | which decision has two defensible answers | a `QuestNode_Signal` per branch, one `End` each |
| **The failure state** | how is it lost, and is losing survivable | `QuestNode_End` with `<outcome>Fail</outcome>` + `failedOrExpiredHistoryEvent` |
| **The reward** | what kind, and is it proportional to the challenge | `rewardValue` slate var + `QuestNode_GiveRewards`, or a specific `AddItemsReward` |
| **The deadline** | how long, and what does the player see | `expireDaysRange` (offer window) and `QuestNode_Delay`/`WorldObjectTimeout` with `isQuestTimeout` (completion) |

**Ten yes/no questions. A "no" is a rewrite, not a note.**

1. Can I state in one sentence why the colony cares, without naming the reward?
2. Is there a decision with at least two defensible answers?
3. Does something *later* acknowledge which answer was given?
4. Can it be failed, and is failing survivable? (A quest that cannot be lost has
   no stakes; one that ends the run gets save-scummed.)
5. Is the reward proportional to the challenge actually imposed?
6. Is the deadline real, enforced, and shown? Do not fake urgency you will not
   enforce.
7. Can it be finished in one sitting?
8. Does it use only mechanics the game already has? *(A quest that needs a new
   subsystem is a mod, not a quest.)*
9. Are the ask, the reward and the deadline each findable in one glance?
10. Has the def taken one of the four firing routes (§7), and does every
    conditional grammar symbol have a fallback (§5)?

⚠️ **Fit the quest to the colony that will get it.** Ludeon shipped a whole wave
of 1.1 fixes that were one idea — no mech clusters at low points, no Empire asker
for hospitality under 240 points. Use `rootMinPoints`, `rootMinProgressScore`,
`rootEarliestDay` rather than letting the player discover the mismatch. And
`minRefireDays` on anything with a memorable premise: the second telling cheapens
the first.

Fuller design rules, with sources: `references/design_and_community.md` Part B.

---

## 3. The shape of a def

Smallest tree that generates, appears, is completable and can fail. Every line is
load-bearing.

```xml
<QuestScriptDef>
  <defName>Example_SmallFavour</defName>
  <rootSelectionWeight>1</rootSelectionWeight>   <!-- 0 = never randomly offered -->
  <rootMinPoints>0</rootMinPoints>
  <expireDaysRange>4~8</expireDaysRange>         <!-- the OFFER window -->
  <everAcceptableInSpace>true</everAcceptableInSpace>
  <questNameRules>
    <rulesStrings><li>questName->A small favour</li></rulesStrings>
  </questNameRules>
  <questDescriptionRules>
    <rulesStrings><li>questDescription->Hold out for [waitTicks_duration].</li></rulesStrings>
  </questDescriptionRules>
  <root Class="QuestNode_Sequence">
    <nodes>
      <li Class="QuestNode_GetMap" />                                <!-- slate: map -->
      <li Class="QuestNode_Set"><name>rewardValue</name><value>500</value></li>
      <li Class="QuestNode_Set"><name>waitTicks</name><value>$(3*60000)</value></li>
      <li Class="QuestNode_Delay">
        <delayTicks>$waitTicks</delayTicks>
        <outSignalComplete>WaitDone</outSignalComplete>
      </li>
      <li Class="QuestNode_GiveRewards">
        <inSignal>WaitDone</inSignal>
        <parms><allowGoodwill>true</allowGoodwill></parms>
      </li>
      <li Class="QuestNode_End">
        <inSignal>WaitDone</inSignal><outcome>Success</outcome>
        <sendStandardLetter>true</sendStandardLetter>
      </li>
      <li Class="QuestNode_End"><inSignal>map.MapRemoved</inSignal><outcome>Fail</outcome></li>
    </nodes>
  </root>
</QuestScriptDef>
```

Irreducible: `defName`, `root`, **at least one runtime-reachable `QuestNode_End`**,
and both text packs — even fully hidden vanilla quests supply placeholder strings
rather than omit them.

- **1 day = 60000 ticks.** Every `delayTicks` in the corpus is a multiple of it.
- **`rewardValue` is a slate var `QuestNode_GiveRewards` reads**, not a field on it.
- **Reach for the 30 `Util_*` sub-scripts before writing anything** —
  `Util_GenerateSite`, `Util_Raid`, `Util_SendItemPods`,
  `Util_GetDefaultRewardValueFromPoints`, `Util_AdjustPointsForDistantFight`.
  They are why a working site quest is 200 lines instead of 800.
- **Def inheritance is live here.** `ParentName` on a `QuestScriptDef` inherits the
  whole `<root>` tree and the text packs; `<li>` lists **append** to the parent's.
- ⭐ **`defaultChallengeRating` is the star rating**, and it is a ConfigError on a
  def that is not offerable at all.

---

## 4. The slate

- `storeAs` (or a node's implicit default name) writes; `$name` reads. **`$name`
  is a node-field reference, `[name_suffix]` is a grammar symbol — same variable,
  different syntax, different position.**
- Paths use `/`: `$site/sitePartDefs`. Expressions use `$( … )` with `randInt`,
  `randFloat`, `roundToTicksRough`: `$(randInt(12,28)*60000)`.
- `QuestNode_SubScript` `<parms>` children become slate vars **inside the callee**;
  `<prefix>` namespaces everything the callee writes, so it can be looped without
  collisions; `returnVarNames` writes back out.
- Conventional names other nodes silently expect: `map`, `asker`, `rewardValue`,
  `points`, `enemyFaction`, `site`, `siteTile`, `sitePartsParams`, `walkInSpot`,
  `customLetterLabel`/`customLetterText`. **Convention only — grep the consumer.**
- **Generate ≠ spawn.** `QuestNode_GenerateWorldObject` then
  `QuestNode_SpawnWorldObjects`, so a later failure leaves no litter on the planet.

---

## 5. Text: rule packs and grammar

All five `*Rules` fields are inline `RulePack`s (`rulesStrings`, `include`,
`rulesFiles`) — **never fields of a node**, always direct children of the def.
Syntax: `symbol(conditions,priority=N)->text`.

🔴 **ONE unresolvable symbol fails the WHOLE rule.** The text renders empty, not
partially. This is the single most common quest-text bug, and it is what square
brackets in a *literal* do: a title like `[BTD] Gravship Blueprints` sends the
resolver looking for a rule named `BTD`. `grep -n '\['` every rule string you
write or adopt.

🔴 **Every conditional symbol needs an unconditional sibling** — `<li>travelTime-></li>`,
an empty fallback, is the idiom. Vanilla omits it only where several conditional
rules cover every case between them.

**A slate var becomes `[symbol]` with no declaration** — the resolver progressively
trims the bracketed text until it hits a slate key: whole string, strip trailing
digits, else truncate at the last `_`, repeat. That is why `[timeoutTicks_duration]`
and `[lodgers0_nameDef]` both work. Suffixes are per-type, not a fixed enum:

| slate value | you get |
|---|---|
| `Pawn` | `nameFull nameDef nameIndef label definite indefinite pronoun possessive objective gender kind title age factionName …` and recurses as `<var>_faction` |
| `Faction` | `name pawnSingular pawnsPlural leaderTitle royalFavorLabel …`, recurses as `<var>_leader` |
| `Def` | `label labelPlural description definite indefinite possessive` |
| any value | `_duration` (ticks→"3 days") · `_money` · `_percent` · `_count` · `_min` `_max` (FloatRange) |

Chains go three deep: `[asker_faction_leaderTitle]`. **Bare `[asker]` never appears**
— a slate object always carries a suffix.

⚠️ **These plausible suffixes do not exist**: `_ticksToDays` (use `_duration`),
`_labelDefinite` (`_definite` *replaces* `_label`), `_kindDef` (it is `_kind`).
⚠️ `{PAWNS}`-style curly tokens are a **different** substitution layer, filled by
the emitting `QuestPart`. Do not invent new ones.
⚠️ Unresolved text surfaces in the log as a `GRAMMAR RESOLUTION TRACE` naming the
root symbol and the `UNRESOLVABLE` sub-symbols. Read the trace; do not guess.

---

## 6. Signals, and how a quest ends

A signal is a plain string, prefixed at runtime with the quest's ID — so two
concurrent quests using the same name can never collide.

- **Object signals are `<slateVarName>.<Suffix>`.** The var name is yours; the
  suffix comes from a fixed set of 75. 🔴 **Rename a `storeAs` and every `inSignal`
  on it silently stops firing** — no error, the quest simply never completes.
- **Custom signals** are any bare PascalCase name you emit and listen for
  (`PeaceTalksTimeout`, `ColonistsReturned`). A node **declares its own outgoing
  signal names** (`outSignalComplete`, `outSignalSuccess`, …) and a later sibling
  listens. That is the entire branching mechanism — no goto, just names agreeing.
- 🔴 **`.Killed` has no XML precedent — vanilla uses `.Destroyed` for "the quest
  pawn died".** About 40 of the 75 suffixes are wired only from C# and appear in no
  shipped def: legal, but nothing to copy.
- 🔴 **There is no `Quest.Accepted` signal.** Acceptance is expressed structurally
  with `<signalListenMode>`: `NotYetAcceptedOnly`, `OngoingOnly`,
  `OngoingOrNotYetAccepted`, `Always`.
- **Arming is easy to invert**, and this is the bug that reads as "success fires
  the instant the quest starts": a top-level `QuestNode_Letter` with **no
  `inSignal` fires on accept**; `WorldObjectTimeout` needs `inSignalDisable`;
  `SignalActivable` starts **disabled** and needs `inSignalEnable` *and* `inSignal`.

**Ending.** `QuestNode_End` is the only exit. Four outcomes, and only four:

| outcome | when |
|---|---|
| `Success` | completed; fires `successHistoryEvent` |
| `Fail` | failed or expired; fires `failedOrExpiredHistoryEvent` |
| `Unknown` | dissolved through no player fault - no verdict, no reputation effect |
| `InvalidPreAcceptance` | became impossible *before* acceptance; disappears silently. Always paired with `signalListenMode NotYetAcceptedOnly` |

Give rewards on the same signal as the end, in a **separate sibling node** placed
before it, so the payout resolves before the quest closes. `sendStandardLetter true`
produces the built-in completed/failed letter — omit it when you send your own.

---

## 7. Make it fire — four routes, pick one deliberately

Most "my quest never appears" reports are a def that took none of these.

1. **Natural random pool** — `rootSelectionWeight > 0`, `randomlySelectable` not
   false. No `IncidentDef` of your own needed.
2. **A dedicated incident** — `IncidentDef` with `<category>GiveQuest</category>`,
   `<workerClass>IncidentWorker_GiveQuest</workerClass>`, `<questScriptDef>Yours</questScriptDef>`.
3. **A quest giver** (1.6/Odyssey) — `<givenBy><li>Traders</li></givenBy>` plus
   `<randomlySelectable>false</randomlySelectable>`.
4. **A framework scheduler** — e.g. VEF's `QuestChainExtension`. ⚠️ **Copying a
   Vanilla Expanded quest def wholesale gives you a quest that never fires**,
   because its trigger lives in that framework's mod extension.

🔴 **Raise the weight LAST, not first.** The weight is zeroed outright by
`rootMinPoints`, `rootEarliestDay`, `rootMinProgressScore` or `minRefireDays`, and
the last-fired quest is damped to **1%**. Shipped weights run 0.15–2.0; above ~2 is
out of family. A quest that "never fires" is nearly always failing a gate, not
under-weighted.

🔴 **`isRootSpecial` fires only from code or an incident**, and `rootSelectionWeight 0`
is the deliberate idiom for the same. Read those two before concluding anything
about weights.

🔴 **Never gate a verification on the storyteller.** At ~25 minutes a load, "wait
for it to come up" is the most expensive test there is. Give yourself a
deterministic trigger: dev mode → Quests → *Generate quest…*, a
`CompProperties_UseEffectGiveQuest` item, or a bridge call.

⚠️ **`everAcceptableInSpace` unset ⇒ Accept is greyed out on a space map.** It
gates *acceptance*, not site placement, and it is invisible in ground testing.

---

## 8. Validate before you deploy

```bash
python3 skills/rimworld-quests/scripts/validate_quest.py MyQuest.xml
python3 skills/rimworld-quests/scripts/validate_quest.py --dir MyMod/Defs/QuestScriptDefs
```

It indexes `Assembly-CSharp.dll` and the shipped quest corpus (cached), resolves
`ParentName` inheritance and `QuestNode_SubScript` outputs, and checks: unknown or
mis-cased node classes · `$vars` nothing stores · unresolvable `[symbols]` and
missing rule fallbacks · signal suffixes that can never fire and `storeAs` names
that do not exist · missing/unreachable `End`, and outcomes that are not one of the
four · the ConfigErrors the game enforces · and whether the def took a firing route
at all.

**Calibration is the honest part of the tool.** Against all 151 shipped quests it
reports **1 error** — which is a real Ludeon slip, `CreepJoinerArrival`'s
`questNameRules` defining `questDescription->` — and ~40 warnings, mostly quests
fired from C# with no XML trigger to see. The first version reported 915 errors on
the same corpus. **If it fires on your def, read it; the false-positive rate is
known and low.** It cannot see inside a C# root, and it does not claim to.

⚠️ **Writing a file is not deploying it.** The game loads from its own `Mods/`
folder — `skills/rimworld-deploy/SKILL.md`.

---

## 9. XML or C#?

**Measured across every installed mod: 4,837 references to vanilla node names
against 410 to modded ones — 12:1.** Ludeon itself composes 88 of its 156 quests
from `QuestNode_Sequence` plus stock nodes.

**Start in XML, always.** `Class=` resolves against *any* loaded assembly, so you
can even borrow another mod's node without compiling anything.

**You need C# when you need a new verb** — a new site type, a custom shuttle
behaviour, a new reward formula, faction-specific pawn selection. Across ~40 mods
that add structurally new quest content there is not one counterexample. The test:
*if vanilla already knows how to do the thing — place a site, hand over pawns or
items, run a timer, branch on a signal, pay out — it is XML.* Check the 30 `Util_*`
sub-scripts and the ~300 nodes first.

🔴 **A custom C# root has a failure mode XML does not**: if its `TestRunInt()`
returns false or throws, the quest is **dropped at selection time with no log entry
at all**. Prefer keeping the `QuestNode_Sequence` wrapper around your end/fail/
timeout branches even when one inner node is yours, so the lifecycle stays editable
without a rebuild — that hybrid is what the best third-party quest mods do.

⚠️ Borrowing a modded node is a hard dependency **and** a load-order constraint.
Confirm the namespace with `strings <mod>/Assemblies/*.dll | grep QuestNode_` and
name the mod in `<modDependencies>`. VEF ships one node under three namespaces.

---

## 10. Keep this skill learning

After any quest work, ask what surprised you. If something did, add it here —
symptom, cause, fix, and **"generalises to"**. The failure table in
`references/mod_patterns.md` §6 is the residue of thirteen of those; the validator
is the half of them that could be automated.

## References

| file | what it holds |
|---|---|
| `references/vanilla_corpus.md` | the full node inventory by job, two annotated walkthroughs, all 43 root fields, the slate, the grammar suffix table, the 75 signal suffixes |
| `references/design_and_community.md` | verified-vs-web evidence marks on every claim, the selection maths, and Part B: what makes a quest worth playing |
| `references/mod_patterns.md` | what 64 quest-shipping mods do, whether C# is needed, and the 13-row symptom→cause→catch-it-offline table |
| `scripts/validate_quest.py` | the offline gate (§8) |
