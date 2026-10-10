import json,re
D="/mnt/d/Luke/dev/_artpipe/done/"
NO=("NO outline, no black edge line, no dark rim; the object's edge is defined by its own colour and soft shading against the transparent background. "
    "Painted in the same realistic natural-history painted style as the Rot plant renders: real material texture, believable lighting, matte, soft contact shadow only. Centered, isolated, transparent background.")
def strip(p):
    p=re.sub(r"^The attached image is a CANON REFERENCE.*?framing\. ","",p)
    p=re.sub(r"Heavy, clean black outline.*?below\. ","",p)
    p=re.sub(r"\bblack outline\b","",p)
    return p
def old(j): return strip(json.load(open(D+j+".json"))["prompt"])
S="Single item, centered, no ground shadow, no background scenery. "
J=[]
def add(name,tdef,tex,prompt):
    J.append({"id":name+"_v3_nooutline","rimflow_item_id":"ICON_OUTLINE_REPAINT_1","target_def":tdef,"canvas_w":128,"canvas_h":128,"background":"transparent","priority":45,"facings":[],
     "prompt":prompt.strip()+" "+NO,
     "style_notes":f"REPAINT of {tdef} without its near-black edge outline (census 2026-10-10, batch 3, owner card). painterly vanilla-RimWorld art style, grounded believable materials, matte, never cartoonish, no outlines, no black edge line, soft contact shadow only",
     "target_texpath":tex})
fish={"RM_DossCatch":"scald2_dosscatch_a","RM_EeshCatch":"scald2_eeshcatch_a","RM_EkkelCatch":"scald2_ekkelcatch_a","RM_KarrashCatch":"scald2_karrashcatch_a","RM_MuddalCatch":"scald2_muddalcatch_a","RM_ThuumCatch":"scald2_thuumcatch_a","RM_BladderboilCatch":"scald2_bladderboilcatch_a"}
for k,v in fish.items(): add(k,k,"Things/Item/Fish/"+k,old(v))
add("RM_EssarnCatch","RM_EssarnCatch","Things/Item/RM_GreySea/RM_EssarnCatch",old("phreg_RM_EssarnCatch_v1"))
add("RM_AluunCatch","RM_AluunCatch","Things/Item/RM_TwilightSea/RM_AluunCatch",old("phreg_RM_AluunCatch_v1"))
add("RM_NoolimCatch","RM_NoolimCatch","Things/Item/RM_TwilightSea/RM_NoolimCatch",old("phreg_RM_NoolimCatch_v1"))
add("RM_WeloonCatch","RM_WeloonCatch","Things/Item/RM_TwilightSea/RM_WeloonCatch",old("phreg_RM_WeloonCatch_v1"))
add("RM_IlissCatch","RM_IlissCatch","Things/Item/RM_TheChill/RM_IlissCatch","RimWorld game item sprite: a single freshly caught iliss, a wire-thin black eel the length of a forearm with a visible spine of conductive mineral running along it, faint metallic sheen, laid out as a harvested catch. "+S)
add("RM_ScaaLumsigh","RM_ScaaLumsigh","Things/Item/Fish/RM_ScaaLumsigh","RimWorld game item sprite: a single freshly caught deep-bodied river fish scaled in green and old gold, with a single seam of cold blue light running nose to tail, laid out as a harvested catch. "+S)
sk={"RSW_MeatOnAStick":"a roasted chunk of meat skewered on a wooden stick","RSW_LittleMeatOnAStick":"one small roasted morsel of meat skewered on a wooden stick","RSW_VegOnAStick":"roasted vegetable pieces (green and orange) skewered on a wooden stick","RSW_FungusOnAStick":"roasted mushrooms skewered on a wooden stick","RSW_FruitOnAStick":"roasted fruit pieces skewered on a wooden stick","RSW_FishOnAStick":"a small whole fish roasted and skewered on a wooden stick","RSW_BlendOnAStick":"a mix of roasted meat and vegetable pieces skewered on a wooden stick"}
for k,v in sk.items(): add(k,k,f"Things/Item/Meal/{k}/{k}",f"RimWorld game item sprite: {v}, cooked over a campfire, seen from above at a slight diagonal, lying flat. "+S)
kits={"SimpleResearchKit":"a simple portable research kit: a small scuffed field case with a few basic sample tubes, a notebook and a magnifier","HiTechResearchKit":"a high-tech research kit: a sleek case with a glowing display panel, sensor probes and neat instrument slots","MultiAnalyzerResearchKit":"a multi-analyzer research kit: a case with several small analyzer modules, dials and a spectrometer head","RemoteResearchKit":"a remote research kit: a ruggedized case with a folding antenna, a satellite dish dish and a handheld uplink unit"}
for k,v in kits.items(): add(k,k,f"Things/Items/{k}/{k}",f"RimWorld game item sprite: {v}, seen from the east side. "+S)
json.dump(J,open("/home/mandrake/rm/foundry/Transient/icon_outline_jobs_batch3_20261010.json","w"),indent=1)
print(len(J)); print(J[0]["prompt"]); print(J[7]["prompt"])
