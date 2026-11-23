# History: corrected lines and their evidence

The active files hold the lessons. This file holds old lines that were wrong, and what showed it (2026-11-23). Each engine
fact was read in the decompiled 1.6 source through RimSage. Each corpus figure was counted in the shipped `Data` folder.

- **Load cost.** `SKILL.md` said that each validator check cost somebody a 20-30 minute game load, and that a load was
  ~25 minutes. `skills/rimworld-load-round/SKILL.md` holds the current figures.
- **What a failed text looks like.** `SKILL.md` said that the text renders empty. `GrammarResolver.ResolveUnsafe` returns
  `ERR: ` and the first rule of the request, or `ERR`. A live pass on an older build reported an empty description
  (`mod_patterns.md` §6 row 1). The skill's own front matter still says that the description goes blank.
- **`delayTicks`.** `SKILL.md` said that every `delayTicks` in the corpus is a multiple of 60000. The shipped defs also
  use 300, 600, 1200, 1800, 3500 and 7500.
- **`QuestPart` count.** `SKILL.md` said 249. The TypeDef table of `Assembly-CSharp.dll` holds 244 `QuestPart_*` types.
- **`storeAs` and signals.** `SKILL.md` said that one pawn under `storeAs` has no signal to listen to.
  `QuestUtility.AddQuestTag` tags a single `Thing`, `WorldObject`, `Map`, `Lord`, `Faction` or `TransportShip`, or each
  element of a list. Vanilla listens to `asker.Destroyed` in three places.
- **`SignalActivable`.** `SKILL.md` said that the node needs `inSignalEnable`. `QuestNode_SignalActivable.RunInt` uses the
  ambient `inSignal` when the field is absent.
- **Acceptance.** `Quest.Accept` calls `Initiate`, which sends `Quest<id>.Initiate`. `QuestGen.InitializeQuestGen` puts
  that signal in the slate as `inSignal`.
- **`HistoricalOnly`.** `SKILL.md` listed four listen modes. `QuestPart.SignalListenMode` has five. No vanilla XML uses
  `HistoricalOnly`. `Quest.QuestTick` ticks no part after the end; `Quest.Notify_SignalReceived` still passes a signal to a
  part that listens in `Always` or `HistoricalOnly`.
- **`QuestNode_SendSignals`.** Found 2026-09-18 in `VAULT_THAW_FIXED_TILES_UNFIREABLE_1`. `SKILL.md` said that the extra
  `<inSignal>` parses clean. `XmlToObjectUtils` logs "doesn't correspond to any field" for it.
- **Hidden quests.** `SKILL.md` said that even fully hidden vanilla quests supply placeholder text. `MechanitorStartingMech`
  supplies none, and `QuestNode_ResolveQuestName` and `QuestNode_ResolveQuestDescription` skip a hidden quest.
- **The incident ConfigError.** Found 2026-09-18 in `VAULT_THAW_FIXED_TILES_UNFIREABLE_1`. The ConfigError tests
  `rootSelectionWeight` only (`IncidentDef.cs:235`).
- **`isRootSpecial`.** `SKILL.md` said that such a quest fires only from code or an incident. `IsRootRandomSelected` reads
  `rootSelectionWeight` and `randomlySelectable`. `isRootSpecial` is read only in `IsRootAny` (the challenge-rating
  ConfigError and the dev menus). Every shipped def with both `isRootSpecial` and a weight above 0 sets
  `randomlySelectable` false.
- **Goodwill and raids.** `SKILL.md` said that the storyteller turns the goodwill change into raids. Only a hostile faction
  raids.
- **The silent drop.** `SKILL.md` said that a `TestRunInt()` that throws is dropped with no log. `QuestScriptDef.CanRun`
  logs an error and throws again. A false result is silent, for an XML root too.
- **`everAcceptableInSpace`.** `QuestScriptDef.CanQuestOccurOnTile` and `IncidentWorker_GiveQuest.CanQuestOccurOnTile` also
  read the field. The second one has no `autoAccept` exception. Both pass an invalid tile, and a `World` target has one.
- **`arrivalMode`.** `SKILL.md` called it an enum with one attested value. `QuestNode_PawnsArrive.arrivalMode` is a
  `PawnsArrivalModeDef`, and `RunInt` falls back to `EdgeWalkIn`.
- **`<choices>`.** `SKILL.md` said that nothing established whether `<choices>` is optional, and that each use is
  Empire-specific. `SetVars` reads `value2.Count` with no null test. The vanilla uses also hold `Tribal`, `Outlander` and
  `Pirate` entries.
- **Calibration.** The first version of `validate_quest.py` reported 915 errors on the 151 shipped quests.
  The later figure was 1 error and ~40 warnings. The run of 2026-11-23 reported 1 error and 40 warnings before the route repair, and 1 error and 32 warnings after. The error is on
  `CreepJoinerArrival_Metalhorror`; `SKILL.md` named `CreepJoinerArrival`.
- **GiveQuest target.** The `targetTags` and challenge-rating traps came from `CATHEDRAL_MISSION_BOON_OFFERS_1` and
  `RIMMANDRAKE_FIX_GIVEQUEST_DEFS_TWO_SILENT_LOAD_TRAPS` (eleven RUT GiveQuest incidents; two KyberTradePlot quests).
  `IncidentDef.ConfigErrors` refuses `World` beside another target tag.
- **Validator routes.** Until 2026-11-23 `validate_quest.py` took a giver or an incident as enough for a star rating, and
  called a decree-only quest "never-fires". It also passed a quest-giver quest of weight 0, and no giver picks one
  (`TradeUtility` and the other givers pick by `rootSelectionWeight`). `selftest_validate_quest.py` covers all three.
