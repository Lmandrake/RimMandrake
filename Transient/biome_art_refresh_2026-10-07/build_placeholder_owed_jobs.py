#!/usr/bin/env python3
"""Jobs for the 29 shipped placeholder textures that had no job (placeholder_plants.md, section A OWED).
RM_SekkulaathTank + RM_GlowTank are NOT here: finished art exists (RM_SekkulaathYoungCask, RM_SunSphere_v2_south).
Run: python3 <this> > placeholder_owed_jobs.json ; fill_queue.py --input placeholder_owed_jobs.json
Prompts: def description + a concrete visual line; two candidates (a, b) per texture; nothing is installed."""
import json, xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FW = ("fever wood register: a drowned jungle where colossal fused trunks have stilled the swamp into black unrippled "
      "mirror pools over deep mud; hot wet gloom, dim green-gold filtered light, wet dark bark")
WW = ("webwork register: a dense nightmare thicket in green gloom, pale dust-lit shafts, silk and tangled vegetation; "
      "dim greens, bruise purples, bone-white silk")
SUMP = ("the sump register: black tar country, bitumen mounds, acrid yellow-brown haze, oily iridescent sheen, "
        "scavenged corroded metal")
LUM = ("luminous pigment register: deep dark workshop palette lit by the glow of deepfire pigment, warm amber and "
       "molten gold against iron and soot")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic and grounded, never cartoonish, never a flat shape "
         "or icon; one centred subject on a fully transparent background, no ground plane, no cast shadow.")
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
VAR = {"a": "", "b": " A second, clearly different rendering of the same subject (different shape and arrangement)."}

# (defName, texpath-relative-to-Textures/Things-or-full, canvas w,h, register or None, visual line, kind)
R = [
 ("RM_LureStake","Things/Building/RM_LureStake/RM_LureStake",64,64,FW,"A stout weathered wooden post driven upright, a rusted chain coiled at its base; seen top-down at a slight angle.","building"),
 ("RM_Sekkulaath_Feeler","Things/Building/RM_Sekkulaath/RM_Sekkulaath_Feeler",128,128,FW,"A thin pale blind tentacle rising from a pool, slightly curled, dripping, wet dark purple-grey skin, seen from above at a slight angle.","building"),
 ("RM_Sekkulaath_Lash","Things/Building/RM_Sekkulaath/RM_Sekkulaath_Lash",128,128,FW,"A long barbed tentacle, wet dark purple-grey skin with a row of hooked barbs, raised mid-strike from the water.","building"),
 ("RM_Sekkulaath_Porter","Things/Building/RM_Sekkulaath/RM_Sekkulaath_Porter",128,128,FW,"A slender delicate tentacle, wet dark purple-grey skin, tip curled gently holding out a small offering at the water's edge.","building"),
 ("RM_Sekkulaath_Sentinel","Things/Building/RM_Sekkulaath/RM_Sekkulaath_Sentinel",128,128,FW,"A motionless tentacle raised straight and still just above the water, wet dark purple-grey skin, tip faintly ridged like a listening organ.","building"),
 ("RM_Sekkulaath_Snare","Things/Building/RM_Sekkulaath/RM_Sekkulaath_Snare",128,128,FW,"A thick muscular tentacle with the underside ridged with rows of suckers, curling to grip, wet dark purple-grey skin.","building"),
 ("RUT_FeverTrunkHeartwood","Things/Building/RUT_FeverTrunkHeartwood/RUT_FeverTrunkHeartwood",128,128,FW,"A top-down tile of dense dark fused trunk wood: tight dark grain, fine growth rings, packed solid like stone, slightly damp. Fills the whole tile edge to edge, no gaps.","building"),
 ("RM_DrommathBurstSap","Things/Item/Resource/RM_DrommathBurstSap/RM_DrommathBurstSap",64,64,FW,"A glistening heap of amber-gold sugar-sap spilled out in a thick gluttonous gob, with a few sticky strings.","item"),
 ("RM_DrommathSap","Things/Item/Resource/RM_DrommathSap/RM_DrommathSap",64,64,FW,"A small pale-amber drop-and-puddle of thin sugar-sap, a modest trickle, glossy.","item"),
 ("RM_OssagrelSap","Things/Item/Resource/RM_OssagrelSap/RM_OssagrelSap",128,128,FW,"A sugar-thick syrup, dark honey-red, pooled in a shallow cut cane section of ossagrel, glossy.","item"),
 ("RM_PottersClay","Things/Item/Resource/RM_PottersClay/RM_PottersClay",128,128,FW,"A rough lump of grey river clay, damp and smooth with finger marks, a few root fibres caught in it.","item"),
 ("RM_RadioactiveSuppressant","Things/Item/Resource/RM_RadioactiveSuppressant/RM_RadioactiveSuppressant",128,128,FW,"A sealed machined metal charge canister, dull steel with a faded hazard marking and a faint sickly green glow at its seams.","item"),
 ("RM_SeepOil","Things/Item/Resource/RM_SeepOil/RM_SeepOil",128,128,FW,"A small stoppered glass flask of iridescent oil, rainbow sheen over dark liquid.","item"),
 ("RM_SekkulaathSpleenChemicals","Things/Item/Resource/RM_SekkulaathSpleenChemicals/RM_SekkulaathSpleenChemicals",128,128,FW,"A glass vial of thick, faintly luminous purple fluid, cork stoppered, a purple stain at the lip.","item"),
 ("RM_ThornbugNectar","Things/Item/Resource/RM_ThornbugNectar/RM_ThornbugNectar",64,64,FW,"A small clay pot of thick pale golden nectar, creamy and sweet, a drip running down the side.","item"),
 ("RM_VaulmLacquer","Things/Item/Resource/RM_VaulmLacquer/RM_VaulmLacquer",64,64,FW,"A cracked-off shard of amber-hard resin, glass-smooth, translucent honey-brown.","item"),
 ("RM_Sekkulaath_Juvenile","Things/Pawn/Animal/RM_Sekkulaath_Juvenile/RM_Sekkulaath_Juvenile",128,128,FW,"Top-down view of a small dark tentacled hatchling creature: a soft rounded body with a ring of short writhing tentacles, wet purple-black skin, a few pale spots. A baby of the great being beneath the pools.","animal"),
 ("RM_DeepfirePress","Things/Building/Production/RM_DeepfirePress/RM_DeepfirePress".replace("/RM_DeepfirePress/RM_DeepfirePress","/RM_DeepfirePress"),192,64,LUM,"A wide three-cell machine seen top-down at a slight angle: a screw press at one end joined by pipes to a brass retort and coil on the same iron bed, glowing amber at the outlet.","building"),
 ("RM_CrowncarpetDead","Things/Item/Resource/RM_Deepfire/RM_CrowncarpetDead",64,64,LUM,"A grey, slumped, dried sheet of dead crowncarpet fungus-mat, limp and crumpled, no glow.","item"),
 ("RM_StrongTarSolvent","Things/Item/Resource/RM_StrongTarSolvent",64,64,SUMP,"A heavy industrial acid jug, thick yellow-green glass or dull metal with a corroded stopper and a hazard tag, faint fumes.","item"),
 ("RM_TarRuinedGoods","Things/Item/Resource/RM_TarRuinedGoods",256,256,SUMP,"A single fused black lump of tar-ruined goods, glossy and lumpy, bits of hide or bone sticking out of it.","item"),
 ("RM_ThrummelSeepwax","Things/Item/Resource/RM_ThrummelSeepwax",64,64,SUMP,"A warm waxy block of pale-amber hive wax, soft edges, slightly translucent, rough comb texture.","item"),
 ("RM_Webwork_NestWall","Things/Building/Natural/RM_Webwork_NestWall/RM_Webwork_NestWall",256,256,WW,"A wall-sized heap of old bones and wreckage packed with grey-white hardened silk into a solid dome-like mass, seen from above at a slight angle.","building"),
 ("RM_BrimlockWater","Things/Item/Resource/RM_BrimlockWater/RM_BrimlockWater",128,128,WW,"A cut green bladder-trunk section holding clear water, with a clear water pool or skin sack, glinting.","item"),
 ("RM_OllathrixEgg","Things/Item/Resource/RM_OllathrixEgg/RM_OllathrixEgg",128,128,WW,"A single leathery bone-white egg the size of a bowling ball, slightly wrinkled, faintly dusted with silk threads.","item"),
 ("RM_TavroskLiquor","Things/Item/Resource/RM_TavroskLiquor/RM_TavroskLiquor",128,128,WW,"A stoppered glass bottle of sweet pale-gold volatile liquor, a drop of sap on the cork.","item"),
 ("RSW_BactaPatch","Things/Item/Bacta/RSW_BactaPatch",128,128,None,"A small square self-adhesive dressing with a peel-off backing tab, translucent blue bacta gel showing through the pad.","item"),
 ("RUT_Greenwood","Things/Item/Resource/RUT_Greenwood",64,64,None,"A short freshly-felled green timber log, bark on, damp and heavy, cut ends showing pale wet wood and a little sap.","item"),
 ("RUT_Hardwood","Things/Item/Resource/RUT_Hardwood",64,64,None,"A short plank/log of dense dark-grained heartwood, near black-brown, fine tight grain, a faint living warp.","item"),
]
DESC = {}
LAB = {}
for f in REPO.glob("src/**/Defs/**/*.xml"):
    try: root = ET.parse(f).getroot()
    except Exception: continue
    for d in root.iter("ThingDef"):
        dn = d.findtext("defName")
        if dn:
            DESC.setdefault(dn, " ".join((d.findtext("description") or "").split()))
            LAB.setdefault(dn, d.findtext("label") or dn)
        # shared-texture sibling

def rows():
    out = []
    for dn, tp, w, h, reg, vis, kind in R:
        lab = LAB[dn]
        nm = {"RUT_Hardwood": "heartwood (Greatbole timber)"}.get(dn, lab)
        desc = DESC[dn]
        if dn == "RUT_Hardwood": desc = DESC[dn]  # RUT_Hardwood's own def description (heartwood)
        for v, extra in VAR.items():
            r = {"id": f"phfix_{dn}_{v}", "rimflow_item_id": ITEM, "target_def": dn, "target_texpath": tp,
                 "prompt": f"RimWorld game {kind} sprite, {nm}: {desc} {vis}{extra}",
                 "style_notes": STYLE, "canvas_w": w, "canvas_h": h, "facings": [], "priority": 0,
                 "background": "transparent", "channel": "codex"}
            if reg: r["biome_register"] = reg
            else: r["biome_neutral"] = True
            out.append(r)
    return out

if __name__ == "__main__":
    print(json.dumps(rows(), indent=1))
