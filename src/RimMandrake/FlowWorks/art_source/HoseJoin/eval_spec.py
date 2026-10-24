#!/usr/bin/env python3
"""Art-eval spec + panels for the flat-face Coupling_Bare redraw (HOSE_JOIN_REDRAW_STILL_SHOWS_ITS_BORE).
The `assembled` panel is an OFFLINE MOCK (render_joins.py + crop_ns.py), not an in-game capture.
Usage: eval_spec.py CAND_DIR OUT_DIR ASSEMBLED_PNG"""
import json, sys, hashlib
from pathlib import Path
from PIL import Image
REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
from scale_panel import human_sprite
HOSE = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose"
LOOKS = {"Scrapper": "", "Industrial": "Styles/Industrial", "Modern": "Styles/Modern", "Futuristic": "Styles/Futuristic"}
OWNER = "South facing hose joins don't look good, I can see into the pipe opening still"


def main(cand, out, asm):
    cand, out = Path(cand), Path(out); out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (4 * 266, 256), (0, 0, 0, 0))
    for i, l in enumerate(LOOKS):
        sheet.alpha_composite(Image.open(cand / l / "Coupling_Bare.png").convert("RGBA").resize((256, 256), Image.NEAREST), (i * 266, 0))
    sp = out / "coupling_sheet.png"; sheet.save(sp)
    # scale: one coupling at its drawn size (FittingSize 0.4376 cell) at 128 px/cell beside a vanilla human
    ppc = 128; hum = human_sprite(ppc)[0]; s = round(0.4376 * ppc)
    sc = Image.new("RGBA", (40 + 4 * (s + 10) + hum.width + 20, max(s, hum.height) + 40), (112, 86, 62, 255))
    for i, l in enumerate(LOOKS):
        t = Image.open(cand / l / "Coupling_Bare.png").convert("RGBA").resize((s, s), Image.LANCZOS)
        sc.alpha_composite(t, (20 + i * (s + 10), sc.height - 20 - s))
    sc.alpha_composite(hum, (sc.width - 20 - hum.width, sc.height - 20 - hum.height))
    scp = out / "coupling_scale.png"; sc.save(scp)
    kept = [{"mod": "src/RimMandrake/FlowWorks", "rel": f"RimMandrake/FlowWorks/Hose/{(sub + '/') if sub else ''}Coupling_Bare.png",
             "sha": hashlib.sha256((HOSE / sub / "Coupling_Bare.png").read_bytes()).hexdigest()} for sub in LOOKS.values()]
    spec = {"subject": "RM_HoseCoupling_FlatFace", "label": "Hose coupling (4 looks): flat cut face",
            "template": "machine", "module": "hose", "candidate": "r1",
            "provenance": "deterministic pixel edit of the shipped art (art_source/HoseJoin/flat_face.py), 2026-10-23",
            "artpipe_job": None,
            "description": ("Coupling_Bare.png for the four hose looks (Scrapper brass, Industrial black/hazard, Modern aluminium, "
                            "Futuristic cyan), left to right on the sheet. ONE sprite, drawn by C# rotated to any heading at every "
                            "hose join (mid-hose joiner = two halves face to face, reel/port/relay couplings), 0.44 cell, lying flat "
                            "on the ground and seen from straight above. The hose enters at the left; the threaded stub on the right "
                            "is the face that meets the port or the other half. The old art ended the stub in a 3/4 'D' face with "
                            "a dark elliptical bore, which read as looking into the pipe once rotated to point south (art brief C6). "
                            "The redraw ends the stub in a flat side-on cut. NOTE: the assembled panel is an OFFLINE MOCK composed "
                            "from the textures with the C# sizes (columns: N joiner, S joiner, N-pointing port coupling, S-pointing "
                            "port coupling; rows: the four looks), not an in-game capture."),
            "tier": "RM_", "invented": False, "earth_body_named": True, "body_plan": None, "departures": [],
            "canon": {"must_show": [], "engine_limits": []}, "owner_notes": [f'Owner 2026-10-23 live walk on save e: "{OWNER}"'],
            "owner_kept": True, "kept_install": kept, "depends_on": None, "previous_prompt": None,
            "size": {"drawSize": [0.4376, 0.4376]}, "ports": [],
            "images": {"south": str(sp), "scale": str(scp), "siblings": [str(HOSE / sub / "Coupling_Bare.png") for sub in LOOKS.values()],
                       "assembled": [str(asm)]}}
    p = out / "RM_HoseCoupling_FlatFace.json"; p.write_text(json.dumps(spec, indent=1)); print(p)


if __name__ == "__main__":
    main(*sys.argv[1:4])
