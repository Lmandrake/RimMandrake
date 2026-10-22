#!/usr/bin/env python3
"""REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED (owner card 2026-10-22 "May we draft north/south reel views? -> Draft all 16"):
16 artpipe jobs, N+S x stored/laid x 4 looks, each drawn from that look+state's installed WEST picture (canon_reference).
Port position follows HoseReelRect.ArtPose: the west picture turned 90 deg, so the outlet sits at top centre (north) /
bottom centre (south). Nothing installed."""
import json
REPO = "/home/mandrake/rm/bench"
TEX = f"{REPO}/src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose"
LOOKS = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
STATE = {
 "PumpHookup": ("stored", "the drum FULL, wound with many neat wraps of thin hose, the hose's short free end plugged into the exit port"),
 "Deployed": ("laid", "the drum nearly EMPTY, only a few wraps left, its thin hose leaving the drum and passing into the exit port"),
}
FACE = {
 "north": ("NORTH", "The reel is TURNED 90 degrees from the attached picture: its drum axle now runs straight up-down the picture "
           "(north-south), so the two round flanges are seen almost edge-on as wide flat ellipses at the TOP and BOTTOM of the drum, "
           "and the drum's wound hose shows as horizontal bands between them. The hand crank sticks out of the BOTTOM (south) flange "
           "toward the viewer. The single exit port is at the TOP centre (x about 128, y about 40): a metal swivel fitting 15-16 px "
           "across whose open mouth faces due NORTH (up the picture); the hose passes into it from the drum."),
 "south": ("SOUTH", "The reel is TURNED 90 degrees from the attached picture: its drum axle now runs straight up-down the picture "
           "(north-south), so the two round flanges are seen almost edge-on as wide flat ellipses at the TOP and BOTTOM of the drum, "
           "and the drum's wound hose shows as horizontal bands between them. The hand crank sticks out of the TOP (north) flange, "
           "away from the viewer, partly hidden. The single exit port is at the BOTTOM centre (x about 128, y about 216): a metal "
           "swivel fitting 15-16 px across whose open mouth faces due SOUTH (down the picture, toward the viewer); the hose passes "
           "into it from the drum."),
}
rows = []
for look, sub in LOOKS.items():
    for st, (word, drum) in STATE.items():
        ref = f"{TEX}/{sub}Reel_{st}.png"
        for face, (FW, geo) in FACE.items():
            rows.append({
                "id": f"reelns_{look.lower()}_{word}_{face}_v1",
                "rimflow_item_id": "REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED",
                "prompt": (f"The attached image is the CURRENT {look} hose reel picture, drawn facing WEST (exit port on the left). "
                           f"Draw the SAME reel - same materials, palette, wear, flange and frame design, same overall size and the same "
                           f"RimWorld building camera (seen from almost straight above with a slight tilt, tops lit, only a short south "
                           f"face showing) - but facing {FW}. {geo} State: {drum}. The hose is thin: 8-9 px wide everywhere. A low "
                           f"A-frame base under the drum. 256x256 canvas, the reel centred, about 120-135 px wide and 150-165 px tall "
                           f"(the west picture's width becomes this height). Nothing else sticks out past the frame. "
                           f"Transparent background, no ground, no cast shadow."),
                "style_notes": "Keep the attached picture's palette and material exactly; only the facing changes. No outlines, painted edges like the attached sprite.",
                "canvas_w": 256, "canvas_h": 256, "priority": 5, "background": "transparent",
                "canon_reference": ref,
                "target_def": "RM_HoseReel",
                "target_texpath": f"RimMandrake/FlowWorks/Hose/{sub}Reel_{st}_{face}",
                "owner_note": f"Draft north/south reel views: the {look} reel {word}, facing {face}, matched to the installed west picture (card 2026-10-22)",
            })
json.dump(rows, open(__file__.replace("make_jobs.py", "jobs.json"), "w"), indent=1)
print(len(rows))
