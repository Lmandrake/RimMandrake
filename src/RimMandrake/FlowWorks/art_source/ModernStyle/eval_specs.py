#!/usr/bin/env python3
"""Build art-eval specs + panels for the Modern redraw candidates (MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL).
The `assembled` panels are OFFLINE MOCKS (scene.py / hose_end_mock.py), not in-game captures; every spec says so.
Usage: eval_specs.py CAND_DIR OUT_DIR"""
import json, sys
from pathlib import Path
from PIL import Image
REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
from scale_panel import human_sprite
TEX = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks"
GROUND = (112, 86, 62, 255)
OWNER = ['Owner 2026-10-23: "solid pipe looks pretty horrible actually. We need a whole art review of the Modern style. You made it all enamel red. That was never the intention. ... This is supposed to be stuff you can really see in the real world right now (modern), not just primary colors."',
         'Owner 2026-10-23: "Modern should instead be thought of as "modern consumer / commercial" and industrial is "brutalist""',
         'Owner 2026-10-23: "We should unfortunately regen the pumps and such to have connectors that match the more modern pipe and hose sizes. looks a bit silly." (pipe 0.136 cell wide, hose 0.18 cell flat)']
MOCK = " NOTE: the assembled panel is an OFFLINE MOCK composed from the textures with the C# sizes (pipe atlas tiles, join/fitting sizes), not an in-game capture; placement of joins in it is approximate."
SUBJ = {
 "RM_UniversalPipe_Modern": dict(module="part", file="UniversalPipe_Atlas.png", cells=(1, 1), desc="Modern look of the universal solid pipe: a linked 4x4 atlas (straights, elbows, tees, cross, end caps) built by build_pipe_atlas.py from a generated straight strip and a cross/end-cap fitting pair. Intended product: white Schedule 40 PVC pressure pipe with socket fittings. Drawn strictly top-down (a ground-lying pipe network), 0.136 cell thick.", scene=True),
 "RM_LiquidJoins_Modern": dict(module="coupler", file="joins_sheet.png", cells=(1, 1), desc="Modern join pieces drawn by C# on the pipe network: Coupler (machine-tank shared edge), Flange (pipe meets tank/machine, flush to the port edge), Saddle (hose on a pipe), UnderCollar + UnderPipe (under-coupler beneath a fixture). Intended product: white PVC socket coupling, PVC flange with stainless bolts, PVC tee saddle, grey moulded wall sleeve, white PVC pipe. Top-down.", scene=True),
 "RM_LiquidPump_Modern": dict(module="pump", file="RM_LiquidPump.png", cells=(1, 1), desc="Modern liquid pump, 1x1 cell, four ports at the N/E/S/W edge midpoints. Intended product: compact commercial electric booster pump (ribbed charcoal motor, thermoplastic pump housing, pressure switch, gauge) on a black base with a white PVC manifold and union stubs to the four ports. Graphic_Single: one picture serves every rotation (there are no other facings).", scene=True, ports=["north edge midpoint: pipe/hose", "east edge midpoint: pipe/hose", "south edge midpoint: pipe/hose", "west edge midpoint: pipe/hose"]),
 "RM_PipeFaucet_Modern": dict(module="part", file="RM_PipeFaucet.png", cells=(1, 1), desc="Modern pipe faucet on a pipe cell. Intended product: brass quarter-turn hose bib with a blue lever on a white PVC riser.", scene=True),
 "RM_SprinklerHead_Modern": dict(module="part", file="RM_SprinklerHead.png", cells=(1, 1), desc="Modern sprinkler head on a pipe cell. Intended product: brass impact sprinkler on a black riser in a white PVC socket.", scene=True),
 "RM_PipeSpan_Modern": dict(module="part", file="PipeSpan.png", cells=(3, 0.25), desc="Modern aerial pipe span between pipe poles: a seamless stretched strip of the network pipe (white PVC).", scene=True),
 "RM_HoseEnd_Modern": dict(module="hose", file="hose_parts.png", cells=(1, 1), desc="Modern fire-hose end pieces: Coupling_Bare (aluminium Storz coupling at reel/port/joiner) and Mouth (the bare free end's outer face, drawn 0.30 x 0.86 of the hose width on the end of the canvas wrap). The hose lies flat on the ground, so its end must be seen side-on with no bore (C6). Owner 2026-10-23 on the old free end: \"the end of this hose looks horrible.\"", scene=False, hose=True),
}

def panel(img, cells, ppc=128):
    w, h = int(cells[0] * ppc), int(cells[1] * ppc)
    hum = human_sprite(ppc)[0]
    W = w + hum.width + 3 * 20; H = max(h, hum.height) + 40
    c = Image.new("RGBA", (W, H), GROUND)
    from PIL import ImageDraw
    d = ImageDraw.Draw(c); x0, y0 = 20, H - 20 - h
    d.rectangle((x0, y0, x0 + w, y0 + h), outline=(230, 220, 120, 255))
    c.alpha_composite(img.convert("RGBA").resize((w, h), Image.LANCZOS), (x0, y0))
    c.alpha_composite(hum, (x0 + w + 20, H - 20 - hum.height))
    return c

def main(cand, out):
    cand, out = Path(cand), Path(out); out.mkdir(parents=True, exist_ok=True)
    comp = out.parent / "composites"
    # joins sheet / hose parts sheet
    def sheet(names, fn):
        ims = [Image.open(cand / n).convert("RGBA") for n in names]
        s = Image.new("RGBA", (sum(256 for _ in ims) + 10 * len(ims), 256), (0, 0, 0, 0)); x = 0
        for im in ims:
            k = min(256 / im.width, 256 / im.height); t = im.resize((int(im.width * k), int(im.height * k)), Image.NEAREST)
            s.alpha_composite(t, (x + (256 - t.width) // 2, (256 - t.height) // 2)); x += 266
        s.save(cand / fn)
    sheet(["Coupler.png", "Flange.png", "Saddle.png", "UnderCollar.png", "UnderPipe.png"], "joins_sheet.png")
    sheet(["Coupling_Bare.png", "Mouth.png"], "hose_parts.png")
    sib = [str(TEX / "Tank/Modern/RM_LiquidTank.png"), str(TEX / "Tank/Modern/RM_LiquidTankTall.png"),
           str(TEX / "Tank/Modern/RM_UniversalCargoTank.png"), str(TEX / "Hose/Styles/Modern/Reel_PumpHookup.png")]
    specs = []
    for subj, s in SUBJ.items():
        img = Image.open(cand / s["file"])
        sc = out / f"{subj}_scale.png"; panel(img, s["cells"]).save(sc)
        asm = [str(comp / "hose_after.png")] if s.get("hose") else [str(comp / (cand.name + "_x2.png"))]
        spec = {"subject": subj, "label": subj.replace("_", " "), "template": "machine", "module": s["module"],
                "candidate": "r1", "provenance": "codex imagegen 2026-10-23 · Transient/modern_style_20261023", "artpipe_job": None,
                "description": s["desc"] + MOCK, "tier": "RM_", "invented": False, "earth_body_named": True, "body_plan": None,
                "departures": [], "canon": {"must_show": [], "engine_limits": []}, "owner_notes": OWNER,
                "owner_kept": False, "depends_on": None, "previous_prompt": None,
                "size": {"drawSize": list(s["cells"])}, "ports": s.get("ports", []),
                "images": {"south": str(cand / s["file"]), "scale": str(sc), "siblings": sib, "assembled": asm}}
        p = out / f"{subj}.json"; p.write_text(json.dumps(spec, indent=1)); specs.append(str(p))
    print("\n".join(specs))

if __name__ == "__main__":
    main(*sys.argv[1:3])
