import json,re
D="/mnt/d/Luke/dev/_artpipe/done/"
NO=("NO outline, no black edge line, no dark rim; the object's edge is defined by its own colour and soft shading against the transparent background. "
    "Painted in the same realistic natural-history painted style as the Rot plant renders: real material texture, believable lighting, matte, soft contact shadow only. Centered, isolated, transparent background.")
S="Single item, centered, no ground shadow, no background scenery. "
def strip(p):
    p=re.sub(r"Heavy, clean black outline.*?below\. ","",p); p=re.sub(r"Heavy, clean black outline[^.]*\.","",p)
    return re.sub(r"\bblack outline\b","",p)
def old(j): return strip(json.load(open(D+j+".json"))["prompt"])
J=[]
def add(name,tdef,tex,prompt):
    J.append({"id":name+"_v3_nooutline","rimflow_item_id":"ICON_OUTLINE_REPAINT_1","target_def":tdef,"canvas_w":128,"canvas_h":128,"background":"transparent","priority":45,"facings":[],
     "prompt":prompt.strip()+" "+NO,
     "style_notes":f"REPAINT of {tdef} without its near-black edge outline (census 2026-10-10, batch 4). painterly vanilla-RimWorld art style, grounded believable materials, matte, never cartoonish, no outlines, no black edge line, soft contact shadow only",
     "target_texpath":tex})
add("RM_FossilSkeleton","RM_FossilSkeleton","Things/Item/Resource/RM_FossilSkeleton/RM_FossilSkeleton",old("RM_FossilSkeleton"))
add("RM_Drazz","RM_Drazz","Things/Item/Resource/RM_Drazz",old("RM_Drazz"))
add("RM_Sunbeam","RM_Sunbeam","Things/Item/Equipment/RM_Sunbeam",old("RM_Sunbeam"))
add("RUT_MetalSaltBezoar","RUT_MetalSaltBezoar","Things/Item/Resource/RUT_MetalSaltBezoar/RUT_MetalSaltBezoar",old("rut_metalsaltbezoar_v1"))
add("RUT_PreservedDrawJoint","RUT_PreservedDrawJoint","Things/Item/RUT_PreservedDrawJoint/RUT_PreservedDrawJoint",old("rut_preserveddrawjoint_v1"))
add("RM_Saal","RM_Saal","Things/Item/Resource/RM_Saal/RM_Saal","RimWorld game item sprite: a freshly caught saal, a bubble-sailor no bigger than a fist, a small translucent bell with a single stiff sail-vane rising from the top, trailing a few thin lines, laid out as a harvested catch. "+S)
add("RM_Deepfire","RM_Deepfire","Things/Item/Resource/RM_Deepfire/RM_Deepfire","RimWorld game item sprite: a small glass jar of pale, faintly glowing pigment pressed from crowncarpet, soft cold inner glow, cork stopper. "+S)
add("RM_LilianaSilk","RM_LilianaSilk","Things/Item/Resource/RM_LilianaSilk/RM_LilianaSilk","RimWorld game item sprite: a loose skein of blood-red silk thread gathered from a wingless moth, soft, warm and lustrous. "+S)
add("Pyrinth","Pyrinth","Things/Item/Resource/Pyrinth/Pyrinth","RimWorld game item sprite: a lump of opaque crystallized pyrinth, warm amber-red mineral, faceted, a dim inner glow, little heat shimmer. "+S)
add("PyrinthBlade","PyrinthBlade","Things/Item/Equipment/WeaponMelee/PyrinthBlade","RimWorld game weapon sprite: a short blade carved from opaque crystallized pyrinth, warm amber-red faceted mineral with a dim inner glow, simple wrapped hilt. "+S)
add("RUT_Jawa_ClaimRumour","RUT_Jawa_ClaimRumour","Things/Item/Special/JawaClaimRumour","RimWorld game item sprite: a scraped hide chart rolled up and tied with cord, a stub of iron cut for driving into wreckage laid across it, faint scratched route marks. "+S)
add("VAEWaste_ToxicMeat","VAEWaste_ToxicMeat","Things/Item/ToxicMeat/ToxicMeat","RimWorld game item sprite: a raw chunk of toxic meat, chewy and gelatinous, sickly greenish-grey flesh with a glossy slick. "+S)
add("RSW_EggOval","RSW_EggOval","Things/Item/Resource/AnimalProductRaw/EggOval/EggOval","RimWorld game item sprite: a single large oval egg, pale speckled shell. "+S)
add("RSW_CookedSkewer","RSW_CookedSkewer","Things/Item/Meal/RSW_CookedSkewer/RSW_CookedSkewer/RSW_CookedSkewer","RimWorld game item sprite: a bare wooden stick roasted over a fire, charred tip, seen from above at a slight diagonal. "+S)
json.dump(J,open("/home/mandrake/rm/foundry/Transient/icon_outline_jobs_batch4_20261010.json","w"),indent=1)
print(len(J))
