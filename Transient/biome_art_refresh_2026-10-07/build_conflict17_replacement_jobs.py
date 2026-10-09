#!/usr/bin/env python3
"""Replacements for the live LeaningScrub pictures deleted by card 2026-10-08 19:05 (Eopie B, Scurrier male B; Lothcat already
has regen_ls2_canon_lothcat_v1_*). Anchored on the deleted picture (store bytes still present) + canon image. Priority 0."""
import json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
SNAP = json.load(open(REPO / "infrastructure/state/art/sheets/leaningscrub_sheet_2026-10-05.snapshot.json"))["rows"]
CANON = REPO / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien, naturalistic and zoologically "
         "believable, never cartoonish or cute; one centred subject on a fully transparent background.")
def img(d, col, f):
    h = SNAP[d]["columns"][col][f]; return str(STORE / h[:2] / f"{h}.png")
rows = []
for d, slug, col, desc, tp, cimg in [
    ("RSW_Eopie", "eopie", "B", "the canon eopie of Tatooine: a tough quadruped mammalian herbivore, ~1.75-2 m tall, rough skin, rock-climbing hooves, trunked mouth", "swanimals/Eopie/Eopie", CANON / "eopie/wookieepedia_infobox.png"),
    ("RSW_Scurrier", "scurrier", "B", "the canon scurrier of Tatooine: a small, agile, scavenging rodent-like desert creature", "swanimals/Scurrier/Scurrier_m", CANON / "scurrier/wookieepedia_canon_1.webp")]:
    for f in ("east", "south", "north"):
        rows.append({"id": f"regen_c17_{slug}_v1", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1", "target_def": d,
          "prompt": f"RimWorld creature sprite of the Star Wars {slug}, {f.upper()} view: {desc}. The FIRST attached image is the previous render of this individual (owner-deleted for a redraw): keep species, colouring and scale but redraw it cleanly following the canon reference (second image). One animal, whole body, centred.",
          "style_notes": STYLE, "canvas_w": 256, "canvas_h": 256, "facings": [f], "background": "transparent", "channel": "codex",
          "priority": 0, "target_texpath": tp, "biome_neutral": True, "canon": slug,
          "canon_reference": [img(d, col, "east"), str(cimg)]})
out = Path(__file__).with_name("conflict17_replacement_jobs.json")
out.write_text(json.dumps(rows, indent=1)); print(len(rows), out)
