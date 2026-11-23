---
name: rimworld-quests
description: Design, author, validate and debug RimWorld quests. A quest is a QuestScriptDef whose node tree runs ONCE at offer time and leaves QuestParts that talk only by signal string, so most quest bugs are silent - a renamed storeAs kills every inSignal on it, one unresolvable [symbol] blanks the whole description rather than degrading, and a def with no firing route loads clean and never occurs. Covers the prose spec that makes a quest worth playing and how each part of it maps onto def fields, the ~300 QuestNode vocabulary and the 30 Util_ sub-scripts, slate vars and $ syntax, rule packs and grammar suffixes, the four ways a quest gets offered, when a custom C# node is genuinely needed, and an offline validator calibrated against all 151 shipped quests. Use for any QuestScriptDef, QuestNode, quest reward, quest text, quest that never fires or never completes, or a request to design a quest at all.
---

# RimWorld quests

Most quest bugs raise no error when the def loads. A bug can spoil the text, or leave a branch that never starts. A bug
can also make a def that loads, appears in the def dump, and never occurs. Each check in `scripts/validate_quest.py`
exists because such a bug cost somebody a full game load. Corrected lines and their evidence: `references/history.md`.

## 0. Which job are you on

| you want to | read |
|---|---|
| decide whether this quest is worth building | §1 the model, §2 spec and stakes. Write the spec *before* the def |
| write the def | §3 shape · §4 slate · §5 text · §6 signals |
| make it actually appear in a game | §7 firing routes |
| find out why it broke | §8 validator, then `references/mod_patterns.md` §6 failure table |
| decide XML vs C# | §9 |
| know what a node/field/suffix really does | `references/vanilla_corpus.md`: the full inventory |

🔴 **Never guess a node class, a field or a signal suffix.** A suffix is the part of a signal name after the dot (§6).

- The game has ~300 `QuestNode_*` types. Some names are near-misses of each other, for example
  `QuestNode_GetSitePartDefsByTagsAndFaction` and `QuestNode_GetDefaultSitePartsParams`.
- Copy each name from a shipped def. The validator checks each class name against `Assembly-CSharp.dll`.

---

## 1. The model, which reorganises everything else

The game generates a quest **once, at offer time**.

- The node tree runs. The tree fills a **slate**: a table from a name to a value, for this generation only.
- The tree adds **`QuestPart`** objects to the live quest. Then the tree is gone.
- Only the `QuestParts` work during play. The `QuestParts` speak to each other **only by signal string**.

```
QuestScriptDef                     <- the def you author
 ├─ root = QuestNode_Sequence      <- tree, runs ONCE at generation
 │    ├─ QuestNode_GetMap          <- writes slate var  map
 │    ├─ QuestNode_Delay           <- EMITS a QuestPart that ticks in play
 │    └─ QuestNode_End             <- EMITS QuestPart_QuestEnd
 ├─ questNameRules / questDescriptionRules   <- grammar, resolved at the end
 └─ root-level fields                        <- when/whether it may be offered
```

Three results of this model:

- **You never name a `QuestPart` in XML.** C# code in `QuestNode.RunInt()` builds each of the 244 types. A new
  `QuestPart` needs a C# `QuestNode` that adds it.
- **Success and failure are structural, not computed.** No step evaluates the quest. Place one `QuestNode_End` on each
  final branch, and write its `<outcome>` there. The signal that arrives first decides the outcome.
- **Nothing declares a contract.** A node reads `map`, `asker` or `rewardValue` because that name is the convention.
  Nothing enforces the name. Read the node that consumes a variable before you name the variable.

---

## 2. Write the spec before the def

A def is the second half of the work. The first half is six lines of prose, and each line has a field in the def. Fill
in this table first. If a row is blank, the quest is not ready to build.

| the spec line | the question it answers | where it lands in the def |
|---|---|---|
| **The ask** | what does the colony have to *do* | the node tree - the site, the pawns, the timer |
| **The reason** | why does the colony care, *without mentioning the reward* | `questDescriptionRules` - first sentence |
| **The choice** | which decision has two defensible answers | a `QuestNode_Signal` per branch, one `End` each |
| **The failure state** | how is it lost, and is losing survivable | `QuestNode_End` with `<outcome>Fail</outcome>` + `failedOrExpiredHistoryEvent` |
| **The reward** | what kind, and is it proportional to the challenge | `rewardValue` slate var + `QuestNode_GiveRewards`, or a specific `AddItemsReward` |
| **The deadline** | how long, and what does the player see | `expireDaysRange` (offer window) and `QuestNode_Delay`/`WorldObjectTimeout` with `isQuestTimeout` (completion) |

**Ten yes/no questions. A "no" is a rewrite, not a note.**

1. Can I state in one sentence why the colony cares, and not name the reward?
2. Is there a decision with at least two defensible answers?
3. Does something *later* acknowledge which answer the player gave?
4. Can the player fail it, and is the failure survivable? (A quest that nobody can lose has no stakes. Players
   save-scum a quest whose failure ends the run.)
5. Is the reward proportional to the challenge that the quest really imposes?
6. Is the deadline real, enforced and shown? Do not fake an urgency that you will not enforce.
7. Can the player finish it in one sitting?
8. Does it use only mechanics that the game already has? *(A quest that needs a new subsystem is a mod, not a quest.)*
9. Can the player find the ask, the reward and the deadline, each in one glance?
10. Does the def take one of the four firing routes (§7)? Does each conditional grammar symbol have a fallback (§5)?

⚠️ **Fit the quest to the colony that will get it.** Ludeon shipped a whole wave of 1.1 fixes from this one idea.

- Two of those fixes: no mech clusters at low points, and no Empire asker for hospitality under 240 points.
- Use `rootMinPoints`, `rootMinProgressScore` and `rootEarliestDay`. Do not let the player discover the mismatch.
- Set `minRefireDays` on each quest with a memorable premise. The second telling makes the first one cheap.

Fuller design rules, with sources: `references/design_and_community.md` Part B.

---

## 3. The shape of a def

The tree below is the smallest one that generates, appears, can be completed and can fail. Each line is necessary.

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

A def cannot omit `defName`, `root`, **at least one `QuestNode_End` that play can reach**, and both text packs. A hidden
quest (`defaultHidden`) is the exception: the game does not resolve its text. Most hidden vanilla quests supply placeholder
strings (`MechanitorStartingMech` supplies none).

- **1 day = 60000 ticks.** Vanilla writes days as `$(3*60000)`. Vanilla also writes short delays in plain ticks,
  for example 300, 600 or 7500. So a delay is not always whole days.
- **`rewardValue` is a slate var that `QuestNode_GiveRewards` reads.** `rewardValue` is not a field of that node.
- **Look at the 30 `Util_*` sub-scripts before you write anything.** Examples: `Util_GenerateSite`, `Util_Raid`,
  `Util_SendItemPods`, `Util_GetDefaultRewardValueFromPoints`, `Util_AdjustPointsForDistantFight`. With them, a working
  site quest is 200 lines and not 800.
- **Def inheritance works here.** `ParentName` on a `QuestScriptDef` inherits the whole `<root>` tree and the text
  packs. A child's `<li>` lists **append** to the lists of the parent.
- ⭐ **`defaultChallengeRating` is the star rating.** On a def that cannot be offered, the rating is a ConfigError. A def
  can be offered when one of these is true:
  - `rootSelectionWeight` is not 0, and `randomlySelectable` is not false;
  - `decreeSelectionWeight` is not 0;
  - `isRootSpecial` is true.
- **Never write `QuestScriptDef`-level fields inside a `QuestNode_End`.** The two fields are `successHistoryEvent` and
  `failedOrExpiredHistoryEvent`. Such a line loads as a red 'doesn't correspond to any field' XML error and never fires.
  - The def-level fields fire on EVERY success, or on EVERY fail and expired offer.
  - To record a history event on one branch, put `QuestNode_RecordHistoryEvent` (`inSignal`, `historyDef`) before the
    `End` of that branch.
- **A mod that is absent from the def dump still gets a static check.** Each child of a `Class=` node must be a field of
  that class or of a base class.

---

## 4. The slate

- `storeAs` writes a var. If a node has no `storeAs`, its implicit default name writes. `$name` reads.
- **`$name` is a reference in a node field. `[name_suffix]` is a grammar symbol.** Both read the same variable. Their
  syntax and their position differ.
- Paths use `/`: `$site/sitePartDefs`. Expressions use `$( … )` with functions such as `randInt`, `randFloat` and
  `roundToTicksRough`: `$(randInt(12,28)*60000)`.
- The children of `<parms>` in a `QuestNode_SubScript` become slate vars **inside the sub-script that it calls**.
  - `<prefix>` puts each var that the sub-script writes under that prefix. So you can call the sub-script in a loop
    with no name collisions.
  - `returnVarNames` writes the named vars back out.
- Other nodes silently expect these conventional names: `map`, `asker`, `rewardValue`, `points`, `enemyFaction`, `site`,
  `siteTile`, `sitePartsParams`, `walkInSpot`, `customLetterLabel`/`customLetterText`. **The names are convention only:
  grep the node that consumes one.**
- 🔴 **To make a list var, write `<addToList>` on the node that generates the element.** `<addToList>` is a plain field.
  - `QuestNode_GeneratePawn` takes `<addToList>lodgers</addToList>`. The node also takes `<storeAs>`, and both can
    stand together.
  - `QuestNode_AddToList` and `AddRangeToList` append to a list var.
  - **An object signal hangs on the var name**, and one listener on a list var hears each element
    (`lodgers.Recruited`).
  - For text, the elements register again as `lodgers0`, `lodgers1` (`[lodgers0_nameDef]`).
  - One pawn with `storeAs` also has signals (`asker.Destroyed` in vanilla). Use a list when one signal must cover more
    than one pawn.
- **Generate ≠ spawn.** Use `QuestNode_GenerateWorldObject`, and then `QuestNode_SpawnWorldObjects`. Then a later
  failure leaves no litter on the planet.

---

## 5. Text: rule packs and grammar

All five `*Rules` fields are inline `RulePack`s (`rulesStrings`, `include`, `rulesFiles`). Each one is a direct child of
the def, **never a field of a node**. Syntax: `symbol(conditions,priority=N)->text`.

🔴 **ONE unresolvable symbol fails the WHOLE rule.** The resolver then tries the other rules for the same symbol. If no
rule is left, the whole text fails.

- The player then sees `ERR: ` and the first raw rule, not a part of your text (1.6 source). One older live pass reported
  an empty description.
- The unresolvable symbol is the single most common quest-text bug. Square brackets in *literal* text cause it. A title like
  `[BTD] Gravship Blueprints` makes the resolver look for a rule with the name `BTD`.
- Run `grep -n '\['` on each rule string that you write or adopt.

🔴 **Every conditional symbol needs an unconditional sibling.** The usual sibling is an empty fallback:
`<li>travelTime-></li>`. Vanilla omits the fallback only where the conditional rules together cover every case.

**A slate var becomes `[symbol]` with no declaration.** The resolver trims the text in the brackets until the text is a
slate key:

- First it tries the whole string.
- Then it strips the last digits. If there are none, it cuts the text at the last `_`. Then it repeats.

So `[timeoutTicks_duration]` and `[lodgers0_nameDef]` both work. The suffixes depend on the type of the value, so there
is no one fixed list:

| slate value | you get |
|---|---|
| `Pawn` | `nameFull nameDef nameIndef label definite indefinite pronoun possessive objective gender kind title age factionName …` and recurses as `<var>_faction` |
| `Faction` | `name pawnSingular pawnsPlural leaderTitle royalFavorLabel …`, recurses as `<var>_leader` |
| `Def` | `label labelPlural description definite indefinite possessive` |
| any value | `_duration` (ticks→"3 days") · `_money` · `_percent` · `_count` · `_min` `_max` (FloatRange) |

Chains go three deep: `[asker_faction_leaderTitle]`. **Bare `[asker]` never appears** in vanilla: a slate object always
carries a suffix.

- ⚠️ **These plausible suffixes do not exist:** `_ticksToDays` (use `_duration`), `_labelDefinite` (`_definite`
  *replaces* `_label`), `_kindDef` (use `_kind`).
- Curly tokens such as `{PAWNS}` are a **different** substitution layer. The `QuestPart` that the node adds fills them.
  Do not invent new ones.
- Unresolved text appears in the log as a `GRAMMAR RESOLUTION TRACE`. The trace names the root symbol and the
  `UNRESOLVABLE` sub-symbols. Read the trace; do not guess.

---

## 6. Signals, and how a quest ends

A signal is a plain string. At runtime the game puts the quest's ID before it. So two live quests that use the same name
never collide.

- **Object signals are `<slateVarName>.<Suffix>`.** You choose the var name. The game sends a fixed set of 75 suffixes.
  Our own C# can send another one through `QuestUtility.SendQuestTargetSignals` (`site.RUT_SleepersWoken`). The validator
  then gives a false `bad-signal-suffix` error.
- 🔴 **Rename a `storeAs` and every `inSignal` on it silently stops firing.** There is no error. The quest never
  completes.
- **Custom signals** are bare PascalCase names that one node sends and another node hears (`PeaceTalksTimeout`,
  `ColonistsReturned`).
  - A node **declares the names of the signals that it sends** (`outSignalComplete`, `outSignalSuccess`, …). A later
    sibling listens for that name.
  - The whole branch mechanism is names that agree. There is no goto.
- 🔴 **`.Killed` has no XML precedent.** Vanilla uses `.Destroyed` for "the quest pawn died". About 40 of the 75
  suffixes are sent only from C# code and appear in no shipped def. Such a suffix is legal, but you have nothing to
  copy.
- 🔴 **`QuestNode_SendSignals` has NO settable `<inSignal>` XML field.** Its only fields are
  `outSignals`/`outSignalsFormat`/`outSignalsFormattedCount`. The node reads the AMBIENT slate `inSignal` var: the
  signal of the node around it. At the top level that signal is the quest's acceptance.
  - An `<inSignal>` written on this node logs a red XML error, and the game discards it. The node then fires on the
    ambient signal, not on the signal that you meant.
  - Wrap the node in `QuestNode_SignalActivable` instead.
- 🔴 **There is no `Quest.Accepted` signal.** At acceptance the quest sends `Quest<id>.Initiate`. That signal is the
  ambient `inSignal` at the top level. So a top-level node with no `inSignal` fires on acceptance.
  - To limit a listener by quest state, use `<signalListenMode>`: `NotYetAcceptedOnly`, `OngoingOnly` (the default),
    `OngoingOrNotYetAccepted`, `Always`, or `HistoricalOnly` (after the end).
- **It is easy to start a branch at the wrong time.** The sign: "success fires the instant the quest starts".
  - A top-level `QuestNode_Letter` with **no `inSignal` fires on accept**.
  - `WorldObjectTimeout` needs `inSignalDisable`, for example `site.MapGenerated`. Without it, the timer runs on while the
    colony is on the site, and it can expire before success.
  - `SignalActivable` starts **disabled**. Its `inSignalEnable` turns it on, and then its `inSignal` fires it. If you
    omit `inSignalEnable`, the ambient signal turns it on (at the top level: acceptance). If you omit `inSignal`, it
    never fires.

**Ending.** In XML, `QuestNode_End` is the normal exit. An offer that expires also ends the quest. Four outcomes, and
only four:

| outcome | when |
|---|---|
| `Success` | completed; fires `successHistoryEvent` |
| `Fail` | failed; fires `failedOrExpiredHistoryEvent`. An expired offer fires the same event |
| `Unknown` | dissolved through no player fault: no verdict, no history event. The default when you omit `<outcome>`. A `goodwillChangeAmount` on the node still applies |
| `InvalidPreAcceptance` | became impossible *before* acceptance; disappears silently. Always paired with `signalListenMode NotYetAcceptedOnly` |

Give the rewards on the same signal as the end. Put them in a **separate sibling node** before the end node. Then the
payout resolves before the quest closes. `sendStandardLetter true` sends the built-in completed or failed letter. Omit it
when you send your own letter.

🔴 **Nothing you schedule after `QuestNode_End` ever runs.** The end cleans up the quest, and no `QuestPart` ticks after
it.

- So "fail the quest, then send the retaliation raid three days later" does not work as written.
- **The delayed consequence you want is the goodwill change.** If the loss makes the faction hostile, the storyteller can
  send its raids on its own schedule. `QuestNode_End` carries the change directly:

```xml
<li Class="QuestNode_End">
  <outcome>Fail</outcome>
  <goodwillChangeAmount>-12</goodwillChangeAmount>
  <goodwillChangeFactionOf>$asker</goodwillChangeFactionOf>
  <goodwillChangeReason>StrandedTravellerTaken</goodwillChangeReason>
</li>
```

⚠️ **`goodwillChangeReason` is a `HistoryEventDef`, not a string.** The player reads its label in the faction tab.

- Core keeps its own reasons in `Data\Core\Defs\Goodwill\GoodwillEvents_Quests.xml` (`QuestPawnLost`,
  `QuestPrisonerRecruited`, …).
- If none fits, ship your own: a `defName` and a `label`, nothing more.

---

## 7. Make it fire — four routes, pick one deliberately

Most "my quest never appears" reports are a def that took none of these routes.

1. **Natural random pool:** `rootSelectionWeight > 0`, and `randomlySelectable` not false. You need no `IncidentDef` of
   your own.
2. **A dedicated incident:** an `IncidentDef` with `<category>GiveQuest</category>`,
   `<workerClass>IncidentWorker_GiveQuest</workerClass>`, `<questScriptDef>Yours</questScriptDef>` and `targetTags`.
   - Vanilla's `GiveQuestBase` parent sets the category, the worker and the target tag `World`.
   - The storyteller's category roll offers only a `World` incident. A storyteller comp that names the incident can also
     fire a `Map_PlayerHome` one with `baseChance` 0 (vanilla: `GiveQuest_Beggars`). Keep `World` unless such a comp,
     a tool or code fires yours.
   - `jawa/storyteller_fire` builds its parms on the current map, so it refuses a `World` incident (`canFireNow` false).
     Make the home map the current map first. For an incident that only a tool, code or such a comp fires, set
     `baseChance` 0 and
     `<targetTags Inherit="False"><li>Map_PlayerHome</li></targetTags>`. Without `Inherit="False"`, the two tags stand
     together, and that is a ConfigError.
   - 🔴 **An `IncidentDef` with `questScriptDef` set AND `rootSelectionWeight != 0` is a hard vanilla `ConfigError`**
     (`IncidentDef.cs:235`), not a style nit. Both the incident and the random root-quest pool could then fire the
     quest. So set `rootSelectionWeight=0` on the quest. Also set `isRootSpecial=true`: without it, a
     `defaultChallengeRating` is a ConfigError, and the dev menu does not list the quest.
3. **A quest giver** (1.6/Odyssey): `<givenBy><li>Traders</li></givenBy>` plus
   `<randomlySelectable>false</randomlySelectable>` and `rootSelectionWeight > 0`. The giver picks by that weight, so a
   weight of 0 is never picked. Set `expireDaysRange` too (a ConfigError without it).
4. **A framework scheduler:** for example the `QuestChainExtension` of VEF (Vanilla Expanded Framework). ⚠️ **Copying a
   Vanilla Expanded quest def wholesale gives you a quest that never fires.** Its trigger lives in that framework's mod
   extension.

Our own C# code, a royal decree (`decreeSelectionWeight` and `decreeTags`) and a sub-script call can also start a quest.

🔴 **Raise the weight LAST, not first.** A quest that "never fires" nearly always fails a gate. The weight is seldom too
low.

- `rootMinPoints`, `rootEarliestDay`, `rootMinProgressScore` or `minRefireDays` can each set the weight to zero.
- A root node whose `TestRun` fails, and a planet layer that the def does not allow, also block the quest.
- The last-fired quest is damped to **1%**. The four before it are damped less.
- Shipped weights run 0.15–2.0. A weight above ~2 is out of family.

🔴 **`isRootSpecial` alone puts nothing in the random pool, and takes nothing out.** The pool reads only
`rootSelectionWeight` and `randomlySelectable`. A def with `rootSelectionWeight 0` fires
only from code, an incident or a decree. A def with `randomlySelectable` false can also fire from a quest giver. Read
those two fields before you conclude anything about weights.

🔴 **Never gate a verification on the storyteller.** "Wait for it to come up" is the most expensive test there is. Give
yourself a deterministic trigger: dev mode → Quests → *Generate quest…*, a `CompProperties_UseEffectGiveQuest` item, or a
bridge call. The dev menu lists only a def that can be offered (§3, `defaultChallengeRating`). For the cost of a load, and
for a short test list, read `skills/rimworld-load-round/SKILL.md`.

⚠️ **`everAcceptableInSpace` unset ⇒ Accept is greyed out on a space map.** The field gates *acceptance*, not site
placement. Ground tests do not show this. An `autoAccept` quest gets no greyed Accept. The natural pool targets the
world, so it still offers such a quest. But an incident whose target is a map in space does not offer it, `autoAccept` or
not.

---

## 8. Validate before you deploy

```bash
python3 skills/rimworld-quests/scripts/validate_quest.py MyQuest.xml
python3 skills/rimworld-quests/scripts/validate_quest.py --dir MyMod/Defs/QuestScriptDefs
```

The validator indexes `Assembly-CSharp.dll` and the shipped quest corpus, and keeps a cache. It resolves `ParentName`
inheritance and the outputs of each `QuestNode_SubScript`. It checks for:

- unknown or mis-cased node classes;
- `$vars` that nothing stores;
- unresolvable `[symbols]`, and missing rule fallbacks;
- signal suffixes that can never fire, and `storeAs` names that do not exist;
- a missing or unreachable `End`, and outcomes that are not one of the four;
- the ConfigErrors that the game enforces;
- whether the def took a firing route at all.

**Calibration is the honest part of the tool.** Against all 151 shipped quests it reports **1 error** and
32 warnings (measured 2026-11-23).

- The error is a real Ludeon slip: `questNameRules` of `CreepJoinerArrival_Metalhorror` defines `questDescription->`,
  inherited from its parent. The slip does no harm there, because the quest is hidden.
- The warnings are mostly quests that C# fires, with no XML trigger for the tool to see.
- **If it fires on your def, read it: the false-positive rate is known and low.** It cannot see inside a C# root, and it
  does not claim to.
- **The tool gives a false WARN `[unwritten-slate]` for a list that only
  `<addToLists><li>X</li></addToLists>` of `QuestNode_GeneratePawn` builds.** That is a real engine field: in 1.6,
  `RunInt` loops it into `AddToOrMakeList`. The tool's `collect_writes` does not read that field. Treat the WARN as a
  false positive for such a list, or teach `collect_writes` the field.

⚠️ **Writing a file is not deploying it.** The game loads from its own `Mods/` folder: `skills/rimworld-deploy/SKILL.md`.

---

## 9. XML or C#?

**Measured across every installed mod: 4,837 references to vanilla node names against 410 to modded ones, 12:1.** Ludeon
ships 156 `QuestScriptDef`s, and five of them are abstract parents. Ludeon composes 88 of the 156 from
`QuestNode_Sequence` plus stock nodes.

**Start in XML, always.** `Class=` resolves against *any* loaded assembly. So you can borrow another mod's node and
compile nothing.

**You need C# when you need a new verb.** Examples: a new site type, a custom shuttle behaviour, a new reward formula,
faction-specific pawn selection. Of the ~40 mods that add structurally new quest content, all ship C# for it.

- The test: *if vanilla already knows how to do the thing, it is XML.* Vanilla can place a site, hand over pawns or
  items, run a timer, branch on a signal and pay out.
- Check the 30 `Util_*` sub-scripts and the ~300 nodes first.

🔴 **A root whose `TestRunInt()` returns false is dropped at selection time with no log entry at all.** A custom C# root
hides the cause, because you cannot read its test in XML. A `TestRunInt()` that throws does log an error ("Error while
checking if can generate quest"). Keep the `QuestNode_Sequence` wrapper around your end, fail and timeout branches, even
when one inner node is yours. Then you can edit the lifecycle and not rebuild. The best third-party quest mods use that
hybrid.

⚠️ A borrowed modded node is a hard dependency **and** a load-order constraint.

- Confirm the namespace in that assembly's metadata. Point `DLL` in a copy of
  `src/RimMandrake/Utils/ilprobe/meta_core.py` at the mod's dll, and list every `QuestNode_*` in `typedefs`. The
  namespace comes with the name.
- Never use `strings … | grep QuestNode_`. The blind-scan hook refuses it. A byte scan of a .NET assembly finds only a
  minority of names, so a miss is not absence.
- Then name the mod in `<modDependencies>`. VEF ships one node under three namespaces.

---

## 10. A worked example, and what it could not tell me

`src/RimMandrake/StrandedQuest/` is a complete one-quest mod, written from this skill and nothing else. The mod holds
an About, one `QuestScriptDef` and one `HistoryEventDef`. The mod uses only vanilla nodes and has no DLC dependency.

- Its header carries the spec that it was built from, and a file-and-line source for every node shape.
- Read it before you write your first quest. Vanilla is slower to read: its teaching examples are 300 lines, with
  a DLC's vocabulary in them.

**Two things were unknown when that quest was built.** The 1.6 source answers both:

- **`arrivalMode` is a `PawnsArrivalModeDef`.** If you omit it on `QuestNode_PawnsArrive`, the pawns walk in from the edge
  (`EdgeWalkIn`). The one literal value in vanilla quest XML is `RandomDrop`. Core defines others, for example
  `EdgeDrop` and `CenterDrop`. The example uses a drop pod only because the author saw one value.
- **`<choices>` of `QuestNode_GetRandomPawnKindForFaction` is required.** Without it the node throws, in the test run
  too. An entry matches on `factionDef` (both vanilla uses name the Empire) or on `categoryTag`. Set `<fallback>`
  unless an entry always matches. The test run fails, and the quest is dropped, in two cases: no match and no
  fallback, or a `factionOf` with no faction. The example uses a
  factionless `SpaceRefugee` instead.

**When you hit a gap that no tutorial covers, file it as a lesson (§11).** The author found both gaps by trying to build something.

## 11. Keep this skill learning

After any quest work, ask what surprised you. If something did, file a lesson (`src/RimMandrake/Utils/lessons.py add`): symptom, cause, fix, and **"generalises
to"**. A fresh-context curation session then adds it here. The failure table in `references/mod_patterns.md` §6 is what
remains of thirteen such lessons. The validator holds the half of them that a program can check.

## References

| file | what it holds |
|---|---|
| `references/vanilla_corpus.md` | the full node inventory by job, two annotated walkthroughs, all 43 root fields, the slate, the grammar suffix table, the 75 signal suffixes |
| `references/design_and_community.md` | verified-vs-web evidence marks on every claim, the selection maths, and Part B: what makes a quest worth playing |
| `references/mod_patterns.md` | what 64 quest-shipping mods do, whether C# is needed, and the 13-row symptom→cause→catch-it-offline table |
| `references/history.md` | old lines of this skill that were wrong or are evidence only, and what showed it |
| `scripts/validate_quest.py` | the offline gate (§8) |
