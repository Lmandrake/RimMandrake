#!/usr/bin/env python3
"""Catch paintings for fish items that had no finished render (fish_texpaths.md). Run: python3 <this> > fish_catch_jobs.json ; fill_queue.py --input fish_catch_jobs.json"""
import json, glob, xml.etree.ElementTree as ET
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
QUEUED = ["RM_FessuCatch", "RM_KrellikCatch", "RM_OdduCatch", "RM_OovuCatch", "RM_TarnnCatch",
          "RSW_FaaCatch", "RSW_LaaCatch", "RSW_MeeCatch", "RUT_Hurrok", "RUT_Vhessa"]
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic and grounded, never cartoonish, never a flat shape "
         "or icon; one centred subject on a fully transparent background, no ground plane, no cast shadow.")
VAR = {"a": "", "b": " A second, clearly different rendering of the same subject (different shape and pose)."}
defs = {}
for f in glob.glob(str(REPO / "src/**/*.xml"), recursive=True):
    try: r = ET.parse(f).getroot()
    except Exception: continue
    for t in r.iter("ThingDef"):
        n = t.findtext("defName")
        if n: defs.setdefault(n, t)
out = []
for dn in QUEUED:
    d = defs[dn]; lab = d.findtext("label"); desc = " ".join(d.findtext("description").split())
    cr = defs.get(dn.replace("Catch", ""))
    ref = (" It must look like the living creature it comes from: " + " ".join(cr.findtext("description").split())) if cr is not None and cr.findtext("description") else ""
    for v, extra in VAR.items():
        out.append({"id": f"phfix_{dn}_{v}", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1", "target_def": dn,
                    "target_texpath": f"Things/Item/Fish/{dn}", "priority": 0, "background": "transparent",
                    "channel": "codex", "canvas_w": 128, "canvas_h": 128, "facings": [], "biome_neutral": True,
                    "prompt": f"RimWorld fish-item icon, the {lab}, a caught fish lying as an inventory item on the ground: {desc}{ref}{extra}",
                    "style_notes": STYLE})
print(json.dumps(out, indent=1))
