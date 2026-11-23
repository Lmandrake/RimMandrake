#!/usr/bin/env python3
"""Judge the generated tank options with GPT (gpt_consult.py, images attached), one call per look, against the look
brief and design/RimMandrake/art_judge_brief.md. Writes infrastructure/state/delegated/2026-11-22/flowworks_tank_designs_<look>.json.

    judge_tanks.py LOOK [NAME ...]      LOOK in futuristic|industrial|modern; names default to every option of the look
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
OPT, PAN, BOARD = HERE / "options", HERE / "panels", HERE / "judge"
OUTDIR = REPO / "infrastructure/state/delegated/2026-11-22"
LOOKS = REPO / "design/specs/2026-11-22-flowworks-look-briefs/looks.md"
BRIEF = REPO / "design/RimMandrake/art_judge_brief.md"
SCRAPPER = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/Scrapper/RM_LiquidTank.png"
TERRAIN = (124, 100, 72, 255)

ASK = """You are a fresh art judge. You did not make these pictures. Read the two inlined files: the look briefs
(looks.md) and the art judge brief (art_judge_brief.md). Judge ONLY against what they say.

Subject: the FlowWorks liquid tank, def RM_LiquidTank, ThingStyleDef drawSize (2,2) on a 2x2 footprint, Graphic_Single
(one picture, used for every rotation), 512x512 canvas, a building drawn from the one building camera (C3). The look
being judged: {look}. These are NEW designs for that look, generated to replace the shipped {look} tank. The owner's
words on this tank (2026-11-22, verbatim): "{owner}"

Attached images, in order:
{images}

For EACH candidate decide KEEP, REDO or UNSURE against the {look} section of looks.md (Represents, Materials, Wear,
Colour range, Instruments, Must NOT look like) and the art judge brief (B1, B1a no drawn outlines, B2 legibility at
32 px/cell, B4, B6, C3 building camera, D1 true scale beside the human, D3 inside the footprint, D4 real alpha, E4 his
note). It must also read as the same game and roughly the same size class as the accepted Scrapper tank. A REDO quotes
the violated line, says what you SAW, and gives a one-line redo_brief for the image generator. Polish (a thing you would
merely like better) is not a REDO: put it in notes. Then name your single pick among the KEEPs for this look and why.

Answer with ONE JSON object and nothing else:
{{"look": "{look}", "verdicts": [{{"candidate": "<name>", "verdict": "KEEP|REDO|UNSURE", "violated": "<id or empty>",
"quote": "<the violated line or empty>", "seen": "<what you saw>", "redo_brief": "<or empty>", "notes": "<short>"}}],
"pick": "<name or empty>", "pick_why": "<one line>", "proposals": []}}"""

OWNER = {
    "futuristic": "The futuristic one just looks like the industrial one with a steampunk vibe. It should be more "
                  "computerized and elegant, sleek with little control access points to slide open access ports. No "
                  "simple analog dials, they should be computerized readouts.",
    "industrial": "The Industrial one looks ok but is rusty and abandoned looking. ... The analog dial would look good "
                  "on the Modern and Industrial one though.",
    "modern": "The modern tank reads very cartoonish, needs to be more realistic with some smudges and normal wear. ... "
              "The analog dial would look good on the Modern and Industrial one though.",
}


def board(png, out):
    """The candidate at full size (512) on desert ground, so the judge sees craft without a checkerboard."""
    im = Image.open(png).convert("RGBA")
    bg = Image.new("RGBA", im.size, TERRAIN)
    bg.alpha_composite(im)
    bg.save(out)


def main(argv):
    look = argv[0]
    names = argv[1:] or sorted(p.stem for p in OPT.glob(f"tank_{look}_*.png"))
    BOARD.mkdir(exist_ok=True)
    imgs, desc = [], []
    board(SCRAPPER, BOARD / "reference_scrapper_full.png")
    imgs.append(BOARD / "reference_scrapper_full.png"); desc.append("the accepted Scrapper tank (reference, not judged), full size on ground")
    for n in names:
        board(OPT / f"{n}.png", BOARD / f"{n}__full.png")
        for p, d in ((BOARD / f"{n}__full.png", "full size 512 px on desert ground"),
                     (PAN / f"{n}__alpha.png", "the PNG itself over a checkerboard: its real alpha channel"),
                     (PAN / f"{n}__scale128.png", "true scale at 128 px/cell (D1): vanilla human | Scrapper | candidate"),
                     (PAN / f"{n}__zoom.png", "play zoom: Scrapper and candidate at 32 px/cell, then at 64 px/cell")):
            imgs.append(p); desc.append(f"candidate {n}: {d}")
    images = "\n".join(f"{i + 1}. {d}" for i, d in enumerate(desc))
    rep = json.loads((HERE / "report.json").read_text())
    facts = {n: {k: rep[n][k] for k in ("restyle_ok", "restyle_blocking", "findings", "port_left", "port_right")} for n in names}
    images += ("\n\nMeasured facts (validate_sprite.py against the Scrapper canvas, and the end-port check): " + json.dumps(facts)
               + "\nThe span/aspect/origin REJECTs are the reference-fidelity family, which the sprite skill says is the wrong"
               " check for a restyle (the shipped Industrial, Modern and Futuristic tanks fail it against Scrapper too); the"
               " canvas, alpha, corner, fringe and port checks are the ones that bind. Camera (C3): each candidate was drawn"
               " as an edit with the accepted Scrapper tank as image 1 for camera, scale and layout; judge C3 by comparing"
               " each candidate's view of its top surface with the Scrapper's, which the owner accepts. The drawSize equals"
               " the footprint (2x2), so the whole 512 canvas IS the footprint: nothing on the canvas can be outside it.")
    q = ASK.format(look=look.capitalize(), owner=OWNER[look], images=images)
    raw = HERE / "judge" / f"gpt_{look}.txt"
    cmd = [sys.executable, str(REPO / "src/RimMandrake/Utils/gpt_consult.py"), q, "-f", str(LOOKS), "-f", str(BRIEF),
           "--out", str(raw), "--timeout", "1500"]
    for p in imgs:
        cmd += ["-i", str(p)]
    rc = subprocess.call(cmd, stdout=subprocess.DEVNULL)
    if rc != 0 or not raw.exists():
        print(f"FAILED gpt_consult rc={rc}; no verdict written", file=sys.stderr)
        return 2
    text = raw.read_text()
    m = re.search(r"\{.*\}", text, re.S)
    try:
        v = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        v = None
    if not v or "verdicts" not in v:
        print(f"FAILED: no JSON verdict in {raw}", file=sys.stderr)
        return 3
    sha = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec = {"judge_model": "GPT via gpt_consult.py (codex exec, Linux side)", "brief": f"design/RimMandrake/art_judge_brief.md@{sha}",
           "looks": f"design/specs/2026-11-22-flowworks-look-briefs/looks.md@{sha}", "subject": "RM_LiquidTank",
           "item": "RIMMANDRAKE_GENERATE_FLOWWORKS_TANK_DESIGNS_FIRST_RUN_ONLY_REPAINTED",
           "given": [str(p.relative_to(REPO)) for p in imgs], **v}
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"flowworks_tank_designs_{look}.json"
    old = json.loads(out.read_text()) if out.exists() else None
    if old:
        rec["earlier_rounds"] = old.get("earlier_rounds", []) + [{k: old[k] for k in ("verdicts", "pick", "pick_why") if k in old}]
    out.write_text(json.dumps(rec, indent=1) + "\n")
    for x in v["verdicts"]:
        print(f"{x.get('candidate')}: {x.get('verdict')} {x.get('violated', '')} {x.get('seen', '')[:150]}")
    print(f"pick: {v.get('pick')} - {v.get('pick_why')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
