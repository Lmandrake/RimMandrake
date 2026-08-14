# RimWorld 1.6 quest corpus — how vanilla actually builds a quest

Researched 2026-08-14 from every shipped `QuestScriptDef` under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\` (Core, Royalty, Ideology, Biotech, Anomaly, Odyssey), plus field/enum/IL metadata read out of `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`. In tables only, `$D` abbreviates that `…\RimWorld\Data` path; section headings give it in full.

**Contents** — [1 Model](#1-the-model) · [2 Node inventory](#2-questnode-inventory-by-job) · [3 Simple walkthrough](#3-walkthrough-a--opportunitysite_peacetalks) · [4 Complex walkthrough](#4-walkthrough-b--pawnlend) · [5 Minimum viable quest](#5-minimum-viable-quest) · [6 Root fields](#6-root-level-fields-of-questscriptdef) · [7 Slate](#7-the-slate) · [8 Text](#8-text-rule-packs-symbols-suffixes) · [9 Signals & ending](#9-signals-and-how-a-quest-ends) · [10 Getting offered](#10-how-a-quest-gets-offered) · [11 Not determined](#11-open-questions--not-determined)

---

## 1. The model

A quest is **generated once, at offer time**, by running a tree of `QuestNode`s. That fills a **Slate** (a string→object dict of generation-time variables) and appends **`QuestPart`** objects to the live `Quest`. Afterwards the tree is gone; only the `QuestPart`s remain, and they are what ticks, listens and fires during play.

```
QuestScriptDef                     <- the def you author
 ├─ root = QuestNode_Sequence      <- tree, run ONCE at generation
 │    ├─ QuestNode_GetMap          <- writes slate var  map
 │    ├─ QuestNode_GetPawn         <- writes slate var  asker
 │    ├─ QuestNode_Delay           <- EMITS a QuestPart (ticks in play)
 │    └─ QuestNode_End             <- EMITS QuestPart_QuestEnd
 ├─ questNameRules / questDescriptionRules   <- grammar, resolved at the end
 └─ root-level fields                        <- when/whether it may be offered
```

At runtime the emitted `QuestPart`s talk **only by signal string** — `inSignal` to react, `outSignal…` to announce. That is the whole coupling, which is why quest logic reads flat.

🔴 **You never name a `QuestPart` in XML.** 249 `QuestPart_*` classes exist; grepping all 249 names against every XML file in the six modules returns **zero** matches. They are built only from C# in `QuestNode.RunInt()`. The XML surface is `QuestNode_*` via `Class="…"`. A mod needing a new QuestPart must ship a C# `QuestNode` to emit it.

Two root families: **XML-composed** (`root Class="QuestNode_Sequence"` with `<nodes>` — what you author) and **C#-composed** (`root Class="QuestNode_Root_WandererJoin_WalkIn"` and ~70 siblings, `$D\Core\Defs\QuestScriptDefs\Script_WandererJoins.xml:21`) where the tree is hardcoded and the def supplies only text and root flags. The latter is not extensible from XML.

`QuestNode_SubScript` calls another `QuestScriptDef` as a subroutine, passing `<parms>` into the callee's slate. The `Util_*` defs in `$D\Core\Defs\QuestScriptDefs\Scripts_Utility_*.xml` and `$D\Royalty\Defs\QuestScriptDefs\Utility\` are the shared library.

---

## 2. QuestNode inventory by job

307 `QuestNode_*` types exist in the assembly; ~130 appear in a shipped def. Useful subset below; every "used at" is a real line.

### 2.1 Structure, slate variables, arithmetic

| Node | Does | Used at |
|---|---|---|
| `QuestNode_Sequence` | Runs `<nodes>` in order. The normal `root`. | `$D\Core\...\Script_PeaceTalks.xml:34` |
| `QuestNode_SubScript` | Runs another `QuestScriptDef`. `def`, `parms`, `prefix`, `returnVarNames`, `allowNonPrefixedLookup`. | `$D\Core\...\Script_BanditCamp.xml:39` |
| `QuestNode_RandomNode` | Picks ONE child by each child's `selectionWeight`. | `$D\Core\...\Script_DownedRefugee.xml:54` |
| `QuestNode_Chance` | `chance` → `node`, else `elseNode`. | `$D\Royalty\...\Script_Hospitality_Utility.xml:109` |
| `QuestNode_LoopCount` | Repeat `node` `loopCount` times; `storeLoopCounterAs`. | `$D\Core\...\Scripts_Utility_ThreatsCore.xml:287` |
| `QuestNode_Set` | `name` = `value`; `convertTo` casts. 262 uses — the workhorse. | `$D\Core\...\Script_DownedRefugee.xml:56` |
| `QuestNode_Unset` / `SetAndRestore` | Remove a var / set it only for a subtree. | `$D\Royalty\...\Script_Hospitality_Worker.xml:843` |
| `QuestNode_AddToList` / `AddRangeToList` | Append to a slate list. | `$D\Royalty\...\Script_ChangeRoyalHeir.xml:73` |
| `QuestNode_Multiply` / `Add` / `Subtract` / `Divide` / `Clamp` / `MultiplyRange` | Arithmetic into `storeAs`. | `$D\Core\...\Script_BanditCamp.xml:122` |
| `QuestNode_EvaluateSimpleCurve` | `value` through an inline `curve` → `storeAs`. The standard points→reward map. | `$D\Core\...\Scripts_Utility_RewardsCore.xml:6` |
| `QuestNode_GetRandomInRangeForChallengeRating` / `SetChallengeRating` | Roll per star rating / force the rating. | `$D\Royalty\...\Script_PawnLend.xml:59` |
| `QuestNode_GetRandomElement(ByWeight)` / `SplitRandomly` | Random selection helpers. | `$D\Royalty\...\Script_Hospitality_Utility.xml:202` |

### 2.2 Map, world objects, sites

| Node | Does | Used at |
|---|---|---|
| `QuestNode_GetMap` | Choose a player map → slate `map`. `canBeSpace`, `preferMapWithMinFreeColonists`, `mustBeInfestable`, `layerWhitelist/Blacklist`. Nearly every map-side quest opens with it. | `$D\Core\...\Script_PeaceTalks.xml:41` |
| `QuestNode_GetSiteTile` | Pick a world tile. `preferCloserTiles`, `selectLandmarkChance`, `allowedLandmarks`. | `$D\Core\...\Script_PeaceTalks.xml:64` |
| `QuestNode_GetSitePartDefsByTagsAndFaction` → `GetDefaultSitePartsParams` → `GenerateSite` | The three-step site pipeline; last step normally via `Util_GenerateSite`. | `$D\Core\...\Script_BanditCamp.xml:92,101` |
| `QuestNode_GenerateWorldObject` | Any other world object by def. | `$D\Core\...\Script_PeaceTalks.xml:69` |
| `QuestNode_SpawnWorldObjects` | Actually place it. **Generate ≠ spawn.** | `$D\Core\...\Script_PeaceTalks.xml:75` |
| `QuestNode_DestroyWorldObject` / `DestroyOrPassToWorldOnCleanup` | Remove it. | `$D\Core\...\Script_PeaceTalks.xml:85` |
| `QuestNode_WorldObjectTimeout` | Object vanishes after `delayTicks` unless `inSignalDisable` fires; runs `node` when it does. `isQuestTimeout` makes it the quest's displayed timer. | `$D\Core\...\Script_BanditCamp.xml:136` |
| `QuestNode_NoWorldObject` | Run `node` if the object is already gone — the standard backstop fail. | `$D\Core\...\Script_EndGame_ShipEscape.xml:47` |
| `QuestNode_GetWalkInSpot` / `GetDropSpot` / `GetLargestClearArea` | Map positions for arrivals. | `$D\Core\...\Scripts_JoinerThreatCore.xml:74` |

### 2.3 Pawns, things, factions, threats

| Node | Does | Used at |
|---|---|---|
| `QuestNode_GetPawn` | Find (or with `canGeneratePawn`, make) an existing pawn — the `asker`. 23 filters incl. `mustBeFactionLeader`, `mustHaveRoyalTitleInCurrentFaction`, `seniorityRange`, `hostileWeight`. | `$D\Core\...\Script_BanditCamp.xml:55` |
| `QuestNode_GeneratePawn` | New pawn from `kindDef` → `storeAs`. `forcedTraits`, `fixedGender`, `allowPregnant`, `mustBeCapableOfViolence`. | `$D\Core\...\Scripts_Utility_RewardsCore.xml:71` |
| `QuestNode_GeneratePawnRandDevelopmentStage` | Same, rolling `childChance`/`adultChance`. | `$D\Core\...\Scripts_Utility_RewardsCore.xml:31` |
| `QuestNode_GenerateThing` / `GenerateThingSet` | One thing by def / a `ThingSetMakerDef` roll with `totalMarketValueRange`. | `$D\Core\...\Scripts_Utility_RewardsCore.xml:111` |
| `QuestNode_PawnsArrive` | Pawns walk or drop in. `arrivalMode`, `joinPlayer`, custom letter. | `$D\Core\...\Scripts_Utility_RewardsCore.xml:42` |
| `QuestNode_DropPods` | Drop `contents` in pods with a letter. | `$D\Core\...\Scripts_Utility_RewardsCore.xml:124` |
| `QuestNode_Leave` / `LeaveOnCleanup` | Send quest pawns away. | `$D\Royalty\...\Scripts_Permits.xml:65` |
| `QuestNode_GetFaction` | Pick a faction (`allowEnemy`, `mustBePermanentEnemy`…). **No-op if the var is already set.** | `$D\Core\...\Script_PeaceTalks.xml:45` |
| `QuestNode_GetFactionOf` / `GetPlayerFaction` / `ExtraFaction` | Faction of a thing / the player's / a temporary quest-scoped faction. | `$D\Core\...\Script_TradeRequest.xml:51` |
| `QuestNode_AddHediff` / `DamageUntilDowned` / `BiocodeWeapons` / `MakeMinified` | Post-process generated pawns and things. | `$D\Royalty\...\Script_Hospitality_Utility.xml:114,127` |
| `QuestNode_Raid` | A raid, normally via `Util_Raid`. `arrivalMode`, `raidPawnKind`, `inSignalLeave`. | `$D\Core\...\Scripts_Utility_ThreatsCore.xml:208` |
| `QuestNode_SpawnMechCluster` / `ManhunterPack` / `Infestation` | Other threats. | `$D\Core\...\Scripts_Utility_ThreatsCore.xml:236` |
| `QuestNode_GameCondition` | Start a `GameConditionDef` for `duration`. | `$D\Royalty\...\Utility\Scripts_Utility_Threats.xml:230` |
| `QuestNode_CreateIncidents` | `randomIncidents` copies of an `incidentDef` spread over time. | `$D\Royalty\...\Script_Hospitality_Worker.xml:252` |
| `QuestNode_ChangeFactionGoodwill` / `RecordHistoryEvent` | `change` + `reason` / fire a `HistoryEventDef` (Ideology precept hooks). | `$D\Royalty\...\Scripts_Permits.xml:88` |

### 2.4 Conditions (all take `node` / `elseNode`), signals, outcomes, text

| Node | Does | Used at |
|---|---|---|
| `QuestNode_IsSet` / `IsNull` / `IsTrue` / `IsTrueOrUnset` / `IsZero` | Slate var present, null, boolean-ish. | `$D\Core\...\Scripts_Utility_ThreatsCore.xml:16`, `:293` |
| `QuestNode_Equal` / `Greater` / `Less` / `…OrEqual` | Compare `value1`/`value2`; `compareAs` forces `int`. | `$D\Core\...\Scripts_Utility_ThreatsCore.xml:322` |
| `QuestNode_EqualOrFail` / `GreaterOrFail` / `LessOrFail` / `CannotRun` | Same, but **abort generation** when false. | `$D\Royalty\...\Script_Hospitality_Worker.xml` |
| `QuestNode_ViolentQuestsAllowed` | Pacifist/no-violence check. **Wrap every threat in it.** | `$D\Core\...\Script_ItemStash.xml:104` |
| `QuestNode_ExpansionActive` / `ModIsActive` | DLC / mod present. | `$D\Royalty\...\Script_PawnLend.xml:66` |
| `QuestNode_QuestUnique` | Abort if a live quest already holds `tag` (optionally per `faction`). | `$D\Core\...\Script_EndGame_ShipEscape.xml:23` |
| `QuestNode_FactionExists` / `WorkDisabled` / `ChildrenAllowed` / `HasRoyalTitleInCurrentFaction` | Situational gates. | `$D\Royalty\...\Scripts_Permits.xml:36` |
| `QuestNode_Signal` | On `inSignal`, run `node` — every time it fires. `outSignals` re-broadcasts; `inSignalDisable` switches it off. | `$D\Core\...\Script_BanditCamp.xml:156` |
| `QuestNode_SignalActivable` | Same, but starts **disabled**; `inSignalEnable`/`inSignalDisable` gate it to one phase. | `$D\Royalty\...\Script_ChangeRoyalHeir.xml:116` |
| `QuestNode_SendSignals` | Emit `outSignals` now (or formatted, `outSignalsFormat`). | `$D\Core\...\Scripts_Utility_ThreatsCore.xml:326` |
| `QuestNode_Delay` | After `delayTicks`, run `node` and emit `outSignalComplete`. `inSignalEnable/Disable`, `reactivatable`, `isQuestTimeout`, `waitUntilPlayerHasHomeMap`, `expiryInfoPart`. | `$D\Core\...\Script_TradeRequest.xml:139` |
| `QuestNode_AnySignal` / `AllSignals` | OR / AND over `inSignals`. | `$D\Odyssey\...\Script_Site.xml:182` |
| `QuestNode_End` | **The only exit.** See §9.1. | `$D\Core\...\Script_BanditCamp.xml:198` |
| `QuestNode_GiveRewards` | Standard reward chooser. Reads slate `rewardValue`; `parms.allowGoodwill`/`allowRoyalFavor`/`giveToCaravan`, `chosenPawnSignal` + `nodeIfChosenPawnSignalUsed` for "who gets the favor". | `$D\Core\...\Script_BanditCamp.xml:178` |
| `QuestNode_AddItemsReward` / `AddPawnReward` / `CampLootReward` | Register a specific reward in the quest's reward list. | `$D\Core\...\Script_ItemStash.xml:165` |
| `QuestNode_EndGame` | Ends the *game* (ship escape, archonexus), not the quest. | `$D\Core\...\Script_EndGame_ShipEscape.xml` |
| `QuestNode_Letter` | Send a letter — see §8. 88 uses (Core 9, Royalty 69, Odyssey 10; **none in Ideology/Biotech/Anomaly**). | `$D\Core\...\Script_BanditCamp.xml:144` |
| `QuestNode_Message` | On-screen message; `inSignal`, `messageType`, `text`, `rules`, `lookTargets`. Exactly **one** vanilla use. | `$D\Royalty\...\Script_BuildMonument_Worker.xml:149-153` |
| `QuestNode_InspectString` | Text on the quest object's inspect pane, e.g. `Time left: {0}`. | `$D\Royalty\...\Scripts_Permits.xml:108` |
| `QuestNode_ResolveTextNow` | Resolve an inline `rules` pack **during generation** into a stored string, so one phrase can be reused verbatim later. `root`, `storeAs`, `rules`. | `$D\Royalty\...\Script_PawnLend.xml:111` |
| `QuestNode_Log` / `SlateDump` | Debug. `SlateDump` prints the whole slate — fastest way to learn what a sub-script left behind. | never used in vanilla |

---

## 3. Walkthrough A — `OpportunitySite_PeaceTalks`

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\QuestScriptDefs\Script_PeaceTalks.xml` (111 lines). The teaching example: 100% XML, only general-purpose nodes, and the complete arc — setup, timeout-fail, signal-success — with nothing domain-specific in the way.

| Lines | What it does |
|---|---|
| 4–8 | `defName`; `rootSelectionWeight 1` (eligible for the random pool); `rootMinProgressScore 10` (not on a young colony); `autoAccept true` (no accept dialog); `defaultChallengeRating 1`. |
| 9–19 | `questNameRules`. `questName` is the root symbol; `[peaceTalks]` resolves from the same pack, `[faction_leader_nameDef]` from the slate. |
| 20–32 | `questDescriptionRules`. Line 25 `favorRewardDetails(faction_leader_royalInCurrentFaction==True,priority=1)` is a **conditional rule**; line 26 is its empty fallback. Line 27 carries `MayRequire="Ludeon.RimWorld.Ideology"` so it vanishes without that DLC. |
| 34–35 | `root Class="QuestNode_Sequence"` + `<nodes>` — the tree begins. |
| 36–39 | `QuestNode_Set` writes `siteDistRange = 5~13`. `QuestNode_GetSiteTile` reads that conventionally-named var rather than taking it as a field. |
| 41–43 | `QuestNode_GetMap` → slate `map` (implicit default name). Everything downstream picks it up from there. |
| 45–53 | `QuestNode_GetFaction` → `faction`, filtered (`allowEnemy`, `leaderMustBeSafe`, `peaceTalksCantExist`). **If nothing qualifies, generation aborts** and the storyteller tries another quest. |
| 55–57 | `QuestNode_GetPlayerFaction` → `playerFaction`, purely so the text can say `[playerFaction_leader_nameFull]`. |
| 59–62 | `QuestNode_QuestUnique` `tag PeaceTalks` + `faction` — refuses a second peace-talks quest with the same faction. |
| 64–67 | `QuestNode_GetSiteTile` → `tile`; `selectLandmarkChance 0` = plain tile. |
| 69–74 | `QuestNode_GenerateWorldObject` `def PeaceTalks` at `$tile`, owned by `$faction` → slate `peaceTalks`. Generated, **not placed**. |
| 75–78 | `QuestNode_SpawnWorldObjects` places it. Splitting the two lets earlier nodes fail without leaving litter on the planet. |
| 80–83 | `QuestNode_Delay` 12–28 days (`$(randInt(12,28)*60000)`; 60000 ticks = 1 day), emitting `PeaceTalksTimeout`. First node that leaves a `QuestPart` behind to tick in play. |
| 85–88 | `QuestNode_DestroyWorldObject` on `inSignal PeaceTalksTimeout` — clears the marker. |
| 89–102 | `QuestNode_Signal` on the same signal → `QuestNode_Letter` (using `[resolvedQuestName]`) then `QuestNode_End outcome Fail`. The canonical expire-fail pair. |
| 104–107 | `QuestNode_End inSignal peaceTalks.Resolved outcome Success`. `peaceTalks` is the slate var from line 73; `.Resolved` is emitted by that world object's own code. **Signal names are `<slateVarName>.<Suffix>`.** |

Transferable: nodes communicate through **conventionally named slate vars** (`map`, `faction`, `asker`, `rewardValue`); **generate and spawn are separate**; the quest has exactly two exits, both `QuestNode_End`, both signal-driven.

---

## 4. Walkthrough B — `PawnLend`

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Royalty\Defs\QuestScriptDefs\Script_PawnLend.xml` (310 lines). Generation-time branching, parameterised sub-scripts, five-way runtime fan-out.

**Generation-time branch (99–164).** `QuestNode_RandomNode` picks one of two `QuestNode_Sequence` children at 0.5 weight each — a faction-leader asker (104–110) or a royal asker (134–142). Each branch does two things so the rest of the file can be written once: `QuestNode_ResolveTextNow` (111–124 / 143–156) resolves a private rule pack *now* and stores a plain string, without which the phrase would be re-rolled in every later letter; and `QuestNode_Set` (125–128 / 157–160) stores `returnLetterText` — **an entire letter body as a slate variable**, used verbatim at line 283 (`<text>$returnLetterText</text>`).

**Guarded pre-acceptance exit (90–94).** `QuestNode_End inSignal map.MapRemoved` with `signalListenMode NotYetAcceptedOnly` kills the offer if the map is lost before acceptance, without touching an accepted quest.

**Parameterised sub-script (193–205).** `QuestNode_SubScript def Util_TransportShip_Pickup` with `<parms>` (`requireColonistCount`, `onlyAcceptHealthy`, `minAge`…). Parms are written into the callee's slate; the callee writes back `pickupShipThing`, which every later branch reads. **Nothing declares that contract** — read the callee (`$D\Royalty\Defs\QuestScriptDefs\Scripts_Utility_TransportShip.xml`) first. Lines 189–214 wrap it in `QuestNode_ShuttleDelay`, so those `QuestPart`s are not created until the shuttle is due.

**Runtime fan-out** — six independent listeners, each a complete outcome path:

| Lines | Signal | Result |
|---|---|---|
| 217–230 | `pickupShipThing.Destroyed` | letter + `End Fail` |
| 233–246 | `pickupShipThing.LeftBehind` | letter + `End Fail` |
| 249–275 | `pickupShipThing.SentSatisfied` | `QuestNode_LendColonistsToFaction` (declaring `outSignalComplete ColonistsReturned` and `outSignalColonistsDied ColonistsDied`), then a short `QuestNode_Delay` before `QuestNode_GiveRewards` |
| 277–291 | `ColonistsReturned` | letter + `End Success` |
| 293–298 | `ColonistsDied` | `End Success` — the contract was still fulfilled |
| 300–305 | `pickupShipThing.SentUnsatisfied` | `End Fail` |

Lines 257–258 are the whole branching mechanism: a node **declares its own outgoing signal names**, and a later sibling listens for them. No goto, no state machine — just names agreeing.

---

## 5. Minimum viable quest

Smallest tree that generates, appears, is completable and can fail. Every line is load-bearing.

```xml
<?xml version="1.0" encoding="utf-8" ?>
<Defs>
  <QuestScriptDef>
    <defName>Jawa_TinyQuest</defName>
    <rootSelectionWeight>1</rootSelectionWeight>   <!-- 0 = never randomly offered -->
    <rootMinPoints>0</rootMinPoints>
    <expireDaysRange>4~8</expireDaysRange>         <!-- accept window -->
    <questNameRules>
      <rulesStrings><li>questName->A small favour</li></rulesStrings>
    </questNameRules>
    <questDescriptionRules>
      <rulesStrings><li>questDescription->Hold out for [waitTicks_duration] and we will pay you.</li></rulesStrings>
    </questDescriptionRules>
    <root Class="QuestNode_Sequence">
      <nodes>
        <li Class="QuestNode_GetMap" />                                        <!-- slate: map -->
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
          <inSignal>WaitDone</inSignal><outcome>Success</outcome><sendStandardLetter>true</sendStandardLetter>
        </li>
        <li Class="QuestNode_End"><inSignal>map.MapRemoved</inSignal><outcome>Fail</outcome></li>
      </nodes>
    </root>
  </QuestScriptDef>
</Defs>
```

Irreducible: **`defName`**, **`root`**, **at least one runtime-reachable `QuestNode_End`**, and **`questNameRules` + `questDescriptionRules`** — even fully hidden vanilla quests supply placeholder strings rather than omit the fields (`$D\Anomaly\Defs\QuestScriptDefs\Script_SightstealerArrival.xml:11-20`). `QuestNode_GetMap` is required by anything touching a map. `rewardValue` is a **slate var** `QuestNode_GiveRewards` consumes — not a field on that node.

⚠️ **Not verified in-game.** Assembled from the corpus, not launched. Prove it on a load round.

---

## 6. Root-level fields of `QuestScriptDef`

Complete list, read from the assembly's `Field` metadata (43 XML-facing fields + 3 private caches). "Uses" counts direct children across all six modules.

| Field | Type (inferred) | Meaning | Typical values | Uses · example |
|---|---|---|---|---|
| `root` | `QuestNode` | The node tree. **Required.** | `QuestNode_Sequence` or `QuestNode_Root_*` | 151 · `$D\Core\...\Script_PeaceTalks.xml:34` |
| `rootSelectionWeight` | float | Weight in the natural random quest chooser. `0` = never picked randomly. | `0`, `0.15`, `0.5`, `1`, `1.1` | 64 · `Script_TradeRequest.xml:6` |
| `rootSelectionWeightFactorFromPointsCurve` | `SimpleCurve` | Scales that weight by threat points. | — | 1 · `$D\Royalty\...\Script_Hospitality_Refugee.xml:7` |
| `rootMinPoints` | float | Minimum storyteller threat points to be offered. | `0`, `150`, `350`, `500` | 38 · `Script_BanditCamp.xml:7` |
| `rootMinProgressScore` | int | Minimum colony progress score. | `3`–`10` | 13 · `Script_PeaceTalks.xml:6` |
| `rootEarliestDay` | int | Earliest game day. | `45` | 1 · `$D\Odyssey\...\Script_AlphaThrumboSighting.xml:14` |
| `rootIncreasesPopulation` | bool | Marks it as adding colonists, so population intent weights it. | `true` | 9 · `Scripts_JoinerThreatCore.xml:35` |
| `randomlySelectable` | bool | Whether the random chooser may pick it at all. | `false` | 12 · `Script_AlphaThrumboSighting.xml:6` |
| `givenBy` | `List<QuestGiverTag>` | Who hands it out. Enum: `Traders`, `OrbitalScanner`, `Reading`, `Beggars`. | `<li>Traders</li>` | 12 · `Script_AlphaThrumboSighting.xml:7` |
| `minRefireDays` | float | Cooldown before this script may fire again. | `30`–`300` | 7 · `$D\Anomaly\...\Script_MysteriousCargo.xml:8` |
| `isRootSpecial` | bool | Excluded from the ordinary random pool — fired by an incident or by code. | `true` | 48 · `Script_WandererJoins.xml:8` |
| `autoAccept` | bool | Skip the accept step; quest starts active. | `true` | 56 · `Script_ItemStash.xml:7` |
| `expireDaysRange` | `FloatRange` | How long the *offer* stays open. | `2`, `4~8`, `20~30`, `0.4~0.6` | 32 · `Script_BanditCamp.xml:9` |
| `defaultChallengeRating` | int | Star rating shown to the player. | `1`, `3`, `4` | 22 · `Script_TradeRequest.xml:8` |
| `defaultHidden` | bool | Does not appear in the Quests tab. | `true` | 19 · `Script_WandererJoins.xml:7` |
| `hideOnCleanup` | bool | Hide once ended. | `true` | 1 · `$D\Ideology\...\Script_EndGame_ArchonexusVictory.xml:27` |
| `hideInvolvedFactionsInfo` | bool | Suppress the faction list on the quest card. | `true` | 5 · `$D\Ideology\...\Script_Beggars.xml:10` |
| `canGiveRoyalFavor` | bool | Reward roll may include royal favor. | `true` | 12 · `Script_BanditCamp.xml:8` |
| `defaultCharity` | bool | Ideology: counts as a charity opportunity. | `true` | 14 · `Script_TransportPodCrash.xml:7` |
| `affectedByPopulation` / `affectedByPoints` | bool | Selection weight responds to population intent / threat points. | `true` / `false` | 4 / 4 · `Script_Beggars.xml:9` |
| `successHistoryEvent` / `failedOrExpiredHistoryEvent` | `HistoryEventDef` | Fired on `Success` / on `Fail`+expiry. | `Raided_BanditCamp`, `CharityRefused_*` | 22 / 14 · `Script_BanditCamp.xml:10` |
| `sendAvailableLetter` | bool | Send the "quest available" letter. | `false` | 5 · `$D\Ideology\...\Script_WorkSite.xml:9` |
| `questAvailableLetterLabel` / `questAvailableLetterDef` / `questAvailableLetterTextIsDescription` | string / `LetterDef` / bool | Override that letter's label, type, or use the description as its body. | `NewQuest_ThreatBig`, `true` | 9 / 1 / 14 · `$D\Odyssey\...\Script_GravShip.xml:73-75` |
| `epic` / `epicParent` | bool / `QuestScriptDef` | Multi-stage chains (Ideology relic hunt). | `true` / `RelicHunt` | 1 / 4 · `$D\Ideology\...\Script_RelicHunt.xml:10` |
| `endOnColonyMove` | bool | End if the colony relocates. | `false` | 2 · `Script_EndGame_ArchonexusVictory.xml:10` |
| `everAcceptableInSpace` | bool | May be accepted on a space map. | `true` | 13 · `Script_BanditCamp.xml:11` |
| `canOccurOnAllPlanetLayers` | bool | Ignore layer restrictions. | `true` | 18 · `Script_GravShip.xml:75` |
| `decreeSelectionWeight` / `decreeTags` | float / list | Royalty decree pool only. | `1` | 1 each · `$D\Royalty\...\Decree\Scripts_Decree.xml:5` |
| `questNameRules` / `questDescriptionRules` | `RulePack` | Root symbols `questName` / `questDescription`. | — | 107 / 121 |
| `questDescriptionAndNameRules` | `RulePack` | Rules shared by both packs. | — | 12 · `$D\Anomaly\...\Script_DistressCall.xml:20` |
| `questContentRules` | `RulePack` | Rules available to letters/messages inside the quest. | — | 26 · `Script_Beggars.xml:103` |
| `questSubjectRules` | `RulePack` | Rules for the quest "subject" (`{SUBJECT_definite}` in letters). | — | 11 · `Script_AlphaThrumboSighting.xml:27` |
| `nameMustBeUnique`, `neverPossibleInSpace`, `layerWhitelist`, `layerBlacklist` | bool, bool, 2× `List<PlanetLayerDef>` | Exist on the class. | — | **0 — set by no shipped def** (the same-named fields on `QuestNode_GetMap` *are* used) |

⚠️ **Defaults not determined** — initialisers live in constructor IL, not decompiled. From usage, `rootSelectionWeight`/`rootMinPoints` behave as 0 and booleans as `false`, except `randomlySelectable`, only ever set to `false`, so its default is almost certainly `true`.

---

## 7. The Slate

- `storeAs` (or a node's implicit default name) writes a slate var; `$name` reads it anywhere a field value is expected. **`$name` is a node-field reference; `[name_suffix]` is a grammar symbol in a rule string. Same variable, different syntax, different position.**
- **Paths** use `/`: `$site/sitePartDefs` reaches into a nested slate left by a prefixed sub-script (`$D\Core\...\Script_BanditCamp.xml:104`).
- **Expressions**: `$( … )` evaluates arithmetic plus `randInt(a,b)`, `randFloat(a,b)`, `roundToTicksRough(x)` — `$(randInt(12,28)*60000)` (`Script_PeaceTalks.xml:81`), `$($requestedThingMarketValue * $wealthRewardValueFactor * randFloat(1.5, 2.1))` (`Script_TradeRequest.xml:104`).
- **Dynamic var names**: `$raid(($raidLoopCounter))/raidDelayTicks` (`$D\Core\...\Scripts_Utility_ThreatsCore.xml:294`) — the inner `(( ))` substitutes first, giving `raid0/raidDelayTicks`, `raid1/…`.
- **`prefix` on `QuestNode_SubScript`** namespaces everything the callee writes, so one sub-script can loop without collisions (`Scripts_Utility_ThreatsCore.xml:307`, `<prefix>raid$raidLoopCounter</prefix>`). `allowNonPrefixedLookup` lets it still *read* outer vars.
- **Conventional names other nodes silently expect**: `map`, `asker`, `rewardValue`, `points`, `enemyFaction`, `site`, `siteTile`, `siteFaction`, `sitePartsParams`, `walkInSpot`, `customLetterLabel`/`customLetterText`(`Rules`). Convention only — grep the consumer first.
- **1 day = 60000 ticks.** Every `delayTicks` in the corpus is a multiple of it.

---

## 8. Text: rule packs, symbols, suffixes

All five `*Rules` fields are `Verse.Grammar.RulePack` — a plain class inlined in the def, **not** a `RulePackDef`. Its four XML-writable members are `rulesStrings`, `rulesFiles`, `rulesRaw`, `include`. Inside quest blocks vanilla uses `rulesStrings` 226×, `include` 9×, `rulesFiles` 3×. All occurrences are direct children of `<QuestScriptDef>`; **these are never fields of a node.**

```xml
<questNameRules>                                    <!-- shape A: inline -->
  <rulesStrings><li>questName->The [bandit] [camp]</li></rulesStrings>
</questNameRules>
<questDescriptionRules>                             <!-- shape B: share a RulePackDef -->
  <include><li>QuestConstructionDescriptionCommon</li></include>
  <rulesStrings><li>commonEnding->…</li></rulesStrings>
</questDescriptionRules>
```
(`$D\Royalty\Defs\QuestScriptDefs\BuildMonument\Script_BuildMonument_Root_Basic.xml:12-24`.) The idiom: the shared pack owns the root symbol and calls out to a leaf symbol (`commonEnding`) that each quest supplies. ⚠️ **Shared quest packs do NOT live in `Defs\RulePackDefs\`** — all three that quests actually `include` sit beside the quests: `QuestConstructionNameCommon` and `QuestConstructionDescriptionCommon` at `$D\Royalty\Defs\QuestScriptDefs\BuildMonument\Script_BuildMonument_TextCommon.xml:5,41`, and `QuestHospitalityCommon` at `$D\Royalty\...\Hospitality\Script_Hospitality_TextCommon.xml:5`. The 337 defs in `Defs\RulePackDefs\` are namers and combat logs; none is included by a quest. `rulesFiles` points at `Languages\<lang>\Strings\…` without the extension (`$D\Odyssey\Defs\QuestScriptDefs\Script_SpaceSites.xml:182-184`).

**Rule syntax**, from the parse regex in `Verse.Grammar.Rule_String`: `keyword ( param OP value , … ) -> output`.
- Separator is `->`. `\n` in the text becomes a newline; a rule may continue on the next physical line (`Script_BanditCamp.xml:33-34`). `MayRequire="…"` on an `<li>` drops it without the DLC.
- **Reserved parameters, assigned with `=`**: `p`, `priority`, `tag`, `requiredTag`, `uses`, `debug`. Using `==` on one of them throws.
- **Weight is `(p=N)`** — there is no `[weight]` prefix form. `constAdj(p=20)` (`Script_BuildMonument_TextCommon.xml:12`), fractional allowed: `questName(p=0.5)` (`$D\Odyssey\...\Script_Site.xml:14`). `priority=N` is a **separate** mechanism — higher priority wins outright rather than being weighted in. Idiom: a `(priority=-999)` empty default plus conditional overrides (`$D\Royalty\...\Script_Hospitality_TextCommon.xml:15-17`).
- Anything else is a **constant constraint**, operators `==` `!=` `>` `<` `>=` `<=` plus the XML-safe `[less_than]`/`[greater_than]`. Order is free, weight and constraints mix: `lodgerIndef(asker_royalInCurrentFaction==True,lodgersCount==1,p=3)`.
- An **empty fallback** rule (`<li>travelTime-></li>`, `Script_TradeRequest.xml:35`) is how an optional sentence is expressed; without it that symbol fails to resolve.
- Root symbols: `questName`, `questDescription`, and `root` for `QuestNode_Letter`/`_Message` rule packs.

**How a slate var becomes `[symbol]` — you do nothing but name it.** `QuestGenUtility.AddSlateVars` scans every rule output for `[ … ]`, then `AddSlateVar` **progressively trims** the bracketed text until it hits a slate key: try the whole string; strip trailing digits; else truncate at the last `_`; repeat. That is why `[timeoutTicks_duration]` works (trim `_duration` → `timeoutTicks` hits, `$D\Core\...\Script_LongRangeMineralScannerLump.xml:137-140` sets it, `:37` uses it), and why `[lodgers0_nameDef]` works (trim `_nameDef`, trim `0` → `lodgers` is a `List<Pawn>`, whose elements are re-registered as `lodgers0`, `lodgers1`, …).

Suffixes are not a fixed enum — each is `<varName>_<field>` emitted by a `GrammarUtility.RulesFor*` method chosen by the value's type:

| Slate value | Suffixes emitted |
|---|---|
| `Pawn` | `nameFull nameDef nameIndef label labelNoParenthesis definite indefinite pronoun possessive objective gender genderResolved kind kindPlural title titleIndef titleDef age chronologicalAge factionName faction factionLeader royalTitle(+Indef/Def) royalTitleFaction royalTitleInCurrentFaction(+Indef/Def) royalInCurrentFaction bestRoyalTitle(+Indef/Def) bestRoyalTitleFaction relationInfo formerlyColonist(Info) flesh` — **and recurses as `<var>_faction` → Faction rules** |
| `Def` | `label labelPlural description definite indefinite possessive` (+ a constant = `defName`) |
| `Faction` | `name pawnSingular(+Def/Indef) pawnsPlural(+Def/Indef) leaderTitle royalFavorLabel temporary hasLeader` — **recurses as `<var>_leader` → Pawn rules** |
| `Thing` | `quality` + its def's rules · `WorldObject`/`Map` → `label definite indefinite` |
| `Ideo` / `Precept` / `HediffDef` / `BodyPartRecord` | `name memberName(Plural)` / `name` / `label labelNoun labelNounPretty` / `label definite indefinite possessive` |
| `IEnumerable` | bulleted or comma list, `_count` (also a constant), plus per-element `<var>0`, `<var>1`, … |
| **any value** | `_duration` (ticks→"3 days", if int-convertible) · `_money` · `_percent` · `_average` `_min` `_max` (FloatRange) · `_count` |

Chains go three deep: `[asker_faction_leaderTitle]` (41 uses, `Script_BanditCamp.xml:33`) is slate `asker` → `.Faction` → `leaderTitle`. **Bare `[asker]` / `[map]` never appear** — a slate object is always referenced with a suffix. Constants (`Def`→`defName`, `Faction`→`def.defName`, primitives→`ToString()`, list→`_count`) are what `(name==value)` rule conditions test.

⚠️ **These plausible suffixes do not exist**: `_ticksToDays` (use `_duration`), `_labelDefinite`/`_labelIndefinite` (`_definite`/`_indefinite` *replace* `_label`), `_kindDef` (it is `_kind`). ⚠️ `[a_b]` is only a resolver call when `a` is a slate var — `reason_AI->…` at `$D\Odyssey\...\Script_OrbitalFugitive.xml:36-39` is an atomic keyword that merely has an underscore. ⚠️ Some symbol roots are injected from C# with no `<storeAs>` anywhere (`worker`, `targetMineable` in `Script_LongRangeMineralScannerLump.xml`) — you have not missed a line. `[resolvedQuestName]` is the already-resolved quest name, available in letters.

**`TKey`** on `<label>`/`<text>` is a translation-key alias. Without it a string is addressed by positional path (`root.nodes.16.node.nodes.2.label`), which breaks the moment a node is inserted; `TKey="LetterLabelMonumentCompleted"` survives. **Optional** — of 88 `QuestNode_Letter` blocks, 83 labels carry one; vanilla omits it when the value is a pure slate ref (`<text>$customLetterText</text>`, nothing to translate). Convention: PascalCase, `Letter`+`Label`|`Text`+`<Event>`, unique per def, not globally. It also applies to `QuestNode_Message.text`, `QuestNode_Delay`, `QuestNode_GiveRewards`, `QuestNode_Set.value`, `QuestNode_SubScript` parms and more.

**`QuestNode_Letter` fields** (15 total, 11 exercised by vanilla): `label`, `text` (88 uses each), `letterDef` 45 (`PositiveEvent`/`NegativeEvent`/`ChoosePawn`), `lookTargets` 9, `inSignal` 5, `chosenPawnSignal` 2, `filterDeadPawnsFromLookTargets` 2, `useColonistsOnMap` 1, `useColonistsFromCaravanArg` 1, `signalListenMode` 1, `labelRules`/`textRules` 1 each; plus `relatedFaction`, `acceptedVisitorsSignal`, `visitors` — **never used in vanilla XML**. The player-picks-a-colonist idiom is `letterDef ChoosePawn` + `useColonistsOnMap` + `chosenPawnSignal` matching a `<parms><chosenPawnSignal>` on the parent `QuestNode_GiveRewards` (`Script_BanditCamp.xml:182,187-193`). The fully rule-driven form used by reusable sub-scripts — `label`/`text` as `$vars` plus `labelRules`/`textRules` — is at `$D\Royalty\...\Utility\Scripts_Utility_Threats.xml:197-204`.

**Curly-brace symbols** (`{PAWNS}`, `{SUBJECT_definite}`, `Script_PawnLend.xml:127`) are a different substitution layer filled by the emitting `QuestPart`. Do not invent new ones.

---

## 9. Signals and how a quest ends

A signal is a plain string. At runtime `QuestGenUtility.HardcodedSignalWithQuestID` prefixes it with the quest's ID, so the same name in two concurrent quests is two distinct signals — cross-quest collisions are impossible.

**Object signals — `<slateVarName>.<Suffix>`.** The var name is yours; the suffix is fixed. The assembly declares exactly **75** `QuestTargetSignalPart_*` constants — the complete legal set:

`Activated AllEnemiesDefeated AllHivesDestroyed AllPawnsLost Arrested Banished BecameMutant BeingAttacked CeremonyDone CeremonyExpired CeremonyFailed ChangedFaction ChangedFactionToNonPlayer ChangedFactionToPlayer ChangedHostFaction CoreDefeated Despawned Destroyed Enslaved ExitMentalState FactionBecameHostileToPlayer FactionBuiltBuilding FactionMemberArrested FactionPlacedBlueprint Fleeing Hacked HackingStarted Inspected Kidnapped Killed KilledLeavingsLeft LaunchedShip LeftBehind LeftMap LockedOut MapGenerated MapRemoved MapSettled MonumentCancelled MonumentCompleted MonumentDestroyed NoActiveThreats NoLongerFactionLeader NodeClosed PeaceTalksResolved PlayerTended PsychicRitualTarget QuestEnded RanWild ReactorDestroyed ReceivedItems Recruited Released Rescued ShipArrived ShipDisposed ShipFlewAway ShipThingAdded ShuttleSentSatisfied ShuttleSentUnsatisfied ShuttleSentWithExtraColonists ShuttleUnloaded Spawned StartedExtractingFromContainer Studied SurgeryViolation SwappedMap TitleAwardedWhenUpdatingChanged TitleChanged TookDamage TookDamageFromPlayer TradeRequestFulfilled Unfogged XenogermAbsorbed XenogermReimplanted`

Those a shipped def listens for, by frequency: `.MapGenerated` 20 (`$D\Core\...\Script_PrisonerWillingToJoin.xml:127`), `.Destroyed` 19 (`Script_BanditCamp.xml:157`), `.MonumentCompleted` 15 (`$D\Royalty\...\Script_ChangeRoyalHeir.xml:92`), `.MapRemoved` 10 (`Script_PawnLend.xml:91`), `.LeftBehind` 8 (`Script_PawnLend.xml:234`), `.BecameHostileToPlayer` 8 (`Script_TradeRequest.xml:56`), `.SentSatisfied` 7, `.SentUnsatisfied` 6, `.AllEnemiesDefeated` 5 (`Script_BanditCamp.xml:172`), then `.Resolved` (`Script_PeaceTalks.xml:105`), `.TradeRequestFulfilled` (`Script_TradeRequest.xml:118`), `.SurgeryViolation`, `.Arrested`, `.Recruited`, `.RanWild`, `.Kidnapped`, `.TitleChanged`, `.LaunchedShip`.

🔴 **`.Killed` has no XML precedent — vanilla uses `.Destroyed` for "the quest pawn died"** (`Script_ChangeRoyalHeir.xml:117`, `titleHolder.Destroyed`). About 40 of the 75 suffixes are wired only from C# roots and appear in no shipped def (`.Killed .Hacked .Studied .Activated .Spawned .Unfogged .CoreDefeated .TookDamage .Inspected .Released .Rescued .Banished .AllPawnsLost` and others). Valid, but nothing to copy.

🔴 **There is no `Quest.Accepted` or `Quest.Ended` signal in XML.** Acceptance is expressed structurally: `<signalListenMode>` scopes a listener to `NotYetAcceptedOnly`, `OngoingOnly`, `OngoingOrNotYetAccepted` or `Always` (`$D\Royalty\...\Hospitality\Script_EndGame_RoyalAscent.xml:46,51,213,258`). `QuestTargetSignalPart_QuestEnded` exists for a parent quest watching a subquest; no vanilla def uses it.

**Custom signals** — any bare PascalCase name you emit and listen for, so it can never collide with an object signal: `PeaceTalksTimeout` (`Script_PeaceTalks.xml:82,86,90`), `ColonistsReturned`/`ColonistsDied` (`Script_PawnLend.xml:257-258,278,294`), `AllRaidsSent` (`Scripts_Utility_ThreatsCore.xml:327`), `TradeRequestTimeout` (`Script_TradeRequest.xml:142,152`), `Incompletable` (`$D\Royalty\...\Decree\Scripts_Decree.xml:226` sends, `…\Scripts_Decree_Utility.xml:44` listens).

**Emitting fields**: `outSignals` (`QuestNode_SendSignals`) · `outSignalComplete` (`QuestNode_Delay`) · `outSignalColonistsDied` (`Script_PawnLend.xml:258`) · `outSignalSuccess`/`outSignalFailed` (`Script_Hospitality_Utility.xml:500-501`) · `outSignalPawnsNotAvailable` (`Scripts_Decree.xml:226`) · `outSignalResult` (`Script_BuildMonument_Worker.xml:279`). **Listening fields**: `inSignal` (almost any node) · `inSignals` list · `inSignalEnable`/`inSignalDisable` · `inSignalChoiceUsed` (`Script_ItemStash.xml:167`) · `inSignalRemovePawn` (`Scripts_Permits.xml:68`) · `inSignalLeave` (`Scripts_Utility_ThreatsCore.xml:217`).

`SignalAction_*` (11 ethereal `ThingDef`s declared once in `$D\Core\Defs\ThingDefs_Misc\Ethereal_SignalActions.xml:4-65`) are a **different** system, spawned and configured from C# during map generation. Not part of the quest-authoring surface.

### 9.1 Ending

`QuestNode_End` → `QuestPart_QuestEnd` is the only exit. `RimWorld.QuestEndOutcome` has exactly four members, read from field metadata:

| Outcome | XML uses | Meaning |
|---|---|---|
| `Fail` | 84 | Failed or expired; fires `failedOrExpiredHistoryEvent`. |
| `Success` | 33 | Completed; fires `successHistoryEvent`. |
| `Unknown` | 2 | Ends with no verdict and no reputation/history consequence — dissolved through no player fault (`Script_ChangeRoyalHeir.xml:126,143`). |
| `InvalidPreAcceptance` | 2 | Became impossible *before* acceptance; disappears silently rather than counting as failure. Always paired with `signalListenMode NotYetAcceptedOnly` (`Script_EndGame_RoyalAscent.xml:96-97`). |

Omitting `<outcome>` is legal and common (`<node Class="QuestNode_End" />`, `$D\Core\...\Script_DownedRefugee.xml:191`); the default *appears* to be `Unknown`, inferred from context, not read from IL. Field usage across 148 `QuestNode_End` occurrences: `outcome` 121 · `goodwillChangeAmount`/`FactionOf`/`Reason` 32 each · `sendStandardLetter` 20 · `inSignal` 18 · `signalListenMode` 6. A fail carrying a reputation cost: `Script_Hospitality_Worker.xml:1208-1213`.

**Success vs failure is structural, not computed.** No evaluation step: place one `QuestNode_End` per terminal branch, hard-code its outcome, and whichever signal arrives first wins. Note the two-listener idiom at `Script_BanditCamp.xml:171-201` — `QuestNode_GiveRewards` on `site.AllEnemiesDefeated` and a *separate sibling* `QuestNode_End` on the same signal, so rewards resolve before the quest closes. `sendStandardLetter true` produces the built-in "Quest completed/failed" letter — omit it when you send your own (`Script_BanditCamp.xml:144-150` sends a custom letter *then* ends).

---

## 10. How a quest gets offered

1. **Natural random pool** — `rootSelectionWeight > 0`, `randomlySelectable` not false, `isRootSpecial` not true, `rootMin*` gates passed. Drawn via `IncidentDef GiveQuest_Random` (`$D\Core\Defs\Storyteller\Incidents_World_Quests.xml:15-20`).
2. **A named incident** — `IncidentDef` with `<workerClass>IncidentWorker_GiveQuest</workerClass>` and `<questScriptDef>YourDefName</questScriptDef>` (`…\Incidents_World_Quests.xml:22-28`). This is how `isRootSpecial` quests fire.
3. **A quest giver** — `givenBy` (`Traders`/`OrbitalScanner`/`Reading`/`Beggars`) plus `randomlySelectable false` (`$D\Odyssey\Defs\QuestScriptDefs\Script_AlphaThrumboSighting.xml:6-11`). Odyssey only.

---

## 11. Open questions / not determined

- **Field defaults** on `QuestScriptDef` and on individual nodes — constructor IL was not read. Everything labelled "typical values" is observed usage.
- **How `p=` weight and `priority=` combine** inside `GrammarResolver.RandomPossiblyResolvableRule`. Both fields exist on `Rule_String` and the parse rules are confirmed; the selection loop is not.
- **`nameMustBeUnique`, `neverPossibleInSpace`, root-level `layerWhitelist`/`layerBlacklist`** exist but are set by no shipped def — behaviour unverified.
- **`QuestNode_TextRules`** (fields `rules`, `target`; enum `TextRulesTarget` = `Description`, `Name`, `DecriptionAndName` — Ludeon's typo, shipped), **`ResolveQuestName`, `ResolveQuestDescription`, `ResolveTextRequests`, `AnySignalActivable`, `AllSignalsActivable`, `CannotRun`, `ModIsActive`** exist but no shipped def uses them; XML shape untested.
- **Whether `include` inside a quest's inline `RulePack` supports `ParentName` inheritance** the way `RulePackDef` does — no vanilla example to check.
- **`QuestEndOutcome` integer ordering** unread; the omitted-`outcome` default is inferred.
- **The `QuestPart_*` list is deliberately not reproduced** (249 types) — irrelevant to an XML author, see §1. A C# author can recover Ludeon's grouping from source paths embedded in the DLL (`strings -a Assembly-CSharp.dll | grep QuestParts`): `Misc\` 88, `Control\Filter\` 31, `Control\Misc\` 21, `Control\Basic\` 18 (holds `QuestPart_QuestEnd`), `Lords\` 14, `Reward\` 11, `Threat\` 6.
- **The §5 minimum viable quest has not been run in-game.**
