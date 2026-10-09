import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def show(tag, r):
    print(tag, "|", json.dumps(r, default=str)[:900]); sys.stdout.flush()
GD=lambda d,f="defName": S.call("jawa/get_defs", defs=d, fields=f)
show("ANSWER", GD("PreceptDef/RUT_Ritual_Answering;RitualOutcomeEffectDef/RUT_AnsweringOutcome;HediffDef/RM_AnsweringStalled;HediffDef/RM_AnsweredLogLine"))
show("GOO", GD("ThingDef/AA_GreenGoo", "race"))
show("SALV", GD("IncidentDef/RM_WreckFall;IncidentDef/RUT_FallLineWreckFall;ThingDef/RUT_FoundrySalvageCache;ThingSetMakerDef/RUT_SalvageLoot_Foundry;ThingSetMakerDef/RUT_SalvageLoot_Imperial;RimMandrake.Wreckage.RM_WreckListDef/RUT_WreckList_FallLine;RimMandrake.Wreckage.RM_WreckWeatheringDef/RUT_WreckWeathering_FallLine;RimMandrake.Wreckage.RM_WreckWeatheringDef/RUT_WreckWeathering_ForgeWarm"))
show("NEW", GD("ThingDef/RUT_ThroatCask;HediffDef/RUT_ThroatCaskNear;PawnKindDef/RUT_Jawa_Junkers_CaskedScavenger;PawnKindDef/RUT_Jawa_Junkers_CaskedElite;ThingDef/RUT_VaultFleshSeal;TraderKindDef/RUT_Caravan_Junkers;ThingDef/RUT_FoundrySalvageCache"))
W="RimMandrake.Webwork.RM_WebworkProof"
for a in ["true|RM_Webwork_Anchor|34","true|RM_Webwork_Web|0","false|RM_Webwork_Anchor|0"]:
    show("WEB "+a, S.call("jawa/static_call", type=W, method="ProofHarvest", args=a))
show("TP_JOB", S.call("jawa/type_probe", typeName="RimMandrake.CreatureBehaviors.RM_PawnJobProof"))
