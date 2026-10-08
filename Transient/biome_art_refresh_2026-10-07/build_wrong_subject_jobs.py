#!/usr/bin/env python3
"""Priority-0 jobs for wrong-subject textures (wrong_subject_art.md, groups 8-11 + Vaalok south). Nothing installed.
Run: python3 <this> > wrong_subject_jobs.json ; fill_queue.py --input wrong_subject_jobs.json"""
import json
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic and grounded, never cartoonish, never a flat shape "
         "or icon; one centred subject on a fully transparent background, no ground plane, no cast shadow.")
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
def job(i, dfn, tp, w, h, prompt, reg=None, facings=(), **kw):
    r = {"id": i, "rimflow_item_id": ITEM, "target_def": dfn, "target_texpath": tp, "prompt": prompt,
         "style_notes": STYLE, "canvas_w": w, "canvas_h": h, "facings": list(facings), "priority": 0,
         "background": "transparent", "channel": "codex"}
    if reg: r["biome_register"] = reg
    else: r["biome_neutral"] = True
    r.update(kw); return r
J = []
J.append(job("wsfix_RM_Vaalok_south_v2", "RM_Vaalok", "Things/Pawn/Animal/RM_Vaalok/RM_Vaalok", 512, 512,
  "RimWorld creature sprite, the same individual as the accepted east render: a slow, deep-chested giant that carries its water inside itself, "
  "a cistern-bodied beast of pale grey-lilac wrinkled hide with a rust-orange cracked-clay hump, trunk-like drooping muzzle, thick pillar legs. "
  "FRONT view, facing the viewer (south), whole body, centred. NOT a spined sail-backed animal.",
  facings=["south"], derive_from="RM_Vaalok_east"))
J.append(job("wsfix_Gloomcast_Dessicated", "RM_Gloomcast", "swanimals/Gloomcast/Gloomcast_Dessicated", 256, 256,
  "RimWorld dessicated-corpse sprite, side view: the bleached, sand-scoured dried remains of a colossal slow desert grazer: a long low "
  "barrel of ribcage, broad flat plated skull, thick pillar leg bones, hide dried to parchment over the bones, half-drifted with fine sand. "
  "Description of the living animal: a colossal, slow-moving grazer that crosses the open dayside in a single committed march, a filter-feeder that strains the sand.",
  reg="long shade register: a baked sand desert under a low furnace sun, hard long shadows, bleached ochre and bone-white"))
J.append(job("wsfix_RM_SummBone", "RM_SummBone", "RM_Abyss/Things/Item/SummBone", 128, 128,
  "RimWorld item sprite, summ brood bone: bone from the summ brood's dead: a single huge, honeycombed, surprisingly light bone fragment, "
  "porous cellular structure visible at the broken end like pale coral or pumice, ivory-grey with faint blue-green deep-sea tint. "
  "Not a pile of ordinary bones.",
  reg="abyss register: lightless deep sea floor, cold blue-black water, pale bioluminescent accents"))
J.append(job("wsfix_RM_SummGreatBone", "RM_SummGreatBone", "RM_Abyss/Things/Building/SummGreatBone", 1024, 512,
  "RimWorld building sprite seen from above at a slight angle: a single enormous bone from a brood-mother long dead, as long as a room: "
  "one long gently curved honeycombed bone, pale ivory-grey, knobbed articulated ends, porous cell structure at the ends, lying on its side. "
  "A single bone only, not a skeleton, no ribs, no skull.",
  reg="abyss register: lightless deep sea floor, cold blue-black water, pale bioluminescent accents"))
J.append(job("wsfix_RM_FlameStatuary", "RM_FlameStatuary", "Things/Building/Art/RM_FlameStatuary/RM_FlameStatuary", 256, 256,
  "RimWorld building sprite, flame statuary: a grand sculpture built to carry fire in its own shape: a 2x2 carved stone plinth statue "
  "with flame issuing from carved vents worked into the stone, tongues of live fire dancing along the form, soot-darkened dark stone, "
  "orange-gold fire. Seen top-down at a slight angle.", reg=None))
print(json.dumps(J, indent=1))
