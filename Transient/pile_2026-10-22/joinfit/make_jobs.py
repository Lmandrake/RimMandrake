#!/usr/bin/env python3
"""PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID (owner card 2026-10-22 "Draw fittings"): the 12 artpipe jobs for
Joins/<Look>/{Flange,Coupler,Saddle}. Generated large (1024), conformed to the game quads by conform.py."""
import json
LOOK = {
 "Scrapper": "rusted salvaged steel: deep brown shadow #302010, warm grey-brown #706050 and rust-orange #805030 body, pale worn highlight #bbaaa0 on the top edge, flaking rust and round rivets",
 "Industrial": "dark gunmetal-grey heavy steel: #303030 shadow, #404040 to #505050 body, pale steel highlight #9fa2a7 on the top edge, chunky hex bolts",
 "Modern": "glossy bright red enamel: #580b0b shadow, #c00000 to #e00000 body, soft pink-white gloss highlight #fe9d9d on the top edge, polished silver bolt heads",
 "Futuristic": "glossy white composite: #c0c0c0 to #e0e0e0 panels, dark #282f37 seams, one thin glowing cyan #2de7ef accent line, sleek flush fasteners",
}
CAM = ("Seen from a high orthographic camera about 35 degrees above the ground, light from overhead-front, top faces lit. "
       "Bold, chunky, simple shapes with a thin dark outline and strong value contrast, so it still reads when shrunk to 32 pixels. "
       "Crisp painterly RimWorld-mod sprite style. One object only, centred, filling about 80 percent of the canvas width, "
       "on a fully transparent background.")
PIECE = {
 "Flange": "ONE pipe flange fitting: a very short stub of round rigid pipe lying exactly horizontally, entering from the left, "
           "ending on the right in a thick round bolted flange collar seen edge-on, the collar about 1.3 times the pipe's diameter "
           "and standing taller than the pipe above and below, with three bold bolt heads across its face. Material: {m}. ",
 "Coupler": "ONE pipe union coupler: two thick round flange collars clamped face to face in the middle, joining two very short "
            "round pipe stubs that point exactly left and right, perfectly symmetric left to right, the collars about 1.2 times "
            "the pipe's diameter, a ring of bold bolt heads holding them together. Material: {m}. ",
 "Saddle": "ONE hose saddle fitting: a short section of round rigid pipe lying exactly horizontally, with a wide bolted band "
           "clamp wrapped around its middle, and on top of the clamp one short round hose spigot ending in a ribbed hose "
           "ferrule, the spigot pointing down toward the viewer. The clamp is about 2.4 times the pipe's diameter across. "
           "Material: {m}. ",
}
rows = []
for piece, p in PIECE.items():
    for look, m in LOOK.items():
        rows.append({"id": f"joinfitraw_{piece.lower()}_{look.lower()}_v1", "rimflow_item_id": "PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID",
                     "prompt": p.format(m=m) + CAM, "canvas_w": 1024, "canvas_h": 1024, "priority": 5,
                     "background": "transparent", "target_texpath": f"RimMandrake/FlowWorks/Joins/{look}/{piece}",
                     "no_subject": "C#-drawn liquid join fitting (RM_LiquidJoins), no def",
                     "owner_note": "Draw fittings: 12 joint fitting pictures, one Flange/Coupler/Saddle per look, matched to that look's pipe colours (card 2026-10-22)",
                     "biome_neutral": True, "oversize_reason": "master only: conform.py shrinks it to the 0.12-0.24 cell fitting on a 128/256 px quad"})
json.dump(rows, open("jobs.json", "w"), indent=1)
print(len(rows))
