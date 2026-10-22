#!/usr/bin/env python3
"""PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS (owner card 2026-10-22 "Draft all of it"): artpipe masters for the pipe atlas
pieces (Cross, Tee, Coupling, EndCap per look; top-down like the atlas) and three pump looks (reskins of the live
4-port hub pump). Masters are conformed by conform.py and composed into draft atlases by compose.py. Nothing installed."""
import json
REPO = "/home/mandrake/rm/bench"
ITEM = "PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS"
NOTE = "Draft all of it: real 3- and 4-way fittings, one coupling per joint, a matched end cap per look, three more pump looks (card 2026-10-22)"
LOOK = {
 "Scrapper": "rusted salvaged steel: deep brown shadow #302010, warm grey-brown #706050 and rust-orange #805030 body, pale worn highlight #bbaaa0, flaking rust and round rivets",
 "Industrial": "dark gunmetal-grey heavy steel: #303030 shadow, #404040 to #505050 body, pale steel highlight #9fa2a7, chunky hex bolts",
 "Modern": "glossy bright red enamel: #580b0b shadow, #c00000 to #e00000 body, soft pink-white gloss highlight #fe9d9d, polished silver bolt heads",
 "Futuristic": "glossy white composite: #c0c0c0 to #e0e0e0 panels, dark #282f37 seams, one thin glowing cyan #2de7ef accent line, sleek flush fasteners",
}
CAM = ("Seen from DIRECTLY ABOVE (pure top-down orthographic plan view, no perspective, no visible side faces), light from the top-left. "
       "Bold, chunky, simple shapes with a thin dark outline and strong value contrast so it still reads when shrunk to 24 pixels. "
       "Crisp painterly RimWorld-mod sprite style. One object only, centred, on a fully transparent background, no shadow on the ground.")
PIECE = {
 "Cross": "ONE four-way pipe cross fitting seen from above: a sturdy round or rounded-square cast junction body in the middle with "
          "four identical short round pipe stubs pointing exactly left, right, up and down, perfectly symmetric in both axes. "
          "The junction body is about 2.2 times the pipe's width across; the stubs are as long as the body is wide. Material: {m}. ",
 "Tee": "ONE three-way pipe tee fitting seen from above: a sturdy cast junction body with three short round pipe stubs, one pointing "
        "exactly left, one exactly right and one exactly DOWN, and NOTHING pointing up (the top of the body is closed and rounded). "
        "Symmetric left to right. The body is about 2 times the pipe's width across; the stubs are as long as the body is wide. Material: {m}. ",
 "Coupling": "ONE pipe coupling seen from above: a short horizontal stub of round pipe running exactly left to right through ONE single "
             "raised clamp band around its middle; the band is about 1.35 times the pipe's width tall and about half the pipe's width "
             "wide, with one bolt head on it. Only one band. Material: {m}. ",
 "EndCap": "ONE pipe end cap seen from above: a short stub of round pipe entering exactly from the left and ending on the right in "
           "a SHALLOW domed cap, the cap only slightly wider than the pipe (about 1.2 times its width) and short (about half the "
           "pipe's width deep), clearly a closed pipe end, not a knob or a ball. Material: {m}. ",
}
rows = []
for piece, p in PIECE.items():
    for look, m in LOOK.items():
        rows.append({"id": f"pipefitraw_{piece.lower()}_{look.lower()}_v1", "rimflow_item_id": ITEM,
                     "prompt": p.format(m=m) + CAM, "canvas_w": 1024, "canvas_h": 1024, "priority": 5,
                     "background": "transparent", "target_texpath": f"RimMandrake/FlowWorks/Pipe/{look}/Draft/{piece}",
                     "no_subject": "piece of a linked pipe atlas (UniversalPipe_Atlas), composed offline; no def",
                     "owner_note": NOTE, "biome_neutral": True,
                     "oversize_reason": "master only: conform.py scales it to the 0.10-cell pipe of the 176 px/cell atlas"})
LIVE = f"{REPO}/src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"
for look in ["Industrial", "Modern", "Futuristic"]:
    rows.append({"id": f"pumplook_{look.lower()}_v1", "rimflow_item_id": ITEM,
                 "prompt": ("The attached image is the CURRENT liquid pump sprite (the Scrapper look). Draw the SAME pump: same "
                            "top-down plan view, same layout (round central pump body with a round grille, four short pipe stubs "
                            "with bolted flanges pointing exactly left, right, up and down, centred on the canvas), same size and "
                            "silhouette, same 1x1 cell footprint, filling the canvas the same way. Change ONLY the material and "
                            f"finish to the {look} look: {LOOK[look]}. The flanges must match that look's pipe colours, not copper. "
                            + CAM),
                 "canvas_w": 512, "canvas_h": 512, "priority": 5, "background": "transparent",
                 "canon_reference": [LIVE], "drawsize": 1.0,
                 "target_texpath": f"RimMandrake/FlowWorks/Pump/{look}/RM_LiquidPump",
                 "no_subject": "a look of RM_LiquidPump (style art, no def binds this path yet)",
                 "owner_note": NOTE, "biome_neutral": True})
json.dump(rows, open(__file__.replace("make_jobs.py", "jobs.json"), "w"), indent=1)
print(len(rows))
