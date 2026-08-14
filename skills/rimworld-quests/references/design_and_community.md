# design_and_community.md — quest authoring: what the code says, what the web says, what good looks like

Compiled 2026-08-14 against this machine: **RimWorld 1.6.4871 rev590**, all five expansions installed (Royalty, Ideology, Biotech, Anomaly, Odyssey).

🔴 **Evidence marks.** **[V]** = VERIFIED here (game XML, decompiled `Assembly-CSharp.dll`, or the local def dump) — trust it. **[W]** = WEB ONLY, not checked locally; every RimWorld quest tutorial on the open web is 1.1–1.3 era, so treat as a lead. **[W✓]** = web claim confirmed locally. **[W✗]** = web claim contradicted locally, do not use.

**Contents.** PART A: [A1 where quests live](#a1-where-quests-live) · [A2 pipeline](#a2-the-generation-pipeline) · [A3 QuestScriptDef fields](#a3-questscriptdef-fields-complete-16) · [A4 selection weight](#a4-selection-how-rootselectionweight-is-actually-used) · [A5 how a quest actually fires](#a5-how-a-modded-quest-actually-fires) · [A6 nodes and slate](#a6-the-node-tree-slate-and--syntax) · [A7 signals](#a7-signals) · [A8 quest text](#a8-quest-text-rulepacks-and-grammar) · [A9 shipped patterns](#a9-shipped-patterns-verbatim) · [A10 gotchas](#a10-gotchas) · [A11 sources](#a11-sources-for-part-a).
PART B: [B1 before you write](#b1-before-you-write-it) · [B2 stakes and consequence](#b2-stakes-choice-consequence) · [B3 failure patterns](#b3-the-named-failure-patterns) · [B4 time and agency](#b4-respecting-the-players-time-and-agency) · [B5 how it reads](#b5-how-the-text-should-read) · [B6 pacing](#b6-pacing-into-a-campaign) · [B7 checklist](#b7-the-draft-checklist) · [B8 sources](#b8-sources-for-part-b). Then [contested or unverified](#contested-or-unverified).

---

# PART A — RimWorld quest authoring

## A1. Where quests live

**[V]** Under `<Module>/Defs/QuestScriptDefs/`. `<QuestScriptDef>` counts shipped under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\`: Royalty 62 (six nested subfolders), Odyssey 32, Core 23, Ideology 15, Anomaly 14, Biotech 10.

**[V]** The folder name is **convention only** — def loading recurses anywhere under `Defs/`. Royalty nests three levels; workshop mods here use `Defs/QuestScriptDef/` (singular) and arbitrary paths and load fine. Several `<QuestScriptDef>` per file is normal, and a `RulePackDef` inside a `QuestScriptDefs` folder loads fine too.

**[V]** With 585 mods active this install resolves **243** `QuestScriptDef`s. The dump at `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\QuestScriptDef.json` (1.49 MB, fully-resolved values including the whole `root` graph) **is the best quest reference on this machine** — post-patch and version-correct, unlike any web page.

## A2. The generation pipeline

**[W✓]** The wiki's account, steps 1–2 confirmed by decompilation: (1) pick a `QuestScriptDef` at random weighted by `rootSelectionWeight`; (2) check its root node passes `TestRunInt()` against an emulated slate — a dry run that may write generation-time slate values but **must not touch the map**; (3) `QuestGen.Generate()` runs the def; (4) the slate is seeded, normally `Map map` and `int points`; (5) call stack `QuestGen.Generate()` → `QuestScriptDef.root.Run()` → `QuestNode.RunInt()`; (6) once the `QuestPart`s exist, the `Quest` appears in the Quests tab.

**[V]** Namespaces, since guessing them wastes a load: `RimWorld.QuestScriptDef`, `RimWorld.QuestGen.QuestGen`, `RimWorld.QuestGen.Slate`, `RimWorld.QuestGen.QuestNode`, `RimWorld.QuestGen.SlateRef<T>`, `RimWorld.QuestGen.QuestGenUtility` — but **`RimWorld.QuestPart`**, *not* in the `QuestGen` namespace. 1.6 defines **301** `QuestNode_*` and **244** `QuestPart_*` types; ~70 of the nodes are `QuestNode_Root_*`, a one-off C# root for a single quest.

## A3. QuestScriptDef fields (complete, 1.6)

**[V]** Decompiled verbatim; this is the entire field set:

```csharp
public QuestNode root;  public float rootSelectionWeight;  public bool randomlySelectable = true;
public SimpleCurve rootSelectionWeightFactorFromPointsCurve;  public float minRefireDays;
public float rootMinPoints, rootMinProgressScore;  public int rootEarliestDay;  public bool rootIncreasesPopulation;
public float decreeSelectionWeight;  public List<string> decreeTags;
public RulePack questDescriptionRules, questNameRules, questDescriptionAndNameRules, questContentRules, questSubjectRules;
public bool autoAccept, hideOnCleanup, nameMustBeUnique, defaultHidden, defaultCharity, isRootSpecial, canGiveRoyalFavor;
public FloatRange expireDaysRange = new FloatRange(-1f, -1f);  public int defaultChallengeRating = -1;
public bool hideInvolvedFactionsInfo, affectedByPopulation;  public bool affectedByPoints = true;
public string questAvailableLetterLabel;  public LetterDef questAvailableLetterDef;
public bool questAvailableLetterTextIsDescription;  public bool sendAvailableLetter = true;
public HistoryEventDef successHistoryEvent, failedOrExpiredHistoryEvent;
public bool epic;  public QuestScriptDef epicParent;  public bool endOnColonyMove = true;
public bool everAcceptableInSpace, neverPossibleInSpace, canOccurOnAllPlanetLayers;
public List<PlanetLayerDef> layerWhitelist, layerBlacklist;  public List<QuestGiverTag> givenBy = new List<QuestGiverTag>();
```

**[V]** `epic`, `epicParent`, `endOnColonyMove`, `everAcceptableInSpace`, `neverPossibleInSpace`, `layerWhitelist/Blacklist`, `canOccurOnAllPlanetLayers` and `givenBy` are **Odyssey/1.6 additions** — no web tutorial covers them. `givenBy` takes tag enums, not defNames; the only values shipped are `["Traders","Beggars","Reading"]` and `["OrbitalScanner"]`.

**[V]** `ConfigErrors()` enforces exactly three rules: `rootSelectionWeight > 0 && !autoAccept && expireDaysRange.TrueMax <= 0` is an error; `autoAccept && expireDaysRange.TrueMax > 0` is an error; `defaultChallengeRating > 0 && !IsRootAny` is an error.

## A4. Selection: how `rootSelectionWeight` is actually used

**[V]** `StorytellerComp_RandomQuest`'s whole body defers to `NaturalRandomQuestChooser.ChooseNaturalRandomQuest(points, target)`, which filters on `IsRootRandomSelected && rootIncreasesPopulation == incPop && CanRun(points, target)` then `TryRandomElementByWeight`. The weight is **zeroed** if any of: `rootSelectionWeight <= 0` · `points < rootMinPoints` · `DaysPassedSinceSettle < rootEarliestDay` · `GetProgressScore(target) < rootMinProgressScore` · the same root fired within `60000 * minRefireDays` ticks. It is then multiplied by `rootSelectionWeightFactorFromPointsCurve`, by `QuestTuning.RecentStoryWeightFactors = {0.01, 0.3, 0.5, 0.7, 0.9}` if the quest is among the last five fired, and by a royal-favour damping curve when `canGiveRoyalFavor == false` and the player wants favour.

🔴 **[V] Consequence:** the last-fired quest is suppressed to **1 %**. A quest that "never fires" is far more often failing `rootMinPoints`, `rootMinProgressScore` or `TestRunInt` than it is under-weighted. **Raise the weight last, not first.**

**[V]** Shipped weights are narrow — `0.15, 0.2, 0.5, 0.6, 1.0, 1.1, 1.3, 1.5, 1.9, 2.0`; above ~2 is out of family. Other tuning: `QuestTuning.PointsToRewardMarketValueCurve = {(300,800),(700,1500),(5000,4000)}`, `IncreasesPopQuestChanceByPopIntentCurve = {(0,0.05),(1,0.3),(3,0.45)}`.

**[V]** `IsRootRandomSelected` is a **computed property**, not an XML field: `rootSelectionWeight != 0 && randomlySelectable`. **[W✗]** Sources telling you to set `isRootRandomSelected` are wrong — the string is absent from the 1.6 assembly, so the tag is a silent no-op; the real knob is `randomlySelectable` (default `true`). **[W✗]** `NaturalRandomQuestChance` and `QuestPointsCurve` likewise do not exist in 1.6.

**[W]** Ludeon 1.1.2610: "Random quests no longer generate at all under 100 points, and lerp to generating as normal at 200 points"; "Quests' reward value is now always at least 250 silver, no matter how small the quest."

## A5. How a modded quest actually fires

**[V]** Four routes, all present in local 1.6 data. Pick one deliberately — most "my quest never appears" reports are a def that took none of them.

1. **Natural random.** `rootSelectionWeight > 0` and `randomlySelectable` not false. Picked out of the shared pool by `IncidentWorker_GiveQuest` with no `questScriptDef` set (`...\Data\Core\Defs\Storyteller\Incidents_World_Quests.xml`). **No IncidentDef of your own is needed.**
2. **Dedicated incident.** An `IncidentDef` with `<category>GiveQuest</category>`, `<workerClass>IncidentWorker_GiveQuest</workerClass>`, `<questScriptDef>YourDef</questScriptDef>` — e.g. `GiveQuest_MechanoidSignal` in `...\Data\Odyssey\Defs\IncidentDefs\Incidents_Map_Special.xml`.
3. **Quest giver (1.6/Odyssey only).** `<givenBy><li>Traders</li><li>Beggars</li><li>Reading</li></givenBy>` together with `<randomlySelectable>false</randomlySelectable>` — `...\Data\Odyssey\Defs\QuestScriptDefs\Script_AncientComplex.xml`.
4. **A framework scheduler.** Vanilla Expanded quests use `VEF.Storyteller.QuestChainExtension` in `<modExtensions>` and set no `rootSelectionWeight` at all.

🔴 **[V] Gotcha:** `rootSelectionWeight` of `0` is the deliberate idiom for "fires only from C# or an incident, never naturally". **Copying a Vanilla Expanded quest def wholesale gives you a quest that never fires**, because its trigger lives in a VEF mod extension — add route 1 or 2 instead.

## A6. The node tree, slate and `$` syntax

**[V]** Of 88 `QuestScriptDef`s in the top-level DLC quest folders, **44 use `<root Class="QuestNode_Sequence">`**; the rest use a bespoke `QuestNode_Root_*` C# class. **[W]** The wiki calls the second style "one single bloated `QuestNode` generating all `QuestPart`s, ignoring the `Slate`", and says Ludeon moved that way from Ideology onward — the shipped ratio bears that out as a drift, not an abandonment. Node frequency across all shipped quest XML — learn these first:

```
QuestNode_Set 262 · Sequence 259 · SubScript 158 · End 146 · Letter 88 · Signal 84 · Delay 41 · IsSet 37
GetMap 34 · IsTrue 24 · RandomNode 22 · GetFaction 19 · SendSignals 16 · WorldObjectTimeout 15 · GetSiteTile 15
GetPawn 15 · AllSignals 14 · SpawnWorldObjects 13 · CreateIncidents 13 · NoWorldObject 12 · IsNull 12
GiveRewards 12 · GeneratePawn 12 · EvaluateSimpleCurve 10
```

**[V]** Three ways a value enters the slate: `<storeAs>name</storeAs>` on a node (multi-output nodes use `storeXAs` — `storeFactionAs`, `storeSitePartsParamsAs`, `storeCanCaravanAs`, …); `<li Class="QuestNode_Set"><name>siteThreatChance</name><value>0.85</value></li>`; and `QuestNode_SubScript` `<parms>`, whose child element names become slate vars inside the called script — `<def>Util_RandomizePointsChallengeRating</def><parms><pointsFactorTwoStar>1.5</pointsFactorTwoStar></parms>`.

**[V]** Reads use `$name`, arithmetic uses `$( … )`: `<chance>$siteThreatChance</chance>` · `<delayTicks>$(randInt(12,28)*60000)</delayTicks>` · `<value2>$($raidCount - 1)</value2>`. A bare `<li Class="QuestNode_GetMap" />` stores under the default name `map`, which is why `[map_definite]` resolves with no `storeAs`.

**[V]** Reusable helpers are ordinary `QuestScriptDef`s with **no** `rootSelectionWeight`, named `Util_*`, called via `QuestNode_SubScript`, declaring `returnVarNames`. Whole example: `Util_GetDefaultRewardValueFromPoints` is one `QuestNode_EvaluateSimpleCurve` over `$points` storing `rewardValue`, curve `(200,550) (400,1100) (800,1600) (1600,2600) (3200,3600) (20000,20000)`.

**[V]** `Class=` accepts a bare name (`QuestNode_Sequence`) or a fully-qualified one; **a node from your own assembly must be namespaced** — `VanillaQuestsExpandedTheGenerator.QuestNode_Root_NuclearArcSite`. A custom C# root's contract with the XML is the slate keys it sets: whatever it `slate.Set(…)`s is exactly what the `questDescriptionRules` symbols may read.

## A7. Signals

**[V]** Tags in use: `inSignal` (125), `inSignalDisable` (36), `outSignals` (16 — **plural**, on `QuestNode_SendSignals`), `inSignalRemovePawn`, `inSignalChoiceUsed`, `outSignalComplete`, `inSignalEnable`, `outSignalResult`, `outSignalSuccess`, `outSignalFailed`, `outSignalColonistsDied`, `outSignalPawnsNotAvailable`, `inSignalLeave`, `outSignal`.

**[V]** Convention is `<slateVarName>.<Event>`. Most common literals: `site.MapGenerated` · `monumentMarker.MonumentCompleted` · `ShuttleArrived` · `map.MapRemoved` · `pickupShipThing.SentSatisfied`/`SentUnsatisfied`/`LeftBehind`/`Destroyed` · `site.AllEnemiesDefeated` · `site.NoActiveThreats` · `site.Destroyed` · `faction.BecameHostileToPlayer` · `settlement.TradeRequestFulfilled` · `conditionCauser.Destroyed` · `lodgers.RanWild`/`Recruited`/`Enslaved`/`Arrested`/`LeftMap` · `peaceTalks.Resolved` · `ColonistsReturned` · `ColonistsDied` · `GameConditionStarted` · `Incompletable` · `RewardGiven`. Bare undotted names are quest-local signals raised by `QuestNode_SendSignals`.

🔴 **The signal name is derived from the `storeAs` name.** Rename a `storeAs` and every `inSignal` referencing it silently stops firing — no error, the quest simply never completes. **[V]** `signalListenMode` (e.g. `NotYetAcceptedOnly`) exists to stop a pre-acceptance failure condition firing after the player accepts.

## A8. Quest text: RulePacks and grammar

**[V]** `questNameRules` / `questDescriptionRules` / `questContentRules` / `questSubjectRules` are **inline RulePacks**: direct children are `<rulesStrings>` and `<include>` (RulePackDef defNames). There is **no** `<rulePack>` wrapper here — that is only for a standalone `RulePackDef`. `questContentRules` holds strings the C# nodes pull at runtime (letter labels and texts), separate from name and description. Rule syntax is `symbol(conditions,priority=N)->text`; conditions compare slate vars with `==`, `>=`, `>`, `<`; `priority=-999` marks a fallback; `(p=3)` weights an alternative. Verbatim from `...\Data\Core\Defs\QuestScriptDefs\Script_TradeRequest.xml`:

```xml
<questDescriptionRules><rulesStrings>
  <li>questDescription->A nearby settlement, [settlement_label], has a special trade request. They would like to purchase:
\n  [requestedThingCount]x [requestedThing_label] [qualityInfo](worth [requestedThingMarketValue_money])
\nIf you want to make the trade, send a caravan with the requested items.[travelTime]</li>
  <li>qualityInfo(requestedThingHasQuality==True,priority=1)->of normal+ quality </li>
  <li>qualityInfo-></li>
  <li>travelTime(canCaravan==True,priority=1)-> The estimated travel time is [estimatedTravelTime_duration].</li>
  <li>travelTime-></li>
</rulesStrings></questDescriptionRules>
```

🔴 **[V] The bare fallback line is not optional.** Every conditional symbol needs an unconditional `symbol->` sibling, or the description becomes *unresolvable* the instant the condition is false.

**[V]** Other mechanics: `\n` is written literally and becomes a newline · rich-text markers `(*Threat)…(/Threat)` · `{SUBJECT_definite}` / `{BASETEXT}` curly tokens are a *separate* substitution channel from `[symbol]` · symbols nest through objects, e.g. `[asker_faction_leaderTitle]`.

**[V]** Every slate variable is expanded into rules named `<var>_<aspect>`. Aspect suffixes in the assembly: `_definite`, `_indefinite`, `_label`, `_nameDef`, `_nameFull`, `_pronoun`, `_possessive`, `_gender`, `_title`, `_titleCase`, `_faction`. Most-used in shipped text: `[asker_nameDef]` 117 · `[asker_faction_name]` 75 · `[map_definite]` 67 · `[asker_pronoun]` 57 · `[asker_nameFull]` 55. `[resolvedQuestName]` works inside letters.

**[V]** Quest text is **not** DefInjected — there is no `Languages\English\DefInjected\QuestScriptDef` folder. Localisation rides `TKey="…"` attributes on `<label>`/`<text>` inside the node tree, plus `Keyed\` UI strings.

## A9. Shipped patterns, verbatim

**[V] Single C# root** — the whole of `...\Data\Core\Defs\QuestScriptDefs\Script_WandererJoins.xml`:

```xml
<QuestScriptDef>
  <defName>WandererJoins</defName>
  <autoAccept>true</autoAccept>  <defaultHidden>true</defaultHidden>  <isRootSpecial>true</isRootSpecial>
  <successHistoryEvent MayRequire="Ludeon.RimWorld.Ideology">CharityFulfilled_WandererJoins</successHistoryEvent>
  <failedOrExpiredHistoryEvent MayRequire="Ludeon.RimWorld.Ideology">CharityRefused_WandererJoins</failedOrExpiredHistoryEvent>
  <questNameRules><rulesStrings><li>questName->Wanderer joins</li></rulesStrings></questNameRules>
  <questDescriptionRules><rulesStrings><li>questDescription-></li></rulesStrings></questDescriptionRules>
  <root Class="QuestNode_Root_WandererJoin_WalkIn" />
</QuestScriptDef>
```

**[V] "Proper" XML tree** — header of `Script_TradeRequest.xml`: `rootSelectionWeight 1.1` · `rootMinProgressScore 8` · `defaultChallengeRating 1` · `expireDaysRange 4~8` · `everAcceptableInSpace true`; then `<root Class="QuestNode_Sequence"><nodes>` of `QuestNode_GetMap` → `QuestNode_GetNearbySettlement` (`storeAs settlement`, `storeFactionLeaderAs asker`) → `QuestNode_GetFactionOf` (`<thing>$asker</thing>`) → `QuestNode_Letter` on `<inSignal>faction.BecameHostileToPlayer</inSignal>`.

**[W]** The best third-party *fragmented* reference read for this document is Save Our Ship 2's `SoSMayday` (`https://raw.githubusercontent.com/KentHaeger/SaveOurShip2/HEAD/1.6/Defs/QuestScriptDefs/Script_ShipMayday.xml`, About lists 1.0–1.6) — pure vanilla nodes, no custom C# at all: `Util_RandomizePointsChallengeRating` → `GetMap` → `GetSiteTile` → `GetSitePartDefsByTagsAndFaction` → `GetDefaultSitePartsParams` → `Util_GenerateSite` → `SpawnWorldObjects` → `WorldObjectTimeout` (fail branch) → `NoWorldObject` (end).

**[W]** The most instructive *hybrid* is Vanilla Quests Expanded – The Generator's `VQE_NuclearArcSite` (`https://raw.githubusercontent.com/Vanilla-Expanded/VanillaQuestsExpanded-TheGenerator/main/1.6/Defs/Quests/Quest6.xml`, About 1.5+1.6): a `QuestNode_Sequence` root, a `QuestNode_RandomNode` choosing asker-vs-no-asker **in pure XML** so the conditional `questDescription(askerIsNull==true)` rules work, then one custom C# node for site generation, then vanilla `WorldObjectTimeout`/`Signal`/`GiveRewards`/`End` for the lifecycle. That buys XML-editable outcomes without reimplementing site gen.

## A10. Gotchas

- 🔴 **[W] The `TestRunInt` trap — expect this failure mode first.** A custom root node whose `TestRunInt()` returns false, or throws, causes the quest to be **dropped at selection time with no log entry at all**. It simply never appears, and nothing tells you why. `TestRunInt` gets a *temporary* slate and must not touch the map. **Consequence: prefer an all-XML `QuestNode_Sequence` root while you can express the quest with vanilla nodes** — no assembly, no build step, no silent-drop trap. Drop to a custom C# root only for site/pawn generation vanilla cannot express, and even then keep the XML `QuestNode_Sequence` wrapper around the end/fail/timeout branches so they stay editable without a rebuild.
- **[V] `isRootSpecial` removes the def from the natural random pool** (42 vanilla defs use it). Setting it *and* a `rootSelectionWeight` is a contradiction; setting neither, and no incident and no `givenBy`, is the commonest reason a new quest never fires (A5).
- **[V] Casing is unforgiving and vanilla is inconsistent.** Both `QuestNode_SubScript` (158 uses) and `QuestNode_Subscript` (2) exist as real types; likewise `QuestNode_Unset` and `QuestNode_UnSet`. Copy class names out of a def; never retype them.
- **[V] Five names look like nodes but are source filenames only** — `Class="…"` on any of them fails: `QuestNode_GetColonistsCount`, `QuestNode_NotifyPlayerRaidedSomeone`, `QuestNode_Root_Creepjoiner_WalkIn`, `QuestNode_Root_MysteriousCargoCube`, `QuestNode_Root_WorshippedTerminal`.
- **[V]** `rootSelectionWeight > 0` with no `expireDaysRange` is a config error; so is `autoAccept` **with** one.
- **[W]** Unresolved description text surfaces as a `GRAMMAR RESOLUTION TRACE` listing the root symbol, custom rules, variables, and the `UNRESOLVABLE` sub-symbols. Read the trace instead of guessing which symbol broke.
- **[W]** Ludeon ships fixes for this class of bug repeatedly — "QuestNode_GetRandomPawnKindForFaction sometimes makes the quest description unresolvable" (1.1.2610), "Wastepack dump quests descriptions unresolved" (1.4.3563), "Quests incorrectly capitalize words inside curly brackets" (1.1.2598). Assume your first draft has an unresolvable branch.
- **[W]** Labels containing `[]{},` break grammar resolution — keep them out of any def a quest names. `nameMustBeUnique` exists because duplicate quest names are a real failure (1.1.2598 improved the duplicate-name warning).
- **[W]** Test without waiting for natural generation: dev mode → debug-actions icon → **Quests → Generate quest…** (has a search filter). A quest-script-defs debug table also exists (1.1.2610 fixed an error in it).
- **[V]** Writing a file is not deploying it — the game loads from the Steam Mods folder, not this repo. See `/mnt/d/Luke/dev/Rimworld/skills/rimworld-deploy/SKILL.md`.

## A11. Sources for Part A

- https://rimworldwiki.com/wiki/Modding_Tutorials/Quests — the only general quest-modding tutorial. Short, marked "Under Review", with an open TODO list including *"Compare single-QuestNode approach to 'proper' fragmented QuestNode approach"* — unwritten. **[W]** Its concepts (Slate, SlateRef, TestRunInt/RunInt, the six-step pipeline) check out; no 1.4–1.6 material. *(Cloudflare 403s a direct fetch; `curl -sL https://r.jina.ai/<url>` works.)*
- https://github-wiki-see.page/m/Taranchuk/RW-Modding-Tutorials/wiki/Quest-framework-tutorial — the fullest community field-by-field walk-through. **Last modified Nov 2021 → 1.3 era.** Its notes on `rootSelectionWeight`, `rootMinPoints`, `expireDaysRange`, `successHistoryEvent` still hold in 1.6; coverage stops well short of the field set.
- https://rimworldwiki.com/wiki/Quests — player-facing mechanics, and current (mentions Odyssey and the Gravship chain). Quest difficulty uses raid points summed across *all* colonies and caravans; 1–3 stars = 1×/2×/3× points with ±30 % variance; endgame quests show 4 stars and do not scale the same way.
- Open-source quest XML read for this document: `https://github.com/KentHaeger/SaveOurShip2` (1.0–1.6, pure vanilla nodes) · `https://github.com/Vanilla-Expanded/VanillaQuestsExpanded-TheGenerator` (1.5+1.6, hybrid) · `https://github.com/Vanilla-Expanded/VanillaQuestsExpanded-DroneFactory` and `-Ancients` (1.6, single custom root, VEF-scheduled) · `https://github.com/Vanilla-Expanded/VanillaExpandedFramework` (`QuestChainExtension`). ⚠️ Dead ends: `emipa606/RimQuest` defines **no** `QuestScriptDef` (it is a quest *dispenser*), `Laurence-042/RimTalk---Quests` has no quest XML, `rvanasa/rimworld-cities` ships a `<!-- TODO convert to 1.1 quest system -->` stub, and `kaczorski/Custom-Quests-Outcasts` is 1.4-only.
- https://ludeon.com/blog/2020/04/update-1-1-2609-improves-quest-generation-and-more/ · https://ludeon.com/blog/2020/04/update-1-1-2598-adds-configurable-quest-rewards-and-more/ · https://ludeon.com/blog/2022/11/update-1-4-3563-improves-quest-reward-variety/

---

# PART B — what makes a quest worth playing

Each rule is phrased so a draft passes or fails it.

## B1. Before you write it

- **B1.1 Name the reason the player cares before you name the reward.** If the only answer is "there is loot", it is filler. Avellone: a good side quest "informs the main plot or the area it's located in in all respects — lore, NPCs, even through the rewards you get".
- **B1.2 Do not upstage.** "A bad side quest is a quest that upstages the main quest in terms of stakes, enemies, or even the lore." — Avellone.
- **B1.3 Use the systems the game already has.** "Side quests should use the core gameplay mechanics and avoid special case new functionality." In RimWorld terms: prefer an existing `QuestNode`/`QuestPart` over a bespoke C# one. A quest needing a new subsystem is a mod, not a quest.
- **B1.4 Kill most of your ideas.** CDPR's side-quest acceptance ratio is **5–10 %** of concepts pitched. If every idea you had shipped, you did not filter.
- **B1.5 Hide the quest type inside the fiction.** "Kill the rat queen", never "kill 10 rats" — force the action through the situation, not through a counter.

## B2. Stakes, choice, consequence

- **B2.1 A real choice needs competing values, imperfect information, and proportional consequences.** Two options where one is strictly better is not a choice.
- **B2.2 Four tests for whether a choice landed:** the player knew they were choosing · it changed mechanics or story · something *later* refers back to it · it cannot be undone. Fail any one and the choice was decoration.
- **B2.3 Delay some consequences.** Deferred consequence produces stronger memory than an immediate payout, and in a colony sim it is cheap — a signal that fires days later.
- **B2.4 Make the consequence visible.** CDPR's rule: display the outcome prominently, or players will not believe the decision mattered.
- **B2.5 Every option should cost something.** "No side is completely right" is what makes a decision memorable rather than a lookup.
- **B2.6 Give it a real failure state, and make failing interesting.** A quest that cannot be lost has no stakes; one that ends the run gets save-scummed. Aim for a loss that costs and continues.

## B3. The named failure patterns

- **B3.1 Fetch/count quest.** "Quantity-based objectives (kill 10, collect 15, visit 8) feel like work when the number is arbitrary." Fix: quality over quantity, justify the number in fiction, keep counts to 3–5 rather than 15–20.
- **B3.2 Fake urgency.** "Don't fake urgency you won't enforce. If the village waits forever, don't say it won't." Fix: soft timers that *degrade* the situation; hard timers only where the stakes justify one — and then show it.
- **B3.3 Flat reward.** "The 50th 'here's 200 gold' reward has no impact." Vary the *kind* of reward: items, access, reputation, a change to the world, a person.
- **B3.4 Reward miscalibration.** A multi-stage quest paying what a trivial one pays tells the player their time is not valued. Scale to the challenge actually imposed, not to the length of the description.
- **B3.5 Volume over quality.** "40 well-designed quests that players remember are worth more than 200 forgettable ones."
- **B3.6 Special-case machinery.** See B1.3 — bespoke mechanics for one quest is what Avellone flags as "very risky".

## B4. Respecting the player's time and agency

- **B4.1 Target ~15 minutes.** Avellone's stated aim for a side quest. Size a colony-sim quest so it does not become the campaign.
- **B4.2 A quest should invite, not conscript.** RimWorld backs this: most quests must be *accepted*, and the acceptance timer is separate from the completion timer. Prefer offering; `autoAccept` is for events the player genuinely has no say in.
- **B4.3 Let the player opt out of rewards they do not want.** Tynan, 1.1.2598: "I'd like to reach a nice balance between creating varying experiences through randomized quest rewards, while also avoiding offering players rewards they're not interested in at all."
- **B4.4 Fit the quest to the state the colony is actually in.** 1.1.2610 shipped a wave of fixes that were all one idea — no mech-cluster or infestation quests at unreasonably low points; no Empire asker for hospitality under 240 points, "to avoid sending nobles when a colony can't realistically support them". Use `rootMinPoints`, `rootMinProgressScore` and `rootEarliestDay` rather than letting the player discover the mismatch.
- **B4.5 Never present a low-stakes errand during a crisis.** Timing is part of tone.
- **B4.6 Do not repeat yourself.** RimWorld already damps the last five quests to 1 %/30 %/50 %/70 %/90 %; add `minRefireDays` to anything with a memorable premise so the second telling does not cheapen the first.

## B5. How the text should read

- **B5.1 One sentence per objective.** "Players skim."
- **B5.2 The ask, the reward and the deadline must each be findable in one glance.** If any of the three is inferred rather than stated, rewrite.
- **B5.3 Cut what does not push the action forward** — but cut the *unnecessary*, not the necessary. Over-trimming buys brevity with confusion.
- **B5.4 Withhold deliberately, not accidentally.** Absence of information is a legitimate hook only when the player can act to obtain it; otherwise it is a bug wearing mystery.
- **B5.5 State the failure condition.** RimWorld quests normally fail by expiry, by the giver turning hostile, or by making peace with a faction you were meant to fight. If yours fails another way, say so in the description.

## B6. Pacing into a campaign

- **B6.1 Tension must vary, not climb.** Players remember the lowest and the highest points; the slopes between are what make the peaks readable.
- **B6.2 Size a quest to one sitting.** A game is paused mid-arc; a quest that cannot be finished in a session loses its tension across the save.
- **B6.3 Chain, don't sprawl.** A short escalating chain beats unrelated one-offs, and gives the delayed consequence from B2.3 somewhere to land.
- **B6.4 Let it change the world it sits in.** If nothing about the map, the factions or the colony differs afterwards, the quest sat *beside* the campaign instead of *in* it.
- **B6.5 Vary the verb.** If three consecutive quests resolve by shooting, one should have resolved by talking, building, hauling or hiding.

## B7. The draft checklist

Ten yes/no questions; a "no" is a rewrite, not a note.

1. Can I state in one sentence why the colony cares, without mentioning the reward?
2. Is there a decision with at least two defensible answers?
3. Does something later acknowledge which answer was given?
4. Can it be failed, and is failing survivable?
5. Is the reward proportional to the challenge actually imposed?
6. Is the deadline real, enforced and shown?
7. Can it be finished in one sitting?
8. Does it use only mechanics the game already has?
9. Are the ask, the reward and the deadline each findable in one glance?
10. Does every conditional grammar symbol have an unconditional fallback, and has the def taken one of the four firing routes? *(A5, A8)*

## B8. Sources for Part B

- https://www.gamedeveloper.com/design/designing-side-quests-study-these-7-games-and-some-chris-avellone-pointers- — Avellone's four rules; lessons from seven games.
- https://retsnom9.github.io/Quest-Design-Research/ — Genís Bayó's quest-design research: pillars, taxonomy, concealment of quest type, the pacing/tension model.
- https://www.strayspark.studio/blog/designing-quest-system-players-want-to-complete — fake urgency, soft vs hard timers, reward treadmill, quantity objectives, quest-log presentation.
- https://gamedevsjourney.substack.com/p/5-quest-design-lessons-from-cdpr — absence of information, noise vs signal, visible consequences, NPCs with their own goals.
- https://www.ttrpg-games.com/blog/side-quest-design-tips — hooks, quest chains, brevity.
- https://multigamedev.blogspot.com/2026/05/rpg-player-choices-how-to-make-decisions-matter.html — the four-part test for an authentic choice; delayed consequence.
- https://ludeon.com/blog/2020/04/update-1-1-2598-adds-configurable-quest-rewards-and-more/ — Tynan on opting out of unwanted rewards.

---

# Contested or unverified

- **`isRootRandomSelected`** — asked about as if it were a field; **[V]** it is a computed property in 1.6 and the string is not in the assembly. Use `randomlySelectable`.
- **`NaturalRandomQuestChance` / `QuestPointsCurve`** — referenced in write-ups; **[V]** neither string exists in 1.6. The real path is `NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight` plus `QuestTuning`.
- **How many vanilla QuestScriptDefs there are.** Two independent counts of the same install disagree — 156 vs 132 `<QuestScriptDef>` elements across `Data\` — depending on whether nested Royalty subfolders and multi-def utility files are swept. Neither number is load-bearing; **do not quote a count, count it when you need it.**
- **Quest cadence.** The wiki says "1 quest every 10 day interval" without Royalty and "2 every 12 days" with it — and flags it `[Verify]` itself. **[V]** `StorytellerComp_RandomQuest` derives from `StorytellerComp_OnOffCycle`, so cadence comes from `onDays`/`offDays`/`minSpacingDays`/`numIncidentsRange` per storyteller. Not measured here.
- **Web tutorials generally.** Only two quest-modding write-ups exist: the wiki page (undated, under review) and the Taranchuk wiki (Nov 2021, 1.3). **Nothing found on the open web covers 1.5 or 1.6 quest authoring**, and no open-source mod ships a README with quest-authoring advice — all five Vanilla Expanded quest repos have a one-line README. The local def dump and the DLC `QuestScriptDefs` folders are the current documentation.
- **Single-source design statistics.** The TTRPG-games article cites a "late 2025 indie team… 14 % increase in 7-day retention after reworking 30 % of fetch quests" with no primary source, and a "players should succeed about 70 % of the time" figure with none either. Direction plausible; numbers unusable.
- **"Ludeon gave up on proper quest structure."** The wiki's claim. **[V]** 44 of 88 top-level quest defs still use `QuestNode_Sequence`, so it is a drift, not an abandonment — though the newer expansions, and the newest 1.6-only Vanilla Expanded quest mods, are almost entirely single-custom-root.
