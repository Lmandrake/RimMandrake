#!/usr/bin/env python3
"""Fish-item paintings for the RUT_ fish that used to borrow timber textures (fish_texpaths.md).
Run: python3 <this> > fish_texpath_jobs.json ; fill_queue.py --input fish_texpath_jobs.json"""
import json, xml.etree.ElementTree as ET
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
B = REPO/"src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items"
FISH = {"RUT_Tubbik": "RUT_CrackedLandsFish_Items.xml", "RUT_Zhurr": "RUT_CrackedLandsFish_Items.xml",
        "RUT_BladderboilCatch": "RUT_ScaldFish.xml"}
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic and grounded, never cartoonish, never a flat shape "
         "or icon; one centred subject on a fully transparent background, no ground plane, no cast shadow.")
VAR = {"a": "", "b": " A second, clearly different rendering of the same subject (different shape and pose)."}
out = []
for dn, f in FISH.items():
    d = next(t for t in ET.parse(B/f).getroot().iter("ThingDef") if t.findtext("defName") == dn)
    desc = " ".join(d.findtext("description").split()); lab = d.findtext("label")
    for v, extra in VAR.items():
        out.append({"id": f"phfix_{dn}_{v}", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1", "target_def": dn,
                    "target_texpath": f"Things/Item/Fish/{dn}", "priority": 0, "background": "transparent",
                    "channel": "codex", "canvas_w": 128, "canvas_h": 128, "facings": [], "biome_neutral": True,
                    "prompt": f"RimWorld fish-item icon, the {lab}, a caught fish lying as an inventory item: {desc}{extra}",
                    "style_notes": STYLE})
print(json.dumps(out, indent=1))
