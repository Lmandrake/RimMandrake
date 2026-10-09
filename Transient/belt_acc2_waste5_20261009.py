import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
g = S.call("jawa/get_defs", defs="QuestScriptDef/RUT_WasteRun;IncidentDef/RUT_WasteRunOffer;HistoryEventDef/RUT_WasteRunDroppedOnEmpire;HistoryEventDef/RUT_WasteRunFrozen;HistoryEventDef/RUT_WasteRunEntombed;HistoryEventDef/RUT_WasteRunPropaneIgnited;HistoryEventDef/RUT_WasteRunSlimeNeutralized;HistoryEventDef/RUT_WasteRunSlimeBloomed;HistoryEventDef/RUT_WasteRunSlimeUnknown;", fields="defName")
print(g.get("success"), g.get("foundCount"), g.get("notFound"))
