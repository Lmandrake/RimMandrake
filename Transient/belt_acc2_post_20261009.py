import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def gd(d, f="defName"):
    g = S.call("jawa/get_defs", defs=d, fields=f); return (g.get("success"), g.get("foundCount"), g.get("notFound"), g)
for d in ("IncidentDef/RUT_JawaReturnTow", "PreceptDef/RUT_Ritual_JoiningWater", "RitualPatternDef/RUT_JoiningWaterPattern", "RitualBehaviorDef/RUT_JoiningWaterBehavior", "RitualOutcomeEffectDef/RUT_JoiningWaterOutcome", "ThoughtDef/RUT_WeHeldTheWater"):
    r = gd(d); print(d, r[:3])
g = gd("ThingDef/RM_ScaldWalker", "modExtensions")[3]; print("ScaldWalker ext", [x.get("fields") for x in g.get("defs", [])])
g = gd("ThingDef/RM_CoolantEel", "comps")[3]; print("CoolantEel comps", [x.get("fields") for x in g.get("defs", [])])
for form in ("strangler", "weeper", "lure", "sleeper"):
    for mode in ("on", "off"):
        r = S.call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FourFormsProof", method="ProofForm", args="%s|%s" % (form, mode))
        print(form, mode, r.get("success"), str(r.get("result") or r.get("message"))[:200], flush=True)
