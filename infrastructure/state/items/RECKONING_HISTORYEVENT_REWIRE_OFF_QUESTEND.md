# RECKONING_HISTORYEVENT_REWIRE_OFF_QUESTEND

## verify

The supervisor's live round (relentless_live_round.py) runs each line below on a game-up sitting (LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST).
The defs must resolve first: a log silent about a def the load never had is not a pass.
A1: the two concrete RUT_Reckoning quests must resolve (EggReckoning loaded); the XML error names the stray QuestNode_End field.

live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --has QuestScriptDef/RUT_Reckoning_CartelOffer --has QuestScriptDef/RUT_Reckoning_Rumor && python3 src/RimMandrake/Utils/live_log_check.py --absent successHistoryEvent --absent failedOrExpiredHistoryEvent
