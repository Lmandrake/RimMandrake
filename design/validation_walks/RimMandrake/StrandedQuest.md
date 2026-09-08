# StrandedQuest — validation walk
subject: src/RimMandrake/StrandedQuest
deps: none (no modDependencies/loadAfter block in About.xml)
list: minimal
status-hint: Adds one quest, "RM_Stranded" — a neighbouring settlement's transport breaks up over your land and drops a survivor (SpaceRefugee, no faction) for 6-10 days; keep them and the asker's goodwill drops, return them and you're paid. Pure XML on vanilla quest nodes, no assembly.

## must be true
- QuestScriptDef `RM_Stranded` loads with no config errors and its `root` (QuestNode_Sequence) resolves.
- Firing the quest generates one `SpaceRefugee`-kind pawn with `addToList=lodgers`, no faction, arriving via `RandomDrop` (`QuestNode_PawnsArrive`, `joinPlayer=false`).
- A shown quest timer (`isQuestTimeout`) of `randInt(6,10)*60000` ticks fires `outSignalComplete=PickupDue`; on that signal the quest gives a reward, ends `Success`, and the lodger leaves on cleanup (`QuestNode_LeaveOnCleanup`).
- Recruiting the lodger (`lodgers.Recruited`) ends the quest `Fail` and changes the asker's faction goodwill by `-12` with reason `RM_StrandedTravellerTaken`; enslaving (`lodgers.Enslaved`) is `-20`; arresting (`lodgers.Arrested`) is `-12` — same reason def in all three.
- The lodger dying (`lodgers.Destroyed`) ends the quest `Fail`, goodwill `-6`, reason `QuestPawnLost` (vanilla's own reason def, not ours).
- The lodger walking off on their own (`lodgers.LeftMap`) ends the quest `Unknown` with no goodwill change.
- `HistoryEventDef RM_StrandedTravellerTaken` loads with label "took in a survivor we vouched for" — the label the faction tab shows next to the three Taken-branch goodwill changes.

## the walk
1. [L] Player.log after load contains no `"Config error in mandrake.rm.strandedquest"` and no XML error naming `Quest_Stranded.xml` or `HistoryEvents_Stranded.xml`
2. [D] def read-back: `QuestScriptDef` `RM_Stranded` exists; `rootMinProgressScore` = 3, `expireDaysRange` = `1~2`, `everAcceptableInSpace` = true, `minRefireDays` = 25
3. [D] def read-back: `HistoryEventDef` `RM_StrandedTravellerTaken` exists; `label` = "took in a survivor we vouched for"
4. [B] `jawa/fire_quest {"questDef": "RM_Stranded", "accept": true}` → quest created and Ongoing (a nearby settlement + leader must already exist in the save/world for `QuestNode_GetNearbySettlement` to resolve — pick a map with one in range, or expect the node to fail quietly and the quest not to fire)
5. [B] `jawa/list_things {"group": "Pawn"}` is wrong tool (pawns excluded by default) — use `jawa/list_things {"includePawns": true}` or the dedicated pawn lister to confirm exactly one new pawn of kind `SpaceRefugee` exists on the map with `Faction = null`, spawned via drop pod
6. [B] `jawa/quest_lifecycle {"action": "list"}` → confirm the RM_Stranded quest is present and Ongoing with its timeout QuestPart counting down
7. [B] `jawa/faction_goodwill_check {"faction": "<asker factionDefName>", "other": "PlayerColony", "goodwillChange": -12}` before recruiting the lodger, to confirm the change is not refused by `CanChangeGoodwillFor` before the live path is exercised
8. [D] after triggering the `lodgers.Recruited` signal path in a debug/quicktest pass: def read-back confirms the resulting goodwill delta against the asker faction matches `-12` and the logged reason is `RM_StrandedTravellerTaken` (read via `jawa/faction_relations_get` before/after, not guessed)

[S] none — every observable outcome here is a letter, a goodwill number, and a def read-back; nothing in this mod needs a human's eyes.
