#!/usr/bin/env python3
"""WEATHER_STONES_OWN_ART_1: one job each for RM_CondenserWater, RM_KarrekPaste, RM_SeepStone. Nothing installed.
Run: python3 <this> > weather_stones_jobs.json ; fill_queue.py --input weather_stones_jobs.json"""
import json
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic and grounded, never cartoonish, never a flat shape "
         "or icon; one centred subject on a fully transparent background, no ground plane, no cast shadow.")
R = [
 ("RM_CondenserWater", "condenser water", "A litre of clean water drawn out of dry air by the ancient condenser, in a stoppered flask.",
  "A stoppered glass flask of perfectly clear water, beads of condensation on the glass, faint blue glint."),
 ("RM_KarrekPaste", "karrek paste", "A basketful of karrek rendered at a stove into a dense, gray-brown ration. Caravan food for the oasis string, eaten with resignation, not enjoyment, but it does not spoil for a season.",
  "A dense gray-brown block of rendered paste ration, loaf-shaped, dull and unappetising, wrapped partly in coarse cloth."),
 ("RM_SeepStone", "seep stone", "A smooth mineral concretion grown drop by drop in the spring throat itself, banded pale and dark the same way the cliffs above the pool are. Oasis-keepers set the best ones on the shrine at the water's edge.",
  "A single smooth rounded mineral concretion the size of a fist, banded pale cream and dark grey-brown, faintly damp."),
]
out = []
for dn, lab, desc, vis in R:
    out.append({"id": f"wsart_{dn}", "rimflow_item_id": "WEATHER_STONES_OWN_ART_1", "target_def": dn,
                "target_texpath": f"Things/Item/Resource/{dn}/{dn}",
                "prompt": f"RimWorld game item sprite, {lab}: {desc} {vis}",
                "style_notes": STYLE, "canvas_w": 128, "canvas_h": 128, "facings": [], "priority": 0,
                "background": "transparent", "channel": "codex", "biome_neutral": True})
print(json.dumps(out, indent=1))
