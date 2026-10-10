import json
NO=("NO outline, no black edge line, no dark rim; the object's edge is defined by its own colour and soft shading against the transparent background. "
    "Painted in the same realistic natural-history painted style as the Rot plant renders: real material texture, believable lighting, matte, soft contact shadow only. Centered, isolated, transparent background.")
rows=[
("RM_PillarArmItem","Things/Item/Health/RM_PillarArmItem","a pillar arm graft - a heavy slab of bone-cored meat, a club-like limb grown from monstrous tissue, thick as a column, raw pink-grey flesh over a pale bone core, ragged shoulder-end where it was cut free, no hand or fingers"),
("RM_RawUltracactus","Things/Item/Plant/RM_RawUltracactus","a pile of ultriss pulp - pale, faintly sweet cactus pad flesh cut into thick wedges, translucent green-white interior with a strip of waxy green skin, slightly bruised at the edges"),
("RM_FE_ScorchFruitYield","Things/Item/Resource/RM_FE_ScorchFruit","a scorch-fruit - the soft sweet contents of a fire-cracked seed-pod, a plump amber-orange fruit with smoke-darkened patches and a few shards of woody cracked casing clinging to it, faint ember glow in the cracks"),
("RM_OllimWood","Things/Item/Resource/RM_OllimWood","a short stack of ollim wood - bone-white, dense stone-like timber planks with very fine tight grain, one end showing a clean pale cross-section, a hairline fracture suggesting brittleness"),
("RM_BladderFruit","Things/Item/Plant/RM_BladderFruit","a bladder-fruit - a fat translucent water-filled pod cut from a bladderquill, pale green-gold skin taut with sloshing liquid and a little starchy pulp visible through it, short cut stem"),
("RM_SweetlineWool","Things/Item/Resource/RM_SweetlineWool","a bundle of sweetline felt - dense, soft, silver-grey felted wool matted and cured in tree resin, faint amber resin sheen and a few flecks of bark, folded into a thick pad"),
("RSW_Apparel_FangPendant","Things/Item/RSW_Apparel_FangPendant/RSW_Apparel_FangPendant","a wyyyschokk fang pendant - a cluster of curved ivory fangs wrapped at the base with rough cord, hanging from a loop of cord, laid flat as an item"),
("RM_VorrelSeedDish","Things/Item/Meal/RM_VorrelSeedDish","a dish of prepared vorrel - a shallow bowl of cooked vorrel seeds, plump and slightly split as if just woken, glossy and bright, gentle steam"),
("RM_ShullaCatch","Things/Item/Fish/RM_ShullaCatch","a shulla - a small hot-white sliver of a fish, narrow and glassy, pale-white body with a faint heat-shimmer glow along its edge, freshly netted"),
("RUT_SealedWaterJar","Things/Item/RUT_SealedWaterJar","a sealed water jar - a clay jar waxed shut at the mouth, fired terracotta body with a dark wax seal and cord, heavy and full"),
]
J=[]
for d,tex,desc in rows:
    J.append({"id":d+"_v3_nooutline","rimflow_item_id":"ICON_OUTLINE_REPAINT_1","target_def":d,"canvas_w":128,"canvas_h":128,"background":"transparent","priority":46,"facings":[],
     "prompt":"RimWorld game item sprite: %s. Single item, centered, no ground shadow, no background scenery. %s"%(desc,NO),
     "style_notes":"REPAINT of %s without its near-black edge outline (census 2026-10-10, foundry fill, owner card; prompt hand-written from def description). painterly vanilla-RimWorld art style, grounded believable materials, matte, never cartoonish, no outlines, no black edge line, soft contact shadow only"%d,
     "target_texpath":tex})
json.dump(J,open("Transient/foundry_art_fill2_jobs_20261010.json","w"),indent=1)
