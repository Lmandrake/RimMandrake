import json,re,os
D="/mnt/d/Luke/dev/_artpipe/done/"
R="/home/mandrake/rm/foundry/"
NO=("NO outline, no black edge line, no dark rim; the object's edge is defined by its own colour and soft shading against the transparent background. "
    "Painted in the same realistic natural-history painted style as the Rot plant renders: real material texture, believable lighting, matte, soft contact shadow only. Centered, isolated, transparent background.")
def strip(p):
    p=re.sub(r"^The attached image is a CANON REFERENCE.*?framing\. ","",p)
    p=re.sub(r"Heavy, clean black outline.*?below\. ","",p)
    return re.sub(r"\bblack outline\b","",p)
# (def, done job id, installed png relative to repo)
rows="""RM_HalfExtractedCore|RM_HalfExtractedCore|src/RimMandrake/Warcasket/Textures/Things/Item/Resource/RM_HalfExtractedCore/RM_HalfExtractedCore.png
RM_BellowsItem|RM_BellowsItem|src/RimMandrake/Contagion/Textures/Things/Item/RM_BellowsItem.png
RM_TetchikJar|RM_TetchikJar|src/RimMandrake/Scarlands/Textures/Things/Item/RM_TetchikJar.png
RM_VisslerArm|RM_VisslerArm|src/RimMandrake/LeaningScrub/Textures/Things/Item/Resource/RM_VisslerArm.png
RM_MurrinCatch|RM_MurrinCatch|src/RimMandrake/WeepingStones/Textures/Things/Item/RM_MurrinCatch.png
RM_SandSieve|RM_SandSieve|src/RimMandrake/Stillsand/Textures/Things/Item/RM_SandSieve.png
RM_ZennaqFilament|RM_ZennaqFilament|src/RimMandrake/FloodedCanyon/Textures/Things/Item/RM_ZennaqFilament.png
RSW_MarshFungus|RSW_MarshFungus|src/RimStarWars/Cuisine/Textures/Things/Item/RSW_MarshFungus.png
RUT_PilgrimJournal|RUT_PilgrimJournal|src/RimUtinni/ScarlandsLadder/Textures/Things/Item/RUT_PilgrimJournal.png
RUT_Mindstone|RUT_Mindstone|src/RimUtinni/UtinniPatches/Textures/Things/Item/RUT_Mindstone/RUT_Mindstone.png
RUT_CrackWax|RUT_CrackWax|src/RimUtinni/UtinniPatches/Textures/Things/Item/Resource/RUT_CrackWax/RUT_CrackWax.png
RM_CaudalSpringItem|RM_CaudalSpringItem|src/RimMandrake/Contagion/Textures/Things/Item/RM_CaudalSpringItem.png
RM_EyeburstItem|RM_EyeburstItem|src/RimMandrake/Contagion/Textures/Things/Item/RM_EyeburstItem.png
RM_FossilDeepStratum|RM_FossilDeepStratum|src/RimMandrake/FloodedCanyon/Textures/Things/Item/Special/RM_FossilDeepStratum/RM_FossilDeepStratum.png
RM_GeneSeekerLoaded|RM_GeneSeekerLoaded|src/RimMandrake/GelatinousSlime/Textures/Things/Item/RM_GeneSeekerLoaded.png
RM_FailedChassis|RM_FailedChassis|src/RimMandrake/Scarlands/Textures/Things/Item/RM_FailedChassis.png
RM_WreckLichenScrapings|RM_WreckLichenScrapings|src/RimMandrake/Scarlands/Textures/Things/Item/Resource/RM_WreckLichenScrapings/RM_WreckLichenScrapings.png
RSW_KraytLens|RSW_KraytLens|src/RimMandrake/Stillsand/Textures/Things/Item/Resource/RSW_KraytLens.png
RM_ChassisCore|RM_ChassisCore|src/RimMandrake/Scarlands/Textures/Things/Item/RM_ChassisCore.png
RM_ContaminantBezoar|RM_ContaminantBezoar|src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_ContaminantBezoar.png
RM_TarRuinedGoods|phfix_RM_TarRuinedGoods_a|src/RimMandrake/TheSump/Textures/Things/Item/Resource/RM_TarRuinedGoods/RM_TarRuinedGoods.png
RM_BrimlockWater|phfix_RM_BrimlockWater_a|src/RimMandrake/Webwork/Textures/Things/Item/Resource/RM_BrimlockWater/RM_BrimlockWater.png""".split("\n")
J=[];miss=[]
for r in rows:
    d,j,png=r.split("|")
    if not os.path.exists(R+png): miss.append(("nopng",d,png)); continue
    jf=D+j+".json"
    if not os.path.exists(jf): miss.append(("nojob",d)); continue
    p=strip(json.load(open(jf))["prompt"])
    tex=png.split("/Textures/")[1][:-4]
    J.append({"id":d+"_v3_nooutline","rimflow_item_id":"ICON_OUTLINE_REPAINT_1","target_def":d,"canvas_w":128,"canvas_h":128,"background":"transparent","priority":46,"facings":[],
      "prompt":p.strip()+" "+NO,
      "style_notes":f"REPAINT of {d} without its near-black edge outline (census 2026-10-10, foundry fill, owner card). painterly vanilla-RimWorld art style, grounded believable materials, matte, never cartoonish, no outlines, no black edge line, soft contact shadow only",
      "target_texpath":tex})
print(len(J),"jobs; misses",miss)
json.dump(J,open(R+"Transient/foundry_art_fill_jobs_20261010.json","w"),indent=1)
